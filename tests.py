"""
Block creation, mining and (de)serialization.
"""

import copy
import time
from dataclasses import dataclass, field
from collections.abc import Sequence
from typing import Any, Optional

from exceptions import InvalidBlockError
from utils import hash_data, meets_difficulty

Transaction = dict[str, int]


@dataclass(frozen=True)
class Block:
    """
    Represents a single, immutable block in the blockchain.

    Attributes:
        block_number: Position in the chain (0 for genesis).
        transactions: Transactions in this block. Any sequence (e.g. a list)
            is accepted; it is stored as an immutable tuple of deep copies.
        parent_hash: Hash of the previous block (None for genesis).
        timestamp: Unix timestamp when the block was created.
        difficulty: Number of leading hex zeros required by proof-of-work.
        nonce: Value found by mining so that the hash meets the difficulty.
        hash: SHA-256 hash of the block contents (computed, never passed in).
    """

    block_number: int
    transactions: Sequence[Transaction]
    parent_hash: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    difficulty: int = 0
    nonce: int = 0
    hash: str = field(init=False)

    def __post_init__(self) -> None:
        # Deep-copy so that later changes to the caller's list/dicts
        # cannot silently invalidate the block hash.
        object.__setattr__(self, "transactions", tuple(copy.deepcopy(list(self.transactions))))
        object.__setattr__(self, "hash", self._calculate_hash())

    @staticmethod
    def _make_contents(
        block_number: int,
        parent_hash: Optional[str],
        timestamp: float,
        transactions: Any,
        difficulty: int,
        nonce: int,
    ) -> dict:
        """Build the hashed contents dict. Single source of truth for the block format."""
        return {
            "blockNumber": block_number,
            "parentHash": parent_hash,
            "timestamp": timestamp,
            "difficulty": difficulty,
            "nonce": nonce,
            "txnCount": len(transactions),
            "txns": list(transactions),
        }

    @property
    def contents(self) -> dict:
        """Get a copy of the block contents (everything except the hash)."""
        return copy.deepcopy(
            self._make_contents(
                self.block_number,
                self.parent_hash,
                self.timestamp,
                self.transactions,
                self.difficulty,
                self.nonce,
            )
        )

    def _calculate_hash(self) -> str:
        """Calculate the SHA-256 hash of the block contents."""
        return hash_data(
            self._make_contents(
                self.block_number,
                self.parent_hash,
                self.timestamp,
                self.transactions,
                self.difficulty,
                self.nonce,
            )
        )

    @classmethod
    def mine(
        cls,
        block_number: int,
        transactions: list[Transaction],
        parent_hash: Optional[str],
        difficulty: int,
        timestamp: Optional[float] = None,
    ) -> "Block":
        """
        Create a block whose hash satisfies the proof-of-work difficulty.

        Increments the nonce until the hash starts with `difficulty` hex zeros.
        Expected work is 16 ** difficulty hashes.

        Returns:
            A new Block with a valid nonce.
        """
        if timestamp is None:
            timestamp = time.time()
        txns = copy.deepcopy(list(transactions))
        contents = cls._make_contents(block_number, parent_hash, timestamp, txns, difficulty, 0)

        nonce = 0
        while not meets_difficulty(hash_data(contents), difficulty):
            nonce += 1
            contents["nonce"] = nonce

        return cls(
            block_number=block_number,
            transactions=txns,
            parent_hash=parent_hash,
            timestamp=timestamp,
            difficulty=difficulty,
            nonce=nonce,
        )

    @property
    def has_valid_pow(self) -> bool:
        """True if the block hash satisfies its own declared difficulty."""
        return meets_difficulty(self.hash, self.difficulty)

    def verify_hash(self) -> bool:
        """Verify that the block's hash matches its contents."""
        return self.hash == self._calculate_hash()

    def to_dict(self) -> dict:
        """Convert block to dictionary representation."""
        return {"hash": self.hash, "contents": self.contents}

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        """
        Create a Block instance from a dictionary.

        Args:
            data: Dictionary with 'hash' and 'contents' keys.

        Returns:
            A new Block instance.

        Raises:
            InvalidBlockError: If fields are missing/malformed or the hash doesn't match.
        """
        try:
            contents = data["contents"]
            expected_hash = data["hash"]
            block = cls(
                block_number=contents["blockNumber"],
                transactions=contents["txns"],
                parent_hash=contents["parentHash"],
                timestamp=contents["timestamp"],
                difficulty=contents["difficulty"],
                nonce=contents["nonce"],
            )
        except (KeyError, TypeError) as e:
            raise InvalidBlockError(f"Malformed block data: {e!r}") from e

        if contents.get("txnCount") != len(block.transactions):
            raise InvalidBlockError(
                f"txnCount mismatch: declared {contents.get('txnCount')}, "
                f"found {len(block.transactions)}"
            )
        if block.hash != expected_hash:
            raise InvalidBlockError(
                f"Block hash mismatch: expected {expected_hash}, got {block.hash}"
            )
        return block

    def __repr__(self) -> str:
        return (
            f"Block(number={self.block_number}, txns={len(self.transactions)}, "
            f"nonce={self.nonce}, hash={self.hash[:12]}...)"
        )