import json
import math
import os
import re
import sys
import tempfile
import tkinter as tk
from tkinter import colorchooser, messagebox
from datetime import datetime, timedelta

import customtkinter as ctk

try:
    from PIL import Image, ImageDraw
except ImportError:  # без Pillow замість малюнка буде символ ✎
    Image = ImageDraw = None

ENERGY_PER_TICK = 15
TICK_HOURS = 3
TICK_SECONDS = TICK_HOURS * 3600

MAX_STANDARD = 560
MAX_SUBSCRIPTION = 840
SPEND_STANDARD = (40,)
SPEND_SUBSCRIPTION = (40, 80)

if sys.platform.startswith("win"):
    BASE_DIR = os.getenv("APPDATA") or os.path.expanduser("~")
    UI_FONT, MONO_FONT = "Segoe UI", "Consolas"
elif sys.platform == "darwin":
    BASE_DIR = os.path.expanduser("~/Library/Application Support")
    UI_FONT, MONO_FONT = "Helvetica Neue", "Menlo"
else:
    BASE_DIR = os.getenv("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    UI_FONT, MONO_FONT = "DejaVu Sans", "DejaVu Sans Mono"

APP_DIR = os.path.join(BASE_DIR, "AionEnergyCalculator")
DATA_FILE = os.path.join(APP_DIR, "aion_energy_data.json")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")


TEXTS = {
    "uk": {
        "title": "Aion 2 — Енергія персонажів",
        "heading": "Енергія персонажів",
        "subtitle": "Кожні 3 години +15 енергії · Максимум {maximum}",
        "settings": "⚙ Налаштування",
        "add": "+ Додати персонажа",
        "save_all": "💾 Зберегти всі",
        "edit": "Редагувати",
        "save": "💾 Зберегти",
        "cancel": "Скасувати",
        "delete": "Видалити",
        "new": "Новий персонаж",
        "name": "Ім'я персонажа",
        "energy": "Енергія (0–{maximum})",
        "time": "Час до наступних +15 (ГГ:ХХ або ГГ:ХХ:СС)",
        "full": "Повна енергія:",
        "max_now": "Вже максимум",
        "max_label": "Максимум!",
        "not_set": "Не задано таймер",
        "settings_title": "Налаштування",
        "appearance": "Оформлення",
        "light": "Світла",
        "dark": "Темна",
        "language": "Мова",
        "ukrainian": "Українська",
        "english": "English",
        "account": "Тип акаунта",
        "standard": "Звичайний — 560 енергії",
        "subscription": "Підписка — 840 енергії",
        "apply": "Застосувати",
        "close": "Закрити",
        "bad_data": "Некоректні дані",
        "name_required": "Вкажи ім'я персонажа.",
        "energy_range": "Енергія має бути від 0 до {maximum}.",
        "time_error": "Введи час у форматі ГГ:ХХ або ГГ:ХХ:СС, наприклад 2:30.",
        "minutes_error": "Хвилини та секунди мають бути від 0 до 59.",
        "delete_title": "Видалити персонажа",
        "delete_confirm": "Видалити «{name}»?",
        "save_error": "Помилка збереження",
        "load_error": "Помилка завантаження",
        "recovered_title": "Енергію відновлено",
        "recovered_text": "Поки програма була закрита:\n\n",
        "recovered_line": "• {name}: +{amount} енергії",
        "next_in": " буде через ",
        "days": "д",
        "empty": "—",
        "spend": "−{amount} енергії",
        "not_enough": "Недостатньо енергії",
        "not_enough_text": "Потрібно {amount}, а в персонажа лише {energy}.",
        "accent_color": "Колір акценту",
        "custom_color": "🎨 Свій колір…",
        "pick_color": "Оберіть колір",
        "card_size": "Розмір плиток",
        "size_compact": "Компактна (в один рядок)",
        "size_medium": "Середня",
        "size_large": "Велика",
        "full_short": "Повна:",
    },
    "en": {
        "title": "Aion 2 — Character Energy",
        "heading": "Character Energy",
        "subtitle": "+15 energy every 3 hours · Maximum {maximum}",
        "settings": "⚙ Settings",
        "add": "+ Add character",
        "save_all": "💾 Save all",
        "edit": "Edit",
        "save": "💾 Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "new": "New character",
        "name": "Character name",
        "energy": "Energy (0–{maximum})",
        "time": "Time until next +15 (HH:MM or HH:MM:SS)",
        "full": "Full energy:",
        "max_now": "Already full",
        "max_label": "Maximum!",
        "not_set": "Timer not set",
        "settings_title": "Settings",
        "appearance": "Appearance",
        "light": "Light",
        "dark": "Dark",
        "language": "Language",
        "ukrainian": "Українська",
        "english": "English",
        "account": "Account type",
        "standard": "Standard — 560 energy",
        "subscription": "Subscription — 840 energy",
        "apply": "Apply",
        "close": "Close",
        "bad_data": "Invalid data",
        "name_required": "Enter a character name.",
        "energy_range": "Energy must be between 0 and {maximum}.",
        "time_error": "Enter time as HH:MM or HH:MM:SS, for example 2:30.",
        "minutes_error": "Minutes and seconds must be between 0 and 59.",
        "delete_title": "Delete character",
        "delete_confirm": "Delete “{name}”?",
        "save_error": "Save error",
        "load_error": "Load error",
        "recovered_title": "Energy restored",
        "recovered_text": "While the app was closed:\n\n",
        "recovered_line": "• {name}: +{amount} energy",
        "next_in": " in ",
        "days": "d",
        "empty": "—",
        "spend": "−{amount} energy",
        "not_enough": "Not enough energy",
        "not_enough_text": "Need {amount}, but the character only has {energy}.",
        "accent_color": "Accent color",
        "custom_color": "🎨 Custom color…",
        "pick_color": "Choose a color",
        "card_size": "Card size",
        "size_compact": "Compact (single row)",
        "size_medium": "Medium",
        "size_large": "Large",
        "full_short": "Full:",
    },
}


# Кольори у форматі (світла тема, темна тема).
# CustomTkinter сам перемикає їх при зміні теми.
C = {
    "bg": ("#eef1f6", "#0e121a"),
    "card": ("#ffffff", "#171d2b"),
    "border": ("#dde3ec", "#262f44"),
    "text": ("#1f2a3a", "#eef1f7"),
    "muted": ("#6b778c", "#8a96ad"),
    "accent": ("#b07a12", "#e2b655"),
    "accent_fill": ("#e0a52e", "#e2b655"),
    "accent_hover": ("#cf951f", "#f0c76d"),
    "on_accent": ("#1a1405", "#1a1405"),
    "soft": ("#f3e6c8", "#2a3043"),
    "soft_hover": ("#ead8ae", "#353c54"),
    "neutral": ("#e3e8f0", "#262e42"),
    "neutral_hover": ("#d6dde8", "#313a52"),
    "green": ("#1f9d63", "#4fd08f"),
    "green_hover": ("#188552", "#6be0a4"),
    "on_green": ("#ffffff", "#0b1a12"),
    "full_bg": ("#e6f6ee", "#13291f"),
    "red": ("#d64545", "#ff7b7b"),
    "danger_bg": ("#fbe9e9", "#3a2327"),
    "danger_hover": ("#f6d6d6", "#4a2a30"),
    "track": ("#e3e8f0", "#262e42"),
    "entry": ("#f5f7fb", "#232b3e"),
}

DEFAULT_ACCENT = "#5aa9e6"

ACCENT_PRESETS = (
    "#5aa9e6",  # світло-синій
    "#4cc3d9",  # блакитний
    "#45b8a0",  # бірюзовий
    "#8e9cf5",  # барвінковий
    "#b38ef0",  # лавандовий
    "#e69ab8",  # м'який рожевий
    "#d4b062",  # пісочне золото
)


def _hex_to_rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def mix(first, second, amount):
    """Змішує два кольори: 0 — перший, 1 — другий."""
    a, b = _hex_to_rgb(first), _hex_to_rgb(second)
    rgb = (round(x * (1 - amount) + y * amount) for x, y in zip(a, b))
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def luminance(value):
    r, g, b = _hex_to_rgb(value)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def apply_accent(base):
    """Будує всі акцентні кольори (для світлої й темної теми) з одного."""
    lum = luminance(base)

    text_on = "#10151f" if lum > 0.5 else "#ffffff"

    light_text = mix(base, "#000000", 0.35 if lum > 0.35 else 0.1)
    dark_text = mix(base, "#ffffff", 0.10 if lum > 0.45 else 0.45)

    C["accent"] = (light_text, dark_text)
    C["accent_fill"] = (base, base)
    C["accent_hover"] = (
        mix(base, "#000000", 0.12), mix(base, "#ffffff", 0.15)
    )
    C["on_accent"] = (text_on, text_on)
    C["soft"] = (
        mix(base, "#ffffff", 0.82), mix(base, "#1a2030", 0.80)
    )
    C["soft_hover"] = (
        mix(base, "#ffffff", 0.70), mix(base, "#1a2030", 0.66)
    )


apply_accent(DEFAULT_ACCENT)


def button_style(kind):
    return {
        "primary": (C["accent_fill"], C["accent_hover"], C["on_accent"]),
        "soft": (C["soft"], C["soft_hover"], C["accent"]),
        "danger": (C["danger_bg"], C["danger_hover"], C["red"]),
        "neutral": (C["neutral"], C["neutral_hover"], C["text"]),
        "success": (C["green"], C["green_hover"], C["on_green"]),
    }[kind]


_fonts = {}


def font(size, weight="normal", mono=False):
    key = (size, weight, mono)

    if key not in _fonts:
        _fonts[key] = ctk.CTkFont(
            family=MONO_FONT if mono else UI_FONT,
            size=size,
            weight=weight,
        )

    return _fonts[key]


def _hex_rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def _draw_pencil(color, px=40, supersample=8):
    """Малює олівець (діагональний) кольором color у вигляді PIL-зображення."""
    size = px * supersample
    k = size / 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    tip = (8, 56)
    d = 0.7071

    def point(s, w):
        return ((tip[0] + d * s + d * w) * k, (tip[1] - d * s + d * w) * k)

    r, g, b = color
    solid = (r, g, b, 255)
    soft = (r, g, b, 150)

    # Загострений кінчик
    draw.polygon([point(0, 0), point(13, -7.5), point(13, 7.5)], fill=soft)
    draw.polygon([point(0, 0), point(5, -2.9), point(5, 2.9)], fill=solid)
    # Корпус та гумка
    draw.polygon(
        [point(15, -7.5), point(43, -7.5), point(43, 7.5), point(15, 7.5)],
        fill=solid,
    )
    draw.polygon(
        [point(46, -7.5), point(54, -7.5), point(54, 7.5), point(46, 7.5)],
        fill=solid,
    )

    return img.resize((px, px), Image.LANCZOS)


def pencil_icon():
    """Іконка олівця в кольорі акценту (для світлої й темної теми)."""
    if Image is None:
        return None

    try:
        light, dark = C["accent"]

        return ctk.CTkImage(
            light_image=_draw_pencil(_hex_rgb(light)),
            dark_image=_draw_pencil(_hex_rgb(dark)),
            size=(18, 18),
        )
    except Exception:
        return None


def make_button(parent, text, command, kind="soft", width=110,
                height=34, size=12, image=None):
    fg, hover, text_color = button_style(kind)

    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=fg,
        hover_color=hover,
        text_color=text_color,
        corner_radius=min(10, height // 2),
        height=height,
        width=width,
        font=font(size, "bold"),
        image=image,
        compound="left",
    )


def edit_button(parent, command, width, height, size, with_text=True):
    """Кнопка «Редагувати» з намальованим олівцем."""
    icon = pencil_icon()

    if icon is None:
        # Запасний варіант, якщо Pillow недоступний
        text = "✎ " + parent.winfo_toplevel().t("edit") if with_text else "✎"
        return make_button(parent, text, command, "soft", width, height, size)

    text = (" " + parent.winfo_toplevel().t("edit")) if with_text else ""

    return make_button(
        parent, text, command, "soft", width, height, size, image=icon
    )


# Параметри розмірів плиток персонажів
SIZES = {
    "compact": dict(radius=12, pad=8, gap=6, strip=4),
    "medium": dict(
        radius=14, pad=10, gap=8, strip=5,
        name=15, big=26, max=12, small=11,
        pill=12, pill_h=26, bar=10,
        btn_h=30, btn_font=11, bw=0.9,
        status_pad=6, bar_pad=(4, 6),
    ),
    "large": dict(
        radius=16, pad=14, gap=12, strip=6,
        name=17, big=36, max=14, small=12,
        pill=13, pill_h=30, bar=12,
        btn_h=34, btn_font=12, bw=1.0,
        status_pad=10, bar_pad=(8, 10),
    ),
}


def pill(text):
    return f"  {text}  "


# ---------------------------------------------------------------------------
# Допоміжні функції
# ---------------------------------------------------------------------------

def resource_path(name):
    """Шлях до ресурсу: працює і в PyCharm, і в зібраному .exe."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def set_window_icon(window):
    try:
        window.iconbitmap(resource_path("aion2.ico"))
    except Exception:
        pass


def duration(seconds, app):
    seconds = max(0, int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    prefix = f"{days}{app.t('days')} " if days else ""
    return prefix + f"{hours:02}:{minutes:02}:{seconds:02}"


def read_energy(value, maximum, app):
    try:
        energy = int(str(value).strip())
    except ValueError:
        raise ValueError(app.t("energy_range", maximum=maximum))

    if not 0 <= energy <= maximum:
        raise ValueError(app.t("energy_range", maximum=maximum))

    return energy


def read_time(value, app):
    parts = (
        value.strip()
        .replace(".", ":")
        .replace(",", ":")
        .split(":")
    )

    if len(parts) not in (1, 2, 3):
        raise ValueError(app.t("time_error"))

    if not all(part.strip().isdigit() for part in parts):
        raise ValueError(app.t("time_error"))

    numbers = [int(part) for part in parts]
    hours = numbers[0]
    minutes = numbers[1] if len(numbers) > 1 else 0
    seconds = numbers[2] if len(numbers) > 2 else 0

    if not (0 <= minutes <= 59 and 0 <= seconds <= 59):
        raise ValueError(app.t("minutes_error"))

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def advance(energy, tick, now, maximum):
    """Єдина логіка відновлення енергії.

    Повертає (енергія, наступний_тік, скільки_відновлено).
    Енергія обрізається до максимуму; при максимумі таймер скидається.
    """
    energy = max(0, min(energy, maximum))

    if energy >= maximum:
        return energy, None, 0

    if tick is None or tick > now:
        return energy, tick, 0

    ticks = int((now - tick).total_seconds() // TICK_SECONDS) + 1
    gained = min(ticks * ENERGY_PER_TICK, maximum - energy)
    energy += gained

    if energy >= maximum:
        tick = None
    else:
        tick += timedelta(seconds=ticks * TICK_SECONDS)

    return energy, tick, gained


def load_tick(timestamp):
    try:
        return (
            datetime.fromtimestamp(float(timestamp))
            if timestamp is not None else None
        )
    except (ValueError, TypeError, OSError, OverflowError):
        return None


# ---------------------------------------------------------------------------
# Картка персонажа
# ---------------------------------------------------------------------------

class CharacterCard:

    def __init__(self, parent, app, data=None):
        self.app = app
        self.editing = False
        self.backup = None
        self.data = data or {}
        self.is_full = None

        self.size = app.card_size
        sz = SIZES[self.size]
        self.gap = sz["gap"]

        self.name = tk.StringVar(value=self.data.get("name", ""))
        self.energy = tk.StringVar(value=str(self.data.get("energy", 0)))
        self.time = tk.StringVar(value="03:00:00")

        self.next_tick = load_tick(self.data.get("target_timestamp"))

        # --- Картка із закругленими кутами ---
        self.frame = ctk.CTkFrame(
            parent,
            corner_radius=sz["radius"],
            fg_color=C["card"],
            border_width=1,
            border_color=C["border"],
        )
        self.frame.grid_columnconfigure(1, weight=1)

        # Кольорова смужка зліва (колір залежить від заповненості)
        self.strip = ctk.CTkFrame(
            self.frame,
            width=sz["strip"],
            height=1,
            corner_radius=max(1, sz["strip"] // 2),
            fg_color=C["accent_fill"],
        )
        self.strip.grid(
            row=0, column=0, sticky="ns",
            padx=(12, 0), pady=sz["pad"],
        )

        body = ctk.CTkFrame(self.frame, fg_color="transparent")
        body.grid(
            row=0, column=1, sticky="ew",
            padx=(12, 14), pady=sz["pad"],
        )
        body.grid_columnconfigure(0, weight=1)

        if self.size == "compact":
            self._build_compact(body)
        else:
            self._build_regular(body, sz)

        self.name.trace_add(
            "write",
            lambda *_: self.title.configure(
                text=self.name.get().strip() or app.t("new")
            ),
        )

        self.editor.grid_remove()
        self.refresh(datetime.now())

    # --- Побудова розкладок ---

    def _build_editor(self, parent, compact):
        app = self.app

        self.editor = ctk.CTkFrame(parent, fg_color="transparent")

        if compact:
            self.editor.grid_columnconfigure(0, weight=2)
            self.editor.grid_columnconfigure(1, weight=1)
            self.editor.grid_columnconfigure(2, weight=2)

            self.name_entry = self.field(
                self.editor, app.t("name"), self.name, 0, 0
            )
            self.energy_entry = self.field(
                self.editor,
                app.t("energy", maximum=app.max_energy),
                self.energy, 0, 1,
            )
            self.time_entry = self.field(
                self.editor, app.t("time"), self.time, 0, 2
            )
            actions_pos = dict(row=0, column=3, sticky="s", pady=(0, 8))
        else:
            self.editor.grid_columnconfigure((0, 1), weight=1)

            self.name_entry = self.field(
                self.editor, app.t("name"), self.name, 0, 0
            )
            self.energy_entry = self.field(
                self.editor,
                app.t("energy", maximum=app.max_energy),
                self.energy, 0, 1,
            )
            self.time_entry = self.field(
                self.editor, app.t("time"), self.time, 1, 0, 2
            )
            actions_pos = dict(
                row=2, column=0, columnspan=2, sticky="e", pady=(4, 0)
            )

        for entry in (self.name_entry, self.energy_entry, self.time_entry):
            entry.bind("<Return>", lambda _: self.save_edit())
            entry.bind("<Escape>", lambda _: self.cancel_edit())

        actions = ctk.CTkFrame(self.editor, fg_color="transparent")
        actions.grid(**actions_pos)

        make_button(
            actions, app.t("save"), self.save_edit, "success", 130,
            height=30 if compact else 34, size=11 if compact else 12,
        ).pack(side="left", padx=6)

        make_button(
            actions, app.t("cancel"), self.cancel_edit, "neutral", 105,
            height=30 if compact else 34, size=11 if compact else 12,
        ).pack(side="left")

    def _build_regular(self, body, sz):
        app = self.app
        bw = sz["bw"]

        # --- Шапка картки ---
        head = ctk.CTkFrame(body, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew")
        head.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(
            head,
            text=self.name.get() or app.t("new"),
            font=font(sz["name"], "bold"),
            text_color=C["text"],
            anchor="w",
        )
        self.title.grid(row=0, column=0, sticky="w")

        edit_button(
            head, self.begin_edit,
            int(130 * bw), sz["btn_h"], sz["btn_font"],
        ).grid(row=0, column=1, padx=6)

        make_button(
            head, app.t("delete"), self.delete, "danger",
            int(95 * bw), sz["btn_h"], sz["btn_font"],
        ).grid(row=0, column=2)

        # --- Режим редагування ---
        self._build_editor(body, compact=False)
        self.editor.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        # --- Звичайний режим ---
        self.status = ctk.CTkFrame(body, fg_color="transparent")
        self.status.grid(
            row=2, column=0, sticky="ew", pady=(sz["status_pad"], 0)
        )
        self.status.grid_columnconfigure(0, weight=1)

        line = ctk.CTkFrame(self.status, fg_color="transparent")
        line.grid(row=0, column=0, sticky="ew")
        line.grid_columnconfigure(0, weight=1)

        numbox = ctk.CTkFrame(line, fg_color="transparent")
        numbox.grid(row=0, column=0, sticky="w")

        self.energy_big = ctk.CTkLabel(
            numbox,
            text="",
            font=font(sz["big"], "bold"),
            text_color=C["text"],
        )
        self.energy_big.pack(side="left")

        self.energy_max = ctk.CTkLabel(
            numbox,
            text="",
            font=font(sz["max"]),
            text_color=C["muted"],
        )
        self.energy_max.pack(
            side="left", anchor="s", pady=(0, 6), padx=(4, 0)
        )

        # Таймер у вигляді «таблетки»
        self.timer_label = ctk.CTkLabel(
            line,
            text="",
            corner_radius=sz["pill_h"] // 2,
            height=sz["pill_h"],
            font=font(sz["pill"], "bold", mono=True),
            fg_color=C["soft"],
            text_color=C["accent"],
        )
        self.timer_label.grid(row=0, column=1, sticky="e")

        self.bar = ctk.CTkProgressBar(
            self.status,
            height=sz["bar"],
            corner_radius=sz["bar"] // 2,
            fg_color=C["track"],
            progress_color=C["accent_fill"],
        )
        self.bar.set(0)
        self.bar.grid(row=1, column=0, sticky="ew", pady=sz["bar_pad"])

        bottom = ctk.CTkFrame(self.status, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="ew")

        ctk.CTkLabel(
            bottom,
            text=app.t("full"),
            font=font(sz["small"]),
            text_color=C["muted"],
        ).pack(side="left")

        self.full_label = ctk.CTkLabel(
            bottom,
            text="",
            font=font(sz["small"], "bold"),
            text_color=C["text"],
        )
        self.full_label.pack(side="left", padx=6)

        # Кнопки витрати: −40 (і −80 для підписки). Пакуємо в зворотному
        # порядку, щоб зліва направо йшло −40, потім −80.
        for amount in reversed(app.spend_options):
            make_button(
                bottom,
                app.t("spend", amount=amount),
                lambda a=amount: self.spend(a),
                "soft",
                int(118 * bw),
                sz["btn_h"],
                sz["btn_font"],
            ).pack(side="right", padx=(6, 0))

    def _build_compact(self, body):
        """Компактна плитка: усе в один рядок."""
        app = self.app

        self._build_editor(body, compact=True)
        self.editor.grid(row=0, column=0, sticky="ew")

        self.status = ctk.CTkFrame(body, fg_color="transparent")
        self.status.grid(row=0, column=0, sticky="ew")
        self.status.grid_columnconfigure(2, weight=1)

        # Ім'я та час повного відновлення
        left = ctk.CTkFrame(self.status, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        self.title = ctk.CTkLabel(
            left,
            text=self.name.get() or app.t("new"),
            font=font(14, "bold"),
            text_color=C["text"],
            anchor="w",
            width=150,
        )
        self.title.grid(row=0, column=0, sticky="w")

        fullrow = ctk.CTkFrame(left, fg_color="transparent")
        fullrow.grid(row=1, column=0, sticky="w")

        ctk.CTkLabel(
            fullrow,
            text=app.t("full_short"),
            font=font(10),
            text_color=C["muted"],
        ).pack(side="left")

        self.full_label = ctk.CTkLabel(
            fullrow,
            text="",
            font=font(10, "bold"),
            text_color=C["text"],
        )
        self.full_label.pack(side="left", padx=4)

        # Енергія
        numbox = ctk.CTkFrame(self.status, fg_color="transparent")
        numbox.grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.energy_big = ctk.CTkLabel(
            numbox,
            text="",
            font=font(20, "bold"),
            text_color=C["text"],
        )
        self.energy_big.pack(side="left")

        self.energy_max = ctk.CTkLabel(
            numbox,
            text="",
            font=font(11),
            text_color=C["muted"],
        )
        self.energy_max.pack(side="left", anchor="s", pady=(0, 3), padx=(3, 0))

        # Смужка
        self.bar = ctk.CTkProgressBar(
            self.status,
            height=8,
            corner_radius=4,
            fg_color=C["track"],
            progress_color=C["accent_fill"],
        )
        self.bar.set(0)
        self.bar.grid(row=0, column=2, sticky="ew", padx=12)

        # Таймер
        self.timer_label = ctk.CTkLabel(
            self.status,
            text="",
            corner_radius=12,
            height=24,
            font=font(11, "bold", mono=True),
            fg_color=C["soft"],
            text_color=C["accent"],
        )
        self.timer_label.grid(row=0, column=3, sticky="e")

        # Витрата енергії
        spend = ctk.CTkFrame(self.status, fg_color="transparent")
        spend.grid(row=0, column=4, padx=(10, 0))

        for amount in reversed(app.spend_options):
            make_button(
                spend,
                f"−{amount}",
                lambda a=amount: self.spend(a),
                "soft",
                54, 28, 11,
            ).pack(side="right", padx=(4, 0))

        # Редагувати / видалити
        tools = ctk.CTkFrame(self.status, fg_color="transparent")
        tools.grid(row=0, column=5, padx=(10, 0))

        edit_button(
            tools, self.begin_edit, 34, 28, 11, with_text=False
        ).pack(side="left", padx=2)

        make_button(
            tools, "✕", self.delete, "danger", 34, 28, 11
        ).pack(side="left", padx=2)

    # --- Створення віджетів ---

    def field(self, parent, label, variable, row, column, span=1):
        compact = self.size == "compact"

        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(
            row=row,
            column=column,
            columnspan=span,
            sticky="ew",
            padx=(0, 10),
            pady=(0, 8),
        )
        box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            box,
            text=label,
            font=font(10 if compact else 11),
            text_color=C["muted"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        entry = ctk.CTkEntry(
            box,
            textvariable=variable,
            height=30 if compact else 36,
            corner_radius=8,
            border_width=1,
            fg_color=C["entry"],
            border_color=C["border"],
            text_color=C["text"],
            font=font(12 if compact else 13),
        )
        entry.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        return entry

    # --- Дані ---

    def current_energy(self):
        """Поточна енергія з поля, обрізана до максимуму акаунта."""
        try:
            energy = int(self.energy.get().strip())
        except ValueError:
            energy = 0

        return max(0, min(energy, self.app.max_energy))

    def to_dict(self):
        name = self.name.get().strip()

        if not name:
            return None

        return {
            "name": name,
            "energy": self.current_energy(),
            "target_timestamp": (
                self.next_tick.timestamp() if self.next_tick else None
            ),
        }

    def snapshot(self):
        """Стан для збереження. Під час редагування — стан до змін."""
        if self.editing and self.backup:
            name, energy_text, _, tick = self.backup

            name = name.strip()
            if not name:
                return None

            try:
                energy = int(energy_text)
            except ValueError:
                return None

            return {
                "name": name,
                "energy": max(0, min(energy, self.app.max_energy)),
                "target_timestamp": tick.timestamp() if tick else None,
            }

        return self.to_dict()

    # --- Редагування ---

    def begin_edit(self):
        if self.editing:
            return

        self.backup = (
            self.name.get(),
            self.energy.get(),
            self.time.get(),
            self.next_tick,
        )

        if self.next_tick:
            remaining = max(
                0, int((self.next_tick - datetime.now()).total_seconds())
            )
            self.time.set(
                f"{remaining // 3600:02}:"
                f"{(remaining % 3600) // 60:02}:"
                f"{remaining % 60:02}"
            )

        self.editing = True
        self.status.grid_remove()
        self.editor.grid()
        self.name_entry.focus_set()

    def end_edit(self):
        self.editing = False
        self.backup = None

        self.editor.grid_remove()
        self.status.grid()
        self.refresh(datetime.now())

    def cancel_edit(self):
        is_new = False

        if self.backup:
            name, energy, time, tick = self.backup
            is_new = not name.strip()

            self.name.set(name)
            self.energy.set(energy)
            self.time.set(time)
            self.next_tick = tick

        if is_new:
            # Скасували створення нового персонажа — прибираємо картку
            self.app.remove(self)
            return

        self.end_edit()

    def save_edit(self):
        try:
            name = self.name.get().strip()

            if not name:
                raise ValueError(self.app.t("name_required"))

            energy = read_energy(
                self.energy.get(), self.app.max_energy, self.app
            )

            tick = (
                datetime.now() + read_time(self.time.get(), self.app)
                if energy < self.app.max_energy else None
            )

        except ValueError as error:
            messagebox.showerror(
                self.app.t("bad_data"), str(error), parent=self.app
            )
            return False

        self.name.set(name)
        self.energy.set(str(energy))
        self.next_tick = tick

        self.end_edit()
        self.app.save()

        return True

    def delete(self):
        name = self.name.get().strip() or self.app.t("new")

        if messagebox.askyesno(
            self.app.t("delete_title"),
            self.app.t("delete_confirm", name=name),
            parent=self.app,
        ):
            self.app.remove(self)

    # --- Витрата енергії ---

    def spend(self, amount):
        energy = self.current_energy()

        if energy < amount:
            messagebox.showwarning(
                self.app.t("not_enough"),
                self.app.t("not_enough_text", amount=amount, energy=energy),
                parent=self.app,
            )
            return

        now = datetime.now()

        # Спершу оновлюємо енергію до поточного моменту
        energy, self.next_tick, _ = advance(
            energy, self.next_tick, now, self.app.max_energy
        )

        energy -= amount
        self.energy.set(str(energy))

        # Якщо таймер не йшов (була повна енергія) — запускаємо заново
        if self.next_tick is None and energy < self.app.max_energy:
            self.next_tick = now + timedelta(seconds=TICK_SECONDS)

        self.refresh(now)
        self.app.save()

    # --- Відображення ---

    def bar_color(self):
        if self.current_energy() >= self.app.max_energy:
            return C["green"]

        return C["accent_fill"]

    def set_full(self, full):
        """Підсвічує картку, коли енергія на максимумі."""
        if full == self.is_full:
            return

        self.is_full = full

        self.frame.configure(
            fg_color=C["full_bg"] if full else C["card"],
            border_color=C["green"] if full else C["border"],
            border_width=2 if full else 1,
        )

    def refresh(self, now):
        """Оновлює картку. Повертає True, якщо дані змінились."""
        maximum = self.app.max_energy

        old_energy = self.current_energy()
        old_tick = self.next_tick

        energy, tick, _ = advance(old_energy, old_tick, now, maximum)

        changed = (
            energy != old_energy
            or tick != old_tick
            or self.energy.get() != str(energy)
        )

        if changed:
            self.energy.set(str(energy))
            self.next_tick = tick

        full = energy >= maximum
        self.set_full(full)

        color = self.bar_color()

        self.energy_big.configure(
            text=str(energy),
            text_color=C["green"] if full else C["text"],
        )
        self.energy_max.configure(text=f"/ {maximum}")

        self.bar.set(energy / maximum)
        self.bar.configure(progress_color=color)
        self.strip.configure(fg_color=color)

        if full:
            self.timer_label.configure(
                text=pill(self.app.t("max_label")),
                fg_color=C["green"],
                text_color=C["on_green"],
            )
            self.full_label.configure(text=self.app.t("max_now"))
            return changed

        if self.next_tick is None:
            self.timer_label.configure(
                text=pill(self.app.t("not_set")),
                fg_color=C["danger_bg"],
                text_color=C["red"],
            )
            self.full_label.configure(text=self.app.t("empty"))
            return changed

        left = max(0, (self.next_tick - now).total_seconds())
        next_energy = min(maximum, energy + ENERGY_PER_TICK)

        if self.size == "compact":
            timer_text = f"{next_energy} · {duration(left, self.app)}"
        else:
            timer_text = (
                f"{next_energy}"
                f"{self.app.t('next_in')}"
                f"{duration(left, self.app)}"
            )

        self.timer_label.configure(
            text=pill(timer_text),
            fg_color=C["soft"],
            text_color=C["accent"],
        )

        ticks = math.ceil((maximum - energy) / ENERGY_PER_TICK)
        target = self.next_tick + timedelta(
            seconds=(ticks - 1) * TICK_SECONDS
        )

        if self.app.language == "uk":
            days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
            full_text = f"{days[target.weekday()]}, {target:%d.%m о %H:%M}"
        else:
            full_text = f"{target:%a, %b %d at %H:%M}"

        self.full_label.configure(text=full_text)

        return changed


# ---------------------------------------------------------------------------
# Головне вікно
# ---------------------------------------------------------------------------

class AionEnergyApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.settings = {
            "theme": "dark",
            "language": "uk",
            "subscription": False,
            "accent": DEFAULT_ACCENT,
            "card_size": "medium",
        }

        self.load_settings()
        self.apply_settings_state()

        set_window_icon(self)
        self.title(self.t("title"))
        self.geometry("920x740")
        self.minsize(780, 480)

        self.cards = []
        self.configure(fg_color=C["bg"])

        self.build_ui()
        self.load()

        self.after(1000, self.tick)
        self.protocol("WM_DELETE_WINDOW", self.close)

    def apply_settings_state(self):
        self.language = self.settings["language"]
        ctk.set_appearance_mode(self.settings["theme"])
        apply_accent(self.settings["accent"])
        self.card_size = self.settings["card_size"]

        subscription = self.settings["subscription"]
        self.max_energy = MAX_SUBSCRIPTION if subscription else MAX_STANDARD
        self.spend_options = (
            SPEND_SUBSCRIPTION if subscription else SPEND_STANDARD
        )

    def t(self, key, **kwargs):
        return TEXTS[self.settings["language"]].get(key, key).format(**kwargs)

    # --- Налаштування ---

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                saved = json.load(f)

            if saved.get("theme") in ("light", "dark"):
                self.settings["theme"] = saved["theme"]

            if saved.get("language") in TEXTS:
                self.settings["language"] = saved["language"]

            self.settings["subscription"] = bool(
                saved.get("subscription", False)
            )

            if saved.get("card_size") in SIZES:
                self.settings["card_size"] = saved["card_size"]

            accent = saved.get("accent")
            if isinstance(accent, str) and re.fullmatch(
                r"#[0-9a-fA-F]{6}", accent
            ):
                self.settings["accent"] = accent.lower()

        except (OSError, json.JSONDecodeError, AttributeError):
            pass

    def save_settings(self):
        os.makedirs(APP_DIR, exist_ok=True)

        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    # --- Інтерфейс ---

    def build_ui(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=26, pady=(22, 0))

        row = ctk.CTkFrame(top, fg_color="transparent")
        row.pack(fill="x")

        ctk.CTkLabel(
            row,
            text=self.t("heading"),
            font=font(28, "bold"),
            text_color=C["text"],
        ).pack(side="left")

        make_button(
            row, self.t("settings"), self.open_settings, "neutral", 160
        ).pack(side="right")

        self.subtitle = ctk.CTkLabel(
            top,
            text=self.t("subtitle", maximum=self.max_energy),
            font=font(12),
            text_color=C["muted"],
            anchor="w",
        )
        self.subtitle.pack(anchor="w", pady=(2, 0))

        ctk.CTkFrame(
            self,
            height=3,
            corner_radius=2,
            fg_color=C["accent_fill"],
        ).pack(fill="x", padx=26, pady=(10, 12))

        self.list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.list_frame.pack(fill="both", expand=True, padx=(18, 12))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=26, pady=16)

        make_button(
            footer, self.t("add"), self.add, "primary", 190
        ).pack(side="left")

        make_button(
            footer, self.t("save_all"), self.save_all, "soft", 155
        ).pack(side="right")

    def open_settings(self):
        win = ctk.CTkToplevel(self)

        win.title(self.t("settings_title"))
        win.geometry("420x700")
        win.minsize(420, 420)
        win.resizable(False, True)
        win.configure(fg_color=C["card"])
        win.transient(self)
        set_window_icon(win)

        def grab():
            try:
                win.grab_set()
                win.focus()
            except tk.TclError:
                pass

        win.after(200, grab)

        # Кнопки внизу завжди видно, навіть якщо вікно низьке
        buttons = ctk.CTkFrame(win, fg_color="transparent")
        buttons.pack(side="bottom", fill="x", padx=26, pady=16)

        body = ctk.CTkScrollableFrame(
            win, fg_color="transparent", corner_radius=0
        )
        body.pack(fill="both", expand=True, padx=(8, 4), pady=(4, 0))

        theme = tk.StringVar(value=self.settings["theme"])
        language = tk.StringVar(value=self.settings["language"])
        card_size = tk.StringVar(value=self.settings["card_size"])
        account = tk.StringVar(
            value="subscription" if self.settings["subscription"]
            else "standard"
        )
        accent = tk.StringVar(value=self.settings["accent"])

        def heading(text):
            ctk.CTkLabel(
                body,
                text=text,
                font=font(14, "bold"),
                text_color=C["accent"],
                anchor="w",
            ).pack(anchor="w", padx=18, pady=(16, 6))

        def choice(text, variable, value):
            ctk.CTkRadioButton(
                body,
                text=text,
                variable=variable,
                value=value,
                width=300,
                fg_color=C["accent_fill"],
                hover_color=C["accent_hover"],
                border_color=C["muted"],
                text_color=C["text"],
                font=font(13),
            ).pack(anchor="w", padx=28, pady=4)

        # --- Оформлення ---
        heading(self.t("appearance"))
        choice(self.t("light"), theme, "light")
        choice(self.t("dark"), theme, "dark")

        # --- Колір акценту ---
        heading(self.t("accent_color"))

        swatches = {}

        swatch_row = ctk.CTkFrame(body, fg_color="transparent")
        swatch_row.pack(anchor="w", padx=24, pady=(2, 4))

        custom_row = ctk.CTkFrame(body, fg_color="transparent")
        custom_row.pack(anchor="w", padx=28, pady=(6, 0))

        preview = ctk.CTkFrame(
            custom_row,
            width=34,
            height=34,
            corner_radius=17,
            fg_color=accent.get(),
        )
        preview.pack(side="left")

        hex_label = ctk.CTkLabel(
            custom_row,
            text=accent.get().upper(),
            font=font(13, "bold", mono=True),
            text_color=C["text"],
        )
        hex_label.pack(side="left", padx=10)

        def refresh_swatches():
            for value, button in swatches.items():
                selected = value == accent.get().lower()
                button.configure(
                    border_width=3 if selected else 0,
                    border_color=C["text"],
                )

        def set_accent(value):
            value = value.lower()
            accent.set(value)
            preview.configure(fg_color=value)
            hex_label.configure(text=value.upper())
            refresh_swatches()

        def pick_custom():
            try:
                result = colorchooser.askcolor(
                    color=accent.get(),
                    parent=win,
                    title=self.t("pick_color"),
                )
            except tk.TclError:
                return

            if result and result[1]:
                set_accent(result[1])

        make_button(
            custom_row, self.t("custom_color"), pick_custom, "neutral", 150
        ).pack(side="left")

        for value in ACCENT_PRESETS:
            button = ctk.CTkButton(
                swatch_row,
                text="",
                width=34,
                height=34,
                corner_radius=17,
                fg_color=value,
                hover_color=mix(value, "#ffffff", 0.25),
                border_width=0,
                command=lambda v=value: set_accent(v),
            )
            button.pack(side="left", padx=4)
            swatches[value] = button

        refresh_swatches()

        # --- Розмір плиток ---
        heading(self.t("card_size"))
        choice(self.t("size_compact"), card_size, "compact")
        choice(self.t("size_medium"), card_size, "medium")
        choice(self.t("size_large"), card_size, "large")

        # --- Мова ---
        heading(self.t("language"))
        choice(self.t("ukrainian"), language, "uk")
        choice(self.t("english"), language, "en")

        # --- Тип акаунта ---
        heading(self.t("account"))
        choice(self.t("standard"), account, "standard")
        choice(self.t("subscription"), account, "subscription")

        def apply():
            # Зберігаємо стан карток до перебудови
            self._pending_cards = [
                item for item in (c.snapshot() for c in self.cards) if item
            ]

            self.settings.update(
                theme=theme.get(),
                language=language.get(),
                subscription=(account.get() == "subscription"),
                accent=accent.get(),
                card_size=card_size.get(),
            )
            self.apply_settings_state()

            try:
                self.save_settings()
            except OSError as error:
                messagebox.showerror(
                    self.t("save_error"), str(error), parent=win
                )

            win.destroy()
            self.rebuild()

        make_button(
            buttons, self.t("apply"), apply, "primary", 130
        ).pack(side="right", padx=(8, 0))

        make_button(
            buttons, self.t("close"), win.destroy, "neutral", 100
        ).pack(side="right")

    def rebuild(self):
        data = getattr(self, "_pending_cards", [])
        now = datetime.now()

        for widget in self.winfo_children():
            widget.destroy()

        self.cards = []
        self.configure(fg_color=C["bg"])
        self.title(self.t("title"))

        self.build_ui()

        for raw in data:
            item, _ = self.normalize(raw, now)

            if item:
                self.add_card(item)

        self.save()

    # --- Картки ---

    def add_card(self, data=None):
        card = CharacterCard(self.list_frame, self, data)
        self.cards.append(card)
        card.frame.pack(fill="x", pady=(0, card.gap), padx=(6, 8))
        return card

    def scroll_to_end(self):
        try:
            self.list_frame._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def add(self):
        card = self.add_card()

        # Новий персонаж одразу відкривається для заповнення
        card.begin_edit()

        self.update_idletasks()
        self.scroll_to_end()

    def remove(self, card):
        if card in self.cards:
            self.cards.remove(card)

        card.frame.destroy()
        self.save()

    # --- Збереження / завантаження ---

    def normalize(self, raw, now):
        """Приводить запис до поточного акаунта та оновлює енергію.

        Повертає (словник | None, скільки_відновлено).
        """
        try:
            name = str(raw.get("name", "")).strip()
            energy = int(raw.get("energy", 0))
        except (AttributeError, ValueError, TypeError):
            return None, 0

        if not name:
            return None, 0

        tick = load_tick(raw.get("target_timestamp"))

        energy, tick, gained = advance(energy, tick, now, self.max_energy)

        return {
            "name": name,
            "energy": energy,
            "target_timestamp": tick.timestamp() if tick else None,
        }, gained

    def save(self):
        os.makedirs(APP_DIR, exist_ok=True)

        data = [
            item for item in (card.snapshot() for card in self.cards) if item
        ]

        temp = None

        try:
            fd, temp = tempfile.mkstemp(dir=APP_DIR, suffix=".tmp")

            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp, DATA_FILE)

        except OSError as error:
            if temp and os.path.exists(temp):
                try:
                    os.remove(temp)
                except OSError:
                    pass

            messagebox.showerror(
                self.t("save_error"), str(error), parent=self
            )

    def save_all(self):
        # Спершу зберігаємо всі відкриті форми редагування
        for card in self.cards[:]:
            if card.editing:
                if not card.save_edit():
                    # Є помилка — форму залишаємо відкритою
                    return

        self.save()

    def load(self):
        if not os.path.exists(DATA_FILE):
            return

        try:
            with open(DATA_FILE, encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Invalid save file format.")

        except (OSError, json.JSONDecodeError, ValueError) as error:
            messagebox.showerror(
                self.t("load_error"), str(error), parent=self
            )
            return

        now = datetime.now()
        recovered = []

        for raw in data:
            item, gained = self.normalize(raw, now)

            if not item:
                continue

            if gained > 0:
                recovered.append(
                    self.t(
                        "recovered_line",
                        name=item["name"],
                        amount=gained,
                    )
                )

            self.add_card(item)

        if recovered:
            messagebox.showinfo(
                self.t("recovered_title"),
                self.t("recovered_text") + "\n".join(recovered),
                parent=self,
            )

        self.save()

    # --- Цикл оновлення ---

    def tick(self):
        now = datetime.now()
        changed = False

        for card in self.cards:
            if not card.editing and card.refresh(now):
                changed = True

        # Один запис на диск за тік, навіть якщо змінилось кілька карток
        if changed:
            self.save()

        self.after(1000, self.tick)

    def close(self):
        self.save()
        self.destroy()


if __name__ == "__main__":
    os.makedirs(APP_DIR, exist_ok=True)
    AionEnergyApp().mainloop()
