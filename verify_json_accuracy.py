"""
Verification script to cross-check JSON files against extracted text.
"""
import json
from pathlib import Path
import re

def check_timestamps(text):
    """Check if timestamps are present in text."""
    timestamp_pattern = r'\d{1,2}:\d{2}'
    return bool(re.search(timestamp_pattern, text))

def verify_week1():
    """Verify Week 1 JSON against extracted text."""
    print("="*60)
    print("VERIFYING WEEK 1")
    print("="*60)
    
    # Read extracted text
    with open('data/extracted_text/week1_extracted.txt', 'r', encoding='utf-8') as f:
        extracted = f.read()
    
    # Read JSON
    with open('data/processed/W1_T1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    turns = data['turns']
    
    print(f"\nW1_T1.json: {len(turns)} turns")
    print(f"Student ID: {data['student_id']}")
    
    # Check for timestamps
    timestamp_count = 0
    for turn in turns:
        if check_timestamps(turn['text']):
            timestamp_count += 1
            print(f"  ⚠️  Turn {turn['turn']} contains timestamp: {turn['text'][:50]}...")
    
    if timestamp_count == 0:
        print("  ✅ No timestamps found in JSON")
    else:
        print(f"  ⚠️  Found {timestamp_count} turns with timestamps")
    
    # Check first few turns
    print("\nFirst 5 turns verification:")
    extracted_lines = extracted.split('\n')
    json_idx = 0
    
    for i, line in enumerate(extracted_lines[:30]):
        if 'You said:' in line or 'English Conversational Partner said:' in line:
            if json_idx < len(turns):
                json_turn = turns[json_idx]
                expected_speaker = 'learner' if 'You said' in line else 'bot'
                actual_speaker = json_turn['speaker']
                
                if expected_speaker != actual_speaker:
                    print(f"  ❌ Turn {json_turn['turn']}: Expected {expected_speaker}, got {actual_speaker}")
                else:
                    print(f"  ✅ Turn {json_turn['turn']}: {actual_speaker} - {json_turn['text'][:50]}...")
                json_idx += 1
    
    return timestamp_count == 0

def verify_week2():
    """Verify Week 2 JSON against extracted text."""
    print("\n" + "="*60)
    print("VERIFYING WEEK 2")
    print("="*60)
    
    with open('data/extracted_text/week2_extracted.txt', 'r', encoding='utf-8') as f:
        extracted = f.read()
    
    with open('data/processed/W2_T1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    turns = data['turns']
    
    print(f"\nW2_T1.json: {len(turns)} turns")
    print(f"Student ID: {data['student_id']}")
    
    # Check for timestamps
    timestamp_count = 0
    for turn in turns:
        if check_timestamps(turn['text']):
            timestamp_count += 1
    
    if timestamp_count == 0:
        print("  ✅ No timestamps found")
    else:
        print(f"  ⚠️  Found {timestamp_count} turns with timestamps")
    
    # Check full-width colon handling
    print("\nChecking full-width colon handling:")
    extracted_lines = extracted.split('\n')
    json_idx = 0
    
    for i, line in enumerate(extracted_lines[:30]):
        if 'You said：' in line or 'English Conversational Partner said：' in line:
            if json_idx < len(turns):
                json_turn = turns[json_idx]
                expected_speaker = 'learner' if 'You said' in line else 'bot'
                actual_speaker = json_turn['speaker']
                
                if expected_speaker == actual_speaker:
                    print(f"  ✅ Turn {json_turn['turn']}: Correctly parsed full-width colon")
                json_idx += 1
    
    return timestamp_count == 0

def verify_week3():
    """Verify Week 3 JSON against extracted text."""
    print("\n" + "="*60)
    print("VERIFYING WEEK 3")
    print("="*60)
    
    with open('data/extracted_text/week3_extracted.txt', 'r', encoding='utf-8') as f:
        extracted = f.read()
    
    with open('data/processed/W3_T1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    turns = data['turns']
    
    print(f"\nW3_T1.json: {len(turns)} turns")
    print(f"Student ID: {data['student_id']}")
    
    # Check Portuguese labels
    print("\nChecking Portuguese label parsing:")
    extracted_lines = extracted.split('\n')
    json_idx = 0
    
    for i, line in enumerate(extracted_lines[:30]):
        if 'Você disse:' in line or 'English Conversational Partner disse:' in line:
            if json_idx < len(turns):
                json_turn = turns[json_idx]
                expected_speaker = 'learner' if 'Você disse' in line else 'bot'
                actual_speaker = json_turn['speaker']
                
                if expected_speaker == actual_speaker:
                    print(f"  ✅ Turn {json_turn['turn']}: Correctly parsed Portuguese label")
                else:
                    print(f"  ❌ Turn {json_turn['turn']}: Expected {expected_speaker}, got {actual_speaker}")
                json_idx += 1
    
    return True

def verify_week4():
    """Verify Week 4 JSON against extracted text."""
    print("\n" + "="*60)
    print("VERIFYING WEEK 4")
    print("="*60)
    
    with open('data/extracted_text/week4_extracted.txt', 'r', encoding='utf-8') as f:
        extracted = f.read()
    
    with open('data/processed/W4_T1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    turns = data['turns']
    
    print(f"\nW4_T1.json: {len(turns)} turns")
    print(f"Student ID: {data['student_id']}")
    
    # Check alternating pattern
    print("\nChecking alternating pattern (learner/bot):")
    errors = 0
    for i, turn in enumerate(turns[:10]):
        expected_speaker = 'learner' if i % 2 == 0 else 'bot'
        actual_speaker = turn['speaker']
        
        if expected_speaker == actual_speaker:
            print(f"  ✅ Turn {turn['turn']}: {actual_speaker} - {turn['text'][:50]}...")
        else:
            print(f"  ❌ Turn {turn['turn']}: Expected {expected_speaker}, got {actual_speaker}")
            errors += 1
    
    # Check if first turn is learner
    if turns[0]['speaker'] == 'learner':
        print("\n  ✅ First turn correctly identified as learner")
    else:
        print("\n  ❌ First turn should be learner")
        errors += 1
    
    return errors == 0

def check_all_files():
    """Check all JSON files exist and have correct structure."""
    print("\n" + "="*60)
    print("CHECKING ALL FILES")
    print("="*60)
    
    expected_files = [
        'W1_T1.json', 'W1_T2.json', 'W1_T3.json',
        'W2_T1.json', 'W2_T2.json', 'W2_T3.json',
        'W3_T1.json', 'W3_T2.json', 'W3_T3.json',
        'W4_T1.json', 'W4_T2.json', 'W4_T3.json'
    ]
    
    all_good = True
    for filename in expected_files:
        filepath = Path('data/processed') / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'student_id' in data and 'turns' in data:
                print(f"  ✅ {filename}: {len(data['turns'])} turns, student_id: {data['student_id']}")
            else:
                print(f"  ❌ {filename}: Missing student_id or turns")
                all_good = False
        else:
            print(f"  ❌ {filename}: File not found")
            all_good = False
    
    return all_good

if __name__ == '__main__':
    print("\n" + "="*60)
    print("JSON ACCURACY VERIFICATION")
    print("="*60)
    
    results = []
    results.append(("Week 1", verify_week1()))
    results.append(("Week 2", verify_week2()))
    results.append(("Week 3", verify_week3()))
    results.append(("Week 4", verify_week4()))
    results.append(("All Files", check_all_files()))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")

