"""
Enhanced repair detection with few-shot examples and improved prompt.
Uses GPT-4o for best accuracy.
"""
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Import base prompt
from repair_detector import REPAIR_DETECTION_SYSTEM_PROMPT, create_user_prompt, validate_repair_annotation

# Load few-shot examples
FEW_SHOT_EXAMPLES = """
===============================
FEW-SHOT EXAMPLES
===============================

These examples show correct repair annotations from real dialogues. Study them carefully to understand the expected format and reasoning.

EXAMPLE 1: Pronunciation/ASR Repair (BI → R)

Dialogue excerpt:
  Turn 5 (learner): "HOTAS."
  Turn 6 (bot): Great, a hot matcha latte it is! Would you like any specific milk, like almond, oat, or regular dairy?

Correct annotation:
{
  "dialogue_id": "W1_T1_S18",
  "repair_id": 1,
  "turn_indices": [5, 6],
  "initiation": "BI",
  "resolution": "R",
  "trigger": "pronunciation/ASR – misrecognition of learner speech",
  "evidence_summary": "The learner says 'HOTAS' in turn 5, which is an unclear utterance. The bot implicitly repairs this by interpreting it as 'hot' in turn 6, and the conversation continues smoothly, indicating successful understanding."
}

EXAMPLE 2: Self-Correction Repair (LI → R)

Dialogue excerpt:
  Turn 29 (learner): "Yes, she'll have a slice of, um, no, a banana bread with gluten-free and she'll like espresso."
  Turn 30 (bot): Perfect! So that's one gluten-free banana bread and one espresso for your friend. That sounds lovely!

Correct annotation:
{
  "dialogue_id": "W1_T1_S18",
  "repair_id": 2,
  "turn_indices": [29, 30],
  "initiation": "LI",
  "resolution": "R",
  "trigger": "self-correction – learner corrects own previous utterance",
  "evidence_summary": "The learner explicitly self-corrects their order from an initial hesitation ('um, no') to 'a banana bread' in turn 29. The bot successfully processes this corrected order in turn 30, resolving the self-correction."
}

EXAMPLE 3: Split Repairs (BI + LI)

Dialogue excerpt:
  Turn 57 (learner): "I would like without milk."
  Turn 58 (bot): "Perfect, oat milk it is! Would you like..."
  Turn 59 (learner): "No, I mean almond milk."
  Turn 60 (bot): "Got it! Almond milk it is."

This contains TWO separate repairs:
1. Bot misunderstanding (turns 57-58): BI, R - Bot misinterprets "without milk" as suggesting oat milk
2. Learner clarification (turns 59-60): LI, R - Learner corrects to specify almond milk

===============================
"""

# Enhanced prompt with few-shot examples
ENHANCED_REPAIR_DETECTION_PROMPT = REPAIR_DETECTION_SYSTEM_PROMPT.replace(
    "===============================\nTHEORETICAL DEFINITIONS\n===============================",
    FEW_SHOT_EXAMPLES + "\n===============================\nTHEORETICAL DEFINITIONS\n==============================="
)

# Add chain-of-thought reasoning section
CHAIN_OF_THOUGHT_SECTION = """

===============================
REASONING PROCESS
===============================

Before outputting JSON, think through each potential repair step-by-step:

1. **Identify trouble:** What specific communication problem occurred? Look for:
   - Explicit signals ("I don't understand", "Sorry, I didn't catch that")
   - Implicit signals (unclear utterances, irrelevant responses, self-corrections)

2. **Check repair attempt:** Did someone try to fix it? Who?
   - Learner asking for clarification = repair attempt
   - Bot interpreting/rephrasing = repair attempt
   - Self-correction = repair attempt

3. **Determine initiation:** Who FIRST signaled the trouble?
   - If learner's utterance was unclear and bot interpreted → BI
   - If bot's response was confusing and learner asked → LI
   - If learner self-corrected → LI

4. **Assess resolution:** How did it end? Look at SUBSEQUENT turns:
   - Conversation continues smoothly → R (Resolved)
   - Topic changes without resolution → U-A (Unresolved-Abandoned)
   - Multiple attempts, ongoing confusion → U-P (Unresolved-Persists)

5. **Classify trigger:** What specifically caused the trouble?
   - Vocabulary issue
   - Pronunciation/ASR error
   - Grammar/fragmentation
   - Contextual/logical error
   - Bot misunderstanding
   - Self-correction

6. **Verify boundaries:** Are all relevant turns included?
   - Include turn where trouble starts
   - Include all clarification attempts
   - Include resolution confirmation turn

Only after completing this reasoning for ALL potential repairs, output the JSON array.

"""

# Final enhanced prompt
FINAL_ENHANCED_PROMPT = ENHANCED_REPAIR_DETECTION_PROMPT.replace(
    "===============================\nDECISION STRATEGY\n===============================",
    CHAIN_OF_THOUGHT_SECTION + "\n===============================\nDECISION STRATEGY\n==============================="
)


def get_openai_client() -> OpenAI:
    """Get OpenAI client with API key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    return OpenAI(api_key=api_key)


def detect_repairs_enhanced(
    dialogue_data: Dict[str, Any],
    model: str = "gpt-4o",
    client: Optional[OpenAI] = None,
    use_enhanced_prompt: bool = True
) -> List[Dict[str, Any]]:
    """
    Detect repair sequences using enhanced GPT-4o with few-shot examples.
    
    Args:
        dialogue_data: Dialogue JSON with student_id, dialogue_id, and turns
        model: GPT model to use (default: gpt-4o - newest and best)
        client: Optional OpenAI client
        use_enhanced_prompt: Whether to use enhanced prompt with few-shot examples
    
    Returns:
        List of repair annotation dictionaries
    """
    if client is None:
        client = get_openai_client()
    
    # Create user prompt
    user_prompt = create_user_prompt(dialogue_data)
    
    # Use enhanced prompt if requested
    system_prompt = FINAL_ENHANCED_PROMPT if use_enhanced_prompt else REPAIR_DETECTION_SYSTEM_PROMPT
    
    # Combine prompts
    full_prompt = system_prompt + "\n\n" + user_prompt
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert analyst of learner–AI dialogues. Follow the instructions precisely and return only valid JSON."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            temperature=0,  # Maximum determinism for consistency
            max_tokens=8192,  # Ensure enough tokens for complete JSON
            # Note: gpt-4o may support response_format, but test first
        )
        
        response_text = response.choices[0].message.content
        
        # Extract JSON from response
        repairs = extract_json_from_response(response_text)
        
        return repairs
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return []


def extract_json_from_response(response_text: str) -> List[Dict[str, Any]]:
    """Extract JSON array from GPT response, handling markdown code blocks."""
    # Remove markdown code blocks if present
    if "```json" in response_text:
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
    elif "```" in response_text:
        response_text = re.sub(r'```\s*', '', response_text)
    
    # Try to find JSON array
    json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group(0)
    
    # Parse JSON
    try:
        repairs = json.loads(response_text)
        if not isinstance(repairs, list):
            # If it's a dict with a 'repairs' key, extract that
            if isinstance(repairs, dict) and 'repairs' in repairs:
                repairs = repairs['repairs']
            else:
                return []
        return repairs
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse JSON from GPT response: {e}")
        print(f"Response text (first 500 chars): {response_text[:500]}")
        return []

