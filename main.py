"""
RULES for a simple banking system:
- The sum of deposits and withdrawals must be 0 (tokens are neither created nor destroyed)
- A user’s account must have sufficient funds to cover any withdrawals
"""

from transactions import make_transaction
from blockchain import make_block, check_chain
from utils import hashMe

# Initialize
genesisBlock = {
    'hash': '',
    'contents': {
        'blockNumber': 0,
        'parentHash': None,
        'txnCount': 1,
        'txns': [{'Alice': 50, 'Bob': -50}]
    }
}
genesisBlock['hash'] = hashMe(genesisBlock['contents'])
chain = [genesisBlock]

# Add blocks
for i in range(5):
    txnBuffer = [make_transaction() for _ in range(5)]
    newBlock = make_block(txnBuffer, chain)
    chain.append(newBlock)

# Check chain validity
final_state = check_chain(chain)
print("Final state:", final_state)