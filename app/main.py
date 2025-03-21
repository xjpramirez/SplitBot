import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, BackgroundTasks
from slack_bolt import App as SlackApp
from slack_bolt.adapter.fastapi import SlackRequestHandler
from app.routes import slack_commands
from app.services.reminder_service import ReminderService

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="SplitBot", description="A Slack bot for splitting expenses")

# Initialize Slack app
slack_app = SlackApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Initialize the reminder service
reminder_service = ReminderService(slack_app)

# Register the slash command handlers
slack_commands.register_commands(slack_app, reminder_service)

# Create a SlackRequestHandler for handling Slack events via FastAPI
handler = SlackRequestHandler(slack_app)

@app.post("/slack/events")
async def slack_events(request: Request, background_tasks: BackgroundTasks):
    """Endpoint for handling Slack events and interactions."""
    return await handler.handle(request)

@app.post("/slack/commands")
async def slack_commands_endpoint(request: Request, background_tasks: BackgroundTasks):
    """Endpoint for handling Slack slash commands."""
    # Process the command in the background so we can respond quickly to Slack
    return await handler.handle(request)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# Start background task for sending reminders
@app.on_event("startup")
async def startup_event():
    """Start the reminder service on application startup."""
    background_tasks = BackgroundTasks()
    background_tasks.add_task(reminder_service.start_reminder_scheduler)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 