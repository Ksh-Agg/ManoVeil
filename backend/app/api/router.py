from fastapi import APIRouter
from app.api import auth, users, assessments, trackers, chat, stress, crisis, interventions, therapist, admin, blockchain

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(trackers.router, prefix="/trackers", tags=["Trackers"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(stress.router, prefix="/stress", tags=["Stress Scores"])
api_router.include_router(crisis.router, prefix="/crisis", tags=["Crisis"])
api_router.include_router(interventions.router, prefix="/interventions", tags=["Interventions"])
api_router.include_router(therapist.router, prefix="/clinical", tags=["Clinical"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(blockchain.router, prefix="/blockchain", tags=["Blockchain / BAFL"])
