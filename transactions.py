import random

# Set the random seed for reproducibility
random.seed(0)


def makeTransaction(maxValue=3):
    """
    Creates a random transaction between Alice and Bob, where the amount is between -maxValue and maxValue.
    The sum of deposits and withdrawals must be 0 (tokens are neither created nor destroyed).
    A user’s account must have sufficient funds to cover any withdrawals.
    The transaction is represented as a dictionary with account names as keys and amounts as values.
    The function returns a dictionary with the transaction details.
    The transaction is guaranteed to be valid according to the rules defined in the isValidTxn function.

    Args:
        maxValue (int, optional): Defaults to 3.

    Returns:
        str: A string representation of the transaction.
    """
    # Randomly choose a value between -1 and 1
    sign = int(random.getrandbits(1)) * 2 - 1
    amount = random.randint(1, maxValue)
    # By construction, this will always return transactions that respect the conservation of tokens.
    alicePays = sign * amount
    bobPays = -1 * alicePays
    
    return {u'Alice':alicePays,u'Bob':bobPays}


def updateState(txn, state):
    """
    Updates the state of the accounts based on the transaction.
    
    Args:
        txn (dict): dictionary keyed with account names, holding numeric values for transfer amount
        state (dict): dictionary keyed with account names, holding numeric values for account balance

    Returns:
        dict: Updated state, with additional users added to state if necessary
    """
    
    # As dictionaries are mutable, let's avoid any confusion by creating a working copy of the data.
    state = state.copy()
    for key in txn:
        if key in state.keys():
            state[key] += txn[key]
        else:
            state[key] = txn[key]
    return state


def isValidTxn(txn, state):
    
    """
    Checks if a transaction is valid according to the rules defined.
    
    Args:
        txn (dict): dictionary keyed with account names, holding numeric values for transfer amount
        state (dict): dictionary keyed with account names, holding numeric values for account balance

    Returns:
        bool: True if the transaction is valid, False otherwise
    """

    # Check that the sum of the deposits and withdrawals is 0
    if sum(txn.values()) != 0:
        return False
    
    # Check that the transaction does not cause an overdraft
    for key in txn.keys():
        if key in state.keys(): 
            acctBalance = state[key]
        else:
            acctBalance = 0
        if (acctBalance + txn[key]) < 0:
            return False
    
    return True