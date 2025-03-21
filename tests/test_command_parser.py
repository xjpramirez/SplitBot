import pytest
from app.utils.command_parser import parse_split_command, extract_user_ids


def test_parse_split_command_single_payer():
    """Test parsing a split command with a single payer."""
    command = "total 100000 paid_by <@USER1> attendees <@USER1> <@USER2> <@USER3> note Friday drinks 🍻"
    result = parse_split_command(command)
    
    assert result["total_amount"] == 100000
    assert len(result["payers"]) == 1
    assert result["payers"][0]["user_id"] == "USER1"
    assert result["payers"][0]["amount"] == 100000
    assert len(result["attendees"]) == 3
    assert "USER1" in result["attendees"]
    assert "USER2" in result["attendees"]
    assert "USER3" in result["attendees"]
    assert result["description"] == "Friday drinks 🍻"


def test_parse_split_command_multiple_payers():
    """Test parsing a split command with multiple payers."""
    command = "total 100000 paid_by <@USER1> 50000 <@USER2> 50000 attendees <@USER1> <@USER2> <@USER3> note Friday drinks 🍻"
    result = parse_split_command(command)
    
    assert result["total_amount"] == 100000
    assert len(result["payers"]) == 2
    assert result["payers"][0]["user_id"] == "USER1"
    assert result["payers"][0]["amount"] == 50000
    assert result["payers"][1]["user_id"] == "USER2"
    assert result["payers"][1]["amount"] == 50000
    assert len(result["attendees"]) == 3
    assert result["description"] == "Friday drinks 🍻"


def test_extract_user_ids():
    """Test extracting user IDs from a string."""
    text = "Hello <@USER1> and <@USER2>!"
    result = extract_user_ids(text)
    
    assert len(result) == 2
    assert "USER1" in result
    assert "USER2" in result 