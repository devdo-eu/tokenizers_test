# Tokenization Overhead Benchmark

Empirical comparison of tokenization costs across languages and tokenizers. The experiment measures how many more tokens non-English text requires compared to English, a hidden "tax" that affects both latency and cost when using LLM APIs.

## Why it matters

Most popular tokenizers are optimized for English. The same sentence in Polish, Arabic, or Japanese can produce 30–400% more tokens, directly inflating API costs and reducing effective context windows. This project quantifies the problem across 5 tokenizers and 7 languages using a reproducible, Wikipedia-based corpus.

## Tokenizers tested

| Tokenizer | Library | Model |
|---|---|---|
| tiktoken (GPT-4) | tiktoken | `cl100k_base` |
| APT4 (Bielik v3) | transformers | `speakleash/Bielik-4.5B-v3` |
| TinyLlama (Llama 2) | transformers | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` |
| Qwen 2.5 | transformers | `Qwen/Qwen2.5-7B` |
| multilingual-e5-large | transformers | `intfloat/multilingual-e5-large` |

## Languages

English (EN), Polish (PL), German (DE), Arabic (AR), Armenian (HY), Japanese (JA), Chinese (ZH)

## How it works

1. **Corpus construction** (`fetch_corpus.py`): Extracts ~100 sentences from three Polish Wikipedia articles (AI, photosynthesis, Battle of Grunwald), then translates each sentence to 6 target languages via Google Translate. This produces parallel sentences so the same semantic content is compared across languages.

2. **Tokenization experiment** (`experiment.py`): Tokenizes every sentence with all 5 tokenizers and computes:
   - **Raw overhead**: % difference in token count vs. English
   - **Character overhead**: % difference in character length vs. English
   - **Normalized overhead**: overhead in tokens-per-character ratio, isolating the tokenizer's efficiency from text length differences

3. **Report generation** (`report.py`): Produces a Markdown report (`results.md`) with summary tables, per-language rankings, token visualizations, and overhead decomposition. Also exports raw data as CSV (`results_detailed.csv`).

4. **Chart generation** (`chart.py`): Renders a publication-ready PNG heatmap (`grafika.png`) comparing raw and normalized overhead across all language–tokenizer pairs.

## Quick start

### Prerequisites

- Python 3.11+
- A Hugging Face token (for gated models like Bielik-4.5B-v3)

### Installation

```bash
git clone <repo-url>
cd tokenizers_test
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with your Hugging Face token:

```
HF_TOKEN=hf_your_token_here
```

### Usage

**Option A: Full pipeline (with corpus generation):**

```bash
# 1. Build the 100-sentence multilingual corpus (~15-30 min, uses Google Translate)
python fetch_corpus.py

# 2. Run the tokenization experiment
python experiment.py

# 3. Generate the chart
python chart.py
```

**Option B: Quick run (built-in sentences):**

```bash
# Runs with 4 fallback sentences, no corpus fetch needed
python experiment.py
```

### Output files

| File | Description |
|---|---|
| `corpus.json` | Multilingual parallel corpus (generated) |
| `results.md` | Full Markdown report with tables and analysis |
| `results_detailed.csv` | Raw per-sentence results for custom analysis |
| `grafika.png` | Overhead heatmap chart |

## Configuration

All parameters are centralized in `config.json`:

- **languages**: language codes and display names
- **tokenizers**: list of tokenizers with library and model ID
- **corpus_fetcher**: Wikipedia sources, sentence count, length filters, target languages, random seed
- **chart**: color scheme, thresholds, figure dimensions

## Metrics explained

| Metric | Formula | Interpretation |
|---|---|---|
| Raw overhead | `(tokens_lang - tokens_EN) / tokens_EN` | Total extra tokens vs. English |
| Character overhead | `(chars_lang - chars_EN) / chars_EN` | How much longer the text itself is |
| Normalized overhead | `(tokens_per_char_lang - tokens_per_char_EN) / tokens_per_char_EN` | Tokenizer inefficiency, independent of text length |

The three metrics are related multiplicatively:
`(1 + raw) = (1 + char_overhead) × (1 + normalized)`

This decomposition separates the "linguistic" factor (some languages simply use more characters) from the "tokenizer" factor (how efficiently the tokenizer handles a given script).

## Results (in polish)
Results from experiment - see [RESULTS](results.md).

## License

Apache License 2.0 - see [LICENSE](LICENSE).
