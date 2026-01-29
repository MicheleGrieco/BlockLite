import random
from typing import Optional
from exceptions import InsufficientFundsError, UnbalancedTransactionError

class TransactionManager:

    def __init__(self, seed: Optional[int] = None) -> None:
        """
        Initialize the transactions manager.
        
        Args:
            seed: Optional random seed for reproducible transaction generation.
        """

        if seed is not None:
            random.seed(seed) # Set a fixed seed for reproducibility
        
    def create_transaction(self, sender: str, receiver: str, amount: int) -> dict:
        """
        Create a transaction transferring tokens between accounts.
        
        Args:
            sender: The account sending tokens (will be debited).
            receiver: The account receiving tokens (will be credited).
            amount: The positive amount to transfer.
        
        Returns:
            A transaction dictionary with account changes.
        
        Raises:
            ValueError: If amount is not positive.
        """
        
        if amount <= 0:
            raise ValueError("Transaction amount must be positive.")
        
        return {sender: -amount, receiver: amount}
    
    def create_random_transaction(
        self, 
        accounts: tuple[str, str] = ("Alice", "Bob"),
        max_amount: int = 3
    ) -> dict[str, int]:
        """
        Create a random transaction between two accounts.
        
        Args:
            accounts: Tuple of two account names.
            max_amount: Maximum transfer amount.
        
        Returns:
            A random valid transaction dictionary.
        """
        amount = random.randint(1, max_amount)
        # Randomly choose direction
        if random.random() < 0.5:
            return {accounts[0]: -amount, accounts[1]: amount}
        else:
            return {accounts[0]: amount, accounts[1]: -amount}
    
    def validate_transaction(
        self, 
        transaction: dict[str, int], 
        state: dict[str, int]
    ) -> None:
        """
        Validate a transaction against the current state.
        
        Args:
            transaction: The transaction to validate.
            state: Current account balances.
        
        Raises:
            UnbalancedTransactionError: If transfers don't sum to zero.
            InsufficientFundsError: If any account would go negative.
        """
        # Rule 1: Conservation of tokens
        if sum(transaction.values()) != 0:
            raise UnbalancedTransactionError(
                f"Transaction must sum to zero, got {sum(transaction.values())}"
            )
        
        # Rule 2: No overdrafts
        for account, change in transaction.items():
            current_balance = state.get(account, 0)
            new_balance = current_balance + change
            if new_balance < 0:
                raise InsufficientFundsError(
                    f"Account '{account}' would have negative balance: {new_balance}"
                )
    
    def is_valid(self, transaction: dict[str, int], state: dict[str, int]) -> bool:
        """
        Check if a transaction is valid without raising exceptions.
        
        Args:
            transaction: The transaction to check.
            state: Current account balances.
        
        Returns:
            True if valid, False otherwise.
        """
        try:
            self.validate_transaction(transaction, state)
            return True
        except (UnbalancedTransactionError, InsufficientFundsError):
            return False
    
    @staticmethod
    def apply_transaction(
        transaction: dict[str, int], 
        state: dict[str, int]
    ) -> dict[str, int]:
        """
        Apply a transaction to a state, returning the new state.
        
        Note: This does NOT validate the transaction. Call validate_transaction
        first if validation is needed.
        
        Args:
            transaction: The transaction to apply.
            state: Current account balances.
        
        Returns:
            New state dictionary with updated balances.
        """
        new_state = state.copy()
        for account, change in transaction.items():
            new_state[account] = new_state.get(account, 0) + change
        return new_state