import json
from utils import hash_me
from transactions import TransactionManager

class Blockchain:
    
    def __init__(self) -> None:
        """
        Initialize a new blockchain.
        """
        self.chain = []
        self.state = {}
    
    def make_block(self, transactions) -> dict:
        """
        Create a new block with the given transactions and append it to the blockchain.
        The block is created by hashing the transactions and the previous block's hash.

        Args:
            txns (list): list of transactions to include in the block
            chain (list): chain of blocks to which the new block will be appended

        Returns:
            block (dict): the new block created with its hash and contents
        """
        
        if not self.chain:
            parent_hash = None
            block_number = 0
        else:
            parent_block = self.chain[-1]
            parent_hash = parent_block['hash']
            block_number = parent_block['contents']['blockNumber'] + 1
        
        block_contents = {
            'blockNumber': block_number,
            'parentHash': parent_hash,
            'transactionsCount': len(transactions),
            'transactions': transactions
        }
        block_hash = hash_me(block_contents)
        return {'hash': block_hash, 'contents': block_contents}


    def check_block_hash(self, block) -> None:
        """
        Check if the hash of the block matches the hash in the block.

        Args:
            block (dict): The block to check.
        """

        # Raise an exception if the hash does not match the block contents
        expected_hash = hash_me(block['contents'])
        if block['hash'] != expected_hash:
            raise Exception(f"Hash does not match contents of block {block['contents']['blockNumber']}")

    def check_block_validity(self, block, parent, state) -> dict:
        """
        Check if a block is valid according to the rules defined.
        The block is valid if:
        - each of the transactions are valid updates to the system state
        - block hash is valid for the block contents
        - block number increments the parent block number by 1
        - accurately references the parent block's hash
        
        Args:
            block (dict): The block to check.
            parent (dict): The parent block.
            state (dict): The current state of the accounts.
        Returns:
            dict: The updated state if the block is valid, raises an exception otherwise.
        """
        
        parent_number = parent['contents']['blockNumber']
        parent_hash = parent['hash']
        block_number = block['contents']['blockNumber']
        
        # Check transaction validity; throw an error if an invalid transaction is found
        for transaction in block['contents']['txns']:
            if TransactionManager().is_valid_transaction(transaction):
                state = transaction.update_state(transaction, state)
            else:
                raise Exception(f"Invalid transaction in block {block_number}: {transaction}")
        
        # Check hash integrity; raise error if inaccurate
        self.check_block_hash(block)
        
        if block_number != parent_number + 1:
            raise Exception( f"Invalid block number: {block_number}")
        if block['contents']['parentHash'] != parent_hash:
            raise Exception(f"Parent hash invalid in block {block_number}")
        
        return state


    def check_chain(self) -> dict | bool:
        """
        Check if a chain of blocks is valid according to the rules defined.
        Work through the chain from the genesis block (which gets special treatment),
        checking that all transactions are internally valid,
        that the transactions do not cause an overdraft,
        and that the blocks are linked by their hashes.
        
        Args:
            chain (list): A list of blocks to check.
        
        Returns:
            state (dict): The final state of the accounts if the chain is valid, False otherwise.
            False: if chain is invalid.
        """
        if isinstance(self.chain, str):
            try:
                self.chain = json.loads(self.chain)
                assert isinstance(self.chain, list)
            except:
                return False
        elif not isinstance(self.chain, list):
            return False
        
        state = {}
        # Verify genesis block
        if self.chain:
            for transaction in self.chain[0]['contents']['txns']:
                state = update_state(transaction, state)
            self.check_block_hash(self.chain[0])
            parent = self.chain[0]
            
            # Check following blocks
            for block in self.chain[1:]:
                state = self.check_block_validity(block, parent, state)
                parent = block
                
        return state
    
    def add_block(self, block) -> bool:
        """
        Add a new block to the blockchain.
        Args:
            block (dict): Block to add.
        Returns: 
            bool: True if the block is added
        """
        if not self.chain: # First block
            for transaction in block['contents']['txns']:
                self.state = update_state(transaction, self.state)
            self.check_block_hash(block)
        else:
            # Verify validity with previous block
            self.state = self.check_block_validity(
                block,
                self.chain[-1],
                self.state.copy()
            )
            
        self.chain.append(block)
        return True
    
    def get_state(self) -> dict:
        """
        Return the current state of the blockchain.
        
        Returns:
            dict: current state
        """
        return self.state.copy()