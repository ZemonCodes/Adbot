# ══════════════════════════════════════════════════
#   TELEGRAM MULTI-ACCOUNT AD BOT — CONFIG
#   Get API_ID & API_HASH from: https://my.telegram.org
# ══════════════════════════════════════════════════

API_ID   = 12345678
API_HASH = "your_api_hash_here"

# ── Delay Settings ────────────────────────────────
DELAY_MIN   = 120   # Min seconds between each group (2 min)
DELAY_MAX   = 300   # Max seconds between each group (5 min)
CYCLE_DELAY = 1800  # Seconds after full cycle (30 min)

# ══════════════════════════════════════════════════
#   ACCOUNTS — Har account ka alag config
#
#   forward_from   → Jis chat/channel se forward hoga
#   forward_msg_id → Konsa message forward hoga
#                    (Copy Link → t.me/chat/123 → 123)
#
#   Groups formats:
#     "@username"
#     "@username:TOPIC_ID"
#     "-1001234567890"
#     "-1001234567890:TOPIC_ID"
#     "https://t.me/+privateHash"
# ══════════════════════════════════════════════════

ACCOUNTS = [
    {
        "session":        "account1",
        "phone":          "+91XXXXXXXXXX",
        "forward_from":   "@yourchannel1",   # Account 1 ka alag ad
        "forward_msg_id": [123, 124, 125],  # Multiple ads — rotate honge
        "groups": [
            "@group1",
            "@group2:15",
            "-1001234567890",
        ],
    },
    {
        "session":        "account2",
        "phone":          "+91YYYYYYYYYY",
        "forward_from":   "@yourchannel2",   # Account 2 ka alag ad
        "forward_msg_id": [456, 457],     # Multiple ads — rotate honge
        "groups": [
            "@group3",
            "-1009876543210:57",
            "https://t.me/+privateHash",
        ],
    },
]
