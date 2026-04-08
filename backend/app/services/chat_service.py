from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from app.models.chat import ChatSession, ChatMessage
from app.models.user import User, Persona
from app.schemas.chat import ChatResponse, MessageRead
from app.services.crisis_service import check_crisis, trigger_sos, get_crisis_resources
from app.core.constants import PERSONA_NAMES, PERSONA_DESCRIPTIONS, CRISIS_HOTLINES

_analyzer = SentimentIntensityAnalyzer()

PERSONA_PROMPTS = {
    Persona.MANOMITRA: (
        "You are ManoMitra, a kind and gentle friend for children aged 5-12. "
        "Use simple words, stories, and encouragement. Ask about their day, friends, and feelings "
        "using fun and warm language. Never be clinical."
    ),
    Persona.MANOSPARK: (
        "You are ManoSpark, a supportive companion for teenagers. "
        "Be relatable, validate their feelings, and understand their world — school pressure, "
        "friendships, identity. Use casual but caring language."
    ),
    Persona.MANOVEIL_CORE: (
        "You are ManoVeil Core, a peer-like mental wellness companion for college students. "
        "Understand academic stress, exam anxiety, social isolation, and career worries. "
        "Offer CBT-based coping strategies and breathing exercises."
    ),
    Persona.MANOBALANCE: (
        "You are ManoBalance, a thoughtful companion for working adults. "
        "Address workplace burnout, relationship stress, financial pressure, and work-life balance. "
        "Offer practical, evidence-based strategies."
    ),
    Persona.MANOSAATHI: (
        "You are ManoSaathi, a warm and patient companion for seniors. "
        "Address loneliness, health concerns, loss, and cognitive wellness. "
        "Speak slowly and clearly. Be respectful and encouraging."
    ),
    Persona.MANOCONNECT: (
        "You are ManoConnect, a clinical AI assistant for therapists. "
        "Provide structured, evidence-based observations. Help with patient analysis."
    ),
}

# Response templates based on sentiment and persona
RESPONSE_TEMPLATES = {
    "negative_high": [
        "I can hear that you're going through something really difficult right now. You're not alone in this. Can you tell me more about what's been weighing on you?",
        "That sounds really tough, and your feelings are completely valid. Let's take this step by step together. What feels most overwhelming right now?",
        "I'm here for you. When things feel this heavy, sometimes it helps to focus on just one small thing. Would you like to try a quick breathing exercise with me?",
    ],
    "negative_mild": [
        "It sounds like things have been a bit tough lately. That's okay — we all have days like this. What's been on your mind?",
        "I appreciate you sharing that with me. Let's explore what might help you feel a little better today.",
        "Thank you for being open about how you feel. Would you like to talk more about it, or try a quick wellness activity?",
    ],
    "neutral": [
        "Thanks for checking in! How has your day been going so far?",
        "I'm glad you're here. Is there anything specific you'd like to talk about today, or shall we do a quick wellness check?",
        "Welcome back! Would you like to share how you've been feeling, or try one of our mindfulness exercises?",
    ],
    "positive": [
        "That's wonderful to hear! It's great that you're feeling good. What's been going well for you?",
        "I'm so glad you're in a good space! Let's keep that positive momentum going. What's been making you happy lately?",
        "That's amazing! Keep celebrating those good moments. Is there anything you'd like to reflect on or build upon?",
    ],
}

CBT_TECHNIQUES = [
    "Let's try a thought record: What was the situation? What thoughts came up? How did those thoughts make you feel? Now, can you think of an alternative, more balanced thought?",
    "Here's a grounding exercise: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste. This can help when feelings get overwhelming.",
    "Let's practice cognitive reframing: You mentioned a difficult thought. What evidence supports it? What evidence goes against it? What would you tell a friend in this situation?",
    "Try this breathing technique: Breathe in for 4 counts, hold for 4 counts, breathe out for 6 counts. Repeat 3 times. How do you feel now?",
]

import random


def analyze_sentiment(text: str) -> float:
    scores = _analyzer.polarity_scores(text)
    return scores["compound"]  # -1 to 1


def _select_response(sentiment: float, persona: Persona) -> str:
    if sentiment <= -0.5:
        pool = RESPONSE_TEMPLATES["negative_high"]
    elif sentiment <= -0.1:
        pool = RESPONSE_TEMPLATES["negative_mild"]
    elif sentiment <= 0.3:
        pool = RESPONSE_TEMPLATES["neutral"]
    else:
        pool = RESPONSE_TEMPLATES["positive"]

    response = random.choice(pool)

    # Add CBT technique for negative sentiment
    if sentiment <= -0.1:
        response += "\n\n" + random.choice(CBT_TECHNIQUES)

    return response


async def create_session(db: AsyncSession, user: User) -> ChatSession:
    session = ChatSession(user_id=user.id, persona=user.persona)
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


async def process_message(db: AsyncSession, session_id, content: str, persona: Persona) -> ChatResponse:
    sentiment = analyze_sentiment(content)
    is_crisis, severity = check_crisis(content, score=None)

    # Store user message
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=content,
        sentiment_score=sentiment,
        crisis_flag=is_crisis,
    )
    db.add(user_msg)

    # Generate response
    if is_crisis:
        hotlines = "\n".join([f"- {h['name']}: {h['number']} ({h['hours']})" for h in CRISIS_HOTLINES[:3]])
        bot_content = (
            "I'm really concerned about what you're sharing, and I want you to know that help is available right now. "
            "You don't have to face this alone.\n\n"
            f"Please reach out to one of these helplines:\n{hotlines}\n\n"
            "If you're in immediate danger, please call emergency services (112) or go to your nearest emergency room. "
            "Would you like me to help you connect with someone who can support you right now?"
        )
    else:
        bot_content = _select_response(sentiment, persona)

    bot_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=bot_content,
        sentiment_score=None,
        crisis_flag=False,
    )
    db.add(bot_msg)
    await db.flush()
    await db.refresh(user_msg)
    await db.refresh(bot_msg)

    crisis_resources = None
    if is_crisis:
        # Also trigger SOS event
        result = await db.execute(
            select(ChatSession.user_id).where(ChatSession.id == session_id)
        )
        uid = result.scalar_one()
        await trigger_sos(db, uid, source="chat_keyword", text=content[:200])
        crisis_resources = [h for h in CRISIS_HOTLINES]

    return ChatResponse(
        user_message=MessageRead.model_validate(user_msg),
        bot_message=MessageRead.model_validate(bot_msg),
        crisis_detected=is_crisis,
        crisis_resources=crisis_resources,
    )


async def get_session_messages(db: AsyncSession, session_id) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    return list(result.scalars().all())


async def get_user_sessions(db: AsyncSession, user_id) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(desc(ChatSession.started_at))
    )
    return list(result.scalars().all())
