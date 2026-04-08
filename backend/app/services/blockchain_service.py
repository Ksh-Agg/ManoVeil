"""
BAFL (Blockchain-Anchored Federated Learning) Service — Phase 2 Placeholder

This module provides the service layer for federated learning gradient management,
blockchain integration, and IPFS metadata storage. In Phase 1, the blockchain and
IPFS interactions are simulated with local state. Phase 2 will connect to actual
Hyperledger Fabric peers and IPFS nodes.
"""

import hashlib
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.blockchain import GradientCommit, FederatedRound
from app.schemas.blockchain import GradientSubmission, BAFLStatus, GradientCommitRead, FederatedRoundRead


def _generate_zk_proof_hash(gradient_data: str, institution_id: str) -> str:
    """Simulate ZK-proof generation. Phase 2 will use actual ZK-SNARK/STARK proofs."""
    proof_input = f"{gradient_data}:{institution_id}:{datetime.now(timezone.utc).isoformat()}"
    return hashlib.sha256(proof_input.encode()).hexdigest()


def _compute_gradient_hash(gradient_data: str) -> str:
    return hashlib.sha256(gradient_data.encode()).hexdigest()


async def _mock_ipfs_store(data: str) -> str:
    """Phase 2: Replace with actual IPFS pinning via ipfshttpclient."""
    return f"Qm{hashlib.sha256(data.encode()).hexdigest()[:44]}"


async def _mock_fabric_submit(tx_data: dict) -> tuple[str, int]:
    """Phase 2: Replace with actual Hyperledger Fabric SDK transaction submission."""
    tx_id = f"fab_{uuid.uuid4().hex[:16]}"
    block_number = hash(tx_id) % 100000
    return tx_id, abs(block_number)


async def submit_gradient(db: AsyncSession, submission: GradientSubmission) -> GradientCommit:
    # Get or create current round
    current_round = await get_current_round(db)
    if not current_round:
        current_round = await start_new_round(db, "v1.0")

    gradient_hash = _compute_gradient_hash(submission.gradient_data)
    zk_proof_hash = _generate_zk_proof_hash(submission.gradient_data, submission.institution_pseudo_id)
    ipfs_hash = await _mock_ipfs_store(submission.gradient_data)
    fabric_tx_id, block_number = await _mock_fabric_submit({
        "gradient_hash": gradient_hash,
        "institution": submission.institution_pseudo_id,
        "zk_proof": zk_proof_hash,
        "round": current_round.round_number,
    })

    commit = GradientCommit(
        round_id=current_round.id,
        institution_pseudo_id=submission.institution_pseudo_id,
        gradient_hash=gradient_hash,
        encrypted_gradient_size=len(submission.gradient_data),
        dp_epsilon_used=submission.dp_epsilon_used,
        zk_proof_valid=True,
        zk_proof_hash=zk_proof_hash,
        fabric_tx_id=fabric_tx_id,
        fabric_block_number=block_number,
        ipfs_gradient_hash=ipfs_hash,
        local_accuracy=submission.local_accuracy,
        local_loss=submission.local_loss,
        local_samples_count=submission.local_samples_count,
        verified_at=datetime.now(timezone.utc),
    )
    db.add(commit)
    await db.flush()
    await db.refresh(commit)
    return commit


async def get_current_round(db: AsyncSession) -> FederatedRound | None:
    result = await db.execute(
        select(FederatedRound)
        .where(FederatedRound.completed_at.is_(None))
        .order_by(desc(FederatedRound.round_number))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def start_new_round(db: AsyncSession, model_version: str) -> FederatedRound:
    result = await db.execute(
        select(func.max(FederatedRound.round_number))
    )
    max_round = result.scalar() or 0

    fed_round = FederatedRound(
        round_number=max_round + 1,
        participating_nodes=0,
        global_model_version=model_version,
        aggregation_method="fedavg",
    )
    db.add(fed_round)
    await db.flush()
    await db.refresh(fed_round)
    return fed_round


async def complete_round(db: AsyncSession, round_id) -> FederatedRound | None:
    result = await db.execute(select(FederatedRound).where(FederatedRound.id == round_id))
    fed_round = result.scalar_one_or_none()
    if not fed_round:
        return None

    # Count participating nodes
    commit_count = await db.execute(
        select(func.count(GradientCommit.id))
        .where(GradientCommit.round_id == round_id)
    )
    fed_round.participating_nodes = commit_count.scalar() or 0
    fed_round.completed_at = datetime.now(timezone.utc)

    # Mock: compute global accuracy as avg of local accuracies
    acc_result = await db.execute(
        select(func.avg(GradientCommit.local_accuracy))
        .where(GradientCommit.round_id == round_id)
    )
    fed_round.global_accuracy = acc_result.scalar()

    # Store global model on IPFS (mock)
    fed_round.ipfs_model_hash = await _mock_ipfs_store(f"global_model_round_{fed_round.round_number}")

    await db.flush()
    await db.refresh(fed_round)
    return fed_round


async def get_bafl_status(db: AsyncSession) -> BAFLStatus:
    current = await get_current_round(db)
    total_commits = (await db.execute(select(func.count(GradientCommit.id)))).scalar() or 0

    # Count unique institutions
    active_nodes = (await db.execute(
        select(func.count(func.distinct(GradientCommit.institution_pseudo_id)))
    )).scalar() or 0

    last_completed = await db.execute(
        select(FederatedRound)
        .where(FederatedRound.completed_at.isnot(None))
        .order_by(desc(FederatedRound.completed_at)).limit(1)
    )
    last_round = last_completed.scalar_one_or_none()

    return BAFLStatus(
        current_round=current.round_number if current else 0,
        total_commits=total_commits,
        active_nodes=active_nodes,
        global_model_version=current.global_model_version if current else "none",
        last_aggregation=last_round.completed_at if last_round else None,
        blockchain_connected=True,  # Phase 2: actual health check
        ipfs_connected=True,  # Phase 2: actual health check
    )


async def get_round_commits(db: AsyncSession, round_id) -> list[GradientCommit]:
    result = await db.execute(
        select(GradientCommit)
        .where(GradientCommit.round_id == round_id)
        .order_by(GradientCommit.submitted_at)
    )
    return list(result.scalars().all())


async def get_all_rounds(db: AsyncSession) -> list[FederatedRound]:
    result = await db.execute(
        select(FederatedRound).order_by(desc(FederatedRound.round_number))
    )
    return list(result.scalars().all())
