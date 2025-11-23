# Designing Data-Responsive Language Learning Environments through Conversation Practice with AI

A comprehensive pipeline for processing, analyzing, and assessing learner-AI dialogue data for second language learning research.

## Project Overview

This project implements a complete workflow for:
1. **Preprocessing**: Extracting and structuring dialogue data from Word/PDF documents
2. **Repair Detection**: Using LLM to identify and classify communication repair sequences
3. **Statistical Analysis**: Comprehensive analysis of repair patterns and dialogue characteristics
4. **Proficiency Assessment**: CEFR-based English proficiency level assessment

## Project Structure

```
.
├── data/
│   ├── raw/              # Original documents (Word/PDF)
│   ├── extracted_text/   # Plain text extracted from documents
│   ├── processed/        # Structured JSON dialogue files and repair annotations
│   └── review/           # Human-readable review documents for validation
├── scripts/
│   ├── document_extractor.py  # Utilities for extracting text from Word/PDF
│   ├── dialogue_parser.py     # Parser for normalizing and structuring dialogues
│   ├── repair_detector.py     # LLM-based repair sequence detection
│   └── task_classifier.py     # Task topic classification
├── notebooks/
│   ├── 01_phase1_preprocessing.ipynb    # Phase 1: Data preprocessing
│   └── 02_statistical_analysis.ipynb    # Phase 2: Statistical analysis and proficiency assessment
├── statistical_analysis_images/  # Generated visualizations and analysis outputs
├── requirements.txt      # Python dependencies
└── README_API_SETUP.md  # Gemini API configuration guide
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Gemini API (see `README_API_SETUP.md`):
   - Create a `.env` file with your `GEMINI_API_KEY`
   - Test connection: `python test_gemini_connection.py`

3. Place your documents in `data/raw/`:
   - Week1: `#18. Week1.docx`
   - Week2: `#12. Week2.docx`
   - Week3: `#16. Week3.docx`
   - Week4: `#14. Week4.docx`

## Workflow

### Phase 1: Preprocessing

Run the preprocessing notebook to extract and structure dialogue data:

```bash
jupyter notebook notebooks/01_phase1_preprocessing.ipynb
```

This will:
- Extract text from Word/PDF documents
- Parse dialogues and normalize speakers (learner/bot)
- Split into tasks (3 tasks per week)
- Save as JSON files: `W1_T1.json`, `W1_T2.json`, etc.

### Phase 2: Repair Detection

Use the repair detection script to identify communication repair sequences:

```bash
python run_phase2_repair_detection.py
```

This uses Gemini API to:
- Detect repair sequences in dialogues
- Classify initiation (LI/BI) and resolution (R/U-A/U-P)
- Identify trigger types
- Save as `*_repairs.json` files

### Phase 3: Statistical Analysis

Run the statistical analysis notebook for comprehensive analysis:

```bash
jupyter notebook notebooks/02_statistical_analysis.ipynb
```

This includes:
- Descriptive statistics (repairs per session, turns, words per turn)
- Repair pattern analysis (Initiation × Resolution)
- Trigger type distribution
- Correlation analysis
- **English proficiency assessment** (CEFR levels A1-C2)
- Visualizations and summary reports

All outputs are saved to `statistical_analysis_images/`.

## Data Formats

### Dialogue JSON Structure

Each dialogue is saved as a JSON file:

```json
{
  "student_id": 18,
  "dialogue_id": "W1_T1_S18",
  "turns": [
    {
      "turn": 1,
      "speaker": "learner",
      "text": "Hi, I'd like to order..."
    },
    {
      "turn": 2,
      "speaker": "bot",
      "text": "Sure! What kind of coffee..."
    }
  ]
}
```

### Repair Annotation Structure

Repair sequences are annotated as:

```json
[
  {
    "dialogue_id": "W1_T1_S18",
    "repair_id": 1,
    "turn_indices": [5, 6],
    "initiation": "BI",
    "resolution": "R",
    "trigger": "pronunciation/ASR – misrecognition of learner speech",
    "evidence_summary": "..."
  }
]
```

## Document Formats Supported

- **Week1 & Week2**: 
  - "You said:" → `speaker: "learner"`
  - "English Conversational Partner said:" → `speaker: "bot"`

- **Week3**: 
  - "Você disse:" → `speaker: "learner"`
  - "English Conversational Partner disse:" → `speaker: "bot"`

- **Week4**: 
  - "You said:" → `speaker: "learner"`
  - "English Conversational Partner said:" → `speaker: "bot"`

## Output Files

### Processed Data
- `data/processed/W*_T*.json` - Structured dialogue files
- `data/processed/*_repairs.json` - Repair sequence annotations

### Analysis Outputs
- `statistical_analysis_images/*.png` - Visualizations (300 DPI)
- `statistical_analysis_images/*.csv` - Statistical tables
- `statistical_analysis_images/proficiency_assessment.csv` - CEFR proficiency levels
- `statistical_analysis_images/summary_report.txt` - Comprehensive analysis summary

### Review Documents
- `data/review/Week*/W*_T*_review.txt` - Human-readable summaries
- `data/review/Week*/Week*_COMPLETE.txt` - Complete dialogues for printing

## Notes

- The parser automatically removes timestamps and normalizes whitespace
- Task splitting is automatic (3 tasks per week)
- All weeks use labeled formats for reliable speaker identification
- Proficiency assessment uses CEFR framework (A1-C2) with subscores
- All visualizations are saved at 300 DPI for publication quality

