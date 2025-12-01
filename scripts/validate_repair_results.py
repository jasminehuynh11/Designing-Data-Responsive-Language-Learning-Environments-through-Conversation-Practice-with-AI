"""
Comprehensive validation of repair detection results.
Cross-checks repairs against dialogues, validates structure, and identifies issues.
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPAIRS_DIR = PROJECT_ROOT / "data" / "repairs"


def load_dialogue(file_path: Path) -> Dict[str, Any]:
    """Load a dialogue JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_repairs(repair_file: Path) -> List[Dict[str, Any]]:
    """Load repair annotations."""
    if not repair_file.exists():
        return []
    try:
        with open(repair_file, 'r', encoding='utf-8') as f:
            repairs = json.load(f)
            return repairs if isinstance(repairs, list) else []
    except Exception as e:
        print(f"Error loading {repair_file}: {e}")
        return []


def find_repair_file(dialogue_file: Path) -> Path:
    """Find corresponding repair file for a dialogue."""
    dialogue_name = dialogue_file.stem
    
    # Check all batch directories
    for batch_dir in REPAIRS_DIR.iterdir():
        if batch_dir.is_dir():
            repair_file = batch_dir / f"{dialogue_name}_repairs.json"
            if repair_file.exists():
                return repair_file
    
    return None


def validate_repair_structure(repair: Dict[str, Any], repair_id: int, dialogue_id: str) -> List[str]:
    """Validate structure of a single repair annotation."""
    issues = []
    
    required_fields = ['repair_id', 'turn_indices', 'initiation', 'resolution', 'trigger', 'evidence_summary']
    for field in required_fields:
        if field not in repair:
            issues.append(f"Missing required field: {field}")
    
    # Validate repair_id
    if 'repair_id' in repair and repair['repair_id'] != repair_id:
        issues.append(f"Repair ID mismatch: expected {repair_id}, got {repair['repair_id']}")
    
    # Validate dialogue_id
    if 'dialogue_id' in repair and repair['dialogue_id'] != dialogue_id:
        issues.append(f"Dialogue ID mismatch: expected {dialogue_id}, got {repair.get('dialogue_id')}")
    
    # Validate initiation
    if 'initiation' in repair and repair['initiation'] not in ['LI', 'BI']:
        issues.append(f"Invalid initiation: {repair['initiation']} (must be LI or BI)")
    
    # Validate resolution
    if 'resolution' in repair and repair['resolution'] not in ['R', 'U-A', 'U-P']:
        issues.append(f"Invalid resolution: {repair['resolution']} (must be R, U-A, or U-P)")
    
    # Validate turn_indices
    if 'turn_indices' in repair:
        if not isinstance(repair['turn_indices'], list):
            issues.append(f"turn_indices must be a list, got {type(repair['turn_indices'])}")
        elif not repair['turn_indices']:
            issues.append("turn_indices is empty")
        elif not all(isinstance(t, int) for t in repair['turn_indices']):
            issues.append("turn_indices contains non-integer values")
    
    # Validate trigger
    if 'trigger' in repair and not isinstance(repair['trigger'], str):
        issues.append(f"trigger must be a string, got {type(repair['trigger'])}")
    
    # Validate evidence_summary
    if 'evidence_summary' in repair and not isinstance(repair['evidence_summary'], str):
        issues.append(f"evidence_summary must be a string, got {type(repair['evidence_summary'])}")
    
    return issues


def validate_repair_against_dialogue(repair: Dict[str, Any], dialogue_data: Dict[str, Any]) -> List[str]:
    """Validate repair annotations against the actual dialogue."""
    issues = []
    
    turns = dialogue_data.get('turns', [])
    max_turn = max([t.get('turn', 0) for t in turns], default=0)
    
    turn_indices = repair.get('turn_indices', [])
    
    # Check if turn indices are valid
    for turn_idx in turn_indices:
        if turn_idx < 1:
            issues.append(f"Invalid turn index: {turn_idx} (must be >= 1)")
        elif turn_idx > max_turn:
            issues.append(f"Turn index {turn_idx} exceeds maximum turn {max_turn}")
        
        # Check if turn exists
        turn_exists = any(t.get('turn') == turn_idx for t in turns)
        if not turn_exists:
            issues.append(f"Turn {turn_idx} does not exist in dialogue")
    
    # Check for duplicate turn indices
    if len(turn_indices) != len(set(turn_indices)):
        issues.append(f"Duplicate turn indices found: {turn_indices}")
    
    # Check if turns are in order
    if turn_indices != sorted(turn_indices):
        issues.append(f"Turn indices not in order: {turn_indices}")
    
    # Validate repair boundaries make sense
    if len(turn_indices) > 0:
        min_turn = min(turn_indices)
        max_turn_idx = max(turn_indices)
        
        # Check if repair spans are reasonable
        if max_turn_idx - min_turn > 20:
            issues.append(f"Repair spans {max_turn_idx - min_turn + 1} turns (very large, may be error)")
    
    return issues


def check_repair_overlap(repairs: List[Dict[str, Any]]) -> List[str]:
    """Check for overlapping repairs."""
    issues = []
    
    for i, repair1 in enumerate(repairs):
        indices1 = set(repair1.get('turn_indices', []))
        for j, repair2 in enumerate(repairs[i+1:], start=i+1):
            indices2 = set(repair2.get('turn_indices', []))
            
            overlap = indices1 & indices2
            if overlap:
                issues.append(f"Repair {repair1.get('repair_id')} and {repair2.get('repair_id')} overlap on turns: {sorted(overlap)}")
    
    return issues


def validate_dialogue_file(dialogue_file: Path) -> Dict[str, Any]:
    """Validate a single dialogue file and its repairs."""
    dialogue_name = dialogue_file.stem
    
    result = {
        'dialogue_file': dialogue_name,
        'dialogue_exists': True,
        'repair_file_exists': False,
        'has_repairs': False,
        'repair_count': 0,
        'issues': [],
        'warnings': [],
        'repairs_valid': True
    }
    
    try:
        dialogue_data = load_dialogue(dialogue_file)
        dialogue_id = dialogue_data.get('dialogue_id', dialogue_name)
        turns = dialogue_data.get('turns', [])
        
        # Find repair file
        repair_file = find_repair_file(dialogue_file)
        
        if not repair_file:
            result['issues'].append(f"No repair file found for {dialogue_name}")
            result['repairs_valid'] = False
            return result
        
        result['repair_file_exists'] = True
        repairs = load_repairs(repair_file)
        
        if not repairs:
            result['warnings'].append("Repair file exists but contains no repairs (empty array)")
            return result
        
        result['has_repairs'] = True
        result['repair_count'] = len(repairs)
        
        # Validate each repair
        repair_issues = []
        for idx, repair in enumerate(repairs, 1):
            # Structure validation
            struct_issues = validate_repair_structure(repair, idx, dialogue_id)
            repair_issues.extend([f"Repair {idx}: {issue}" for issue in struct_issues])
            
            # Dialogue validation
            dialogue_issues = validate_repair_against_dialogue(repair, dialogue_data)
            repair_issues.extend([f"Repair {idx}: {issue}" for issue in dialogue_issues])
        
        result['issues'].extend(repair_issues)
        
        # Check for overlapping repairs
        overlap_issues = check_repair_overlap(repairs)
        if overlap_issues:
            result['warnings'].extend(overlap_issues)
        
        # Check repair ID sequence
        expected_ids = list(range(1, len(repairs) + 1))
        actual_ids = [r.get('repair_id') for r in repairs]
        if actual_ids != expected_ids:
            result['warnings'].append(f"Repair IDs not sequential: {actual_ids} (expected {expected_ids})")
        
        # Check if repairs are sorted by appearance
        first_turns = [min(r.get('turn_indices', []), default=0) for r in repairs]
        if first_turns != sorted(first_turns):
            result['warnings'].append("Repairs not sorted by first turn index")
        
        if repair_issues:
            result['repairs_valid'] = False
        
    except Exception as e:
        result['issues'].append(f"Error processing dialogue: {str(e)}")
        result['repairs_valid'] = False
    
    return result


def validate_all() -> Dict[str, Any]:
    """Validate all dialogue files and their repairs."""
    print("=" * 80)
    print("COMPREHENSIVE VALIDATION OF REPAIR DETECTION RESULTS")
    print("=" * 80)
    print()
    
    # Get all dialogue files
    new_files = sorted(PROCESSED_DIR.glob('S*_W*_T*.json'))
    legacy_files = sorted(PROCESSED_DIR.glob('W*_T*.json'))
    all_dialogue_files = sorted(set(new_files) | set(legacy_files))
    
    print(f"Found {len(all_dialogue_files)} dialogue files to validate")
    print()
    
    results = []
    summary = {
        'total_dialogues': len(all_dialogue_files),
        'with_repair_files': 0,
        'with_repairs': 0,
        'without_repairs': 0,
        'missing_repair_files': 0,
        'total_repairs': 0,
        'valid_repairs': 0,
        'invalid_repairs': 0,
        'files_with_issues': 0,
        'files_with_warnings': 0,
        'issues': defaultdict(int),
        'warnings': defaultdict(int)
    }
    
    # Validate each file
    for i, dialogue_file in enumerate(all_dialogue_files, 1):
        if i % 50 == 0:
            print(f"Validating... {i}/{len(all_dialogue_files)}")
        
        result = validate_dialogue_file(dialogue_file)
        results.append(result)
        
        # Update summary
        if result['repair_file_exists']:
            summary['with_repair_files'] += 1
        else:
            summary['missing_repair_files'] += 1
        
        if result['has_repairs']:
            summary['with_repairs'] += 1
            summary['total_repairs'] += result['repair_count']
        else:
            summary['without_repairs'] += 1
        
        if result['repairs_valid']:
            summary['valid_repairs'] += result['repair_count']
        else:
            summary['invalid_repairs'] += result['repair_count']
            summary['files_with_issues'] += 1
        
        if result['issues']:
            summary['files_with_issues'] += 1
            for issue in result['issues']:
                issue_type = issue.split(':')[0] if ':' in issue else 'general'
                summary['issues'][issue_type] += 1
        
        if result['warnings']:
            summary['files_with_warnings'] += 1
            for warning in result['warnings']:
                warning_type = warning.split(':')[0] if ':' in warning else 'general'
                summary['warnings'][warning_type] += 1
    
    # Print summary
    print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total dialogues: {summary['total_dialogues']}")
    print(f"With repair files: {summary['with_repair_files']} ✅")
    print(f"Missing repair files: {summary['missing_repair_files']} ❌")
    print()
    print(f"Files with repairs: {summary['with_repairs']}")
    print(f"Files without repairs: {summary['without_repairs']}")
    print(f"Total repairs: {summary['total_repairs']}")
    print()
    print(f"Valid repairs: {summary['valid_repairs']} ✅")
    print(f"Invalid repairs: {summary['invalid_repairs']} ❌")
    print()
    print(f"Files with issues: {summary['files_with_issues']}")
    print(f"Files with warnings: {summary['files_with_warnings']}")
    
    if summary['issues']:
        print("\nIssues found:")
        for issue_type, count in sorted(summary['issues'].items(), key=lambda x: -x[1])[:10]:
            print(f"  {issue_type}: {count}")
    
    if summary['warnings']:
        print("\nWarnings:")
        for warning_type, count in sorted(summary['warnings'].items(), key=lambda x: -x[1])[:10]:
            print(f"  {warning_type}: {count}")
    
    # Find files with issues
    files_with_issues = [r for r in results if r['issues']]
    files_with_warnings = [r for r in results if r['warnings']]
    
    if files_with_issues:
        print(f"\n⚠️  Files with issues ({len(files_with_issues)}):")
        for result in files_with_issues[:10]:
            print(f"  {result['dialogue_file']}: {len(result['issues'])} issue(s)")
            for issue in result['issues'][:2]:
                print(f"    - {issue}")
        if len(files_with_issues) > 10:
            print(f"    ... and {len(files_with_issues) - 10} more")
    
    # Save detailed report
    report = {
        'summary': dict(summary),
        'files_with_issues': [
            {
                'dialogue': r['dialogue_file'],
                'issues': r['issues'],
                'warnings': r['warnings']
            }
            for r in files_with_issues
        ],
        'files_with_warnings': [
            {
                'dialogue': r['dialogue_file'],
                'warnings': r['warnings']
            }
            for r in files_with_warnings if not r['issues']
        ]
    }
    
    output_file = REPAIRS_DIR / 'VALIDATION_REPORT.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Detailed validation report saved to: {output_file}")
    print("=" * 80)
    
    return report


if __name__ == "__main__":
    validate_all()

