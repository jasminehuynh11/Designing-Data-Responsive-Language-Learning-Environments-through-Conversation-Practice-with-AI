# Phase 2: Repair Detection - Quick Start Guide

## Recommended Approach Summary

Based on comprehensive analysis, here's the optimal strategy:

### ✅ **Use GPT-4 Turbo** (you have paid access)
- Better reasoning for complex linguistic analysis
- More consistent JSON output
- Better at nuanced distinctions
- Cost: ~$3 for all 193 dialogues (very affordable!)

### ✅ **Batch Processing** (not all at once)
- Process in batches: Pilot (10-20) → Validation (50) → Production (remaining)
- Allows review and refinement
- Better error handling
- Cost control

### ✅ **Iterative Refinement**
- Review pilot results
- Refine prompt based on feedback
- Validate before full production

## Step-by-Step Execution

### Step 1: Process Pilot Batch (10-20 files)

```bash
# Process 10 files with GPT-4 Turbo
python scripts/run_repair_detection_batch.py --batch-name pilot --model gpt --batch-size 10
```

This will:
- Process 10 diverse dialogues
- Save results to `data/repairs/pilot/`
- Create batch summary

### Step 2: Review Pilot Results

```bash
# Interactive review (shows dialogues with repairs)
python scripts/review_repairs.py --batch pilot

# Or generate statistics report only
python scripts/review_repairs.py --batch pilot --report-only
```

**What to look for:**
- Are repairs correctly identified?
- Are false positives common?
- Are edge cases handled well?
- Any systematic issues?

### Step 3: Refine Prompt (if needed)

If you find issues:
1. Edit `scripts/repair_detector.py` (REPAIR_DETECTION_SYSTEM_PROMPT)
2. Add examples or clarify edge cases
3. Version control your prompts

### Step 4: Process Validation Batch (50 files)

```bash
# Process 50 files with refined approach
python scripts/run_repair_detection_batch.py --batch-name validation --model gpt --batch-size 50
```

### Step 5: Review Validation Results

```bash
python scripts/review_repairs.py --batch validation --report-only
```

Compare metrics:
- Repair count distribution
- Initiation (LI vs BI) ratio
- Resolution (R vs U-A vs U-P) ratio
- Trigger categories

### Step 6: Full Production (Remaining files)

```bash
# Process all remaining files
python scripts/run_repair_detection_batch.py --batch-name production --model gpt --batch-size 0
```

(`--batch-size 0` means process all remaining files)

## Alternative: Process All at Once (Not Recommended)

If you want to process everything immediately:

```bash
python run_phase2_repair_detection.py
```

**But this:**
- ❌ No review/refinement opportunity
- ❌ Harder to catch systematic issues
- ❌ No cost control
- ❌ All-or-nothing (if it fails, you lose progress)

## Model Comparison (A/B Testing)

To compare GPT vs Gemini on same dialogues:

```python
from scripts.repair_detector_gpt import compare_models
import json

# Load a dialogue
with open('data/processed/S18_W1_T1.json', 'r') as f:
    dialogue = json.load(f)

# Compare models
results = compare_models(dialogue)
print(json.dumps(results, indent=2))
```

## Cost Estimation

- **GPT-4 Turbo:** ~$0.015 per dialogue
- **193 dialogues:** ~$2.90 total
- **Very affordable!** Worth it for better quality

## Current Prompt Assessment

### ✅ Strengths
- Comprehensive theoretical definitions
- Clear examples of what NOT to mark
- Detailed decision strategy
- Good output schema

### 🔧 Potential Improvements
1. Add few-shot examples (2-3 real examples)
2. Strengthen JSON output instructions
3. Clarify edge cases (split vs merged repairs)
4. Add confidence indicators (optional)

**Recommendation:** Start with current prompt, refine based on pilot review.

## Troubleshooting

### API Rate Limits
- Use `--delay` flag to add delays between calls
- Default: 1 second delay

### Resume Processing
- Script automatically skips already processed files
- Use `--no-resume` to reprocess everything

### Filter by Student/Week
```bash
# Process only student 18, week 1
python scripts/run_repair_detection_batch.py --student 18 --week 1
```

## Next Actions

1. ✅ Review this plan
2. ⏳ Run pilot batch (10 files)
3. ⏳ Review results
4. ⏳ Refine if needed
5. ⏳ Process validation batch
6. ⏳ Full production

---

**Ready to start?** Run the pilot batch command above!

