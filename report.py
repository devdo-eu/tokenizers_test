import csv
import math
from pathlib import Path

from experiment import LANGUAGES, LANG_NAMES


def _std_dev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(variance)


def _avg(results: list[dict], lang: str, tok: str, field: str = "overhead_pct") -> float | None:
    vals = [r[field] for r in results if r["lang"] == lang and r["tokenizer"] == tok]
    return sum(vals) / len(vals) if vals else None


def _signed(val: float) -> str:
    return f"+{val:.1f}%" if val >= 0 else f"{val:.1f}%"


def _format_overhead_table(results: list[dict], title: str, field: str) -> str:
    tok_names = list(dict.fromkeys(r["tokenizer"] for r in results))
    non_en = [lang for lang in LANGUAGES if lang != "EN"]

    lines = [
        f"## {title}\n",
        "| Jezyk | " + " | ".join(tok_names) + " |",
        "|-------|" + "|".join(["--------"] * len(tok_names)) + "|"
    ]

    for lang in non_en:
        row = f"| **{lang}** ({LANG_NAMES[lang]}) "
        for tok in tok_names:
            vals = [r[field] for r in results if r["lang"] == lang and r["tokenizer"] == tok]
            if vals:
                avg = sum(vals) / len(vals)
                row += f"| {_signed(avg)} ({_std_dev(vals):.0f}) "
            else:
                row += "| - "
        lines.append(row + "|")

    return "\n".join(lines)


def format_summary_table(results: list[dict]) -> str:
    return _format_overhead_table(
        results, "Sredni narzut tokenizacji vs angielski (%)", "overhead_pct"
    )


def format_normalized_summary_table(results: list[dict]) -> str:
    return _format_overhead_table(
        results, "Znormalizowany narzut tokenizacji vs angielski (%) — tokens/char", "normalized_overhead_pct"
    )


def format_char_analysis(sentences: dict[str, dict[str, str]]) -> str:
    lines = [
        "## Analiza dlugosci znakowej tekstu\n",
        "| Jezyk | Srednia dl. (znaki) | Sredni narzut znakowy vs EN |",
        "|-------|---------------------|----------------------------|"
    ]

    char_avgs = {
        lang: sum(len(sentences[s][lang]) for s in sentences) / len(sentences)
        for lang in LANGUAGES
    }

    lines.append(f"| **EN** (English) | {char_avgs['EN']:.0f} | - |")

    for lang in [l for l in LANGUAGES if l != "EN"]:
        overheads = [
            ((len(sentences[s][lang]) - len(sentences[s]["EN"])) / len(sentences[s]["EN"])) * 100
            for s in sentences if len(sentences[s]["EN"]) > 0
        ]
        avg_oh = sum(overheads) / len(overheads) if overheads else 0
        lines.append(f"| **{lang}** ({LANG_NAMES[lang]}) | {char_avgs[lang]:.0f} | {_signed(avg_oh)} |")

    return "\n".join(lines)


def format_ranking(results: list[dict]) -> str:
    tok_names = list(dict.fromkeys(r["tokenizer"] for r in results))
    non_en = [lang for lang in LANGUAGES if lang != "EN"]
    lines = ["## Ranking jezykow (od najtanszego do najdrozszego)\n"]

    for tok in tok_names:
        lines.append(f"### {tok}\n")
        avgs = sorted(
            [(lang, _avg(results, lang, tok)) for lang in non_en if _avg(results, lang, tok) is not None],
            key=lambda x: x[1],
        )
        for i, (lang, avg) in enumerate(avgs, 1):
            lines.append(f"{i}. **{lang}** ({LANG_NAMES[lang]}): {_signed(avg)}")
        lines.append("")

    return "\n".join(lines)


def format_token_visualization(results: list[dict]) -> str:
    lines = ["## Wizualizacja tokenow (tiktoken GPT-4, wybrane zdania)\n"]
    sample_sids = list(dict.fromkeys(r["sentence"] for r in results))[:3]
    tik = [r for r in results if r["tokenizer"] == "tiktoken (GPT-4)" and r["sentence"] in sample_sids]

    for sid in sample_sids:
        lines.append(f"### Zdanie: {sid}\n")
        for lang in ["EN", "PL"]:
            matches = [r for r in tik if r["sentence"] == sid and r["lang"] == lang]
            if matches:
                r = matches[0]
                tokens_str = " | ".join(f"`{t}`" for t in r["tokens"][:40])
                if len(r["tokens"]) > 40:
                    tokens_str += " | ..."
                lines.append(f"**{r['lang']}** ({r['count']} tokenow):")
                lines.append(f"> {tokens_str}")
                lines.append("")

    return "\n".join(lines)


def format_conclusions(results: list[dict]) -> str:
    tok_names = list(dict.fromkeys(r["tokenizer"] for r in results))
    lines = ["## Kluczowe wnioski\n"]

    for tok in tok_names:
        avg = _avg(results, "PL", tok)
        if avg is not None:
            std = _std_dev([r["overhead_pct"] for r in results if r["lang"] == "PL" and r["tokenizer"] == tok])
            lines.append(f"- **{tok}**: polski tekst potrzebuje srednio **{_signed(avg)}** (std={std:.0f}) wiecej tokenow niz angielski")

    lines.append("")

    for name, lang, label in [("Bielik v3", "PL", "polskim"), ("Qwen 2.5", "ZH", "chinskim")]:
        spec = _avg(results, lang, name)
        if spec is not None:
            others = [v for v in [_avg(results, lang, t) for t in tok_names if t != name] if v is not None]
            if others:
                om = sum(others) / len(others)
                lines.append(f"- {name} (specjalizowany w {label}): narzut {lang} = {_signed(spec)} vs srednia pozostalych = {_signed(om)}")

    lines.append("")
    lines.append("### Dekompozycja narzutu (PL vs EN)\n")
    lines.append("Relacja multiplikatywna: (1 + surowy narzut) = (1 + narzut znakowy) x (1 + narzut znormalizowany)\n")

    for tok in tok_names:
        raw = _avg(results, "PL", tok)
        if raw is not None:
            char_oh = _avg(results, "PL", tok, "char_overhead_pct")
            norm = _avg(results, "PL", tok, "normalized_overhead_pct")
            lines.append(
                f"- **{tok}**: surowy {_signed(raw)}, z czego narzut znakowy {_signed(char_oh)}, "
                f"znormalizowany (tokenizer) {_signed(norm)}"
            )

    return "\n".join(lines)


def format_data_sources(metadata: dict | None) -> str:
    lines = ["## Zrodla danych\n"]

    if not metadata:
        lines.append("Dane wbudowane (4 zdania testowe).\n")
        return "\n".join(lines)

    lines.append(f"**Korpus**: {metadata.get('total_sentences', '?')} zdan z artykulow polskiej Wikipedii\n")
    lines.append(f"**Tlumaczenie**: {metadata.get('translation_method', '?')}\n")
    lines.append(f"**Data generacji**: {metadata.get('generated_at', '?')}\n")
    lines.append("**Artykuly zrodlowe:**\n")

    for src in metadata.get("sources", []):
        lines.append(f"- [{src['title']}]({src['url']}) ({src['domain']}) — {src.get('sentences_selected', '?')} zdan")

    lines.append("")
    return "\n".join(lines)


def save_detailed_csv(results: list[dict], output_path: Path) -> None:
    fieldnames = [
        "sentence", "lang", "tokenizer", "count", "char_count", "overhead_pct",
        "char_overhead_pct", "normalized_overhead_pct", "tokens_per_char"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    print(f"Detail table saved to: {output_path}")


def save_results_md(
    results: list[dict],
    sentences: dict[str, dict[str, str]],
    metadata: dict | None,
    output_path: Path
) -> None:
    n = len(sentences)
    desc = "100 zdan z artykulow Wikipedia PL" if n >= 100 else f"{n} zdan testowych"

    sections = [
        "# Wyniki eksperymentu tokenizacji\n",
        f"5 tokenizerow x 7 jezykow x {desc}\n",
        format_data_sources(metadata), "",
        format_summary_table(results), "",
        format_char_analysis(sentences), "",
        format_normalized_summary_table(results), "",
        format_ranking(results), "",
        format_token_visualization(results), "",
        format_conclusions(results),
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sections))

    print(f"\nResults saved to: {output_path}")
