from app.models.user import AgeGroup, Persona
from app.models.assessment import AssessmentType

# ─── Score Thresholds ───
SCORE_TIERS = {
    "minimal": (0.0, 2.0),
    "mild": (2.1, 4.5),
    "moderate": (4.6, 7.0),
    "moderately_severe": (7.1, 8.9),
    "severe": (9.0, 10.0),
}

TIER_BOUNDARIES = [2.0, 4.5, 7.0, 8.9]
YELLOW_FLAG_THRESHOLD = 0.5

FUSION_WEIGHTS = {"psychometric": 0.6, "nlp": 0.4}

# ─── Assessment Eligibility by Age Group ───
ASSESSMENT_ELIGIBILITY: dict[AgeGroup, list[AssessmentType]] = {
    AgeGroup.CHILDREN_5_12: [AssessmentType.CDI_2, AssessmentType.SCARED],
    AgeGroup.TEENAGERS_13_17: [AssessmentType.PHQ_9, AssessmentType.GAD_7, AssessmentType.SCARED],
    AgeGroup.COLLEGE_18_24: [AssessmentType.DASS_21, AssessmentType.GAD_7, AssessmentType.PHQ_9],
    AgeGroup.ADULTS_25_59: [AssessmentType.DASS_21, AssessmentType.GAD_7, AssessmentType.PHQ_9],
    AgeGroup.ELDERLY_60_PLUS: [AssessmentType.GDS_15, AssessmentType.GAD_7, AssessmentType.PHQ_9],
}

# ─── Assessment Normalization (raw_max → 0-10) ───
ASSESSMENT_MAX_SCORES: dict[AssessmentType, float] = {
    AssessmentType.DASS_21: 42.0,
    AssessmentType.GAD_7: 21.0,
    AssessmentType.PHQ_9: 27.0,
    AssessmentType.CDI_2: 54.0,
    AssessmentType.SCARED: 82.0,
    AssessmentType.GDS_15: 15.0,
}

# ─── Crisis Hotlines (India-focused) ───
CRISIS_HOTLINES = [
    {"name": "iCall", "number": "9152987821", "description": "Psychosocial helpline by TISS Mumbai", "hours": "Mon-Sat 8am-10pm"},
    {"name": "Vandrevala Foundation", "number": "1860-2662-345", "description": "24/7 mental health support", "hours": "24/7"},
    {"name": "AASRA", "number": "9820466726", "description": "Crisis intervention center", "hours": "24/7"},
    {"name": "Snehi", "number": "044-24640050", "description": "Emotional support helpline", "hours": "24/7"},
    {"name": "NIMHANS", "number": "080-46110007", "description": "National mental health institute helpline", "hours": "Mon-Sat 9am-5pm"},
    {"name": "Kiran Mental Health", "number": "1800-599-0019", "description": "Government toll-free helpline", "hours": "24/7"},
]

# ─── Crisis Keywords ───
CRISIS_KEYWORDS = [
    "kill myself", "suicide", "suicidal", "end my life", "want to die",
    "no reason to live", "better off dead", "self harm", "self-harm",
    "cut myself", "cutting", "hurt myself", "overdose", "jump off",
    "hang myself", "not worth living", "can't go on", "ending it",
    "goodbye forever", "final goodbye", "last message",
]

# ─── Persona Display Names ───
PERSONA_NAMES = {
    Persona.MANOMITRA: "ManoMitra",
    Persona.MANOSPARK: "ManoSpark",
    Persona.MANOVEIL_CORE: "ManoVeil Core",
    Persona.MANOBALANCE: "ManoBalance",
    Persona.MANOSAATHI: "ManoSaathi",
    Persona.MANOCONNECT: "ManoConnect",
}

# ─── Persona Descriptions ───
PERSONA_DESCRIPTIONS = {
    Persona.MANOMITRA: "A gentle, playful companion for children — uses simple language, stories, and emoji-based interactions",
    Persona.MANOSPARK: "A relatable friend for teens — informal, validates feelings, supports identity exploration",
    Persona.MANOVEIL_CORE: "A supportive peer for college students — understands academic pressure, social stress, career anxiety",
    Persona.MANOBALANCE: "A thoughtful companion for adults — workplace burnout, relationship stress, financial pressure",
    Persona.MANOSAATHI: "A warm, patient companion for seniors — addresses loneliness, health concerns, cognitive wellness",
    Persona.MANOCONNECT: "A clinical intelligence layer for therapists — structured, evidence-based, multi-patient management",
}
