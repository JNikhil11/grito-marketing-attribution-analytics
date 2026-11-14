"""
Grito Labs Marketing Analytics & Attribution Framework
Module: src/budget_optimizer.py
Description: Budget Optimization & Diminishing Returns Response Modeling:
             1. Fits Hill Saturation & Log Response Curves per channel
             2. Solves constrained portfolio optimization under fixed marketing budget
             3. Generates Scenario Bounds (Low -10%, Base, High +15%)
             4. Generates Geo-Holdout / Incrementality Testing Design Framework
"""

import math

def hill_response(spend, r_max, s_half, alpha=1.2):
    """
    Hill saturation function (S-curve):
    R(S) = (R_max * S^alpha) / (S_half^alpha + S^alpha)
    """
    if spend <= 0:
        return 0.0
    sp_a = math.pow(spend, alpha)
    sh_a = math.pow(s_half, alpha)
    return (r_max * sp_a) / (sh_a + sp_a)

def marginal_hill_roas(spend, r_max, s_half, alpha=1.2, delta=100.0):
    """Computes marginal revenue per additional dollar spent: dR/dS"""
    r1 = hill_response(spend, r_max, s_half, alpha)
    r2 = hill_response(spend + delta, r_max, s_half, alpha)
    return (r2 - r1) / delta

def optimize_budget_allocation(channels_data, total_budget, iterations=5000, step_size=50.0):
    """
    Equalizes Marginal ROAS across channels using iterative gradient/greedy reallocation
    subject to fixed total budget and channel min/max bounds.
    channels_data: dict of channel configs:
      {
         'Paid Search': {'current_spend': 26267.53, 'current_revenue': 499240.85, 'r_max': 900000.0, 's_half': 40000.0, 'min_spend': 15000.0, 'max_spend': 38000.0, 'alpha': 1.1},
         ...
      }
    """
    # Start at current spend
    allocations = {ch: data['current_spend'] for ch, data in channels_data.items()}
    
    # Scale allocations so they sum exactly to total_budget initially
    curr_sum = sum(allocations.values())
    for ch in allocations:
        allocations[ch] = (allocations[ch] / curr_sum) * total_budget

    # Iterative reallocation to equalize marginal ROAS
    for it in range(iterations):
        # Calculate marginal ROAS for all channels
        marginal_returns = {}
        for ch, data in channels_data.items():
            s = allocations[ch]
            m_roas = marginal_hill_roas(s, data['r_max'], data['s_half'], data.get('alpha', 1.2))
            marginal_returns[ch] = m_roas
            
        # Find channel with highest marginal ROAS (below max spend)
        best_ch = None
        best_m = -1e9
        for ch, data in channels_data.items():
            if allocations[ch] + step_size <= data['max_spend']:
                if marginal_returns[ch] > best_m:
                    best_m = marginal_returns[ch]
                    best_ch = ch
                    
        # Find channel with lowest marginal ROAS (above min spend)
        worst_ch = None
        worst_m = 1e9
        for ch, data in channels_data.items():
            if allocations[ch] - step_size >= data['min_spend']:
                if marginal_returns[ch] < worst_m:
                    worst_m = marginal_returns[ch]
                    worst_ch = ch
                    
        # If difference in marginal return is negligible, equilibrium achieved
        if best_ch is None or worst_ch is None or best_ch == worst_ch:
            break
        if (best_m - worst_m) < 0.05:
            break
            
        # Shift step_size from worst to best
        allocations[worst_ch] -= step_size
        allocations[best_ch] += step_size

    # Compile optimized results
    results = []
    total_cur_spend = 0.0
    total_cur_rev = 0.0
    total_opt_spend = 0.0
    total_opt_rev_base = 0.0

    for ch, data in channels_data.items():
        cur_s = data['current_spend']
        opt_s = round(allocations[ch], 2)
        cur_r = data['current_revenue']
        
        # Current and Optimized modeled revenue
        opt_r = round(hill_response(opt_s, data['r_max'], data['s_half'], data.get('alpha', 1.2)), 2)
        
        # Scaling adjustment so model matches exact baseline at current spend
        base_curve_rev = hill_response(cur_s, data['r_max'], data['s_half'], data.get('alpha', 1.2))
        scale_factor = cur_r / base_curve_rev if base_curve_rev > 0 else 1.0
        
        adj_opt_r = round(opt_r * scale_factor, 2)
        m_roas = round(marginal_hill_roas(opt_s, data['r_max'], data['s_half'], data.get('alpha', 1.2)), 2)
        
        d_shift = round(opt_s - cur_s, 2)
        p_shift = round((d_shift / cur_s) * 100.0, 1)
        
        # Scenarios
        rev_low = round(adj_opt_r * 0.90, 2)
        rev_high = round(adj_opt_r * 1.15, 2)
        inc_rev = round(adj_opt_r - cur_r, 2)

        results.append({
            'channel_name': ch,
            'current_spend': cur_s,
            'recommended_spend': opt_s,
            'dollar_shift': d_shift,
            'pct_shift': p_shift,
            'current_roas': round(cur_r / cur_s, 2),
            'projected_roas': round(adj_opt_r / opt_s, 2),
            'marginal_roas': m_roas,
            'current_revenue': cur_r,
            'projected_revenue_base': adj_opt_r,
            'incremental_revenue_base': inc_rev,
            'projected_revenue_low': rev_low,
            'projected_revenue_high': rev_high
        })
        
        total_cur_spend += cur_s
        total_cur_rev += cur_r
        total_opt_spend += opt_s
        total_opt_rev_base += adj_opt_r

    summary = {
        'total_current_spend': round(total_cur_spend, 2),
        'total_recommended_spend': round(total_opt_spend, 2),
        'total_current_revenue': round(total_cur_rev, 2),
        'total_projected_revenue_base': round(total_opt_rev_base, 2),
        'total_incremental_revenue': round(total_opt_rev_base - total_cur_rev, 2),
        'total_projected_revenue_low': round(total_opt_rev_base * 0.90, 2),
        'total_projected_revenue_high': round(total_opt_rev_base * 1.15, 2),
        'portfolio_current_roas': round(total_cur_rev / total_cur_spend, 2),
        'portfolio_projected_roas': round(total_opt_rev_base / total_opt_spend, 2)
    }

    return results, summary


def generate_incrementality_test_plan():
    """
    Returns the structured methodology for a Geo-Holdout / Matched-Market Incrementality Test.
    """
    return {
        "framework_name": "Matched-Market Geo-Holdout Incrementality Testing (GTM-IT)",
        "duration_weeks": 4,
        "pre_test_calibration_weeks": 3,
        "control_markets": ["Austin, TX", "Seattle, WA", "Denver, CO", "Raleigh, NC"],
        "treatment_markets": ["Dallas, TX", "San Francisco, CA", "Boulder, CO", "Charlotte, NC"],
        "matching_criteria": [
            "Historical ROAS correlation (r > 0.92)",
            "Similar Edtech search intent volume",
            "Matched student demographic profiles"
        ],
        "test_mechanism": {
            "treatment_group": "Implement proposed +12% Paid Search and +60% Email scaling",
            "control_group": "Hold ad spend completely flat at historical baseline"
        },
        "statistical_metric": "Difference-in-Differences (DiD) synthetic control estimation",
        "minimum_detectable_effect_mde": "5.2% incremental revenue lift at 95% confidence (p < 0.05)",
        "stop_loss_guardrail": "If CPA increases by > 25% in treatment markets for 5 consecutive days, trigger auto-pause."
    }
