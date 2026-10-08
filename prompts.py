"""Prompt templates. Good prompts = clear role, task, format and constraints."""
import json

SYSTEM = (
    "You are a friendly, accurate study tutor for college students. "
    "Use simple language, short paragraphs and concrete examples. "
    "If you are not sure about something, say so instead of guessing."
)


def explain(topic, level):
    return (
        f"Explain '{topic}' for a {level} learner.\n"
        "Format:\n1. One-sentence definition\n2. Simple explanation (max 120 words)\n"
        "3. A real-life example\n4. Three key points as bullets"
    )


def quiz(topic, n):
    return (
        f"Create a {n}-question multiple-choice quiz on '{topic}' for a beginner.\n"
        "Return ONLY valid JSON (no markdown fences, no extra text) as a list of objects:\n"
        '[{"question": "...", "options": ["...", "...", "...", "..."], '
        '"answer": "A", "explanation": "..."}]\n'
        'The "answer" must be one letter: A, B, C or D, matching the position in "options".'
    )


def summarise(text):
    return (
        "Summarise the following study material.\n"
        "Format: a 2-sentence overview, then 5 short bullet points, then 3 exam-style questions.\n\n"
        f"MATERIAL:\n{text}"
    )


def flashcards(topic, n):
    return (
        f"Create {n} flashcards on '{topic}'.\n"
        "Format each as:\nQ: <question>\nA: <short answer>\n"
        "Keep answers under 25 words."
    )


def study_plan(topic, days):
    return (
        f"Create a {days}-day study plan to learn '{topic}' from scratch, about 1 hour per day.\n"
        "For each day give: goal, what to study, and one small practice task."
    )


# ---- built-in answers used in demo mode (no API key) ----
DEMO_EXPLAIN = (
    "[DEMO ANSWER]\n1. Definition: Machine learning lets computers learn patterns from data.\n"
    "2. Explanation: Instead of writing rules by hand, we show the computer many examples "
    "and it works out the rules itself.\n3. Example: A spam filter learns from thousands of "
    "emails marked spam or not spam.\n4. Key points:\n - Needs data\n - Learns patterns\n - Improves with more examples"
)
DEMO_SUMMARY = "[DEMO ANSWER]\nOverview: This is a sample summary.\n- Point 1\n- Point 2\n- Point 3\n- Point 4\n- Point 5"
DEMO_FLASHCARDS = "[DEMO ANSWER]\nQ: What is a variable?\nA: A named place that stores a value.\n\nQ: What is a loop?\nA: Code that repeats until a condition ends it."
DEMO_PLAN = "[DEMO ANSWER]\nDay 1: Basics - read an intro and write notes.\nDay 2: Practice - do 5 small exercises.\nDay 3: Project - build something tiny."
DEMO_QUIZ = json.dumps([
    {"question": "Which keyword defines a function in Python?", "options": ["func", "def", "define", "fun"],
     "answer": "B", "explanation": "Python uses 'def' to define functions."},
    {"question": "Which data type stores True or False?", "options": ["int", "str", "bool", "float"],
     "answer": "C", "explanation": "bool holds True or False."},
    {"question": "What does len([1, 2, 3]) return?", "options": ["2", "3", "4", "1"],
     "answer": "B", "explanation": "The list has 3 items."},
])
