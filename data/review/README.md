# Human-in-the-Loop Review Documents

This folder contains merged documents organized by week for easy human review and validation.

## Folder Structure

```
data/review/
├── Week1/
│   ├── W1_T1_merged.json      # Complete dialogue + repairs (JSON)
│   ├── W1_T1_review.txt       # Human-readable summary
│   ├── W1_T2_merged.json
│   ├── W1_T2_review.txt
│   ├── W1_T3_merged.json
│   ├── W1_T3_review.txt
│   └── INDEX.json             # Overview of all dialogues in Week 1
├── Week2/
│   └── ...
├── Week3/
│   └── ...
└── Week4/
    └── ...
```

## File Types

### 1. `*_merged.json`
Complete merged document containing:
- Dialogue metadata (student_id, task_topic, week, task)
- Full dialogue turns
- All repair annotations
- Summary statistics

**Use for**: Detailed analysis, programmatic access, data validation

### 2. `*_review.txt`
Human-readable summary including:
- Quick overview (student ID, task topic, turn count, repair count)
- Repair summary statistics (BI/LI counts, resolution types)
- Detailed repair information with:
  - Turn indices
  - Initiation type (LI/BI)
  - Resolution type (R/U-A/U-P)
  - Trigger description
  - Evidence summary
  - Actual turn content for each repair

**Use for**: Quick human review, checking repair accuracy, identifying issues

### 3. `INDEX.json`
Overview file for each week containing:
- Total dialogues in the week
- Total repairs detected
- List of all dialogues with key statistics

**Use for**: Getting an overview of the week, finding specific dialogues

## Review Workflow

### Quick Review (Recommended)
1. Open the `*_review.txt` file for the dialogue you want to check
2. Review the repair summary at the top
3. Check each repair detail:
   - Are the turn indices correct?
   - Is the initiation type (LI/BI) correct?
   - Is the resolution type (R/U-A/U-P) correct?
   - Does the trigger description match?
   - Does the evidence summary make sense?
4. Review the actual turn content shown for each repair

### Detailed Review
1. Open the `*_merged.json` file
2. Review the full dialogue turns
3. Cross-check each repair annotation against the actual dialogue
4. Verify repair boundaries and classifications

### Batch Review
1. Start with `INDEX.json` to see overview
2. Review dialogues with high repair counts first (may need more attention)
3. Review dialogues with zero or very few repairs (may have missed repairs)

## Statistics by Week

- **Week 1**: 3 dialogues, 10 repairs
- **Week 2**: 3 dialogues, 11 repairs
- **Week 3**: 3 dialogues, 21 repairs
- **Week 4**: 3 dialogues, 5 repairs

**Total**: 12 dialogues, 47 repairs

## What to Check

### ✅ Correct Annotations
- Turn indices match the actual repair sequence
- Initiation type (LI/BI) correctly identifies who started the repair
- Resolution type (R/U-A/U-P) accurately reflects the outcome
- Trigger description is specific and accurate
- Evidence summary explains the reasoning

### ⚠️ Potential Issues to Look For
- **False Positives**: Normal conversation marked as repairs
- **Missed Repairs**: Actual repair sequences not detected
- **Incorrect Splitting**: One repair split into multiple, or multiple merged into one
- **Wrong Classification**: LI vs BI, or R vs U-A vs U-P
- **Incomplete Turn Indices**: Missing turns that are part of the repair

## Making Corrections

If you find issues during review:

1. **Note the issue** in the review document or a separate notes file
2. **Document the correction needed**:
   - Which repair ID?
   - What needs to change?
   - What should it be instead?
3. **Update the JSON files** in `data/processed/` if making corrections
4. **Re-run the merge script** to update review documents

## Tips

- Start with validated files (W1_T1, W1_T2) to understand the expected quality
- Focus on dialogues with unusual repair counts (very high or very low)
- Check repair splitting carefully - complex sequences may need adjustment
- Verify that turn indices include all relevant turns, including resolution confirmation

---

*Documents created for human-in-the-loop validation*
*Last updated: After Phase 2 completion*

