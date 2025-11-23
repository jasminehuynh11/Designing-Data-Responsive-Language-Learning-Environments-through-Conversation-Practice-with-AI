# Dialogue Processing Pipeline

Professional workflow for extracting and processing dialogue data from Word and PDF documents.

## Project Structure

```
.
├── data/
│   ├── raw/              # Original documents (Word/PDF)
│   ├── extracted_text/   # Plain text extracted from documents
│   └── processed/        # Final JSON dialogue files (W1_T1.json, etc.)
├── scripts/
│   ├── document_extractor.py  # Utilities for extracting text from Word/PDF
│   └── dialogue_parser.py      # Parser for normalizing and structuring dialogues
├── notebooks/
│   └── 01_phase1_preprocessing.ipynb  # Main preprocessing workflow
└── requirements.txt      # Python dependencies
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your documents in `data/raw/`:
   - Week1: `#18. Week1.docx`
   - Week2: `#12. Week2.docx`
   - Week3: `#16. Week3.docx`
   - Week4: `#14. Week4.pdf`

## Usage

1. Open the Jupyter notebook:
```bash
jupyter notebook notebooks/01_phase1_preprocessing.ipynb
```

2. Run all cells to:
   - Extract text from documents
   - Parse dialogues and normalize speakers
   - Split into tasks (if multiple tasks per document)
   - Save as JSON files

## Output Format

Each dialogue is saved as a JSON file with the following structure:

```json
[
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
```

## Document Formats Supported

- **Week1 & Week2**: 
  - "You said:" → `speaker: "learner"`
  - "English Conversational Partner said:" → `speaker: "bot"`

- **Week3**: 
  - "Você disse:" → `speaker: "learner"`
  - "English Conversational Partner disse:" → `speaker: "bot"`

- **Week4**: 
  - Red text → `speaker: "learner"`
  - Black text → `speaker: "bot"`

## Notes

- The parser automatically removes timestamps and normalizes whitespace
- Task splitting is automatic but can be refined based on document structure
- Week4 color detection requires pdfplumber and may need manual verification

