# ASCII_Banner_Engine
Generate stunning ASCII text banners with 571+ pyfiglet fonts, 18 style presets, and intelligent terminal sizing. Built with Python, Rich, and pyfiglet.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
python banner_engine.py "Hello World"
python banner_engine.py --font slant --style cyber-blue "DEMO"
python banner_engine.py --demo
python banner_engine.py --interactive
```

## CLI Flags

| Flag | Description |
|------|-------------|
| `--demo` | Run a quick style demo |
| `--themes` / `--styles` | List all 18 style presets |
| `--sizes` | Show terminal size information |
| `--compare TEXT` | Compare multiple fonts on TEXT |
| `--fonts` | List available fonts |
| `--export OUTPUT` | Export rendered banner to plain-text file |
| `--interactive` / `-i` | Launch interactive menu |
| `--font NAME` | pyfiglet font name (default: banner3) |
| `--style NAME` | Style preset name (default: neon-green) |
| `--align left\|center\|right` | Text alignment |

## Style Presets (18)

`neon-green`, `cyber-blue`, `fire-red`, `gold`, `purple-haze`, `ice`,
`white-noise`, `matrix`, `sunset`, `ocean`, `lava`, `midnight`, `forest`,
`rose`, `toxic`, `void`, `retro`, `ultraviolet`

---

## New Features

### 1. Gradient Renderer

Render multi-color banners where each line shifts hue from top to bottom.

**Gradient presets:** `fire`, `ocean`, `matrix`, `sunset`, `ice`

```bash
python banner_engine.py --gradient fire "FIRE"
python banner_engine.py --gradient ocean --font slant "WAVE"
python banner_engine.py --gradients   # list all gradient presets
```

**API:**
```python
engine = ASCIIBannerEngine()
engine.render_gradient("Hello", font="big", gradient_name="fire")
```

---

### 2. Animation Engine

Cycle through fonts or styles frame-by-frame for terminal demos.

```bash
python banner_engine.py --animate "COOL"
python banner_engine.py --animate "DEMO" --animate-interval 0.3
python banner_engine.py --animate "LOOP" --animate-loop     # loops until Ctrl-C
```

**API:**
```python
engine.animate_banner(
    text="Hello",
    fonts_list=["big", "slant", "block"],
    interval=0.5,
    loop=False,
    style="neon-green",
)
```

---

### 3. YAML Config / Profile System

Define named font+style profiles in `config.yaml` and load them by name.

**`config.yaml` example:**
```yaml
profiles:
  hero:
    font: big
    style: neon-green
    align: center

  retro:
    font: banner3
    style: retro
    align: left
```

```bash
python banner_engine.py --profile hero "My Title"
```

**API:**
```python
engine.render_profile("hero", "My Title")
```

The engine auto-loads `config.yaml` on startup. Falls back gracefully if
`PyYAML` is not installed.

---

### 4. PNG Image Export

Export banners as PNG images using Pillow.

```bash
python banner_engine.py --png "Banner"
python banner_engine.py --png "Banner" --png-output out.png --png-bg "#1a1a2e" --png-fg "#e94560"
```

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--png TEXT` | — | Text to render as PNG |
| `--png-output PATH` | `banner.png` | Output file path |
| `--png-bg COLOR` | `#000000` | Background color |
| `--png-fg COLOR` | `#00FF00` | Text color |
| `--png-font-size SIZE` | `20` | Font size in pixels |
| `--png-padding PX` | `20` | Padding in pixels |

**API:**
```python
engine.export_png(
    text="Hello",
    font="big",
    output_path="banner.png",
    bg_color="#000000",
    text_color="#00FF00",
    font_size=20,
    padding=20,
)
```

Falls back gracefully if `Pillow` is not installed.

---

### 5. Plugin System

Drop-in modules in `./plugins/`. Each plugin is a `.py` file with a
`render(text, **kwargs) -> str` method. The engine auto-discovers and loads
all plugins on startup.

```bash
python banner_engine.py --plugins   # list loaded plugins
```

**Creating a plugin** (`plugins/my_plugin.py`):
```python
import pyfiglet

def render(text: str, font: str = "banner3", **kwargs) -> str:
    """My custom renderer."""
    art = pyfiglet.figlet_format(text, font=font)
    return art.upper()  # example transformation
```

**API:**
```python
result = engine.plugin_manager.run("my_plugin", "Hello")
print(result)
```

A sample plugin (`plugins/reverse_banner.py`) is included as a reference.

---

## Interactive Menu

```bash
python banner_engine.py --interactive
```

Available interactive commands:

| Command | Description |
|---------|-------------|
| `render <text>` | Render with default settings |
| `font <font> <text>` | Render with specific font |
| `style <style> <text>` | Render with specific style preset |
| `gradient <preset> <text>` | Render with gradient colors |
| `animate <text>` | Animate through fonts |
| `profile <name> <text>` | Render using a named config profile |
| `png <text>` | Export banner as banner.png |
| `themes` / `styles` | List all style presets |
| `fonts` | Browse all fonts with pagination |
| `sizes` | Show terminal size info |
| `gradients` | List gradient presets |
| `plugins` | List loaded plugins |
| `demo` | Run a quick demo |
| `compare <text>` | Compare multiple fonts |
| `help` | Show help |
| `quit` / `exit` | Exit |
