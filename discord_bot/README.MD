# Scanlation System Discord Bot
This is a Discord bot designed to facilitate the operations of your team on Discord. 
You can perform tasks related to chapters through the bot, view your current tasks, 
track progress, and benefit from various other features.

## Features:
1. Various fun commands such as animal photos, beer recommendation or anime quotes etc.
2. Open, close, delete chapters or look into details.
3. Enter your works to the bot (with `/translate`, `/ts` etc.) and track them in the bot using your main API. Calculate all the works you have done
   and your monthly (periodically) salary. Admins can extract a month's payroll into an excel file. You can see your own
   work. 
4. See your remaining works. Never forget any chapter that you work on.
5. Inspect a channel's serie with details or payments!
6. Create, detele or update payment periods!
7. Track whole team's work daily! Or you can just type `/daily` to see all works instantly.
8. Automatically track new chapters from main API and send notifications to serie's dedicated channels!
9. Warn your team members who have overdue chapters!

## How To Use
1. Install Python 3.11 or higher.
2. Create a virtual environment.
    ```bash
   # On Linux and Mac:
   cd project_dir
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install requirements.
   ```bash
   # On Linux and Mac:
   pip3 install -r requirements.txt
   ```
4. Edit `config.json` file to your preferences.
5. Edit `payment.py` file to your preferences.
6. Start the bot.
   ```bash
   python3 main.py
   ```