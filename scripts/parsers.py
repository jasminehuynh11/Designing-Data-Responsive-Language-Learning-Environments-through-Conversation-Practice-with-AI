"""
Modular parser functions for different document formats.
Can be reused for processing multiple students' documents.
"""
from typing import List, Dict, Optional
from .dialogue_parser import DialogueParser


def parse_word_document_with_labels(text: str, format_type: str = 'week1_week2') -> List[Dict[str, any]]:
    """
    Parse Word documents that have speaker labels.
    
    Args:
        text: Extracted text from Word document
        format_type: 'week1_week2' (English labels) or 'week3' (Portuguese labels)
    
    Returns:
        List of dialogue turns
    """
    parser = DialogueParser()
    
    if format_type == 'week1_week2':
        return parser.parse_week1_week2(text)
    elif format_type == 'week3':
        return parser.parse_week3(text)
    else:
        raise ValueError(f"Unknown format_type: {format_type}. Use 'week1_week2' or 'week3'")


def parse_pdf_without_labels(text: str) -> List[Dict[str, any]]:
    """
    Parse PDF documents without speaker labels (alternating pattern).
    
    For documents like Week4 where there are no "You said" labels,
    just alternating dialogue blocks separated by blank lines.
    
    Args:
        text: Extracted text from PDF document
    
    Returns:
        List of dialogue turns with alternating speakers
    """
    parser = DialogueParser()
    return parser.parse_week4_pdf(text)


def process_student_document(file_path: str, student_id: int, format_type: str = 'auto') -> List[Dict[str, any]]:
    """
    Process a single student document and return dialogue turns.
    
    Args:
        file_path: Path to the document (Word or PDF)
        student_id: Student ID number
        format_type: 'word_labeled', 'pdf_unlabeled', or 'auto' (detect from file)
    
    Returns:
        List of dialogue turns with student_id metadata
    """
    from pathlib import Path
    from .document_extractor import extract_text
    
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    # Auto-detect format if not specified
    if format_type == 'auto':
        if suffix == '.docx':
            format_type = 'word_labeled'
        elif suffix == '.pdf':
            format_type = 'pdf_unlabeled'
        else:
            raise ValueError(f"Cannot auto-detect format for {suffix}")
    
    # Extract text
    text = extract_text(str(file_path))
    
    # Parse based on format
    if format_type == 'word_labeled':
        # Default to week1_week2 format, can be customized
        turns = parse_word_document_with_labels(text, format_type='week1_week2')
    elif format_type == 'pdf_unlabeled':
        turns = parse_pdf_without_labels(text)
    else:
        raise ValueError(f"Unknown format_type: {format_type}")
    
    # Add student_id to each turn (optional metadata)
    for turn in turns:
        turn['student_id'] = student_id
    
    return turns

