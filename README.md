# ASCII Banner Engine v2.0

> Generate stunning ASCII text banners with 571+ fonts, 18 style presets, and intelligent terminal sizing.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 🚀 Features

### 571+ Fonts — Auto-Loaded
No hardcoded font dictionaries. The engine discovers **all available pyfiglet fonts** at runtime and adds 5 curated aliases for readability.

| Category | Count | Example Aliases |
|----------|-------|-----------------|
| Auto-discovered fonts | 571 | `standard`, `slant`, `big`, `gothic` |
| Curated aliases | 5 | `3d` → `3-d`, `isomeric` → `isometric1` |
| **Total** | **576** | |

### 18 Style Presets
Each preset combines color, border style, and alignment in one word:

| Category | Presets |
|----------|---------|
| **Classic** | `default`, `minimal`, `clean`, `boxed`, `heavy` |
| **Neon/Cyber** | `neon-blue`, `neon-green`, `neon-pink`, `cyber`, `matrix` |
| **Elegant** | `elegant`, `royal`, `shadow` |
| **Playful** | `retro`, `arcade`, `comic` |
| **Bare (no frame)** | `bare`, `bare-center` |

### Intelligent Size Manager
Automatically detects your terminal dimensions and adjusts banners to fit:

- **Auto-fit**: Tries larger fonts first, falls back to smaller ones if banner overflows
- **Truncation**: Hard-cuts wide banners with `‥` indicator
- **Padding/Alignment**: Left, center, right padding control
- **Real-time detection**: Refreshes terminal width on window resize

### Rich CLI Experience
Built with `rich` library for beautiful terminal output:

- Colored tables for font/style listings
- Panels with configurable borders
- Unicode symbols and formatting
- Clear error messages

### Export Mode
Render your text in **every font** and save to individual `.txt` files:

bash python3 banner_engine.py --export TRUTH

Creates ./banner_output/truth_standard.txt, truth_big.txt, etc.
📦 Installation
Requirements
pip install pyfiglet rich

Verify Setup
python3 banner_engine.py --help

💻 Usage
CLI Commands
Command	Description
python3 banner_engine.py "<text>"	Quick render with default styling
python3 banner_engine.py --demo	Basic banner examples
python3 banner_engine.py --themes	Themed collections (cyberpunk, gothic, etc.)
python3 banner_engine.py --styles	Show style preset gallery
python3 banner_engine.py --sizes	SizeManager diagnostics
python3 banner_engine.py --fonts	List all 576 fonts
python3 banner_engine.py --styles	List style presets table
python3 banner_engine.py --compare <text>	Side-by-side font comparison
python3 banner_engine.py --export <text>	Render all fonts to files
python3 banner_engine.py --interactive	Full interactive menu
python3 banner_engine.py --help	Show command reference
Interactive Mode
Run without arguments to launch the interactive CLI:

python3 banner_engine.py

Input	Action
<text>	Enter font + style prompts
fonts	List all fonts
styles	Show style presets
sizes	Terminal size info
compare <text>	Font comparison
export <text>	Batch render
quit	Exit
🎨 Style Presets
All 18 presets you can use:

Preset	Color	Border	Alignment
default	white	Rounded	left
minimal	dim	Minimal	left
clean	cyan	Square	left
boxed	yellow	Double	left
heavy	red	Heavy	left
neon-blue	bright_blue	Double Edge	center
neon-green	bright_green	Double Edge	center
neon-pink	bright_magenta	Double Edge	center
cyber	blue	ASCII Double Head	center
matrix	green	Minimal Double Head	left
elegant	magenta	Rounded	center
royal	blue	Double	center
shadow	bright_black	Simple Head	left
retro	bright_yellow	ASCII	center
arcade	bright_cyan	Double	center
comic	bright_red	Rounded	center
bare	white	none	left
bare-center	cyan	none	center
Bonus: Any Rich color name works as a style input too! Type raw colors like bright_yellow, sea_green1, or orange_red1.

🔧 Programmatic Usage
Import and use the engine directly in your Python projects:

from banner_engine import ASCIIBannerEngine, StyleManager, SizeManager

# Initialize
engine = ASCIIBannerEngine()

# Generate banner
art = engine.generate("TRUTH", font="big", auto_fit=True)
print(art)

# Display with style
engine.display_banner("TRUTH", font="standard", style="neon-green")

# Get all fonts
for key, figlet_name in engine.FONTS.items():
    print(f"{key}: {figlet_name}")

# Export all fonts
engine.render_all_fonts("MY_PROJECT", output_dir="./banners")

# Use SizeManager directly
sizer = SizeManager()
print(sizer.report())
print(sizer.usable_width)

# Test auto-fit font
best_font = sizer.auto_fit_font("LONGER TEXT", preferred_font="big")
print(f"Best fit: {best_font}")

# List style presets
print(StyleManager.list_presets())

Custom Font + Style
# Override alignment
engine.display_banner("CENTERED", font="small", style="neon-pink", align="center")

# Use custom color (not in presets)
engine.display_banner("CUSTOM", font="ghost", style="spring_green2")

📊 Font Catalog
Curated Aliases (5)
Alias Key	Actual FIGlet Name	Purpose
3d	3-d	Readable shorthand
isomeric	isometric1	Cleaner naming
technology	4x4_offr	Cryptic name fix
fireball	fire_font-s	Thematic alias
pump	puffy	Typo fix
Font Families (Examples)
Large / Bold:

big, block, colossal, epic, doh, 3d, isometric1-4, henry_3d, letters
Small / Compact:

small, mini, term, stop, alphabet, rectangles, smkeyboard, smslant
Tech / Digital:

digital, binary, lcd, dotmatrix, hex, eftirobot, eftiwater, eftiwall, cyberlarge/medium/small
Decorative / Themed:

ghost, starwars, cosmic, graffiti, script, rounded, univers, o8, gothic
AMC Series (Arne Hoffmann):

amc_razor, amc_razor2, amc_tubes, amc_neko, amc_3_liv1
NancyJ (Hacker Aesthetic):

nancyj, nancyj_fancy, nancyj_improved, nancyj_underlined
See full list with:

python3 banner_engine.py --fonts

⚙️ Advanced Configuration
SizeManager Tuning
from banner_engine import SizeManager, ASCIIBannerEngine

# Custom width constraints
sizer = SizeManager(min_width=30, max_width=100)
engine = ASCIIBannerEngine(size_manager=sizer)

Custom Fallback Order
# Change the order SizeManager tries when auto-fit fails
fallback = ["preferred", "small", "tiny", "digital"]
font_key = sizer.auto_fit_font(text, preferred_font="big", fallback_order=fallback)

Padding & Alignment
# Manually pad a banner
padded = sizer.pad_banner(ascii_art, align="center", h_pad=3, v_pad=1)

🛠️ Troubleshooting
Problem	Solution
ModuleNotFoundError: No module named 'pyfiglet'	Run pip install pyfiglet rich
Font not found	Use --fonts to list available keys. Some may have spaces/hyphens
Banner overflows terminal	Enable auto_fit=True or use smaller fonts like small, mini
Colors don't show	Ensure your terminal supports ANSI colors (most do)
UnicodeEncodeError on Windows	Set PYTHONIOENCODING=utf-8 environment variable
📁 Project Structure
ASCII_Banner_Engine/
├── banner_engine.py          # Main engine (571 fonts + full CLI)
├── banner_output/            # Generated font renders from --export
│   ├── standard.txt
│   ├── big.txt
│   └── ... (571 files)
└── README.md                 # This file

🔗 Inspiration & Credits
pyfiglet — The legendary ASCII art font library (571 fonts)
Rich — Beautiful Python terminal formatting
ASCII Art Archive — Historical font collection
📄 License
MIT — Free to use, modify, and distribute.

---

## 🚧 Roadmap

Potential future features:

- [ ] Gradient color banners (multi-color lines)
- [ ] Animation frames (cycle fonts/styles)
- [ ] YAML config for saved font+style profiles
- [ ] Web API endpoint (Flask/FastAPI)
- [ ] Image export (PNG/JPEG via Pillow)
- [ ] Plugin system for custom renderers

---

**Go ahead and create some art.**

**SUDOER - Alex** — Honesty first. Audit everything. If it's not real, it doesn't belong.
