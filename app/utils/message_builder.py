from typing import Dict, List

from app.models.expense import Expense, Debt


def format_currency(amount: float) -> str:
    """Format a currency amount."""
    return f"${amount:,.0f}"


def build_expense_summary_message(expense: Expense) -> List[Dict]:
    """Build a message summarizing an expense."""
    # Calculate the share per person
    share_per_person = expense.total_amount / len(expense.attendees)
    
    # Group debts by payer
    debts_by_payer = {}
    for debt in expense.debts:
        if debt.payer_id not in debts_by_payer:
            debts_by_payer[debt.payer_id] = []
        debts_by_payer[debt.payer_id].append(debt)
    
    # Build the message
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{expense.description}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Total:* {format_currency(expense.total_amount)}\n*Attendees:* {len(expense.attendees)} people\n*Each person owes:* {format_currency(share_per_person)}"
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # Add payment summary
    for payer_id, payer_debts in debts_by_payer.items():
        debtor_text = ""
        for debt in payer_debts:
            paid_status = ":white_check_mark:" if debt.is_paid else ":hourglass_flowing_sand:"
            debtor_text += f"{paid_status} <@{debt.debtor_id}> owes <@{debt.payer_id}> {format_currency(debt.amount)}\n"
        
        if debtor_text:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": debtor_text
                }
            })
    
    return blocks


def build_payment_confirmation_message(expense: Expense, debt: Debt) -> List[Dict]:
    """Build a message to confirm payment."""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"You owe <@{debt.payer_id}> {format_currency(debt.amount)} for *{expense.description}*. Have you paid this amount?"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Yes, I've paid",
                        "emoji": True
                    },
                    "style": "primary",
                    "value": f"{expense.id}|{debt.debtor_id}|{debt.payer_id}",
                    "action_id": "confirm_payment"
                }
            ]
        }
    ]
    
    return blocks


def build_reminder_message(expense: Expense, debt: Debt) -> List[Dict]:
    """Build a reminder message for a debt."""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Hey! Don't forget to pay your share for *{expense.description}* 😄"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"You owe <@{debt.payer_id}> {format_currency(debt.amount)}"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "I've paid now",
                        "emoji": True
                    },
                    "style": "primary",
                    "value": f"{expense.id}|{debt.debtor_id}|{debt.payer_id}",
                    "action_id": "confirm_payment"
                }
            ]
        }
    ]
    
    return blocks


def build_payment_notification_message(expense: Expense, debt: Debt) -> List[Dict]:
    """Build a notification message for a payer when a debtor has paid."""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Good news! <@{debt.debtor_id}> has confirmed payment of {format_currency(debt.amount)} for *{expense.description}*."
            }
        }
    ]
    
    return blocks


def build_manual_reminder_summary(result: Dict) -> List[Dict]:
    """Build a summary message for manual reminders."""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Reminder Summary*\nSent: {result['sent']}\nFailed: {result['failed']}\nTotal: {result['total']}"
            }
        }
    ]
    
    return blocks 