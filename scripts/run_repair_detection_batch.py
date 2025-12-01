"""
Batch processing script for repair detection with progress tracking and resume capability.
Supports both GPT-4 Turbo and Gemini models.
"""
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from repair_detector import detect_repairs, get_gemini_model, save_repair_annotations, validate_repair_annotation
from repair_detector_gpt import detect_repairs_gpt, get_openai_client
from repair_detector_enhanced import detect_repairs_enhanced
from task_classifier import add_task_topic_to_dialogue

# Configure output encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_dialogue_json(file_path: Path) -> Dict[str, Any]:
    """Load a dialogue JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def process_dialogue_file(
    dialogue_file: Path,
    repairs_dir: Path,
    model_type: str = "gpt",  # "gpt", "gpt-enhanced", or "gemini"
    model=None,
    client=None,
    batch_name: str = "default",
    gpt_model: str = "gpt-4o"
) -> Dict[str, Any]:
    """
    Process a single dialogue file for repair detection.
    
    Returns:
        Dictionary with processing results
    """
    result = {
        "file": dialogue_file.name,
        "success": False,
        "repairs_count": 0,
        "error": None,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Load dialogue
        dialogue_data = load_dialogue_json(dialogue_file)
        
        # Add dialogue_id if not present
        if 'dialogue_id' not in dialogue_data:
            filename = dialogue_file.stem
            student_id = dialogue_data.get('student_id', 'UNKNOWN')
            dialogue_data['dialogue_id'] = f"{filename}_S{student_id}"
        
        # Add task_topic
        dialogue_data = add_task_topic_to_dialogue(dialogue_data)
        
        # Detect repairs based on model type
        if model_type == "gpt-enhanced":
            repairs = detect_repairs_enhanced(dialogue_data, model=gpt_model, client=client, use_enhanced_prompt=True)
        elif model_type == "gpt":
            repairs = detect_repairs_gpt(dialogue_data, model=gpt_model, client=client)
        else:
            repairs = detect_repairs(dialogue_data, model=model)
        
        # Validate repairs
        dialogue_id = dialogue_data['dialogue_id']
        valid_repairs = []
        for repair in repairs:
            if validate_repair_annotation(repair, dialogue_id):
                valid_repairs.append(repair)
        
        # Save repairs
        repairs_dir.mkdir(parents=True, exist_ok=True)
        batch_dir = repairs_dir / batch_name
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = batch_dir / f"{dialogue_file.stem}_repairs.json"
        save_repair_annotations(valid_repairs, output_file)
        
        result["success"] = True
        result["repairs_count"] = len(valid_repairs)
        result["output_file"] = str(output_file.relative_to(repairs_dir))
        
        return result
        
    except Exception as e:
        result["error"] = str(e)
        return result


def get_processed_files(repairs_dir: Path, batch_name: str) -> set:
    """Get set of already processed files across ALL batches."""
    # Check all batch directories to avoid reprocessing
    processed = set()
    
    # Check all subdirectories in repairs_dir
    if repairs_dir.exists():
        for batch_dir in repairs_dir.iterdir():
            if batch_dir.is_dir():
                for repair_file in batch_dir.glob("*_repairs.json"):
                    # Extract dialogue filename from repair filename
                    dialogue_name = repair_file.stem.replace("_repairs", "")
                    processed.add(dialogue_name)
    
    return processed


def process_batch(
    dialogue_files: List[Path],
    repairs_dir: Path,
    batch_name: str = "pilot",
    model_type: str = "gpt-enhanced",
    batch_size: int = 10,
    resume: bool = True,
    delay_seconds: float = 1.0,
    gpt_model: str = "gpt-4o"
) -> Dict[str, Any]:
    """
    Process a batch of dialogue files.
    
    Args:
        dialogue_files: List of dialogue file paths
        repairs_dir: Directory to save repair annotations
        batch_name: Name of this batch (for organization)
        model_type: "gpt" or "gemini"
        batch_size: Number of files to process (None = all)
        resume: Skip already processed files
        delay_seconds: Delay between API calls (rate limiting)
    """
    print("=" * 70)
    print(f"BATCH PROCESSING: {batch_name.upper()}")
    print("=" * 70)
    print(f"Model: {model_type.upper()}")
    print(f"Total files: {len(dialogue_files)}")
    if batch_size:
        print(f"Processing: {min(batch_size, len(dialogue_files))} files")
    print()
    
    # Get already processed files if resuming
    processed = set()
    if resume:
        processed = get_processed_files(repairs_dir, batch_name)
        if processed:
            print(f"Found {len(processed)} already processed files (will skip)")
    
    # Limit batch size
    files_to_process = dialogue_files[:batch_size] if batch_size else dialogue_files
    
    # Initialize model/client
    model = None
    client = None
    if model_type in ["gpt", "gpt-enhanced"]:
        try:
            client = get_openai_client()
            print(f"[OK] Initialized OpenAI client (model: {gpt_model})")
        except Exception as e:
            print(f"[ERROR] Failed to initialize OpenAI: {e}")
            return {"error": str(e)}
    else:
        try:
            model = get_gemini_model()
            print(f"[OK] Initialized Gemini model: {model._model_name}")
        except Exception as e:
            print(f"[ERROR] Failed to initialize Gemini: {e}")
            return {"error": str(e)}
    
    # Process files
    results = []
    successful = 0
    failed = 0
    skipped = 0
    
    for i, dialogue_file in enumerate(files_to_process, 1):
        # Check if already processed
        if resume and dialogue_file.stem in processed:
            print(f"[{i}/{len(files_to_process)}] SKIP: {dialogue_file.name} (already processed)")
            skipped += 1
            continue
        
        print(f"[{i}/{len(files_to_process)}] Processing: {dialogue_file.name}")
        
        result = process_dialogue_file(
            dialogue_file,
            repairs_dir,
            model_type=model_type,
            model=model,
            client=client,
            batch_name=batch_name,
            gpt_model=gpt_model
        )
        
        results.append(result)
        
        if result["success"]:
            successful += 1
            print(f"  ✓ Found {result['repairs_count']} repair(s)")
        else:
            failed += 1
            print(f"  ✗ Error: {result['error']}")
        
        # Rate limiting delay
        if i < len(files_to_process) and delay_seconds > 0:
            time.sleep(delay_seconds)
    
    # Save batch summary
    summary = {
        "batch_name": batch_name,
        "model_type": model_type,
        "timestamp": datetime.now().isoformat(),
        "total_files": len(files_to_process),
        "successful": successful,
        "failed": failed,
        "skipped": skipped,
        "results": results
    }
    
    summary_file = repairs_dir / batch_name / "batch_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 70)
    print("BATCH SUMMARY")
    print("=" * 70)
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Total repairs found: {sum(r.get('repairs_count', 0) for r in results if r.get('success'))}")
    print(f"\nSummary saved to: {summary_file}")
    
    return summary


def main():
    """Main function with command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch process dialogues for repair detection")
    parser.add_argument("--batch-name", default="pilot", help="Name of this batch")
    parser.add_argument("--model", choices=["gpt", "gpt-enhanced", "gemini"], default="gpt-enhanced", help="Model to use (gpt-enhanced recommended)")
    parser.add_argument("--gpt-model", default="gpt-4o", help="GPT model name (gpt-4o, gpt-4-turbo-preview, etc.)")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of files to process")
    parser.add_argument("--no-resume", action="store_true", help="Don't skip already processed files")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between API calls (seconds)")
    parser.add_argument("--student", type=int, help="Filter by student ID")
    parser.add_argument("--week", type=int, help="Filter by week")
    
    args = parser.parse_args()
    
    # Get dialogue files
    processed_dir = Path('data/processed')
    new_files = sorted(processed_dir.glob('S*_W*_T*.json'))
    legacy_files = sorted(processed_dir.glob('W*_T*.json'))
    dialogue_files = sorted(set(new_files) | set(legacy_files))
    
    # Filter out repair files
    dialogue_files = [f for f in dialogue_files if '_repairs.json' not in f.name]
    
    # Apply filters
    if args.student or args.week:
        filtered = []
        for f in dialogue_files:
            data = load_dialogue_json(f)
            if args.student and data.get('student_id') != args.student:
                continue
            if args.week and data.get('week') != args.week:
                continue
            filtered.append(f)
        dialogue_files = filtered
    
    if not dialogue_files:
        print("[ERROR] No dialogue files found")
        return
    
    repairs_dir = Path('data/repairs')
    
    # Process batch
    summary = process_batch(
        dialogue_files,
        repairs_dir,
        batch_name=args.batch_name,
        model_type=args.model,
        batch_size=args.batch_size if args.batch_size > 0 else None,
        resume=not args.no_resume,
        delay_seconds=args.delay,
        gpt_model=args.gpt_model
    )


if __name__ == "__main__":
    main()

