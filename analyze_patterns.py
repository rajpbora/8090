import json

# Load test cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Analyze high-error cases specifically
high_error_patterns = [
    (8, 795, 1645.99, 644.69),   # Case 684
    (14, 1056, 2489.69, 1894.16), # Case 242
    (14, 481, 939.99, 877.17),    # Case 520
    (5, 516, 1878.49, 669.85),    # Case 711
    (4, 69, 2321.49, 322.00),     # Case 152
]

print("HIGH-ERROR CASE ANALYSIS:")
print("=" * 50)

for days, miles, receipts, expected in high_error_patterns:
    mileage_component = miles * 0.58
    remaining = expected - mileage_component
    base_per_day = remaining / days if days > 0 else 0
    receipt_contribution = remaining - (base_per_day * days)
    
    print(f"{days}d, {miles}mi, ${receipts:.2f} → ${expected:.2f}")
    print(f"  Mileage (${miles} × 0.58): ${mileage_component:.2f}")
    print(f"  Remaining after mileage: ${remaining:.2f}")
    print(f"  Implied base per day: ${base_per_day:.2f}")
    print(f"  Receipt contribution: ${receipt_contribution:.2f}")
    if receipts > 0:
        receipt_ratio = receipt_contribution / receipts
        print(f"  Receipt ratio: {receipt_ratio:.3f}")
    print()

# Analyze patterns by trip length for low-receipt cases
print("LOW-RECEIPT CASES BY TRIP LENGTH:")
print("=" * 40)

by_days = {}
for case in cases:
    receipts = case['input']['total_receipts_amount']
    if receipts < 30:  # Focus on low-receipt cases
        days = case['input']['trip_duration_days']
        if days not in by_days:
            by_days[days] = []
        by_days[days].append({
            'miles': case['input']['miles_traveled'],
            'receipts': receipts,
            'output': case['expected_output']
        })

for days in sorted(by_days.keys())[:10]:  # First 10 day lengths
    if len(by_days[days]) >= 3:
        avg_output = sum(c['output'] for c in by_days[days]) / len(by_days[days])
        avg_miles = sum(c['miles'] for c in by_days[days]) / len(by_days[days])
        avg_receipts = sum(c['receipts'] for c in by_days[days]) / len(by_days[days])
        
        # Remove mileage component to see base rate
        avg_mileage_component = avg_miles * 0.58
        avg_base = avg_output - avg_mileage_component
        base_per_day = avg_base / days
        
        print(f"{days}-day trips (low receipts): avg total=${avg_output:.2f}")
        print(f"  After mileage: ${avg_base:.2f}, per day: ${base_per_day:.2f}")

# Analyze receipt scaling for various amounts
print("\nRECEIPT SCALING ANALYSIS:")
print("=" * 30)

receipt_ranges = [
    (0, 10), (10, 30), (30, 100), (100, 300), 
    (300, 1000), (1000, 2000), (2000, 5000)
]

for min_r, max_r in receipt_ranges:
    matching_cases = []
    for case in cases:
        receipts = case['input']['total_receipts_amount']
        if min_r <= receipts < max_r:
            days = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            output = case['expected_output']
            
            # Estimate what the output should be without receipts
            base_estimate = days * 100 + miles * 0.58  # Rough estimate
            receipt_contribution = output - base_estimate
            
            matching_cases.append({
                'receipts': receipts,
                'contribution': receipt_contribution,
                'ratio': receipt_contribution / receipts if receipts > 0 else 0
            })
    
    if matching_cases:
        avg_ratio = sum(c['ratio'] for c in matching_cases) / len(matching_cases)
        print(f"Receipts ${min_r}-${max_r}: {len(matching_cases)} cases, avg ratio: {avg_ratio:.3f}") 