"""
Custom exceptions for the blockchain.
"""

class BlockchainError(Exception):
    """Base exception for all blockchain-related errors."""
    pass


class InvalidTransactionError(BlockchainError):
    """Raised when a transaction violates the rules."""
    pass


class InvalidBlockError(BlockchainError):
    """Raised when a block fails validation."""
    pass


class InsufficientFundsError(InvalidTransactionError):
    """Raised when an account has insufficient balance for a withdrawal."""
    pass


class UnbalancedTransactionError(InvalidTransactionError):
    """Raised when transaction deposits and withdrawals don't sum to zero."""
    pass