# ══════════════════════════════════════════════════
#   TELEGRAM MULTI-ACCOUNT AD BOT — CONFIG
#   Get API_ID & API_HASH from: https://my.telegram.org
# ══════════════════════════════════════════════════

API_ID   = 12345678
API_HASH = "your_api_hash_here"

# ── Delay Settings ────────────────────────────────
DELAY_MIN   = 120   # Min seconds between groups (2 min)
DELAY_MAX   = 300   # Max seconds between groups (5 min)
CYCLE_DELAY = 1800  # Seconds after full cycle (30 min)

# ── Forward Settings (Global) ─────────────────────
# Jis channel/chat ka message forward karna hai
FORWARD_FROM   = "@yourchannel"  # Channel username ya ID
FORWARD_MSG_ID = 123             # Message ID
# Message ID kaise pata kare:
#   Message pe right-click → Copy Link
#   https://t.me/channelname/123 → 123 hai ID

# ── Accounts ─────────────────────────────────────
# Har account ke sirf phone, session, aur groups
# Groups formats:
#   "@username"
#   "@username:TOPIC_ID"
#   "-1001234567890"
#   "-1001234567890:TOPIC_ID"
#   "https://t.me/+privateInviteHash"

ACCOUNTS = [
    {
        "session": "account1",
        "phone":   "+91XXXXXXXXXX",
        "groups": [
            "@examplegroup1",
            "@examplegroup2:57",
            "-1001234567890",
            "https://t.me/+privateHash1",
        ],
    },
    {
        "session": "account2",
        "phone":   "+91YYYYYYYYYY",
        "groups": [
            "@anothergroup1",
            "-1009876543210:12",
            "https://t.me/+privateHash2",
        ],
    },
    # Aur accounts add karo same format mein...
]
