"""
    RULES for a simple banking system:
    - The sum of deposits and withdrawals must be 0 (tokens are neither created nor destroyed)
    - A user’s account must have sufficient funds to cover any withdrawals
"""

###############################################################################


def makeBlock(txns, chain):
    """
    Creates a new block with the given transactions and appends it to the blockchain.
    The block is created by hashing the transactions and the previous block's hash.

    Args:
        txns (list): list of transactions to include in the block
        chain (list): chain of blocks to which the new block will be appended

    Returns:
        block (dict): the new block created with its hash and contents
    """
    parentBlock = chain[-1]  # Get the last block in the chain
    parentHash = parentBlock[u'hash']  # Get the hash of the last block
    blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1  # Increment the block number
    txnCount = len(txns)  # Get the number of transactions in the new block
    blockContents = {u'blockNumber':blockNumber, u'parentHash':parentHash, u'txnCount':len(txns), u'txns':txns}  # Create the block contents
    blockHash = hashMe(blockContents)  # Hash the block contents to get the block hash
    block = {u'hash':blockHash, u'contents':blockContents}  # Create the block with its hash and contents
    return block


###############################################################################


def checkBlockHash(block):
    """
    Checks if the hash of the block matches the hash in the block.

    Args:
        block (dict): The block to check.

    Returns:
        bool: True if the hash matches, False otherwise.
    """

    # Raise an exception if the hash does not match the block contents
    expectedHash = hashMe(block['contents'])
    if block['hash'] != expectedHash:
        raise Exception('Hash does not match contents of block %s'%block['contents']['blockNumber'])
    return


def checkBlockValidity(block, parent, state):
    """
    Checks if a block is valid according to the rules defined.
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
    
    parentNumber = parent[u'contents'][u'blockNumber']
    parentHash = parent[u'hash']
    blockNumber = block[u'contents'][u'blockNumber']
    
    # Check transaction validity; throw an error if an invalid transaction is found
    for txn in block[u'contents'][u'txns']:
        if isValidTxn(txn, state):
            state = updateState(txn, state)
        else:
            raise Exception('Invalid transaction in block %s: %s'%(blockNumber, txn))
    
    # Check hash integrity; raise error if inaccurate
    checkBlockHash(block)
    
    if blockNumber != parentNumber + 1:
        raise Exception('Hash does not match contents of block %s'%blockNumber)
    if block[u'contents'][u'parentHash'] != parentHash:
        raise Exception('Parent hash not accurate at block %s'%blockNumber)
    
    return state


def checkChain(chain):
    """
    Checks if a chain of blocks is valid according to the rules defined.
    Works through the chain from the genesis block (which gets special treatment),
    checking that all transactions are internally valid,
    that the transactions do not cause an overdraft,
    and that the blocks are linked by their hashes.
    
    Args:
        chain (list): A list of blocks to check.
    
    Returns:
        state (dict): The final state of the accounts if the chain is valid, False otherwise.
    """
    
    if type(chain) == str:
        try:
            chain = json.loads(chain)
            assert type(chain) == list
        except:
            return False
    elif type(chain) != list:
        return False
    
    state = {}
    
    for txn in chain[0][u'contents'][u'txns']:
        state = updateState(txn, state)
    checkBlockHash(chain[0])
    parent = chain[0]
    
    for block in chain[1:]:
        state = checkBlockValidity(block, parent, state)
        parent = block
        
    return state

###############################################################################


def checkBlockHash(block):
    """
    Checks if the hash of the block matches the hash in the block.

    Args:
        block (dict): The block to check.

    Returns:
        bool: True if the hash matches, False otherwise.
    """

    # Raise an exception if the hash does not match the block contents
    expectedHash = hashMe(block['contents'])
    if block['hash'] != expectedHash:
        raise Exception('Hash does not match contents of block %s'%block['contents']['blockNumber'])
    return


def checkBlockValidity(block, parent, state):
    """
    Checks if a block is valid according to the rules defined.
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
    Raises:
        Exception: If the block is invalid, an exception is raised with a message indicating the reason.
    """
    
    parentNumber = parent[u'contents'][u'blockNumber']
    parentHash = parent[u'hash']
    blockNumber = block[u'contents'][u'blockNumber']
    
    # Check transaction validity; throw an error if an invalid transaction is found
    for txn in block[u'contents'][u'txns']:
        if isValidTxn(txn, state):
            state = updateState(txn, state)
        else:
            raise Exception('Invalid transaction in block %s: %s'%(blockNumber, txn))
        
    # Check hash integrity; raise error if inaccurate
    checkBlockHash(block)
    
    if blockNumber != parentNumber + 1:
        raise Exception('Hash does not match contents of block %s'%blockNumber)
    
    if block[u'contents'][u'parentHash'] != parentHash:
        raise Exception('Parent hash not accurate at block %s'%blockNumber)
    
    return state


def checkChain(chain):
    """
    Checks if a chain of blocks is valid according to the rules defined.
    Works through the chain from the genesis block (which gets special treatment),
    checking that all transactions are internally valid,
    that the transactions do not cause an overdraft,
    and that the blocks are linked by their hashes.
    Args:
        chain (list): A list of blocks to check.
    Returns:
        state (dict): The final state of the accounts if the chain is valid, False otherwise.
    Raises:
        Exception: If the chain is invalid, an exception is raised with a message indicating the reason.
    """
    
    if type(chain) == str:
        try:
            chain = json.loads(chain)
            assert type(chain) == list
        except: # This will catch any errors in the JSON parsing
            return False
    elif type(chain) != list:
        return False
    
    state = {}
    
    for txn in chain[0][u'contents'][u'txns']:
        state = updateState(txn, state)
    checkBlockHash(chain[0])
    parent = chain[0]
    
    for block in chain[1:]:
        state = checkBlockValidity(block, parent, state)
        parent = block
    
    return state

###############################################################################