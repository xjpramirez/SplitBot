import re
from typing import Dict, List, Tuple, Optional

def parse_split_command(command_text: str) -> Dict:
    """Parse the /split command."""
    # Initialize the result
    result = {
        "total_amount": None,
        "payers": [],
        "attendees": [],
        "description": "Expense"
    }
    
    # Extract the total amount
    total_match = re.search(r'total\s+(\d+(\.\d+)?)', command_text)
    if total_match:
        result["total_amount"] = float(total_match.group(1))
    
    # Extract the payers
    paid_by_section = re.search(r'paid_by\s+(.*?)(?=attendees|note|$)', command_text)
    if paid_by_section:
        paid_by_text = paid_by_section.group(1).strip()
        
        # Match user IDs with optional amounts
        # Format: @user1 [amount1] @user2 [amount2] ...
        payer_matches = re.finditer(r'<@([A-Z0-9]+)>\s*(?:(\d+(\.\d+)?)\s*)?', paid_by_text)
        
        # If we have a single payer with no amount, assume they paid the total
        payers = list(payer_matches)
        if len(payers) == 1 and not payers[0].group(2):
            result["payers"].append({
                "user_id": payers[0].group(1),
                "amount": result["total_amount"]
            })
        else:
            # Process multiple payers with specified amounts
            total_paid = 0
            for match in payers:
                user_id = match.group(1)
                if match.group(2):  # Amount specified
                    amount = float(match.group(2))
                    result["payers"].append({
                        "user_id": user_id,
                        "amount": amount
                    })
                    total_paid += amount
            
            # Validate that the sum of paid amounts equals the total
            if total_paid != result["total_amount"]:
                raise ValueError(f"Sum of paid amounts ({total_paid}) does not equal total amount ({result['total_amount']})")
    
    # Extract the attendees
    attendees_section = re.search(r'attendees\s+(.*?)(?=note|$)', command_text)
    if attendees_section:
        attendees_text = attendees_section.group(1).strip()
        
        # Match user IDs
        attendee_matches = re.finditer(r'<@([A-Z0-9]+)>', attendees_text)
        for match in attendee_matches:
            result["attendees"].append(match.group(1))
    
    # Extract the description
    note_match = re.search(r'note\s+(.*?)$', command_text)
    if note_match:
        result["description"] = note_match.group(1).strip()
    
    return result


def extract_user_ids(text: str) -> List[str]:
    """Extract user IDs from a string."""
    user_ids = []
    
    # Match all user mentions
    matches = re.finditer(r'<@([A-Z0-9]+)>', text)
    for match in matches:
        user_ids.append(match.group(1))
    
    return user_ids 