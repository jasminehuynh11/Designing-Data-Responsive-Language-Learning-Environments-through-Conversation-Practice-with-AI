"""Quick script to find missing task files based on expected counts."""
from pathlib import Path

# Expected counts from user's table
expected = {
    (18, 1): 3,
    (12, 2): 3,
    (16, 3): 3,
    (14, 4): 3,
    (1, 1): 2, (1, 2): 3, (1, 3): 4, (1, 4): 3,
    (2, 1): 2, (2, 2): 2, (2, 3): 2, (2, 4): 2,
    (5, 1): 2, (5, 2): 2, (5, 3): 2, (5, 4): 2,
    (7, 1): 3, (7, 2): 2, (7, 3): 2, (7, 4): 2,
    (8, 1): 2, (8, 2): 3, (8, 3): 3, (8, 4): 3,
    (9, 1): 2, (9, 2): 2, (9, 3): 2, (9, 4): 2,
    (12, 1): 2, (12, 3): 2, (12, 4): 2,
    (13, 1): 3, (13, 2): 2, (13, 3): 2, (13, 4): 2,
    (16, 1): 3, (16, 2): 3, (16, 4): 3,
    (17, 1): 2, (17, 2): 3, (17, 3): 3, (17, 4): 3,
    (20, 1): 3, (20, 2): 3, (20, 3): 3, (20, 4): 3,
    (21, 1): 3, (21, 2): 3, (21, 3): 3, (21, 4): 2,
    (23, 1): 3, (23, 2): 3, (23, 3): 4, (23, 4): 2,
    (24, 1): 2, (24, 2): 2, (24, 3): 2, (24, 4): 2,
    (25, 1): 2, (25, 2): 2, (25, 3): 2, (25, 4): 2,
    (28, 1): 3, (28, 2): 3, (28, 3): 3, (28, 4): 3,
    (40, 1): 2, (40, 2): 2, (40, 3): 2, (40, 4): 2,
    (14, 1): 3, (14, 2): 3, (14, 3): 3,
    (30, 1): 3, (30, 2): 3, (30, 3): 3, (30, 4): 3,
    (34, 1): 3, (34, 2): 3, (34, 3): 3, (34, 4): 2,
}

processed_dir = Path('data/processed')
missing = []

for (student, week), expected_count in expected.items():
    existing = list(processed_dir.glob(f'S{student}_W{week}_T*.json'))
    existing_count = len(existing)
    
    if existing_count < expected_count:
        existing_tasks = sorted([int(f.stem.split('_T')[1]) for f in existing])
        missing_tasks = [t for t in range(1, expected_count + 1) if t not in existing_tasks]
        missing.append({
            'student': student,
            'week': week,
            'expected': expected_count,
            'found': existing_count,
            'missing_tasks': missing_tasks
        })
        print(f"S{student}_W{week}: Expected {expected_count}, found {existing_count}, missing tasks: {missing_tasks}")

print(f"\nTotal missing: {len(missing)} cases")
print("\nMissing files:")
for m in missing:
    for task in m['missing_tasks']:
        print(f"  S{m['student']}_W{m['week']}_T{task}.json")

