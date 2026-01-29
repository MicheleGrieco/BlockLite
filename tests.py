"""
Unit tests for the BlockLite blockchain.
"""

import pytest
import json

from utils import hash_data
from exceptions import (
    InvalidBlockError,
    InvalidTransactionError,
    InsufficientFundsError,
    UnbalancedTransactionError
)
from transactions import TransactionManager
from block import Block
from blockchain import Blockchain

class TestUtils:
    """Tests for utility functions."""
    
    def test_hash_string(self):
        """Hash of a string should be consistent."""
        
        result = hash_data("hello")
        assert isinstance(result, str)
        assert len(result) == 64 # SHA-256 produces 64 hex characters
        assert result == hash_data("hello")
        
    def test_hash_different_strings(self):
        """"Different strings should produce different hashes."""

        assert hash_data("hello") != hash_data("world")
        
    def test_hash_dict(self):
        """"Dictionaries should be hashable."""
        
        data = {"name": "Alice", "amount": 50}
        result = hash_data(data)
        assert isinstance(result, str)
        assert len(result) == 64
        
    def test_hash_dict_key_order_independent(self):
        """"Dict hash should not depend on key insertion order."""
        
        dict1 = {"b": 2, "a": 1}
        dict2 = {"a": 1, "b": 2}
        assert hash_data(dict1) == hash_data(dict2)
        