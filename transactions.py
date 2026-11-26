"""
Transaction creation, validation and application.

A transaction is a mapping {account: delta}. Negative deltas are
withdrawals, positive deltas are deposits. A valid transaction:
    1. is a non-empty dict of non-empty string accounts to non-zero ints;
    2. sums to zero (conservation of tokens);
    3. leaves no account with a negative balance (no overdrafts).
"""

import random
from typing import Optional

from exceptions import (
    InsufficientFundsError,
    InvalidTransactionError,
    MalformedTransactionError,
    UnbalancedTransactionError,
)

Transaction = dict[str, int]
State = dict[str, int]


def _is_strict_int(value: object) -> bool:
    """True for ints but not bools (bool is a subclass of int in Python)."""
    return isinstance(value, int) and not isinstance(value, bool)


class TransactionManager:
    """Creates, validates and applies account-based transactions."""

    def __init__(self, seed: Optional[int] = None) -> None:
        """
        Initialize the transactions manager.

        Args:
            seed: Optional random seed for reproducible transaction generation.
                  A private RNG is used, so the global `random` module is untouched.
        """
        self._rng = random.Random(seed)

    def create_transaction(self, sender: str, receiver: str, amount: int) -> Transaction:
        """
        Create a transaction transferring tokens between accounts.

        Args:
            sender: The account sending tokens (will be debited).
            receiver: The account receiving tokens (will be credited).
            amount: The positive amount to transfer.

        Returns:
            A transaction dictionary with account changes.

        Raises:
            ValueError: If amount is not a positive integer or sender == receiver.
        """
        if not _is_strict_int(amount) or amount <= 0:
            raise ValueError("Transaction amount must be a positive integer.")
        if sender == receiver:
            raise ValueError("Sender and receiver must be different accounts.")

        return {sender: -amount, receiver: amount}

    def create_random_transaction(
        self,
        accounts: tuple[str, str] = ("Alice", "Bob"),
        max_amount: int = 3,
    ) -> Transaction:
        """
        Create a random transaction between two accounts.

        Args:
            accounts: Tuple of two account names.
            max_amount: Maximum transfer amount.

        Returns:
            A random, well-formed transaction (it may still overdraw an account).
        """
        amount = self._rng.randint(1, max_amount)
        sender, receiver = accounts if self._rng.random() < 0.5 else accounts[::-1]
        return {sender: -amount, receiver: amount}

    @staticmethod
    def validate_structure(transaction: object) -> None:
        """
        Check the shape of a transaction, independently of any state.

        Raises:
            MalformedTransactionError: If the transaction is not a non-empty
                dict of non-empty str accounts to non-zero ints.
        """
        if not isinstance(transaction, dict):
            raise MalformedTransactionError(
                f"Transaction must be a dict, got {type(transaction).__name__}"
            )
        if not transaction:
            raise MalformedTransactionError("Transaction must not be empty")

        for account, change in transaction.items():
            if not isinstance(account, str) or not account:
                raise MalformedTransactionError(
                    f"Account names must be non-empty strings, got {account!r}"
                )
            if not _is_strict_int(change):
                raise MalformedTransactionError(
                    f"Amount for '{account}' must be an int, got {type(change).__name__}"
                )
            if change == 0:
                raise MalformedTransactionError(f"Amount for '{account}' must be non-zero")

    def validate_transaction(self, transaction: Transaction, state: State) -> None:
        """
        Validate a transaction against the current state.

        Args:
            transaction: The transaction to validate.
            state: Current account balances.

        Raises:
            MalformedTransactionError: If the transaction has the wrong shape.
            UnbalancedTransactionError: If transfers don't sum to zero.
            InsufficientFundsError: If any account would go negative.
        """
        self.validate_structure(transaction)

        # Rule 1: Conservation of tokens
        total = sum(transaction.values())
        if total != 0:
            raise UnbalancedTransactionError(f"Transaction must sum to zero, got {total}")

        # Rule 2: No overdrafts
        for account, change in transaction.items():
            new_balance = state.get(account, 0) + change
            if new_balance < 0:
                raise InsufficientFundsError(
                    f"Account '{account}' would have negative balance: {new_balance}"
                )

    def is_valid(self, transaction: Transaction, state: State) -> bool:
        """
        Check if a transaction is valid without raising exceptions.

        Returns:
            True if valid, False otherwise.
        """
        try:
            self.validate_transaction(transaction, state)
            return True
        except InvalidTransactionError:
            return False

    @staticmethod
    def validate_initial_balances(balances: object) -> None:
        """
        Validate the token allocation of a genesis block.

        Genesis is the only place where tokens are created, so it is exempt
        from the zero-sum rule, but balances must still be well-formed and
        non-negative.

        Raises:
            MalformedTransactionError: If balances are malformed or negative.
        """
        if not isinstance(balances, dict) or not balances:
            raise MalformedTransactionError("Initial balances must be a non-empty dict")
        for account, amount in balances.items():
            if not isinstance(account, str) or not account:
                raise MalformedTransactionError(
                    f"Account names must be non-empty strings, got {account!r}"
                )
            if not _is_strict_int(amount) or amount < 0:
                raise MalformedTransactionError(
                    f"Initial balance for '{account}' must be a non-negative int, got {amount!r}"
                )

    @staticmethod
    def apply_transaction(transaction: Transaction, state: State) -> State:
        """
        Apply a transaction to a state, returning the new state.

        Note: This does NOT validate the transaction. Call validate_transaction
        first if validation is needed.

        Returns:
            New state dictionary with updated balances (input is not modified).
        """
        new_state = state.copy()
        for account, change in transaction.items():
            new_state[account] = new_state.get(account, 0) + change
        return new_state
