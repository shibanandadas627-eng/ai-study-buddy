"""AI Study Buddy - a command-line study assistant powered by a Gemini AI model.

Features: explain a concept, take an AI-generated quiz (graded by the program),
summarise notes, make flashcards, build a study plan, and save answers to a file.
"""
import json
import re
from datetime import datetime

import prompts
from ai_client import AIError, ask_ai, is_demo_mode, load_env

NOTES_FILE = "study_notes.md"
LEVELS = {"1": "complete beginner", "2": "school-level", "3": "college-level"}


# ---------- logic that can be tested without the AI ----------
def parse_quiz(text):
    """Turn the AI's JSON reply into a validated list of questions."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        items = json.loads(cleaned)
    except json.JSONDecodeError:
        raise AIError("The AI did not return a valid quiz. Please try again.")
    if not isinstance(items, list) or not items:
        raise AIError("The quiz was empty. Please try again.")
    quiz = []
    for item in items:
        options = item.get("options", [])
        answer = str(item.get("answer", "")).strip().upper()[:1]
        if (not item.get("question") or len(options) != 4
                or answer not in "ABCD" or not answer):
            continue  # skip malformed questions
        quiz.append({"question": item["question"], "options": options,
                     "answer": answer, "explanation": item.get("explanation", "")})
    if not quiz:
        raise AIError("No usable quiz questions were returned. Please try again.")
    return quiz


def grade(quiz, user_answers):
    """Return the number of correct answers."""
    return sum(1 for q, a in zip(quiz, user_answers) if a.upper() == q["answer"])


def save_note(title, content, path=NOTES_FILE):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n## {title} ({stamp})\n\n{content}\n")
    return path


# ---------- terminal helpers ----------
def ask_number(label, default, low, high):
    raw = input(f"{label} [{default}]: ").strip()
    if not raw:
        return default
    if raw.isdigit() and low <= int(raw) <= high:
        return int(raw)
    print(f"Using default {default}.")
    return default


def read_multiline():
    print("Paste your text. Type END on a new line when finished:")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def run_quiz(topic, n):
    reply = ask_ai(prompts.quiz(topic, n), system=prompts.SYSTEM, demo=prompts.DEMO_QUIZ)
    quiz = parse_quiz(reply)
    answers = []
    for i, q in enumerate(quiz, 1):
        print(f"\nQ{i}. {q['question']}")
        for letter, option in zip("ABCD", q["options"]):
            print(f"   {letter}. {option}")
        while True:
            a = input("Your answer (A/B/C/D): ").strip().upper()
            if a in ("A", "B", "C", "D"):
                break
            print("Please type A, B, C or D.")
        answers.append(a)
        print("Correct!" if a == q["answer"] else f"Not quite. Answer: {q['answer']}.")
        if q["explanation"]:
            print("Why:", q["explanation"])
    score = grade(quiz, answers)
    print(f"\nScore: {score}/{len(quiz)} ({score / len(quiz) * 100:.0f}%)")
    return f"Quiz on {topic}: {score}/{len(quiz)}"


MENU = """
====== AI STUDY BUDDY ======
1. Explain a concept
2. Quiz me
3. Summarise my notes
4. Make flashcards
5. Make a study plan
6. Save last answer to notes
0. Exit
"""


def main():
    load_env()
    print("AI Study Buddy" + ("  [DEMO MODE: no API key found, using sample answers]" if is_demo_mode() else ""))
    last_title, last_answer = None, None

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                topic = input("Topic: ").strip()
                print("Level: 1) complete beginner  2) school-level  3) college-level")
                level = LEVELS.get(input("Choose [1]: ").strip() or "1", LEVELS["1"])
                last_answer = ask_ai(prompts.explain(topic, level), system=prompts.SYSTEM, demo=prompts.DEMO_EXPLAIN)
                last_title = f"Explanation: {topic}"
                print("\n" + last_answer)
            elif choice == "2":
                topic = input("Quiz topic: ").strip()
                n = ask_number("Number of questions", 3, 1, 10)
                last_answer = run_quiz(topic, n)
                last_title = f"Quiz result: {topic}"
            elif choice == "3":
                text = read_multiline()
                if not text:
                    print("Nothing to summarise.")
                    continue
                last_answer = ask_ai(prompts.summarise(text), system=prompts.SYSTEM, demo=prompts.DEMO_SUMMARY)
                last_title = "Summary"
                print("\n" + last_answer)
            elif choice == "4":
                topic = input("Topic: ").strip()
                n = ask_number("Number of flashcards", 5, 1, 15)
                last_answer = ask_ai(prompts.flashcards(topic, n), system=prompts.SYSTEM, demo=prompts.DEMO_FLASHCARDS)
                last_title = f"Flashcards: {topic}"
                print("\n" + last_answer)
            elif choice == "5":
                topic = input("What do you want to learn? ").strip()
                days = ask_number("Number of days", 7, 1, 30)
                last_answer = ask_ai(prompts.study_plan(topic, days), system=prompts.SYSTEM, demo=prompts.DEMO_PLAN)
                last_title = f"Study plan: {topic}"
                print("\n" + last_answer)
            elif choice == "6":
                if last_answer:
                    print("Saved to", save_note(last_title, last_answer))
                else:
                    print("Nothing to save yet.")
            elif choice == "0":
                print("Happy studying!")
                break
            else:
                print("Invalid option.")
        except AIError as e:
            print("Error:", e)
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
