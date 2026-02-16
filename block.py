"""
Block creation and validation for the blockchain.
"""
import time
from utils import hash_data
from dataclasses import dataclass, field
from typing import Optional
from exceptions import InvalidBlockError

@dataclass
class Block:
    """
    Represents a single block in the blockchain.
    
    Attributes:
        block_number: Position in the chain (0 for genesis).
        parent_hash: Hash of the previous block (None for genesis).
        timestamp: Unix timestamp when block was created.
        transactions: List of transactions in this block.
        hash: SHA-256 hash of the block contents.
    """
    
    block_number: int
    transactions: list[dict[str, int]]
    parent_hash: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    hash: str = field(init=False)
    
    def __post_init__(self) -> None:
        """Calculate hash after initialization."""
        self.hash = self._calculate_hash()
        
    @property
    def contents(self) -> dict:
        """Get the block contents (everything except the hash)"""
        return {
            "blockNumber": self.block_number,
            "parentHash": self.parent_hash,
            "timestamp": self.timestamp,
            "txnCount": len(self.transactions),
            "txns": self.transactions 
        }
        
    def _calculate_hash(self) -> str:
        """Calculate the SHA-256 hash of the block contents."""
        return hash_data(self.contents)
    
    def to_dict(self) -> dict:
        """Convert block to dictionary representation."""
        return {
            "hash": self.hash,
            "contents": self.contents 
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        """
        Create a Block instance from a dictionary.
        
        Args:
            data: Dictionary with 'hash' and 'contents' keys.
        
        Returns:
            A new Block instance.
        """
        contents = data["contents"]
        block = cls(
            block_number = contents["blockNumber"],
            transactions = contents["txns"],
            parent_hash = contents["parentHash"],
            timestamp = contents["timestamp"] 
        )
        
        # Verify the hash matches
        if block.hash != data["hash"]:
            raise InvalidBlockError(
                f"Block hash mismatch: expected {data['hash']}, got {block.hash}"
            )
            
        return block
    
    def verify_hash(self) -> bool:
        """Verify that the block's hash matches its contents."""
        return self.hash == self._calculate_hash()
    
    def __repr__(self) -> str:
        return f"Block(number={self.block_number}, txns={len(self.transactions)}, hash={self.hash[:8]}...)"