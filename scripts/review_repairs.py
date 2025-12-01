"""
Interactive review tool for repair detection results.
Shows dialogue and repairs side-by-side for manual review.
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))


def load_dialogue(file_path: Path) -> Dict[str, Any]:
    """Load a dialogue JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_repairs(repair_file: Path) -> List[Dict[str, Any]]:
    """Load repair annotations."""
    if not repair_file.exists():
        return []
    with open(repair_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def display_dialogue_with_repairs(
    dialogue_data: Dict[str, Any],
    repairs: List[Dict[str, Any]],
    dialogue_file: Path
):
    """Display dialogue with repairs highlighted."""
    print("=" * 80)
    print(f"DIALOGUE: {dialogue_file.name}")
    print("=" * 80)
    print(f"Student: {dialogue_data.get('student_id')}, Week: {dialogue_data.get('week')}, Task: {dialogue_data.get('task')}")
    print(f"Total turns: {len(dialogue_data.get('turns', []))}")
    print(f"Repairs detected: {len(repairs)}")
    print()
    
    turns = dialogue_data.get('turns', [])
    
    # Create repair map (turn -> repairs)
    repair_map = {}
    for repair in repairs:
        for turn_idx in repair.get('turn_indices', []):
            if turn_idx not in repair_map:
                repair_map[turn_idx] = []
            repair_map[turn_idx].append(repair)
    
    # Display turns
    for turn in turns:
        turn_num = turn.get('turn')
        speaker = turn.get('speaker', 'unknown')
        text = turn.get('text', '')
        
        # Check if this turn is part of a repair
        is_repair = turn_num in repair_map
        
        if is_repair:
            print("┌" + "─" * 78 + "┐")
            for repair in repair_map[turn_num]:
                print(f"│ REPAIR #{repair.get('repair_id')}: {repair.get('initiation')} → {repair.get('resolution')}")
                print(f"│ Trigger: {repair.get('trigger', 'N/A')}")
                print(f"│ Turns: {repair.get('turn_indices', [])}")
                print("│")
        
        # Display turn
        speaker_label = "LEARNER" if speaker == "learner" else "BOT"
        print(f"│ Turn {turn_num:3d} [{speaker_label:8s}]: {text[:70]}")
        
        if is_repair:
            print("└" + "─" * 78 + "┘")
        print()
    
    # Summary of repairs
    if repairs:
        print("\n" + "=" * 80)
        print("REPAIR SUMMARY")
        print("=" * 80)
        for repair in repairs:
            print(f"\nRepair #{repair.get('repair_id')}:")
            print(f"  Initiation: {repair.get('initiation')}")
            print(f"  Resolution: {repair.get('resolution')}")
            print(f"  Trigger: {repair.get('trigger')}")
            print(f"  Turns: {repair.get('turn_indices')}")
            print(f"  Evidence: {repair.get('evidence_summary', 'N/A')[:100]}...")


def review_batch(batch_dir: Path, processed_dir: Path):
    """Review all files in a batch."""
    repair_files = sorted(batch_dir.glob("*_repairs.json"))
    
    if not repair_files:
        print(f"No repair files found in {batch_dir}")
        return
    
    print(f"Found {len(repair_files)} repair files to review")
    print()
    
    for repair_file in repair_files:
        # Find corresponding dialogue file
        dialogue_name = repair_file.stem.replace("_repairs", "")
        dialogue_file = processed_dir / f"{dialogue_name}.json"
        
        if not dialogue_file.exists():
            print(f"[WARNING] Dialogue file not found: {dialogue_file}")
            continue
        
        dialogue_data = load_dialogue(dialogue_file)
        repairs = load_repairs(repair_file)
        
        display_dialogue_with_repairs(dialogue_data, repairs, dialogue_file)
        
        # Pause for review
        input("\nPress Enter to continue to next dialogue...")
        print("\n" * 2)


def generate_review_report(batch_dir: Path, processed_dir: Path, output_file: Path):
    """Generate a review report with statistics."""
    repair_files = sorted(batch_dir.glob("*_repairs.json"))
    
    stats = {
        "total_files": len(repair_files),
        "files_with_repairs": 0,
        "files_without_repairs": 0,
        "total_repairs": 0,
        "initiation_distribution": {"LI": 0, "BI": 0},
        "resolution_distribution": {"R": 0, "U-A": 0, "U-P": 0},
        "trigger_categories": {},
        "files": []
    }
    
    for repair_file in repair_files:
        dialogue_name = repair_file.stem.replace("_repairs", "")
        dialogue_file = processed_dir / f"{dialogue_name}.json"
        
        if not dialogue_file.exists():
            continue
        
        dialogue_data = load_dialogue(dialogue_file)
        repairs = load_repairs(repair_file)
        
        file_stat = {
            "file": dialogue_name,
            "turns": len(dialogue_data.get('turns', [])),
            "repairs_count": len(repairs),
            "repairs": repairs
        }
        
        stats["files"].append(file_stat)
        
        if repairs:
            stats["files_with_repairs"] += 1
            stats["total_repairs"] += len(repairs)
            
            for repair in repairs:
                # Count initiation
                init = repair.get('initiation', '')
                if init in stats["initiation_distribution"]:
                    stats["initiation_distribution"][init] += 1
                
                # Count resolution
                res = repair.get('resolution', '')
                if res in stats["resolution_distribution"]:
                    stats["resolution_distribution"][res] += 1
                
                # Count triggers
                trigger = repair.get('trigger', 'other')
                trigger_cat = trigger.split('–')[0].strip() if '–' in trigger else 'other'
                stats["trigger_categories"][trigger_cat] = stats["trigger_categories"].get(trigger_cat, 0) + 1
        else:
            stats["files_without_repairs"] += 1
    
    # Save report
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("=" * 80)
    print("REVIEW REPORT")
    print("=" * 80)
    print(f"Total files: {stats['total_files']}")
    print(f"Files with repairs: {stats['files_with_repairs']}")
    print(f"Files without repairs: {stats['files_without_repairs']}")
    print(f"Total repairs: {stats['total_repairs']}")
    print(f"\nInitiation distribution:")
    for k, v in stats['initiation_distribution'].items():
        print(f"  {k}: {v}")
    print(f"\nResolution distribution:")
    for k, v in stats['resolution_distribution'].items():
        print(f"  {k}: {v}")
    print(f"\nTrigger categories:")
    for k, v in sorted(stats['trigger_categories'].items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print(f"\nReport saved to: {output_file}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Review repair detection results")
    parser.add_argument("--batch", default="pilot", help="Batch name to review")
    parser.add_argument("--report-only", action="store_true", help="Generate report only (no interactive review)")
    parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    repairs_dir = Path('data/repairs')
    processed_dir = Path('data/processed')
    batch_dir = repairs_dir / args.batch
    
    if not batch_dir.exists():
        print(f"[ERROR] Batch directory not found: {batch_dir}")
        return
    
    if args.report_only:
        output_file = Path(args.output) if args.output else batch_dir / "review_report.json"
        generate_review_report(batch_dir, processed_dir, output_file)
    else:
        review_batch(batch_dir, processed_dir)


if __name__ == "__main__":
    main()

