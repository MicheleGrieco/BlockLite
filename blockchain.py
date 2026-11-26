"""
Blockchain management - the core chain data structure and operations.
"""

import json
import os
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from block import Block
from exceptions import (
    BlockchainError,
    ChainLoadError,
    InvalidBlockError,
    InvalidProofOfWorkError,
    InvalidTransactionError,
)
from transactions import State, Transaction, TransactionManager

DEFAULT_DIFFICULTY = 2
MAX_DIFFICULTY = 64  # a SHA-256 hex digest has 64 characters
MAX_FUTURE_DRIFT_SECONDS = 2 * 60 * 60  # same tolerance Bitcoin uses
SERIALIZATION_VERSION = 1


@dataclass
class Blockchain:
    """
    A simple account-based blockchain with proof-of-work.

    The blockchain maintains:
        - A list of blocks, starting with the genesis block
        - The current state (account balances)
        - A pool of pending (validated, not yet mined) transactions
        - A transaction manager for validation

    Rules enforced on every block:
        1. Hash must match contents and satisfy the chain difficulty
        2. Block numbers must be sequential and parent hashes must link
        3. Timestamps must not go backwards nor be too far in the future
        4. Genesis must allocate non-negative balances; all other
           transactions must be well-formed, zero-sum and not overdraw
    """

    chain: list[Block] = field(default_factory=list)
    state: State = field(default_factory=dict)
    tx_manager: TransactionManager = field(default_factory=TransactionManager)
    difficulty: int = DEFAULT_DIFFICULTY
    pending_transactions: list[Transaction] = field(default_factory=list)

    def __post_init__(self) -> None:
        if (
            not isinstance(self.difficulty, int)
            or isinstance(self.difficulty, bool)
            or not 0 <= self.difficulty <= MAX_DIFFICULTY
        ):
            raise ValueError(f"difficulty must be an int in [0, {MAX_DIFFICULTY}]")

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def height(self) -> int:
        """Return the number of blocks in the chain."""
        return len(self.chain)

    @property
    def latest_block(self) -> Optional[Block]:
        """Return the most recent block, or None if chain is empty."""
        return self.chain[-1] if self.chain else None

    @property
    def pending_state(self) -> State:
        """State obtained by applying all pending transactions to the current state."""
        state = self.state.copy()
        for txn in self.pending_transactions:
            state = TransactionManager.apply_transaction(txn, state)
        return state

    # ------------------------------------------------------------------ #
    # Block creation
    # ------------------------------------------------------------------ #

    def create_genesis_block(self, initial_balances: State) -> Block:
        """
        Create, mine and add the genesis (first) block.

        The genesis block is special: it creates tokens from nothing
        to establish initial account balances.

        Raises:
            InvalidBlockError: If genesis block already exists.
            MalformedTransactionError: If balances are malformed or negative.
        """
        if self.chain:
            raise InvalidBlockError("Genesis block already exists.")

        self.tx_manager.validate_initial_balances(initial_balances)
        block = Block.mine(
            block_number=0,
            transactions=[initial_balances],
            parent_hash=None,
            difficulty=self.difficulty,
        )
        self.add_block(block)
        return block

    def create_block(self, transactions: list[Transaction]) -> Block:
        """
        Mine a new block on top of the current tip.

        Note: This creates but does NOT add the block to the chain.
        Use add_block() to add it after creation.

        Raises:
            InvalidBlockError: If no genesis block exists.
        """
        parent = self.latest_block
        if parent is None:
            raise InvalidBlockError("Cannot create block: no genesis block exists.")

        return Block.mine(
            block_number=parent.block_number + 1,
            transactions=transactions,
            parent_hash=parent.hash,
            difficulty=self.difficulty,
            # Guarantee monotonic timestamps even if the system clock jumps back
            timestamp=max(time.time(), parent.timestamp),
        )

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #

    def _check_block(self, block: Block, parent: Optional[Block], state: State) -> State:
        """
        Validate `block` as the child of `parent` starting from `state`.

        Pure with respect to the chain: it never reads or mutates self.chain,
        so it can be reused to validate any sequence of blocks.

        Returns:
            The new state after applying all transactions.
        """
        if not isinstance(block, Block):
            raise InvalidBlockError(f"Expected Block, got {type(block).__name__}")

        if not block.verify_hash():
            raise InvalidBlockError(f"Block {block.block_number} hash verification failed")

        if block.difficulty != self.difficulty:
            raise InvalidProofOfWorkError(
                f"Block {block.block_number} declares difficulty {block.difficulty}, "
                f"chain requires {self.difficulty}"
            )
        if not block.has_valid_pow:
            raise InvalidProofOfWorkError(
                f"Block {block.block_number} hash does not meet difficulty {self.difficulty}"
            )

        if not isinstance(block.timestamp, (int, float)) or isinstance(block.timestamp, bool):
            raise InvalidBlockError(f"Block {block.block_number} has an invalid timestamp")
        if block.timestamp > time.time() + MAX_FUTURE_DRIFT_SECONDS:
            raise InvalidBlockError(f"Block {block.block_number} timestamp is too far in the future")

        if parent is None:
            return self._check_genesis(block, state)

        if block.block_number != parent.block_number + 1:
            raise InvalidBlockError(
                f"Invalid block number: expected {parent.block_number + 1}, "
                f"got {block.block_number}"
            )
        if block.parent_hash != parent.hash:
            raise InvalidBlockError(f"Invalid parent hash in block {block.block_number}")
        if block.timestamp < parent.timestamp:
            raise InvalidBlockError(
                f"Block {block.block_number} timestamp is earlier than its parent"
            )

        new_state = state.copy()
        for i, txn in enumerate(block.transactions):
            try:
                self.tx_manager.validate_transaction(txn, new_state)
            except InvalidTransactionError as e:
                # Re-raise the same subclass (e.g. InsufficientFundsError) with context
                raise type(e)(
                    f"Invalid transaction {i} in block {block.block_number}: {e}"
                ) from e
            new_state = TransactionManager.apply_transaction(txn, new_state)
        return new_state

    def _check_genesis(self, block: Block, state: State) -> State:
        """Genesis-specific rules: number 0, no parent, one non-negative allocation."""
        if block.block_number != 0:
            raise InvalidBlockError("First block must be genesis (number 0)")
        if block.parent_hash is not None:
            raise InvalidBlockError("Genesis block must have no parent hash")
        if len(block.transactions) != 1:
            raise InvalidBlockError("Genesis block must contain exactly one allocation")

        allocation = block.transactions[0]
        self.tx_manager.validate_initial_balances(allocation)
        return TransactionManager.apply_transaction(allocation, state)

    def validate_block(self, block: Block, expected_state: Optional[State] = None) -> State:
        """
        Validate a block as the next block of this chain.

        Args:
            block: The block to validate.
            expected_state: The state before this block (defaults to current state).

        Returns:
            The new state after applying all transactions.

        Raises:
            InvalidBlockError: If block structure is invalid.
            InvalidTransactionError: If any transaction is invalid.
        """
        state = self.state if expected_state is None else expected_state
        return self._check_block(block, self.latest_block, state)

    def validate_chain(self) -> State:
        """
        Re-validate the entire chain from genesis, without mutating it.

        Returns:
            The final state if the chain is valid.

        Raises:
            InvalidBlockError / InvalidTransactionError: If any block is invalid.
            BlockchainError: If the stored state does not match the replayed chain.
        """
        state: State = {}
        parent: Optional[Block] = None
        for block in self.chain:
            state = self._check_block(block, parent, state)
            parent = block

        if state != self.state:
            raise BlockchainError("Stored state does not match the state replayed from the chain")
        return state

    # ------------------------------------------------------------------ #
    # Chain mutation
    # ------------------------------------------------------------------ #

    def add_block(self, block: Block) -> None:
        """
        Validate and add a block to the chain.

        Pending transactions that are no longer valid on the new state are dropped.

        Raises:
            InvalidBlockError: If block is invalid.
            InvalidTransactionError: If any transaction is invalid.
        """
        new_state = self.validate_block(block)
        self.chain.append(block)
        self.state = new_state
        self._revalidate_pending()

    def mine_block(self, transactions: list[Transaction]) -> Block:
        """
        Filter, mine and add a new block with the given transactions.

        Invalid transactions are filtered out automatically, in order.

        Returns:
            The newly added block.

        Raises:
            InvalidBlockError: If no transaction is valid.
        """
        valid_txns: list[Transaction] = []
        temp_state = self.state.copy()

        for txn in transactions:
            if self.tx_manager.is_valid(txn, temp_state):
                valid_txns.append(txn)
                temp_state = TransactionManager.apply_transaction(txn, temp_state)

        if not valid_txns:
            raise InvalidBlockError("No valid transactions to include in block")

        block = self.create_block(valid_txns)
        self.add_block(block)
        return block

    # ------------------------------------------------------------------ #
    # Mempool
    # ------------------------------------------------------------------ #

    def submit_transaction(self, transaction: Transaction) -> None:
        """
        Validate a transaction against the pending state and queue it for mining.

        Raises:
            InvalidTransactionError: If the transaction is invalid given the
                current state plus the already-pending transactions.
        """
        self.tx_manager.validate_transaction(transaction, self.pending_state)
        self.pending_transactions.append(dict(transaction))

    def mine_pending(self) -> Block:
        """
        Mine a block with all pending transactions and clear the pool.

        Raises:
            InvalidBlockError: If there are no pending transactions.
        """
        if not self.pending_transactions:
            raise InvalidBlockError("No pending transactions to mine")
        txns = list(self.pending_transactions)
        block = self.mine_block(txns)
        self.pending_transactions.clear()
        return block

    def _revalidate_pending(self) -> None:
        """Drop pending transactions that are no longer valid on the current state."""
        still_valid: list[Transaction] = []
        state = self.state.copy()
        for txn in self.pending_transactions:
            if self.tx_manager.is_valid(txn, state):
                still_valid.append(txn)
                state = TransactionManager.apply_transaction(txn, state)
        self.pending_transactions = still_valid

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #

    def get_balance(self, account: str) -> int:
        """Get the current (confirmed) balance of an account."""
        return self.state.get(account, 0)

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        """Serialize the blockchain to a JSON-compatible dict."""
        return {
            "version": SERIALIZATION_VERSION,
            "difficulty": self.difficulty,
            "blocks": [block.to_dict() for block in self.chain],
        }

    def to_json(self) -> str:
        """Serialize the blockchain to JSON."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str, tx_manager: Optional[TransactionManager] = None) -> "Blockchain":
        """
        Load a blockchain from JSON, fully re-validating every block.

        Raises:
            ChainLoadError: If the JSON is malformed or has an unsupported format.
            InvalidBlockError / InvalidTransactionError: If any block is invalid.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ChainLoadError(f"Invalid JSON: {e}") from e

        if not isinstance(data, dict) or not isinstance(data.get("blocks"), list):
            raise ChainLoadError("Expected an object with a 'blocks' list")
        if data.get("version") != SERIALIZATION_VERSION:
            raise ChainLoadError(f"Unsupported format version: {data.get('version')!r}")

        try:
            blockchain = cls(
                difficulty=data.get("difficulty", DEFAULT_DIFFICULTY),
                tx_manager=tx_manager or TransactionManager(),
            )
        except ValueError as e:
            raise ChainLoadError(str(e)) from e

        for block_data in data["blocks"]:
            blockchain.add_block(Block.from_dict(block_data))
        return blockchain

    def save(self, path: str | Path) -> None:
        """
        Atomically write the chain to `path`.

        Writes to a temporary file in the same directory and renames it,
        so a crash mid-write never leaves a truncated chain file.
        """
        path = Path(path)
        fd, tmp_name = tempfile.mkstemp(dir=path.parent or ".", prefix=f".{path.name}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(self.to_json())
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_name, path)
        except BaseException:
            Path(tmp_name).unlink(missing_ok=True)
            raise

    @classmethod
    def load(cls, path: str | Path, tx_manager: Optional[TransactionManager] = None) -> "Blockchain":
        """Load and re-validate a chain previously written with save()."""
        try:
            text = Path(path).read_text(encoding="utf-8")
        except OSError as e:
            raise ChainLoadError(f"Cannot read chain file {path}: {e}") from e
        return cls.from_json(text, tx_manager=tx_manager)

    def __repr__(self) -> str:
        return (
            f"Blockchain(height={self.height}, difficulty={self.difficulty}, "
            f"pending={len(self.pending_transactions)}, state={self.state})"
        )
