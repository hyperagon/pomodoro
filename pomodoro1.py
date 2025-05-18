# pip install pygame
# Vibe-coded by Hyperag⬡n

import tkinter as tk
from tkinter import simpledialog, colorchooser, messagebox
import threading
import os
import configparser
import pygame

# Initialize pygame mixer safely
try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Failed to initialize sound system: {e}")

# Constants
DEFAULT_TOTAL_MINUTES = 60
DEFAULT_BREAK_TRIGGER = 35
DEFAULT_NORMAL_BG = "black"
DEFAULT_BREAK_BG = "red"
DEFAULT_NORMAL_FG = "white"
DEFAULT_BREAK_FG = "white"
DEFAULT_LONG_BREAK_MINUTES = 15
DEFAULT_SHORT_BREAK_MINUTES = 5
SETTINGS_FILE = "settings.ini"

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)

        self.window_width = 200
        self.window_height = 100

        # Load settings
        self.load_settings()

        # Set background
        self.root.configure(bg=self.normal_bg)

        # Load window position or center
        x, y = self.load_window_position()
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

        self.label = tk.Label(root, text="", font=("Helvetica", 28, "bold"), fg=self.normal_fg, bg=self.normal_bg)
        self.label.pack(expand=True, fill='both')

        # Timer state
        self.seconds_left = self.total_minutes * 60
        self.running = True
        self.paused = False
        self.break_triggered = False
        self.session_counter = 0  # Counter for completed sessions

        # Mouse drag state
        self.offset_x = 0
        self.offset_y = 0

        # Bind events
        self.root.bind("<Button-1>", self.on_click)
        self.root.bind("<B1-Motion>", self.on_drag)
        self.root.bind("<Double-Button-1>", self.on_double_click)
        self.root.bind("<Button-3>", self.on_right_click)

        self.update_display()
        self.root.after(1000, self.timer_tick)

    def timer_tick(self):
        if self.running and not self.paused:
            self.seconds_left -= 1
            self.update_display()

            if self.seconds_left == self.break_trigger * 60 and not self.break_triggered:
                self.break_triggered = True
                self.trigger_break()

            if self.seconds_left <= 0:
                self.seconds_left = 0
                self.running = False
                self.root.after(1000, self.reset_timer)
                return

        self.root.after(1000, self.timer_tick)

    def reset_timer(self):
        threading.Thread(target=self.play_sound, daemon=True).start()
        self.session_counter += 1  # Increment session counter
        self.seconds_left = self.total_minutes * 60
        self.break_triggered = False
        self.running = True
        self.paused = False
        self.root.configure(bg=self.normal_bg)
        self.label.configure(bg=self.normal_bg, fg=self.normal_fg)
        self.update_display()
        self.root.after(1000, self.timer_tick)

    def update_display(self):
        minutes = self.seconds_left // 60
        seconds = self.seconds_left % 60
        if self.paused:
            self.label.config(text=f"|| ({minutes:02}:{seconds:02})")
        else:
            self.label.config(text=f"{minutes:02}:{seconds:02}")

    def trigger_break(self):
        # Determine break duration based on session counter
        if self.session_counter % 4 == 0:
            break_duration = self.long_break_minutes
        else:
            break_duration = self.short_break_minutes

        self.seconds_left = break_duration * 60
        self.root.configure(bg=self.break_bg)
        self.label.configure(bg=self.break_bg, fg=self.break_fg)
        threading.Thread(target=self.play_sound, daemon=True).start()

    def play_sound(self):
        try:
            if os.path.exists("4.wav"):
                pygame.mixer.music.load("4.wav")
                pygame.mixer.music.play()
            else:
                print("Sound file not found: 4.wav")
        except Exception as e:
            print("Sound error:", e)

    def on_click(self, event):
        self.offset_x = event.x
        self.offset_y = event.y
        self.paused = not self.paused
        self.update_display()

    def on_drag(self, event):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = self.root.winfo_pointerx() - self.offset_x
        y = self.root.winfo_pointery() - self.offset_y

        threshold = 20

        if abs(x) < threshold:
            x = 0
        if abs((x + self.window_width) - screen_width) < threshold:
            x = screen_width - self.window_width
        if abs(y) < threshold:
            y = 0
        if abs((y + self.window_height) - screen_height) < threshold:
            y = screen_height - self.window_height

        self.save_settings()
        self.root.geometry(f'+{x}+{y}')

    def on_double_click(self, event):
        self.save_settings()
        self.root.destroy()

    def on_right_click(self, event):
        self.open_config_window()

    def open_config_window(self):
        # Store current values
        temp_total_minutes = self.total_minutes
        temp_break_trigger = self.break_trigger
        temp_normal_bg = self.normal_bg
        temp_break_bg = self.break_bg
        temp_normal_fg = self.normal_fg
        temp_break_fg = self.break_fg
        temp_long_break_minutes = self.long_break_minutes
        temp_short_break_minutes = self.short_break_minutes

        config_win = tk.Toplevel(self.root)
        config_win.title("Pomodoro Settings")
        config_win.geometry("300x430")
        config_win.attributes('-topmost', True)

        # Time entries
        tk.Label(config_win, text="Pomodoro Duration (min):").pack(pady=5)
        total_entry = tk.Entry(config_win)
        total_entry.insert(0, str(temp_total_minutes))
        total_entry.pack()

        tk.Label(config_win, text="Break Trigger Time (min):").pack(pady=5)
        break_entry = tk.Entry(config_win)
        break_entry.insert(0, str(temp_break_trigger))
        break_entry.pack()

        tk.Label(config_win, text="Long Break Duration (min):").pack(pady=5)
        long_break_entry = tk.Entry(config_win)
        long_break_entry.insert(0, str(temp_long_break_minutes))
        long_break_entry.pack()

        tk.Label(config_win, text="Short Break Duration (min):").pack(pady=5)
        short_break_entry = tk.Entry(config_win)
        short_break_entry.insert(0, str(temp_short_break_minutes))
        short_break_entry.pack()

        # Color pickers
        def choose_color(current_color):
            color = colorchooser.askcolor(title="Choose color", initialcolor=current_color)
            return color[1] if color[1] else current_color

        def choose_normal_color():
            nonlocal temp_normal_bg
            temp_normal_bg = choose_color(temp_normal_bg)

        def choose_break_color():
            nonlocal temp_break_bg
            temp_break_bg = choose_color(temp_break_bg)

        def choose_normal_fg():
            nonlocal temp_normal_fg
            temp_normal_fg = choose_color(temp_normal_fg)

        def choose_break_fg():
            nonlocal temp_break_fg
            temp_break_fg = choose_color(temp_break_fg)

        tk.Button(config_win, text="Choose Normal BG Color", command=choose_normal_color).pack(pady=5)
        tk.Button(config_win, text="Choose Break BG Color", command=choose_break_color).pack(pady=5)
        tk.Button(config_win, text="Choose Normal Text Color", command=choose_normal_fg).pack(pady=5)
        tk.Button(config_win, text="Choose Break Text Color", command=choose_break_fg).pack(pady=5)

        def save_and_apply():
            try:
                new_total = int(total_entry.get())
                new_break = int(break_entry.get())
                new_long_break = int(long_break_entry.get())
                new_short_break = int(short_break_entry.get())

                self.total_minutes = new_total
                self.break_trigger = new_break
                self.long_break_minutes = new_long_break
                self.short_break_minutes = new_short_break

                self.normal_bg = temp_normal_bg
                self.break_bg = temp_break_bg
                self.normal_fg = temp_normal_fg
                self.break_fg = temp_break_fg

                # Apply correct color depending on state
                if self.break_triggered:
                    self.root.configure(bg=self.break_bg)
                    self.label.configure(bg=self.break_bg, fg=self.break_fg)
                else:
                    self.root.configure(bg=self.normal_bg)
                    self.label.configure(bg=self.normal_bg, fg=self.normal_fg)

                self.save_settings()
                self.update_display()
                config_win.destroy()
            except ValueError:
                messagebox.showerror("Invalid input", "Please enter valid integer values.")

        tk.Button(config_win, text="Save and Apply", command=save_and_apply).pack(pady=10)

    def load_window_position(self):
        config = configparser.ConfigParser()
        if os.path.exists(SETTINGS_FILE):
            config.read(SETTINGS_FILE)
            try:
                x = int(config.get("position", "x", fallback="0"))
                y = int(config.get("position", "y", fallback="0"))
                return x, y
            except Exception as e:
                print("Error loading position:", e)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        return x, y

    def load_settings(self):
        config = configparser.ConfigParser()
        if os.path.exists(SETTINGS_FILE):
            config.read(SETTINGS_FILE)
            self.total_minutes = int(config.get("timer", "total_minutes", fallback=DEFAULT_TOTAL_MINUTES))
            self.break_trigger = int(config.get("timer", "break_trigger", fallback=DEFAULT_BREAK_TRIGGER))
            self.normal_bg = config.get("colors", "normal_bg", fallback=DEFAULT_NORMAL_BG)
            self.break_bg = config.get("colors", "break_bg", fallback=DEFAULT_BREAK_BG)
            self.normal_fg = config.get("text", "normal_fg", fallback=DEFAULT_NORMAL_FG)
            self.break_fg = config.get("text", "break_fg", fallback=DEFAULT_BREAK_FG)
            self.long_break_minutes = int(config.get("timer", "long_break_minutes", fallback=DEFAULT_LONG_BREAK_MINUTES))
            self.short_break_minutes = int(config.get("timer", "short_break_minutes", fallback=DEFAULT_SHORT_BREAK_MINUTES))
        else:
            # Defaults
            self.total_minutes = DEFAULT_TOTAL_MINUTES
            self.break_trigger = DEFAULT_BREAK_TRIGGER
            self.normal_bg = DEFAULT_NORMAL_BG
            self.break_bg = DEFAULT_BREAK_BG
            self.normal_fg = DEFAULT_NORMAL_FG
            self.break_fg = DEFAULT_BREAK_FG
            self.long_break_minutes = DEFAULT_LONG_BREAK_MINUTES
            self.short_break_minutes = DEFAULT_SHORT_BREAK_MINUTES

    def save_settings(self):
        config = configparser.ConfigParser()

        # Load existing if available
        if os.path.exists(SETTINGS_FILE):
            config.read(SETTINGS_FILE)

        # Timer settings
        if 'timer' not in config:
            config['timer'] = {}
        config['timer']['total_minutes'] = str(self.total_minutes)
        config['timer']['break_trigger'] = str(self.break_trigger)
        config['timer']['long_break_minutes'] = str(self.long_break_minutes)
        config['timer']['short_break_minutes'] = str(self.short_break_minutes)

        # Color settings
        if 'colors' not in config:
            config['colors'] = {}
        config['colors']['normal_bg'] = self.normal_bg
        config['colors']['break_bg'] = self.break_bg

        # Text color settings
        if 'text' not in config:
            config['text'] = {}
        config['text']['normal_fg'] = self.normal_fg
        config['text']['break_fg'] = self.break_fg

        # Window position
        if 'position' not in config:
            config['position'] = {}
        config['position']['x'] = str(self.root.winfo_x())
        config['position']['y'] = str(self.root.winfo_y())

        with open(SETTINGS_FILE, 'w') as configfile:
            config.write(configfile)

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()

