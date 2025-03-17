# AI-Powered Scheduling Bot

This AI-powered scheduling bot is a *Telegram bot* that automatically finds the best available time slot for meetings between a *candidate and an interviewer. It integrates with **Google Calendar* to check availability and sends a *Google Calendar invite* via Gmail.

## Features
- 📅 *Checks Google Calendar* for busy slots
- 🤖 *AI-powered slot matching* between candidate and interviewer
- 📩 *Sends Google Calendar invites* via Gmail
- 🗓 *Handles all-day events & time zones correctly*

---

## Prerequisites
Ensure you have the following installed:
1. *Python 3.10+* – Download from [python.org](https://www.python.org/downloads/)
2. *Google API Credentials* for Calendar & Gmail (explained below)
3. *A Telegram Bot Token* (generated via BotFather)

---

## 1️⃣ Google API Setup (Calendar & Gmail)
### *Step 1: Enable Google APIs*
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable *Google Calendar API* and *Gmail API*

### *Step 2: Create OAuth Credentials*
1. Navigate to *APIs & Services → Credentials*
2. Click *Create Credentials → OAuth Client ID*
3. Select *Desktop App, then **Create*
4. Download the *credentials.json* file and place it in the project directory

### *Step 3: Authorize Access*
1. Run the bot once to generate token.json
   bash
   python bot.py
   
2. Open the authentication link in your browser
3. Sign in with your Google account & allow permissions
4. Copy and paste the authorization code back into the terminal

---

## 2️⃣ Telegram Bot Setup
### *Step 1: Create a Telegram Bot*
1. Open Telegram and start a chat with *BotFather*
2. Send /newbot and follow the prompts
3. Copy the *bot token* provided

### **Step 2: Add Token to .env**
1. Create a .env file in the project root
2. Add your bot token:
   env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   

---

## 3️⃣ Installation & Running the Bot
### *Step 1: Clone the Repository*
bash
git clone https://github.com/yourusername/ai-scheduling-bot.git
cd ai-scheduling-bot


### *Step 2: Install Dependencies*
bash
pip install -r requirements.txt


### *Step 3: Run the Bot*
bash
python bot.py


If running for the first time, authorize Google Calendar and Gmail as mentioned in *Step 1: Authorize Access* above.

---

## 4️⃣ How to Use the Bot
### *1. Start the Bot*
Open Telegram and **send /start** to your bot.

### *2. Enter Available Time Slots*
Example input:
text
9:00 AM - 10:00 AM
2:00 PM - 3:30 PM


### *3. The Bot Finds the Best Slot*
It checks Google Calendar and finds a free slot.

### *4. Google Calendar Invite Sent!*
If a slot is found, the bot automatically sends a Google Calendar invite to the provided email.

---

## 5️⃣ Troubleshooting
### *1. "No match found" Error*
- Ensure the interviewer has *free time slots* in Google Calendar
- Check if all-day events are blocking availability

### *2. "KeyError: 'dateTime'"*
- Your calendar might contain *all-day events*
- Ensure the code correctly handles event['start'].get('dateTime', event['start'].get('date'))

### *3. Authorization Issues*
- Delete token.json and re-run python bot.py to *re-authenticate*


