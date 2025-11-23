"""
Phase 2: LLM Repair Detection
Processes all dialogue JSON files and detects repair sequences using Gemini API.
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from repair_detector import detect_repairs, save_repair_annotations, get_gemini_model, validate_repair_annotation
from task_classifier import add_task_topic_to_dialogue

# Configure output encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_dialogue_json(file_path: Path) -> Dict[str, Any]:
    """Load a dialogue JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_dialogue_id(file_path: Path) -> str:
    """Create dialogue_id from filename (e.g., W1_T1.json -> W1_T1_S18)."""
    filename = file_path.stem  # e.g., "W1_T1"
    
    # Load dialogue to get student_id
    dialogue = load_dialogue_json(file_path)
    student_id = dialogue.get('student_id', 'UNKNOWN')
    
    return f"{filename}_S{student_id}"


def process_dialogue_file(dialogue_file: Path, model=None) -> bool:
    """
    Process a single dialogue file for repair detection.
    
    Args:
        dialogue_file: Path to dialogue JSON file
        model: Optional Gemini model instance
    
    Returns:
        True if successful, False otherwise
    """
    print(f"\nProcessing: {dialogue_file.name}")
    
    try:
        # Load dialogue
        dialogue_data = load_dialogue_json(dialogue_file)
        
        # Add dialogue_id if not present
        if 'dialogue_id' not in dialogue_data:
            dialogue_data['dialogue_id'] = create_dialogue_id(dialogue_file)
        
        # Add task_topic
        dialogue_data = add_task_topic_to_dialogue(dialogue_data)
        if 'task_topic' in dialogue_data:
            print(f"  Task topic: {dialogue_data['task_topic']}")
        
        # Detect repairs
        print(f"  Detecting repairs in {len(dialogue_data['turns'])} turns...")
        repairs = detect_repairs(dialogue_data, model=model)
        
        # Validate repairs
        dialogue_id = dialogue_data['dialogue_id']
        valid_repairs = []
        for repair in repairs:
            if validate_repair_annotation(repair, dialogue_id):
                valid_repairs.append(repair)
        
        # Save repairs
        output_file = dialogue_file.parent / f"{dialogue_file.stem}_repairs.json"
        save_repair_annotations(valid_repairs, output_file)
        
        print(f"  Found {len(valid_repairs)} repair sequence(s)")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Failed to process {dialogue_file.name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to process all dialogue files."""
    print("="*60)
    print("PHASE 2: LLM REPAIR DETECTION")
    print("="*60)
    
    # Get processed dialogue files
    processed_dir = Path('data/processed')
    dialogue_files = sorted(processed_dir.glob('W*_T*.json'))
    
    # Filter out repair files
    dialogue_files = [f for f in dialogue_files if '_repairs.json' not in f.name]
    
    if not dialogue_files:
        print("[ERROR] No dialogue files found in data/processed/")
        return
    
    print(f"\nFound {len(dialogue_files)} dialogue file(s) to process")
    
    # Get Gemini model (reuse for all dialogues)
    try:
        print("\nInitializing Gemini API...")
        model = get_gemini_model()
        print(f"  [OK] Using model: {model._model_name}")
    except Exception as e:
        print(f"  [ERROR] Failed to initialize Gemini API: {e}")
        return
    
    # Process each dialogue
    successful = 0
    failed = 0
    
    for dialogue_file in dialogue_files:
        if process_dialogue_file(dialogue_file, model=model):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Successfully processed: {successful} file(s)")
    if failed > 0:
        print(f"Failed: {failed} file(s)")
    print(f"\nRepair annotation files saved to: {processed_dir}/")


if __name__ == "__main__":
    main()

