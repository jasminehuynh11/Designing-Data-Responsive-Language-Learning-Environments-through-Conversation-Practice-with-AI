# Missing Tasks Investigation Report

## Summary

After cross-checking processed files against expected task counts, we found **9 cases** where tasks are missing.

## Missing Tasks Found

1. **S1_W3**: Expected 4 tasks, found 3 → Missing T4
2. **S2_W3**: Expected 2 tasks, found 1 → Missing T2  
3. **S8_W3**: Expected 3 tasks, found 2 → Missing T3
4. **S12_W1**: Expected 2 tasks, found 1 → Missing T2 ⚠️ **CRITICAL - You mentioned this**
5. **S13_W3**: Expected 2 tasks, found 1 → Missing T2
6. **S20_W1**: Expected 3 tasks, found 1 → Missing T1, T3 (Note: T2 exists but only 1 turn)
7. **S21_W1**: Expected 3 tasks, found 1 → Missing T2, T3
8. **S23_W3**: Expected 4 tasks, found 1 → Missing T2, T3, T4
9. **S34_W1**: Expected 3 tasks, found 2 → Missing T3

## Root Cause

The preprocessing pipeline's task splitting logic is not detecting all tasks in these documents. The pipeline reports:
- "Tasks identified: X (expected Y)" - meaning it's not splitting correctly

**Possible reasons:**
1. Documents may have different formatting/structure
2. Task markers may be missing or in different format
3. Documents may be combined in a single dialogue without clear separators
4. Some tasks might be very short or formatted differently

## Re-processing Attempts

We attempted to re-process all missing cases with `--force` flag, but the pipeline still only found the same number of tasks. This suggests the issue is with **task detection/splitting logic**, not with file skipping.

## Next Steps

### Option 1: Manual Review (Recommended)
1. Check the raw documents for these students/weeks
2. Verify if tasks are actually separated or combined
3. Manually split if needed
4. Update preprocessing logic if patterns are found

### Option 2: Update Task Splitting Logic
1. Review extracted text files for these cases
2. Identify why task markers aren't being detected
3. Enhance the splitting algorithm
4. Re-run preprocessing

### Option 3: Accept Current State
- Some documents may legitimately have fewer tasks
- Verify with original source documents
- Document exceptions

## Files to Check

Raw documents to review:
- `data/raw/#12/#12/#12. Week1.docx` (S12_W1 - missing T2)
- `data/raw/#1/#1/#1. Week3.docx` (S1_W3 - missing T4)
- `data/raw/#2/#2/#2. Week3.docx` (S2_W3 - missing T2)
- `data/raw/#8/#8/#8. Week3.docx` (S8_W3 - missing T3)
- `data/raw/#13/#13/#13. Week3.docx` (S13_W3 - missing T2)
- `data/raw/#20/#20/#20. Week1.docx` (S20_W1 - missing T1, T3)
- `data/raw/#21/#21/#21. Week1.docx` (S21_W1 - missing T2, T3)
- `data/raw/#23/#23/#23. Week3.docx` (S23_W3 - missing T2, T3, T4)
- `data/raw/#34/#34/#34. Week1.docx` (S34_W1 - missing T3)

Extracted text files (for easier review):
- `data/extracted_text/S12_W1.txt`
- `data/extracted_text/S1_W3.txt`
- etc.

## Impact on Repair Detection

**Current status:**
- Pilot batch: 10 files processed ✅
- Validation batch: 50 files processed ✅
- **Missing tasks will NOT be processed for repair detection until fixed**

**Recommendation:** Fix missing tasks before full production run to ensure complete data coverage.

