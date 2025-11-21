# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python-based research project for testing GPT model consistency using persona-based prompting. The project evaluates how consistently LLMs answer personality/preference questionnaires when given a detailed Personal Preference Vector (PPV) profile.

## Architecture

### Core Components

1. **PPV (Personal Preference Vector)**: JSON files containing detailed psychological profiles
   - Location: `ppv_initial.json`, `ppv_updated.json`, `ppv_output.json`
   - Structure: Contains personality dimensions (Big5, MBTI, DISC, Enneagram), value systems (Schwartz Values, Moral Foundations), risk profiles, decision styles, and behavioral indicators
   - Confidence scores: Each dimension includes confidence values (0.0-1.0) indicating reliability

2. **Question List**: Centralized questionnaire definitions
   - Location: `questions_list.py`
   - Contains 10 multiple-choice questions about financial/lifestyle decision-making
   - Each question has 5 options (A-E) ranging from conservative to risk-taking

3. **Testing Scripts**: Multiple versions for different testing scenarios
   - `ask_gpt5.py`: Basic version using GPT-5.1
   - `ask_gpt5_v2.py`: Uses GPT-5.1 with stability analysis
   - `ask_gpt5_v3.py`: Uses GPT-4o with enhanced stability metrics
   - `ask_gpt5_v4.py`: No-PPV baseline using gpt-5-mini

### Data Flow

1. Scripts load PPV profile from JSON file
2. PPV is injected into system prompt with decision-making rules
3. All 10 questions are sent to the model in a single conversation
4. Model responds with A-E choices for each question
5. Multiple rounds (10-50) are executed to measure consistency
6. Results are analyzed for stability metrics

### Key Design Patterns

**Persona Prompting**: The system prompt includes:
- Full PPV JSON data structure
- Explicit decision priorities (stability, controllability, long-term benefit, efficiency)
- Response format constraints (only output option letters)
- Consistency requirements

**Stability Measurement** (in v2/v3):
- Runs 50 rounds of the same questionnaire
- Uses `Counter` to find most common answer per question
- Calculates stability score = (count of most common answer) / (total rounds)

## Environment Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (manually)
pip install openai pandas numpy tqdm
```

## Running Tests

### Basic consistency test (50 rounds with GPT-4o)
```bash
python ask_gpt5_v3.py
```

### Testing with different models
- GPT-5.1: `ask_gpt5_v2.py`
- GPT-4o: `ask_gpt5_v3.py`
- GPT-5-mini (no PPV baseline): `ask_gpt5_v4.py`

### Environment Variables

Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-key-here"
```

## Script Differences

- **v2**: GPT-5.1 model, includes stability calculation
- **v3**: GPT-4o model (more stable), enhanced stability output formatting
- **v4**: GPT-5-mini, no PPV in prompt (baseline control), includes error handling and rate limiting

## Output Format

Each script prints:
1. Per-round answers: `回合 N: A B C D E...`
2. Full results table: All rounds in sequence
3. Stability analysis (v2/v3): Per-question consistency scores with most common answer and frequency

## Chinese Language Context

All prompts, questions, and outputs are in Traditional Chinese (Taiwanese Mandarin). When modifying prompts:
- Maintain formal but accessible language style
- Use Traditional Chinese characters (繁體中文)
- Keep decision-making terminology consistent with the existing PPV structure
