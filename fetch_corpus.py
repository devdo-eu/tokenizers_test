import json
import logging
import random
import re
import time
from datetime import datetime
from pathlib import Path

import nltk
import wikipediaapi
from deep_translator import GoogleTranslator

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


CONFIG = load_config()
CORPUS_CONFIG = CONFIG["corpus_fetcher"]

SEED = CORPUS_CONFIG["seed"]
SENTENCES_PER_ARTICLE = CORPUS_CONFIG["sentences_per_article"]
ARTICLES = CORPUS_CONFIG["articles"]
TARGET_LANGUAGES = CORPUS_CONFIG["target_languages"]
MIN_SENTENCE_LEN = CORPUS_CONFIG["min_sentence_length"]
MAX_SENTENCE_LEN = CORPUS_CONFIG["max_sentence_length"]


def ensure_nltk_data() -> None:
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        logger.info("Downloading nltk punkt_tab data...")
        nltk.download("punkt_tab", quiet=True)


def fetch_article_text(title: str) -> str:
    wiki = wikipediaapi.Wikipedia(
        user_agent="TokenizationExperiment/1.0 (contact@example.com)",
        language="pl",
    )
    page = wiki.page(title)
    if not page.exists():
        raise ValueError(f"Article '{title}' does not exist on PL Wikipedia")
    return page.text


def extract_sentences(text: str) -> list[str]:
    sentences = nltk.sent_tokenize(text, language="polish")
    filtered = []

    for s in sentences:
        s = s.strip()
        if len(s) < MIN_SENTENCE_LEN or len(s) > MAX_SENTENCE_LEN:
            continue
        if re.match(r"^[\d\s\.\,\-\/]+$", s) or s[:2] == "==" or s[0] in "[|{":
            continue
        filtered.append(s)

    return filtered


def translate_sentence(text: str, target_lang: str, max_retries: int = 3) -> str | None:
    for attempt in range(max_retries):
        try:
            return GoogleTranslator(source="pl", target=target_lang).translate(text)
        except Exception as e:
            if attempt < max_retries - 1:
                wait = (attempt + 1) * 2
                logger.warning(f"Translation error (attempt {attempt + 1}): {e}. Waiting {wait}s...")
                time.sleep(wait)
            else:
                logger.error(f"Failed to translate to {target_lang}: {e}")
                return None


def main() -> None:
    logger.info("=== Fetching 100-sentence corpus from Wikipedia ===\n")
    ensure_nltk_data()
    random.seed(SEED)

    all_sentences = []
    sources_meta = []

    for i, article in enumerate(ARTICLES):
        logger.info(f"\n--- Article {i + 1}: {article['title']} ({article['domain']}) ---")
        text = fetch_article_text(article["title"])
        sentences = extract_sentences(text)
        logger.info(f"{len(text)} chars, {len(sentences)} sentences after filtering.")

        n = SENTENCES_PER_ARTICLE[i]
        if len(sentences) < n:
            logger.warning(f"Not enough sentences ({len(sentences)}), taking all.")

        selected = sentences if len(sentences) < n else random.sample(sentences, n)

        sources_meta.append({
            "title": article["title"],
            "url": article["url"],
            "domain": article["domain"],
            "total_sentences_extracted": len(sentences),
            "sentences_selected": len(selected),
        })
        all_sentences.extend({"source": article["title"], "PL": s} for s in selected)
        logger.info(f"Selected {len(selected)} sentences.")

    logger.info(f"\nTotal PL sentences: {len(all_sentences)}")
    logger.info(f"\n=== Translating {len(all_sentences)} sentences to {len(TARGET_LANGUAGES)} languages ===\n")

    for idx, sent in enumerate(all_sentences):
        logger.info(f"Sentence {idx + 1}/{len(all_sentences)}: {sent['PL'][:60]}...")
        for lang_code, lang_key in TARGET_LANGUAGES.items():
            sent[lang_key] = translate_sentence(sent["PL"], lang_code) or ""
            time.sleep(0.5)

    corpus = {
        "metadata": {
            "sources": sources_meta,
            "total_sentences": len(all_sentences),
            "languages": ["PL", "EN", "DE", "AR", "HY", "JA", "ZH"],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "translation_method": "Google Translate via deep_translator",
            "seed": SEED,
        },
        "sentences": [
            {
                "id": f"s{idx + 1:03d}",
                "source": sent["source"],
                **{lang: sent.get(lang, "") for lang in ["PL", "EN", "DE", "AR", "HY", "JA", "ZH"]}
            }
            for idx, sent in enumerate(all_sentences)
        ],
    }

    script_dir = Path(__file__).parent
    output_path = script_dir / "corpus.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    langs = corpus["metadata"]["languages"]
    total = len(corpus["sentences"]) * len(langs)
    ok = sum(1 for s in corpus["sentences"] for lang in langs if s.get(lang))
    logger.info(f"\nSaved {output_path}: {len(corpus['sentences'])} sentences, {ok}/{total} fields populated")


if __name__ == "__main__":
    main()
