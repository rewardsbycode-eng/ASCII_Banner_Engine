from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text
from rich.align import Align
from pyfiglet import Figlet
import shutil
import os
import sys

console = Console()


# ═══════════════════════════════════════════════════════════════════════
#  SIZE MANAGER
# ═══════════════════════════════════════════════════════════════════════

class SizeManager:
    """
    Manages banner dimensions, terminal-fit logic, and scaling.
    """

    def __init__(self, max_width: int | None = None, min_width: int = 40):
        self._terminal_width = shutil.get_terminal_size((80, 24)).columns
        self.max_width = max_width or self._terminal_width
        self.min_width = min_width

    @property
    def terminal_width(self) -> int:
        return shutil.get_terminal_size((80, 24)).columns

    @property
    def usable_width(self) -> int:
        return max(self.min_width, self.terminal_width - 6)

    def refresh(self) -> None:
        self._terminal_width = self.terminal_width
        self.max_width = min(self.max_width, self.terminal_width)

    def measure_banner(self, ascii_art: str) -> int:
        if not ascii_art:
            return 0
        return max(len(line) for line in ascii_art.splitlines())

    def fits(self, ascii_art: str, margin: int = 0) -> bool:
        return self.measure_banner(ascii_art) <= (self.usable_width - margin)

    def auto_fit_font(self, text: str, preferred_font: str = "standard",
                      fallback_order: list[str] | None = None) -> str:
        if fallback_order is None:
            fallback_order = [
                preferred_font,
                "big", "standard", "slant", "small",
                "banner", "smkeyboard", "digital", "mini",
            ]
        seen = set()
        ordered = []
        for f in fallback_order:
            if f not in seen:
                ordered.append(f)
                seen.add(f)
        available = ASCIIBannerEngine.FONTS
        for font_key in ordered:
            if font_key not in available:
                continue
            fig = Figlet(font=available[font_key])
            art = fig.renderText(text)
            if self.fits(art):
                return font_key
        return ordered[-1] if ordered else "standard"

    def truncate_to_width(self, ascii_art: str, width: int | None = None) -> str:
        target = width or self.usable_width
        lines = ascii_art.splitlines()
        result = []
        for line in lines:
            if len(line) > target:
                result.append(line[:target - 1] + "\u2025")
            else:
                result.append(line)
        return "\n".join(result)

    def pad_banner(self, ascii_art: str, align: str = "left",
                   h_pad: int = 2, v_pad: int = 0) -> str:
        lines = ascii_art.splitlines()
        target_width = self.measure_banner(ascii_art) + (h_pad * 2)
        padded = []
        for _ in range(v_pad):
            padded.append("")
        for line in lines:
            stripped = line.rstrip()
            ln = len(stripped)
            if align == "center":
                left = (target_width - ln) // 2
                right = target_width - ln - left
                padded.append(" " * left + stripped + " " * right)
            elif align == "right":
                padded.append(" " * (target_width - ln) + stripped)
            else:
                padded.append(stripped + " " * (target_width - ln))
        for _ in range(v_pad):
            padded.append("")
        return "\n".join(padded)

    def report(self) -> str:
        return (
            f"Terminal: {self.terminal_width} cols | "
            f"Usable: {self.usable_width} cols | "
            f"Min: {self.min_width} | Max: {self.max_width}"
        )


# ═══════════════════════════════════════════════════════════════════════
#  STYLE MANAGER
# ═══════════════════════════════════════════════════════════════════════

class StyleManager:
    """
    Predefined style presets combining color, border style, alignment,
    and box characters.
    """

    PRESETS = {
        # ── Classic ──
        "default":     {"color": "white",          "border": box.ROUNDED,             "align": "left"},
        "minimal":     {"color": "dim",            "border": box.MINIMAL,             "align": "left"},
        "clean":       {"color": "cyan",           "border": box.SQUARE,              "align": "left"},
        "boxed":       {"color": "yellow",         "border": box.DOUBLE,              "align": "left"},
        "heavy":       {"color": "red",            "border": box.HEAVY,               "align": "left"},

        # ── Neon / Cyber ──
        "neon-blue":   {"color": "bright_blue",    "border": box.DOUBLE_EDGE,         "align": "center"},
        "neon-green":  {"color": "bright_green",   "border": box.DOUBLE_EDGE,         "align": "center"},
        "neon-pink":   {"color": "bright_magenta", "border": box.DOUBLE_EDGE,         "align": "center"},
        "cyber":       {"color": "blue",           "border": box.ASCII_DOUBLE_HEAD,   "align": "center"},
        "matrix":      {"color": "green",          "border": box.MINIMAL_DOUBLE_HEAD, "align": "left"},

        # ── Elegant ──
        "elegant":     {"color": "magenta",        "border": box.ROUNDED,             "align": "center"},
        "royal":       {"color": "blue",           "border": box.DOUBLE,              "align": "center"},
        "shadow":      {"color": "bright_black",   "border": box.SIMPLE_HEAD,         "align": "left"},

        # ── Playful ──
        "retro":       {"color": "bright_yellow",  "border": box.ASCII,               "align": "center"},
        "arcade":      {"color": "bright_cyan",    "border": box.DOUBLE,              "align": "center"},
        "comic":       {"color": "bright_red",     "border": box.ROUNDED,             "align": "center"},

        # ── Bare / No frame ──
        "bare":        {"color": "white",          "border": None,                    "align": "left"},
        "bare-center": {"color": "cyan",           "border": None,                    "align": "center"},
    }

    @classmethod
    def get(cls, name: str) -> dict:
        return cls.PRESETS.get(name, cls.PRESETS["default"])

    @classmethod
    def list_presets(cls) -> list[str]:
        return sorted(cls.PRESETS.keys())

    @classmethod
    def list_presets_table(cls) -> None:
        tbl = Table(
            title="[bold magenta]Style Presets[/bold magenta]",
            show_header=True,
            header_style="bold cyan",
            box=box.DOUBLE,
        )
        tbl.add_column("ID", justify="right", style="dim", width=3)
        tbl.add_column("Preset Name", style="bold yellow")
        tbl.add_column("Color", justify="center")
        tbl.add_column("Border", justify="center")
        tbl.add_column("Align", justify="center")

        border_names = {
            id(box.ROUNDED): "Rounded",
            id(box.DOUBLE): "Double",
            id(box.SQUARE): "Square",
            id(box.HEAVY): "Heavy",
            id(box.MINIMAL): "Minimal",
            id(box.MINIMAL_DOUBLE_HEAD): "Min-Double",
            id(box.DOUBLE_EDGE): "Dbl-Edge",
            id(box.ASCII): "ASCII",
            id(box.ASCII_DOUBLE_HEAD): "ASCII-Dbl",
            id(box.SIMPLE_HEAD): "Simple-Hd",
        }

        for i, name in enumerate(sorted(cls.PRESETS.keys())):
            s = cls.PRESETS[name]
            border_label = "None" if s["border"] is None else \
                            border_names.get(id(s["border"]), "?")
            tbl.add_row(
                str(i), name,
                f"[{s['color']}]{s['color']}[/{s['color']}]",
                border_label, s["align"],
            )
        console.print(tbl)


# ═══════════════════════════════════════════════════════════════════════
#  ASCII BANNER ENGINE
# ═══════════════════════════════════════════════════════════════════════

class ASCIIBannerEngine:
    """Multi-style ASCII banner generator using pyfiglet"""

    # Curated aliases — readable names for cryptic FIGlet font names
    _ALIASES = {
        "3d": "3-d",
        "isomeric": "isometric1",
        "technology": "4x4_offr",
        "fireball": "fire_font-s",
        "pump": "puffy",
    }

    # Auto-load all available FIGlet fonts, then layer aliases on top
    FONTS = {f: f for f in Figlet().getFonts()}
    FONTS.update(_ALIASES)

    def __init__(self, size_manager: SizeManager | None = None):
        self.sizer = size_manager or SizeManager()

    # ── Core generation ──────────────────────────────────────────────

    def generate(self, text: str, font: str = "standard",
                 auto_fit: bool = False) -> str | None:
        if font not in self.FONTS:
            console.print(f"[red]Font '{font}' not found. "
                          f"Use 'fonts' command to list available.[/red]")
            return None
        if auto_fit:
            font = self.sizer.auto_fit_font(text, preferred_font=font)
        fig = Figlet(font=self.FONTS[font])
        return fig.renderText(text)

    # ── Display ──────────────────────────────────────────────────────

    def display_banner(self, text: str, font: str = "standard",
                       style: str = "default",
                       auto_fit: bool = True,
                       align: str | None = None) -> None:
        # Resolve style — .copy() prevents mutating the class-level PRESETS
        if style in StyleManager.PRESETS:
            preset = StyleManager.get(style).copy()
        else:
            preset = {"color": style, "border": box.ROUNDED, "align": "left"}

        if align:
            preset["align"] = align

        ascii_art = self.generate(text, font, auto_fit=auto_fit)
        if ascii_art is None:
            return

        if not self.sizer.fits(ascii_art, margin=6):
            ascii_art = self.sizer.truncate_to_width(
                ascii_art, self.sizer.usable_width - 6)

        rich_text = Text(ascii_art, style=preset["color"])
        aligned = Align(rich_text, align=preset["align"])

        panel_title = (f"[bold {preset['color']}]\n"
            f"{font.upper()} . {style.upper()}\n"
            f"[/bold {preset['color']}]")

        if preset["border"] is None:
            console.print(aligned)
        else:
            panel = Panel(
                aligned,
                title=panel_title,
                border_style=preset["color"],
                box=preset["border"],
                padding=(1, 2),
            )
            console.print(panel)

    # ── Listing ──────────────────────────────────────────────────────

    def list_fonts(self) -> None:
        ref_table = Table(
            title=f"[bold magenta]Available ASCII Fonts ({len(self.FONTS)})[/bold magenta]",
            show_header=True,
            header_style="bold cyan",
            box=box.DOUBLE,
        )
        ref_table.add_column("ID", justify="right", style="dim", width=5)
        ref_table.add_column("Key", style="bold yellow")
        ref_table.add_column("FIGlet Name", style="dim")

        for i, (key, figlet_name) in enumerate(sorted(self.FONTS.items())):
            alias_tag = " [cyan](alias)[/cyan]" if key != figlet_name else ""
            ref_table.add_row(str(i), key, figlet_name + alias_tag)

        console.print(ref_table)

    def list_styles(self) -> None:
        StyleManager.list_presets_table()

    # ── Comparison ───────────────────────────────────────────────────
    def compare_fonts(self, text: str, fonts: list[str] | None = None) -> None:
        if fonts is None:
            fonts = [
                "standard", "slant", "big", "ghost",
                "digital", "small", "gothic", "bubble",
            ]

        preview_grid = Table(
            title="[bold green]Font Comparison Preview[/bold green]",
            box=box.MINIMAL_DOUBLE_HEAD,
            show_lines=True,
        )
        preview_grid.add_column("Font -> Preview", style="white")

        colors = ["bright_green", "bright_cyan", "bright_yellow",
                  "bright_magenta", "bright_blue", "bright_red",
                  "bright_white", "green"]

        for i, font_name in enumerate(fonts):
            if font_name not in self.FONTS:
                preview_grid.add_row(f"[red]x {font_name} (not found)[/red]")
                continue
            try:
                fig = Figlet(font=self.FONTS[font_name])
                preview = fig.renderText(text)
                preview_lines = preview.splitlines()
                if len(preview_lines) > 6:
                    preview = "\n".join(preview_lines[:6]) + "\n..."
                color = colors[i % len(colors)]
                cell = (f"[bold {color}]{font_name}[/bold {color}]\n"
                        f"[{color}]{preview}[/{color}]")
                preview_grid.add_row(cell)
            except Exception as e:
                preview_grid.add_row(f"[red]x {font_name} (error: {e})[/red]")

        console.print(preview_grid)

    # ── Batch / Export ───────────────────────────────────────────────

    def render_all_fonts(self, text: str, output_dir: str = "./banner_output") -> None:
        os.makedirs(output_dir, exist_ok=True)
        count = 0
        failed = 0
        for key, figlet_name in sorted(self.FONTS.items()):
            try:
                fig = Figlet(font=figlet_name)
                art = fig.renderText(text)
                safe_name = key.replace("/", "_").replace("\\", "_")
                path = os.path.join(output_dir, f"{safe_name}.txt")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"# Font: {key} -> {figlet_name}\n")
                    f.write(f"# Size: {self.sizer.measure_banner(art)} cols\n")
                    f.write(art)
                count += 1
            except Exception:
                console.print(f"[red]x Failed: {key} ({figlet_name})[/red]")
                failed += 1
        console.print(f"[green]Rendered {count} fonts to {output_dir}/[/green]")
        if failed:
            console.print(f"[red]{failed} fonts failed.[/red]")


# ═══════════════════════════════════════════════════════════════════════
#  DEMO FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def demo_basic_banners():
    engine = ASCIIBannerEngine()
    console.print("\n[bold blue]=== BASIC BANNERS (auto-fit ON) ===[/bold blue]\n")
    engine.display_banner("HELLO", "standard", "clean")
    engine.display_banner("WELCOME", "slant", "neon-green")
    engine.display_banner("AUTHOR", "big", "elegant")
    engine.display_banner("SYSTEM", "ghost", "neon-blue")


def demo_themed_banners():
    engine = ASCIIBannerEngine()
    themes = [
        ("CYBERPUNK", "speed",     "cyber"),
        ("GHOST",     "ghost",     "bare-center"),
        ("MATRIX",    "binary",    "matrix"),
        ("SPACE",     "starwars",  "neon-pink"),
        ("URBAN",     "graffiti",  "retro"),
        ("GOTHIC",    "gothic",    "royal"),
    ]
    console.print("\n[bold]=== THEMED COLLECTIONS ===[/bold]\n")
    for text, font, style in themes:
        engine.display_banner(text, font, style)
        console.print()


def demo_styles():
    engine = ASCIIBannerEngine()
    console.print("\n[bold magenta]=== STYLE PRESETS ===[/bold magenta]\n")
    StyleManager.list_presets_table()
    console.print()
    for style in ["minimal", "neon-green", "matrix", "royal", "arcade", "bare"]:
        engine.display_banner("STYLES", "slant", style)


def demo_size_manager():
    engine = ASCIIBannerEngine()
    sm = engine.sizer
    console.print(f"\n[bold cyan]=== SIZE MANAGER REPORT ===[/bold cyan]")
    console.print(f"  {sm.report()}\n")
    test_text = "AUTOFIT_TESTING_WIDE_BANNERS"
    console.print(f"[yellow]Testing text: '{test_text}'[/yellow]")
    best_font = sm.auto_fit_font(test_text, preferred_font="big")
    console.print(f"[green]Auto-fit selected: '{best_font}'[/green]\n")
    engine.display_banner(test_text, best_font, "clean", auto_fit=False)


# ═══════════════════════════════════════════════════════════════════════
#  INTERACTIVE MENU
# ═══════════════════════════════════════════════════════════════════════

def interactive_menu():
    engine = ASCIIBannerEngine()
    console.print("\n[bold reverse] ASCII BANNER ENGINE v2.0 [/bold reverse]")
    console.print(f"[dim]  {engine.sizer.report()}[/dim]")
    console.print(f"[dim]  {len(engine.FONTS)} fonts loaded[/dim]\n")

    while True:
        console.print("\n[bold cyan]Commands:[/bold cyan]")
        console.print("  [yellow]<text>[/yellow]          - generate banner")
        console.print("  [yellow]fonts[/yellow]           - list all fonts")
        console.print("  [yellow]styles[/yellow]          - list style presets")
        console.print("  [yellow]sizes[/yellow]           - show size info")
        console.print("  [yellow]compare <text>[/yellow]   - compare sample fonts")
        console.print("  [yellow]export <text>[/yellow]     - render all fonts to files")
        console.print("  [yellow]quit[/yellow]")

        raw = console.input("\n[bold yellow]> [/bold yellow]").strip()
        if not raw:
            continue

        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "quit":
            console.print("[green]Goodbye.[/green]")
            break
        elif cmd == "fonts":
            engine.list_fonts()
        elif cmd == "styles":
            engine.list_styles()
        elif cmd == "sizes":
            console.print(f"[cyan]{engine.sizer.report()}[/cyan]")
            best = engine.sizer.auto_fit_font("SAMPLE TEXT", "big")
            console.print(f"[green]Best fit for 'SAMPLE TEXT': {best}[/green]")
        elif cmd == "compare":
            engine.compare_fonts(arg or "Hello")
        elif cmd == "export":
            text = arg or "EXPORT_DEMO"
            engine.render_all_fonts(text)
        else:
            # Treat entire input as banner text
            text = raw
            console.print("\n[dim]Font (name or number 1-8):[/dim]")
            console.print("  1-standard 2-slant 3-big 4-ghost "
                          "5-banner 6-gothic 7-digital 8-small")
            font_choice = console.input("[bold]Font: [/bold]").strip().lower()
            font_map = {
                "1": "standard", "2": "slant", "3": "big",
                "4": "ghost", "5": "banner", "6": "gothic",
                "7": "digital", "8": "small",
            }
            font = font_map.get(font_choice, font_choice or "standard")

            console.print("[dim]Style (preset name or color):[/dim]")
            console.print(f"  {' | '.join(StyleManager.list_presets()[:8])}")
            style_choice = console.input("[bold]Style: [/bold]").strip().lower()
            style = style_choice or "default"

            engine.display_banner(text, font, style)


# ═══════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        from pyfiglet import Figlet
    except ImportError:
        console.print("[red]Install required packages:[/red]")
        console.print("  pip install pyfiglet rich")
        sys.exit(1)

    font_count = len(ASCIIBannerEngine.FONTS)

    print(f"""
+-----------------------------------------------------------+
|                                                           |
|   ASCII BANNER ENGINE v2.0                                |
|                                                           |
|   {font_count} fonts auto-loaded | 18 style presets | SizeManager  |
|                                                           |
+-----------------------------------------------------------+
""")

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "--demo":
            demo_basic_banners()
        elif cmd == "--themes":
            demo_themed_banners()
        elif cmd == "--styles":
            demo_styles()
        elif cmd == "--sizes":
            demo_size_manager()
        elif cmd == "--compare":
            ASCIIBannerEngine().compare_fonts(
                sys.argv[2] if len(sys.argv) > 2 else "Hello")
        elif cmd == "--interactive":
            interactive_menu()
        elif cmd == "--fonts":
            ASCIIBannerEngine().list_fonts()
        elif cmd == "--export":
            ASCIIBannerEngine().render_all_fonts(
                sys.argv[2] if len(sys.argv) > 2 else "DEMO")
        elif cmd == "--help":
            console.print("""
[bold]ASCII Banner Engine v2.0 - Commands:[/bold]

  [cyan]--demo[/cyan]            Basic banner examples
  [cyan]--themes[/cyan]          Themed banner collection
  [cyan]--styles[/cyan]          Style preset showcase
  [cyan]--sizes[/cyan]           SizeManager demo
  [cyan]--compare <text>[/cyan]  Compare fonts side-by-side
  [cyan]--fonts[/cyan]           List all available fonts
  [cyan]--export <text>[/cyan]   Render all fonts to ./banner_output/
  [cyan]--interactive[/cyan]    Full interactive menu
  [cyan]<text>[/cyan]            Quick render with default styling
""")
        else:
            ASCIIBannerEngine().display_banner(sys.argv[1], "banner", "clean")
    else:
        interactive_menu()
