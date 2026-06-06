"""
╔══════════════════════════════════════════════════╗
║   TELEGRAM MULTI-ACCOUNT AD BOT — main.py       ║
║   Channel → Groups Forward | Multi-Account      ║
╚══════════════════════════════════════════════════╝

  pip install telethon
  python main.py
"""

import asyncio
import random
import logging
import sys
from datetime import datetime

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import (
    FloodWaitError,
    ChatWriteForbiddenError,
    UserBannedInChannelError,
    SlowModeWaitError,
    ChannelPrivateError,
    UsernameNotOccupiedError,
    UsernameInvalidError,
    PeerFloodError,
    UserAlreadyParticipantError,
    InviteHashExpiredError,
    InviteHashInvalidError,
)
from config import (
    API_ID, API_HASH,
    DELAY_MIN, DELAY_MAX, CYCLE_DELAY,
    FORWARD_FROM, FORWARD_MSG_ID,
    ACCOUNTS,
)


# ── Logger ────────────────────────────────────────
def make_logger(name: str) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    fmt = logging.Formatter(f"%(asctime)s  [{name}]  %(message)s", datefmt="%H:%M:%S")
    if not log.handlers:
        fh = logging.FileHandler(f"{name}.log", encoding="utf-8")
        fh.setFormatter(fmt)
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        log.addHandler(fh)
        log.addHandler(sh)
    return log


# ── Parse Group Entry ─────────────────────────────
def parse_group(entry: str):
    """Returns (group_id_or_username, topic_id or None)"""
    topic_id = None

    if entry.startswith("-"):
        parts = entry.split(":")
        try:
            group = int(parts[0])
            if len(parts) == 2:
                topic_id = int(parts[1])
            return group, topic_id
        except ValueError:
            pass

    if ":" in entry and not entry.startswith("http"):
        parts = entry.rsplit(":", 1)
        try:
            topic_id = int(parts[1])
            return parts[0], topic_id
        except ValueError:
            pass

    return entry, None


# ── Auto Join Private Group ───────────────────────
async def try_join(client, entry: str, log):
    try:
        if "t.me/+" in entry or "telegram.me/+" in entry:
            hash_ = entry.split("+")[-1].strip("/")
            await client(ImportChatInviteRequest(hash_))
            log.info(f"  ✅  Joined private group")
        else:
            group, _ = parse_group(entry)
            entity = await client.get_entity(group)
            await client(JoinChannelRequest(entity))
            log.info(f"  ✅  Joined: {entry}")
    except UserAlreadyParticipantError:
        pass
    except (InviteHashExpiredError, InviteHashInvalidError):
        log.warning(f"  ❌  Invite expired: {entry}")
    except Exception as e:
        log.warning(f"  ⚠️  Join failed {entry}: {e}")


# ── Forward to One Group ──────────────────────────
async def forward_to_group(client, group_entry: str, source, log) -> bool:
    group, topic_id = parse_group(group_entry)

    try:
        target = await client.get_entity(group)
        await client.forward_messages(
            entity=target,
            messages=FORWARD_MSG_ID,
            from_peer=source,
        )
        label = f"{group_entry}" + (f" [Topic:{topic_id}]" if topic_id else "")
        log.info(f"  ✅  Forwarded  →  {label}")
        return True

    except FloodWaitError as e:
        log.warning(f"  ⏳  FloodWait {e.seconds}s — waiting...")
        await asyncio.sleep(e.seconds + 5)
        try:
            target = await client.get_entity(group)
            await client.forward_messages(entity=target, messages=FORWARD_MSG_ID, from_peer=source)
            log.info(f"  ✅  Forwarded (retry)  →  {group_entry}")
            return True
        except Exception:
            return False

    except PeerFloodError:
        log.warning("  ⚠️  PeerFlood — sleeping 10 min...")
        await asyncio.sleep(600)
        return False

    except SlowModeWaitError as e:
        log.warning(f"  🐢  SlowMode — skipping [{group_entry}]")
        return False

    except (ChatWriteForbiddenError, ChannelPrivateError):
        log.warning(f"  🔒  Access issue — trying to join: {group_entry}")
        await try_join(client, group_entry, log)
        return False

    except UserBannedInChannelError:
        log.warning(f"  🔨  Banned  →  {group_entry}")
        return False

    except (UsernameNotOccupiedError, UsernameInvalidError):
        log.warning(f"  ❓  Invalid  →  {group_entry}")
        return False

    except Exception as e:
        log.error(f"  ❌  {group_entry}: {type(e).__name__}: {e}")
        return False


# ── Single Account Runner ─────────────────────────
async def run_account(account: dict):
    session = account["session"]
    phone   = account["phone"]
    groups  = account["groups"]
    log     = make_logger(session)

    client = TelegramClient(session, API_ID, API_HASH)
    await client.start(phone=phone)

    me = await client.get_me()
    log.info(f"\n{'═'*55}")
    log.info(f"  🚀  Account: {me.first_name} (@{me.username})")
    log.info(f"  📨  Forwarding msg #{FORWARD_MSG_ID} from {FORWARD_FROM}")
    log.info(f"  👥  Groups: {len(groups)}")
    log.info(f"  ⏱   Delay: {DELAY_MIN}s–{DELAY_MAX}s | Cycle cooldown: {CYCLE_DELAY}s")
    log.info(f"{'═'*55}\n")

    # Resolve source channel once
    try:
        source = await client.get_entity(FORWARD_FROM)
    except Exception as e:
        log.error(f"  ❌  Cannot find source channel '{FORWARD_FROM}': {e}")
        return

    cycle = 1
    while True:
        sent = failed = 0
        log.info(f"┌── CYCLE {cycle}  |  {datetime.now().strftime('%d %b, %I:%M %p')}  |  {len(groups)} groups")

        for i, group_entry in enumerate(groups, 1):
            log.info(f"│  [{i}/{len(groups)}]  →  {group_entry}")
            ok = await forward_to_group(client, group_entry, source, log)
            sent += ok
            failed += not ok

            if i < len(groups):
                delay = random.randint(DELAY_MIN, DELAY_MAX)
                log.info(f"│  ⏱  Next in {delay}s...")
                await asyncio.sleep(delay)

        log.info(f"└── CYCLE {cycle} DONE  |  ✅ {sent}  ❌ {failed}")
        log.info(f"    💤  Sleeping {CYCLE_DELAY}s...\n")
        cycle += 1
        await asyncio.sleep(CYCLE_DELAY)


# ── Main ──────────────────────────────────────────
async def main():
    if not ACCOUNTS:
        print("❌ ACCOUNTS empty hai config.py mein!")
        return
    print(f"\n🚀 {len(ACCOUNTS)} account(s) simultaneously start ho rahe hain...\n")
    await asyncio.gather(*[run_account(acc) for acc in ACCOUNTS])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")
