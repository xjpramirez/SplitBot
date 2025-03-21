# SplitBot

A Slack bot designed to simplify group expense splitting after going out with coworkers.

## Features

- Split bill evenly among attendees
- Identify who paid and how much
- Automated messages to attendees about their share
- Payment tracking and confirmation
- Automated reminders for pending payments

## Setup

1. Create a Slack App in the [Slack API Console](https://api.slack.com/apps)
2. Enable Socket Mode and Event Subscriptions
3. Add the following bot scopes:
   - `chat:write`
   - `commands`
   - `users:read`
   - `im:write`
   - `im:history`

4. Install the bot to your workspace
5. Create a `.env` file with the following variables:
   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_APP_TOKEN=xapp-your-app-token
   ```

6. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

7. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

## Usage

### Slash Commands

- `/split total <amount> paid_by <@user1> [<@user2> <amount2>] attendees <@user1> <@user2> ... [note <description>]`
  - Split a bill among attendees

- `/split remind`
  - Send reminders to users who haven't confirmed payment

### Examples

```
/split total 100000 paid_by @jp attendees @jp @ana @nico note Friday drinks 🍻
```

This will:
- Calculate that each person owes $33,333
- Notify @ana and @nico that they each owe $33,333 to @jp
- Track payments until confirmed 