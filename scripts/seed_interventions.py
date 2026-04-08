"""
Seed interventions table with CBT, mindfulness, and psychoeducation content.
Usage: python -m scripts.seed_interventions
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.session import async_session
from app.models.intervention import Intervention

INTERVENTIONS = [
    # CBT Interventions
    {
        "title": "Thought Record",
        "description": "Identify and challenge negative automatic thoughts",
        "intervention_type": "cbt",
        "content": {
            "description": "A thought record helps you notice negative thinking patterns and reframe them into more balanced thoughts.",
            "steps": [
                "Notice when your mood shifts negatively",
                "Write down the situation — what happened?",
                "Record the automatic thought — what went through your mind?",
                "Identify the emotion and rate its intensity (0-100%)",
                "Look for evidence that supports the thought",
                "Look for evidence against the thought",
                "Create a balanced alternative thought",
                "Re-rate the emotion intensity",
            ],
            "duration": "10-15 minutes",
            "benefits": ["Reduces rumination", "Builds awareness of thinking patterns", "Improves emotional regulation"],
        },
        "target_personas": ["manoveil_core", "manobalance", "manospark"],
        "target_categories": ["mild", "moderate", "moderately_severe"],
        "duration_minutes": 15,
    },
    {
        "title": "Behavioral Activation",
        "description": "Schedule enjoyable activities to improve mood",
        "intervention_type": "cbt",
        "content": {
            "description": "When feeling low, we tend to withdraw from activities. Behavioral activation breaks this cycle by scheduling pleasant activities.",
            "steps": [
                "List 5-10 activities you used to enjoy",
                "Rate each on a scale of 1-10 for how pleasant they are",
                "Pick 2-3 activities for this week",
                "Schedule specific times for each activity",
                "Do the activity even if you don't feel like it",
                "Rate your mood before and after each activity",
                "Review what worked at the end of the week",
            ],
            "duration": "Ongoing (5 min planning)",
            "benefits": ["Breaks the cycle of withdrawal", "Boosts natural mood-enhancing chemicals", "Rebuilds a sense of accomplishment"],
        },
        "target_personas": ["manoveil_core", "manobalance", "manosaathi"],
        "target_categories": ["mild", "moderate"],
        "duration_minutes": 10,
    },
    {
        "title": "Worry Time",
        "description": "Contain anxious thoughts to a specific time period",
        "intervention_type": "cbt",
        "content": {
            "description": "Instead of worrying all day, designate a specific 'worry time' to process anxious thoughts.",
            "steps": [
                "Choose a 15-minute window each day as your worry time",
                "When a worry pops up outside that time, write it down and postpone it",
                "During worry time, review your worry list",
                "For each worry, ask: Can I do something about this?",
                "If yes, make a simple action plan",
                "If no, practice letting go using a grounding technique",
                "After 15 minutes, stop and move to a pleasant activity",
            ],
            "duration": "15 minutes daily",
            "benefits": ["Reduces constant worrying", "Gives structure to anxious thoughts", "Improves focus during the day"],
        },
        "target_personas": ["manoveil_core", "manobalance", "manospark"],
        "target_categories": ["mild", "moderate", "moderately_severe"],
        "duration_minutes": 15,
    },

    # Mindfulness Interventions
    {
        "title": "Body Scan Meditation",
        "description": "Progressive relaxation through body awareness",
        "intervention_type": "mindfulness",
        "content": {
            "description": "A guided body scan helps you release physical tension and connect with the present moment.",
            "steps": [
                "Lie down or sit comfortably. Close your eyes.",
                "Take 3 deep breaths to settle in",
                "Focus attention on the top of your head",
                "Slowly move attention down: forehead, eyes, jaw",
                "Notice shoulders, arms, hands — release any tension",
                "Move to chest, belly — notice your breath here",
                "Continue down: hips, thighs, knees, calves, feet",
                "Take a final full-body breath and gently open your eyes",
            ],
            "duration": "10-20 minutes",
            "benefits": ["Reduces physical tension", "Improves body awareness", "Promotes relaxation and better sleep"],
        },
        "target_personas": ["manoveil_core", "manobalance", "manosaathi", "manospark"],
        "target_categories": ["minimal", "mild", "moderate"],
        "duration_minutes": 15,
    },
    {
        "title": "Mindful Breathing",
        "description": "Simple focused breathing to calm the nervous system",
        "intervention_type": "mindfulness",
        "content": {
            "description": "Focused breathing activates the parasympathetic nervous system, reducing stress and anxiety.",
            "steps": [
                "Find a quiet spot and sit comfortably",
                "Close your eyes or soften your gaze",
                "Breathe in slowly for 4 counts",
                "Hold gently for 4 counts",
                "Exhale slowly for 6 counts",
                "When your mind wanders, gently bring attention back to the breath",
                "Continue for 5-10 minutes",
                "Notice how you feel compared to when you started",
            ],
            "duration": "5-10 minutes",
            "benefits": ["Immediately calms anxiety", "Can be done anywhere", "Improves focus and clarity"],
        },
        "target_personas": ["manomitra", "manospark", "manoveil_core", "manobalance", "manosaathi"],
        "target_categories": ["minimal", "mild", "moderate", "moderately_severe"],
        "duration_minutes": 10,
    },
    {
        "title": "Gratitude Journaling",
        "description": "Daily practice of noticing positive aspects of life",
        "intervention_type": "mindfulness",
        "content": {
            "description": "Writing down things you're grateful for shifts attention from what's wrong to what's right.",
            "steps": [
                "Set aside 5 minutes at the end of each day",
                "Write down 3 things you're grateful for today",
                "Be specific — not just 'my family' but 'my sister called to check on me'",
                "Include at least one small, easily overlooked good thing",
                "Notice how it feels to recall these moments",
            ],
            "duration": "5 minutes daily",
            "benefits": ["Improves overall mood", "Builds positive thinking habits", "Enhances relationships and empathy"],
        },
        "target_personas": ["manospark", "manoveil_core", "manobalance", "manosaathi"],
        "target_categories": ["minimal", "mild", "moderate"],
        "duration_minutes": 5,
    },

    # Psychoeducation
    {
        "title": "Understanding Anxiety",
        "description": "Learn how anxiety works in the brain and body",
        "intervention_type": "psychoeducation",
        "content": {
            "description": "Anxiety is a normal response that becomes a problem when it's too frequent or intense. Understanding the mechanism helps you manage it.",
            "steps": [
                "Read: Anxiety is the brain's alarm system — the amygdala detects threat and triggers fight-or-flight",
                "Physical symptoms (racing heart, sweating, tension) are your body preparing for action",
                "Anxious thoughts are the brain's attempt to prepare for worst-case scenarios",
                "The good news: these responses are temporary and manageable",
                "Key strategies: breathing (calms the body), cognitive reframing (calms the mind), exposure (retrains the brain)",
            ],
            "duration": "5 minutes reading",
            "benefits": ["Normalizes anxiety symptoms", "Reduces fear of anxiety itself", "Provides framework for coping"],
        },
        "target_personas": ["manospark", "manoveil_core", "manobalance"],
        "target_categories": ["mild", "moderate", "moderately_severe"],
        "duration_minutes": 5,
    },
    {
        "title": "Sleep Hygiene Basics",
        "description": "Evidence-based practices for better sleep",
        "intervention_type": "psychoeducation",
        "content": {
            "description": "Poor sleep amplifies stress and emotional reactivity. Good sleep hygiene can dramatically improve mental health.",
            "steps": [
                "Keep a consistent sleep schedule — same bedtime and wake time, even weekends",
                "Create a wind-down routine: dim lights 1 hour before bed",
                "Avoid screens (phone, laptop) 30 minutes before sleep",
                "Keep your bedroom cool, dark, and quiet",
                "Avoid caffeine after 2pm and heavy meals before bed",
                "If you can't sleep after 20 minutes, get up and do something calming, then return",
                "Exercise regularly, but not within 3 hours of bedtime",
            ],
            "duration": "5 minutes reading",
            "benefits": ["Improves sleep quality", "Reduces daytime fatigue", "Stabilizes mood and stress levels"],
        },
        "target_personas": ["manospark", "manoveil_core", "manobalance", "manosaathi"],
        "target_categories": ["minimal", "mild", "moderate"],
        "duration_minutes": 5,
    },
    {
        "title": "Emotional Feelings Chart",
        "description": "Learn to identify and name your emotions",
        "intervention_type": "psychoeducation",
        "content": {
            "description": "Being able to name your feelings is the first step to managing them. This is called 'emotional literacy'.",
            "steps": [
                "Primary emotions: Happy, Sad, Angry, Scared, Disgusted, Surprised",
                "Each has many shades — 'Sad' might really be lonely, disappointed, grieving, or helpless",
                "Practice: Right now, what are you feeling? Try to find the most specific word",
                "Notice where you feel it in your body",
                "Remember: all emotions are valid — there are no 'bad' feelings, only uncomfortable ones",
                "Naming an emotion ('I feel anxious') reduces its intensity — this is called 'affect labeling'",
            ],
            "duration": "5 minutes",
            "benefits": ["Improves emotional awareness", "Reduces emotional overwhelm", "Enhances communication about feelings"],
        },
        "target_personas": ["manomitra", "manospark", "manoveil_core"],
        "target_categories": ["minimal", "mild", "moderate"],
        "duration_minutes": 5,
    },
    {
        "title": "Stress and the Body",
        "description": "Understanding how chronic stress affects physical health",
        "intervention_type": "psychoeducation",
        "content": {
            "description": "Chronic stress isn't just mental — it changes your body. Understanding this connection motivates stress management.",
            "steps": [
                "Acute stress triggers cortisol and adrenaline — useful in short bursts",
                "Chronic stress keeps cortisol elevated, which weakens immunity and digestion",
                "Physical signs of chronic stress: headaches, muscle tension, fatigue, stomach issues",
                "The mind-body connection works both ways: relaxing the body calms the mind",
                "Three quick body-based interventions: deep breathing, progressive muscle relaxation, light exercise",
            ],
            "duration": "5 minutes reading",
            "benefits": ["Connects physical and mental symptoms", "Motivates stress management", "Provides actionable body-based tools"],
        },
        "target_personas": ["manoveil_core", "manobalance", "manosaathi"],
        "target_categories": ["moderate", "moderately_severe"],
        "duration_minutes": 5,
    },
]


async def seed():
    async with async_session() as session:
        for data in INTERVENTIONS:
            intervention = Intervention(**data)
            session.add(intervention)
        await session.commit()
        print(f"Seeded {len(INTERVENTIONS)} interventions.")


if __name__ == "__main__":
    asyncio.run(seed())
