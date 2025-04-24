import random

random.seed(0)

"""
    makeTransaction(maxValue=3) -> dict
    Creates a random transaction between Alice and Bob, where the amount is between -maxValue and maxValue.
    The sum of deposits and withdrawals must be 0 (tokens are neither created nor destroyed)
    A user’s account must have sufficient funds to cover any withdrawals.
    The transaction is represented as a dictionary with account names as keys and amounts as values.
    The function returns a dictionary with the transaction details.
    The transaction is guaranteed to be valid according to the rules defined in the isValidTxn function.
"""
def makeTransaction(maxValue=3):
    sign = int(random.getrandbits(1)) * 2 - 1
    # Randomly choose a value between -1 and 1
    amount = random.randint(1, maxValue)
    alicePays = sign * amount
    bobPays = -1 * alicePays
    
    # By construction, this will always return transactions that respect the conservation of tokens.
    # However, note that we have not done anything to check whether these overdraft an account
    return {u'Alice':alicePays,u'Bob':bobPays}

# This is a list of transactions that will be used to test the algorithm.
txnBuffer = [makeTransaction() for i in range(30)]