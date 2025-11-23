"""
Task topic classification based on dialogue content.
Maps dialogues to task scenarios from Language Tasks.pdf.
"""
import re
from typing import Dict, Any, Optional


# Task topic mapping based on Language Tasks.pdf
TASK_TOPICS = {
    "Ordering Coffee at a Café": [
        "coffee", "café", "cafe", "latte", "espresso", "cappuccino", 
        "matcha", "order", "drink", "barista", "menu"
    ],
    "Booking a Restaurant Table": [
        "restaurant", "table", "reservation", "book", "dinner", 
        "reserve", "seating", "party", "guests"
    ],
    "Returning or Exchanging Clothes": [
        "return", "exchange", "clothes", "clothing", "refund", 
        "store", "policy", "receipt"
    ],
    "Visiting a Medical Clinic": [
        "medical", "clinic", "doctor", "appointment", "toothache", 
        "dentist", "health", "symptom", "pain"
    ],
    "Visiting a Bank": [
        "bank", "banking", "account", "deposit", "withdraw", 
        "balance", "transaction", "card"
    ],
    "Enquiring About a Rental Property": [
        "rental", "property", "apartment", "house", "rent", 
        "inspection", "lease", "landlord"
    ],
    "Reporting an Internet Outage": [
        "internet", "outage", "connection", "wifi", "router", 
        "network", "online", "signal"
    ],
    "Reporting a Lost Item": [
        "lost", "item", "police", "report", "missing", 
        "found", "belongings"
    ],
    "Requesting Maintenance or Repairs": [
        "maintenance", "repair", "fix", "broken", "issue", 
        "problem", "service", "technician"
    ],
    "Seeking Technical Support": [
        "technical", "support", "device", "help", "troubleshoot", 
        "error", "software", "hardware"
    ],
    "Discussing Study or Career Plans": [
        "study", "career", "advisor", "university", "education", 
        "overseas", "abroad", "program", "course"
    ],
    "Participating in Group Decisions": [
        "group", "decision", "negotiate", "discuss", "meeting", 
        "team", "agree", "consensus"
    ],
    "Responding to Feedback": [
        "feedback", "review", "performance", "evaluation", 
        "improve", "suggestions"
    ]
}


def classify_task_topic(dialogue_data: Dict[str, Any]) -> Optional[str]:
    """
    Classify the task topic based on dialogue content.
    
    Args:
        dialogue_data: Dialogue JSON with turns
    
    Returns:
        Task topic string or None if not identifiable
    """
    # Combine all turn text
    all_text = " ".join([
        turn.get('text', '') for turn in dialogue_data.get('turns', [])
    ]).lower()
    
    # Score each topic
    topic_scores = {}
    for topic, keywords in TASK_TOPICS.items():
        score = sum(1 for keyword in keywords if keyword in all_text)
        if score > 0:
            topic_scores[topic] = score
    
    if not topic_scores:
        return None
    
    # Return topic with highest score
    return max(topic_scores.items(), key=lambda x: x[1])[0]


def add_task_topic_to_dialogue(dialogue_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add task_topic field to dialogue data.
    
    Args:
        dialogue_data: Dialogue JSON
    
    Returns:
        Dialogue JSON with task_topic added
    """
    dialogue_data = dialogue_data.copy()
    task_topic = classify_task_topic(dialogue_data)
    if task_topic:
        dialogue_data['task_topic'] = task_topic
    return dialogue_data

