"""Tiny client for the Google Gemini API using only the Python standard library.

If no API key is set, the app runs in DEMO MODE with built-in sample answers, so
it can still be tried (and tested) without internet or an account.
"""
import json
import os
import time
import urllib.error
import urllib.request

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-3.1-flash-lite"   # override with GEMINI_MODEL if it is retired


class AIError(Exception):
    """Raised for any problem talking to the AI service."""


def load_env(path=".env"):
    """Load KEY=value lines from a .env file into os.environ (if the file exists)."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_api_key():
    return os.environ.get("GEMINI_API_KEY", "").strip()


def is_demo_mode():
    return not get_api_key()


def extract_text(data):
    """Pull the answer text out of a Gemini response dictionary."""
    candidates = data.get("candidates") or []
    if not candidates:
        reason = (data.get("promptFeedback") or {}).get("blockReason", "no answer returned")
        raise AIError(f"The AI returned no answer ({reason}). Try rephrasing.")
    parts = (candidates[0].get("content") or {}).get("parts") or []
    text = "".join(p.get("text", "") for p in parts).strip()
    if not text:
        raise AIError("The AI returned an empty answer. Try again.")
    return text


def _friendly_http_error(code, body):
    if code in (400, 403):
        return "The API rejected the request. Check that GEMINI_API_KEY is correct."
    if code == 404:
        return "Model not found. Set GEMINI_MODEL to a current model name from ai.google.dev."
    if code == 429:
        return "Rate limit reached (free tier). Wait a minute and try again."
    return f"The AI service returned an error (HTTP {code})."


def ask_ai(prompt, system=None, demo=None, timeout=60, retries=2):
    """Send a prompt to Gemini and return the reply text.

    In demo mode (no API key) the `demo` text is returned instead.
    """
    if is_demo_mode():
        return demo or "(Demo mode: set GEMINI_API_KEY to get real AI answers.)"

    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}

    request = urllib.request.Request(
        API_URL.format(model=model),
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": get_api_key()},
        method="POST",
    )

    last_error = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return extract_text(json.loads(response.read().decode("utf-8")))
        except urllib.error.HTTPError as e:
            last_error = AIError(_friendly_http_error(e.code, ""))
            if e.code not in (429, 500, 503) or attempt == retries:
                raise last_error
        except (urllib.error.URLError, TimeoutError):
            last_error = AIError("Could not reach the AI service. Check your internet connection.")
            if attempt == retries:
                raise last_error
        time.sleep(2 * (attempt + 1))
    raise last_error
