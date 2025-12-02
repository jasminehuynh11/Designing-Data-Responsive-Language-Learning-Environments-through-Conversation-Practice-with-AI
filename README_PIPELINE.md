# Complete Data Processing Pipeline

This document explains how to use the unified pipeline script to process new student data from raw documents to repair detection.

## Quick Start

When you have new student folders in `data/raw/`, simply run:

```bash
# Process specific students and weeks
python run_full_pipeline.py --student 18 26 32 36 --week 1 2 3 4

# Process all students and weeks (auto-discovers from config)
python run_full_pipeline.py --all
```

## What the Pipeline Does

The unified pipeline performs three main steps:

1. **Text Extraction** - Extracts text from Word/PDF documents
2. **Dialogue Processing** - Parses dialogues and splits into tasks
3. **Repair Detection** - Detects repair sequences using LLM

## Usage Examples

### Process Specific Students

```bash
# Process student 18, weeks 2, 3, 4
python run_full_pipeline.py --student 18 --week 2 3 4

# Process multiple students
python run_full_pipeline.py --student 18 26 32 36 --week 1 2 3 4
```

### Process All New Files

```bash
# Auto-discovers all students/weeks from config/preprocessing_config.json
python run_full_pipeline.py --all
```

### Reprocess Existing Files

```bash
# Force reprocessing even if output files exist
python run_full_pipeline.py --student 18 --week 2 --force
```

### Skip Repair Detection

```bash
# Only run preprocessing (extraction + processing)
python run_full_pipeline.py --student 18 --week 2 --skip-repairs
```

### Quiet Mode

```bash
# Reduce output verbosity
python run_full_pipeline.py --student 18 --week 2 --quiet
```

## Configuration

Before running, ensure your `config/preprocessing_config.json` includes entries for the students you want to process:

```json
{
  "students": {
    "18": {
      "label_set": "english_standard",
      "weeks": {
        "1": { "tasks": 3 },
        "2": { "tasks": 3 },
        "3": { "tasks": 4 },
        "4": { "tasks": 3 }
      }
    }
  }
}
```

## Output Structure

The pipeline creates files in the following structure:

```
data/
├── extracted_text/          # Extracted plain text
│   └── S18_W2.txt
├── processed/               # Processed dialogue JSON files
│   └── S18_W2_T1.json
│   └── S18_W2_T2.json
│   └── S18_W2_T3.json
└── repairs/
    └── production/          # Repair detection results
        └── S18_W2_T1_repairs.json
        └── S18_W2_T2_repairs.json
        └── S18_W2_T3_repairs.json
```

## File Naming Convention

All output files follow the pattern: `S{student_id}_W{week}_T{task}.json`

- `S18_W2_T1.json` = Student 18, Week 2, Task 1
- `S18_W2_T1_repairs.json` = Repair annotations for the above dialogue

## Requirements

- Python 3.8+
- Required packages (see `requirements.txt`)
- Gemini API key in `.env` file (for repair detection)
- Documents in `data/raw/#{student}/#{student}/#{student}. Week{week}.docx`

## Troubleshooting

### No files found
- Check that documents exist in `data/raw/#{student}/#{student}/`
- Verify file naming matches pattern: `#{student}. Week{week}.docx`
- Ensure student is configured in `config/preprocessing_config.json`

### Repair detection fails
- Check that `.env` file contains `GEMINI_API_KEY`
- Verify API key is valid and has quota
- Check internet connection

### Files not reprocessing
- Use `--force` flag to reprocess existing files
- Delete output files manually if needed

## Advanced Usage

### Process Only Preprocessing

If you only want to extract and process dialogues without repair detection:

```bash
python run_full_pipeline.py --student 18 --week 2 --skip-repairs
```

### Process Only Repair Detection

If dialogues are already processed and you only need repair detection:

```bash
python run_phase2_repair_detection.py
```

## Related Scripts

While `run_full_pipeline.py` is the recommended way to process new data, individual scripts are still available:

- `scripts/preprocessing_pipeline.py` - Preprocessing only
- `run_phase2_repair_detection.py` - Repair detection only
- `scripts/validate_repair_results.py` - Validation

## Support

For issues or questions, check:
- `docs/PREPROCESSING_COMPLETE_FINAL.md` - Preprocessing details
- `docs/PHASE2_FINAL_SUMMARY.md` - Repair detection details
- `docs/PHASE2_QUICK_START.md` - Quick start guide

