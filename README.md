# AI Study Buddy

A command-line study assistant powered by Google's Gemini AI. Built with plain Python (standard library only, no pip installs).

## Features
- **Explain** any concept at beginner, school or college level
- **Quiz me**: the AI writes multiple-choice questions as JSON, and the program asks them, grades them and shows explanations
- **Summarise** pasted notes into an overview, bullet points and exam questions
- **Flashcards** on any topic
- **Study plan** for N days
- **Save** any answer to `study_notes.md`
- **Demo mode**: works without an API key using sample answers

## How the AI is used
`ai_client.py` sends a prompt to the Gemini API over HTTPS and returns the text. `prompts.py` holds the prompt templates (role, task, format, constraints). `main.py` is the menu and the quiz logic (parsing the AI's JSON, grading locally, handling errors).

## Setup
1. Get a free API key from Google AI Studio (aistudio.google.com).
2. Copy `.env.example` to `.env` and paste your key:
   ```
   GEMINI_API_KEY=your_key_here
   ```
   (or set it in the terminal: `export GEMINI_API_KEY=...` on Mac/Linux, `set GEMINI_API_KEY=...` on Windows)
3. Run:
   ```bash
   python main.py
   ```
Without a key the app starts in demo mode.

**Privacy:** on the free tier, prompts may be used by Google to improve its products, so never paste personal or confidential information. Never commit your `.env` file (it is in `.gitignore`).

## Troubleshooting
| Message | Fix |
|---|---|
| `Model not found` | Model names change. Set `GEMINI_MODEL` in `.env` to a current model from ai.google.dev |
| `API rejected the request` | Check your key has no extra spaces |
| `Rate limit reached` | Free tier has limits. Wait a minute |

## Tests
```bash
python -m unittest discover tests
```
12 tests cover response parsing, error handling (network mocked), quiz parsing and grading, prompts and saving notes.

## Project structure
```
ai-study-buddy/
├── main.py            # menu, quiz logic, notes
├── ai_client.py       # Gemini API client + demo mode
├── prompts.py         # prompt templates and demo answers
├── tests/test_study_buddy.py
├── docs/ai_tools_notes.md
├── docs/linkedin_post.md
├── .env.example
└── .gitignore
```

## Ideas for improvement
Conversation memory, saving quiz scores over time, reading notes from PDF/text files, a web version with Streamlit.
