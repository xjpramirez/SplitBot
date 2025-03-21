import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.models.expense import Expense, Payment, Debt


class ExpenseService:
    """Service to manage expense data."""
    
    def __init__(self):
        """Initialize the expense service with an in-memory database."""
        self.expenses: Dict[str, Expense] = {}
    
    def create_expense(
        self, 
        total_amount: float, 
        payers: List[Dict[str, float]], 
        attendees: List[str], 
        description: str, 
        channel_id: str,
        created_by: str
    ) -> Expense:
        """Create a new expense."""
        expense_id = str(uuid.uuid4())
        
        # Convert the payers list to Payment objects
        payment_objects = [
            Payment(user_id=payer["user_id"], amount=payer["amount"])
            for payer in payers
        ]
        
        # Create the expense
        expense = Expense(
            id=expense_id,
            total_amount=total_amount,
            payers=payment_objects,
            attendees=attendees,
            description=description,
            channel_id=channel_id,
            created_by=created_by,
            created_at=datetime.now()
        )
        
        # Calculate the shares
        expense.calculate_shares()
        
        # Save the expense
        self.expenses[expense_id] = expense
        
        return expense
    
    def get_expense(self, expense_id: str) -> Optional[Expense]:
        """Get an expense by ID."""
        return self.expenses.get(expense_id)
    
    def get_all_expenses(self) -> List[Expense]:
        """Get all expenses."""
        return list(self.expenses.values())
    
    def mark_debt_as_paid(self, expense_id: str, debtor_id: str, payer_id: str) -> bool:
        """Mark a debt as paid."""
        expense = self.get_expense(expense_id)
        if not expense:
            return False
        
        for debt in expense.debts:
            if debt.debtor_id == debtor_id and debt.payer_id == payer_id and not debt.is_paid:
                debt.is_paid = True
                debt.paid_timestamp = datetime.now()
                return True
        
        return False
    
    def get_pending_debts(self) -> List[Dict]:
        """Get all pending debts across all expenses."""
        pending_debts = []
        
        for expense_id, expense in self.expenses.items():
            for debt in expense.debts:
                if not debt.is_paid:
                    pending_debts.append({
                        "expense_id": expense_id,
                        "expense": expense,
                        "debt": debt
                    })
        
        return pending_debts
    
    def update_reminder_timestamp(self, expense_id: str, debtor_id: str, payer_id: str) -> bool:
        """Update the last reminder timestamp for a debt."""
        expense = self.get_expense(expense_id)
        if not expense:
            return False
        
        for debt in expense.debts:
            if debt.debtor_id == debtor_id and debt.payer_id == payer_id and not debt.is_paid:
                debt.last_reminder_sent = datetime.now()
                return True
        
        return False 