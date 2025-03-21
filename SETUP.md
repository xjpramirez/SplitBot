# SplitBot Setup Guide

This guide will walk you through setting up SplitBot for your Slack workspace.

## Prerequisites

- Python 3.8 or higher
- A Slack workspace where you have permissions to add apps
- pip for installing Python packages

## Step 1: Create a Slack App

1. Go to [Slack API Apps page](https://api.slack.com/apps) and sign in with your Slack account.
2. Click on "Create New App" and select "From scratch".
3. Enter "SplitBot" as the app name and select your workspace.
4. Click "Create App".

## Step 2: Configure Bot Scopes

1. In the left sidebar, click on "OAuth & Permissions".
2. Scroll down to "Scopes" section and add the following Bot Token Scopes:
   - `chat:write` (Send messages as the app)
   - `commands` (Add slash commands)
   - `users:read` (View users in the workspace)
   - `im:write` (Start direct messages with users)
   - `im:history` (View messages in direct messages)

## Step 3: Create a Slash Command

1. In the left sidebar, click on "Slash Commands".
2. Click "Create New Command".
3. Fill in the details:
   - Command: `/split`
   - Short Description: "Split expenses with your team"
   - Usage Hint: "total [amount] paid_by [@user] attendees [@user1 @user2...] note [description]"
   - Escape channels, users, and links: Check this box
4. Click "Save".

## Step 4: Set up Interactivity

1. In the left sidebar, click on "Interactivity & Shortcuts".
2. Toggle "Interactivity" to On.
3. Set the Request URL to your server URL + "/slack/events" (e.g., `https://your-server.com/slack/events`).
   - If you're running locally, you'll need to use a tool like ngrok to expose your local server to the internet.
4. Click "Save Changes".

## Step 5: Install the App to Your Workspace

1. In the left sidebar, click on "Install App".
2. Click "Install to Workspace".
3. Review the permissions and click "Allow".
4. Copy the Bot User OAuth Token (starts with `xoxb-`).

## Step 6: Set Up Environment Variables

1. Copy the `.env.example` file to `.env`:
   ```
   cp .env.example .env
   ```
2. Edit the `.env` file and fill in the values:
   - `SLACK_BOT_TOKEN`: The Bot User OAuth Token you copied in Step 5
   - `SLACK_SIGNING_SECRET`: Found under "Basic Information" > "App Credentials" > "Signing Secret"

## Step 7: Install Dependencies and Run

1. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
2. Start the server:
   ```
   uvicorn app.main:app --reload
   ```

## Step 8: Test the Bot

1. In Slack, go to any channel where the bot is present.
2. Try out the `/split` command:
   ```
   /split total 100000 paid_by @jp attendees @jp @ana @nico note Friday drinks 🍻
   ```
3. The bot should respond with a breakdown of who owes what to whom.

## Common Issues

- **Command Not Found**: Make sure the slash command is properly configured and the app is installed to your workspace.
- **Bot Not Responding**: Check that your server is running and the Request URL is correctly set up.
- **Permission Errors**: Ensure that all required scopes are added to the bot.

## Using the Bot

- **Split a Bill**: Use the `/split` command with the syntax shown in Step 8.
- **Send Reminders**: Use `/split remind` to send reminders to users who haven't paid yet.
- **Payment Confirmation**: When users click the "Yes, I've paid" button, the bot will update the payment status and notify the payer. 