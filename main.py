"""
BlockLite - A minimal blockchain implementation in Python.

This script demonstrates the core blockchain functionality:
1. Creating a genesis block with initial balances
2. Submitting transactions to the pending pool (mempool)
3. Mining new blocks with proof-of-work
4. Saving, reloading and verifying chain integrity
"""

import time
from pathlib import Path

from blockchain import Blockchain
from exceptions import InvalidBlockError, InvalidTransactionError
from transactions import TransactionManager

DIFFICULTY = 3
CHAIN_FILE = Path("chain.json")


def main() -> None:
    tx_manager = TransactionManager(seed=42)  # Fixed seed for reproducibility
    blockchain = Blockchain(difficulty=DIFFICULTY, tx_manager=tx_manager)

    genesis = blockchain.create_genesis_block({"Alice": 50, "Bob": 50})
    print(f"Genesis: {genesis}")

    for i in range(5):
        print(f"\nRound {i + 1}")
        for _ in range(3):
            txn = tx_manager.create_random_transaction(("Alice", "Bob"), max_amount=5)
            try:
                blockchain.submit_transaction(txn)
                print(f"  accepted  {txn}")
            except InvalidTransactionError as e:
                print(f"  rejected  {txn}: {e}")

        try:
            start = time.perf_counter()
            block = blockchain.mine_pending()
            elapsed = time.perf_counter() - start
            print(f"  mined     {block} in {elapsed:.3f}s")
            print(
                f"  state     Alice={blockchain.get_balance('Alice')}, "
                f"Bob={blockchain.get_balance('Bob')}"
            )
        except InvalidBlockError as e:
            print(f"  nothing to mine: {e}")

    blockchain.save(CHAIN_FILE)
    reloaded = Blockchain.load(CHAIN_FILE)
    reloaded.validate_chain()
    print(f"\nSaved and reloaded {CHAIN_FILE}: {reloaded}")


if __name__ == "__main__":
    main()
