"""Fix identified repair annotation issues."""
from pathlib import Path
import json
from typing import Dict, List, Any

PROCESSED_DIR = Path('data/processed')
REPAIRS_DIR = Path('data/repairs')


def load_dialogue(file_path: Path) -> Dict[str, Any]:
    """Load dialogue JSON."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_repairs(dialogue_file: Path) -> tuple:
    """Load repairs from all batches, return the best one."""
    dialogue_name = dialogue_file.stem
    
    repair_files = []
    for batch_dir in REPAIRS_DIR.iterdir():
        if batch_dir.is_dir():
            repair_file = batch_dir / f"{dialogue_name}_repairs.json"
            if repair_file.exists():
                try:
                    with open(repair_file, 'r', encoding='utf-8') as f:
                        repairs = json.load(f)
                        repair_files.append((batch_dir.name, repair_file, repairs if isinstance(repairs, list) else []))
                except:
                    pass
    
    return repair_files


def fix_turn_indices(repairs: List[Dict[str, Any]], dialogue_data: Dict[str, Any]) -> tuple:
    """Fix turn indices that are out of bounds."""
    turns = dialogue_data.get('turns', [])
    max_turn = max([t.get('turn', 0) for t in turns], default=0)
    
    fixed_repairs = []
    removed_repairs = []
    
    for repair in repairs:
        turn_indices = repair.get('turn_indices', [])
        valid_indices = [t for t in turn_indices if 1 <= t <= max_turn]
        
        if len(valid_indices) < 2:
            # Not enough valid turns, remove this repair
            removed_repairs.append(repair)
            continue
        
        # Keep repair with valid indices only
        fixed_repair = repair.copy()
        fixed_repair['turn_indices'] = valid_indices
        fixed_repairs.append(fixed_repair)
    
    # Renumber repair IDs
    for idx, repair in enumerate(fixed_repairs, 1):
        repair['repair_id'] = idx
    
    return fixed_repairs, removed_repairs


def fix_dialogue_id_mismatches(repairs: List[Dict[str, Any]], expected_dialogue_id: str) -> List[Dict[str, Any]]:
    """Fix dialogue_id to match expected format."""
    fixed = []
    for repair in repairs:
        fixed_repair = repair.copy()
        fixed_repair['dialogue_id'] = expected_dialogue_id
        fixed.append(fixed_repair)
    return fixed


def fix_repair_file(dialogue_file: Path, dry_run: bool = True) -> Dict[str, Any]:
    """Fix issues in repair file for a dialogue."""
    dialogue_name = dialogue_file.stem
    
    result = {
        'dialogue_file': dialogue_name,
        'issues_found': [],
        'issues_fixed': [],
        'action': 'none'
    }
    
    try:
        dialogue_data = load_dialogue(dialogue_file)
        expected_dialogue_id = dialogue_data.get('dialogue_id', dialogue_name)
        turns = dialogue_data.get('turns', [])
        max_turn = max([t.get('turn', 0) for t in turns], default=0)
        
        # Get all repair files
        repair_files = load_repairs(dialogue_file)
        
        if not repair_files:
            return result
        
        # Use the repair file from production batch (most recent)
        best_batch = None
        best_file = None
        best_repairs = None
        
        for batch_name, repair_file, repairs in repair_files:
            if batch_name == 'production':
                best_batch = batch_name
                best_file = repair_file
                best_repairs = repairs
                break
        
        if not best_repairs:
            # Use validation batch
            for batch_name, repair_file, repairs in repair_files:
                if batch_name == 'validation':
                    best_batch = batch_name
                    best_file = repair_file
                    best_repairs = repairs
                    break
        
        if not best_repairs:
            # Use any available
            best_batch, best_file, best_repairs = repair_files[0]
        
        if not best_repairs:
            return result
        
        # Check for issues
        fixed_repairs = []
        for repair in best_repairs:
            turn_indices = repair.get('turn_indices', [])
            invalid_indices = [t for t in turn_indices if t < 1 or t > max_turn]
            
            if invalid_indices:
                result['issues_found'].append(f"Repair {repair.get('repair_id')}: Invalid turn indices {invalid_indices} (max turn is {max_turn})")
                
                # Fix by removing invalid indices
                valid_indices = [t for t in turn_indices if 1 <= t <= max_turn]
                if len(valid_indices) >= 2:
                    fixed_repair = repair.copy()
                    fixed_repair['turn_indices'] = valid_indices
                    fixed_repairs.append(fixed_repair)
                    result['issues_fixed'].append(f"Repair {repair.get('repair_id')}: Removed invalid indices, kept {valid_indices}")
                else:
                    result['issues_found'].append(f"Repair {repair.get('repair_id')}: Not enough valid turns after fixing, will remove")
            else:
                fixed_repairs.append(repair)
        
        # Fix dialogue_id if needed
        for repair in fixed_repairs:
            if repair.get('dialogue_id') != expected_dialogue_id:
                repair['dialogue_id'] = expected_dialogue_id
        
        # Renumber repair IDs
        for idx, repair in enumerate(fixed_repairs, 1):
            repair['repair_id'] = idx
        
        if fixed_repairs != best_repairs:
            result['action'] = 'fixed'
            if not dry_run:
                # Save fixed repairs
                with open(best_file, 'w', encoding='utf-8') as f:
                    json.dump(fixed_repairs, f, indent=2, ensure_ascii=False)
                result['issues_fixed'].append(f"Saved fixed repairs to {best_file}")
        
    except Exception as e:
        result['issues_found'].append(f"Error: {str(e)}")
    
    return result


def fix_all_issues(dry_run: bool = True):
    """Fix all identified repair issues."""
    print("=" * 80)
    print(f"{'DRY RUN - ' if dry_run else ''}FIXING REPAIR ANNOTATION ISSUES")
    print("=" * 80)
    print()
    
    # Files with issues from validation
    problematic_files = [
        'S12_W1_T1',  # Turn indices out of bounds
        'W1_T1',  # Dialogue ID mismatch
        'W1_T2',  # Dialogue ID mismatch
        'W2_T1',  # Dialogue ID mismatch
        'W3_T1',  # Dialogue ID mismatch
        'W3_T2',  # Dialogue ID mismatch
        'W3_T3',  # Dialogue ID mismatch
    ]
    
    results = []
    
    for dialogue_name in problematic_files:
        dialogue_file = PROCESSED_DIR / f"{dialogue_name}.json"
        if dialogue_file.exists():
            result = fix_repair_file(dialogue_file, dry_run=dry_run)
            results.append(result)
            
            if result['issues_found'] or result['issues_fixed']:
                print(f"File: {dialogue_name}")
                if result['issues_found']:
                    print(f"  Issues found: {len(result['issues_found'])}")
                    for issue in result['issues_found']:
                        print(f"    - {issue}")
                if result['issues_fixed']:
                    print(f"  Issues fixed: {len(result['issues_fixed'])}")
                    for fix in result['issues_fixed']:
                        print(f"    ✓ {fix}")
                print()
    
    if not dry_run:
        print("=" * 80)
        print("FIXES APPLIED")
        print("=" * 80)
    else:
        print("=" * 80)
        print("DRY RUN COMPLETE - No files modified")
        print("Run with --apply to fix issues")
        print("=" * 80)
    
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually apply fixes (default is dry run)")
    args = parser.parse_args()
    
    fix_all_issues(dry_run=not args.apply)

