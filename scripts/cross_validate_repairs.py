"""
Cross-validate repairs against source dialogues and extracted text.
Performs detailed quality checks.
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
import re

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPAIRS_DIR = PROJECT_ROOT / "data" / "repairs"
EXTRACTED_TEXT_DIR = PROJECT_ROOT / "data" / "extracted_text"


def load_dialogue(file_path: Path) -> Dict[str, Any]:
    """Load a dialogue JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_repairs(dialogue_file: Path) -> List[Dict[str, Any]]:
    """Load repair annotations for a dialogue."""
    dialogue_name = dialogue_file.stem
    
    # Check all batch directories
    for batch_dir in REPAIRS_DIR.iterdir():
        if batch_dir.is_dir():
            repair_file = batch_dir / f"{dialogue_name}_repairs.json"
            if repair_file.exists():
                with open(repair_file, 'r', encoding='utf-8') as f:
                    repairs = json.load(f)
                    return repairs if isinstance(repairs, list) else []
    return []


def load_extracted_text(dialogue_file: Path) -> str:
    """Load extracted source text if available."""
    # Try to find extracted text file
    student_id = dialogue_file.stem.split('_')[0]
    week = dialogue_file.stem.split('_')[1]
    
    extracted_file = EXTRACTED_TEXT_DIR / f"{student_id}_{week}.txt"
    if extracted_file.exists():
        with open(extracted_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    return ""


def get_turn_text(dialogue_data: Dict[str, Any], turn_num: int) -> str:
    """Get text of a specific turn."""
    turns = dialogue_data.get('turns', [])
    for turn in turns:
        if turn.get('turn') == turn_num:
            return turn.get('text', '')
    return ""


def validate_repair_turn_indices(repair: Dict[str, Any], dialogue_data: Dict[str, Any]) -> List[str]:
    """Validate turn indices are correct and turns exist."""
    issues = []
    
    turns = dialogue_data.get('turns', [])
    max_turn = max([t.get('turn', 0) for t in turns], default=0)
    
    turn_indices = repair.get('turn_indices', [])
    
    for turn_idx in turn_indices:
        if turn_idx < 1:
            issues.append(f"Turn index {turn_idx} is less than 1")
        elif turn_idx > max_turn:
            issues.append(f"Turn index {turn_idx} exceeds maximum turn {max_turn} in dialogue")
        else:
            # Verify turn exists
            turn_exists = any(t.get('turn') == turn_idx for t in turns)
            if not turn_exists:
                issues.append(f"Turn {turn_idx} does not exist in dialogue turns")
    
    return issues


def cross_validate_repair_content(repair: Dict[str, Any], dialogue_data: Dict[str, Any], source_text: str) -> List[str]:
    """Cross-validate repair content against dialogue and source."""
    issues = []
    warnings = []
    
    turn_indices = repair.get('turn_indices', [])
    trigger = repair.get('trigger', '')
    evidence = repair.get('evidence_summary', '')
    initiation = repair.get('initiation', '')
    resolution = repair.get('resolution', '')
    
    # Check if repair turns are actually part of a repair sequence
    if len(turn_indices) > 0:
        repair_turns = []
        for turn_idx in turn_indices:
            turn_text = get_turn_text(dialogue_data, turn_idx)
            if turn_text:
                repair_turns.append((turn_idx, turn_text))
        
        if len(repair_turns) < 2:
            warnings.append(f"Repair has fewer than 2 valid turns ({len(repair_turns)}), may be incomplete")
        
        # Check if repair spans make sense
        if len(turn_indices) > 10:
            warnings.append(f"Repair spans {len(turn_indices)} turns (unusually large)")
        
        # Validate initiation matches actual dialogue
        if turn_indices:
            first_turn_idx = min(turn_indices)
            first_turn = get_turn_text(dialogue_data, first_turn_idx)
            first_turn_speaker = None
            for turn in dialogue_data.get('turns', []):
                if turn.get('turn') == first_turn_idx:
                    first_turn_speaker = turn.get('speaker')
                    break
            
            # Check if initiation type matches speaker
            if first_turn_speaker:
                if initiation == "LI" and first_turn_speaker != "learner":
                    warnings.append(f"Marked as LI but first turn ({first_turn_idx}) is from {first_turn_speaker}")
                elif initiation == "BI" and first_turn_speaker != "bot":
                    warnings.append(f"Marked as BI but first turn ({first_turn_idx}) is from {first_turn_speaker}")
        
        # Check if trigger description makes sense
        if trigger:
            # Look for trigger keywords in repair turns
            trigger_lower = trigger.lower()
            found_keywords = False
            for turn_idx, turn_text in repair_turns:
                if any(keyword in turn_text.lower() for keyword in ['understand', 'repeat', 'clarify', 'confus', 'sorry', 'mean']):
                    found_keywords = True
                    break
            
            if not found_keywords and len(repair_turns) < 3:
                warnings.append(f"Trigger mentions repair but no obvious repair keywords found in turns")
        
        # Validate resolution makes sense
        if turn_indices:
            last_turn_idx = max(turn_indices)
            last_turn = get_turn_text(dialogue_data, last_turn_idx)
            
            if resolution == "R":
                # Check if conversation continues smoothly after
                all_turns = dialogue_data.get('turns', [])
                last_turn_idx_in_dialogue = max([t.get('turn', 0) for t in all_turns], default=0)
                
                # If repair ends near the end of dialogue, resolution might be uncertain
                if last_turn_idx >= last_turn_idx_in_dialogue - 2:
                    warnings.append(f"Repair ends near dialogue end (turn {last_turn_idx}/{last_turn_idx_in_dialogue}), resolution may be uncertain")
    
    # Check evidence summary mentions actual turn content
    if evidence and turn_indices:
        evidence_lower = evidence.lower()
        some_turn_mentioned = False
        
        for turn_idx in turn_indices[:3]:  # Check first 3 turns
            turn_text = get_turn_text(dialogue_data, turn_idx)
            if turn_text:
                # Check if any words from turn appear in evidence
                turn_words = set(re.findall(r'\b\w+\b', turn_text.lower()))
                evidence_words = set(re.findall(r'\b\w+\b', evidence_lower))
                if turn_words & evidence_words:
                    some_turn_mentioned = True
                    break
        
        if not some_turn_mentioned:
            warnings.append("Evidence summary doesn't seem to reference actual turn content")
    
    return issues, warnings


def cross_validate_dialogue(dialogue_file: Path) -> Dict[str, Any]:
    """Cross-validate a single dialogue and its repairs."""
    dialogue_name = dialogue_file.stem
    
    result = {
        'dialogue_file': dialogue_name,
        'has_repairs': False,
        'repair_count': 0,
        'issues': [],
        'warnings': [],
        'validation_score': 1.0
    }
    
    try:
        dialogue_data = load_dialogue(dialogue_file)
        repairs = load_repairs(dialogue_file)
        source_text = load_extracted_text(dialogue_file)
        
        if not repairs:
            return result
        
        result['has_repairs'] = True
        result['repair_count'] = len(repairs)
        
        all_issues = []
        all_warnings = []
        
        for repair in repairs:
            # Validate turn indices
            turn_issues = validate_repair_turn_indices(repair, dialogue_data)
            all_issues.extend([f"Repair {repair.get('repair_id')}: {issue}" for issue in turn_issues])
            
            # Cross-validate content
            content_issues, content_warnings = cross_validate_repair_content(repair, dialogue_data, source_text)
            all_issues.extend([f"Repair {repair.get('repair_id')}: {issue}" for issue in content_issues])
            all_warnings.extend([f"Repair {repair.get('repair_id')}: {warning}" for warning in content_warnings])
        
        result['issues'] = all_issues
        result['warnings'] = all_warnings
        
        # Calculate validation score (1.0 = perfect, lower = more issues)
        total_checks = len(repairs) * 5  # Rough estimate
        issue_count = len(all_issues)
        warning_count = len(all_warnings)
        
        result['validation_score'] = max(0.0, 1.0 - (issue_count * 0.1 + warning_count * 0.02))
        
    except Exception as e:
        result['issues'].append(f"Error during validation: {str(e)}")
        result['validation_score'] = 0.0
    
    return result


def cross_validate_all() -> Dict[str, Any]:
    """Cross-validate all dialogues."""
    print("=" * 80)
    print("CROSS-VALIDATION OF REPAIR DETECTION RESULTS")
    print("=" * 80)
    print()
    
    # Get all dialogue files
    new_files = sorted(PROCESSED_DIR.glob('S*_W*_T*.json'))
    legacy_files = sorted(PROCESSED_DIR.glob('W*_T*.json'))
    all_dialogue_files = sorted(set(new_files) | set(legacy_files))
    
    print(f"Found {len(all_dialogue_files)} dialogue files to cross-validate")
    print()
    
    results = []
    summary = {
        'total_dialogues': len(all_dialogue_files),
        'dialogues_with_repairs': 0,
        'total_repairs': 0,
        'total_issues': 0,
        'total_warnings': 0,
        'files_with_issues': 0,
        'files_with_warnings': 0,
        'average_validation_score': 0.0
    }
    
    # Validate files with repairs
    for i, dialogue_file in enumerate(all_dialogue_files, 1):
        repairs = load_repairs(dialogue_file)
        if not repairs:
            continue
        
        if i % 20 == 0:
            print(f"Cross-validating... {i}/{len(all_dialogue_files)} (files with repairs)")
        
        result = cross_validate_dialogue(dialogue_file)
        results.append(result)
        
        summary['dialogues_with_repairs'] += 1
        summary['total_repairs'] += result['repair_count']
        summary['total_issues'] += len(result['issues'])
        summary['total_warnings'] += len(result['warnings'])
        
        if result['issues']:
            summary['files_with_issues'] += 1
        if result['warnings']:
            summary['files_with_warnings'] += 1
    
    # Calculate average score
    if results:
        summary['average_validation_score'] = sum(r['validation_score'] for r in results) / len(results)
    
    # Print summary
    print()
    print("=" * 80)
    print("CROSS-VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total dialogues: {summary['total_dialogues']}")
    print(f"Dialogues with repairs: {summary['dialogues_with_repairs']}")
    print(f"Total repairs validated: {summary['total_repairs']}")
    print()
    print(f"Issues found: {summary['total_issues']}")
    print(f"Warnings: {summary['total_warnings']}")
    print(f"Files with issues: {summary['files_with_issues']}")
    print(f"Files with warnings: {summary['files_with_warnings']}")
    print()
    print(f"Average validation score: {summary['average_validation_score']:.2%}")
    
    # Show files with issues
    files_with_issues = [r for r in results if r['issues']]
    if files_with_issues:
        print(f"\n⚠️  Files with issues ({len(files_with_issues)}):")
        for result in files_with_issues[:10]:
            print(f"  {result['dialogue_file']}: {len(result['issues'])} issue(s)")
            for issue in result['issues'][:2]:
                print(f"    - {issue}")
        if len(files_with_issues) > 10:
            print(f"    ... and {len(files_with_issues) - 10} more")
    
    # Save report
    report = {
        'summary': summary,
        'files_with_issues': [
            {
                'dialogue': r['dialogue_file'],
                'repair_count': r['repair_count'],
                'issues': r['issues'],
                'warnings': r['warnings'],
                'validation_score': r['validation_score']
            }
            for r in files_with_issues
        ]
    }
    
    output_file = REPAIRS_DIR / 'CROSS_VALIDATION_REPORT.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Cross-validation report saved to: {output_file}")
    print("=" * 80)
    
    return report


if __name__ == "__main__":
    cross_validate_all()

