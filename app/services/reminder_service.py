import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from slack_bolt import App as SlackApp

from app.services.expense_service import ExpenseService
from app.utils.message_builder import build_reminder_message

logger = logging.getLogger(__name__)

class ReminderService:
    """Service to handle automated reminders for unpaid debts."""
    
    def __init__(self, slack_app: SlackApp, expense_service: ExpenseService = None):
        """Initialize the reminder service."""
        self.slack_app = slack_app
        self.expense_service = expense_service or ExpenseService()
        self.reminder_interval = timedelta(hours=24)
        self._running = False
    
    async def start_reminder_scheduler(self):
        """Start the reminder scheduler."""
        self._running = True
        logger.info("Starting reminder scheduler")
        
        while self._running:
            try:
                await self.send_automatic_reminders()
            except Exception as e:
                logger.error(f"Error sending automatic reminders: {e}")
            
            # Sleep for 1 hour before checking again
            await asyncio.sleep(3600)
    
    def stop_reminder_scheduler(self):
        """Stop the reminder scheduler."""
        self._running = False
        logger.info("Stopping reminder scheduler")
    
    async def send_automatic_reminders(self):
        """Send automatic reminders for all pending debts."""
        pending_debts = self.expense_service.get_pending_debts()
        
        now = datetime.now()
        
        for pending_debt in pending_debts:
            expense = pending_debt["expense"]
            debt = pending_debt["debt"]
            expense_id = pending_debt["expense_id"]
            
            # If we haven't sent a reminder yet, or it's been more than the reminder interval
            if (debt.last_reminder_sent is None or 
                (now - debt.last_reminder_sent) >= self.reminder_interval):
                
                # Send the reminder
                await self.send_reminder(expense_id, debt.debtor_id, debt.payer_id)
                
                # Update the reminder timestamp
                self.expense_service.update_reminder_timestamp(
                    expense_id, debt.debtor_id, debt.payer_id
                )
    
    async def send_reminder(self, expense_id: str, debtor_id: str, payer_id: str) -> bool:
        """Send a reminder to a debtor."""
        expense = self.expense_service.get_expense(expense_id)
        if not expense:
            return False
        
        # Find the specific debt
        debt = next(
            (d for d in expense.debts 
             if d.debtor_id == debtor_id and d.payer_id == payer_id and not d.is_paid),
            None
        )
        
        if not debt:
            return False
        
        try:
            # Build the reminder message
            blocks = build_reminder_message(expense, debt)
            
            # Send a DM to the debtor
            response = self.slack_app.client.chat_postMessage(
                channel=debtor_id,
                text=f"Reminder: You owe money for {expense.description}",
                blocks=blocks
            )
            
            return response["ok"]
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
            return False
    
    async def send_manual_reminders(self) -> Dict[str, int]:
        """Send manual reminders for all pending debts."""
        pending_debts = self.expense_service.get_pending_debts()
        
        sent_count = 0
        failed_count = 0
        
        for pending_debt in pending_debts:
            expense = pending_debt["expense"]
            debt = pending_debt["debt"]
            expense_id = pending_debt["expense_id"]
            
            # Send the reminder
            success = await self.send_reminder(expense_id, debt.debtor_id, debt.payer_id)
            
            if success:
                sent_count += 1
                # Update the reminder timestamp
                self.expense_service.update_reminder_timestamp(
                    expense_id, debt.debtor_id, debt.payer_id
                )
            else:
                failed_count += 1
        
        return {
            "sent": sent_count,
            "failed": failed_count,
            "total": sent_count + failed_count
        } 