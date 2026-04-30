from PIL import Image, ImageDraw, ImageFont

# ==========================================
# 🛠️ SETTINGS TO TWEAK
# ==========================================
TEXT_X = 540            # 540 is exact left/right middle of 1080
TEXT_Y = 810            # 960 is exact up/down middle. Lower number = higher up
FONT_PATH = "Pabasing.otf" # Put your exact font file name here
FONT_SIZE = 300
TEXT_COLOR = "#FFFFFF"

TOP_COLOR = "#FFFFFF"   # Dark blue
BOTTOM_COLOR = "#000000" # Lighter blue
DAY_TEXT = "Day 81"
# ==========================================

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def create_gradient(width, height, top_hex, bottom_hex):
    base = Image.new('RGB', (1, 2))
    base.putpixel((0, 0), hex_to_rgb(top_hex))
    base.putpixel((0, 1), hex_to_rgb(bottom_hex))
    return base.resize((width, height), Image.Resampling.BICUBIC)

# 1. Create Background
img = create_gradient(1080, 1920, TOP_COLOR, BOTTOM_COLOR)
draw = ImageDraw.Draw(img)

# 2. Load Font
try:
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
except IOError:
    print(f"⚠️ Could not find {FONT_PATH}. Using default font.")
    font = ImageFont.load_default()

# 3. Draw Text
draw.text(
    (TEXT_X, TEXT_Y), 
    DAY_TEXT, 
    fill=TEXT_COLOR, 
    anchor="mm",      # "mm" means the X,Y coordinate is the exact center of the text
    align="center",
    font=font
)

# 4. Save test image
img.save("test_story_output2.png")
print("✅ Saved test_story_output.png! Open it to see how it looks.")