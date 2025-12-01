"""
Extract few-shot examples from existing repair annotations for prompt enhancement.
"""
import json
from pathlib import Path
from typing import Dict, List, Any


def load_dialogue(dialogue_file: Path) -> Dict[str, Any]:
    """Load dialogue JSON."""
    with open(dialogue_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_repairs(repair_file: Path) -> List[Dict[str, Any]]:
    """Load repair annotations."""
    with open(repair_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_turn_for_example(turn: Dict[str, Any]) -> str:
    """Format a turn for inclusion in example."""
    speaker = "learner" if turn.get('speaker') == 'learner' else "bot"
    text = turn.get('text', '')
    return f"  Turn {turn.get('turn')} ({speaker}): {text}"


def create_few_shot_example(
    dialogue_data: Dict[str, Any],
    repair: Dict[str, Any]
) -> str:
    """Create a formatted few-shot example."""
    turns = dialogue_data.get('turns', [])
    turn_indices = repair.get('turn_indices', [])
    
    # Get relevant turns
    relevant_turns = [t for t in turns if t.get('turn') in turn_indices]
    
    # Format dialogue excerpt
    dialogue_excerpt = "\n".join([format_turn_for_example(t) for t in relevant_turns])
    
    # Format repair annotation
    repair_json = json.dumps(repair, indent=2, ensure_ascii=False)
    
    example = f"""
EXAMPLE: {repair.get('trigger', 'Repair')} ({repair.get('initiation')} → {repair.get('resolution')})

Dialogue excerpt:
{dialogue_excerpt}

Correct annotation:
{repair_json}

Reasoning:
{repair.get('evidence_summary', 'N/A')}
"""
    return example


def extract_few_shot_examples(
    processed_dir: Path,
    repairs_dir: Path,
    num_examples: int = 3
) -> str:
    """Extract diverse few-shot examples from existing repairs."""
    
    # Find dialogues with repairs
    repair_files = sorted(repairs_dir.glob("*_repairs.json"))
    
    examples = []
    seen_types = set()
    
    for repair_file in repair_files:
        # Find corresponding dialogue
        dialogue_name = repair_file.stem.replace("_repairs", "")
        dialogue_file = processed_dir / f"{dialogue_name}.json"
        
        if not dialogue_file.exists():
            continue
        
        dialogue_data = load_dialogue(dialogue_file)
        repairs = load_repairs(repair_file)
        
        for repair in repairs:
            # Get unique example types
            example_type = f"{repair.get('initiation')}_{repair.get('resolution')}_{repair.get('trigger', '').split('–')[0].strip()}"
            
            if example_type not in seen_types and len(examples) < num_examples:
                example = create_few_shot_example(dialogue_data, repair)
                examples.append(example)
                seen_types.add(example_type)
                
                if len(examples) >= num_examples:
                    break
        
        if len(examples) >= num_examples:
            break
    
    return "\n".join(examples)


def main():
    """Generate few-shot examples section for prompt."""
    processed_dir = Path('data/processed')
    repairs_dir = Path('data/repairs')
    
    examples = extract_few_shot_examples(processed_dir, repairs_dir, num_examples=3)
    
    few_shot_section = f"""
===============================
FEW-SHOT EXAMPLES
===============================

These examples show correct repair annotations from real dialogues. Study them carefully to understand the expected format and reasoning.

{examples}

===============================
"""
    
    print("=" * 80)
    print("FEW-SHOT EXAMPLES FOR PROMPT")
    print("=" * 80)
    print(few_shot_section)
    
    # Save to file
    output_file = Path('config/few_shot_examples.txt')
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(few_shot_section)
    
    print(f"\n[OK] Few-shot examples saved to: {output_file}")
    print("\n[INFO] Add this section to your repair detection prompt for better accuracy!")


if __name__ == "__main__":
    main()

