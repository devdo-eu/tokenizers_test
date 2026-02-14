import csv
import json
import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

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
CHART_CONFIG = CONFIG["chart"]

TABLE_COL_HEADERS = CHART_CONFIG["table_headers"]
TABLE_ROW_LABELS = CHART_CONFIG["row_labels"]
TABLE_ROW_NAMES = CHART_CONFIG["row_names"]

COLORS = CHART_CONFIG["colors"]
BG_COLOR = COLORS["background"]
PANEL_BG = COLORS["panel_background"]
TEXT_COLOR = COLORS["text_primary"]
TEXT_SECONDARY = COLORS["text_secondary"]
GRID_COLOR = COLORS["grid"]
ACCENT_GREEN = COLORS["accent_green"]

FIGURE_CONFIG = CHART_CONFIG["figure"]


def load_csv_data(csv_path: Path) -> dict[str, dict[str, list[float]]]:
    tokenizer_names = [tok["name"] for tok in CONFIG["tokenizers"]]

    raw_values = {lang: [0.0] * len(tokenizer_names) for lang in TABLE_ROW_LABELS}
    norm_values = {lang: [0.0] * len(tokenizer_names) for lang in TABLE_ROW_LABELS}

    counts = {lang: [0] * len(tokenizer_names) for lang in TABLE_ROW_LABELS}

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lang = row["lang"]
            tokenizer = row["tokenizer"]

            if lang not in TABLE_ROW_LABELS:
                continue

            try:
                tok_idx = tokenizer_names.index(tokenizer)
            except ValueError:
                continue

            overhead = float(row["overhead_pct"])
            normalized = float(row["normalized_overhead_pct"])

            raw_values[lang][tok_idx] += overhead
            norm_values[lang][tok_idx] += normalized
            counts[lang][tok_idx] += 1

    for lang in TABLE_ROW_LABELS:
        for idx in range(len(tokenizer_names)):
            if counts[lang][idx] > 0:
                raw_values[lang][idx] /= counts[lang][idx]
                norm_values[lang][idx] /= counts[lang][idx]

    return {"raw": raw_values, "normalized": norm_values}


def _format_cell(val: float) -> str:
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.1f}%"


def _colors_for(val: float) -> tuple[str, str]:
    thresholds = CHART_CONFIG["color_thresholds"]

    for item in thresholds:
        threshold = item["threshold"]
        if threshold is None or val < threshold:
            return item["text"], item["background"]

    last = thresholds[-1]
    return last["text"], last["background"]


def draw_table(ax, title: str, value_data: dict[str, list[float]]) -> None:
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")
    ax.set_title(
        title, fontsize=15, color=TEXT_COLOR, pad=14,
        fontfamily="sans-serif", fontweight="medium", loc="left"
    )

    cell_text = [[_format_cell(v) for v in value_data[lang]] for lang in TABLE_ROW_LABELS]
    row_labels = [f"{code}  {name}" for code, name in zip(TABLE_ROW_LABELS, TABLE_ROW_NAMES)]

    table = ax.table(
        cellText=cell_text, rowLabels=row_labels, colLabels=TABLE_COL_HEADERS,
        cellLoc="center", rowLoc="right", loc="upper center",
        bbox=[0.0, 0.02, 1.0, 0.95],
    )
    table.auto_set_font_size(False)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(GRID_COLOR)
        cell.set_linewidth(1.2)

        if row == 0:
            cell.set_facecolor("#1e2130")
            cell.set_text_props(color=TEXT_COLOR, fontsize=11, fontweight="bold", fontfamily="sans-serif")
            cell.set_height(0.16)
        elif col == -1:
            cell.set_facecolor("#1e2130")
            is_pl = TABLE_ROW_LABELS[row - 1] == "PL"
            cell.set_text_props(
                color=ACCENT_GREEN if is_pl else TEXT_COLOR,
                fontsize=12, fontweight="bold" if is_pl else "medium", fontfamily="sans-serif",
            )
            cell.set_height(0.115)
        else:
            val = value_data[TABLE_ROW_LABELS[row - 1]][col]
            txt_c, bg_c = _colors_for(val)
            cell.set_facecolor(bg_c)
            cell.set_text_props(color=txt_c, fontsize=12, fontweight="bold", fontfamily="sans-serif")
            cell.set_height(0.115)


def main() -> None:
    script_dir = Path(__file__).parent
    csv_path = script_dir / "results_detailed.csv"

    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        logger.error("Please run experiment.py first to generate results_detailed.csv")
        return

    data = load_csv_data(csv_path)
    logger.info("Loaded data from CSV")

    sns.set_theme(style="dark", rc={
        "axes.facecolor": PANEL_BG, "figure.facecolor": BG_COLOR,
        "text.color": TEXT_COLOR, "axes.labelcolor": TEXT_COLOR,
        "xtick.color": TEXT_SECONDARY, "ytick.color": TEXT_COLOR,
        "grid.color": GRID_COLOR, "axes.edgecolor": GRID_COLOR,
    })

    fig = plt.figure(
        figsize=(FIGURE_CONFIG["width"], FIGURE_CONFIG["height"]),
        dpi=FIGURE_CONFIG["dpi"]
    )
    fig.patch.set_facecolor(BG_COLOR)

    gs = fig.add_gridspec(
        2, 1, height_ratios=[1.0, 1.0], hspace=0.18,
        left=0.18, right=0.95, top=0.88, bottom=0.06
    )

    fig.text(
        0.50, 0.96, "Narzut tokenizacji: polski vs angielski",
        ha="center", va="center", fontsize=24, fontweight="bold",
        color=TEXT_COLOR, fontfamily="sans-serif"
    )
    fig.text(
        0.50, 0.93,
        "Sredni % roznicy w liczbie tokenow - 100 zdan z artykulow Wikipedia, 5 tokenizerow",
        ha="center", va="center", fontsize=13, color=TEXT_SECONDARY, fontfamily="sans-serif"
    )

    draw_table(
        fig.add_subplot(gs[0]),
        "Sredni narzut tokenizacji vs angielski (%)",
        data["raw"]
    )
    draw_table(
        fig.add_subplot(gs[1]),
        "Znormalizowany narzut tokenizacji vs angielski (%) - tokens/char",
        data["normalized"]
    )

    output_path = script_dir.parent / "grafika.png"
    fig.savefig(output_path, dpi=FIGURE_CONFIG["save_dpi"], bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)

    logger.info(f"Chart saved: {output_path}")


if __name__ == "__main__":
    main()
