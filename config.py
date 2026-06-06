# ══════════════════════════════════════════════════
#   TELEGRAM MULTI-ACCOUNT AD BOT — CONFIG
#   Get API_ID & API_HASH from: https://my.telegram.org
# ══════════════════════════════════════════════════

API_ID   = 31857751
API_HASH = "8a661cf5c52ac0c17d66264d6693c7d4"

# ── Delay Settings ────────────────────────────────
DELAY_MIN   = 120   # Min seconds between each group (2 min)
DELAY_MAX   = 250   # Max seconds between each group (5 min)
CYCLE_DELAY = 900  # Seconds after full cycle (30 min)

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
        "session":        "whyzemom",
        "phone":          "+13209613081",
        "forward_from":   "@zemonserves",   # Account 1 ka alag ad
        "forward_msg_id": [4, 5],  # Multiple ads — rotate honge
        "groups": [
            "@foruming:15",
            "@marketogs:127871",
            "@texted:24",
            "@celismarket:92",
            "@useanmm8266",
            "@sectormarket:24",
            "@porkmarket:15",
            "@credibles:2",
            "-1003594189213:17",
        ],
    },
    {
        "session":        "Cursedzemon",
        "phone":          "+15858332363",
        "forward_from":   "@zemonserves",   # Account 2 ka alag ad
        "forward_msg_id": [4, 5],     # Multiple ads — rotate honge
        "groups": [
            "@foruming:15",
            "@marketogs:127871",
            "@texted:24",
            "@celismarket:92",
            "@useanmm8266",
            "@sectormarket:24",
            "@porkmarket:15",
            "@credibles:2",
            "-1003594189213:17",
        ],
    },
]
