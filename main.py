"""
BlockLite - A minimal blockchain implementation in Python.

This script demonstrates the core blockchain functionality:
1. Creating a genesis block with initial balances
2. Generating and validating transactions
3. Mining new blocks
4. Verifying chain integrity
"""

from blockchain import Blockchain
from transactions import TransactionManager


for i in range(5):
    transactions = [
        
    ]
    
def main():
    blockchain = Blockchain()
    tx_manager = TransactionManager(seed=42) # Fixed seed for reproducibility
    initial_balances = {"Alice": 50, "Bob": 50}
    genesis = blockchain.create_genesis_block(initial_balances)
    
    for i in range(5):
        transactions = [
            tx_manager.create_random_transaction(("Alice", "Bob"), max_amount=5)
            for _ in range(3)
        ]
        
        print(f"\n Mining block {i + 1}")
        print(f"Candidate transactions: {transactions}")
        try:
            block = blockchain.mine_block(transactions)
            print(f"Block mined: {block}")
            print(f"   State: Alice={blockchain.get_balance('Alice')}, Bob={blockchain.get_balance('Bob')}")
        except Exception as e:
            print(f"Failed to mine block: {e}")
            