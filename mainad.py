"""
╔══════════════════════════════════════════════════╗
║   TELEGRAM MULTI-ACCOUNT AD BOT — mainad.py     ║
║   Per-Account Ads | Multi-Ad Rotation | Topics  ║
╚══════════════════════════════════════════════════╝

  pip install telethon
  python mainad.py
"""

import asyncio
import random
import logging
import sys
from datetime import datetime

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, ForwardMessagesRequest
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
from config import API_ID, API_HASH, DELAY_MIN, DELAY_MAX, CYCLE_DELAY, ACCOUNTS


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


# ── Auto Join ─────────────────────────────────────
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
async def forward_to_group(client, group_entry: str, source, msg_id: int, log) -> bool:
    group, topic_id = parse_group(group_entry)
    label = group_entry + (f" [Topic:{topic_id}]" if topic_id else "")

    try:
        target = await client.get_entity(group)

        if topic_id:
            await client(ForwardMessagesRequest(
                from_peer=source,
                id=[msg_id],
                to_peer=target,
                top_msg_id=topic_id,
                random_id=[random.randint(0, 2**63 - 1)],
                silent=False,
            ))
        else:
            await client.forward_messages(
                entity=target,
                messages=msg_id,
                from_peer=source,
            )

        log.info(f"  ✅  Forwarded (msg #{msg_id})  →  {label}")
        return True

    except FloodWaitError as e:
        log.warning(f"  ⏳  FloodWait {e.seconds}s — waiting...")
        await asyncio.sleep(e.seconds + 5)
        try:
            target = await client.get_entity(group)
            if topic_id:
                await client(ForwardMessagesRequest(
                    from_peer=source, id=[msg_id], to_peer=target,
                    top_msg_id=topic_id, random_id=[random.randint(0, 2**63 - 1)],
                ))
            else:
                await client.forward_messages(entity=target, messages=msg_id, from_peer=source)
            log.info(f"  ✅  Forwarded (retry)  →  {label}")
            return True
        except Exception:
            return False

    except PeerFloodError:
        log.warning("  ⚠️  PeerFlood — sleeping 10 min...")
        await asyncio.sleep(600)
        return False

    except SlowModeWaitError:
        log.warning(f"  🐢  SlowMode — skipping [{label}]")
        return False

    except (ChatWriteForbiddenError, ChannelPrivateError):
        log.warning(f"  🔒  Access issue — trying to join: {label}")
        await try_join(client, group_entry, log)
        return False

    except UserBannedInChannelError:
        log.warning(f"  🔨  Banned  →  {label}")
        return False

    except (UsernameNotOccupiedError, UsernameInvalidError):
        log.warning(f"  ❓  Invalid  →  {label}")
        return False

    except Exception as e:
        log.error(f"  ❌  {label}: {type(e).__name__}: {e}")
        return False


# ── Single Account Runner ─────────────────────────
async def run_account(account: dict):
    session    = account["session"]
    phone      = account["phone"]
    fwd_from   = account["forward_from"]
    groups     = account["groups"]
    log        = make_logger(session)

    # forward_msg_id — int ya list dono support
    raw_ids = account["forward_msg_id"]
    msg_ids = raw_ids if isinstance(raw_ids, list) else [raw_ids]

    client = TelegramClient(session, API_ID, API_HASH)
    await client.start(phone=phone)

    me = await client.get_me()
    log.info(f"\n{'═'*55}")
    uname = f"@{me.username}" if me.username else f"id:{me.id}"
    log.info(f"  🚀  Account : {me.first_name} ({uname})")
    log.info(f"  📨  Ads     : {len(msg_ids)} message(s) from {fwd_from}")
    log.info(f"  👥  Groups  : {len(groups)}")
    log.info(f"  ⏱   Delay   : {DELAY_MIN}s–{DELAY_MAX}s | Cycle: {CYCLE_DELAY}s")
    log.info(f"{'═'*55}\n")

    try:
        source = await client.get_entity(fwd_from)
    except Exception as e:
        log.error(f"  ❌  Source resolve nahi hua '{fwd_from}': {e}")
        return

    cycle = 1
    ad_index = 0  # global rotation counter across cycles

    while True:
        sent = failed = 0
        log.info(f"┌── CYCLE {cycle}  |  {datetime.now().strftime('%d %b, %I:%M %p')}  |  {len(groups)} groups")

        for i, group_entry in enumerate(groups, 1):
            # Rotate through msg_ids per group
            msg_id = msg_ids[ad_index % len(msg_ids)]
            ad_index += 1

            log.info(f"│  [{i}/{len(groups)}] Ad #{(ad_index-1) % len(msg_ids) + 1}/{len(msg_ids)}  →  {group_entry}")
            ok = await forward_to_group(client, group_entry, source, msg_id, log)
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
    print(f"\n🚀 {len(ACCOUNTS)} account(s) start ho rahe hain...\n")
    await asyncio.gather(*[run_account(acc) for acc in ACCOUNTS])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")
