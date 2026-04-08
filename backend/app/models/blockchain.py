import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class FederatedRound(Base):
    """Tracks each round of federated learning aggregation."""
    __tablename__ = "federated_rounds"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    participating_nodes: Mapped[int] = mapped_column(Integer, nullable=False)
    global_model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregation_method: Mapped[str] = mapped_column(String(50), default="fedavg")
    global_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    global_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    ipfs_model_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GradientCommit(Base):
    """Records each institution's gradient contribution to a federated round,
    including blockchain transaction details and ZK-proof verification status."""
    __tablename__ = "gradient_commits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    institution_pseudo_id: Mapped[str] = mapped_column(String(255), nullable=False)
    gradient_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    encrypted_gradient_size: Mapped[int] = mapped_column(Integer, nullable=False)
    dp_epsilon_used: Mapped[float] = mapped_column(Float, nullable=False)
    dp_delta_used: Mapped[float] = mapped_column(Float, default=1e-5)
    zk_proof_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    zk_proof_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fabric_tx_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fabric_block_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ipfs_gradient_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    local_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    local_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    local_samples_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
