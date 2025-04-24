import random

random.seed(0)

def makeTransaction(maxValue=3):
    # Creates a valid transaction in the range of (1, maxValue)
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