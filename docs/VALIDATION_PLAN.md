# Preprocessing Validation & Quality Assurance Plan

## Overview

This document outlines the comprehensive validation strategy for preprocessed dialogue JSON files before proceeding to repair detection (Phase 2).

## Validation Approach

### 1. **Skip Keyword Handling (Updated)**

**Previous Behavior:** Entire documents were skipped if they contained skip keywords (e.g., "transcript was not available").

**New Behavior:** Documents are processed, but sections containing skip keywords are filtered out. This allows us to:
- Process available dialogue even when some parts are marked as unavailable
- Preserve context by keeping the line that contains the skip keyword
- Log which sections were removed for review

**Implementation:** `filter_skip_sections()` function in `scripts/preprocessing_pipeline.py`

### 2. **Comprehensive Validation Script**

The `scripts/validate_preprocessing.py` script performs multiple validation checks:

#### A. Metadata Consistency
- **Filename Format:** Validates `S##_W#_T#.json` pattern
- **Metadata Matching:** Ensures `student_id`, `week`, `task` in JSON match filename
- **Dialogue ID:** Verifies `dialogue_id` matches expected format

#### B. Turn Structure Validation
- **Turn Numbering:** Checks for missing, extra, or duplicate turn numbers
- **Speaker Labels:** Validates all speakers are either "learner" or "bot"
- **Empty Turns:** Flags turns with missing or empty text

#### C. Content Quality Checks
- **Encoding Issues:** Detects replacement characters () indicating encoding problems
- **Formatting:** Flags excessive whitespace or formatting artifacts
- **Turn Length:** Warns about suspiciously short (<2 chars) or long (>2000 chars) turns

#### D. Speaker Pattern Analysis
- **Alternation:** Checks for excessive consecutive same-speaker turns
- **Distribution:** Analyzes speaker distribution (learner vs bot ratio)

#### E. Cross-Reference Validation
- **Source Text:** Verifies dialogue turns appear in original extracted text
- **Source File:** Checks that source file path exists and is accessible

### 3. **Validation Report**

The script generates:
- **Console Output:** Summary statistics and top issues
- **JSON Report:** Detailed report saved to `data/validation_report.json` with:
  - Summary statistics (total files, valid/invalid counts, errors/warnings)
  - Per-file results with all issues and statistics

## Usage

### Run Validation
```bash
python scripts/validate_preprocessing.py
```

### Integration with Pipeline
Validation should be run after preprocessing and before repair detection:

1. **Preprocess all documents:**
   ```bash
   python scripts/preprocessing_pipeline.py --force
   ```

2. **Validate all JSON files:**
   ```bash
   python scripts/validate_preprocessing.py
   ```

3. **Review validation report:**
   - Check console output for summary
   - Review `data/validation_report.json` for detailed issues
   - Fix any critical errors before proceeding

4. **Proceed to repair detection:**
   ```bash
   python run_phase2_repair_detection.py
   ```

## Validation Categories

### Critical Errors (Must Fix)
- Invalid JSON syntax
- Filename/metadata mismatches
- Missing or duplicate turn numbers
- Invalid speaker labels
- Empty dialogues

### Warnings (Review Recommended)
- Content quality issues (encoding, formatting)
- Suspicious turn lengths
- Excessive consecutive same-speaker turns
- Cross-reference failures (may indicate parsing issues)

## Current Status

**Last Validation Run:**
- Total files: 191
- Valid files: 191 (100%)
- Files with errors: 0
- Total turns: 9,367
- Total warnings: 14 (mostly speaker pattern and content quality)

## Next Steps

1. ✅ **Skip keyword filtering** - Implemented
2. ✅ **Comprehensive validation script** - Implemented
3. ⏳ **Review and fix warnings** - Manual review recommended
4. ⏳ **Re-run preprocessing with updated skip logic** - Process previously skipped documents
5. ⏳ **Final validation pass** - Ensure all files pass before Phase 2

## Notes

- The validation script is non-destructive (read-only)
- Warnings don't block processing but should be reviewed
- Some warnings (e.g., long turns, consecutive speakers) may be normal for certain dialogue patterns
- Cross-reference validation may fail if source text format differs significantly from parsed output

