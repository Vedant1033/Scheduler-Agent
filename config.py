"""Central configuration for Voice Agent."""

# ── API ──────────────────────────────────────────────────────────────────────
GEMINI_API_URL = "http://192.168.0.89:9004/generate_text_TPA"

# ── STT ──────────────────────────────────────────────────────────────────────
WHISPER_MODEL   = "small"
WHISPER_COMPUTE = "int8"

SUPPORTED_LANGS = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ar": "Arabic",
    "pt": "Portuguese",
}

# ── Mock policy DB (replace with real DB / API) ───────────────────────────────
MOCK_POLICIES = {
    "POL-001": {
        "holder": "Rajesh Kumar",
        "type": "Health Insurance",
        "status": "Active",
        "premium_due": "2025-05-15",
        "coverage": "₹5,00,000",
        "claims_pending": 0,
    },
    "POL-002": {
        "holder": "Priya Sharma",
        "type": "Motor Insurance",
        "status": "Expiring Soon",
        "premium_due": "2025-04-20",
        "coverage": "₹2,00,000",
        "claims_pending": 1,
    },
    "POL-003": {
        "holder": "Amit Joshi",
        "type": "Life Insurance",
        "status": "Lapsed",
        "premium_due": "2025-01-01",
        "coverage": "₹10,00,000",
        "claims_pending": 0,
    },
}
