"""
Create merged review documents for human-in-the-loop checking.
Organizes dialogues and repairs by week in separate folders.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Configure output encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_task_topic(dialogue_file: Path) -> str:
    """Get task topic from task classifier."""
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
        from task_classifier import classify_task_topic
        dialogue = load_json(dialogue_file)
        topic = classify_task_topic(dialogue)
        return topic if topic else 'Unknown'
    except:
        return 'Unknown'


def create_merged_document(dialogue_file: Path, repair_file: Path) -> Dict[str, Any]:
    """Create a merged document with dialogue and repairs."""
    dialogue = load_json(dialogue_file)
    repairs = load_json(repair_file) if repair_file.exists() else []
    
    # Get task topic
    task_topic = dialogue.get('task_topic') or get_task_topic(dialogue_file)
    
    # Create merged document
    merged = {
        "dialogue_id": dialogue.get('dialogue_id', dialogue_file.stem),
        "student_id": dialogue.get('student_id'),
        "task_topic": task_topic,
        "week": int(dialogue_file.name[1]),  # Extract week number from filename
        "task": int(dialogue_file.name[4]),  # Extract task number from filename
        "total_turns": len(dialogue.get('turns', [])),
        "total_repairs": len(repairs),
        "dialogue": {
            "turns": dialogue.get('turns', [])
        },
        "repairs": repairs,
        "summary": {
            "repair_count": len(repairs),
            "bi_count": sum(1 for r in repairs if r.get('initiation') == 'BI'),
            "li_count": sum(1 for r in repairs if r.get('initiation') == 'LI'),
            "resolved_count": sum(1 for r in repairs if r.get('resolution') == 'R'),
            "unresolved_count": sum(1 for r in repairs if r.get('resolution') in ['U-A', 'U-P'])
        }
    }
    
    return merged


def create_human_readable_summary(merged: Dict[str, Any], output_path: Path) -> None:
    """Create a human-readable text summary for quick review."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write(f"DIALOGUE REVIEW: {merged['dialogue_id']}\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Student ID: {merged['student_id']}\n")
        f.write(f"Task Topic: {merged.get('task_topic', 'Unknown')}\n")
        f.write(f"Total Turns: {merged['total_turns']}\n")
        f.write(f"Total Repairs: {merged['total_repairs']}\n\n")
        
        f.write("REPAIR SUMMARY:\n")
        f.write("-"*80 + "\n")
        f.write(f"  Bot-Initiated (BI): {merged['summary']['bi_count']}\n")
        f.write(f"  Learner-Initiated (LI): {merged['summary']['li_count']}\n")
        f.write(f"  Resolved (R): {merged['summary']['resolved_count']}\n")
        f.write(f"  Unresolved: {merged['summary']['unresolved_count']}\n\n")
        
        if merged['repairs']:
            f.write("REPAIR DETAILS:\n")
            f.write("-"*80 + "\n")
            for repair in merged['repairs']:
                f.write(f"\nRepair {repair['repair_id']}:\n")
                f.write(f"  Turns: {repair['turn_indices']}\n")
                f.write(f"  Initiation: {repair['initiation']}\n")
                f.write(f"  Resolution: {repair['resolution']}\n")
                f.write(f"  Trigger: {repair['trigger']}\n")
                f.write(f"  Evidence: {repair['evidence_summary']}\n")
                
                # Show the actual turns
                f.write(f"\n  Turn Content:\n")
                for turn_idx in repair['turn_indices']:
                    turn = next((t for t in merged['dialogue']['turns'] if t['turn'] == turn_idx), None)
                    if turn:
                        f.write(f"    Turn {turn_idx} ({turn['speaker']}): {turn['text'][:100]}...\n")
                f.write("\n")
        else:
            f.write("No repairs detected in this dialogue.\n\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("FULL DIALOGUE:\n")
        f.write("="*80 + "\n\n")
        
        for turn in merged['dialogue']['turns']:
            f.write(f"Turn {turn['turn']} ({turn['speaker']}):\n")
            f.write(f"  {turn['text']}\n\n")


def create_full_dialogue_text(merged: Dict[str, Any]) -> str:
    """Create full dialogue text for printing."""
    lines = []
    lines.append("\n" + "="*80 + "\n")
    lines.append("FULL DIALOGUE\n")
    lines.append("="*80 + "\n\n")
    
    for turn in merged['dialogue']['turns']:
        speaker_label = "LEARNER" if turn['speaker'] == 'learner' else "BOT"
        lines.append(f"Turn {turn['turn']:3d} [{speaker_label:8s}]: {turn['text']}\n")
    
    return "".join(lines)


def create_consolidated_week_document(week_num: int, week_folder: Path, merged_docs: List[Dict[str, Any]]) -> None:
    """Create one consolidated text file for the entire week."""
    output_file = week_folder / f"Week{week_num}_COMPLETE.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write("="*80 + "\n")
        f.write(f"WEEK {week_num} - COMPLETE REVIEW DOCUMENT\n")
        f.write("="*80 + "\n")
        f.write(f"Generated for human-in-the-loop cross-checking\n")
        f.write(f"Total Dialogues: {len(merged_docs)}\n")
        f.write(f"Total Repairs: {sum(m['total_repairs'] for m in merged_docs)}\n")
        f.write("="*80 + "\n\n")
        
        # Process each dialogue in order (T1, T2, T3)
        for merged in merged_docs:
            # Write review section
            f.write("\n\n")
            f.write("="*80 + "\n")
            f.write(f"DIALOGUE: {merged['dialogue_id']}\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Student ID: {merged['student_id']}\n")
            f.write(f"Task Topic: {merged.get('task_topic', 'Unknown')}\n")
            f.write(f"Total Turns: {merged['total_turns']}\n")
            f.write(f"Total Repairs: {merged['total_repairs']}\n\n")
            
            f.write("REPAIR SUMMARY:\n")
            f.write("-"*80 + "\n")
            f.write(f"  Bot-Initiated (BI): {merged['summary']['bi_count']}\n")
            f.write(f"  Learner-Initiated (LI): {merged['summary']['li_count']}\n")
            f.write(f"  Resolved (R): {merged['summary']['resolved_count']}\n")
            f.write(f"  Unresolved: {merged['summary']['unresolved_count']}\n\n")
            
            if merged['repairs']:
                f.write("REPAIR DETAILS:\n")
                f.write("-"*80 + "\n")
                for repair in merged['repairs']:
                    f.write(f"\nRepair {repair['repair_id']}:\n")
                    f.write(f"  Turns: {repair['turn_indices']}\n")
                    f.write(f"  Initiation: {repair['initiation']}\n")
                    f.write(f"  Resolution: {repair['resolution']}\n")
                    f.write(f"  Trigger: {repair['trigger']}\n")
                    f.write(f"  Evidence: {repair['evidence_summary']}\n")
                    
                    # Show the actual turns
                    f.write(f"\n  Turn Content:\n")
                    for turn_idx in repair['turn_indices']:
                        turn = next((t for t in merged['dialogue']['turns'] if t['turn'] == turn_idx), None)
                        if turn:
                            speaker_label = "LEARNER" if turn['speaker'] == 'learner' else "BOT"
                            f.write(f"    Turn {turn_idx} [{speaker_label}]: {turn['text'][:100]}...\n")
                    f.write("\n")
            else:
                f.write("No repairs detected in this dialogue.\n\n")
            
            # Write full dialogue
            f.write(create_full_dialogue_text(merged))
            
            # Page break between dialogues
            f.write("\n\n" + "="*80 + "\n")
            f.write("END OF " + merged['dialogue_id'] + "\n")
            f.write("="*80 + "\n")
    
    print(f"  [OK] Created consolidated document: Week{week_num}_COMPLETE.txt")


def main():
    """Create review documents organized by week."""
    print("="*60)
    print("CREATING REVIEW DOCUMENTS FOR HUMAN CHECKING")
    print("="*60)
    
    processed_dir = Path('data/processed')
    review_dir = Path('data/review')
    
    # Create week folders
    week_folders = {}
    for week_num in [1, 2, 3, 4]:
        week_folder = review_dir / f"Week{week_num}"
        week_folder.mkdir(parents=True, exist_ok=True)
        week_folders[week_num] = week_folder
        print(f"\nCreated folder: {week_folder}")
    
    # Process each dialogue file
    dialogue_files = sorted(processed_dir.glob('W*_T*.json'))
    dialogue_files = [f for f in dialogue_files if '_repairs.json' not in f.name]
    
    print(f"\nProcessing {len(dialogue_files)} dialogue files...\n")
    
    # Store merged documents by week
    week_documents = {1: [], 2: [], 3: [], 4: []}
    
    for dialogue_file in dialogue_files:
        # Extract week and task numbers
        filename = dialogue_file.stem  # e.g., "W1_T1"
        week_num = int(filename[1])
        task_num = int(filename[4])
        
        # Find corresponding repair file
        repair_file = processed_dir / f"{filename}_repairs.json"
        
        # Create merged document
        merged = create_merged_document(dialogue_file, repair_file)
        
        # Store for consolidated document
        week_documents[week_num].append(merged)
        
        # Save JSON version
        week_folder = week_folders[week_num]
        json_output = week_folder / f"{filename}_merged.json"
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        
        # Save human-readable summary
        txt_output = week_folder / f"{filename}_review.txt"
        create_human_readable_summary(merged, txt_output)
        
        print(f"  [OK] {filename}: {merged['total_repairs']} repairs")
        print(f"        Saved to: {week_folder.name}/")
    
    # Create consolidated documents for each week
    print("\n" + "="*60)
    print("Creating consolidated week documents...")
    
    for week_num in [1, 2, 3, 4]:
        week_folder = week_folders[week_num]
        # Sort by task number (T1, T2, T3)
        merged_docs = sorted(week_documents[week_num], key=lambda x: x['task'])
        create_consolidated_week_document(week_num, week_folder, merged_docs)
    
    # Create index files for each week
    print("\n" + "="*60)
    print("Creating index files...")
    
    for week_num in [1, 2, 3, 4]:
        week_folder = week_folders[week_num]
        merged_files = sorted(week_folder.glob('*_merged.json'))
        
        index_content = {
            "week": week_num,
            "total_dialogues": len(merged_files),
            "total_repairs": 0,
            "dialogues": []
        }
        
        for merged_file in merged_files:
            merged = load_json(merged_file)
            index_content["total_repairs"] += merged['total_repairs']
            index_content["dialogues"].append({
                "file": merged_file.name,
                "dialogue_id": merged['dialogue_id'],
                "student_id": merged['student_id'],
                "task_topic": merged.get('task_topic', 'Unknown'),
                "turns": merged['total_turns'],
                "repairs": merged['total_repairs']
            })
        
        # Save index
        index_file = week_folder / "INDEX.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_content, f, ensure_ascii=False, indent=2)
        
        print(f"  [OK] Week {week_num}: {len(merged_files)} dialogues, {index_content['total_repairs']} repairs")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Review documents created in: {review_dir}/")
    print("\nStructure:")
    print("  data/review/")
    print("    Week1/")
    print("      Week1_COMPLETE.txt    <-- PRINT THIS for Week 1")
    print("      W1_T1_merged.json")
    print("      W1_T1_review.txt")
    print("      ...")
    print("    Week2/")
    print("      Week2_COMPLETE.txt    <-- PRINT THIS for Week 2")
    print("    Week3/")
    print("      Week3_COMPLETE.txt    <-- PRINT THIS for Week 3")
    print("    Week4/")
    print("      Week4_COMPLETE.txt    <-- PRINT THIS for Week 4")
    print("\nEach week folder contains:")
    print("  - Week*_COMPLETE.txt: All dialogues + reviews in one file (FOR PRINTING)")
    print("  - *_merged.json: Complete dialogue + repairs in JSON")
    print("  - *_review.txt: Human-readable summary for quick checking")
    print("  - INDEX.json: Overview of all dialogues in that week")


if __name__ == "__main__":
    main()

