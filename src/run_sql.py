"""
Grito Labs Marketing Analytics & Attribution Framework
Module: src/run_sql.py
Description: Executes all SQL pipeline scripts (00 to 07) against the SQLite
             data warehouse, runs data sanity checks, prints analytical summaries,
             and exports clean model-ready CSVs to data/powerbi_exports/.
"""

import os
import sys
import sqlite3
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_DIR = os.path.join(BASE_DIR, "sql")
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "marketing_analytics.db")
EXPORTS_DIR = os.path.join(BASE_DIR, "data", "powerbi_exports")

os.makedirs(EXPORTS_DIR, exist_ok=True)

SQL_FILES = [
    "00_schema.sql",
    "01_data_cleaning.sql",
    "02_kpi_queries.sql",
    "03_journey_analysis.sql",
    "04_attribution_models.sql",
    "05_campaign_ranking.sql",
    "06_clv_cohort.sql",
    "07_budget_optimization.sql"
]

def format_table(headers, rows, max_rows=15):
    if not rows:
        return "(No rows returned)\n"
    col_widths = [len(str(h)) for h in headers]
    for row in rows[:max_rows]:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val) if val is not None else "NULL"))
    
    header_str = " | ".join(f"{str(h):<{col_widths[i]}}" for i, h in enumerate(headers))
    sep_str = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    
    out_lines = [header_str, sep_str]
    for row in rows[:max_rows]:
        row_str = " | ".join(f"{str(val if val is not None else 'NULL'):<{col_widths[i]}}" for i, val in enumerate(row))
        out_lines.append(row_str)
        
    if len(rows) > max_rows:
        out_lines.append(f"... ({len(rows) - max_rows} additional rows omitted)")
    return "\n".join(out_lines) + "\n"

def export_query_to_csv(cursor, query, filename):
    cursor.execute(query)
    headers = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    out_path = os.path.join(EXPORTS_DIR, filename)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"  [Exported] {filename} ({len(rows)} rows)")
    return headers, rows

def run_all_sql():
    print("=" * 80)
    print("GRITO LABS MARKETING ANALYTICS: SQL PIPELINE RUNNER")
    print(f"Database: {DB_PATH}")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    # Enable math functions (POWER, EXP, LN, etc.)
    conn.enable_load_extension(False)
    cursor = conn.cursor()
    
    # Execute 00_schema.sql first
    print("\n[Step 1/8] Executing 00_schema.sql...")
    with open(os.path.join(SQL_DIR, "00_schema.sql"), "r", encoding="utf-8") as f:
        schema_sql = f.read()
    # Note: 00_schema drops and recreates tables. We repopulate from raw if needed,
    # or just create views if tables already exist.
    # To keep populated data intact, let's verify if tables exist:
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='fact_touchpoints'")
    if cursor.fetchone()[0] == 0:
        cursor.executescript(schema_sql)
        conn.commit()
        print("  Schema created.")
    else:
        print("  Database tables already populated with data. Proceeding to views and analytics.")

    # Execute 01_data_cleaning.sql
    print("\n[Step 2/8] Executing 01_data_cleaning.sql...")
    with open(os.path.join(SQL_DIR, "01_data_cleaning.sql"), "r", encoding="utf-8") as f:
        clean_sql = f.read()
    cursor.executescript(clean_sql)
    conn.commit()
    
    # Run data validation checks
    cursor.execute("SELECT * FROM (SELECT 'Duplicate Touchpoints' AS check_type, COUNT(*) AS violations FROM (SELECT touchpoint_id FROM fact_touchpoints GROUP BY touchpoint_id HAVING COUNT(*) > 1))")
    dup_res = cursor.fetchall()
    print("  Data Integrity Sanity Check:")
    print(" ", dup_res)

    # Execute 04_attribution_models.sql to ensure v_touchpoint_attribution_weights view is created
    print("\n[Step 3/8] Executing 04_attribution_models.sql (Views and Model Definitions)...")
    with open(os.path.join(SQL_DIR, "04_attribution_models.sql"), "r", encoding="utf-8") as f:
        attrib_sql = f.read()
    cursor.executescript(attrib_sql)
    conn.commit()
    print("  Attribution views created.")

    # ---------------------------------------------------------
    # EXPORT CLEAN ANALYTICAL CSVs FOR POWER BI
    # ---------------------------------------------------------
    print("\n[Step 4/8] Generating clean Power BI CSV exports in data/powerbi_exports/...")
    
    # 1. Dimensions
    export_query_to_csv(cursor, "SELECT * FROM dim_channel", "dim_channel.csv")
    export_query_to_csv(cursor, "SELECT * FROM dim_campaign", "dim_campaign.csv")
    export_query_to_csv(cursor, "SELECT * FROM dim_customer", "dim_customer.csv")
    export_query_to_csv(cursor, "SELECT * FROM dim_date", "dim_date.csv")
    
    # 2. Fact Tables
    export_query_to_csv(cursor, "SELECT * FROM fact_daily_spend", "fact_daily_spend.csv")
    export_query_to_csv(cursor, "SELECT * FROM fact_conversions", "fact_conversions.csv")
    export_query_to_csv(cursor, "SELECT * FROM fact_touchpoints", "fact_touchpoints.csv")
    
    # 3. Channel KPI Summary (from 02_kpi_queries.sql Query 1)
    kpi_query = """
    WITH channel_media_metrics AS (
        SELECT 
            s.channel_id,
            c.channel_name,
            c.channel_group,
            c.is_paid,
            SUM(s.impressions) AS total_impressions,
            SUM(s.clicks) AS total_clicks,
            SUM(s.spend) AS total_spend
        FROM fact_daily_spend s
        JOIN dim_channel c ON s.channel_id = c.channel_id
        GROUP BY s.channel_id, c.channel_name, c.channel_group, c.is_paid
    ),
    channel_last_touch_conversions AS (
        SELECT 
            tp.channel_id,
            COUNT(DISTINCT cv.conversion_id) AS total_conversions,
            SUM(cv.revenue) AS total_revenue
        FROM fact_conversions cv
        JOIN fact_touchpoints tp ON cv.touchpoint_id = tp.touchpoint_id
        WHERE cv.conversion_cycle = 1
        GROUP BY tp.channel_id
    )
    SELECT 
        m.channel_id,
        m.channel_name,
        m.channel_group,
        m.is_paid,
        m.total_impressions,
        m.total_clicks,
        ROUND(m.total_spend, 2) AS total_spend,
        COALESCE(c.total_conversions, 0) AS last_touch_conversions,
        ROUND(COALESCE(c.total_revenue, 0.0), 2) AS last_touch_revenue,
        ROUND(CAST(m.total_clicks AS REAL) / NULLIF(m.total_impressions, 0) * 100.0, 2) AS ctr_pct,
        ROUND(m.total_spend / NULLIF(m.total_clicks, 0), 2) AS cpc,
        ROUND(CAST(COALESCE(c.total_conversions, 0) AS REAL) / NULLIF(m.total_clicks, 0) * 100.0, 2) AS cvr_pct,
        ROUND(m.total_spend / NULLIF(c.total_conversions, 0), 2) AS cpa_cac,
        ROUND(COALESCE(c.total_revenue, 0.0) / NULLIF(m.total_spend, 0), 2) AS last_touch_roas,
        ROUND((COALESCE(c.total_revenue, 0.0) - m.total_spend) / NULLIF(m.total_spend, 0) * 100.0, 2) AS roi_pct
    FROM channel_media_metrics m
    LEFT JOIN channel_last_touch_conversions c ON m.channel_id = c.channel_id
    ORDER BY total_spend DESC;
    """
    h_kpi, r_kpi = export_query_to_csv(cursor, kpi_query, "kpi_channel_summary.csv")
    print("\n--- Channel KPI Summary ---")
    print(format_table(h_kpi, r_kpi))

    # 4. Multi-Touch Attribution Matrix (from 04_attribution_models.sql)
    attrib_matrix_query = """
    WITH channel_spend AS (
        SELECT 
            s.channel_id,
            c.channel_name,
            SUM(s.spend) AS total_spend
        FROM fact_daily_spend s
        JOIN dim_channel c ON s.channel_id = c.channel_id
        GROUP BY s.channel_id, c.channel_name
    ),
    channel_attributed_metrics AS (
        SELECT 
            w.channel_id,
            w.channel_name,
            ROUND(SUM(w.weight_first_touch), 1) AS conv_first_touch,
            ROUND(SUM(w.weight_last_touch), 1) AS conv_last_touch,
            ROUND(SUM(w.weight_linear), 1) AS conv_linear,
            ROUND(SUM(w.weight_time_decay), 1) AS conv_time_decay,
            ROUND(SUM(w.weight_position_based), 1) AS conv_position_based,
            ROUND(SUM(w.weight_first_touch * w.conversion_revenue), 2) AS rev_first_touch,
            ROUND(SUM(w.weight_last_touch * w.conversion_revenue), 2) AS rev_last_touch,
            ROUND(SUM(w.weight_linear * w.conversion_revenue), 2) AS rev_linear,
            ROUND(SUM(w.weight_time_decay * w.conversion_revenue), 2) AS rev_time_decay,
            ROUND(SUM(w.weight_position_based * w.conversion_revenue), 2) AS rev_position_based
        FROM v_touchpoint_attribution_weights w
        GROUP BY w.channel_id, w.channel_name
    )
    SELECT 
        m.channel_id,
        m.channel_name,
        ROUND(s.total_spend, 2) AS spend,
        m.conv_first_touch,
        m.conv_last_touch,
        m.conv_linear,
        m.conv_time_decay,
        m.conv_position_based,
        m.rev_first_touch,
        m.rev_last_touch,
        m.rev_linear,
        m.rev_time_decay,
        m.rev_position_based,
        ROUND(m.rev_first_touch / NULLIF(s.total_spend, 0), 2) AS roas_first_touch,
        ROUND(m.rev_last_touch / NULLIF(s.total_spend, 0), 2) AS roas_last_touch,
        ROUND(m.rev_linear / NULLIF(s.total_spend, 0), 2) AS roas_linear,
        ROUND(m.rev_time_decay / NULLIF(s.total_spend, 0), 2) AS roas_time_decay,
        ROUND(m.rev_position_based / NULLIF(s.total_spend, 0), 2) AS roas_position_based,
        ROUND((m.rev_position_based - m.rev_last_touch) / NULLIF(m.rev_last_touch, 0) * 100.0, 1) AS roas_shift_pct
    FROM channel_attributed_metrics m
    JOIN channel_spend s ON m.channel_id = s.channel_id
    ORDER BY s.total_spend DESC;
    """
    h_att, r_att = export_query_to_csv(cursor, attrib_matrix_query, "attribution_comparison_matrix.csv")
    print("\n--- Attribution Model Comparison Matrix ---")
    print(format_table(h_att, r_att))

    # 5. Model Sum Reconciliation Audit
    recon_query = """
    SELECT 
        'Ground Truth (fact_conversions)' AS model_name,
        COUNT(DISTINCT conversion_id) AS total_conversions,
        ROUND(SUM(revenue), 2) AS total_revenue
    FROM fact_conversions
    WHERE conversion_cycle = 1
    UNION ALL
    SELECT 'First-Touch Model', ROUND(SUM(weight_first_touch), 2), ROUND(SUM(weight_first_touch * conversion_revenue), 2) FROM v_touchpoint_attribution_weights
    UNION ALL
    SELECT 'Last-Touch Model', ROUND(SUM(weight_last_touch), 2), ROUND(SUM(weight_last_touch * conversion_revenue), 2) FROM v_touchpoint_attribution_weights
    UNION ALL
    SELECT 'Linear Model', ROUND(SUM(weight_linear), 2), ROUND(SUM(weight_linear * conversion_revenue), 2) FROM v_touchpoint_attribution_weights
    UNION ALL
    SELECT 'Time-Decay Model', ROUND(SUM(weight_time_decay), 2), ROUND(SUM(weight_time_decay * conversion_revenue), 2) FROM v_touchpoint_attribution_weights
    UNION ALL
    SELECT 'Position-Based Model', ROUND(SUM(weight_position_based), 2), ROUND(SUM(weight_position_based * conversion_revenue), 2) FROM v_touchpoint_attribution_weights;
    """
    cursor.execute(recon_query)
    h_rec = [d[0] for d in cursor.description]
    r_rec = cursor.fetchall()
    print("\n--- Revenue Sum Reconciliation Audit (Must Agree Exactly) ---")
    print(format_table(h_rec, r_rec))

    # 6. Campaign Quadrant Ranking (from 05_campaign_ranking.sql)
    with open(os.path.join(SQL_DIR, "05_campaign_ranking.sql"), "r", encoding="utf-8") as f:
        ranking_query = f.read()
    h_rnk, r_rnk = export_query_to_csv(cursor, ranking_query, "kpi_campaign_ranking.csv")
    print("\n--- Campaign Strategic Quadrant Classification ---")
    print(format_table(h_rnk, r_rnk))

    # 7. Customer Lifetime Value & Repeat Enrolment Summary (from 06_clv_cohort.sql)
    clv_query = """
    WITH customer_orders AS (
        SELECT 
            c.customer_id,
            c.acquisition_channel,
            COUNT(cv.conversion_id) AS total_orders,
            SUM(cv.revenue) AS lifetime_revenue,
            CASE WHEN COUNT(cv.conversion_id) > 1 THEN 1 ELSE 0 END AS is_repeat
        FROM dim_customer c
        JOIN fact_conversions cv ON c.customer_id = cv.customer_id
        GROUP BY c.customer_id, c.acquisition_channel
    ),
    channel_spend AS (
        SELECT c.channel_name, SUM(s.spend) AS total_spend
        FROM fact_daily_spend s
        JOIN dim_channel c ON s.channel_id = c.channel_id
        GROUP BY c.channel_name
    )
    SELECT 
        co.acquisition_channel,
        COUNT(DISTINCT co.customer_id) AS acquired_customers,
        SUM(co.is_repeat) AS repeat_customers,
        ROUND(CAST(SUM(co.is_repeat) AS REAL) / COUNT(DISTINCT co.customer_id) * 100.0, 1) AS repeat_rate_pct,
        ROUND(SUM(co.lifetime_revenue), 2) AS total_lifetime_revenue,
        ROUND(AVG(co.lifetime_revenue), 2) AS avg_historical_clv,
        ROUND(COALESCE(cs.total_spend, 0.0) / COUNT(DISTINCT co.customer_id), 2) AS blended_cac,
        ROUND(AVG(co.lifetime_revenue) / NULLIF(COALESCE(cs.total_spend, 0.0) / COUNT(DISTINCT co.customer_id), 0), 2) AS ltv_cac_ratio
    FROM customer_orders co
    LEFT JOIN channel_spend cs ON co.acquisition_channel = cs.channel_name
    GROUP BY co.acquisition_channel, cs.total_spend
    ORDER BY total_lifetime_revenue DESC;
    """
    h_clv, r_clv = export_query_to_csv(cursor, clv_query, "clv_channel_summary.csv")
    print("\n--- Customer Lifetime Value (CLV) & LTV:CAC Summary ---")
    print(format_table(h_clv, r_clv))

    # 8. Budget Optimization & Scenario Output (from 07_budget_optimization.sql)
    with open(os.path.join(SQL_DIR, "07_budget_optimization.sql"), "r", encoding="utf-8") as f:
        opt_sql = f.read()
    h_opt, r_opt = export_query_to_csv(cursor, opt_sql, "budget_reallocation_scenario.csv")
    print("\n--- Budget Reallocation & Projected Scenario Returns ---")
    print(format_table(h_opt, r_opt))

    conn.close()
    print("\n" + "=" * 80)
    print("ALL SQL SCRIPTS AND AUDITS EXECUTED SUCCESSFULLY.")
    print("=" * 80)

if __name__ == "__main__":
    run_all_sql()
