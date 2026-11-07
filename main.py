import json
import math
import os
import tempfile
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

ENERGY_PER_TICK = 15
TICK_HOURS = 3
TICK_SECONDS = TICK_HOURS * 3600

APP_DIR = os.path.join(
    os.getenv("APPDATA") or os.path.expanduser("~"),
    "AionEnergyCalculator"
)
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
        "edit": "✏️ Редагувати",
        "save": "💾 Зберегти",
        "cancel": "Скасувати",
        "delete": "Видалити",
        "new": "Новий персонаж",
        "name": "Ім'я персонажа",
        "energy": "Енергія (0–{maximum})",
        "time": "Час до наступних +15 (ГГ:ХХ)",
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
        "time_error": "Введи час у форматі ГГ:ХХ, наприклад 2:30.",
        "minutes_error": "Хвилини мають бути від 0 до 59.",
        "delete_title": "Видалити персонажа",
        "delete_confirm": "Видалити «{name}»?",
        "save_error": "Помилка збереження",
        "load_error": "Помилка завантаження",
        "recovered_title": "Енергію відновлено",
        "recovered_text": "Поки програма була закрита:\n\n",
        "recovered_line": "• {name}: +{amount} енергії",
        "next_in": " буде через ",
        "days": "д",
        "full_energy": "Вже максимум",
        "empty": "—",
    },
    "en": {
        "title": "Aion 2 — Character Energy",
        "heading": "Character Energy",
        "subtitle": "+15 energy every 3 hours · Maximum {maximum}",
        "settings": "⚙ Settings",
        "add": "+ Add character",
        "save_all": "💾 Save all",
        "edit": "✏️ Edit",
        "save": "💾 Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "new": "New character",
        "name": "Character name",
        "energy": "Energy (0–{maximum})",
        "time": "Time until next +15 (HH:MM)",
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
        "time_error": "Enter time as HH:MM, for example 2:30.",
        "minutes_error": "Minutes must be between 0 and 59.",
        "delete_title": "Delete character",
        "delete_confirm": "Delete “{name}”?",
        "save_error": "Save error",
        "load_error": "Load error",
        "recovered_title": "Energy restored",
        "recovered_text": "While the app was closed:\n\n",
        "recovered_line": "• {name}: +{amount} energy",
        "next_in": " in ",
        "days": "d",
        "full_energy": "Already full",
        "empty": "—",
    }
}


PALETTES = {
    "light": {
        "bg": "#eef2f7",
        "card": "#ffffff",
        "text": "#263445",
        "muted": "#718096",
        "blue": "#2878d0",
        "green": "#239b63",
        "red": "#d64545",
        "border": "#dce3ec",
        "entry": "#ffffff",
        "track": "#e8edf3",
        "soft": "#e8f1fc",
        "button_text": "#ffffff"
    },
    "dark": {
        "bg": "#171c24",
        "card": "#222a35",
        "text": "#edf2f7",
        "muted": "#a0aec0",
        "blue": "#63a9f5",
        "green": "#55c995",
        "red": "#ff7777",
        "border": "#394555",
        "entry": "#303a48",
        "track": "#394555",
        "soft": "#30445b",
        "button_text": "#ffffff"
    },
}


def duration(seconds, app):
    seconds = max(0, int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    prefix = f"{days}{app.t('days')} " if days else ""
    return prefix + f"{hours:02}:{minutes:02}:{seconds:02}"


def read_energy(value, maximum, app):
    energy = int(value.strip())

    if not 0 <= energy <= maximum:
        raise ValueError(
            app.t("energy_range", maximum=maximum)
        )

    return energy


def read_time(value, app):
    parts = (
        value.strip()
        .replace(".", ":")
        .replace(",", ":")
        .split(":")
    )

    if len(parts) not in (1, 2):
        raise ValueError(app.t("time_error"))

    if not all(part.strip().isdigit() for part in parts):
        raise ValueError(app.t("time_error"))

    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) == 2 else 0

    if not 0 <= minutes <= 59:
        raise ValueError(app.t("minutes_error"))

    return timedelta(hours=hours, minutes=minutes)


class CharacterCard:

    def __init__(self, parent, app, data=None):
        self.app = app
        self.editing = False
        self.backup = None
        self.data = data or {}

        self.name = tk.StringVar(
            value=self.data.get("name", "")
        )
        self.energy = tk.StringVar(
            value=str(self.data.get("energy", 0))
        )
        self.time = tk.StringVar(value="03:00")

        self.next_tick = self._load_tick(
            self.data.get("target_timestamp")
        )

        p = app.p

        self.frame = tk.Frame(
            parent,
            bg=p["card"],
            padx=16,
            pady=12,
            highlightbackground=p["border"],
            highlightthickness=1
        )

        self.frame.columnconfigure(0, weight=1)

        head = tk.Frame(self.frame, bg=p["card"])
        head.grid(row=0, column=0, sticky="ew")
        head.columnconfigure(0, weight=1)

        self.title = tk.Label(
            head,
            text=self.name.get() or app.t("new"),
            font=("Segoe UI", 12, "bold"),
            bg=p["card"],
            fg=p["text"]
        )
        self.title.grid(row=0, column=0, sticky="w")

        self.button(
            head, app.t("edit"), self.begin_edit,
            p["soft"], p["blue"]
        ).grid(row=0, column=1, padx=4)

        self.button(
            head, app.t("delete"), self.delete,
            p["bg"], p["red"]
        ).grid(row=0, column=2)

        self.editor = tk.Frame(
            self.frame, bg=p["card"]
        )
        self.editor.grid(
            row=1, column=0, sticky="ew", pady=(10, 0)
        )
        self.editor.columnconfigure((0, 1), weight=1)

        self.name_entry = self.field(
            self.editor, app.t("name"), self.name, 0, 0
        )

        self.energy_entry = self.field(
            self.editor,
            app.t("energy", maximum=app.max_energy),
            self.energy, 0, 1
        )

        self.time_entry = self.field(
            self.editor, app.t("time"), self.time, 1, 0, 2
        )

        actions = tk.Frame(
            self.editor, bg=p["card"]
        )
        actions.grid(
            row=2, column=0, columnspan=2, sticky="e"
        )

        self.button(
            actions, app.t("save"), self.save_edit,
            p["green"], "white"
        ).pack(side="left", padx=4)

        self.button(
            actions, app.t("cancel"), self.cancel_edit,
            p["track"], p["text"]
        ).pack(side="left")

        self.status = tk.Frame(
            self.frame, bg=p["card"]
        )
        self.status.grid(
            row=2, column=0, sticky="ew", pady=(12, 0)
        )
        self.status.columnconfigure(0, weight=1)

        line = tk.Frame(
            self.status, bg=p["card"]
        )
        line.grid(row=0, column=0, sticky="ew")
        line.columnconfigure(0, weight=1)

        self.energy_label = tk.Label(
            line,
            font=("Segoe UI", 16, "bold"),
            bg=p["card"],
            fg=p["green"]
        )
        self.energy_label.grid(
            row=0, column=0, sticky="w"
        )

        self.timer_label = tk.Label(
            line,
            font=("Consolas", 11, "bold"),
            bg=p["card"],
            fg=p["blue"]
        )
        self.timer_label.grid(
            row=0, column=1, sticky="e"
        )

        self.bar = tk.Canvas(
            self.status,
            height=10,
            bg=p["track"],
            highlightthickness=0
        )
        self.bar.grid(
            row=1, column=0, sticky="ew", pady=8
        )
        self.bar.bind(
            "<Configure>",
            lambda _: self.draw_bar()
        )

        bottom = tk.Frame(
            self.status, bg=p["card"]
        )
        bottom.grid(row=2, column=0, sticky="ew")

        tk.Label(
            bottom,
            text=app.t("full"),
            bg=p["card"],
            fg=p["muted"],
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.full_label = tk.Label(
            bottom,
            bg=p["card"],
            fg=p["text"],
            font=("Segoe UI", 9, "bold")
        )
        self.full_label.pack(side="left", padx=6)

        self.name.trace_add(
            "write",
            lambda *_: self.title.config(
                text=self.name.get().strip() or app.t("new")
            )
        )

        # Важливо: тут більше немає автоматичного begin_edit().
        # Завантажені персонажі відкриваються у звичайному режимі.

        self.editor.grid_remove()
        self.refresh(datetime.now())

    @staticmethod
    def button(parent, text, command, bg, fg):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            font=("Segoe UI", 9),
            padx=10,
            pady=5,
            cursor="hand2"
        )

    def field(self, parent, label, variable, row, column, span=1):
        p = self.app.p

        box = tk.Frame(parent, bg=p["card"])
        box.grid(
            row=row,
            column=column,
            columnspan=span,
            sticky="ew",
            padx=(0, 10),
            pady=(0, 8)
        )

        tk.Label(
            box,
            text=label,
            bg=p["card"],
            fg=p["muted"],
            font=("Segoe UI", 8)
        ).pack(anchor="w")

        entry = tk.Entry(
            box,
            textvariable=variable,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            bg=p["entry"],
            fg=p["text"],
            insertbackground=p["text"]
        )
        entry.pack(fill="x", ipady=4, pady=3)

        return entry

    @staticmethod
    def _load_tick(timestamp):
        try:
            return (
                datetime.fromtimestamp(float(timestamp))
                if timestamp is not None else None
            )
        except (ValueError, TypeError, OSError, OverflowError):
            return None

    def begin_edit(self):
        if self.editing:
            return

        self.backup = (
            self.name.get(),
            self.energy.get(),
            self.time.get(),
            self.next_tick
        )

        if self.next_tick:
            remaining = max(
                0,
                int(
                    (self.next_tick - datetime.now())
                    .total_seconds()
                )
            )

            self.time.set(
                f"{remaining // 3600:02}:"
                f"{(remaining % 3600) // 60:02}"
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
        if self.backup:
            name, energy, time, tick = self.backup

            self.name.set(name)
            self.energy.set(energy)
            self.time.set(time)
            self.next_tick = tick

        self.end_edit()

    def save_edit(self):
        try:
            name = self.name.get().strip()

            if not name:
                raise ValueError(
                    self.app.t("name_required")
                )

            energy = read_energy(
                self.energy.get(),
                self.app.max_energy,
                self.app
            )

            tick = (
                datetime.now() + read_time(
                    self.time.get(), self.app
                )
                if energy < self.app.max_energy else None
            )

        except ValueError as error:
            messagebox.showerror(
                self.app.t("bad_data"),
                str(error),
                parent=self.app
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
            parent=self.app
        ):
            self.app.remove(self)

    def draw_bar(self):
        self.bar.delete("all")
        width = self.bar.winfo_width()

        try:
            energy = read_energy(
                self.energy.get(), 840, self.app
            )
        except ValueError:
            energy = 0

        if width > 1:
            self.bar.create_rectangle(
                0,
                0,
                width * min(
                    energy, self.app.max_energy
                ) / self.app.max_energy,
                10,
                fill=self.app.p["blue"],
                outline=""
            )

    def refresh(self, now):
        try:
            energy = read_energy(
                self.energy.get(), 840, self.app
            )
        except ValueError:
            energy = 0

        maximum = self.app.max_energy

        self.energy_label.config(
            text=f"{energy} / {maximum}"
        )
        self.draw_bar()

        if energy >= maximum:
            self.timer_label.config(
                text=self.app.t("max_label"),
                fg=self.app.p["green"]
            )
            self.full_label.config(
                text=self.app.t("max_now")
            )
            return

        if self.next_tick is None:
            self.timer_label.config(
                text=self.app.t("not_set"),
                fg=self.app.p["red"]
            )
            self.full_label.config(
                text=self.app.t("empty")
            )
            return

        left = (
            self.next_tick - now
        ).total_seconds()

        if left <= 0:
            ticks = int(
                (-left) // TICK_SECONDS
            ) + 1

            energy = min(
                maximum,
                energy + ticks * ENERGY_PER_TICK
            )

            self.next_tick += timedelta(
                seconds=ticks * TICK_SECONDS
            )

            self.energy.set(str(energy))
            self.app.save()

            self.energy_label.config(
                text=f"{energy} / {maximum}"
            )
            self.draw_bar()

        if energy >= maximum:
            self.timer_label.config(
                text=self.app.t("max_label"),
                fg=self.app.p["green"]
            )
            self.full_label.config(
                text=self.app.t("max_now")
            )

        else:
            left = max(
                0,
                (self.next_tick - now).total_seconds()
            )

            next_energy = min(
                maximum,
                energy + ENERGY_PER_TICK
            )

            self.timer_label.config(
                text=(
                    f"{next_energy}"
                    f"{self.app.t('next_in')}"
                    f"{duration(left, self.app)}"
                ),
                fg=self.app.p["blue"]
            )

            ticks = math.ceil(
                (maximum - energy) / ENERGY_PER_TICK
            )

            target = self.next_tick + timedelta(
                seconds=(ticks - 1) * TICK_SECONDS
            )

            if self.app.language == "uk":
                days = [
                    "Пн", "Вт", "Ср", "Чт",
                    "Пт", "Сб", "Нд"
                ]
                full = (
                    f"{days[target.weekday()]}, "
                    f"{target:%d.%m о %H:%M}"
                )
            else:
                full = (
                    f"{target:%a, %b %d at %H:%M}"
                )

            self.full_label.config(text=full)

    def to_dict(self):
        try:
            energy = read_energy(
                self.energy.get(), 840, self.app
            )
        except ValueError:
            return None

        name = self.name.get().strip()

        if not name:
            return None

        return {
            "name": name,
            "energy": energy,
            "target_timestamp": (
                self.next_tick.timestamp()
                if self.next_tick else None
            )
        }


class AionEnergyApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.settings = {
            "theme": "light",
            "language": "en",
            "subscription": False
        }

        self.load_settings()

        self.language = self.settings["language"]
        self.p = PALETTES[self.settings["theme"]]

        self.max_energy = (
            840 if self.settings["subscription"] else 560
        )

        self.title(self.t("title"))
        self.geometry("900x720")
        self.minsize(700, 480)

        self.cards = []
        self.configure(bg=self.p["bg"])

        self.build_ui()
        self.load()

        self.after(1000, self.tick)
        self.protocol("WM_DELETE_WINDOW", self.close)

    def t(self, key, **kwargs):
        return TEXTS[
            self.settings["language"]
        ].get(key, key).format(**kwargs)

    def load_settings(self):
        try:
            with open(
                SETTINGS_FILE, encoding="utf-8"
            ) as f:
                saved = json.load(f)

            if saved.get("theme") in PALETTES:
                self.settings["theme"] = saved["theme"]

            if saved.get("language") in TEXTS:
                self.settings["language"] = saved["language"]

            self.settings["subscription"] = bool(
                saved.get("subscription", False)
            )

        except (
            OSError,
            json.JSONDecodeError,
            AttributeError
        ):
            pass

    def save_settings(self):
        os.makedirs(APP_DIR, exist_ok=True)

        with open(
            SETTINGS_FILE, "w", encoding="utf-8"
        ) as f:
            json.dump(
                self.settings,
                f,
                ensure_ascii=False,
                indent=2
            )

    def build_ui(self):
        p = self.p

        top = tk.Frame(self, bg=p["bg"])
        top.pack(
            fill="x",
            padx=22,
            pady=(16, 12)
        )

        row = tk.Frame(top, bg=p["bg"])
        row.pack(fill="x")

        tk.Label(
            row,
            text=self.t("heading"),
            bg=p["bg"],
            fg=p["text"],
            font=("Segoe UI", 20, "bold")
        ).pack(side="left")

        CharacterCard.button(
            row,
            self.t("settings"),
            self.open_settings,
            p["track"],
            p["text"]
        ).pack(side="right")

        self.subtitle = tk.Label(
            top,
            text=self.t(
                "subtitle", maximum=self.max_energy
            ),
            bg=p["bg"],
            fg=p["muted"],
            font=("Segoe UI", 9)
        )
        self.subtitle.pack(
            anchor="w", pady=(3, 0)
        )

        area = tk.Frame(self, bg=p["bg"])
        area.pack(
            fill="both",
            expand=True,
            padx=22
        )

        self.canvas = tk.Canvas(
            area,
            bg=p["bg"],
            highlightthickness=0
        )

        scroll = tk.Scrollbar(
            area,
            orient="vertical",
            command=self.canvas.yview
        )

        self.list_frame = tk.Frame(
            self.canvas, bg=p["bg"]
        )

        self.window = self.canvas.create_window(
            (0, 0),
            window=self.list_frame,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=scroll.set
        )

        self.list_frame.bind(
            "<Configure>",
            lambda _: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(
                self.window, width=e.width
            )
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(
                int(-e.delta / 120), "units"
            )
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scroll.pack(
            side="right",
            fill="y"
        )

        footer = tk.Frame(self, bg=p["bg"])
        footer.pack(
            fill="x",
            padx=22,
            pady=14
        )

        CharacterCard.button(
            footer,
            self.t("add"),
            self.add,
            p["blue"],
            "white"
        ).pack(side="left")

        CharacterCard.button(
            footer,
            self.t("save_all"),
            self.save_all,
            p["soft"],
            p["text"]
        ).pack(side="right")

    def open_settings(self):
        win = tk.Toplevel(self)

        win.title(self.t("settings_title"))
        win.configure(bg=self.p["card"])
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        p = self.p

        theme = tk.StringVar(
            value=self.settings["theme"]
        )

        language = tk.StringVar(
            value=self.settings["language"]
        )

        subscription = tk.BooleanVar(
            value=self.settings["subscription"]
        )

        pad = {"padx": 18, "pady": 5}

        def heading(text):
            tk.Label(
                win,
                text=text,
                bg=p["card"],
                fg=p["text"],
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w", **pad)

        def choice(text, variable, value):
            tk.Radiobutton(
                win,
                text=text,
                variable=variable,
                value=value,
                bg=p["card"],
                fg=p["text"],
                selectcolor=p["entry"],
                activebackground=p["card"],
                activeforeground=p["text"],
                font=("Segoe UI", 9)
            ).pack(
                anchor="w",
                padx=30,
                pady=2
            )

        heading(self.t("appearance"))
        choice(self.t("light"), theme, "light")
        choice(self.t("dark"), theme, "dark")

        heading(self.t("language"))
        choice(
            self.t("ukrainian"), language, "uk"
        )
        choice(
            self.t("english"), language, "en"
        )

        heading(self.t("account"))
        choice(
            self.t("standard"), subscription, False
        )
        choice(
            self.t("subscription"), subscription, True
        )

        buttons = tk.Frame(
            win, bg=p["card"]
        )
        buttons.pack(
            fill="x",
            padx=18,
            pady=16
        )

        def apply():
            pending_cards = []

            for card in self.cards:
                if card.editing and card.backup:
                    name, energy_text, _, tick = card.backup

                    try:
                        energy = int(energy_text)
                    except ValueError:
                        continue

                    if name.strip():
                        pending_cards.append({
                            "name": name,
                            "energy": energy,
                            "target_timestamp": (
                                tick.timestamp() if tick else None
                            )
                        })

                else:
                    item = card.to_dict()

                    if item:
                        pending_cards.append(item)

            self._pending_cards = pending_cards

            self.settings.update(
                theme=theme.get(),
                language=language.get(),
                subscription=subscription.get()
            )

            self.language = self.settings["language"]
            self.p = PALETTES[
                self.settings["theme"]
            ]

            self.max_energy = (
                840 if self.settings["subscription"]
                else 560
            )

            try:
                self.save_settings()
            except OSError as error:
                messagebox.showerror(
                    self.t("save_error"),
                    str(error),
                    parent=win
                )

            win.destroy()
            self.rebuild()

        CharacterCard.button(
            buttons,
            self.t("apply"),
            apply,
            p["blue"],
            "white"
        ).pack(side="right", padx=4)

        CharacterCard.button(
            buttons,
            self.t("close"),
            win.destroy,
            p["track"],
            p["text"]
        ).pack(side="right")

        win.update_idletasks()

        win.geometry(
            f"{win.winfo_reqwidth()}x{win.winfo_reqheight()}"
        )

    def rebuild(self):
        data = getattr(
            self, "_pending_cards", []
        )

        for widget in self.winfo_children():
            widget.destroy()

        self.cards = []
        self.configure(bg=self.p["bg"])
        self.title(self.t("title"))

        self.build_ui()

        for item in data:
            card = CharacterCard(
                self.list_frame, self, item
            )

            self.cards.append(card)
            card.frame.pack(
                fill="x", pady=(0, 10)
            )

        self.save()

    def add(self):
        card = CharacterCard(
            self.list_frame, self
        )

        self.cards.append(card)
        card.frame.pack(
            fill="x", pady=(0, 10)
        )

        # Новий персонаж одразу відкривається для заповнення.
        card.begin_edit()

        self.canvas.yview_moveto(1)

    def remove(self, card):
        self.cards.remove(card)
        card.frame.destroy()
        self.save()

    def save(self):
        os.makedirs(APP_DIR, exist_ok=True)

        data = []

        for card in self.cards:
            if card.editing and card.backup:
                name, energy_text, _, tick = card.backup

                try:
                    energy = int(energy_text)
                except ValueError:
                    continue

                if name.strip():
                    data.append({
                        "name": name.strip(),
                        "energy": energy,
                        "target_timestamp": (
                            tick.timestamp() if tick else None
                        )
                    })

            elif not card.editing:
                item = card.to_dict()

                if item:
                    data.append(item)

        temp = None

        try:
            fd, temp = tempfile.mkstemp(
                dir=APP_DIR,
                suffix=".tmp"
            )

            with os.fdopen(
                fd, "w", encoding="utf-8"
            ) as f:
                json.dump(
                    data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

                f.flush()
                os.fsync(f.fileno())

            os.replace(temp, DATA_FILE)

        except OSError as error:
            if temp and os.path.exists(temp):
                os.remove(temp)

            messagebox.showerror(
                self.t("save_error"),
                str(error),
                parent=self
            )

    def save_all(self):
        # Зберігаємо всі відкриті форми редагування.
        for card in self.cards[:]:
            if card.editing:
                success = card.save_edit()

                # Якщо форма містить помилку,
                # залишаємо її відкритою.
                if not success:
                    return

        # Фінальне збереження всіх персонажів.
        self.save()

    def load(self):
        if not os.path.exists(DATA_FILE):
            return

        try:
            with open(
                DATA_FILE, encoding="utf-8"
            ) as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError(
                    "Invalid save file format."
                )

            now = datetime.now()
            recovered = []

            for item in data:
                try:
                    name = str(
                        item.get("name", "")
                    ).strip()

                    energy = read_energy(
                        str(item.get("energy", 0)),
                        840,
                        self
                    )

                    if not name:
                        continue

                    tick = CharacterCard._load_tick(
                        item.get("target_timestamp")
                    )

                    if (
                        energy < self.max_energy
                        and tick
                        and tick <= now
                    ):
                        ticks = int(
                            (now - tick).total_seconds()
                            // TICK_SECONDS
                        ) + 1

                        old = energy

                        energy = min(
                            self.max_energy,
                            energy + ticks * ENERGY_PER_TICK
                        )

                        tick += timedelta(
                            seconds=ticks * TICK_SECONDS
                        )

                        if energy > old:
                            recovered.append(
                                self.t(
                                    "recovered_line",
                                    name=name,
                                    amount=energy - old
                                )
                            )

                    if energy >= 840:
                        tick = None

                    card = CharacterCard(
                        self.list_frame,
                        self,
                        {
                            "name": name,
                            "energy": energy,
                            "target_timestamp": (
                                tick.timestamp() if tick else None
                            )
                        }
                    )

                    self.cards.append(card)
                    card.frame.pack(
                        fill="x", pady=(0, 10)
                    )

                except (
                    AttributeError,
                    ValueError,
                    TypeError,
                    OSError,
                    OverflowError
                ):
                    continue

            if recovered:
                messagebox.showinfo(
                    self.t("recovered_title"),
                    self.t("recovered_text")
                    + "\n".join(recovered),
                    parent=self
                )

            self.save()

        except (
            OSError,
            json.JSONDecodeError,
            ValueError
        ) as error:
            messagebox.showerror(
                self.t("load_error"),
                str(error),
                parent=self
            )

    def tick(self):
        now = datetime.now()

        for card in self.cards:
            if not card.editing:
                card.refresh(now)

        self.after(1000, self.tick)

    def close(self):
        self.save()
        self.destroy()


if __name__ == "__main__":
    os.makedirs(APP_DIR, exist_ok=True)
    AionEnergyApp().mainloop()