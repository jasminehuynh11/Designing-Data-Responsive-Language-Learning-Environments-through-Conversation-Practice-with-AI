"""
Calibration script: Test repair detection on dialogues with known annotations.
Measures accuracy by comparing to existing repair annotations.
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent))

from repair_detector_gpt import detect_repairs_gpt, get_openai_client
from repair_detector import detect_repairs, get_gemini_model
from repair_detector_enhanced import detect_repairs_enhanced


def load_dialogue(dialogue_file: Path) -> Dict[str, Any]:
    """Load dialogue JSON."""
    with open(dialogue_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_repairs(repair_file: Path) -> List[Dict[str, Any]]:
    """Load repair annotations."""
    if not repair_file.exists():
        return []
    with open(repair_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize_repair(repair: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize repair for comparison (remove dialogue_id, sort turn_indices)."""
    # Handle case where repair might not be a dict
    if not isinstance(repair, dict):
        return None
    
    normalized = {
        "repair_id": repair.get('repair_id'),
        "turn_indices": sorted(repair.get('turn_indices', [])),
        "initiation": repair.get('initiation'),
        "resolution": repair.get('resolution'),
        "trigger": repair.get('trigger', '').lower().strip()
    }
    return normalized


def compare_repairs(
    predicted: List[Dict[str, Any]],
    actual: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Compare predicted repairs to actual repairs."""
    
    # Normalize both (filter out None values)
    pred_norm = [r for r in [normalize_repair(r) for r in predicted] if r is not None]
    actual_norm = [r for r in [normalize_repair(r) for r in actual] if r is not None]
    
    # Exact matches
    exact_matches = 0
    partial_matches = 0
    
    matched_pred = set()
    matched_actual = set()
    
    # Find exact matches
    for i, pred in enumerate(pred_norm):
        for j, act in enumerate(actual_norm):
            if (pred['turn_indices'] == act['turn_indices'] and
                pred['initiation'] == act['initiation'] and
                pred['resolution'] == act['resolution']):
                exact_matches += 1
                matched_pred.add(i)
                matched_actual.add(j)
                break
    
    # Find partial matches (same turn_indices, different classification)
    for i, pred in enumerate(pred_norm):
        if i in matched_pred:
            continue
        for j, act in enumerate(actual_norm):
            if j in matched_actual:
                continue
            if pred['turn_indices'] == act['turn_indices']:
                partial_matches += 1
                matched_pred.add(i)
                matched_actual.add(j)
                break
    
    # Calculate metrics
    total_pred = len(predicted)
    total_actual = len(actual)
    
    true_positives = exact_matches
    false_positives = total_pred - len(matched_pred)
    false_negatives = total_actual - len(matched_actual)
    
    precision = true_positives / total_pred if total_pred > 0 else 0
    recall = true_positives / total_actual if total_actual > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "total_predicted": total_pred,
        "total_actual": total_actual,
        "exact_matches": exact_matches,
        "partial_matches": partial_matches,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }


def calibrate_model(
    processed_dir: Path,
    repairs_dir: Path,
    model_type: str = "gpt",
    model_name: str = "gpt-4o"
) -> Dict[str, Any]:
    """Calibrate repair detection on known dialogues."""
    
    print("=" * 80)
    print(f"CALIBRATION: {model_type.upper()} ({model_name})")
    print("=" * 80)
    
    # Find dialogues with existing repairs
    repair_files = sorted(repairs_dir.glob("*_repairs.json"))
    
    if not repair_files:
        print("[ERROR] No existing repair files found for calibration")
        return {}
    
    print(f"\nFound {len(repair_files)} dialogues with existing repairs")
    print("Testing on these dialogues...\n")
    
    # Initialize model
    model = None
    client = None
    if model_type == "gpt":
        try:
            client = get_openai_client()
            print(f"[OK] Initialized OpenAI client")
        except Exception as e:
            print(f"[ERROR] Failed to initialize OpenAI: {e}")
            return {}
    else:
        try:
            model = get_gemini_model()
            print(f"[OK] Initialized Gemini model")
        except Exception as e:
            print(f"[ERROR] Failed to initialize Gemini: {e}")
            return {}
    
    results = []
    all_metrics = {
        "total_predicted": 0,
        "total_actual": 0,
        "exact_matches": 0,
        "partial_matches": 0,
        "true_positives": 0,
        "false_positives": 0,
        "false_negatives": 0
    }
    
    for repair_file in repair_files:
        # Find corresponding dialogue
        dialogue_name = repair_file.stem.replace("_repairs", "")
        dialogue_file = processed_dir / f"{dialogue_name}.json"
        
        if not dialogue_file.exists():
            print(f"[SKIP] Dialogue not found: {dialogue_file}")
            continue
        
        dialogue_data = load_dialogue(dialogue_file)
        actual_repairs = load_repairs(repair_file)
        
        if not actual_repairs:
            continue
        
        print(f"Testing: {dialogue_file.name}")
        
        # Get predicted repairs
        try:
            if model_type == "gpt":
                # Use enhanced version for better accuracy
                predicted_repairs = detect_repairs_enhanced(dialogue_data, model=model_name, client=client, use_enhanced_prompt=True)
            else:
                predicted_repairs = detect_repairs(dialogue_data, model=model)
        except Exception as e:
            print(f"  [ERROR] {e}")
            continue
        
        # Compare
        metrics = compare_repairs(predicted_repairs, actual_repairs)
        results.append({
            "dialogue": dialogue_name,
            "metrics": metrics
        })
        
        # Aggregate
        for key in all_metrics:
            all_metrics[key] += metrics.get(key, 0)
        
        print(f"  Predicted: {metrics['total_predicted']}, Actual: {metrics['total_actual']}")
        print(f"  Exact matches: {metrics['exact_matches']}, Partial: {metrics['partial_matches']}")
        print(f"  Precision: {metrics['precision']:.2%}, Recall: {metrics['recall']:.2%}, F1: {metrics['f1_score']:.2%}")
        print()
    
    # Calculate overall metrics
    total_pred = all_metrics['total_predicted']
    total_actual = all_metrics['total_actual']
    
    overall_precision = all_metrics['true_positives'] / total_pred if total_pred > 0 else 0
    overall_recall = all_metrics['true_positives'] / total_actual if total_actual > 0 else 0
    overall_f1 = 2 * (overall_precision * overall_recall) / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0
    
    summary = {
        "model_type": model_type,
        "model_name": model_name,
        "dialogues_tested": len(results),
        "overall_metrics": {
            "total_predicted": total_pred,
            "total_actual": total_actual,
            "exact_matches": all_metrics['exact_matches'],
            "partial_matches": all_metrics['partial_matches'],
            "true_positives": all_metrics['true_positives'],
            "false_positives": all_metrics['false_positives'],
            "false_negatives": all_metrics['false_negatives'],
            "precision": overall_precision,
            "recall": overall_recall,
            "f1_score": overall_f1
        },
        "per_dialogue": results
    }
    
    # Print summary
    print("=" * 80)
    print("CALIBRATION SUMMARY")
    print("=" * 80)
    print(f"Dialogues tested: {len(results)}")
    print(f"Total predicted repairs: {total_pred}")
    print(f"Total actual repairs: {total_actual}")
    print(f"Exact matches: {all_metrics['exact_matches']}")
    print(f"Partial matches: {all_metrics['partial_matches']}")
    print(f"\nOverall Precision: {overall_precision:.2%}")
    print(f"Overall Recall: {overall_recall:.2%}")
    print(f"Overall F1 Score: {overall_f1:.2%}")
    
    # Save results
    output_file = Path('data/calibration_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Calibration results saved to: {output_file}")
    
    return summary


def main():
    """Main calibration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Calibrate repair detection on known dialogues")
    parser.add_argument("--model", choices=["gpt", "gemini"], default="gpt", help="Model to test")
    parser.add_argument("--gpt-model", default="gpt-4o", help="GPT model name (gpt-4o, gpt-4-turbo-preview, etc.)")
    
    args = parser.parse_args()
    
    processed_dir = Path('data/processed')
    repairs_dir = Path('data/repairs')
    
    results = calibrate_model(
        processed_dir,
        repairs_dir,
        model_type=args.model,
        model_name=args.gpt_model
    )


if __name__ == "__main__":
    main()

