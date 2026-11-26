"""
Custom exceptions for the blockchain.
"""


class BlockchainError(Exception):
    """Base exception for all blockchain-related errors."""


class InvalidTransactionError(BlockchainError):
    """Raised when a transaction violates the rules."""


class MalformedTransactionError(InvalidTransactionError):
    """Raised when a transaction has the wrong shape (types, empty, zero amounts)."""


class InsufficientFundsError(InvalidTransactionError):
    """Raised when an account has insufficient balance for a withdrawal."""


class UnbalancedTransactionError(InvalidTransactionError):
    """Raised when transaction deposits and withdrawals don't sum to zero."""


class InvalidBlockError(BlockchainError):
    """Raised when a block fails validation."""


class InvalidProofOfWorkError(InvalidBlockError):
    """Raised when a block hash does not satisfy the required difficulty."""


class ChainLoadError(BlockchainError):
    """Raised when a serialized chain cannot be parsed or loaded."""
