import os
import asyncio
import random
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient
from telethon.sessions import StringSession

# Load credentials and bot configuration from environment
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]
# Combined mapping of bot usernames and commands, e.g. "@bot1:/qd,@bot2:/sign,@bot3"
BOT_CONFIG_RAW = os.environ.get("BOT_CONFIG", "").strip()


def _normalize_command(cmd: str) -> str:
    """Ensure command has leading slash for Telegram."""
    cmd = (cmd or "").strip()
    if not cmd:
        return "/qd"
    return cmd if cmd.startswith("/") else f"/{cmd}"


def get_bot_command_list() -> list[tuple[str, str]]:
    """
    Build (bot_username, command) pairs from BOT_CONFIG.

    BOT_CONFIG example: "@bot1:/qd,@bot2:/sign,@bot3"
    - Each entry: "bot_username:command"
    - If command is omitted, default "/qd" is used.
    """
    result: list[tuple[str, str]] = []

    if not BOT_CONFIG_RAW:
        return result

    entries = [e.strip() for e in BOT_CONFIG_RAW.split(",") if e.strip()]
    for entry in entries:
        if ":" in entry:
            bot, cmd_raw = entry.split(":", 1)
        else:
            bot, cmd_raw = entry, "qd"
        bot = bot.strip()
        if not bot:
            continue
        cmd = _normalize_command(cmd_raw)
        result.append((bot, cmd))

    return result


async def main():
    # Random startup delay to mimic human behavior and reduce spam risk
    delay_seconds = random.randint(60, 300)
    await asyncio.sleep(delay_seconds)

    print("Connecting to Telegram...")
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    print("Logged in.\n")

    bot_command_list = get_bot_command_list()
    success_bots = []

    for bot_username, sign_cmd in bot_command_list:
        print(f"Sending sign command '{sign_cmd}' to {bot_username}...")
        await client.send_message(bot_username, sign_cmd)
        success_bots.append(f"{bot_username}({sign_cmd})")

        sleep_time = random.randint(2, 5)
        await asyncio.sleep(sleep_time)

    print("\nAll sign commands sent.")
    await client.disconnect()

    tz = timezone(timedelta(hours=8))
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    log_msg = (
        f"[{current_time}] Sent sign commands to {', '.join(success_bots)} "
        f"(start delay: {delay_seconds}s).\n"
    )
    with open("checkin.log", "a", encoding="utf-8") as f:
        f.write(log_msg)
    print("Log written to checkin.log")


if __name__ == "__main__":
    asyncio.run(main())
