import random

class TransactionManager:

    def __init__(self, initial_state=None) -> None:
        """
        Initialize transactions manager.
        
        Args:
            initial_state (dict, optional): Initial state of the transactions. Default: None
        """

        random.seed(0) # Set a fixed seed for reproducibility
        self.state = initial_state if initial_state is not None else {}

    def make_transaction(self, max_value=3) -> dict:
        """
        Creates a random transaction between Alice and Bob, where the amount is between -max_value and max_value.
        The sum of deposits and withdrawals must be 0 (tokens are neither created nor destroyed).
        A user’s account must have sufficient funds to cover any withdrawals.
        The transaction is represented as a dictionary with account names as keys and amounts as values.
        The function returns a dictionary with the transaction details.
        The transaction is guaranteed to be valid according to the rules defined in the is_valid_transaction function.

        Args:
            max_value (int, optional): Defaults to 3.

        Returns:
            str: A string representation of the transaction.
        """
        # Randomly choose a value between -1 and 1
        sign = int(random.getrandbits(1)) * 2 - 1
        amount = random.randint(1, max_value)
        
        # By construction, this will always return transactions that respect the conservation of tokens.
        alice_pays = sign * amount
        bob_pays = -1 * alice_pays
        
        return {u'Alice':alice_pays, u'Bob':bob_pays}


    def update_state(self, transaction, state) -> dict:
        """
        Updates the state of the accounts based on the transaction.
        
        Args:
            transaction (dict): dictionary keyed with account names, holding numeric values for transfer amount
            state (dict): dictionary keyed with account names, holding numeric values for account balance

        Returns:
            dict: Updated state, with additional users added to state if necessary
        """
        if not self.is_valid_transaction(transaction):
            raise ValueError("Invalid transaction.")
        
        # Update the state with the transaction
        for account, amount in transaction.items():
            if account in self.state:
                self.state[account] += amount
            else:
                self.state[account] = amount
                
        # As dictionaries are mutable, let's avoid any confusion by creating a working copy of the data.
        return self.state.copy()


    def is_valid_transaction(self, transaction) -> bool:
        
        """
        Checks if a transaction is valid according to the rules defined.
        
        Args:
            txn (dict): dictionary keyed with account names, holding numeric values for transfer amount
            state (dict): dictionary keyed with account names, holding numeric values for account balance

        Returns:
            bool: True if the transaction is valid, False otherwise
        """

        # Check that the sum of the deposits and withdrawals is 0
        if sum(transaction.values()) != 0:
            return False
        
        # Check that the transaction does not cause an overdraft
        for account, amount in transaction.items():
            current_balance = self.state.get(account, 0)
            if (current_balance + amount) < 0:
                return False
        
        return True
    
    def get_state(self) -> dict:
        """
        Return a copy of the current state
        Returns:
            dict: Current transactions state
        """
        return self.state.copy()