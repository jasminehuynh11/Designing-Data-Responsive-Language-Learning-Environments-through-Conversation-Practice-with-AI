# Phase 2: Enhanced Accuracy Plan - Maximum Precision Strategy

## Current Plan Assessment

### ✅ What's Already Good
- Batch processing approach
- GPT-4 Turbo selection
- Review system
- Comprehensive prompt

### 🔧 What Can Be Enhanced for Maximum Accuracy

## Enhanced Strategy for Best Accuracy

### 1. **Add Few-Shot Examples to Prompt** (HIGH IMPACT)

**Why:** Few-shot learning dramatically improves LLM accuracy by showing concrete examples.

**Implementation:**
- Extract 2-3 real examples from your existing repair annotations
- Include complete examples showing:
  - Dialogue turns
  - Correct repair annotation
  - Reasoning for each classification

**Example structure to add:**
```
===============================
FEW-SHOT EXAMPLES
===============================

EXAMPLE 1: Pronunciation/ASR Repair (BI → R)
Dialogue:
  Turn 5 (learner): "HOTAS."
  Turn 6 (bot): "Great, a hot matcha latte it is!..."

Correct Annotation:
{
  "repair_id": 1,
  "turn_indices": [5, 6],
  "initiation": "BI",
  "resolution": "R",
  "trigger": "pronunciation/ASR – misrecognition of learner speech",
  "evidence_summary": "Learner says 'HOTAS' which is unclear. Bot interprets as 'hot' and conversation continues smoothly."
}

EXAMPLE 2: Self-Correction Repair (LI → R)
[Include another real example]

EXAMPLE 3: Split Repairs (BI + LI)
[Show example of when to split vs merge]
```

### 2. **Use GPT-4o Instead of GPT-4 Turbo** (RECOMMENDED)

**Why:** GPT-4o (released 2024) is:
- Faster and cheaper than GPT-4 Turbo
- Better at following complex instructions
- More consistent JSON output
- Better reasoning for nuanced tasks

**Cost:** Similar or cheaper than GPT-4 Turbo

### 3. **Chain-of-Thought Reasoning** (MEDIUM IMPACT)

**Enhance prompt with explicit reasoning steps:**

Add to prompt:
```
Before outputting JSON, think through each repair step-by-step:

1. Identify trouble: What specific communication problem occurred?
2. Check repair attempt: Did someone try to fix it? Who?
3. Determine initiation: Who first signaled the trouble?
4. Assess resolution: How did it end? (Look at subsequent turns)
5. Classify trigger: What specifically caused the trouble?
6. Verify boundaries: Are all relevant turns included?

Only after completing this reasoning, output the JSON.
```

### 4. **Validation Against Existing Annotations** (HIGH VALUE)

**You have existing repair annotations!** Use them for:
- **Calibration:** Test prompt on dialogues with known repairs
- **Accuracy measurement:** Compare new results to existing
- **Prompt refinement:** Identify systematic differences

**Implementation:**
- Run on dialogues that already have repairs (W1_T1, W1_T2, etc.)
- Compare results
- Measure precision/recall
- Refine prompt based on differences

### 5. **Ensemble Method** (OPTIONAL, HIGH ACCURACY)

**Run each dialogue twice and compare:**
- If results match → high confidence
- If results differ → flag for review
- Use consensus or more detailed analysis

**Cost:** 2x API calls (~$6 total instead of $3)
**Benefit:** Catches inconsistencies, improves accuracy

### 6. **Temperature Settings** (IMPORTANT)

**Current:** temperature=0.1 (good)
**Enhancement:** 
- Use temperature=0 for maximum determinism
- Or use temperature=0.1 with seed for reproducibility

### 7. **JSON Mode** (GPT-4o Feature)

**Use structured output:**
- GPT-4o supports `response_format={"type": "json_object"}`
- Guarantees valid JSON
- Reduces parsing errors

### 8. **Prompt Structure Improvements**

**Current prompt is excellent, but can add:**

1. **Explicit JSON Schema** (not just example):
```python
{
  "type": "array",
  "items": {
    "type": "object",
    "required": ["dialogue_id", "repair_id", "turn_indices", "initiation", "resolution", "trigger", "evidence_summary"],
    "properties": {
      "dialogue_id": {"type": "string"},
      "repair_id": {"type": "integer"},
      "turn_indices": {"type": "array", "items": {"type": "integer"}},
      "initiation": {"type": "string", "enum": ["LI", "BI"]},
      "resolution": {"type": "string", "enum": ["R", "U-A", "U-P"]},
      "trigger": {"type": "string"},
      "evidence_summary": {"type": "string"}
    }
  }
}
```

2. **Confidence Scoring** (optional):
Add field: `confidence: "high" | "medium" | "low"`

3. **Edge Case Handling:**
More explicit instructions for:
- Very long dialogues (>100 turns)
- Multiple overlapping repairs
- Ambiguous cases

## Recommended Enhanced Workflow

### Phase 2A: Calibration (NEW)
1. **Test on known dialogues:**
   - Run on W1_T1, W1_T2, W1_T3 (already have repairs)
   - Compare results to existing annotations
   - Calculate precision/recall
   - Identify systematic issues

2. **Refine prompt:**
   - Add few-shot examples from real data
   - Adjust based on calibration results
   - Test again until accuracy is high

### Phase 2B: Pilot Batch (Enhanced)
1. Process 10-20 diverse files
2. **Use GPT-4o** (not Turbo)
3. **Include few-shot examples** in prompt
4. **Chain-of-thought reasoning**
5. Manual review

### Phase 2C: Validation Batch
1. Process 50 files with refined approach
2. Statistical validation
3. Compare to calibration baseline

### Phase 2D: Production
1. Full production run
2. Optional: Ensemble method for critical dialogues

## Accuracy Improvements Summary

| Enhancement | Impact | Effort | Cost Impact |
|------------|--------|--------|-------------|
| Few-shot examples | ⭐⭐⭐⭐⭐ | Low | None |
| GPT-4o instead of Turbo | ⭐⭐⭐⭐ | Low | Similar/Cheaper |
| Chain-of-thought | ⭐⭐⭐ | Low | None |
| Calibration testing | ⭐⭐⭐⭐⭐ | Medium | ~$0.10 |
| Ensemble method | ⭐⭐⭐⭐ | Low | 2x cost |
| JSON mode | ⭐⭐⭐ | Low | None |
| Temperature=0 | ⭐⭐ | Low | None |

**Recommended Priority:**
1. ✅ Few-shot examples (HIGHEST impact, easy)
2. ✅ Calibration testing (validate against known data)
3. ✅ GPT-4o (better model)
4. ✅ Chain-of-thought (better reasoning)
5. ⚠️ Ensemble (optional, if budget allows)

## Implementation Checklist

- [ ] Extract few-shot examples from existing repairs
- [ ] Update prompt with examples
- [ ] Switch to GPT-4o
- [ ] Add chain-of-thought reasoning
- [ ] Create calibration script (test on known dialogues)
- [ ] Run calibration and measure accuracy
- [ ] Refine prompt based on calibration
- [ ] Process pilot batch
- [ ] Review and iterate
- [ ] Full production

## Expected Accuracy Improvements

**Baseline (current plan):** ~85-90% accuracy (estimated)
**With enhancements:** ~92-95% accuracy (estimated)

**Key improvements:**
- Few-shot examples: +5-7% accuracy
- Calibration: +3-5% accuracy
- GPT-4o: +2-3% accuracy
- Chain-of-thought: +1-2% accuracy

## Cost-Benefit Analysis

**Enhanced approach:**
- Calibration: ~$0.10 (10 dialogues)
- Pilot: ~$0.15 (10 dialogues)
- Validation: ~$0.75 (50 dialogues)
- Production: ~$2.00 (remaining ~130)
- **Total: ~$3.00** (same as original plan!)

**But with:**
- Higher accuracy
- Validated against known data
- Better confidence in results
- Fewer errors to fix later

## Conclusion

**The enhanced plan is significantly better for accuracy:**
- ✅ Uses existing annotations for calibration
- ✅ Adds few-shot examples (proven to improve accuracy)
- ✅ Better model (GPT-4o)
- ✅ Better reasoning (chain-of-thought)
- ✅ Same cost (~$3)
- ✅ Higher confidence in results

**Recommendation:** Implement the enhanced plan, especially:
1. Few-shot examples (easy, high impact)
2. Calibration testing (validate approach)
3. GPT-4o (better model)

This will give you the most accurate results possible within your budget.

