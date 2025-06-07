import json

# Load test cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Analyze the specific high-error cases
high_error_cases = [
    (5, 516, 1878.49, 669.85),   # Case 711
    (1, 1082, 1809.49, 446.94), # Case 996  
    (8, 795, 1645.99, 644.69),  # Case 684
    (14, 481, 939.99, 877.17),  # Case 520
    (5, 195.73, 1228.49, 511.23), # Case 115
]

print("HIGH-ERROR CASE ANALYSIS:")
print("=" * 50)

for days, miles, receipts, expected in high_error_cases:
    # Calculate what a "normal" trip would get
    base_estimate = days * 75 + miles * 0.58  # Conservative estimate
    
    # See how much the receipts are contributing (could be negative)
    receipt_effect = expected - base_estimate
    receipt_ratio = receipt_effect / receipts if receipts > 0 else 0
    
    efficiency = miles / days if days > 0 else 0
    
    print(f"{days}d, {miles}mi, ${receipts:.2f} → ${expected:.2f}")
    print(f"  Efficiency: {efficiency:.1f} mi/day")
    print(f"  Base estimate: ${base_estimate:.2f}")
    print(f"  Receipt effect: ${receipt_effect:.2f}")
    print(f"  Receipt ratio: {receipt_ratio:.3f}")
    print()

# Look for patterns in high-receipt cases that get low reimbursements
print("HIGH RECEIPTS WITH LOW OUTPUTS:")
print("-" * 40)

low_output_high_receipt = []
for case in cases:
    receipts = case['input']['total_receipts_amount']
    output = case['expected_output']
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    
    if receipts > 1500:  # High receipts
        base_estimate = days * 75 + miles * 0.58
        if output < base_estimate:  # Output is lower than base estimate
            low_output_high_receipt.append({
                'days': days,
                'miles': miles,
                'receipts': receipts,
                'output': output,
                'base_est': base_estimate,
                'penalty': base_estimate - output
            })

# Sort by penalty (highest penalty first)
low_output_high_receipt.sort(key=lambda x: x['penalty'], reverse=True)

print("TOP 10 HIGH-RECEIPT PENALTY CASES:")
for i, case in enumerate(low_output_high_receipt[:10]):
    efficiency = case['miles'] / case['days'] if case['days'] > 0 else 0
    print(f"{i+1}. {case['days']}d, {case['miles']}mi ({efficiency:.1f} mi/day), ${case['receipts']:.2f}")
    print(f"   Expected: ${case['output']:.2f}, Base est: ${case['base_est']:.2f}")
    print(f"   Penalty: ${case['penalty']:.2f}")

# Look for patterns in efficiency vs receipts
print(f"\nEFFICIENCY VS RECEIPT PATTERNS:")
print("-" * 30)

efficiency_buckets = {
    'very_low': [],    # < 30 mi/day
    'low': [],         # 30-60 mi/day  
    'medium': [],      # 60-100 mi/day
    'high': [],        # 100+ mi/day
}

for case in cases:
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    output = case['expected_output']
    
    if days > 0 and receipts > 1000:  # Focus on high-receipt cases
        efficiency = miles / days
        base_estimate = days * 75 + miles * 0.58
        receipt_effect = output - base_estimate
        receipt_ratio = receipt_effect / receipts
        
        if efficiency < 30:
            bucket = 'very_low'
        elif efficiency < 60:
            bucket = 'low'
        elif efficiency < 100:
            bucket = 'medium'
        else:
            bucket = 'high'
            
        efficiency_buckets[bucket].append(receipt_ratio)

for bucket, ratios in efficiency_buckets.items():
    if ratios:
        avg_ratio = sum(ratios) / len(ratios)
        print(f"{bucket.upper()} efficiency: {len(ratios)} cases, avg receipt ratio: {avg_ratio:.3f}") 