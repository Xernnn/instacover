"""Contact sheet of one swatch per week, Day START_DAY -> Day END_DAY.

Renders each week's actual gradient concept in miniature so you can see the
whole color range *and* where the concept changes (vertical -> horizontal ->
diagonal -> radial -> ...) at a glance, without generating all the full-size
story images first.
"""

from PIL import Image, ImageDraw, ImageFont

from allday import (
    START_DAY,
    END_DAY,
    get_gradient_colors,
    concept_for_day,
    create_gradient,
    load_font,
)

SWATCH_W, SWATCH_H = 160, 284  # 1080:1920 aspect, scaled down
COLS = 8
LABEL_H = 34
PAD = 8
OUT_PATH = "color_preview.png"


def main():
    weeks = list(range(START_DAY, END_DAY + 1, 7))
    rows = (len(weeks) + COLS - 1) // COLS

    sheet_w = COLS * (SWATCH_W + PAD) + PAD
    sheet_h = rows * (SWATCH_H + LABEL_H + PAD) + PAD

    sheet = Image.new("RGB", (sheet_w, sheet_h), "#111111")
    draw = ImageDraw.Draw(sheet)
    try:
        label_font = ImageFont.truetype("Pabasing.otf", 20)
    except IOError:
        label_font = ImageFont.load_default()

    current_concept = None
    for i, day in enumerate(weeks):
        color_a, color_b = get_gradient_colors(day, START_DAY)
        concept = concept_for_day(day, START_DAY)
        swatch = create_gradient(SWATCH_W, SWATCH_H, color_a, color_b, concept)

        col, row = i % COLS, i // COLS
        x = PAD + col * (SWATCH_W + PAD)
        y = PAD + row * (SWATCH_H + LABEL_H + PAD)
        sheet.paste(swatch, (x, y))

        label = f"Day {day}"
        if concept != current_concept:
            current_concept = concept
            label += f" [{concept}]"
        draw.text((x, y + SWATCH_H + 4), label, fill="#FFFFFF", font=label_font)

    sheet.save(OUT_PATH)
    print(f"Saved {OUT_PATH} -- {len(weeks)} weeks, Day {START_DAY} to Day {END_DAY}.")


if __name__ == "__main__":
    main()
