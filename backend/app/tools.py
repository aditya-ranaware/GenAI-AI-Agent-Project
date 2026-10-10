import json
import uuid
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw charts to files, no pop-up window (needed on servers)
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import StrMethodFormatter
from app.config import settings

AGG_FUNCS = ["sum", "mean", "count", "min", "max", "median"]
OPS = ["==", "!=", ">", ">=", "<", "<=", "contains"]
CHART_TYPES = ["bar", "line", "pie"]
# Chart colors match the dark app theme
INK, TEXT, MUTED, GRID, GOLD = "#1a2040", "#e8ebf8", "#99a2cc", "#2e376a", "#ffb84d"
PIE_COLORS = ["#ffb84d", "#5ce0a4", "#7aa2ff", "#ff7a8a", "#c79bff", "#4fd1e0", "#f5d76e", "#99a2cc"]

# ---------------------------------------------------------------- helpers
def _load(file_name: str) -> pd.DataFrame:
    path = settings.upload_dir / Path(file_name).name  # .name blocks "../" tricks
    if not path.exists():
        raise ValueError(f"File '{file_name}' not found in uploads.")
    return pd.read_csv(path)


def _check_column(df: pd.DataFrame, col: str) -> None:
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found. Available columns: {list(df.columns)}")


def _apply_filters(df: pd.DataFrame, filters: list | None) -> pd.DataFrame:
    for f in filters or []:
        col, op, value = f["column"], f["op"], f["value"]
        _check_column(df, col)
        if op not in OPS:
            raise ValueError(f"Operator '{op}' is not allowed. Use one of {OPS}")
        series = df[col]
        if op == "contains":
            df = df[series.astype(str).str.contains(str(value), case=False, na=False)]
            continue
        if pd.api.types.is_numeric_dtype(series):  # the LLM sends values as text
            value = pd.to_numeric(value)
        df = df[{
            "==": series == value, "!=": series != value,
            ">": series > value, ">=": series >= value,
            "<": series < value, "<=": series <= value,
        }[op]]
    return df


# ------------------------------------------------------------------ tools
def get_schema(file_name: str) -> dict:
    """Describe the CSV: size, columns, types, sample rows, and values of small categories."""
    df = _load(file_name)
    categories = {
        c: df[c].dropna().unique().tolist()
        for c in df.columns
        if not pd.api.types.is_numeric_dtype(df[c]) and df[c].nunique() <= 10
    }
    return {
        "rows": len(df),
        "columns": {c: str(t) for c, t in df.dtypes.items()},
        "sample_rows": df.head(3).to_dict(orient="records"),
        "category_values": categories,
    }


def query_data(file_name: str, filters: list | None = None, group_by: list | None = None,
               aggregations: list | None = None, sort_by: str | None = None,
               descending: bool = True, limit: int = 10) -> dict:
    """Filter, group, aggregate, sort and limit the data (no code execution)."""
    df = _apply_filters(_load(file_name), filters)

    if group_by and not aggregations:
        raise ValueError("group_by needs at least one aggregation.")

    if aggregations:
        for a in aggregations:
            _check_column(df, a["column"])
            if a["function"] not in AGG_FUNCS:
                raise ValueError(f"Function '{a['function']}' is not allowed. Use one of {AGG_FUNCS}")
        named = {f"{a['column']}_{a['function']}": (a["column"], a["function"]) for a in aggregations}
        if group_by:
            for c in group_by:
                _check_column(df, c)
            result = df.groupby(group_by).agg(**named).reset_index()
        else:
            result = pd.DataFrame([{k: df[col].agg(fn) for k, (col, fn) in named.items()}])
    else:
        result = df

    if sort_by:
        if sort_by not in result.columns:
            raise ValueError(f"Cannot sort by '{sort_by}'. Result columns: {list(result.columns)}")
        result = result.sort_values(sort_by, ascending=not descending)

    limit = max(1, min(int(limit), 50))
    shown = result.head(limit).round(2)
    shown = shown.astype(object).where(shown.notna(), None)
    return {"total_rows": len(result), "rows": shown.to_dict(orient="records")}

def make_chart(file_name: str, chart_type: str, x: str, y: str, aggregation: str = "sum",
               filters: list | None = None, title: str | None = None, limit: int = 15) -> dict:
    """Group by column x, aggregate column y, and save a bar, line or pie chart as a PNG."""
    if chart_type not in CHART_TYPES:
        raise ValueError(f"chart_type must be one of {CHART_TYPES}")
    if aggregation not in AGG_FUNCS:
        raise ValueError(f"aggregation must be one of {AGG_FUNCS}")

    df = _apply_filters(_load(file_name), filters)
    _check_column(df, x)
    _check_column(df, y)

    data = df.groupby(x)[y].agg(aggregation)
    data = data.sort_index() if chart_type == "line" else data.sort_values(ascending=False).head(int(limit))
    if data.empty:
        raise ValueError("No data left to plot after filtering.")

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=INK)
    ax.set_facecolor(INK)
    labels = [str(i) for i in data.index]
    n = len(data)
    positions = list(range(n))
    if chart_type == "bar":
        ax.bar(positions, data.values, color=GOLD, width=0.65)
    elif chart_type == "line":
        ax.plot(positions, data.values, marker="o" if n <= 31 else None, color=GOLD, linewidth=2.2, markersize=5)
    else:
        _, _, percents = ax.pie(data.values, labels=labels, autopct="%1.0f%%", colors=(PIE_COLORS * 2)[: len(data)],
                                textprops={"color": TEXT}, wedgeprops={"edgecolor": INK, "linewidth": 2})
        for t in percents:  # dark text on the bright slices
            t.set_color(INK)
            t.set_fontweight("bold")
    if chart_type != "pie":
        ax.set_xlabel(x, color=MUTED)
        ax.set_ylabel(f"{aggregation} of {y}", color=MUTED)
        step = max(1, -(-n // 12))  # show at most about 12 labels on the x-axis
        ax.set_xticks(positions[::step])
        ax.set_xticklabels(labels[::step], rotation=45, ha="right")
        ax.tick_params(axis="x", colors=MUTED)
        ax.tick_params(axis="y", colors=MUTED)
        if data.abs().max() >= 1000:
            ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))  # 4,000,000 instead of 4e6
        else:
            ax.ticklabel_format(style="plain", axis="y")
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
    ax.set_title(title or f"{aggregation} of {y} by {x}", color=TEXT, fontsize=13, fontweight="bold", pad=12)

    settings.charts_dir.mkdir(parents=True, exist_ok=True)
    name = f"chart_{uuid.uuid4().hex[:8]}.png"
    fig.savefig(settings.charts_dir / name, dpi=150, bbox_inches="tight", facecolor=INK)
    plt.close(fig)

    values = {str(k): round(float(v), 2) for k, v in data.items()}
    if len(values) > 20:  # keep the result short: the LLM does not need hundreds of numbers
        values = {
            "note": f"{n} points plotted, showing a summary only",
            "first": [labels[0], round(float(data.iloc[0]), 2)],
            "last": [labels[-1], round(float(data.iloc[-1]), 2)],
            "highest": [str(data.idxmax()), round(float(data.max()), 2)],
            "lowest": [str(data.idxmin()), round(float(data.min()), 2)],
        }
    return {"chart_file": name, "plotted_values": values}


# ------------------------------------------- what the LLM sees (schemas)
_FILE = {"type": "string", "description": "CSV file name, e.g. sales.csv"}
_FILTERS = {
    "type": "array",
    "description": "Optional row filters. All filters must match.",
    "items": {
        "type": "object",
        "properties": {
            "column": {"type": "string"},
            "op": {"type": "string", "enum": OPS},
            "value": {"type": "string", "description": "The value to compare with (numbers as text)"},
        },
        "required": ["column", "op", "value"],
    },
}

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_schema",
        "description": "Look at the CSV first: row count, column names and types, sample rows, "
                       "and the allowed values of small category columns. Call this before anything else.",
        "parameters": {"type": "object", "properties": {"file_name": _FILE}, "required": ["file_name"]},
    }},
    {"type": "function", "function": {
        "name": "query_data",
        "description": "Filter, group, aggregate, sort and limit the data to get exact numbers. "
                       "Aggregated columns are named <column>_<function>, e.g. revenue_sum.",
        "parameters": {"type": "object", "properties": {
            "file_name": _FILE,
            "filters": _FILTERS,
            "group_by": {"type": "array", "items": {"type": "string"}, "description": "Columns to group by"},
            "aggregations": {"type": "array", "items": {"type": "object", "properties": {
                "column": {"type": "string"},
                "function": {"type": "string", "enum": AGG_FUNCS},
            }, "required": ["column", "function"]}},
            "sort_by": {"type": "string", "description": "Column of the result to sort by"},
            "descending": {"type": "boolean"},
            "limit": {"type": "integer", "description": "Max rows to return (up to 50)"},
        }, "required": ["file_name"]},
    }},
    {"type": "function", "function": {
        "name": "make_chart",
        "description": "Draw a chart: groups the data by column x, aggregates column y, saves a PNG.",
        "parameters": {"type": "object", "properties": {
            "file_name": _FILE,
            "chart_type": {"type": "string", "enum": CHART_TYPES},
            "x": {"type": "string", "description": "Column for the categories or x-axis"},
            "y": {"type": "string", "description": "Column to measure"},
            "aggregation": {"type": "string", "enum": AGG_FUNCS},
            "filters": _FILTERS,
            "title": {"type": "string"},
        }, "required": ["file_name", "chart_type", "x", "y"]},
    }},
]

TOOLS = {"get_schema": get_schema, "query_data": query_data, "make_chart": make_chart}


# ------------------------------------------------------- the dispatcher
def run_tool(name: str, args: dict) -> str:
    """Run a tool the LLM asked for. Errors go back to the LLM as text so it can fix its mistake."""
    func = TOOLS.get(name)
    if func is None:
        return json.dumps({"error": f"Unknown tool '{name}'. Available tools: {list(TOOLS)}"})
    try:
        result = func(**args)
    except TypeError as e:  # wrong or missing arguments
        return json.dumps({"error": f"Bad arguments for {name}: {e}"})
    except Exception as e:  # any other problem, e.g. a wrong column name
        return json.dumps({"error": str(e)})

    text = json.dumps(result, default=str)
    if len(text) > settings.max_tool_output_chars:
        text = text[: settings.max_tool_output_chars] + " ...[truncated]"
    return text