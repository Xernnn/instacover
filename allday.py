from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
import os

# ==========================================
# 🛠️ SETTINGS
# ==========================================
TEXT_X = 540
TEXT_Y = 810
FONT_PATH = "Pabasing.otf"
FONT_SIZE = 300
TEXT_COLOR = "#FFFFFF"

WIDTH, HEIGHT = 1080, 1920

START_DAY = 215
END_DAY = 600

# Every this many days (~3 months), swap the visual "concept" the color runs
# through -- vertical fade, then horizontal, then diagonal, then radial, ...
ERA_LENGTH_DAYS = 84
CONCEPTS = ["horizontal", "diagonal", "radial_center", "radial_corner", "vertical"]

GOLDEN = 0.6180339887498949  # spreads hues around the wheel with no near-repeats
PLASTIC = 0.5436890126920763  # decorrelated step for lightness/chroma "mood"
# ==========================================

os.makedirs("output_stories", exist_ok=True)


# ---------------------------------------------------------------------------
# OKLCH -> sRGB
#
# HSV hue is not perceptually uniform: a 0.1 step through blue/purple looks
# far more similar to the eye than the same 0.1 step through yellow/orange,
# which is why the old golden-ratio hue walk still felt like it was looping
# every few weeks. OKLCH fixes that -- equal numeric steps in hue/lightness
# read as equally different colors -- so the same low-discrepancy walk now
# actually delivers a visibly distinct color every week across the run.
# ---------------------------------------------------------------------------

def _linear_to_srgb(c):
    c = max(0.0, min(1.0, c))
    c = c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return max(0.0, min(1.0, c)) * 255.0


def oklch_to_rgb(lightness, chroma, hue_deg):
    h = math.radians(hue_deg)
    a = chroma * math.cos(h)
    b = chroma * math.sin(h)

    l_ = lightness + 0.3963377774 * a + 0.2158037573 * b
    m_ = lightness - 0.1055613458 * a - 0.0638541728 * b
    s_ = lightness - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3

    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    return (round(_linear_to_srgb(r)), round(_linear_to_srgb(g)), round(_linear_to_srgb(bl)))


# ---------------------------------------------------------------------------
# Color engine
# ---------------------------------------------------------------------------

def get_week_palette(week_index):
    """One well-separated hue + mood per week.

    Hue is walked around the OKLCH wheel with the golden ratio, which is a
    low-discrepancy sequence: each new week lands in the biggest remaining
    gap, so nearby weeks are never close in hue and the full run (~56 weeks)
    covers the wheel edge to edge before anything repeats.

    Lightness/chroma ("mood": dark & bold vs. pale & soft) is walked with a
    second, decorrelated irrational step so it doesn't just track hue -- two
    weeks with similar hues can still feel completely different in tone.
    """
    hue = (week_index * GOLDEN) % 1.0 * 360.0
    tone = (week_index * PLASTIC) % 1.0
    lightness = 0.45 + 0.25 * tone     # 0.45 - 0.70
    chroma = 0.12 + 0.06 * (1 - tone)  # 0.12 - 0.18
    return hue, lightness, chroma


def get_gradient_colors(current_day, start_day):
    days_passed = current_day - start_day
    week_index = days_passed // 7
    day_of_week = days_passed % 7

    hue, lightness, chroma = get_week_palette(week_index)

    # Two-tone spread within the week: hue drifts and lightness ramps up
    # from Monday to Sunday, same idea as before, just perceptually uniform.
    hue_a = hue + day_of_week * 8.0
    hue_b = hue_a + 45.0
    lightness_a = min(0.90, lightness + day_of_week * 0.035)
    lightness_b = min(0.95, lightness_a + 0.22)

    color_a = oklch_to_rgb(lightness_a, chroma, hue_a % 360.0)
    color_b = oklch_to_rgb(lightness_b, chroma, hue_b % 360.0)
    return color_a, color_b


def concept_for_day(current_day, start_day):
    era_index = (current_day - start_day) // ERA_LENGTH_DAYS
    return CONCEPTS[era_index % len(CONCEPTS)]


# ---------------------------------------------------------------------------
# Rendering: same two colors, different geometry per "concept"
# ---------------------------------------------------------------------------

def _gradient_mask(width, height, concept):
    y, x = np.mgrid[0:height, 0:width].astype(np.float32)
    if concept == "vertical":
        t = y / (height - 1)
    elif concept == "horizontal":
        t = x / (width - 1)
    elif concept == "diagonal":
        t = (x / (width - 1) + y / (height - 1)) / 2.0
    elif concept == "radial_center":
        cx, cy = (width - 1) / 2.0, (height - 1) / 2.0
        d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        t = d / d.max()
    elif concept == "radial_corner":
        d = np.sqrt(x ** 2 + y ** 2)
        t = d / d.max()
    else:
        raise ValueError(f"Unknown concept: {concept}")
    return t


def create_gradient(width, height, color_a, color_b, concept):
    t = _gradient_mask(width, height, concept)[..., None]
    a = np.array(color_a, dtype=np.float32)
    b = np.array(color_b, dtype=np.float32)
    rgb = a + (b - a) * t
    return Image.fromarray(rgb.astype(np.uint8), mode="RGB")


def load_font():
    try:
        return ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except IOError:
        print(f"⚠️ Could not find {FONT_PATH}. Using default font.")
        return ImageFont.load_default()


def main():
    font = load_font()
    print(f"Starting production: Day {START_DAY} to {END_DAY}...")

    current_concept = None
    for current_day in range(START_DAY, END_DAY + 1):
        color_a, color_b = get_gradient_colors(current_day, START_DAY)
        concept = concept_for_day(current_day, START_DAY)
        if concept != current_concept:
            current_concept = concept
            print(f"-- Day {current_day}: gradient concept -> '{concept}' --")

        img = create_gradient(WIDTH, HEIGHT, color_a, color_b, concept)
        draw = ImageDraw.Draw(img)
        draw.text(
            (TEXT_X, TEXT_Y),
            f"Day {current_day}",
            fill=TEXT_COLOR,
            anchor="mm",
            align="center",
            font=font,
        )
        img.save(f"output_stories/Day_{current_day}.png")

        if current_day % 50 == 0:
            print(f"✅ Generated up to Day {current_day}...")

    print("🎉 All stories generated! Enjoy your distinct daily gradients.")


if __name__ == "__main__":
    main()
