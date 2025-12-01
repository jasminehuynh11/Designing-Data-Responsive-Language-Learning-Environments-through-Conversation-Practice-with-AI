# Phase 2: Repair Detection - Comprehensive Strategy Plan

## Executive Summary

This document outlines the optimal strategy for Phase 2 repair detection, addressing:
- Batch processing vs. all-at-once
- Model selection (GPT-4 vs Gemini)
- Iterative feedback system
- Quality assurance workflow
- Prompt optimization

## 1. Processing Strategy: Batch Processing (Recommended)

### Why Batch Processing?

**193 files is too many to process all at once because:**
- **Cost Control:** Allows monitoring API costs incrementally
- **Error Recovery:** If something fails, you don't lose all progress
- **Quality Control:** Review samples before full run
- **Rate Limiting:** Avoids API rate limits
- **Iterative Improvement:** Refine approach based on early results

### Recommended Batch Strategy

**Phase 2A: Pilot Batch (10-20 files)**
- Process diverse sample (different students, weeks, task types)
- Manual review of results
- Identify common issues
- Refine prompt if needed

**Phase 2B: Validation Batch (50 files)**
- Process larger sample with refined approach
- Statistical validation
- Quality metrics check
- Final prompt adjustments

**Phase 2C: Full Production (Remaining ~140 files)**
- Process all remaining files
- Automated quality checks
- Progress tracking

## 2. Model Selection: GPT-4 Turbo vs Gemini

### Current Setup: Gemini
- **Pros:** Free tier available, good performance
- **Cons:** May have rate limits, less powerful than GPT-4

### GPT-4 Turbo (Recommended for Paid Access)
- **Pros:**
  - Superior reasoning for complex linguistic analysis
  - Better at following detailed instructions
  - More consistent JSON output
  - Higher token limits
  - Better handling of nuanced distinctions (LI vs BI, R vs U-A vs U-P)
- **Cons:** Costs money (~$0.01-0.03 per dialogue depending on length)

### Recommendation: **Hybrid Approach**

1. **Use GPT-4 Turbo for production** (you have paid access)
2. **Keep Gemini as fallback** (if GPT has issues)
3. **A/B test on sample** (compare results on same dialogues)

### Cost Estimate
- Average dialogue: ~50 turns = ~2000 input tokens + ~500 output tokens
- GPT-4 Turbo: ~$0.015 per dialogue
- 193 dialogues: ~$2.90 total (very affordable!)

## 3. Iterative Feedback System

### Workflow Design

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Pilot Batch (10-20 files)                       │
│   → Process with GPT-4 Turbo                            │
│   → Save to data/repairs/pilot/                          │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: Manual Review                                    │
│   → Review tool shows dialogue + repairs side-by-side    │
│   → Mark: Correct / Needs Fix / False Positive          │
│   → Collect feedback on common issues                   │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: Prompt Refinement                                │
│   → Analyze review feedback                              │
│   → Update prompt to address issues                     │
│   → Version control prompts                             │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 4: Validation Batch (50 files)                      │
│   → Process with refined prompt                          │
│   → Automated quality checks                             │
│   → Compare metrics to pilot                             │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 5: Final Production (Remaining files)               │
│   → Process all remaining                                │
│   → Automated validation                                 │
│   → Progress tracking                                    │
└─────────────────────────────────────────────────────────┘
```

## 4. Quality Assurance System

### Automated Checks

1. **Schema Validation**
   - All required fields present
   - Correct data types
   - Valid values (LI/BI, R/U-A/U-P)

2. **Logical Validation**
   - Turn indices within dialogue bounds
   - Repair IDs sequential
   - No overlapping repairs (unless intentional)

3. **Statistical Validation**
   - Repair count distribution (some dialogues should have 0)
   - Initiation distribution (LI vs BI ratio)
   - Resolution distribution (R vs U-A vs U-P ratio)
   - Trigger category distribution

4. **Cross-Validation**
   - Compare with manual annotations (if available)
   - Check consistency across similar dialogues

### Manual Review Tool

Create a web-based or notebook-based review interface:
- Side-by-side dialogue and repairs
- Easy marking: ✓ Correct | ✗ Needs Fix | ⚠ Review
- Export feedback for prompt refinement

## 5. Prompt Analysis & Improvements

### Current Prompt Strengths ✅
- Comprehensive theoretical definitions
- Clear examples of what NOT to mark
- Detailed decision strategy
- Good output schema specification

### Potential Improvements 🔧

1. **Add Few-Shot Examples**
   - Include 2-3 real examples in prompt
   - Show edge cases (e.g., split repairs, self-corrections)

2. **Strengthen JSON Output Instructions**
   - More explicit about JSON formatting
   - Add example of complete valid output

3. **Clarify Edge Cases**
   - More examples of split vs. merged repairs
   - Better distinction between R and U-P

4. **Add Confidence Indicators** (Optional)
   - Ask model to indicate confidence level
   - Helps identify cases needing review

5. **Context Window Optimization**
   - For very long dialogues (>100 turns), consider chunking strategy

## 6. Implementation Plan

### Step-by-Step Execution

**Week 1: Setup & Pilot**
1. Implement GPT-4 Turbo support
2. Create batch processing script
3. Process pilot batch (10-20 files)
4. Create review tool
5. Manual review of pilot results

**Week 2: Refinement**
1. Analyze review feedback
2. Refine prompt (v2)
3. Process validation batch (50 files)
4. Automated quality checks
5. Compare metrics

**Week 3: Production**
1. Final prompt (v3 if needed)
2. Process remaining files in batches
3. Continuous quality monitoring
4. Error handling and retry logic

### Tools to Build

1. **Batch Processor Script**
   - Process N files at a time
   - Progress tracking
   - Resume capability
   - Error handling

2. **Review Tool**
   - Jupyter notebook or web interface
   - Side-by-side view
   - Feedback collection

3. **Quality Metrics Dashboard**
   - Real-time statistics
   - Anomaly detection
   - Comparison across batches

4. **Prompt Version Control**
   - Track prompt versions
   - Link versions to results
   - A/B comparison

## 7. Risk Mitigation

### Potential Issues & Solutions

| Issue | Risk | Mitigation |
|-------|------|------------|
| API Rate Limits | High | Batch processing, exponential backoff |
| Cost Overruns | Medium | Monitor costs, set budget alerts |
| Quality Degradation | High | Pilot batch, review, metrics |
| JSON Parsing Errors | Medium | Robust extraction, validation |
| Model Hallucination | Medium | Validation checks, review tool |

## 8. Success Metrics

### Quality Metrics
- **Precision:** % of detected repairs that are correct
- **Recall:** % of actual repairs that were detected
- **F1 Score:** Balance of precision and recall
- **Inter-annotator Agreement:** (if manual annotations available)

### Efficiency Metrics
- **Processing Time:** Time per dialogue
- **Cost per Dialogue:** API costs
- **Error Rate:** % of failed processing attempts
- **Retry Rate:** % requiring reprocessing

## 9. Next Steps

1. ✅ Review this plan
2. ⏳ Implement GPT-4 Turbo support
3. ⏳ Create batch processing script
4. ⏳ Build review tool
5. ⏳ Process pilot batch
6. ⏳ Refine based on feedback
7. ⏳ Full production run

---

**Status:** Planning Complete
**Recommended Approach:** Batch Processing + GPT-4 Turbo + Iterative Refinement
**Estimated Timeline:** 2-3 weeks for full production
**Estimated Cost:** ~$3-5 for all 193 dialogues

