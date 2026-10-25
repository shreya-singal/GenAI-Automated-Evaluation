# GenAI Automated Evaluation

Automated grading of short-answer exam responses using LLMs (GPT-3.5-turbo and Gemini Pro), comparing three prompting strategies for assessing student answers.

## Overview
Student answers to ML conceptual questions (e.g., "What is the difference between supervised and unsupervised learning?") are scored by an LLM acting as a grader. The project compares how OpenAI and Gemini behave under three evaluation methods on the same data (15 students x 3 questions).

## Methods
| Method | Input to LLM | Output |
|---|---|---|
| 1. Holistic closeness | Question + reference answer + student answer | Score (0-1) + reasoning (<=50 words) |
| 2. Reference-based rubric | Question + reference answer + student answer + rubric query | Yes/No + reasoning |
| 3. Reference-free rubric | Question + student answer + rubric query | Yes/No + reasoning |

Methods 2 and 3 break grading into granular yes/no criteria (from the `Query` sheet), which makes it possible to test whether the LLM needs a reference answer at all.

## Repo structure
- `OpenAI/call_openai.py` - pipeline using gpt-3.5-turbo
- `Gemini/call_gemini.py` - pipeline using gemini-pro
- `*/Processed_Exam_Data_Method{1,2,3}*.xlsx` - outputs for each method
- `.env.example` - template for API keys
- `requirements.txt` - dependencies

## Setup
```bash
pip install -r requirements.txt
cp .env.example openai.env    # add your OpenAI key
cp .env.example gemini.env    # add your Gemini key
```

## Usage
Place `Exam1-Answers.xlsx` and `Exam1-Q1.xlsx` (not included in this repo) in the script's folder, then:
```bash
python OpenAI/call_openai.py
python Gemini/call_gemini.py
```

## Notes / limitations
- Model outputs are parsed from free-text lines, so malformed responses fall back to "NA".
- Small sample (15 students, 3 questions); no human-grade comparison yet.
- Uses the legacy `openai<1.0` API and the deprecated `gemini-pro` model.
