# Phase 2: Complete Execution Plan - Repair Detection

## Current Status Assessment

### ✅ Completed
1. **Calibration Testing** - Tested on 9 known dialogues
   - Precision: 31.58%
   - Recall: 14.63%
   - F1 Score: 20.00%
   - Results: `data/calibration_results.json`

2. **Pilot Batch** - 10 files processed
   - Success rate: 100%
   - Repairs found: 7
   - Location: `data/repairs/pilot/`

3. **Validation Batch** - 50 files processed
   - Success rate: 100%
   - Repairs found: 41
   - Location: `data/repairs/validation/`

### 📊 Current Statistics
- **Total dialogue files:** 206
- **Already processed:** 50 files
  - Pilot: 10 files
  - Validation: 50 files (includes 10 from pilot)
- **Remaining to process:** **156 files**

### 📁 Files Already Processed
- Students 12, 13, 14, 16, 17 (various weeks)
- Total: 50 dialogue files

## Complete Execution Plan

### Step 1: Review & Analyze Current Results ✅

**Purpose:** Understand quality and identify any patterns before full production

**Actions:**
1. Review validation batch statistics
2. Check repair distribution patterns
3. Verify quality of detected repairs
4. Identify any systematic issues

**Output:** Decision on whether to proceed or refine

### Step 2: Identify Remaining Files 📋

**Purpose:** Know exactly which files need processing

**Actions:**
1. List all processed dialogue files
2. List all dialogue files with repairs
3. Calculate remaining files
4. Organize by student/week for efficient processing

**Output:** List of 156 files to process

### Step 3: Organize Production Batch Strategy 🎯

**Purpose:** Efficient processing with progress tracking

**Options:**
- **Option A: Single Production Batch** (Recommended)
  - Process all 156 files in one batch
  - Simple, comprehensive
  - Batch name: "production"
  
- **Option B: Multiple Smaller Batches**
  - Process by student groups (e.g., students 1-10, 18-30, etc.)
  - Easier to track progress
  - Better for monitoring
  - Batch names: "production_s1-10", "production_s18-30", etc.

**Recommendation:** Option A (single batch) - simpler and batch processor handles resumption

### Step 4: Configure Production Run ⚙️

**Settings:**
- **Model:** `gpt-enhanced` (with few-shot examples)
- **GPT Model:** `gpt-4o` (best quality)
- **Batch name:** `production`
- **Resume capability:** Yes (skip already processed)
- **Delay:** 1.0 second (rate limiting)

### Step 5: Execute Production Batch 🚀

**Command:**
```bash
python scripts/run_repair_detection_batch.py \
  --batch-name production \
  --model gpt-enhanced \
  --gpt-model gpt-4o \
  --batch-size 0 \
  --delay 1.0
```

**Expected:**
- Process ~156 remaining files
- Skip already processed (pilot/validation)
- Save to `data/repairs/production/`
- Create batch summary

**Estimated Time:** ~3-5 hours (with 1s delay between files)
**Estimated Cost:** ~$2.30 (156 files × ~$0.015/file)

### Step 6: Verification & Quality Check ✅

**Purpose:** Ensure all files processed correctly

**Actions:**
1. Verify all 206 files have repair annotations
2. Check for processing errors
3. Review batch summary
4. Generate final statistics

**Output:** Verification report

### Step 7: Final Statistics & Summary 📊

**Purpose:** Complete overview of Phase 2 results

**Actions:**
1. Aggregate statistics from all batches
2. Generate comprehensive report
3. Calculate:
   - Total repairs detected
   - Distribution by initiation (LI/BI)
   - Distribution by resolution (R/U-A/U-P)
   - Trigger categories
   - Files with/without repairs

**Output:** `data/repairs/FINAL_STATISTICS.json`

## Detailed Execution Steps

### Immediate Actions

1. ✅ **Verify current status** - Check what's already done
2. ✅ **Create execution plan** - This document
3. ⏳ **Identify remaining files** - Calculate exactly what needs processing
4. ⏳ **Execute production batch** - Process all remaining files
5. ⏳ **Verify completeness** - Ensure all files processed
6. ⏳ **Generate final report** - Complete statistics

### Processing Strategy

**Resume Capability:**
- Batch processor automatically skips already processed files
- Safe to re-run if interrupted
- Can resume from where it left off

**Error Handling:**
- Failed files logged in batch summary
- Can re-run failed files separately
- Manual review for persistent failures

**Progress Tracking:**
- Batch summary saved after each run
- Review reports available
- Statistics tracked per batch

## Expected Outcomes

### After Complete Production

- **Total files processed:** 206 dialogues
- **Repair annotations:** ~150-200 repairs (estimated)
- **Success rate:** >95% expected
- **All files:** Have repair annotation files (even if empty [])

### Files Structure

```
data/repairs/
├── pilot/
│   ├── *.json (10 files)
│   └── batch_summary.json
├── validation/
│   ├── *.json (50 files)
│   └── batch_summary.json
└── production/
    ├── *.json (156 files)
    └── batch_summary.json
```

## Risk Assessment

### Potential Issues

1. **API Rate Limits**
   - **Risk:** Medium
   - **Mitigation:** 1s delay between calls, batch processor handles retries

2. **Cost Overrun**
   - **Risk:** Low
   - **Mitigation:** ~$2.30 estimated, well within budget

3. **Processing Errors**
   - **Risk:** Low
   - **Mitigation:** Error logging, resume capability, can retry failed files

4. **Quality Concerns**
   - **Risk:** Medium (recall is low)
   - **Mitigation:** Can review and refine after production, manual review for critical files

## Quality Assurance

### Post-Processing Review

1. **Statistical Review:**
   - Check repair distribution makes sense
   - Verify no unexpected patterns

2. **Sample Review:**
   - Review 5-10 random files manually
   - Check for obvious errors

3. **Comparison:**
   - Compare with known annotations (if available)
   - Verify consistency

## Next Steps After Completion

1. **Generate comprehensive statistics**
2. **Create merged review documents**
3. **Prepare for Phase 3 analysis** (if applicable)

---

## Ready to Execute?

**Command to run:**
```bash
python scripts/run_repair_detection_batch.py \
  --batch-name production \
  --model gpt-enhanced \
  --gpt-model gpt-4o \
  --batch-size 0
```

This will:
- ✅ Process all remaining 156 files
- ✅ Skip already processed files (pilot/validation)
- ✅ Save results to `data/repairs/production/`
- ✅ Create comprehensive batch summary
- ✅ Handle errors gracefully
- ✅ Resume if interrupted

**Estimated completion:** 3-5 hours
**Estimated cost:** ~$2.30

---

**Status:** Ready for execution! 🚀

