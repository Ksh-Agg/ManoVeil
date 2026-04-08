from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class GradientCommitRead(BaseModel):
    id: UUID
    round_id: UUID
    institution_pseudo_id: str
    gradient_hash: str
    dp_epsilon_used: float
    zk_proof_valid: bool
    fabric_tx_id: str | None
    fabric_block_number: int | None
    ipfs_gradient_hash: str | None
    local_accuracy: float | None
    local_samples_count: int | None
    submitted_at: datetime
    verified_at: datetime | None
    model_config = {"from_attributes": True}


class FederatedRoundRead(BaseModel):
    id: UUID
    round_number: int
    participating_nodes: int
    global_model_version: str
    aggregation_method: str
    global_accuracy: float | None
    global_loss: float | None
    ipfs_model_hash: str | None
    started_at: datetime
    completed_at: datetime | None
    model_config = {"from_attributes": True}


class GradientSubmission(BaseModel):
    institution_pseudo_id: str
    gradient_data: str  # base64-encoded encrypted gradient
    local_accuracy: float
    local_loss: float
    local_samples_count: int
    dp_epsilon_used: float


class BAFLStatus(BaseModel):
    current_round: int
    total_commits: int
    active_nodes: int
    global_model_version: str
    last_aggregation: datetime | None
    blockchain_connected: bool
    ipfs_connected: bool
