"""
Script to run the preprocessing pipeline and check results.
"""
import sys
from pathlib import Path
import json

# Add scripts directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'scripts'))

from document_extractor import extract_text, save_extracted_text, extract_text_with_colors_from_pdf
from dialogue_parser import DialogueParser

# Define paths
raw_data_dir = project_root / 'data' / 'raw'
extracted_text_dir = project_root / 'data' / 'extracted_text'
processed_dir = project_root / 'data' / 'processed'

# Document mapping with student IDs
# Student 18 did Week 1, Student 12 did Week 2, Student 16 did Week 3, Student 14 did Week 4
documents = {
    'week1': {
        'file': raw_data_dir / '#18. Week1.docx',
        'format': 'week1_week2',
        'student_id': 18
    },
    'week2': {
        'file': raw_data_dir / '#12. Week2.docx',
        'format': 'week1_week2',
        'student_id': 12
    },
    'week3': {
        'file': raw_data_dir / '#16. Week3.docx',
        'format': 'week3',
        'student_id': 16
    },
    'week4': {
        'file': raw_data_dir / '#14. Week4.pdf',
        'format': 'week4',
        'student_id': 14
    }
}

# Also check root directory for Week3
if not documents['week3']['file'].exists():
    root_week3 = project_root / '#16. Week3.docx'
    if root_week3.exists():
        documents['week3']['file'] = root_week3
        print(f"Note: Using Week3 from root directory: {root_week3}")

print("="*60)
print("PHASE 1: DIALOGUE PREPROCESSING")
print("="*60)

# Step 1: Extract text
print("\n[STEP 1] Extracting text from documents...")
extracted_texts = {}
week4_color_data = None

for week, info in documents.items():
    if not info['file'].exists():
        print(f"Warning: {info['file']} not found, skipping...")
        continue
    
    print(f"\nExtracting from {week}...")
    try:
        if week == 'week4':
            try:
                week4_color_data = extract_text_with_colors_from_pdf(str(info['file']))
                text = extract_text(str(info['file']))
                extracted_texts[week] = text
                print(f"  [OK] Extracted text with color information")
            except Exception as e:
                print(f"  Warning: Could not extract colors: {e}")
                text = extract_text(str(info['file']))
                extracted_texts[week] = text
        else:
            text = extract_text(str(info['file']))
            extracted_texts[week] = text
        
        output_file = extracted_text_dir / f"{week}_extracted.txt"
        save_extracted_text(text, str(output_file))
        print(f"  [OK] Extracted {len(text)} characters")
    except Exception as e:
        print(f"  [ERROR] {e}")

# Step 2 & 3: Parse dialogues
print("\n[STEP 2 & 3] Parsing dialogues...")
parser = DialogueParser()
all_dialogues = {}

for week, info in documents.items():
    if week not in extracted_texts:
        continue
    
    print(f"\nProcessing {week.upper()}...")
    text = extracted_texts[week]
    
    try:
        if info['format'] == 'week1_week2':
            turns = parser.parse_week1_week2(text)
        elif info['format'] == 'week3':
            turns = parser.parse_week3(text)
        elif info['format'] == 'week4':
            turns = parser.parse_week4_pdf(text, color_data=week4_color_data)
        else:
            print(f"  ✗ Unknown format")
            continue
        
        print(f"  [OK] Parsed {len(turns)} turns")
        if turns:
            print(f"  Preview: Turn 1 ({turns[0]['speaker']}): {turns[0]['text'][:60]}...")
        all_dialogues[week] = turns
    except Exception as e:
        print(f"  [ERROR] Error parsing: {e}")

# Step 4: Split into tasks and save
print("\n[STEP 4] Splitting into tasks and saving...")
saved_files = []

for week, turns in all_dialogues.items():
    if not turns:
        continue
    
    week_num = week.replace('week', '')
    text = extracted_texts[week]
    info = documents[week]
    
    # Try to split into tasks
    tasks = parser.split_into_tasks(text, int(week_num))
    
    if len(tasks) > 1:
        print(f"\n{week.upper()}: Found {len(tasks)} tasks")
        for task_idx, (task_name, task_text) in enumerate(tasks, 1):
            try:
                if info['format'] == 'week1_week2':
                    task_turns = parser.parse_week1_week2(task_text)
                elif info['format'] == 'week3':
                    task_turns = parser.parse_week3(task_text)
                elif info['format'] == 'week4':
                    task_turns = parser.parse_week4_pdf(task_text, color_data=week4_color_data)
                else:
                    task_turns = []
                
                if task_turns:
                    for i, turn in enumerate(task_turns, 1):
                        turn['turn'] = i
                    
                    output_file = processed_dir / f"W{week_num}_T{task_idx}.json"
                    student_id = info.get('student_id')
                    parser.save_dialogue_json(task_turns, str(output_file), student_id=student_id)
                    saved_files.append(output_file)
                    print(f"  [OK] Saved {output_file.name} ({len(task_turns)} turns, student_id: {student_id})")
            except Exception as e:
                print(f"  [ERROR] Error processing task {task_idx}: {e}")
    else:
        # If no tasks found, try to split the full dialogue into 3 parts
        print(f"\n{week.upper()}: No clear task markers found, attempting to split into 3 tasks...")
        total_turns = len(turns)
        if total_turns >= 3:
            # Split turns into 3 roughly equal parts
            chunk_size = total_turns // 3
            for task_idx in range(1, 4):
                start_idx = (task_idx - 1) * chunk_size
                end_idx = task_idx * chunk_size if task_idx < 3 else total_turns
                task_turns = turns[start_idx:end_idx]
                
                # Renumber turns
                for i, turn in enumerate(task_turns, 1):
                    turn['turn'] = i
                
                output_file = processed_dir / f"W{week_num}_T{task_idx}.json"
                student_id = info.get('student_id')
                parser.save_dialogue_json(task_turns, str(output_file), student_id=student_id)
                saved_files.append(output_file)
                print(f"  [OK] Saved {output_file.name} ({len(task_turns)} turns, student_id: {student_id})")
        else:
            # Too few turns, save as single task
            output_file = processed_dir / f"W{week_num}_T1.json"
            student_id = info.get('student_id')
            parser.save_dialogue_json(turns, str(output_file), student_id=student_id)
            saved_files.append(output_file)
            print(f"\n{week.upper()}: Saved as single task {output_file.name} ({len(turns)} turns, student_id: {student_id})")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total files saved: {len(saved_files)}")
for f in saved_files:
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Handle both old format (list) and new format (dict with student_id)
    if isinstance(data, dict) and 'turns' in data:
        turns = data['turns']
        student_id = data.get('student_id', 'N/A')
        print(f"  {f.name}: {len(turns)} turns (student_id: {student_id})")
        learners = sum(1 for t in turns if t['speaker'] == 'learner')
        bots = sum(1 for t in turns if t['speaker'] == 'bot')
    else:
        turns = data
        print(f"  {f.name}: {len(turns)} turns")
        learners = sum(1 for t in turns if t['speaker'] == 'learner')
        bots = sum(1 for t in turns if t['speaker'] == 'bot')
    print(f"    - Learners: {learners}, Bots: {bots}")

print("\n" + "="*60)
print("VERIFICATION: Sample from first file")
print("="*60)
if saved_files:
    sample_file = saved_files[0]
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both formats
    if isinstance(data, dict) and 'turns' in data:
        turns = data['turns']
        student_id = data.get('student_id', 'N/A')
        print(f"\n{sample_file.name} (student_id: {student_id}) - First 3 turns:")
    else:
        turns = data
        print(f"\n{sample_file.name} - First 3 turns:")
    
    for turn in turns[:3]:
        print(f"\n  Turn {turn['turn']} ({turn['speaker']}):")
        print(f"    {turn['text'][:100]}...")

