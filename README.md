# BlockLite

A minimal yet powerful blockchain algorithm built from scratch in Python.
> Credits: <a href="https://ecomunsing.com/build-your-own-blockchain">Build your own blockchain</a> by Ellery Comunsing.

# Getting Started
Clone the repository and follow the inline comments in the Python scripts to explore each part of the blockchain.
```bash
git clone https://github.com/MicheleGrieco/blocklite.git
cd blocklite
python3 main.py
```

# Project Structure

```bash
blocklite/
├── __init__.py
├── utils.py            # General utility functions
├── transactions.py     # Transaction-related logic
├── blockchain.py       # Block and chain operations
└── main.py             # Entry point or test script
```

## The Basics

Ever wondered how Bitcoin, Ethereum, and other cryptocurrencies actually work under the hood? This project is a hands-on, code-first exploration into the fundamental mechanics of blockchain technology.

We'll demystify blockchains by constructing a simple yet functional model, focusing on how and why it works—one block at a time.

This tutorial will walk you through the basics of **how to build a blockchain from scratch**. Focusing on the details of a concrete example will provide a deeper understanding of the strengths and limitations of blockchains.

## Transactions, Validation and updating system state

At a fundamental level, **a blockchain is a shared database governed by rules that determine how new data can be added**. To illustrate this, we'll simulate accounts for two fictional users, *Alice* and *Bob*, who will exchange virtual currency.

We'll begin by building a **transaction pool** to store pending exchanges, then **verify** each transaction and group valid ones into **blocks**.

To ensure each transaction is uniquely identified and to link blocks together, we’ll use a **hash function** that acts like a digital fingerprint. To simplify this, we’ll define a helper called *hashMe(msg="")* that wraps Python’s built-in hashing.

We’ll also write a *makeTransaction()* function to simulate transfers between Alice and Bob. **Withdrawals** will be represented by negative values and **deposits** by positive ones. Every transaction will involve only these two users and ensure that no money is artificially created or destroyed—each deposit will exactly match a withdrawal.

```python
import random
random.seed(0)
```

Now let’s create a large set of transactions, then chunk them into blocks:

```python
txnBuffer = [makeTransaction() for i in range(30)]
```

Now it’s time to start creating our own blocks! We'll take the first *k* transactions from the transaction pool and bundle them into a new block. But before doing that, we need a way to **verify that the transactions are valid**.

In cryptocurrencies like *Bitcoin*, validation involves checking that inputs are unspent outputs from previous transactions, that total outputs don’t exceed inputs, and that digital signatures are correct. *Ethereum* does this by ensuring smart contracts run correctly and stay within gas limits.

Thankfully, our system is much simpler. We’ll use two basic rules that are suitable for a simple token-based model:

* The total of all deposits and withdrawals must be zero (so tokens aren’t created or destroyed).
* A user must have enough balance to make a withdrawal.

These checks are handled by the *updateState(txn, state)* and *isValidTxn(txn, state)* functions. Any transaction that breaks these rules will be rejected.

We’ll then test these rules using **example transactions**, including some intentionally invalid ones, to demonstrate how validation works.

```python
# Initial state
state = {u'Alice':5, u'Bob':5}

print(isValidTxn({u'Alice': -3, u'Bob': 3}, state))  # Valid
print(isValidTxn({u'Alice': -4, u'Bob': 3}, state))  # Not valid
print(isValidTxn({u'Alice': -6, u'Bob': 6}, state))  # Overdraft
print(isValidTxn({u'Alice': -4, u'Bob': 2,'Lisa':2}, state)) # Creating new user
print(isValidTxn({u'Alice': -4, u'Bob': 3,'Lisa':2}, state)) # Not valid
```

Each block holds a group of transactions, a link to the hash of the preceding block (for all blocks after the first), and its own hash, which is generated from its contents and header.

## Building the Blockchain: from Transactions to Blocks

Now we’re ready to build our blockchain! Since it’s currently empty, we’ll begin by creating the **genesis block**, which is the very first block in the chain. Unlike other blocks, it doesn’t reference a previous one, so we can define its state manually. For our setup, we’ll initialize accounts for Alice and Bob, assigning 50 coins to each.

```python
# Genesis block
# The genesis block is the first block in the blockchain, and it has no parent.
# Initial state of the system is set to 50 for both Alice and Bob.
state = {u'Alice':50, u'Bob':50}
genesisBlockTxns = [state]
genesisBlockContents = {u'blockNumber':0, u'parentHash':None, u'txnCount':1, u'txns':genesisBlockTxns}
genesisHash = hashMe(genesisBlockContents)
genesisBlock = {u'hash':genesisHash, u'contents':genesisBlockContents}
genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)

# Initialize the blockchain with the genesis block
chain = [genesisBlock]
```

This genesis block serves as the foundation for the entire blockchain—every subsequent block will be linked to it. For each new block, we’ll gather valid transactions, generate a header, compute its hash, and append it to the chain. The *makeBlock(txns, chain)* function handles this process.

Now, let’s use it to turn our transaction pool into a series of blocks:

```python
# Arbitrary number of transactions per block - this is chosen by the block miner, and can vary between blocks.
blockSizeLimit = 5

while len(txnBuffer) > 0:
    bufferStartSize = len(txnBuffer)
    
    # Gather a set of valid transactions for inclusion
    txnList = []
    while (len(txnBuffer) > 0) & (len(txnList) < blockSizeLimit):
        newTxn = txnBuffer.pop()
        validTxn = isValidTxn(newTxn,state) # This will return False if txn is invalid
        
        if validTxn:           # If we got a valid state, not 'False'
            txnList.append(newTxn)
            state = updateState(newTxn,state)
        else:
            print("ignored transaction")
            sys.stdout.flush()
            continue  # This was an invalid transaction: ignore it and move on.
        
    # Make a block
    myBlock = makeBlock(txnList,chain)
    chain.append(myBlock)  
    
    chain[0]
    chain[1]
```

As anticipated, the genesis block contains a special transaction that sets initial account balances—effectively creating tokens from nothing. Each subsequent block references the hash of its parent and includes new transactions that modify the system’s state. We can now observe how these transactions have updated the overall state.

```python
state
```

## Checking Chain Validity

Now that we know how to create new blocks and link them together into a chain, let’s define functions to check that new blocks are valid- and that the whole chain is valid.

On a blockchain network, this becomes important in two ways:

- When we initially set up our node, we will download the full blockchain history. After downloading the chain, we would need to run through the blockchain to compute the state of the system. To protect against somebody inserting invalid transactions in the initial chain, we need to check the validity of the entire chain in this initial download.
- Once our node is synced with the network (has an up-to-date copy of the blockchain and a representation of system state) it will need to check the validity of new blocks that are broadcast to the network.

We will need three functions to facilitate in this:

- **checkBlockHash**: A simple helper function that makes sure that the block contents match the hash
- **checkBlockValidity**: Checks the validity of a block, given its parent and the current system state. We want this to return the updated state if the block is valid, and raise an error otherwise.
- **checkChain**: Check the validity of the entire chain, and compute the system state beginning at the genesis block. This will return the system state if the chain is valid, and raise an error otherwise.

We can now check the validity of the state.

And even if we are loading the chain from a text file, e.g. from backup or loading it for the first time, we can check the integrity of the chain and create the current state:

```python
chainAsText = json.dumps(chain, sort_keys=True)
checkChain(chainAsText)
```

## Putting it together: The final Blockchain Architecture

In an actual blockchain network, new nodes would download a copy of the blockchain and verify it (as we just did above), then annouce their presence on the peer-to-peer network and start listening for transactions. Bundling transactions into a block, they then pass their proposed block on to other nodes.

We've seen how to verify a copy of the blockchain, and how to bundle transactions into a block. If we recieve a block from somewhere else, verifying it and adding it to our blockchain is easy.

Let's say that the following code runs on Node A, which mines the block:

```python
import copy
nodeBchain = copy.copy(chain)
nodeBtxns = [makeTransaction() for i in range(5)]
newBlock = makeBlock(nodeBtxns, nodeBchain)
```

Now assume that the newBlock is trasmitted to our node, and we want to check it and update our state if it is a valid block:

```python
print("Blockchain on Node A is currently %s blocks long"%len(chain))
try:
    print("New Block Received; checking validity...")
    # Update the state - this will throw an error if the block is invalid!
    state = checkBlockValidity(newBlock, chain[-1], state)
    chain.append(newBlock)
except:
    print("Invalid block; ignoring and waiting for the next block...")

print("Blockchain on Node A is now %s blocks long"%len(chain))
```

## Conclusions and Extensions

We've created all the basic architecture for a blockchain, from a set of state transition rules to a method for creating blocks, to mechanisms for checking the validity of transactions, blocks, and the full chain. We can derive the system state from a downloaded copy of the blockchain, validate new blocks that we receive from the network, and create our own blocks.

The system state that we've created is effectively a distriuted ledger or database - the core of many blockchains. We could extend this to include special transaction types or full smart contracts.

We haven't explored the network architecture, the proof-of-work or proof-of-state validation step, and the consensus mechanism which provides blockchains with security against attacks. We also haven't discussed public key cryptography, privacy, and verification steps. More on that in the future!