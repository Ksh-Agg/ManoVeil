"""
Seed test users (one per age group + therapist + admin).
Usage: python -m scripts.seed_data
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.session import async_session
from app.models.user import User, AgeGroup, UserRole, Persona, AGE_TO_PERSONA
from app.core.security import hash_password

TEST_USERS = [
    {
        "email": "child@manoveil.test",
        "full_name": "Test Child",
        "age_group": AgeGroup.CHILDREN_5_12,
        "role": UserRole.USER,
    },
    {
        "email": "teen@manoveil.test",
        "full_name": "Test Teen",
        "age_group": AgeGroup.TEENAGERS_13_17,
        "role": UserRole.USER,
    },
    {
        "email": "college@manoveil.test",
        "full_name": "Test College Student",
        "age_group": AgeGroup.COLLEGE_18_24,
        "role": UserRole.USER,
    },
    {
        "email": "adult@manoveil.test",
        "full_name": "Test Adult",
        "age_group": AgeGroup.ADULTS_25_59,
        "role": UserRole.USER,
    },
    {
        "email": "elder@manoveil.test",
        "full_name": "Test Senior",
        "age_group": AgeGroup.ELDERLY_60_PLUS,
        "role": UserRole.USER,
    },
    {
        "email": "patient@manoveil.test",
        "full_name": "Test Patient",
        "age_group": AgeGroup.ADULTS_25_59,
        "role": UserRole.PATIENT,
    },
    {
        "email": "therapist@manoveil.test",
        "full_name": "Dr. Test Therapist",
        "age_group": AgeGroup.ADULTS_25_59,
        "role": UserRole.THERAPIST,
    },
    {
        "email": "admin@manoveil.test",
        "full_name": "Test Admin",
        "age_group": AgeGroup.ADULTS_25_59,
        "role": UserRole.ADMIN,
    },
]

DEFAULT_PASSWORD = "Test1234!"


async def seed():
    async with async_session() as session:
        hashed = hash_password(DEFAULT_PASSWORD)
        for data in TEST_USERS:
            persona = (
                Persona.MANOCONNECT
                if data["role"] == UserRole.THERAPIST
                else AGE_TO_PERSONA[data["age_group"]]
            )
            user = User(
                email=data["email"],
                hashed_password=hashed,
                full_name=data["full_name"],
                age_group=data["age_group"],
                role=data["role"],
                persona=persona,
            )
            session.add(user)

        await session.commit()
        print(f"Seeded {len(TEST_USERS)} test users with password: {DEFAULT_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
