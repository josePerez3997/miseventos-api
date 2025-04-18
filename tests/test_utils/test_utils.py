import pytest
from datetime import datetime
from app.utils import get_current_timestamp

def test_get_current_timestamp():
    """Test para la función get_current_timestamp"""
    result = get_current_timestamp()
    
    assert isinstance(result, datetime)
    assert result.tzinfo is not None