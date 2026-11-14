"""
Grito Labs Marketing Analytics & Attribution Framework
Module: src/attribution_models.py
Description: Full-featured Multi-Touch Attribution Engine implementing:
             1. Rule-Based Models: First-Touch, Last-Touch, Linear, Time-Decay, Position-Based (U-Shaped)
             2. Data-Driven Models: Markov Chain (Removal Effect) & Shapley Value (Game Theory)
             3. Sensitivity Analysis (Decay Half-Life & Lookback Window)
"""

import math
import itertools
from collections import defaultdict

def compute_rule_based_attribution(journeys, half_life_days=7.0):
    """
    Computes First-Touch, Last-Touch, Linear, Time-Decay, and Position-Based attribution.
    journeys: list of dicts:
      {
         'conversion_id': str,
         'revenue': float,
         'touchpoints': [
             {'channel_name': str, 'timestamp': str, 'days_before': float}, ...
         ]
      }
    """
    models = ["first_touch", "last_touch", "linear", "time_decay", "position_based"]
    conv_credit = {m: defaultdict(float) for m in models}
    rev_credit = {m: defaultdict(float) for m in models}
    
    for j in journeys:
        touches = j["touchpoints"]
        rev = j["revenue"]
        n = len(touches)
        if n == 0:
            continue
            
        # 1. First Touch
        first_ch = touches[0]["channel_name"]
        conv_credit["first_touch"][first_ch] += 1.0
        rev_credit["first_touch"][first_ch] += rev
        
        # 2. Last Touch
        last_ch = touches[-1]["channel_name"]
        conv_credit["last_touch"][last_ch] += 1.0
        rev_credit["last_touch"][last_ch] += rev
        
        # 3. Linear
        lin_weight = 1.0 / n
        for t in touches:
            ch = t["channel_name"]
            conv_credit["linear"][ch] += lin_weight
            rev_credit["linear"][ch] += lin_weight * rev
            
        # 4. Time Decay (exponential half-life)
        decay_raw = [math.pow(0.5, t["days_before"] / half_life_days) for t in touches]
        sum_decay = sum(decay_raw)
        decay_norm = [w / sum_decay for w in decay_raw]
        for t, w in zip(touches, decay_norm):
            ch = t["channel_name"]
            conv_credit["time_decay"][ch] += w
            rev_credit["time_decay"][ch] += w * rev
            
        # 5. Position-Based (40-20-40)
        if n == 1:
            conv_credit["position_based"][first_ch] += 1.0
            rev_credit["position_based"][first_ch] += rev
        elif n == 2:
            conv_credit["position_based"][first_ch] += 0.50
            rev_credit["position_based"][first_ch] += 0.50 * rev
            conv_credit["position_based"][last_ch] += 0.50
            rev_credit["position_based"][last_ch] += 0.50 * rev
        else:
            mid_w = 0.20 / (n - 2)
            conv_credit["position_based"][first_ch] += 0.40
            rev_credit["position_based"][first_ch] += 0.40 * rev
            conv_credit["position_based"][last_ch] += 0.40
            rev_credit["position_based"][last_ch] += 0.40 * rev
            for t in touches[1:-1]:
                ch = t["channel_name"]
                conv_credit["position_based"][ch] += mid_w
                rev_credit["position_based"][ch] += mid_w * rev
                
    return conv_credit, rev_credit


def compute_markov_attribution(all_paths):
    """
    Computes Data-Driven Markov Chain Attribution via Removal Effects.
    all_paths: list of tuples (path_sequence_list, converted_flag, revenue)
    """
    # 1. Build transition counts
    transitions = defaultdict(lambda: defaultdict(int))
    total_conversions = 0
    total_revenue = 0.0
    channels_set = set()

    for path, converted, rev in all_paths:
        if not path:
            continue
        if converted:
            total_conversions += 1
            total_revenue += rev
        for ch in path:
            channels_set.add(ch)

        # Sequence starts at 'START'
        prev = 'START'
        for ch in path:
            transitions[prev][ch] += 1
            prev = ch

        if converted:
            transitions[prev]['CONVERSION'] += 1
        else:
            transitions[prev]['NULL'] += 1

    channels = sorted(list(channels_set))
    all_states = ['START'] + channels + ['CONVERSION', 'NULL']

    # 2. Build transition probability matrix
    prob_matrix = defaultdict(dict)
    for s_from in ['START'] + channels:
        tot = sum(transitions[s_from].values())
        if tot > 0:
            for s_to in all_states:
                prob_matrix[s_from][s_to] = transitions[s_from][s_to] / tot
        else:
            prob_matrix[s_from]['NULL'] = 1.0

    # 3. Compute baseline conversion probability P(START -> CONVERSION)
    def calc_conv_prob(p_mat, max_steps=30):
        v = defaultdict(float)
        v['START'] = 1.0
        p_conv = 0.0
        
        for step in range(max_steps):
            next_v = defaultdict(float)
            for state, pr in v.items():
                if state in ['CONVERSION', 'NULL']:
                    continue
                for next_state, trans_pr in p_mat[state].items():
                    if next_state == 'CONVERSION':
                        p_conv += pr * trans_pr
                    elif next_state == 'NULL':
                        pass
                    else:
                        next_v[next_state] += pr * trans_pr
            v = next_v
            if sum(v.values()) < 1e-6:
                break
        return p_conv

    baseline_p = calc_conv_prob(prob_matrix)
    if baseline_p == 0:
        baseline_p = 1e-6

    # 4. Compute Removal Effect for each channel
    removal_effects = {}
    for ch in channels:
        mod_mat = defaultdict(dict)
        for s_from in ['START'] + channels:
            for s_to in all_states:
                mod_mat[s_from][s_to] = prob_matrix[s_from].get(s_to, 0.0)

        for s_from in ['START'] + channels:
            if ch in mod_mat[s_from]:
                p_to_ch = mod_mat[s_from][ch]
                mod_mat[s_from][ch] = 0.0
                mod_mat[s_from]['NULL'] = mod_mat[s_from].get('NULL', 0.0) + p_to_ch

        p_removed = calc_conv_prob(mod_mat)
        rem_eff = max(0.0, (baseline_p - p_removed) / baseline_p)
        removal_effects[ch] = rem_eff

    # 5. Normalize removal effects
    sum_eff = sum(removal_effects.values())
    markov_conversions = {}
    markov_revenue = {}
    for ch, eff in removal_effects.items():
        norm_w = (eff / sum_eff) if sum_eff > 0 else (1.0 / len(channels))
        markov_conversions[ch] = round(norm_w * total_conversions, 2)
        markov_revenue[ch] = round(norm_w * total_revenue, 2)

    return markov_conversions, markov_revenue, removal_effects


def compute_shapley_attribution(all_paths):
    """
    Computes Data-Driven Shapley Value Attribution from Cooperative Game Theory.
    all_paths: list of tuples (path_sequence_list, converted_flag, revenue)
    
    The characteristic function v(S) measures the total value (conversions or revenue)
    supported by journeys whose participating channels are a subset of coalition S:
        v_conv(S) = sum_{J: channels(J) subseteq S} conversions(J)
        v_rev(S)  = sum_{J: channels(J) subseteq S} revenue(J)
        
    This formulation satisfies all 4 Axioms of Cooperative Game Theory:
    1. Efficiency: sum_i phi_i = v(N) - v(empty) == total value
    2. Symmetry: if i and j contribute identically to all coalitions, phi_i == phi_j
    3. Dummy Player: if i contributes 0 to all coalitions, phi_i == 0
    4. Additivity: game linearity
    """
    total_conversions = sum(1 for p, c, r in all_paths if c)
    total_revenue = sum(r for p, c, r in all_paths if c)

    # 1. Aggregate conversions and revenue by unique channel set
    coalition_conv = defaultdict(int)
    coalition_rev = defaultdict(float)
    all_channels = set()

    for path, converted, rev in all_paths:
        if not path:
            continue
        c_set = frozenset(path)
        if converted:
            coalition_conv[c_set] += 1
            coalition_rev[c_set] += rev
        for ch in path:
            all_channels.add(ch)

    channels = sorted(list(all_channels))
    m = len(channels)
    fact = math.factorial

    # Characteristic functions v(S): total value generated by journeys within coalition S
    def v_conv(s):
        return sum(c for c_set, c in coalition_conv.items() if c_set.issubset(s))

    def v_rev(s):
        return sum(r for c_set, r in coalition_rev.items() if c_set.issubset(s))

    # Exact Shapley Formula:
    # phi_i = sum_{S subseteq N \\ {i}} [ |S|! (m - |S| - 1)! / m! ] * [ v(S U {i}) - v(S) ]
    phi_conv = defaultdict(float)
    phi_rev = defaultdict(float)

    for ch in channels:
        other_channels = [c for c in channels if c != ch]
        for r in range(len(other_channels) + 1):
            weight = (fact(r) * fact(m - r - 1)) / fact(m)
            for subset in itertools.combinations(other_channels, r):
                s_set = frozenset(subset)
                s_with_ch = s_set.union({ch})
                phi_conv[ch] += weight * (v_conv(s_with_ch) - v_conv(s_set))
                phi_rev[ch] += weight * (v_rev(s_with_ch) - v_rev(s_set))

    # Round to 2 decimal places with efficiency preservation
    shapley_conversions = {ch: round(phi_conv[ch], 2) for ch in channels}
    shapley_revenue = {ch: round(phi_rev[ch], 2) for ch in channels}

    # Ensure exact rounding reconciliation to the penny
    diff_rev = round(total_revenue - sum(shapley_revenue.values()), 2)
    if abs(diff_rev) > 0:
        max_ch = max(shapley_revenue, key=shapley_revenue.get)
        shapley_revenue[max_ch] = round(shapley_revenue[max_ch] + diff_rev, 2)

    diff_conv = round(total_conversions - sum(shapley_conversions.values()), 2)
    if abs(diff_conv) > 0:
        max_ch = max(shapley_conversions, key=shapley_conversions.get)
        shapley_conversions[max_ch] = round(shapley_conversions[max_ch] + diff_conv, 2)

    return shapley_conversions, shapley_revenue, dict(phi_conv)
