#type: ignore

"""
Blockchain management - the core chain data structure and operations.
"""

import json
from typing import Optional

from block import Block
from transactions import TransactionManager
from exceptions import InvalidBlockError, InvalidTransactionError

class Blockchain:
    """
    A simple blockchain implementation.
    
    The blockchain maintains:
        - A list of blocks, starting with the genesis block
        - The current state (account balances)
        - A transaction manager for validation
    
    Rules enforced:
        1. Each block must reference the previous block's hash
        2. Block numbers must be sequential
        3. All transactions must be valid
        4. Block hashes must match their contents
    """
    
    def __init__(self) -> None:
        """Initialize an empty blockchain."""
        self.chain: list[Block] = []
        self.state: dict[str, int] = {}
        self.tx_manager = TransactionManager()

    @property
    def height(self) -> int:
        """Return the number of blocks in the chain."""
        return len(self.chain)
    
    @property
    def latest_block(self) -> Optional[Block]:
        """Return the most recent block, or None if chain is empty."""
        
    def create_genesis_block(self, initial_balances: dict[str, int]) -> Block:
        """
        Create and add the genesis (first) block.
        
        The genesis block is special: it creates tokens from nothing
        to establish initial account balances.
        
        Args:
            initial_balances: Starting balances for accounts.
        
        Returns:
            The created genesis block.
        
        Raises:
            InvalidBlockError: If genesis block already exists.
        """
        
        if self.chain:
            raise InvalidBlockError("Genesis block already exists.")
        
        # Genesis transaction doesn't need to sum to zero
        genesis_txn = initial_balances.copy()
        
        block = Block(
            block_number=0,
            transactions=[genesis_txn],
            parent_hash=None
        )
        
        self.chain.append(block)
        self.state = initial_balances.copy()
        
        return block
    
    def create_block(self, transactions: list[dict[str, int]]) -> Block:
        """
        Create a new block with the given transactions.
        
        Note: This creates but does NOT add the block to the chain.
        Use add_block() to add it after creation.
        
        Args:
            transactions: List of transactions to include.
            
        Returns:
            The new block.
            
        Raises:
            InvalidBlockError: If no genesis block exists.
        """
        
        if not self.chain:
            raise InvalidBlockError("Cannot create block: no genesis block exists.")
        
        parent = self.latest_block
        
        return Block(
            block_number=parent.block_number+1,
            transactions=transactions,
            parent_hash=parent.hash
        )
        
    def validate_block(self, block: Block, expected_state: dict[str, int]) -> dict[str, int]:
        """
        Validate a block and return the resulting state.
        
        Args:
            block: The block to validate.
            expected_state: The state before this block's transactions.
        
        Returns:
            The new state after applying all transactions.
        
        Raises:
            InvalidBlockError: If block structure is invalid.
            InvalidTransactionError: If any transaction is invalid.
        """
        # Verify hash integrity
        if not block.verify_hash():
            raise InvalidBlockError(f"Block {block.block_number} hash verification failed")
        
        # Check block links to chain correctly
        if self.chain:
            parent = self.latest_block
            
            if block.block_number != parent.block_number + 1:
                raise InvalidBlockError(
                    f"Invalid block number: expected {parent.block_number + 1}, "
                    f"got {block.block_number}"
                )
            
            if block.parent_hash != parent.hash:
                raise InvalidBlockError(
                    f"Invalid parent hash in block {block.block_number}"
                )
        else:
            # This should be genesis block
            if block.block_number != 0:
                raise InvalidBlockError("First block must be genesis (number 0)")
            if block.parent_hash is not None:
                raise InvalidBlockError("Genesis block must have no parent hash")
        
        # Validate and apply each transaction
        new_state = expected_state.copy()
        
        # Genesis block gets special treatment (creates tokens)
        if block.block_number == 0:
            for txn in block.transactions:
                new_state = TransactionManager.apply_transaction(txn, new_state)
        else:
            for i, txn in enumerate(block.transactions):
                try:
                    self.tx_manager.validate_transaction(txn, new_state)
                    new_state = TransactionManager.apply_transaction(txn, new_state)
                except Exception as e:
                    raise InvalidTransactionError(
                        f"Invalid transaction {i} in block {block.block_number}: {e}"
                    )
        
        return new_state
    
    def add_block(self, block: Block) -> None:
        """
        Validate and add a block to the chain.
        
        Args:
            block: The block to add.
        
        Raises:
            InvalidBlockError: If block is invalid.
            InvalidTransactionError: If any transaction is invalid.
        """
        new_state = self.validate_block(block, self.state)
        self.chain.append(block)
        self.state = new_state
    
    def mine_block(self, transactions: list[dict[str, int]]) -> Block:
        """
        Create, validate, and add a new block with the given transactions.
        
        This is a convenience method that combines create_block and add_block.
        Invalid transactions are filtered out automatically.
        
        Args:
            transactions: List of transactions to include.
        
        Returns:
            The newly added block.
        """
        # Filter to only valid transactions
        valid_txns = []
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
    
    def validate_chain(self) -> dict[str, int]:
        """
        Validate the entire chain from genesis.
        
        Returns:
            The final state if chain is valid.
        
        Raises:
            InvalidBlockError: If any block is invalid.
        """
        if not self.chain:
            return {}
        
        # Temporarily reset and rebuild
        temp_chain = self.chain.copy()
        self.chain = []
        state = {}
        
        try:
            for block in temp_chain:
                state = self.validate_block(block, state)
                self.chain.append(block)
            return state
        except Exception:
            # Restore original chain on failure
            self.chain = temp_chain
            raise
        
     def get_balance(self, account: str) -> int:
        """Get the current balance of an account."""
        return self.state.get(account, 0)
    
    def to_json(self) -> str:
        """Serialize the blockchain to JSON."""
        return json.dumps([block.to_dict() for block in self.chain], indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Blockchain":
        """
        Load a blockchain from JSON.
        
        Args:
            json_str: JSON string representing the chain.
        
        Returns:
            A new Blockchain instance with the loaded data.
        """
        blockchain = cls()
        blocks_data = json.loads(json_str)
        
        for block_data in blocks_data:
            block = Block.from_dict(block_data)
            blockchain.add_block(block)
        
        return blockchain
    
    def __repr__(self) -> str:
        return f"Blockchain(height={self.height}, state={self.state})"