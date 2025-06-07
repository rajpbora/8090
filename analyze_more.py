import json

# Load test cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("DETAILED RECEIPT ANALYSIS")
print("=" * 40)

# Analyze high receipt cases more carefully
high_receipt_cases = []
for case in cases:
    receipts = case['input']['total_receipts_amount']
    if receipts > 1000:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        output = case['expected_output']
        
        # Calculate what the output would be with no receipts
        # Using a very conservative base estimate
        if days <= 3:
            base_per_day = 100
        elif days <= 5:
            base_per_day = 75
        elif days <= 8:
            base_per_day = 50
        else:
            base_per_day = 30
            
        mileage_component = miles * 0.58
        base_component = days * base_per_day
        no_receipt_estimate = base_component + mileage_component
        
        receipt_contribution = output - no_receipt_estimate
        receipt_ratio = receipt_contribution / receipts if receipts > 0 else 0
        
        high_receipt_cases.append({
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'output': output,
            'no_receipt_est': no_receipt_estimate,
            'receipt_contrib': receipt_contribution,
            'ratio': receipt_ratio
        })

# Sort by receipt amount
high_receipt_cases.sort(key=lambda x: x['receipts'])

print("HIGH RECEIPT CASES (>$1000):")
for i, case in enumerate(high_receipt_cases[:20]):  # Show first 20
    print(f"{case['days']}d, {case['miles']}mi, ${case['receipts']:.2f} → ${case['output']:.2f}")
    print(f"  Est without receipts: ${case['no_receipt_est']:.2f}")
    print(f"  Receipt contribution: ${case['receipt_contrib']:.2f}")
    print(f"  Receipt ratio: {case['ratio']:.4f}")
    print()

# Check if there are cases where high receipts lead to LOWER total reimbursement
print("LOOKING FOR RECEIPT PENALTIES:")
print("-" * 30)

# Group similar trips and see if higher receipts lead to lower totals
similar_trips = {}
for case in cases:
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    
    # Create a key for "similar" trips (within 20% mileage and same days)
    mile_bucket = round(miles / 50) * 50  # Round to nearest 50
    key = f"{days}d_{mile_bucket}mi"
    
    if key not in similar_trips:
        similar_trips[key] = []
    
    similar_trips[key].append({
        'receipts': case['input']['total_receipts_amount'],
        'output': case['expected_output'],
        'exact_miles': miles
    })

# Look for patterns where higher receipts lead to lower outputs
penalty_evidence = []
for key, trips in similar_trips.items():
    if len(trips) >= 3:  # Need at least 3 similar trips
        # Sort by receipt amount
        trips.sort(key=lambda x: x['receipts'])
        
        # Check if higher receipts lead to lower outputs
        for i in range(len(trips) - 1):
            lower_receipt = trips[i]
            higher_receipt = trips[i + 1]
            
            if (higher_receipt['receipts'] > lower_receipt['receipts'] * 1.5 and
                higher_receipt['output'] < lower_receipt['output']):
                penalty_evidence.append({
                    'key': key,
                    'low': lower_receipt,
                    'high': higher_receipt
                })

print("EVIDENCE OF RECEIPT PENALTIES:")
for evidence in penalty_evidence[:10]:  # Show first 10
    print(f"{evidence['key']}:")
    print(f"  Low receipts: ${evidence['low']['receipts']:.2f} → ${evidence['low']['output']:.2f}")
    print(f"  High receipts: ${evidence['high']['receipts']:.2f} → ${evidence['high']['output']:.2f}")
    print(f"  Higher receipts led to ${evidence['high']['output'] - evidence['low']['output']:.2f} LOWER reimbursement")
    print() 