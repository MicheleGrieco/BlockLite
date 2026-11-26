# BlockLite

A minimal, account-based blockchain built from scratch in Python, with no runtime dependencies.
> Credits: <a href="https://ecomunsing.com/build-your-own-blockchain">Build your own blockchain</a> by Ellery Comunsing.

## Features

- Blocks linked by SHA-256 hash, immutable once created
- Proof-of-work mining with adjustable difficulty (leading hex zeros)
- Account-based transactions with three rules: well-formed, zero-sum, no overdrafts
- Genesis block as the only source of new tokens (non-negative allocations only)
- Pending transaction pool (mempool) validated against the projected state
- Full chain re-validation from genesis, including detection of a tampered state
- Timestamp checks (monotonic, bounded future drift)
- JSON serialization and atomic save/load to disk, with re-validation on load
- Typed exception hierarchy for precise error handling

## Getting started

Requires **Python 3.10+**.

```bash
git clone https://github.com/MicheleGrieco/BlockLite.git
cd BlockLite
python main.py          # runs the demo and writes chain.json
pip install -r requirements.txt
pytest                  # runs the test suite
```

## Usage

```python
from blockchain import Blockchain

bc = Blockchain(difficulty=3)
bc.create_genesis_block({"Alice": 50, "Bob": 50})

bc.submit_transaction({"Alice": -10, "Bob": 10})   # queued in the mempool
bc.submit_transaction({"Bob": -5, "Carol": 5})     # multi-account transfers are allowed
block = bc.mine_pending()                          # proof-of-work + validation

print(bc.get_balance("Alice"))   # 40
bc.validate_chain()              # replays the chain from genesis

bc.save("chain.json")
restored = Blockchain.load("chain.json")
```

## Architecture

| Module | Responsibility |
| --- | --- |
| `utils.py` | Canonical JSON, SHA-256 hashing, difficulty check |
| `exceptions.py` | `BlockchainError` hierarchy (transaction, block, PoW, load errors) |
| `transactions.py` | `TransactionManager`: creation, structural and state validation, application |
| `block.py` | Immutable `Block` dataclass, mining, (de)serialization |
| `blockchain.py` | `Blockchain`: chain rules, mempool, validation, persistence |
| `main.py` | Demo script |
| `tests.py` | pytest suite |

A transaction is a mapping `{account: delta}`; for example `{"Alice": -5, "Bob": 5}` moves 5 tokens from Alice to Bob.

## Roadmap

- Digital signatures (Ed25519) and account nonces, so only the owner can spend
- Merkle root in the block header
- Difficulty retargeting based on block time
- Command-line interface and REST API
- Peer-to-peer networking with longest/heaviest-chain fork choice

## Contributing

- Fork the repository and create a feature branch
- Write clear, concise commit messages
- Keep code PEP 8 compliant and covered by tests (`pytest`)
- Open a pull request describing your changes
