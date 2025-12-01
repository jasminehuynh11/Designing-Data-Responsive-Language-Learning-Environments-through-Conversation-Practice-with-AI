"""Quick verification script to check data structure before Phase 2."""
import json
from pathlib import Path

processed_dir = Path('data/processed')
json_files = sorted(processed_dir.glob('S*_W*_T*.json'))

print("=" * 70)
print("DATA STRUCTURE VERIFICATION")
print("=" * 70)
print(f"\nTotal dialogue files: {len(json_files)}")

# Sample a few files
print("\nSample files (first 5):")
for file_path in json_files[:5]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"  {file_path.name}:")
    print(f"    - {len(data.get('turns', []))} turns")
    print(f"    - Student {data.get('student_id')}, Week {data.get('week')}, Task {data.get('task')}")
    print(f"    - Dialogue ID: {data.get('dialogue_id')}")
    print(f"    - Has metadata: {all(k in data for k in ['student_id', 'week', 'task', 'dialogue_id', 'turns'])}")

# Count total turns
total_turns = 0
for file_path in json_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        total_turns += len(data.get('turns', []))

print(f"\nTotal turns across all files: {total_turns}")

# Check for required fields
print("\nChecking required fields...")
missing_fields = []
for file_path in json_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        required = ['student_id', 'week', 'task', 'dialogue_id', 'turns']
        missing = [f for f in required if f not in data]
        if missing:
            missing_fields.append((file_path.name, missing))

if missing_fields:
    print(f"  [WARNING] {len(missing_fields)} files missing required fields:")
    for name, fields in missing_fields[:5]:
        print(f"    - {name}: missing {fields}")
else:
    print("  [OK] All files have required fields")

# Check turn structure
print("\nChecking turn structure...")
turn_issues = []
for file_path in json_files[:20]:  # Sample first 20
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        turns = data.get('turns', [])
        for i, turn in enumerate(turns, 1):
            if 'turn' not in turn or 'speaker' not in turn or 'text' not in turn:
                turn_issues.append((file_path.name, i, [k for k in ['turn', 'speaker', 'text'] if k not in turn]))

if turn_issues:
    print(f"  [WARNING] {len(turn_issues)} turn structure issues found")
else:
    print("  [OK] Turn structure looks good (sampled 20 files)")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\nReady for Phase 2 (Repair Detection)!")

