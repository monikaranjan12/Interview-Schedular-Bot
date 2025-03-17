import logging
import datetime
import json
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler

import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
)
from telegram import Update
import datetime

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define Gmail API scopes
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def authenticate_gmail():
    """Authenticate and return Gmail service."""
    creds = None
    if os.path.exists("token_gmail.json"):
        creds = Credentials.from_authorized_user_file("token_gmail.json", GMAIL_SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", GMAIL_SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token_gmail.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

gmail_service = authenticate_gmail()

# Define conversation states
ENTER_SLOTS, ENTER_DATE, ENTER_EMAIL = range(3)


BOT_TOKEN = "7601448793:AAG_NnNO0QdNmD4hw_fll64EXnGkF6NLuN4"

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

# Define a global vectorizer
vectorizer = CountVectorizer()

def encode_time_slot(slots):
    """Convert time slots into a consistent numerical representation for ML matching."""
    return vectorizer.transform(slots).toarray()  # Ensure same vocab for all slots

def find_best_slot(user_slots):
    """Find the best matching slot using ML similarity scoring."""
    now = datetime.datetime.utcnow().isoformat() + "Z"

    events_result = calendar_service.events().list(
        calendarId="primary", timeMin=now, maxResults=10, singleEvents=True, orderBy="startTime"
    ).execute()
    
    busy_slots = []
    
    for event in events_result.get("items", []):
        start = event["start"].get("dateTime", event["start"].get("date"))  # Use date if dateTime is missing
        end = event["end"].get("dateTime", event["end"].get("date"))
        busy_slots.append((start, end))

    print("🚀 Debug: Busy Slots ->", busy_slots)  # 🛠 Check what slots are being marked as busy
    print("🚀 Debug: User Slots ->", user_slots)  # 🛠 Check what user provided slots

    best_match = None
    for user_slot in user_slots:
        user_start, user_end = user_slot.split("-")
        user_start = user_start.strip()
        user_end = user_end.strip()

        # Check if the user slot overlaps with any busy slot
        slot_free = True
        for start, end in busy_slots:
            if start and end:  # Ensure the slots exist
                if not (user_end <= start or user_start >= end):  # Overlapping condition
                    slot_free = False
                    break

        if slot_free:
            best_match = user_slot
            break  # Stop after finding the first available slot

    print(f"🚀 Debug: Best Match Found -> {best_match}")  # 🛠 Debug final selected slot

    return best_match


def authenticate_google():
    """Authenticate and return Google Calendar service."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

calendar_service = authenticate_google()

def find_available_slot(user_slot):
    """Check if the interviewer's calendar has a matching free slot."""
    now = datetime.datetime.utcnow().isoformat() + "Z"
    
    events_result = calendar_service.events().list(
        calendarId="primary", timeMin=now, maxResults=10, singleEvents=True, orderBy="startTime"
    ).execute()
    
    busy_slots = [(event["start"]["dateTime"], event["end"]["dateTime"]) for event in events_result.get("items", [])]

    user_start, user_end = user_slot.split("-")
    user_start = datetime.datetime.strptime(user_start.strip(), "%I:%M %p").isoformat()
    user_end = datetime.datetime.strptime(user_end.strip(), "%I:%M %p").isoformat()

    for start, end in busy_slots:
        if not (user_end <= start or user_start >= end):  # Overlapping slot found
            return None
    return user_slot

def create_calendar_event(best_match, user_date, user_email):
    """Create a Google Calendar event and send an invite via Gmail."""

    start_time, end_time = best_match.split("-")
    start_dt = f"{user_date}T{datetime.datetime.strptime(start_time.strip(), '%I:%M %p').time().isoformat()}"
    end_dt = f"{user_date}T{datetime.datetime.strptime(end_time.strip(), '%I:%M %p').time().isoformat()}"

    event = {
        "summary": "Interview Schedule",
        "location": "Google Meet",
        "description": "Your interview has been scheduled.",
        "start": {"dateTime": start_dt, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_dt, "timeZone": "Asia/Kolkata"},
        "attendees": [{"email": user_email}],
    }

    event_result = calendar_service.events().insert(
        calendarId="primary",
        body=event,
        sendUpdates="all"  # Auto-send Calendar Invite
    ).execute()

    # Send Gmail Notification
    send_email_notification(user_email, event_result)

    return event_result
def send_email_notification(user_email, event_result):
    """Send a Gmail email notification with event details."""
    subject = "Your Interview is Scheduled"
    body = f"""
    Hello,

    Your interview has been successfully scheduled.

    📅 Date: {event_result['start']['dateTime'][:10]}
    ⏰ Time: {event_result['start']['dateTime'][11:16]} - {event_result['end']['dateTime'][11:16]}
    📍 Location: {event_result.get('location', 'Google Meet')}
    🔗 Event Link: {event_result['htmlLink']}

    Please check your Google Calendar for details.

    Regards,
    Interview Bot
    """

    message = MIMEMultipart()
    message["to"] = user_email
    message["subject"] = subject
    message.attach(MIMEText(body, "plain"))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        gmail_service.users().messages().send(
            userId="me",
            body={"raw": raw_message}
        ).execute()
        print(f"✅ Email sent to {user_email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")



async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! Send your available slots (e.g., 10:00 AM - 12:00 PM)")

async def receive_email(update: Update, context: CallbackContext) -> int:
    """Step 4: Store email, match slot, and schedule the event."""
    user_email = update.message.text.strip()

    if "@" not in user_email:  # Validate email
        await update.message.reply_text("Invalid email! Please enter a valid Gmail address.")
        return ENTER_EMAIL  # Stay in email step if input is incorrect

    user_slots = context.user_data["slots"]
    user_date = context.user_data.get("date")

    best_match = find_best_slot(user_slots)  # Match slot with interviewer availability

    if best_match:
        event = create_calendar_event(best_match, user_date, user_email)
        await update.message.reply_text(
            f"Meeting scheduled on {user_date} at {best_match}!\nGoogle Calendar Event: {event['htmlLink']}"
        )
        return ConversationHandler.END  # End the conversation
    else:
        await update.message.reply_text("No matching slot found. Please restart the process.")
        return ConversationHandler.END




async def receive_date(update: Update, context: CallbackContext) -> int:
    """Step 3: Store the date and ask for the email."""
    user_date = update.message.text.strip()

    # Validate date format
    try:
        datetime.datetime.strptime(user_date, "%Y-%m-%d")
    except ValueError:
        await update.message.reply_text("Invalid date format! Please enter in YYYY-MM-DD format.")
        return ENTER_DATE  # Stay in date step if input is incorrect

    context.user_data["date"] = user_date  # Save the date
    await update.message.reply_text("Great! Now, please enter your Gmail ID to receive the invite.")
    return ENTER_EMAIL  # Move to the next step


async def receive_slots(update: Update, context: CallbackContext) -> int:
    """Step 2: Store time slots and ask for the date."""
    context.user_data["slots"] = update.message.text.split(",")  # Store time slots

    await update.message.reply_text("Got it! Now, please enter the date (YYYY-MM-DD) for the interview:")
    return ENTER_DATE  # Move to the next step


async def receive_availability(update: Update, context: CallbackContext) -> int:
    """Step 1: Ask user for available time slots."""
    await update.message.reply_text(
        "Please enter your available time slots (e.g., '9:00 AM - 10:00 AM, 2:00 PM - 3:00 PM'):"
    )
    return ENTER_SLOTS  # Move to the slot entry step



async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm":
        await query.edit_message_text("Schedule confirmed!")
    else:
        await query.edit_message_text("Schedule cancelled.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", receive_availability)],  # Start by asking for slots
        states={
            ENTER_SLOTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_slots)],  # Step 1: Time Slots
            ENTER_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_date)],  # Step 2: Date
            ENTER_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)],  # Step 3: Email
        },
        fallbacks=[CommandHandler("start", receive_availability)],  # Restart if needed
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()

