"""
RULES for a simple banking system:
- The sum of deposits and withdrawals must be 0 (tokens are neither created nor destroyed)
- A user’s account must have sufficient funds to cover any withdrawals
"""

from transactions import makeTransaction
from blockchain import makeBlock, checkChain
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
    txnBuffer = [makeTransaction() for _ in range(5)]
    newBlock = makeBlock(txnBuffer, chain)
    chain.append(newBlock)

# Check chain validity
final_state = checkChain(chain)
print("Final state:", final_state)