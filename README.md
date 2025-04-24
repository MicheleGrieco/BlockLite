# BlockLite

A minimal yet powerful blockchain algorithm built from scratch in Python.
> Credits: <a href="https://ecomunsing.com/build-your-own-blockchain">Build your own blockchain</a> by Ellery Comunsing.

# Getting Started
Clone the repository and follow the inline comments in the Python scripts to explore each part of the blockchain.
```bash
git clone https://github.com/MicheleGrieco/blocklite.git
cd blocklite
python3 [main]
```

# Introduction

Ever wondered how Bitcoin, Ethereum, and other cryptocurrencies actually work under the hood? This project is a hands-on, code-first exploration into the fundamental mechanics of blockchain technology.

We'll demystify blockchains by constructing a simple yet functional model, focusing on how and why it works—one block at a time.

## The Basics

This tutorial will walk you through the basics of **how to build a blockchain from scratch**. Focusing on the details of a concrete example will provide a deeper understanding of the strengths and limitations of blockchains.

## Transactions, Validation and updating system state

At its core, **a blockchain is a distributed database with a set of rules for verifying new additions to the database**. We'll start off by tracking the accounts of two imaginary people: *Alice* and *Bob*, who will trade virtual money with each other.

We’ll need to create a **transaction pool** of incoming transactions, **validate** those transactions, and make them into a **block**.

We’ll be using a **hash function** to create a ‘*fingerprint*’ for each of our transactions - this hash function links each of our blocks to each other. To make this easier to use, we’ll define a **helper function** to wrap the python hash function that we’re using.

Next, we want to create a function to generate exchanges between Alice and Bob. We’ll indicate *withdrawals* with negative numbers, and *deposits* with positive numbers. We’ll construct our transactions to always be between the two users of our system, and make sure that the deposit is the same magnitude as the withdrawal - i.e. that we’re neither creating nor destroying money.

Now let’s create a large set of transactions, then chunk them into blocks.

Next step: making our very own blocks! We’ll take the first *k* transactions from the transaction buffer, and turn them into a block. Before we do that, we need to define a method for checking the **validity of the transactions** we’ve pulled into the block.

For *bitcoin*, the validation function checks that the input values are valid unspent transaction outputs (UTXOs), that the outputs of the transaction are no greater than the input, and that the keys used for the signatures are valid. In *Ethereum*, the validation function checks that the smart contracts were faithfully executed and respect gas limits.

[TODO: Expand ruleset]