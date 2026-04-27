#!/usr/bin/env python3
"""
Reads garden.yaml and index.template.html, generates index.html.

garden.yaml structure:
  catalog:
    <Plant Name>:
      description: "..."
      color: "#rrggbb"
      svg: '<svg ...>...</svg>'
  grid:
    1: [Plant Name, Plant Name, null, ...]
    2: [...]
    ...

Run: python build.py
"""
import re
import sys
import yaml
from collections import Counter


def tip_styles(row_index, total_rows):
    """Return inline styles for tooltip and arrow based on vertical position."""
    top_half = row_index < total_rows / 2
    if top_half:
        tip = "top:calc(100% + 10px);bottom:auto;left:0;transform:none;"
        arrow = "bottom:100%;top:auto;border-bottom-color:#fff;border-top-color:transparent;"
        arrow_border = "bottom:100%;top:auto;border-bottom-color:#c8b98a;border-top-color:transparent;margin-bottom:1px;"
    else:
        tip = "bottom:calc(100% + 10px);top:auto;left:0;transform:none;"
        arrow = "top:100%;border-top-color:#fff;border-bottom-color:transparent;"
        arrow_border = "top:100%;border-top-color:#c8b98a;border-bottom-color:transparent;margin-top:1px;"
    return tip, arrow, arrow_border


def build_cell(col, row, row_index, total_rows, plant_name, catalog):
    cell_id = f"c{col}r{row}"
    if plant_name is None:
        return f'<div class="cell empty" id="{cell_id}"></div>\n'

    entry = catalog.get(plant_name)
    if entry is None:
        raise ValueError(f"Plant '{plant_name}' not found in catalog")

    color = entry["color"]
    svg = entry["svg"]
    description = entry["description"]
    tip_style, arrow_style, arrow_border_style = tip_styles(row_index, total_rows)

    return (
        f'<div class="cell" id="{cell_id}" data-plant="{plant_name}" style="background:{color}22;border-color:{color}">'
        f'{svg}'
        f'<div class="tip" style="{tip_style}">'
        f"<b>{plant_name}</b>"
        f"<p>{description}</p>"
        f'<div class="tip-arrow" style="{arrow_style}"></div>'
        f'<div class="tip-arrow-border" style="{arrow_border_style}"></div>'
        f"</div></div>\n"
    )


def build_grid(grid, catalog):
    max_rows = max(len(rows) for rows in grid.values())
    col_height = max_rows * 39 - 3

    parts = []
    for col_num in sorted(grid.keys(), key=int):
        rows = grid[col_num]
        total_rows = len(rows)
        cells_html = ""
        for row_index, plant_name in enumerate(rows):
            row_num = row_index + 1
            cells_html += build_cell(col_num, row_num, row_index, total_rows, plant_name, catalog)

        parts.append(
            f'<div class="col" id="col{col_num}"><div class="col-label">{col_num}</div>\n'
            f'<div class="col-inner" style="height:{col_height}px">{cells_html}'
            f"</div>\n</div>\n"
        )
    return "".join(parts)


def build_legend(grid, catalog):
    counts = Counter()
    for rows in grid.values():
        for plant in rows:
            if plant is not None:
                counts[plant] += 1

    parts = []
    seen = sorted(
        {plant for rows in grid.values() for plant in rows if plant},
        key=lambda s: s.lower()
    )

    for plant in seen:
        entry = catalog[plant]
        color = entry["color"]
        svg = entry["svg"]
        count = counts[plant]
        parts.append(
            f'<div class="legend-item" data-plant="{plant}">'
            f'<div style="width:22px;height:22px;flex-shrink:0">{svg}</div>'
            f'<span class="legend-name" style="color:{color}">{plant}</span>'
            f'<span class="legend-count">({count})</span>'
            f"</div>"
        )
    return "".join(parts)


def main():
    with open("garden.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    catalog = data["catalog"]
    grid = {str(k): v for k, v in data["grid"].items()}

    with open("index.template.html", "r", encoding="utf-8") as f:
        template = f.read()

    garden_grid_html = build_grid(grid, catalog)
    legend_html = build_legend(grid, catalog)

    output = template.replace("{{GARDEN_GRID}}", garden_grid_html)
    output = output.replace("{{LEGEND}}", legend_html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(output)

    total_plants = sum(1 for rows in grid.values() for p in rows if p is not None)
    print(f"Built index.html — {len(grid)} columns, {total_plants} plants")


if __name__ == "__main__":
    main()
