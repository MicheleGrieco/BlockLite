"""
    The sum of deposits and withdrawals must be 0 (tokens are neither created nor destroyed)
    A user’s account must have sufficient funds to cover any withdrawals
"""

def updateState(txn, state):
    # Inputs: txn, state: dictionaries keyed with account names, holding numeric values for transfer amount (txn) or account balance (state)
    # Returns: Updated state, with additional users added to state if necessary
    # NOTE: This does not not validate the transaction- just updates the state!
    
    # If the transaction is valid, then update the state
    # As dictionaries are mutable, let's avoid any confusion by creating a working copy of the data.
    state = state.copy()
    for key in txn:
        if key in state.keys():
            state[key] += txn[key]
        else:
            state[key] = txn[key]
    return state

def isValidTxn(txn, state):
    # Assume that the transaction is a dictionary keyed by account names

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

state = {u'Alice':5, u'Bob':5}

print(isValidTxn({u'Alice': -3, u'Bob': 3}, state))  # Basic transaction- this works great!
print(isValidTxn({u'Alice': -4, u'Bob': 3}, state))  # But we can't create or destroy tokens!
print(isValidTxn({u'Alice': -6, u'Bob': 6}, state))  # We also can't overdraft our account.
print(isValidTxn({u'Alice': -4, u'Bob': 2,'Lisa':2}, state)) # Creating new users is valid
print(isValidTxn({u'Alice': -4, u'Bob': 3,'Lisa':2}, state)) # But the same rules still apply!