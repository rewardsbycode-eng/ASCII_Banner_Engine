#!/usr/bin/env python3
"""
ASCII Banner Engine
===================
Generate stunning ASCII text banners with 571+ pyfiglet fonts, 18 style presets,
and intelligent terminal sizing. Built with Python, Rich, and pyfiglet.

Features:
  - 571+ auto-loaded fonts
  - 18 style presets
  - SizeManager with auto-fit, truncation, and padding
  - Full CLI (--demo, --themes, --styles, --sizes, --compare, --fonts,
               --export, --interactive, --gradient, --animate, --profile,
               --png, --plugins)
  - Interactive menu
  - Export mode
  - Gradient renderer
  - Animation engine
  - YAML config / profile system
  - PNG image export
  - Plugin system
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pyfiglet
from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# ---------------------------------------------------------------------------
# Optional dependency guards
# ---------------------------------------------------------------------------
try:
    import yaml  # type: ignore

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont  # type: ignore

    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# ---------------------------------------------------------------------------
# Global console
# ---------------------------------------------------------------------------
console = Console()

# ---------------------------------------------------------------------------
# Style presets (18 presets)
# ---------------------------------------------------------------------------
STYLE_PRESETS: Dict[str, Dict] = {
    "neon-green": {"color": "bright_green", "border": box.DOUBLE, "border_style": "green"},
    "cyber-blue": {"color": "bright_blue", "border": box.HEAVY, "border_style": "blue"},
    "fire-red": {"color": "bright_red", "border": box.DOUBLE_EDGE, "border_style": "red"},
    "gold": {"color": "bright_yellow", "border": box.SQUARE, "border_style": "yellow"},
    "purple-haze": {"color": "bright_magenta", "border": box.ROUNDED, "border_style": "magenta"},
    "ice": {"color": "bright_cyan", "border": box.SIMPLE_HEAVY, "border_style": "cyan"},
    "white-noise": {"color": "bright_white", "border": box.MINIMAL, "border_style": "white"},
    "matrix": {"color": "green", "border": box.ASCII, "border_style": "green"},
    "sunset": {"color": "yellow", "border": box.HEAVY_HEAD, "border_style": "magenta"},
    "ocean": {"color": "cyan", "border": box.SIMPLE, "border_style": "blue"},
    "lava": {"color": "red", "border": box.MARKDOWN, "border_style": "red"},
    "midnight": {"color": "blue", "border": box.HORIZONTALS, "border_style": "blue"},
    "forest": {"color": "dark_green", "border": box.SQUARE, "border_style": "green"},
    "rose": {"color": "magenta", "border": box.ROUNDED, "border_style": "magenta"},
    "toxic": {"color": "yellow_green" if hasattr(box, "DOUBLE") else "bright_green", "border": box.DOUBLE, "border_style": "green"},
    "void": {"color": "grey50", "border": box.MINIMAL_DOUBLE_HEAD, "border_style": "white"},
    "retro": {"color": "orange1", "border": box.HEAVY_EDGE, "border_style": "yellow"},
    "ultraviolet": {"color": "medium_purple1", "border": box.DOUBLE, "border_style": "magenta"},
}

# ---------------------------------------------------------------------------
# Gradient presets
# ---------------------------------------------------------------------------
GRADIENT_PRESETS: Dict[str, List[str]] = {
    "fire": ["red", "bright_red", "dark_orange", "orange1", "bright_yellow"],
    "ocean": ["blue", "bright_blue", "cyan", "bright_cyan"],
    "matrix": ["green", "bright_green", "green3", "bright_green"],
    "sunset": ["magenta", "bright_magenta", "dark_orange", "bright_yellow"],
    "ice": ["white", "bright_white", "bright_cyan", "bright_blue"],
}

# ---------------------------------------------------------------------------
# SizeManager
# ---------------------------------------------------------------------------
TERMINAL_WIDTH = shutil.get_terminal_size((120, 40)).columns


class SizeManager:
    """Manages banner sizing: auto-fit, truncation, and padding."""

    def __init__(self, max_width: int = TERMINAL_WIDTH):
        self.max_width = max_width

    def fit_font(self, text: str, font: str) -> str:
        """Return the rendered ASCII art, auto-fitting to terminal width."""
        art = pyfiglet.figlet_format(text, font=font)
        lines = art.splitlines()
        if not lines:
            return art
        widest = max(len(l) for l in lines)
        if widest <= self.max_width:
            return art
        # Truncate each line
        truncated = [l[: self.max_width] for l in lines]
        return "\n".join(truncated)

    def pad(self, art: str, padding: int = 1) -> str:
        """Add horizontal padding to each line."""
        pad_str = " " * padding
        return "\n".join(pad_str + l for l in art.splitlines())

    def center(self, art: str) -> str:
        """Center each line within terminal width."""
        return "\n".join(l.center(self.max_width) for l in art.splitlines())


# ---------------------------------------------------------------------------
# Plugin loader
# ---------------------------------------------------------------------------
class PluginManager:
    """Auto-discovers and loads plugins from the ./plugins/ directory."""

    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, object] = {}
        self._load_plugins()

    def _load_plugins(self) -> None:
        """Load all .py files from the plugins directory."""
        if not self.plugins_dir.exists():
            return
        for path in sorted(self.plugins_dir.glob("*.py")):
            if path.name.startswith("_"):
                continue
            try:
                spec = importlib.util.spec_from_file_location(path.stem, path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)  # type: ignore[union-attr]
                    if hasattr(module, "render"):
                        self.plugins[path.stem] = module
            except Exception as exc:  # noqa: BLE001
                console.print(f"[yellow]Warning: failed to load plugin {path.name}: {exc}[/yellow]")

    def list_plugins(self) -> List[str]:
        """Return list of loaded plugin names."""
        return list(self.plugins.keys())

    def run(self, name: str, text: str, **kwargs) -> Optional[str]:
        """Run a plugin's render() method."""
        plugin = self.plugins.get(name)
        if plugin is None:
            return None
        try:
            return plugin.render(text, **kwargs)  # type: ignore[union-attr]
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Plugin {name} error: {exc}[/red]")
            return None


# ---------------------------------------------------------------------------
# Config / Profile loader
# ---------------------------------------------------------------------------
DEFAULT_CONFIG_YAML = """\
# ASCII Banner Engine - Profile Configuration
# Define named profiles for font+style combinations.
# Usage: python banner_engine.py --profile hero "My Text"
#
# Each profile supports:
#   font:    any pyfiglet font name (e.g. big, banner, slant)
#   style:   one of the 18 style presets
#   align:   left | center | right

profiles:
  hero:
    font: big
    style: neon-green
    align: center

  retro:
    font: banner3
    style: retro
    align: left

  ocean-wave:
    font: slant
    style: ocean
    align: center

  fire-lord:
    font: block
    style: fire-red
    align: center

  ice-king:
    font: lean
    style: ice
    align: center
"""

CONFIG_PATH = Path("config.yaml")


def load_config() -> Dict:
    """Load profiles from config.yaml. Returns empty dict if not available."""
    if not YAML_AVAILABLE:
        return {}
    if not CONFIG_PATH.exists():
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return data.get("profiles", {})
    except Exception as exc:  # noqa: BLE001
        console.print(f"[yellow]Warning: could not load config.yaml: {exc}[/yellow]")
        return {}


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------
class ASCIIBannerEngine:
    """
    Core ASCII Banner Engine.

    Responsibilities:
      - Render banners with pyfiglet + Rich styling
      - Provide gradient rendering
      - Provide animation cycling
      - Expose PNG export
      - Expose plugin interface
    """

    ALL_FONTS: List[str] = pyfiglet.FigletFont.getFonts()

    def __init__(self) -> None:
        self.size_manager = SizeManager()
        self.profiles: Dict = load_config()
        self.plugin_manager = PluginManager()

    # ------------------------------------------------------------------
    # Core render
    # ------------------------------------------------------------------
    def render(
        self,
        text: str,
        font: str = "banner3",
        style: str = "neon-green",
        align: str = "center",
        show_panel: bool = True,
    ) -> None:
        """Render an ASCII banner with the given font and style preset."""
        preset = STYLE_PRESETS.get(style, STYLE_PRESETS["neon-green"])
        art = self.size_manager.fit_font(text, font)
        rich_text = Text(art, style=preset["color"], justify=align)
        if show_panel:
            panel = Panel(
                Align(rich_text, align=align),
                border_style=preset["border_style"],
                box=preset["border"],
                expand=False,
            )
            console.print(panel)
        else:
            console.print(rich_text)

    def render_to_string(self, text: str, font: str = "banner3") -> str:
        """Return raw ASCII art string without Rich markup."""
        return self.size_manager.fit_font(text, font)

    # ------------------------------------------------------------------
    # Gradient renderer
    # ------------------------------------------------------------------
    def render_gradient(
        self,
        text: str,
        font: str = "banner3",
        gradient_name: str = "fire",
    ) -> None:
        """
        Render a multi-color ASCII banner where each line shifts hue.

        Gradient presets: fire, ocean, matrix, sunset, ice.
        """
        colors = GRADIENT_PRESETS.get(gradient_name, GRADIENT_PRESETS["fire"])
        art = self.size_manager.fit_font(text, font)
        lines = art.splitlines()
        if not lines:
            console.print("[red]No output for that font/text combination.[/red]")
            return

        n = len(lines)
        result = Text()
        for i, line in enumerate(lines):
            color = colors[int(i / max(n - 1, 1) * (len(colors) - 1))]
            result.append(line + "\n", style=color)

        panel = Panel(
            result,
            title=f"[bold]Gradient: {gradient_name}[/bold]",
            border_style=colors[-1],
            box=box.DOUBLE,
            expand=False,
        )
        console.print(panel)

    # ------------------------------------------------------------------
    # Animation engine
    # ------------------------------------------------------------------
    def animate_banner(
        self,
        text: str,
        fonts_list: Optional[List[str]] = None,
        interval: float = 0.5,
        loop: bool = False,
        style: str = "neon-green",
    ) -> None:
        """
        Cycle through fonts frame-by-frame for terminal demos.

        Args:
            text:       Text to render.
            fonts_list: List of fonts to cycle. Defaults to a curated set.
            interval:   Seconds between frames (fps = 1/interval).
            loop:       If True, loop indefinitely (Ctrl-C to stop).
            style:      Style preset name.
        """
        if fonts_list is None:
            fonts_list = [
                "banner3", "big", "block", "bubble", "digital",
                "isometric1", "lean", "mini", "shadow", "slant",
            ]
        preset = STYLE_PRESETS.get(style, STYLE_PRESETS["neon-green"])

        def _show_frame(font: str) -> None:
            console.clear()
            art = self.size_manager.fit_font(text, font)
            rich_text = Text(art, style=preset["color"])
            panel = Panel(
                Align(rich_text, align="center"),
                title=f"[bold]Font: {font}[/bold]",
                border_style=preset["border_style"],
                box=preset["border"],
                expand=False,
            )
            console.print(panel)
            console.print(f"[grey50]Press Ctrl-C to stop  |  interval={interval}s[/grey50]")

        try:
            if loop:
                while True:
                    for font in fonts_list:
                        _show_frame(font)
                        time.sleep(interval)
            else:
                for font in fonts_list:
                    _show_frame(font)
                    time.sleep(interval)
        except KeyboardInterrupt:
            console.print("\n[yellow]Animation stopped.[/yellow]")

    # ------------------------------------------------------------------
    # PNG export
    # ------------------------------------------------------------------
    def export_png(
        self,
        text: str,
        font: str = "banner3",
        output_path: str = "banner.png",
        bg_color: str = "#000000",
        text_color: str = "#00FF00",
        font_size: int = 20,
        padding: int = 20,
    ) -> None:
        """
        Export the banner as a PNG image using Pillow.

        Args:
            text:        Text to render.
            font:        pyfiglet font name.
            output_path: Destination file path.
            bg_color:    Background color (hex or name).
            text_color:  Text color (hex or name).
            font_size:   Font size for the monospace system font.
            padding:     Pixel padding around the text.
        """
        if not PILLOW_AVAILABLE:
            console.print(
                "[red]Pillow is not installed. Install it with: pip install Pillow[/red]"
            )
            return

        art = self.size_manager.fit_font(text, font)
        lines = art.splitlines()

        # Try to get a monospace system font, fall back to default
        img_font: ImageFont.ImageFont | ImageFont.FreeTypeFont
        try:
            img_font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
        except OSError:
            try:
                img_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", font_size)
            except OSError:
                img_font = ImageFont.load_default()

        # Measure text size
        dummy = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(dummy)
        line_heights: List[int] = []
        line_widths: List[int] = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=img_font)
            line_widths.append(bbox[2] - bbox[0])
            line_heights.append(bbox[3] - bbox[1])

        img_w = max(line_widths, default=100) + padding * 2
        line_h = max(line_heights, default=font_size) + 2
        img_h = line_h * len(lines) + padding * 2

        img = Image.new("RGB", (img_w, img_h), color=bg_color)
        draw = ImageDraw.Draw(img)

        y = padding
        for line in lines:
            draw.text((padding, y), line, fill=text_color, font=img_font)
            y += line_h

        img.save(output_path)
        console.print(f"[green]PNG saved to: {output_path}[/green]")

    # ------------------------------------------------------------------
    # Profile rendering
    # ------------------------------------------------------------------
    def render_profile(self, profile_name: str, text: str) -> None:
        """Render using a named profile from config.yaml."""
        if not YAML_AVAILABLE:
            console.print("[red]PyYAML is not installed. Install with: pip install pyyaml[/red]")
            return
        profile = self.profiles.get(profile_name)
        if profile is None:
            console.print(f"[red]Profile '{profile_name}' not found in config.yaml[/red]")
            console.print(f"Available profiles: {', '.join(self.profiles.keys()) or 'none'}")
            return
        font = profile.get("font", "banner3")
        style = profile.get("style", "neon-green")
        align = profile.get("align", "center")
        self.render(text, font=font, style=style, align=align)

    # ------------------------------------------------------------------
    # Demo / info helpers
    # ------------------------------------------------------------------
    def demo(self) -> None:
        """Run a quick demonstration of multiple styles."""
        demo_text = "DEMO"
        for i, (style_name, _) in enumerate(STYLE_PRESETS.items()):
            if i >= 6:
                break
            console.rule(f"[bold]Style: {style_name}[/bold]")
            self.render(demo_text, font="banner3", style=style_name)

    def show_themes(self) -> None:
        """Display all theme/style presets in a table."""
        table = Table(title="Available Style Presets", box=box.ROUNDED, border_style="cyan")
        table.add_column("Name", style="bold", no_wrap=True)
        table.add_column("Color", style="white")
        table.add_column("Border Style", style="white")
        for name, preset in STYLE_PRESETS.items():
            table.add_row(name, preset["color"], preset["border_style"])
        console.print(table)

    def show_styles(self) -> None:
        """Alias for show_themes."""
        self.show_themes()

    def show_sizes(self) -> None:
        """Display terminal size info."""
        w = shutil.get_terminal_size((120, 40)).columns
        h = shutil.get_terminal_size((120, 40)).lines
        table = Table(title="Terminal Size Info", box=box.ROUNDED, border_style="blue")
        table.add_column("Property", style="bold")
        table.add_column("Value", style="green")
        table.add_row("Terminal Width", str(w))
        table.add_row("Terminal Height", str(h))
        table.add_row("Max Banner Width", str(self.size_manager.max_width))
        console.print(table)

    def compare_fonts(self, text: str, fonts: Optional[List[str]] = None) -> None:
        """Compare multiple fonts side-by-side."""
        if fonts is None:
            fonts = ["banner3", "big", "block", "bubble", "digital", "slant"]
        for font in fonts:
            console.rule(f"[bold cyan]Font: {font}[/bold cyan]")
            try:
                self.render(text, font=font, style="cyber-blue", show_panel=True)
            except Exception as exc:  # noqa: BLE001
                console.print(f"[yellow]Skipped font {font}: {exc}[/yellow]")

    def list_fonts(self, limit: int = 50) -> None:
        """List available pyfiglet fonts."""
        fonts = self.ALL_FONTS[:limit]
        table = Table(title=f"Available Fonts (showing {limit} of {len(self.ALL_FONTS)})", box=box.SIMPLE)
        table.add_column("Font Name", style="cyan", no_wrap=True)
        for f in fonts:
            table.add_row(f)
        console.print(table)

    def export_text(self, text: str, font: str, style: str, output_path: str) -> None:
        """Export the rendered art to a plain-text file."""
        art = self.render_to_string(text, font)
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(art)
        console.print(f"[green]Exported to: {output_path}[/green]")

    def show_gradients(self) -> None:
        """Display all gradient presets."""
        table = Table(title="Gradient Presets", box=box.ROUNDED, border_style="magenta")
        table.add_column("Name", style="bold", no_wrap=True)
        table.add_column("Colors", style="white")
        for name, colors in GRADIENT_PRESETS.items():
            table.add_row(name, " → ".join(colors))
        console.print(table)

    def show_plugins(self) -> None:
        """Display loaded plugins."""
        plugins = self.plugin_manager.list_plugins()
        table = Table(title="Loaded Plugins", box=box.ROUNDED, border_style="yellow")
        table.add_column("Plugin Name", style="bold cyan", no_wrap=True)
        if plugins:
            for p in plugins:
                table.add_row(p)
        else:
            table.add_row("[grey50]No plugins found[/grey50]")
        console.print(table)

    # ------------------------------------------------------------------
    # Interactive menu
    # ------------------------------------------------------------------
    def interactive_menu(self) -> None:
        """Launch the interactive ASCII banner menu."""
        console.print(
            Panel(
                "[bold bright_green]ASCII Banner Engine - Interactive Mode[/bold bright_green]\n"
                "[grey50]Type 'help' for commands, 'quit' to exit.[/grey50]",
                box=box.DOUBLE,
                border_style="green",
            )
        )

        while True:
            try:
                cmd = console.input("\n[bold cyan]banner>[/bold cyan] ").strip()
            except (EOFError, KeyboardInterrupt):
                console.print("\n[yellow]Goodbye![/yellow]")
                break

            if not cmd:
                continue

            parts = cmd.split(None, 1)
            verb = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if verb in ("quit", "exit", "q"):
                console.print("[yellow]Goodbye![/yellow]")
                break

            elif verb == "help":
                self._interactive_help()

            elif verb == "render":
                if not arg:
                    console.print("[red]Usage: render <text>[/red]")
                else:
                    self.render(arg)

            elif verb == "font":
                # font <font_name> <text>
                sub = arg.split(None, 1)
                if len(sub) < 2:
                    console.print("[red]Usage: font <font_name> <text>[/red]")
                else:
                    self.render(sub[1], font=sub[0])

            elif verb == "style":
                # style <style_name> <text>
                sub = arg.split(None, 1)
                if len(sub) < 2:
                    console.print("[red]Usage: style <style_name> <text>[/red]")
                else:
                    self.render(sub[1], style=sub[0])

            elif verb == "gradient":
                # gradient <gradient_name> <text>
                sub = arg.split(None, 1)
                if len(sub) < 2:
                    console.print("[red]Usage: gradient <gradient_name> <text>[/red]")
                else:
                    self.render_gradient(sub[1], gradient_name=sub[0])

            elif verb == "animate":
                if not arg:
                    console.print("[red]Usage: animate <text>[/red]")
                else:
                    self.animate_banner(arg)

            elif verb == "profile":
                sub = arg.split(None, 1)
                if len(sub) < 2:
                    console.print("[red]Usage: profile <profile_name> <text>[/red]")
                else:
                    self.render_profile(sub[0], sub[1])

            elif verb == "png":
                sub = arg.split(None, 1)
                if len(sub) < 1:
                    console.print("[red]Usage: png <text>[/red]")
                else:
                    self.export_png(arg, output_path="banner.png")

            elif verb == "themes":
                self.show_themes()

            elif verb == "styles":
                self.show_styles()

            elif verb == "fonts":
                self.show_fonts_interactive()

            elif verb == "sizes":
                self.show_sizes()

            elif verb == "gradients":
                self.show_gradients()

            elif verb == "plugins":
                self.show_plugins()

            elif verb == "demo":
                self.demo()

            elif verb == "compare":
                if not arg:
                    console.print("[red]Usage: compare <text>[/red]")
                else:
                    self.compare_fonts(arg)

            else:
                console.print(f"[red]Unknown command: {verb}. Type 'help' for commands.[/red]")

    def show_fonts_interactive(self) -> None:
        """Show fonts interactively with pagination."""
        total = len(self.ALL_FONTS)
        page_size = 20
        page = 0
        while True:
            start = page * page_size
            end = min(start + page_size, total)
            table = Table(
                title=f"Fonts {start + 1}–{end} of {total}",
                box=box.SIMPLE,
                border_style="cyan",
            )
            table.add_column("#", style="grey50", no_wrap=True)
            table.add_column("Font Name", style="cyan", no_wrap=True)
            for i, f in enumerate(self.ALL_FONTS[start:end], start=start + 1):
                table.add_row(str(i), f)
            console.print(table)
            console.print("[grey50](n)ext  (p)rev  (q)uit[/grey50]")
            try:
                nav = console.input("[bold cyan]fonts>[/bold cyan] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                break
            if nav in ("q", "quit"):
                break
            elif nav == "n" and end < total:
                page += 1
            elif nav == "p" and page > 0:
                page -= 1

    def _interactive_help(self) -> None:
        """Print help for interactive mode."""
        table = Table(title="Interactive Commands", box=box.ROUNDED, border_style="green")
        table.add_column("Command", style="bold cyan", no_wrap=True)
        table.add_column("Description", style="white")
        cmds = [
            ("render <text>", "Render text with default settings"),
            ("font <font> <text>", "Render with specific font"),
            ("style <style> <text>", "Render with specific style preset"),
            ("gradient <preset> <text>", "Render with gradient colors"),
            ("animate <text>", "Animate through fonts"),
            ("profile <name> <text>", "Render using a named config profile"),
            ("png <text>", "Export banner as banner.png"),
            ("themes", "List all style presets"),
            ("styles", "Alias for themes"),
            ("fonts", "Browse all fonts"),
            ("sizes", "Show terminal size info"),
            ("gradients", "List gradient presets"),
            ("plugins", "List loaded plugins"),
            ("demo", "Run a quick demo"),
            ("compare <text>", "Compare multiple fonts"),
            ("help", "Show this help"),
            ("quit / exit", "Exit interactive mode"),
        ]
        for cmd, desc in cmds:
            table.add_row(cmd, desc)
        console.print(table)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="banner_engine",
        description="ASCII Banner Engine — generate stunning ASCII banners",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python banner_engine.py "Hello World"
  python banner_engine.py --font slant --style cyber-blue "DEMO"
  python banner_engine.py --demo
  python banner_engine.py --gradient fire "FIRE"
  python banner_engine.py --animate "COOL"
  python banner_engine.py --profile hero "My Title"
  python banner_engine.py --png "Banner" --png-output banner.png
  python banner_engine.py --plugins
""",
    )

    # Core text arg
    parser.add_argument("text", nargs="?", default=None, help="Text to render as ASCII banner")

    # Existing flags
    parser.add_argument("--font", default="banner3", help="pyfiglet font name (default: banner3)")
    parser.add_argument("--style", default="neon-green", help="Style preset name (default: neon-green)")
    parser.add_argument("--align", default="center", choices=["left", "center", "right"], help="Text alignment")
    parser.add_argument("--demo", action="store_true", help="Run a quick style demo")
    parser.add_argument("--themes", action="store_true", help="List all style presets / themes")
    parser.add_argument("--styles", action="store_true", help="List all style presets (alias for --themes)")
    parser.add_argument("--sizes", action="store_true", help="Show terminal size information")
    parser.add_argument("--compare", metavar="TEXT", help="Compare multiple fonts on TEXT")
    parser.add_argument("--fonts", action="store_true", help="List available fonts")
    parser.add_argument(
        "--export",
        metavar="OUTPUT",
        help="Export rendered banner to a plain-text file",
    )
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive menu")

    # New flags
    parser.add_argument(
        "--gradient",
        metavar="PRESET",
        help="Render with gradient colors (fire|ocean|matrix|sunset|ice)",
    )
    parser.add_argument(
        "--animate",
        metavar="TEXT",
        help="Animate TEXT by cycling through fonts",
    )
    parser.add_argument(
        "--animate-interval",
        type=float,
        default=0.5,
        metavar="SECONDS",
        help="Seconds between animation frames (default: 0.5)",
    )
    parser.add_argument(
        "--animate-loop",
        action="store_true",
        help="Loop animation indefinitely (Ctrl-C to stop)",
    )
    parser.add_argument(
        "--profile",
        metavar="NAME",
        help="Render using a named profile from config.yaml",
    )
    parser.add_argument(
        "--png",
        metavar="TEXT",
        help="Export TEXT as a PNG image",
    )
    parser.add_argument("--png-output", default="banner.png", metavar="PATH", help="PNG output path (default: banner.png)")
    parser.add_argument("--png-bg", default="#000000", metavar="COLOR", help="PNG background color (default: #000000)")
    parser.add_argument("--png-fg", default="#00FF00", metavar="COLOR", help="PNG text color (default: #00FF00)")
    parser.add_argument("--png-font-size", type=int, default=20, metavar="SIZE", help="PNG font size in pixels (default: 20)")
    parser.add_argument("--png-padding", type=int, default=20, metavar="PX", help="PNG padding in pixels (default: 20)")
    parser.add_argument(
        "--plugins",
        action="store_true",
        help="List loaded plugins",
    )
    parser.add_argument(
        "--gradients",
        action="store_true",
        help="List available gradient presets",
    )

    return parser


def main() -> None:
    """Entry point for the ASCII Banner Engine CLI."""
    parser = build_parser()
    args = parser.parse_args()

    engine = ASCIIBannerEngine()

    # ---- Existing flags ----
    if args.demo:
        engine.demo()
        return

    if args.themes or args.styles:
        engine.show_themes()
        return

    if args.sizes:
        engine.show_sizes()
        return

    if args.compare:
        engine.compare_fonts(args.compare)
        return

    if args.fonts:
        engine.list_fonts(limit=100)
        return

    if args.interactive:
        engine.interactive_menu()
        return

    # ---- New flags ----
    if args.gradients:
        engine.show_gradients()
        return

    if args.plugins:
        engine.show_plugins()
        return

    if args.gradient:
        text = args.text or "BANNER"
        engine.render_gradient(text, font=args.font, gradient_name=args.gradient)
        return

    if args.animate:
        engine.animate_banner(
            args.animate,
            interval=args.animate_interval,
            loop=args.animate_loop,
            style=args.style,
        )
        return

    if args.profile:
        text = args.text or "BANNER"
        engine.render_profile(args.profile, text)
        return

    if args.png:
        engine.export_png(
            args.png,
            font=args.font,
            output_path=args.png_output,
            bg_color=args.png_bg,
            text_color=args.png_fg,
            font_size=args.png_font_size,
            padding=args.png_padding,
        )
        return

    if args.export:
        text = args.text or "BANNER"
        engine.export_text(text, font=args.font, style=args.style, output_path=args.export)
        return

    # ---- Default: render text ----
    if args.text:
        engine.render(args.text, font=args.font, style=args.style, align=args.align)
    else:
        # No args — show a welcome banner
        engine.render("ASCII Engine", font="banner3", style="neon-green")
        console.print("\n[grey50]Run with --help for usage information.[/grey50]")


if __name__ == "__main__":
    main()
