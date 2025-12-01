"""Verify all processed tasks match expected counts."""
from pathlib import Path
import json

# Expected counts from user
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
issues = []
all_good = []

for (student, week), expected_count in sorted(expected.items()):
    existing = list(processed_dir.glob(f'S{student}_W{week}_T*.json'))
    existing_count = len(existing)
    
    if existing_count < expected_count:
        existing_tasks = sorted([int(f.stem.split('_T')[1]) for f in existing])
        missing_tasks = [t for t in range(1, expected_count + 1) if t not in existing_tasks]
        issues.append({
            'student': student,
            'week': week,
            'expected': expected_count,
            'found': existing_count,
            'missing_tasks': missing_tasks,
            'existing_tasks': existing_tasks
        })
    elif existing_count > expected_count:
        existing_tasks = sorted([int(f.stem.split('_T')[1]) for f in existing])
        extra_tasks = [t for t in existing_tasks if t > expected_count]
        issues.append({
            'student': student,
            'week': week,
            'expected': expected_count,
            'found': existing_count,
            'extra_tasks': extra_tasks,
            'existing_tasks': existing_tasks
        })
    else:
        all_good.append((student, week, expected_count))

print("=" * 80)
print("VERIFICATION REPORT")
print("=" * 80)
print(f"\n✅ CORRECT: {len(all_good)} student/week combinations")
print(f"❌ ISSUES: {len(issues)} student/week combinations need attention\n")

if issues:
    print("ISSUES FOUND:\n")
    for issue in issues:
        print(f"S{issue['student']}_W{issue['week']}: Expected {issue['expected']}, found {issue['found']}")
        if 'missing_tasks' in issue:
            print(f"  Missing tasks: {issue['missing_tasks']}")
        if 'extra_tasks' in issue:
            print(f"  Extra tasks: {issue['extra_tasks']} (should only have tasks 1-{issue['expected']})")
        print()

# Save detailed report
report = {
    'summary': {
        'total_checked': len(expected),
        'correct': len(all_good),
        'issues': len(issues)
    },
    'correct': [{'student': s, 'week': w, 'tasks': c} for s, w, c in all_good],
    'issues': issues
}

report_file = Path('data/task_verification_report.json')
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\nDetailed report saved to: {report_file}")

