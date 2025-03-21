import logging
from typing import Dict

from slack_bolt import App as SlackApp
from slack_bolt.adapter.fastapi import SlackRequestHandler

from app.services.expense_service import ExpenseService
from app.services.reminder_service import ReminderService
from app.utils.command_parser import parse_split_command
from app.utils.message_builder import (
    build_expense_summary_message,
    build_payment_confirmation_message,
    build_payment_notification_message,
    build_manual_reminder_summary
)

logger = logging.getLogger(__name__)

# Create a global instance of the expense service
expense_service = ExpenseService()


def register_commands(slack_app: SlackApp, reminder_service: ReminderService):
    """Register all Slack commands with the app."""
    
    # Set the expense service on the reminder service
    reminder_service.expense_service = expense_service
    
    # Handle the /split command
    @slack_app.command("/split")
    async def handle_split_command(ack, command, client):
        """Handle the /split command."""
        await ack()  # Acknowledge the command
        
        try:
            # Parse the command text
            command_text = command["text"]
            
            # If the command is just "remind", send reminders
            if command_text.strip().lower() == "remind":
                result = await reminder_service.send_manual_reminders()
                blocks = build_manual_reminder_summary(result)
                
                await client.chat_postEphemeral(
                    channel=command["channel_id"],
                    user=command["user_id"],
                    text=f"Sent {result['sent']} reminders",
                    blocks=blocks
                )
                return
            
            # Parse the split command
            parsed = parse_split_command(command_text)
            
            # Validate the required fields
            if not parsed["total_amount"]:
                await client.chat_postEphemeral(
                    channel=command["channel_id"],
                    user=command["user_id"],
                    text="Error: Total amount is required"
                )
                return
            
            if not parsed["payers"]:
                await client.chat_postEphemeral(
                    channel=command["channel_id"],
                    user=command["user_id"],
                    text="Error: At least one payer is required"
                )
                return
            
            if not parsed["attendees"]:
                await client.chat_postEphemeral(
                    channel=command["channel_id"],
                    user=command["user_id"],
                    text="Error: At least one attendee is required"
                )
                return
            
            # Create the expense
            expense = expense_service.create_expense(
                total_amount=parsed["total_amount"],
                payers=parsed["payers"],
                attendees=parsed["attendees"],
                description=parsed["description"],
                channel_id=command["channel_id"],
                created_by=command["user_id"]
            )
            
            # Build the expense summary message
            blocks = build_expense_summary_message(expense)
            
            # Post the expense summary in the channel
            await client.chat_postMessage(
                channel=command["channel_id"],
                text=f"{parsed['description']} - Total: ${parsed['total_amount']:,.0f}",
                blocks=blocks
            )
            
            # Send payment confirmation messages to each debtor
            for debt in expense.debts:
                if not debt.is_paid:
                    confirmation_blocks = build_payment_confirmation_message(expense, debt)
                    
                    await client.chat_postMessage(
                        channel=debt.debtor_id,
                        text=f"You owe ${debt.amount:,.0f} for {expense.description}",
                        blocks=confirmation_blocks
                    )
            
        except Exception as e:
            logger.error(f"Error handling split command: {e}")
            
            await client.chat_postEphemeral(
                channel=command["channel_id"],
                user=command["user_id"],
                text=f"Error: {str(e)}"
            )
    
    # Handle the payment confirmation button click
    @slack_app.action("confirm_payment")
    async def handle_confirm_payment(ack, body, client):
        """Handle the payment confirmation button click."""
        await ack()  # Acknowledge the action
        
        try:
            # Parse the value
            value = body["actions"][0]["value"].split("|")
            expense_id = value[0]
            debtor_id = value[1]
            payer_id = value[2]
            
            # Mark the debt as paid
            if expense_service.mark_debt_as_paid(expense_id, debtor_id, payer_id):
                # Get the expense
                expense = expense_service.get_expense(expense_id)
                if not expense:
                    return
                
                # Find the debt
                debt = next(
                    (d for d in expense.debts 
                     if d.debtor_id == debtor_id and d.payer_id == payer_id and d.is_paid),
                    None
                )
                
                if not debt:
                    return
                
                # Update the message
                await client.chat_update(
                    channel=body["channel"]["id"],
                    ts=body["message"]["ts"],
                    text=f"You have paid ${debt.amount:,.0f} for {expense.description}",
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"You have paid <@{debt.payer_id}> ${debt.amount:,.0f} for *{expense.description}*. Thank you! :tada:"
                            }
                        }
                    ]
                )
                
                # Notify the payer
                notification_blocks = build_payment_notification_message(expense, debt)
                
                await client.chat_postMessage(
                    channel=payer_id,
                    text=f"<@{debt.debtor_id}> has paid ${debt.amount:,.0f} for {expense.description}",
                    blocks=notification_blocks
                )
                
                # Post an updated summary in the original channel
                blocks = build_expense_summary_message(expense)
                
                # Instead of updating the original message, post a new one
                # This is because the original message might be too old
                await client.chat_postMessage(
                    channel=expense.channel_id,
                    text=f"Payment update for {expense.description}",
                    blocks=blocks
                )
        
        except Exception as e:
            logger.error(f"Error handling payment confirmation: {e}")
            
            # Respond with an error message
            try:
                await client.chat_postEphemeral(
                    channel=body["channel"]["id"],
                    user=body["user"]["id"],
                    text=f"Error confirming payment: {str(e)}"
                )
            except:
                pass  # Ignore errors here 