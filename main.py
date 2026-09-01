import os
import asyncio
import random
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional

from telethon import TelegramClient
from telethon.sessions import StringSession

# Load credentials and bot configuration from environment
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]
BOT_CONFIG_RAW = os.environ.get("BOT_CONFIG", "").strip()


@dataclass(frozen=True)
class BotConfig:
    bot_username: str
    command: str
    button_text: Optional[str] = None


def _resolve_command(cmd: str) -> str:
    """Use the configured command as-is, defaulting to '/qd' when omitted."""
    cmd = (cmd or "").strip()
    return cmd or "/qd"


def parse_bot_config(raw: str) -> list[BotConfig]:
    """
    Parse BOT_CONFIG.

    Backward-compatible examples:
      @bot1:/qd,@bot2:sign,@bot3

    Button-click example:
      @okemby_bot:/start|button=签到
    """
    result: list[BotConfig] = []
    if not raw:
        return result

    for entry in [e.strip() for e in raw.split(",") if e.strip()]:
        if ":" in entry:
            bot, action_raw = entry.split(":", 1)
        else:
            bot, action_raw = entry, ""

        bot = bot.strip()
        if not bot:
            continue

        parts = [p.strip() for p in action_raw.split("|")]
        command = _resolve_command(parts[0] if parts else "")
        button_text: Optional[str] = None

        for option in parts[1:]:
            key, sep, value = option.partition("=")
            if sep and key.strip().lower() == "button":
                value = value.strip()
                if value:
                    button_text = value

        result.append(BotConfig(bot, command, button_text))

    return result


def get_bot_command_list() -> list[BotConfig]:
    return parse_bot_config(BOT_CONFIG_RAW)


def button_matches(actual_text: str, expected_text: str) -> bool:
    """Match by substring so labels such as '🎯 签到' match '签到'."""
    return expected_text.strip() in (actual_text or "")


async def click_matching_button(client, bot_username: str, expected_text: str) -> Optional[str]:
    """Find the newest inline keyboard containing expected_text and click it."""
    messages = await client.get_messages(bot_username, limit=5)

    for message in messages:
        if not getattr(message, "buttons", None):
            continue

        for row in message.buttons:
            for button in row:
                text = getattr(button, "text", "") or ""
                if button_matches(text, expected_text):
                    await button.click()
                    return text

    return None


async def latest_bot_text(client, bot_username: str) -> str:
    messages = await client.get_messages(bot_username, limit=1)
    if not messages:
        return ""
    return (getattr(messages[0], "text", "") or "").strip()


async def process_bot(client, config: BotConfig) -> tuple[bool, str]:
    print(f"Sending '{config.command}' to {config.bot_username}...")
    await client.send_message(config.bot_username, config.command)

    if not config.button_text:
        return True, f"command sent: {config.command}"

    # Wait for the bot to render/update its inline keyboard.
    await asyncio.sleep(random.randint(2, 4))

    clicked_text = await click_matching_button(
        client, config.bot_username, config.button_text
    )
    if not clicked_text:
        return False, f"button not found: {config.button_text}"

    print(f"Clicked button '{clicked_text}' on {config.bot_username}.")

    # Callback buttons may send a new message or edit the current one.
    await asyncio.sleep(random.randint(2, 4))
    result_text = await latest_bot_text(client, config.bot_username)
    if result_text:
        print(f"Latest bot response from {config.bot_username}:\n{result_text}\n")

    return True, f"clicked: {clicked_text}"


async def main():
    # Random startup delay to mimic human behavior and reduce spam risk.
    # Set START_DELAY_MAX=0 for manual debugging if desired.
    start_delay_max = max(0, int(os.environ.get("START_DELAY_MAX", "300")))
    delay_seconds = random.randint(0 if start_delay_max == 0 else 60, start_delay_max) if start_delay_max else 0
    if delay_seconds:
        print(f"Random startup delay: {delay_seconds}s")
        await asyncio.sleep(delay_seconds)

    print("Connecting to Telegram...")
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    print("Logged in.\n")

    configs = get_bot_command_list()
    if not configs:
        raise RuntimeError("BOT_CONFIG is empty. Nothing to sign in.")

    results: list[str] = []
    has_failure = False

    try:
        for config in configs:
            try:
                ok, detail = await process_bot(client, config)
                status = "OK" if ok else "FAILED"
                results.append(f"{config.bot_username}: {status} ({detail})")
                has_failure = has_failure or not ok
            except Exception as exc:
                has_failure = True
                detail = f"{type(exc).__name__}: {exc}"
                results.append(f"{config.bot_username}: FAILED ({detail})")
                print(f"Error processing {config.bot_username}: {detail}")

            await asyncio.sleep(random.randint(2, 5))
    finally:
        await client.disconnect()

    tz = timezone(timedelta(hours=8))
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{current_time}] " + " | ".join(results) + f" (start delay: {delay_seconds}s).\n"

    with open("checkin.log", "a", encoding="utf-8") as f:
        f.write(log_msg)

    print("\n" + "\n".join(results))
    print("Log written to checkin.log")

    if has_failure:
        raise RuntimeError("One or more bots failed to sign in; see log above.")


if __name__ == "__main__":
    asyncio.run(main())
