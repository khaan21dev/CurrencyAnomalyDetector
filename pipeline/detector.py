def analyze_rate(pair, rate, change_percent, previous_rate):
    
    # Rule 1 - Rate velocity (MiFID II)
    if abs(change_percent) > 1.5:
        severity = "HIGH" if abs(change_percent) > 3 else "MEDIUM"
        return {
            'rule': f'Rate velocity breach - moved {change_percent:.2f}% in 10 minutes',
            'severity': severity
        }
    
    # Rule 2 - Psychological level crossing (MAR)
    psychological_levels = [4.10, 4.15, 4.20, 4.25, 4.30, 4.35, 4.40]
    if previous_rate:
        for level in psychological_levels:
            if (previous_rate < level <= rate) or (previous_rate > level >= rate):
                return {
                    'rule': f'Psychological level {level} crossed',
                    'severity': 'MEDIUM'
                }
    
    # Rule 3 - Structuring detection (AML)
    round_numbers = [0.20, 0.25, 0.30, 0.35, 0.40]
    for round_num in round_numbers:
        if round_num - 0.001 <= rate <= round_num - 0.0001:
            return {
                'rule': f'Structuring detected - rate just below {round_num}',
                'severity': 'LOW'
            }
    
    return None
