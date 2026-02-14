import json
import logging
import sys
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class TokenizerLibrary(Enum):
    TIKTOKEN = "tiktoken"
    TRANSFORMERS = "transformers"


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


CONFIG = load_config()
LANGUAGES = CONFIG["languages"]["codes"]
LANG_NAMES = CONFIG["languages"]["names"]


def _load_fallback() -> dict[str, dict[str, str]]:
    fallback_path = Path(__file__).parent / "fallback_sentences.json"
    with open(fallback_path, encoding="utf-8") as f:
        return json.load(f)


def load_corpus(path: Path) -> tuple[dict[str, dict[str, str]] | None, dict | None]:
    if not path.exists():
        return None, None

    with open(path, encoding="utf-8") as f:
        corpus = json.load(f)

    complete = {}
    incomplete_count = 0

    for sent in corpus["sentences"]:
        langs = {lang: sent[lang] for lang in LANGUAGES if sent.get(lang)}
        if len(langs) == len(LANGUAGES):
            complete[sent["id"]] = langs
        else:
            incomplete_count += 1

    if incomplete_count > 0:
        logger.warning(f"Filtered out {incomplete_count} incomplete sentences")

    return complete, corpus.get("metadata", {})


def load_tokenizers() -> dict[str, tuple[TokenizerLibrary, object]]:
    tokenizers = {}

    for tok_config in CONFIG["tokenizers"]:
        name = tok_config["name"]
        library = tok_config["library"]
        model_id = tok_config["model_id"]

        try:
            if library == TokenizerLibrary.TIKTOKEN.value:
                import tiktoken
                tokenizers[name] = (TokenizerLibrary.TIKTOKEN, tiktoken.get_encoding(model_id))
            else:
                from transformers import AutoTokenizer
                tokenizers[name] = (
                    TokenizerLibrary.TRANSFORMERS,
                    AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
                )
            logger.info(f"[OK] {name}")
        except Exception as e:
            logger.error(f"[FAIL] {name}: {e}")

    return tokenizers


def tokenize(text: str, tok_type: TokenizerLibrary, tok_obj) -> tuple[int, list[str]]:
    if tok_type == TokenizerLibrary.TIKTOKEN:
        ids = tok_obj.encode(text)
        return len(ids), [tok_obj.decode([i]) for i in ids]

    ids = tok_obj.encode(text, add_special_tokens=False)
    return len(ids), tok_obj.convert_ids_to_tokens(ids)


def run_experiment(
    sentences: dict[str, dict[str, str]],
    tokenizers: dict[str, tuple[TokenizerLibrary, object]]
) -> list[dict]:
    results = []
    total_sentences = len(sentences)

    for idx, sent_id in enumerate(sentences):
        if (idx + 1) % 10 == 0 or idx == 0:
            logger.info(f"Sentence {idx + 1}/{total_sentences}...")

        for lang in LANGUAGES:
            text = sentences[sent_id][lang]

            for tok_name, (tok_type, tok_obj) in tokenizers.items():
                count, tokens = tokenize(text, tok_type, tok_obj)
                char_count = len(text)

                results.append({
                    "sentence": sent_id,
                    "lang": lang,
                    "tokenizer": tok_name,
                    "count": count,
                    "tokens": tokens,
                    "text": text,
                    "char_count": char_count,
                    "tokens_per_char": count / char_count if char_count else 0,
                })

    return results


def compute_overhead(results: list[dict]) -> list[dict]:
    en_counts = {
        (r["sentence"], r["tokenizer"]): r["count"]
        for r in results if r["lang"] == "EN"
    }

    for r in results:
        en_count = en_counts.get((r["sentence"], r["tokenizer"]), 0)
        if en_count and r["lang"] != "EN":
            r["overhead_pct"] = ((r["count"] - en_count) / en_count) * 100
        else:
            r["overhead_pct"] = 0.0

    return results


def compute_char_normalized_overhead(results: list[dict]) -> list[dict]:
    en_data = {
        (r["sentence"], r["tokenizer"]): r
        for r in results if r["lang"] == "EN"
    }

    for r in results:
        en = en_data.get((r["sentence"], r["tokenizer"]))

        if en and r["lang"] != "EN" and en["tokens_per_char"] > 0:
            char_diff = r["char_count"] - en["char_count"]
            r["char_overhead_pct"] = (char_diff / en["char_count"]) * 100

            tpc_diff = r["tokens_per_char"] - en["tokens_per_char"]
            r["normalized_overhead_pct"] = (tpc_diff / en["tokens_per_char"]) * 100
        else:
            r["char_overhead_pct"] = 0.0
            r["normalized_overhead_pct"] = 0.0

    return results


def main() -> None:
    from report import (
        format_summary_table,
        format_normalized_summary_table,
        format_char_analysis,
        format_conclusions,
        save_results_md,
        save_detailed_csv,
    )

    logger.info("=== Tokenization experiment ===\n")

    script_dir = Path(__file__).parent
    corpus_path = script_dir / "corpus.json"

    sentences, metadata = load_corpus(corpus_path)

    if sentences:
        logger.info(f"Loaded corpus: {len(sentences)} sentences from corpus.json")
    else:
        logger.info("corpus.json not found — using 4 built-in test sentences")
        sentences, metadata = _load_fallback(), None

    logger.info("\nLoading tokenizers...")
    tokenizers = load_tokenizers()

    if not tokenizers:
        logger.error("No tokenizers available. Exiting.")
        sys.exit(1)

    expected_count = len(CONFIG["tokenizers"])
    logger.info(f"\nLoaded {len(tokenizers)}/{expected_count} tokenizers.\n")

    logger.info("Running tokenization...")
    results = compute_char_normalized_overhead(
        compute_overhead(run_experiment(sentences, tokenizers))
    )
    logger.info(f"Collected {len(results)} results.\n")

    print(format_summary_table(results))
    print()
    print(format_char_analysis(sentences))
    print()
    print(format_normalized_summary_table(results))
    print()
    print(format_conclusions(results))

    save_results_md(results, sentences, metadata, script_dir / "results.md")
    save_detailed_csv(results, script_dir / "results_detailed.csv")


if __name__ == "__main__":
    main()
