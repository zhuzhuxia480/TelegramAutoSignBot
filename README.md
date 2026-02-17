# 🤖 Telegram Auto Sign

An automated daily sign-in script for Telegram bots, powered by GitHub Actions and Python (Telethon). It uses your personal account (Userbot) to send configurable sign-in commands to specified Telegram bots daily.

## ✨ Core Features
* **☁️ Zero-Cost Deployment**: Runs entirely on GitHub Actions. No need for a local server or VPS.
* **👥 Multi-Bot Support**: Sends sign-in commands to multiple bots sequentially. Each bot can use its own command (e.g. `/qd`, `/sign`) via a single combined `BOT_CONFIG` variable.
* **🎲 Smart Anti-Ban System**: Built-in 1~20 minutes randomized startup delay and random pauses between messages to prevent triggering Telegram's spam filters.
* **📝 Auto-Log Keepalive**: Automatically writes sign-in results to `checkin.log` and pushes it to the repository after each run. This perfectly bypasses GitHub Actions' 60-day inactivity suspension rule.

## 🚀 Deployment Guide

### Step 1: Get API Credentials
1. Log in to the [Telegram API Development Tools](https://my.telegram.org/).
2. Create a new application.
3. Note down your `App api_id` and `App api_hash`.

### Step 2: Get Session String
Install the dependency (`pip install telethon`) on your local machine and run a script to generate your session string. 
> ⚠️ **WARNING**: Treat your Session String like a password. NEVER share it publicly!

### Step 3: Configure GitHub Repository Secrets
1. Create a **Private** repository (Highly recommended for security).
2. Go to `Settings` -> `Secrets and variables` -> `Actions`, and under the **Secrets** tab add:
   * `API_ID`: Your API ID (Numbers only).
   * `API_HASH`: Your API Hash string.
   * `SESSION_STRING`: The extremely long session string generated in Step 2.

### Step 4: Configure GitHub Actions Variables
1. Still under `Settings` -> `Secrets and variables` -> `Actions`, switch to the **Variables** tab.
2. Add a new variable:
   * `BOT_CONFIG`: Mapping of bot usernames and sign-in commands in a single string.

     Format: comma-separated entries, each entry is `bot_username:command`.  
     Examples:
     * `@bot1:/qd,@bot2:/sign`
     * `@bot1:/qd,@bot2:/sign,@bot3`  (bot3 uses default `/qd` since no command is specified)

### Step 5: Grant Action Permissions
To allow the script to push the log file back to the repository:
1. Go to `Settings` -> `Actions` -> `General`.
2. Scroll down to **Workflow permissions**.
3. Select **Read and write permissions** and click `Save`.

### Step 6: First Run & Test
Go to the **Actions** tab, select the `Telegram Auto Sign` workflow on the left, and click `Run workflow` to test it manually. If successful, your account will send the commands, and a log file will appear in your repository!

---

## ⏱️ Schedule Modification
The default trigger time is **00:00 UTC daily**. 
To modify this, edit the cron expression in `.github/workflows/main.yml`.

## 📄 License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## ⚠️ Disclaimer
This script is for educational and automated testing purposes only. Do not use it for high-frequency spamming or violating Telegram's Terms of Service. The user bears all responsibility for any account restrictions or bans caused by API abuse.
