# Phase 2: Answers to Your Questions

## Q1: Should we run all repairs at the same time or different times?

### Answer: **Different times (Batch Processing) - STRONGLY RECOMMENDED**

**Why batch processing:**
- ✅ **Cost Control:** Monitor API costs incrementally (~$3 total, but better to track)
- ✅ **Quality Control:** Review samples before full run
- ✅ **Error Recovery:** If something fails, you don't lose all progress
- ✅ **Iterative Improvement:** Refine approach based on early results
- ✅ **Rate Limiting:** Avoids API rate limits

**Recommended batches:**
1. **Pilot:** 10-20 files → Review → Refine
2. **Validation:** 50 files → Check metrics → Final adjustments
3. **Production:** Remaining ~140 files → Full run

## Q2: Should we use GPT-4 (paid) or stick with Gemini?

### Answer: **Use GPT-4 Turbo - RECOMMENDED**

**Why GPT-4 Turbo:**
- ✅ **Superior reasoning** for complex linguistic analysis
- ✅ **Better at following detailed instructions** (your prompt is complex)
- ✅ **More consistent JSON output** (fewer parsing errors)
- ✅ **Better handling of nuanced distinctions** (LI vs BI, R vs U-A vs U-P)
- ✅ **Very affordable:** ~$0.015 per dialogue = ~$3 for all 193 files

**Cost breakdown:**
- Average dialogue: ~50 turns = ~2000 input + 500 output tokens
- GPT-4 Turbo pricing: ~$0.01 input + $0.03 output per 1K tokens
- Per dialogue: ~$0.015
- **Total for 193 dialogues: ~$2.90** (extremely affordable!)

**Recommendation:** Use GPT-4 Turbo for production, keep Gemini as fallback.

## Q3: How to build feedback/re-check system?

### Answer: **Iterative Review Workflow - IMPLEMENTED**

**System I've built:**

1. **Batch Processing Script** (`scripts/run_repair_detection_batch.py`)
   - Process files in batches
   - Track progress
   - Resume capability
   - Error handling

2. **Review Tool** (`scripts/review_repairs.py`)
   - Shows dialogue + repairs side-by-side
   - Interactive review
   - Statistics generation
   - Easy to identify issues

3. **Workflow:**
   ```
   Process Pilot → Review → Refine Prompt → Process Validation → Review → Full Production
   ```

**How to use:**
```bash
# Step 1: Process pilot batch
python scripts/run_repair_detection_batch.py --batch-name pilot --model gpt --batch-size 10

# Step 2: Review results
python scripts/review_repairs.py --batch pilot

# Step 3: If issues found, refine prompt in repair_detector.py

# Step 4: Process validation batch
python scripts/run_repair_detection_batch.py --batch-name validation --model gpt --batch-size 50

# Step 5: Review validation
python scripts/review_repairs.py --batch validation --report-only

# Step 6: Full production
python scripts/run_repair_detection_batch.py --batch-name production --model gpt --batch-size 0
```

## Q4: How to make Phase 2 most accurate, correct, and efficient?

### Answer: **Multi-Layer Quality Assurance System**

**Accuracy:**
1. ✅ **Use GPT-4 Turbo** (better reasoning)
2. ✅ **Comprehensive prompt** (already excellent, can refine)
3. ✅ **Validation checks** (schema, logical, statistical)
4. ✅ **Manual review** (pilot batch)
5. ✅ **Iterative refinement** (improve based on feedback)

**Correctness:**
1. ✅ **Automated validation** (required fields, data types, values)
2. ✅ **Logical checks** (turn indices in bounds, no overlaps)
3. ✅ **Cross-validation** (compare with manual annotations if available)
4. ✅ **Review tool** (catch systematic issues)

**Efficiency:**
1. ✅ **Batch processing** (parallel where possible, but controlled)
2. ✅ **Resume capability** (don't reprocess completed files)
3. ✅ **Progress tracking** (know where you are)
4. ✅ **Error handling** (retry failed files)
5. ✅ **Cost monitoring** (track API usage)

## Q5: Is the current prompt good?

### Answer: **Yes, it's excellent! But can be improved**

### Current Prompt Strengths ✅

1. **Comprehensive theoretical definitions**
   - Clear definitions of repair sequences
   - Detailed initiation (LI/BI) criteria
   - Resolution (R/U-A/U-P) guidelines
   - Trigger categories

2. **Clear examples of what NOT to mark**
   - Prevents false positives
   - Distinguishes normal conversation from repairs

3. **Detailed decision strategy**
   - Step-by-step analysis approach
   - Clear splitting vs merging rules

4. **Good output schema**
   - Well-defined JSON structure
   - Required fields specified

### Potential Improvements 🔧

1. **Add Few-Shot Examples** (High Impact)
   - Include 2-3 real examples in prompt
   - Show edge cases (split repairs, self-corrections)
   - Helps model understand expected output format

2. **Strengthen JSON Output Instructions** (Medium Impact)
   - More explicit about JSON formatting
   - Add example of complete valid output
   - Emphasize "return ONLY JSON, no commentary"

3. **Clarify Edge Cases** (Medium Impact)
   - More examples of split vs merged repairs
   - Better distinction between R and U-P
   - When to mark as U-A vs U-P

4. **Add Confidence Indicators** (Optional)
   - Ask model to indicate confidence level
   - Helps identify cases needing review

5. **Context Window Optimization** (For long dialogues)
   - For dialogues >100 turns, consider chunking strategy

### Recommendation

**Start with current prompt** → Process pilot batch → Review results → Refine if needed

The current prompt is very good. Refinements should be based on actual results, not speculation.

## Summary: Best Approach

### ✅ Recommended Strategy

1. **Model:** GPT-4 Turbo (you have paid access, better quality)
2. **Processing:** Batch processing (pilot → validation → production)
3. **Review:** Iterative feedback system (built tools ready)
4. **Prompt:** Start with current (excellent), refine based on pilot review
5. **Quality:** Multi-layer validation (automated + manual)

### 📊 Expected Timeline

- **Week 1:** Pilot batch + review + refinement
- **Week 2:** Validation batch + metrics check
- **Week 3:** Full production

### 💰 Expected Cost

- **Total:** ~$3 for all 193 dialogues
- **Very affordable!** Worth it for better quality

### 🎯 Success Metrics

- **Quality:** Precision, recall (if manual annotations available)
- **Efficiency:** Processing time, cost per dialogue
- **Reliability:** Error rate, retry rate

---

## Ready to Start?

**Next command to run:**
```bash
python scripts/run_repair_detection_batch.py --batch-name pilot --model gpt --batch-size 10
```

This will process 10 files with GPT-4 Turbo and save results for review!

