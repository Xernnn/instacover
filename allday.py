from PIL import Image, ImageDraw, ImageFont
import colorsys
import os

# ==========================================
# 🛠️ YOUR EXACT PHOTOPEA SETTINGS
# ==========================================
TEXT_X = 540            
TEXT_Y = 810            
FONT_PATH = "Pabasing.otf" 
FONT_SIZE = 300
TEXT_COLOR = "#FFFFFF"

START_DAY = 82
END_DAY = 600
# ==========================================

os.makedirs("output_stories", exist_ok=True)

def hsv_to_rgb255(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

def get_gradient_colors(current_day, start_day):
    days_passed = current_day - start_day
    week_index = days_passed // 7
    day_of_week = days_passed % 7
    
    # 1. WEEKLY GENRE (Golden Ratio)
    week_base_hue = (week_index * 0.6180339887) % 1.0 
    
    # 2. INCREASED DAILY SHIFT 
    # Was 0.02 (2% shift). Now 0.045 (4.5% shift per day).
    # This makes the color visibly morph (e.g., from Ocean Blue on Mon to Purple on Sun)
    day_hue = (week_base_hue + (day_of_week * 0.065)) % 1.0
    
    # 3. INCREASED BRIGHTNESS CONTRAST
    # Was 0.04. Now 0.08 per day. 
    # Monday starts noticeably darker (0.35), Sunday ends very bright (0.83)
    brightness_top = 0.35 + (day_of_week * 0.09)
    
    # 4. BOTTOM GRADIENT COLOR
    # Widened the gradient gap slightly for a cooler two-tone effect
    bottom_hue = (day_hue + 0.15) % 1.0
    brightness_bottom = min(1.0, brightness_top + 0.30)
    
    saturation = 0.85
    
    color_top = hsv_to_rgb255(day_hue, saturation, brightness_top)
    color_bottom = hsv_to_rgb255(bottom_hue, saturation, brightness_bottom)
    
    return color_top, color_bottom

def create_gradient(width, height, color_top, color_bottom):
    base = Image.new('RGB', (1, 2))
    base.putpixel((0, 0), color_top)
    base.putpixel((0, 1), color_bottom)
    return base.resize((width, height), Image.Resampling.BICUBIC)

# Load font
try:
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
except IOError:
    print(f"⚠️ Could not find {FONT_PATH}. Using default font.")
    font = ImageFont.load_default()

# Generate loop
print(f"Starting production: Day {START_DAY} to {END_DAY}...")

for current_day in range(START_DAY, END_DAY + 1):
    top_color, bottom_color = get_gradient_colors(current_day, START_DAY)
    
    img = create_gradient(1080, 1920, top_color, bottom_color)
    draw = ImageDraw.Draw(img)
    
    draw.text(
        (TEXT_X, TEXT_Y), 
        f"Day {current_day}", 
        fill=TEXT_COLOR, 
        anchor="mm", 
        align="center",
        font=font
    )
    
    img.save(f"output_stories/Day_{current_day}.png")
    
    if current_day % 50 == 0:
        print(f"✅ Generated up to Day {current_day}...")

print("🎉 All stories generated! Enjoy your distinct daily gradients.")