# BlockLite

A minimal yet powerful blockchain algorithm built from scratch in Python.
> Credits: <a href="https://ecomunsing.com/build-your-own-blockchain">Build your own blockchain</a> by Ellery Comunsing.

# Getting Started

BlockLite is currently under active development. The following features have already been implemented:

- Basic blockchain structure with blocks linked by hash
- Mining function with proof-of-work
- Chain validation
- Adding new transactions and blocks
- Blockchain serialization and deserialization

## Next Steps

- Implementation of a simple REST API
- Minimal user interface
- Improved transaction management

## How to contribute

Feel free to open issues or pull requests to suggest improvements or report bugs.

# Technical Overview

## Architecture

BlockLite is composed of the following core components:

- **Block**: Represents a single block in the chain, containing transactions, a timestamp, a nonce, and the hash of the previous block.
- **Blockchain**: Manages the chain of blocks, validation logic, and consensus (proof-of-work).
- **Transaction**: (Planned) Encapsulates transaction data to be included in blocks.
- **Persistence**: Serialization and deserialization of the blockchain to/from disk.

## Features

- SHA-256 hashing for block integrity
- Adjustable proof-of-work difficulty
- Chain validation to ensure immutability
- Simple transaction pool (planned)
- Extensible for networking and APIs

## Usage

1. **Clone the repository**  
   `git clone https://github.com/yourusername/BlockLite.git`

2. **Install dependencies**  
   BlockLite uses only Python standard libraries (Python 3.7+ required).

3. **Run the blockchain**  
   ```bash
   python main.py
   ```

4. **Mine a new block**  
   Use the CLI or API (when available) to add transactions and mine blocks.

## Project Status

BlockLite is under active development. Implemented features:

- Core blockchain and block logic
- Proof-of-work mining
- Chain validation
- Block and chain serialization

Planned features:

- REST API for interaction
- Minimal web-based UI
- Enhanced transaction management
- Peer-to-peer networking

## Contributing

- Fork the repository and create a feature branch
- Write clear, concise commit messages
- Ensure code is PEP8 compliant and tested
- Open a pull request describing your changes
---
