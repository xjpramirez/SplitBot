from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Payment(BaseModel):
    """Represents a payment made by a payer for the expense."""
    user_id: str
    amount: float
    timestamp: datetime = Field(default_factory=datetime.now)


class Debt(BaseModel):
    """Represents a debt owed by a debtor to a payer."""
    debtor_id: str
    payer_id: str
    amount: float
    is_paid: bool = False
    paid_timestamp: Optional[datetime] = None
    last_reminder_sent: Optional[datetime] = None


class Expense(BaseModel):
    """Represents an expense to be split among attendees."""
    id: str
    total_amount: float
    payers: List[Payment]
    attendees: List[str]
    description: str
    channel_id: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    debts: List[Debt] = []
    
    def calculate_shares(self) -> None:
        """Calculate how much each attendee owes."""
        if not self.attendees:
            return
            
        # Calculate the share per person
        share_per_person = self.total_amount / len(self.attendees)
        
        # Create a dictionary to track how much each payer has paid
        payer_amounts = {}
        for payment in self.payers:
            payer_amounts[payment.user_id] = payment.amount
            
        # Create a dictionary to track how much each person owes
        debts = []
        
        # For each attendee who is not a payer, or who paid less than their share
        for attendee in self.attendees:
            # How much did this attendee pay (if anything)
            paid_amount = payer_amounts.get(attendee, 0)
            
            # How much does this attendee still owe
            remaining_to_pay = share_per_person - paid_amount
            
            # If they still owe money, create a debt for each payer who paid more than their share
            if remaining_to_pay > 0:
                for payer_id, payer_amount in payer_amounts.items():
                    payer_excess = payer_amount - share_per_person
                    
                    # If this payer paid more than their share, they are owed money
                    if payer_excess > 0 and payer_id != attendee:
                        # Calculate how much this attendee should pay this payer
                        amount_to_pay = min(remaining_to_pay, payer_excess)
                        
                        # Create a debt object
                        debt = Debt(
                            debtor_id=attendee,
                            payer_id=payer_id,
                            amount=amount_to_pay,
                            is_paid=False
                        )
                        debts.append(debt)
                        
                        # Update the remaining amount to pay
                        remaining_to_pay -= amount_to_pay
                        
                        # If nothing left to pay, break out of the loop
                        if remaining_to_pay <= 0:
                            break
        
        self.debts = debts 