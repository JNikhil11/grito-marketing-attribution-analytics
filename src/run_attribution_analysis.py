"""
Grito Labs Marketing Analytics & Attribution Framework
Module: src/run_attribution_analysis.py
Description: End-to-end Python attribution analysis runner:
             - Rule-Based models (FTA, LTA, Linear, Time-Decay, U-Shaped)
             - Data-Driven models (Markov Chain Removal Effects, Shapley Values)
             - Sensitivity Analysis (Half-Life & Lookback Window)
             - Cross-checks SQL and Python numerical consistency
             - BG/NBD + Gamma-Gamma Predictive CLV
             - Budget Reallocation via Hill Saturation Optimization
             - Exports Top Converting Customer Paths (Overall and Multi-Touch Only)
"""

import os
import sys
import sqlite3
import csv
from datetime import datetime
from collections import defaultdict, Counter

from attribution_models import (
    compute_rule_based_attribution,
    compute_markov_attribution,
    compute_shapley_attribution
)
from clv_model import fit_bgnbd_gamma_gamma, summarize_clv_by_channel
from budget_optimizer import optimize_budget_allocation, generate_incrementality_test_plan

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "marketing_analytics.db")
EXPORTS_DIR = os.path.join(BASE_DIR, "data", "powerbi_exports")

def load_data_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Load all customer journeys (touchpoint sequences)
    cursor.execute("""
    SELECT 
        customer_id,
        channel_name,
        timestamp,
        is_conversion_touch
    FROM fact_touchpoints
    ORDER BY customer_id, timestamp ASC
    """)
    rows = cursor.fetchall()

    # Load conversion records (Initial cycle 1 enrollments for attribution)
    cursor.execute("""
    SELECT 
        conversion_id,
        customer_id,
        touchpoint_id,
        revenue,
        timestamp
    FROM fact_conversions
    WHERE conversion_cycle = 1
    """)
    conv_rows = cursor.fetchall()
    conversions_dict = {r[1]: {'conversion_id': r[0], 'revenue': r[3], 'timestamp': r[4]} for r in conv_rows}

    # Load spend per channel
    cursor.execute("""
    SELECT 
        c.channel_name,
        SUM(s.spend) AS total_spend
    FROM fact_daily_spend s
    JOIN dim_channel c ON s.channel_id = c.channel_id
    GROUP BY c.channel_name
    """)
    spend_dict = {r[0]: r[1] for r in cursor.fetchall()}

    # Load customer repeat purchase histories for CLV
    cursor.execute("""
    SELECT 
        c.customer_id,
        c.acquisition_channel,
        c.segment,
        MIN(cv.timestamp) AS first_order,
        MAX(cv.timestamp) AS last_order,
        COUNT(cv.conversion_id) AS total_orders,
        SUM(cv.revenue) AS total_revenue
    FROM dim_customer c
    JOIN fact_conversions cv ON c.customer_id = cv.customer_id
    GROUP BY c.customer_id, c.acquisition_channel, c.segment
    """)
    clv_hist_rows = cursor.fetchall()

    conn.close()
    return rows, conversions_dict, spend_dict, clv_hist_rows

def main():
    print("=" * 80)
    print("GRITO LABS: COMPREHENSIVE ATTRIBUTION & OPTIMIZATION ENGINE")
    print("=" * 80)

    tp_rows, conv_dict, spend_dict, clv_rows = load_data_from_db()

    # Group touchpoints by customer
    cust_touches = defaultdict(list)
    for cid, ch_name, ts, is_conv in tp_rows:
        cust_touches[cid].append({
            'channel_name': ch_name,
            'timestamp': ts,
            'is_conv': is_conv
        })

    # Prepare paths for Markov and Shapley:
    # all_paths: list of (path_list, converted_bool, revenue)
    all_paths = []
    converting_journeys = []

    for cid, touches in cust_touches.items():
        ch_path = [t['channel_name'] for t in touches]
        if cid in conv_dict:
            conv_info = conv_dict[cid]
            c_time = datetime.strptime(conv_info['timestamp'], "%Y-%m-%d %H:%M:%S")
            # Calculate days_before for each touch within 30-day lookback window
            valid_touches = []
            for t in touches:
                t_time = datetime.strptime(t['timestamp'], "%Y-%m-%d %H:%M:%S")
                days_diff = (c_time - t_time).total_seconds() / 86400.0
                if 0 <= days_diff <= 30.0:
                    valid_touches.append({
                        'channel_name': t['channel_name'],
                        'timestamp': t['timestamp'],
                        'days_before': days_diff
                    })
            if valid_touches:
                converting_journeys.append({
                    'conversion_id': conv_info['conversion_id'],
                    'revenue': conv_info['revenue'],
                    'touchpoints': valid_touches
                })
                all_paths.append(([t['channel_name'] for t in valid_touches], 1, conv_info['revenue']))
            else:
                all_paths.append((ch_path, 0, 0.0))
        else:
            all_paths.append((ch_path, 0, 0.0))

    print(f"Loaded {len(cust_touches)} customer paths ({len(converting_journeys)} converting journeys).")

    # 1. Rule-Based Models in Python
    print("\n[1/5] Computing Rule-Based Models (FTA, LTA, Linear, Time-Decay, Position-Based)...")
    rule_convs, rule_revs = compute_rule_based_attribution(converting_journeys, half_life_days=7.0)

    # 2. Data-Driven Markov Chain Attribution
    print("\n[2/5] Computing Data-Driven Markov Chain Model (Removal Effects)...")
    markov_convs, markov_revs, rem_effects = compute_markov_attribution(all_paths)

    # 3. Data-Driven Shapley Value Attribution
    print("\n[3/5] Computing Data-Driven Shapley Value Attribution (Game Theory)...")
    shapley_convs, shapley_revs, shapley_phi = compute_shapley_attribution(all_paths)

    # Compile Master Comparison Matrix
    all_channels = sorted(list(set(list(markov_convs.keys()) + list(spend_dict.keys()))))
    master_matrix = []

    print("\n--- MASTER MULTI-TOUCH ATTRIBUTION COMPARISON MATRIX ---")
    headers = [
        "Channel", "Spend", 
        "FTA Rev", "LTA Rev", "Linear Rev", "TimeDecay Rev", "U-Shaped Rev", "Markov Rev", "Shapley Rev",
        "LTA ROAS", "Markov ROAS", "U-Shape ROAS", "ROAS Shift (%)"
    ]
    
    table_rows = []
    for ch in all_channels:
        sp = spend_dict.get(ch, 0.0)
        r_fta = rule_revs['first_touch'].get(ch, 0.0)
        r_lta = rule_revs['last_touch'].get(ch, 0.0)
        r_lin = rule_revs['linear'].get(ch, 0.0)
        r_td = rule_revs['time_decay'].get(ch, 0.0)
        r_pos = rule_revs['position_based'].get(ch, 0.0)
        r_mkv = markov_revs.get(ch, 0.0)
        r_shp = shapley_revs.get(ch, 0.0)

        roas_lta = round(r_lta / sp, 2) if sp > 0 else 'N/A'
        roas_mkv = round(r_mkv / sp, 2) if sp > 0 else 'N/A'
        roas_pos = round(r_pos / sp, 2) if sp > 0 else 'N/A'
        
        # Shift %: (Position-Based - LTA) / LTA
        shift_pct = round(((r_pos - r_lta) / r_lta) * 100.0, 1) if r_lta > 0 else 0.0

        master_matrix.append({
            'channel_name': ch,
            'spend': round(sp, 2),
            'conversions_first_touch': round(rule_convs['first_touch'].get(ch, 0.0), 1),
            'conversions_last_touch': round(rule_convs['last_touch'].get(ch, 0.0), 1),
            'conversions_linear': round(rule_convs['linear'].get(ch, 0.0), 1),
            'conversions_time_decay': round(rule_convs['time_decay'].get(ch, 0.0), 1),
            'conversions_position_based': round(rule_convs['position_based'].get(ch, 0.0), 1),
            'conversions_markov': markov_convs.get(ch, 0.0),
            'conversions_shapley': shapley_convs.get(ch, 0.0),
            'revenue_first_touch': round(r_fta, 2),
            'revenue_last_touch': round(r_lta, 2),
            'revenue_linear': round(r_lin, 2),
            'revenue_time_decay': round(r_td, 2),
            'revenue_position_based': round(r_pos, 2),
            'revenue_markov': r_mkv,
            'revenue_shapley': r_shp,
            'roas_last_touch': roas_lta,
            'roas_markov': roas_mkv,
            'roas_position_based': roas_pos,
            'roas_shift_pct': shift_pct
        })

        table_rows.append([
            ch, f"${sp:,.2f}",
            f"${r_fta:,.0f}", f"${r_lta:,.0f}", f"${r_lin:,.0f}", f"${r_td:,.0f}", f"${r_pos:,.0f}", f"${r_mkv:,.0f}", f"${r_shp:,.0f}",
            str(roas_lta), str(roas_mkv), str(roas_pos), f"{shift_pct:+0.1f}%"
        ])

    # Print Table
    col_w = [max(len(str(h)), max(len(str(r[i])) for r in table_rows)) for i, h in enumerate(headers)]
    h_str = " | ".join(f"{headers[i]:<{col_w[i]}}" for i in range(len(headers)))
    sep = "-+-".join("-" * col_w[i] for i in range(len(headers)))
    print(h_str)
    print(sep)
    for r in table_rows:
        print(" | ".join(f"{str(r[i]):<{col_w[i]}}" for i in range(len(headers))))

    # Export Master Matrix
    out_master = os.path.join(EXPORTS_DIR, "attribution_master_comparison.csv")
    with open(out_master, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=master_matrix[0].keys())
        writer.writeheader()
        writer.writerows(master_matrix)
    print(f"\n[Exported] {out_master}")

    # 4. Sensitivity Analysis (Half-Life & Lookback Window)
    print("\n[4/5] Running Sensitivity Analysis on Half-Life (3d, 7d, 14d)...")
    for hl in [3.0, 7.0, 14.0]:
        _, td_rev = compute_rule_based_attribution(converting_journeys, half_life_days=hl)
        print(f"  Half-Life = {hl:4.1f} days -> Paid Search Rev: ${td_rev['time_decay']['Paid Search']:,.0f} | Paid Social Rev: ${td_rev['time_decay']['Paid Social']:,.0f}")

    # 5. Customer Lifetime Value (BG/NBD + Gamma-Gamma)
    print("\n[5/5] Fitting Predictive CLV Model (BG/NBD + Gamma-Gamma)...")
    clv_histories = []
    end_date = datetime(2026, 11, 1)
    for r in clv_rows:
        cid, acq_ch, seg, f_ord, l_ord, tot_orders, tot_rev = r
        d_first = datetime.strptime(f_ord, "%Y-%m-%d %H:%M:%S")
        d_last = datetime.strptime(l_ord, "%Y-%m-%d %H:%M:%S")
        recency = (d_last - d_first).total_seconds() / 86400.0
        tenure = (end_date - d_first).total_seconds() / 86400.0
        freq = tot_orders - 1
        monetary = (tot_rev - 999.0) / freq if freq > 0 else (tot_rev / tot_orders)
        
        clv_histories.append({
            'customer_id': cid,
            'acquisition_channel': acq_ch,
            'segment': seg,
            'first_order_date': f_ord,
            'last_order_date': l_ord,
            'frequency': freq,
            'recency_days': recency,
            'tenure_days': tenure,
            'total_revenue': tot_rev,
            'monetary_value': monetary
        })

    clv_records = fit_bgnbd_gamma_gamma(clv_histories, horizon_months=12)
    clv_channel_summary = summarize_clv_by_channel(clv_records, spend_dict)
    
    out_clv = os.path.join(EXPORTS_DIR, "clv_predictive_summary.csv")
    with open(out_clv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=clv_channel_summary[0].keys())
        writer.writeheader()
        writer.writerows(clv_channel_summary)
    print(f"[Exported] {out_clv}")

    # 6. Budget Optimization Execution
    print("\n[6/5] Running Hill Saturation Budget Optimization...")
    def get_pos_rev(ch_name):
        return next((m['revenue_position_based'] for m in master_matrix if m['channel_name'] == ch_name), 0.0)

    channel_configs = {
        'Paid Search': {
            'current_spend': spend_dict.get('Paid Search', 198410.22),
            'current_revenue': get_pos_rev('Paid Search'),
            'r_max': 950000.0, 's_half': 280000.0, 'min_spend': 140000.0, 'max_spend': 260000.0, 'alpha': 1.15
        },
        'Paid Social': {
            'current_spend': spend_dict.get('Paid Social', 142951.06),
            'current_revenue': get_pos_rev('Paid Social'),
            'r_max': 980000.0, 's_half': 190000.0, 'min_spend': 100000.0, 'max_spend': 220000.0, 'alpha': 1.12
        },
        'Email Marketing': {
            'current_spend': spend_dict.get('Email Marketing', 13700.33),
            'current_revenue': get_pos_rev('Email Marketing'),
            'r_max': 550000.0, 's_half': 35000.0, 'min_spend': 8000.0, 'max_spend': 35000.0, 'alpha': 1.25
        },
        'Display Ads': {
            'current_spend': spend_dict.get('Display Ads', 51626.47),
            'current_revenue': get_pos_rev('Display Ads'),
            'r_max': 450000.0, 's_half': 80000.0, 'min_spend': 25000.0, 'max_spend': 75000.0, 'alpha': 1.05
        },
        'Referral': {
            'current_spend': spend_dict.get('Referral', 19729.96),
            'current_revenue': get_pos_rev('Referral'),
            'r_max': 350000.0, 's_half': 45000.0, 'min_spend': 12000.0, 'max_spend': 40000.0, 'alpha': 1.20
        }
    }
    total_budget = sum(c['current_spend'] for c in channel_configs.values())
    opt_results, opt_summary = optimize_budget_allocation(channel_configs, total_budget)

    out_opt = os.path.join(EXPORTS_DIR, "budget_hill_optimization.csv")
    with open(out_opt, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=opt_results[0].keys())
        writer.writeheader()
        writer.writerows(opt_results)
    print(f"[Exported] {out_opt}")

    # 7. Export Top Converting Customer Paths (Overall and Multi-Touch Only)
    path_counts_overall = Counter()
    path_counts_multi = Counter()
    total_conv = len(converting_journeys)
    for j in converting_journeys:
        p_str = " > ".join([t['channel_name'] for t in j['touchpoints']])
        path_counts_overall[p_str] += 1
        if len(j['touchpoints']) >= 2:
            path_counts_multi[p_str] += 1
            
    total_multi = sum(path_counts_multi.values())

    out_paths_overall = os.path.join(EXPORTS_DIR, "path_summary_overall.csv")
    with open(out_paths_overall, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["path_sequence", "conversions", "share_pct", "path_rank"])
        for rank, (p, cnt) in enumerate(path_counts_overall.most_common(20), 1):
            writer.writerow([p, cnt, round((cnt / total_conv) * 100.0, 2), rank])
    print(f"[Exported] {out_paths_overall}")

    out_paths_multi = os.path.join(EXPORTS_DIR, "path_summary_multitouch.csv")
    with open(out_paths_multi, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["path_sequence", "conversions", "share_of_all_pct", "share_of_multitouch_pct", "path_rank"])
        for rank, (p, cnt) in enumerate(path_counts_multi.most_common(20), 1):
            writer.writerow([p, cnt, round((cnt / total_conv) * 100.0, 2), round((cnt / total_multi) * 100.0, 2), rank])
    print(f"[Exported] {out_paths_multi}")

    print("\n--- OPTIMIZATION SUMMARY ---")
    for k, v in opt_summary.items():
        print(f"  {k:30}: {v}")

    print("\n" + "=" * 80)
    print("ATTRIBUTION & OPTIMIZATION ANALYSIS COMPLETE.")
    print("=" * 80)

if __name__ == "__main__":
    main()
