"""
Verify processed dialogue counts against expected (student, week, task) plan.
"""
from pathlib import Path
from collections import defaultdict

# Expected counts per student per week (from user-provided table)
EXPECTED = {
    18: {1: 3},
    12: {1: 2, 2: 3, 3: 2, 4: 2},
    16: {1: 3, 2: 3, 3: 3, 4: 3},
    14: {1: 3, 2: 3, 3: 3, 4: 3},
    1: {1: 2, 2: 3, 3: 4, 4: 3},
    2: {1: 2, 2: 2, 3: 2, 4: 2},
    5: {1: 2, 2: 2, 3: 2, 4: 2},
    7: {1: 3, 2: 2, 3: 2, 4: 2},
    8: {1: 2, 2: 3, 3: 3, 4: 3},
    9: {1: 2, 2: 2, 3: 2, 4: 2},
    13: {1: 3, 2: 2, 3: 2, 4: 2},
    17: {1: 2, 2: 3, 3: 3, 4: 3},
    20: {1: 3, 2: 3, 3: 3, 4: 3},
    21: {1: 3, 2: 3, 3: 3, 4: 2},
    23: {1: 3, 2: 3, 3: 4, 4: 2},
    24: {1: 2, 2: 2, 3: 2, 4: 2},
    25: {1: 2, 2: 2, 3: 2, 4: 2},
    28: {1: 3, 2: 3, 3: 3, 4: 3},
    40: {1: 2, 2: 2, 3: 2, 4: 2},
    30: {1: 3, 2: 3, 3: 3, 4: 3},
    34: {1: 3, 2: 3, 3: 3, 4: 2},
}


def load_processed_counts(processed_dir: Path) -> dict:
    counts = defaultdict(lambda: defaultdict(list))
    for path in processed_dir.glob("S*_W*_T*.json"):
        stem = path.stem
        try:
            student_part, week_part, task_part = stem.split("_")
            student = int(student_part[1:])
            week = int(week_part[1:])
        except Exception:
            continue
        counts[student][week].append(stem)
    return counts


def main():
    processed_dir = Path("data/processed")
    counts = load_processed_counts(processed_dir)

    missing = []
    extra = []

    print("Processed dialogue counts vs expected:\n")
    for student in sorted(EXPECTED):
        print(f"Student {student}:")
        for week in sorted(EXPECTED[student]):
            expected = EXPECTED[student][week]
            actual_list = counts.get(student, {}).get(week, [])
            actual = len(actual_list)
            status = "OK" if actual == expected else "MISMATCH"
            print(f"  Week {week}: expected {expected}, actual {actual} -> {status}")
            if actual < expected:
                missing.append((student, week, expected, actual))
            elif actual > expected:
                extra.append((student, week, expected, actual))
        print()

    if missing:
        print("Missing task files:")
        for student, week, expected, actual in missing:
            print(f"  Student {student} Week {week}: expected {expected}, actual {actual}")
    else:
        print("No missing task files.")

    if extra:
        print("\nUnexpected extra task files:")
        for student, week, expected, actual in extra:
            print(f"  Student {student} Week {week}: expected {expected}, actual {actual}")


if __name__ == "__main__":
    main()

