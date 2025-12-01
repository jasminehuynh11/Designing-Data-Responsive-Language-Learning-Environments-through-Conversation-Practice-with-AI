"""
Comprehensive validation script for preprocessed dialogue JSON files.

This script performs multiple validation checks:
1. Metadata consistency (filename matches JSON content)
2. Turn structure validation (numbering, speaker labels)
3. Content quality checks (encoding, artifacts)
4. Cross-reference with extracted text
5. Statistical validation (turn counts, speaker distribution)
6. Missing or duplicate detection
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

from document_extractor import extract_text


class ValidationResult:
    """Container for validation results."""
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.issues: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.stats: Dict[str, Any] = {}
    
    def add_issue(self, severity: str, category: str, message: str, details: Optional[Dict] = None):
        """Add a validation issue."""
        self.issues.append({
            "severity": severity,  # "error" or "warning"
            "category": category,
            "message": message,
            "details": details or {}
        })
    
    def add_warning(self, category: str, message: str, details: Optional[Dict] = None):
        """Add a warning."""
        self.warnings.append({
            "category": category,
            "message": message,
            "details": details or {}
        })
    
    def is_valid(self) -> bool:
        """Check if file passed all critical validations."""
        return all(issue["severity"] != "error" for issue in self.issues)


def validate_filename_metadata(json_data: Dict, file_path: Path) -> List[Dict[str, Any]]:
    """Validate that filename matches JSON metadata."""
    issues = []
    filename = file_path.stem  # e.g., "S18_W1_T1"
    
    # Parse filename
    filename_match = re.match(r'S(\d+)_W(\d+)_T(\d+)', filename)
    if not filename_match:
        issues.append({
            "severity": "error",
            "category": "filename_format",
            "message": f"Filename '{filename}' does not match expected pattern S##_W#_T#",
            "details": {"filename": filename}
        })
        return issues
    
    expected_student, expected_week, expected_task = filename_match.groups()
    
    # Check metadata consistency
    if json_data.get("student_id") != int(expected_student):
        issues.append({
            "severity": "error",
            "category": "metadata_mismatch",
            "message": f"student_id mismatch: filename={expected_student}, JSON={json_data.get('student_id')}",
            "details": {"expected": expected_student, "actual": json_data.get("student_id")}
        })
    
    if json_data.get("week") != int(expected_week):
        issues.append({
            "severity": "error",
            "category": "metadata_mismatch",
            "message": f"week mismatch: filename={expected_week}, JSON={json_data.get('week')}",
            "details": {"expected": expected_week, "actual": json_data.get("week")}
        })
    
    if json_data.get("task") != int(expected_task):
        issues.append({
            "severity": "error",
            "category": "metadata_mismatch",
            "message": f"task mismatch: filename={expected_task}, JSON={json_data.get('task')}",
            "details": {"expected": expected_task, "actual": json_data.get("task")}
        })
    
    # Check dialogue_id
    expected_dialogue_id = f"S{expected_student}_W{expected_week}_T{expected_task}"
    if json_data.get("dialogue_id") != expected_dialogue_id:
        issues.append({
            "severity": "error",
            "category": "metadata_mismatch",
            "message": f"dialogue_id mismatch: expected={expected_dialogue_id}, actual={json_data.get('dialogue_id')}",
            "details": {"expected": expected_dialogue_id, "actual": json_data.get("dialogue_id")}
        })
    
    return issues


def validate_turn_structure(turns: List[Dict]) -> List[Dict[str, Any]]:
    """Validate turn structure and numbering."""
    issues = []
    
    if not turns:
        issues.append({
            "severity": "error",
            "category": "empty_dialogue",
            "message": "Dialogue has no turns",
            "details": {}
        })
        return issues
    
    # Check turn numbering
    expected_turn_nums = set(range(1, len(turns) + 1))
    actual_turn_nums = {turn.get("turn") for turn in turns}
    
    missing_turns = expected_turn_nums - actual_turn_nums
    if missing_turns:
        issues.append({
            "severity": "error",
            "category": "turn_numbering",
            "message": f"Missing turn numbers: {sorted(missing_turns)}",
            "details": {"missing": sorted(missing_turns), "total_expected": len(turns)}
        })
    
    extra_turns = actual_turn_nums - expected_turn_nums
    if extra_turns:
        issues.append({
            "severity": "error",
            "category": "turn_numbering",
            "message": f"Extra turn numbers: {sorted(extra_turns)}",
            "details": {"extra": sorted(extra_turns)}
        })
    
    # Check for duplicate turn numbers
    turn_nums = [turn.get("turn") for turn in turns]
    duplicates = [num for num, count in Counter(turn_nums).items() if count > 1]
    if duplicates:
        issues.append({
            "severity": "error",
            "category": "turn_numbering",
            "message": f"Duplicate turn numbers: {duplicates}",
            "details": {"duplicates": duplicates}
        })
    
    # Check speaker labels
    valid_speakers = {"learner", "bot"}
    invalid_speakers = []
    for i, turn in enumerate(turns, 1):
        speaker = turn.get("speaker")
        if speaker not in valid_speakers:
            invalid_speakers.append((i, speaker))
    
    if invalid_speakers:
        issues.append({
            "severity": "error",
            "category": "speaker_labels",
            "message": f"Invalid speaker labels: {invalid_speakers[:5]}",
            "details": {"invalid": invalid_speakers}
        })
    
    # Check for missing text
    empty_turns = []
    for i, turn in enumerate(turns, 1):
        text = turn.get("text", "").strip()
        if not text:
            empty_turns.append(i)
    
    if empty_turns:
        issues.append({
            "severity": "warning",
            "category": "content_quality",
            "message": f"Empty or missing text in turns: {empty_turns[:10]}",
            "details": {"empty_turns": empty_turns}
        })
    
    return issues


def validate_content_quality(turns: List[Dict]) -> List[Dict[str, Any]]:
    """Check for content quality issues."""
    issues = []
    
    # Check for encoding issues (common problematic characters)
    encoding_issues = []
    for i, turn in enumerate(turns, 1):
        text = turn.get("text", "")
        # Check for replacement characters (often indicate encoding issues)
        if '\ufffd' in text or '\uFFFD' in text:
            encoding_issues.append(i)
        # Check for excessive whitespace
        if re.search(r'\s{5,}', text):
            encoding_issues.append(i)
    
    if encoding_issues:
        issues.append({
            "severity": "warning",
            "category": "content_quality",
            "message": f"Potential encoding or formatting issues in turns: {encoding_issues[:10]}",
            "details": {"affected_turns": encoding_issues}
        })
    
    # Check for suspiciously short or long turns
    suspicious_turns = []
    for i, turn in enumerate(turns, 1):
        text = turn.get("text", "").strip()
        if len(text) < 2:  # Very short
            suspicious_turns.append((i, "too_short", len(text)))
        elif len(text) > 2000:  # Very long
            suspicious_turns.append((i, "too_long", len(text)))
    
    if suspicious_turns:
        issues.append({
            "severity": "warning",
            "category": "content_quality",
            "message": f"Suspicious turn lengths: {suspicious_turns[:5]}",
            "details": {"suspicious": suspicious_turns}
        })
    
    return issues


def validate_speaker_alternation(turns: List[Dict]) -> List[Dict[str, Any]]:
    """Check if speaker alternation makes sense."""
    issues = []
    
    if len(turns) < 2:
        return issues
    
    # Count consecutive same-speaker turns
    consecutive_same = []
    for i in range(len(turns) - 1):
        if turns[i].get("speaker") == turns[i + 1].get("speaker"):
            consecutive_same.append((i + 1, i + 2))
    
    if consecutive_same:
        # This is often normal (e.g., bot giving long response), but flag if excessive
        if len(consecutive_same) > len(turns) * 0.3:  # More than 30% consecutive
            issues.append({
                "severity": "warning",
                "category": "speaker_pattern",
                "message": f"Many consecutive same-speaker turns: {len(consecutive_same)} pairs",
                "details": {"consecutive_pairs": consecutive_same[:10]}
            })
    
    return issues


def cross_reference_with_source(json_data: Dict, file_path: Path) -> List[Dict[str, Any]]:
    """Cross-reference JSON content with source extracted text."""
    issues = []
    
    source_file = json_data.get("source_file")
    if not source_file:
        return issues
    
    source_path = PROJECT_ROOT / source_file
    if not source_path.exists():
        issues.append({
            "severity": "warning",
            "category": "source_reference",
            "message": f"Source file not found: {source_file}",
            "details": {"source_file": source_file}
        })
        return issues
    
    try:
        extracted_text = extract_text(str(source_path))
        
        # Check if dialogue turns appear in source text
        turns = json_data.get("turns", [])
        if not turns:
            return issues
        
        # Sample check: verify first few turns appear in source
        found_count = 0
        sample_size = min(5, len(turns))
        
        for turn in turns[:sample_size]:
            turn_text = turn.get("text", "").strip()
            # Remove quotes and normalize whitespace for comparison
            normalized_turn = re.sub(r'["""]', '', turn_text)
            normalized_turn = re.sub(r'\s+', ' ', normalized_turn).strip()
            
            # Check if substantial portion appears in source
            if len(normalized_turn) > 10:
                # Look for key phrases (first 20 chars)
                key_phrase = normalized_turn[:20].lower()
                if key_phrase in extracted_text.lower():
                    found_count += 1
        
        if found_count == 0 and sample_size > 0:
            issues.append({
                "severity": "warning",
                "category": "source_reference",
                "message": "Dialogue turns not found in source text (possible parsing issue)",
                "details": {"checked_turns": sample_size, "found": found_count}
            })
    
    except Exception as e:
        issues.append({
            "severity": "warning",
            "category": "source_reference",
            "message": f"Could not cross-reference with source: {e}",
            "details": {"error": str(e)}
        })
    
    return issues


def validate_json_file(file_path: Path) -> ValidationResult:
    """Validate a single JSON file."""
    result = ValidationResult(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        result.add_issue("error", "json_syntax", f"Invalid JSON: {e}", {"error": str(e)})
        return result
    except Exception as e:
        result.add_issue("error", "file_read", f"Could not read file: {e}", {"error": str(e)})
        return result
    
    # Collect statistics
    turns = json_data.get("turns", [])
    result.stats = {
        "total_turns": len(turns),
        "student_id": json_data.get("student_id"),
        "week": json_data.get("week"),
        "task": json_data.get("task"),
        "dialogue_id": json_data.get("dialogue_id"),
        "speaker_distribution": dict(Counter(turn.get("speaker") for turn in turns))
    }
    
    # Run all validations
    result.issues.extend(validate_filename_metadata(json_data, file_path))
    result.issues.extend(validate_turn_structure(turns))
    result.issues.extend(validate_content_quality(turns))
    result.issues.extend(validate_speaker_alternation(turns))
    result.issues.extend(cross_reference_with_source(json_data, file_path))
    
    return result


def validate_all_files(processed_dir: Path) -> Dict[str, Any]:
    """Validate all JSON files in processed directory."""
    json_files = sorted(processed_dir.glob("S*_W*_T*.json"))
    
    if not json_files:
        return {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "results": []
        }
    
    results = []
    for file_path in json_files:
        result = validate_json_file(file_path)
        results.append(result)
    
    valid_count = sum(1 for r in results if r.is_valid())
    invalid_count = len(results) - valid_count
    
    # Aggregate statistics
    total_turns = sum(r.stats.get("total_turns", 0) for r in results)
    error_count = sum(len([i for i in r.issues if i["severity"] == "error"]) for r in results)
    warning_count = sum(len([i for i in r.issues if i["severity"] == "warning"]) for r in results)
    
    return {
        "total_files": len(results),
        "valid_files": valid_count,
        "invalid_files": invalid_count,
        "total_turns": total_turns,
        "total_errors": error_count,
        "total_warnings": warning_count,
        "results": results
    }


def print_validation_report(summary: Dict[str, Any], verbose: bool = True):
    """Print a formatted validation report."""
    print("=" * 70)
    print("PREPROCESSING VALIDATION REPORT")
    print("=" * 70)
    print(f"\nTotal files validated: {summary['total_files']}")
    print(f"Valid files: {summary['valid_files']}")
    print(f"Files with errors: {summary['invalid_files']}")
    print(f"Total turns: {summary['total_turns']}")
    print(f"Total errors: {summary['total_errors']}")
    print(f"Total warnings: {summary['total_warnings']}")
    
    if not verbose:
        return
    
    # Group issues by category
    error_files = [r for r in summary['results'] if not r.is_valid()]
    
    if error_files:
        print("\n" + "=" * 70)
        print("FILES WITH ERRORS")
        print("=" * 70)
        for result in error_files[:20]:  # Show first 20
            print(f"\n{result.file_path.name}:")
            errors = [i for i in result.issues if i["severity"] == "error"]
            for error in errors[:5]:  # Show first 5 errors per file
                print(f"  [ERROR] {error['category']}: {error['message']}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more errors")
    
    # Show warnings for files with many warnings
    warning_files = [r for r in summary['results'] if len(r.issues) > 0]
    if warning_files:
        print("\n" + "=" * 70)
        print("FILES WITH WARNINGS (Top 10)")
        print("=" * 70)
        warning_files.sort(key=lambda r: len(r.issues), reverse=True)
        for result in warning_files[:10]:
            warnings = [i for i in result.issues if i["severity"] == "warning"]
            if warnings:
                print(f"\n{result.file_path.name} ({len(warnings)} warnings):")
                for warning in warnings[:3]:
                    print(f"  [WARN] {warning['category']}: {warning['message']}")


def main():
    """Main validation function."""
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    if not processed_dir.exists():
        print(f"[ERROR] Processed directory not found: {processed_dir}")
        return
    
    summary = validate_all_files(processed_dir)
    print_validation_report(summary, verbose=True)
    
    # Save detailed report to file
    report_file = PROJECT_ROOT / "data" / "validation_report.json"
    report_data = {
        "summary": {
            "total_files": summary["total_files"],
            "valid_files": summary["valid_files"],
            "invalid_files": summary["invalid_files"],
            "total_turns": summary["total_turns"],
            "total_errors": summary["total_errors"],
            "total_warnings": summary["total_warnings"]
        },
        "files": [
            {
                "file": str(r.file_path.relative_to(PROJECT_ROOT)),
                "valid": r.is_valid(),
                "stats": r.stats,
                "issues": r.issues
            }
            for r in summary["results"]
        ]
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[INFO] Detailed report saved to: {report_file}")
    
    # Return exit code based on validation results
    if summary["invalid_files"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

