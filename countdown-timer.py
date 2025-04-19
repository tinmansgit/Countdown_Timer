# Countdown Timer v2.0 20250414.07:50
import tkinter as tk
from tkinter import ttk, messagebox
import time
import logger_countdown_timer
from logger_countdown_timer import log_error, log_debug
import os
import subprocess

DEFAULT_SOUND_FILE = "/path/to/your/Music/level-up.mp3"
log_debug("Sound file set to level-up.mp3")

class CountdownTimer:
    def __init__(self, master):
        self.master = master
        log_debug("Initializing Countdown Timer")
        master.title("Countdown Timer")
        try:
            icon = tk.PhotoImage(file="countdown_timer_icon.png")
            master.iconphoto(False, icon)
        except Exception as e:
            log_error(f"Failed to load icon: {e}")
        master.configure(bg="black")
        self.container = tk.Frame(master, bg="black", padx=10, pady=10)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.total_seconds = 0
        self.repeat = 1
        self.current_repeat = 1
        self.running = False
        self.timer_id = None
        self.configured_mp3 = DEFAULT_SOUND_FILE if os.path.isfile(DEFAULT_SOUND_FILE) else None
        log_debug("UI layout")
        self.create_input_frame()
        self.countdown_label = tk.Label(self.container, text="00:00:00", font=("Helvetica", 48), fg="white", bg="black")
        self.countdown_label.pack(pady=10)
        style = ttk.Style(self.container)
        style.theme_use('clam')
        style.configure("White.Horizontal.TProgressbar", foreground='white', background='white', troughcolor='black')
        self.progress = ttk.Progressbar(self.container, orient='horizontal', mode='determinate', length=400, style="White.Horizontal.TProgressbar")
        self.progress.pack(pady=1)
        self.text_display = tk.Label(self.container, text="", font=("Helvetica", 14), fg="white", bg="black")
        self.text_display.pack(pady=1)
        self.start_button = tk.Button(self.container, text="Start", command=self.start_timer, bg="gray", fg="white")
        self.start_button.pack(pady=1)
        master.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_input_frame(self):
        log_debug("Layout for input fields")
        input_frame = tk.Frame(self.container, bg="black")
        input_frame.pack(pady=10)
        tk.Label(input_frame, text="Hours", fg="white", bg="black").grid(row=0, column=0, padx=5, pady=5)
        self.hours_entry = tk.Entry(input_frame, width=5)
        self.hours_entry.grid(row=1, column=0, padx=5)
        tk.Label(input_frame, text="Minutes", fg="white", bg="black").grid(row=0, column=1, padx=5, pady=5)
        self.minutes_entry = tk.Entry(input_frame, width=5)
        self.minutes_entry.grid(row=1, column=1, padx=5)
        tk.Label(input_frame, text="Seconds", fg="white", bg="black").grid(row=0, column=2, padx=5, pady=5)
        self.seconds_entry = tk.Entry(input_frame, width=5)
        self.seconds_entry.grid(row=1, column=2, padx=5)
        tk.Label(input_frame, text="Repeats", fg="white", bg="black").grid(row=0, column=3, padx=5, pady=5)
        self.repeat_entry = tk.Entry(input_frame, width=5)
        self.repeat_entry.grid(row=1, column=3, padx=5)

    def start_timer(self):
        log_debug("start_timer function called")
        if self.running:
            return
        try:
            hrs = self.parse_input(self.hours_entry.get())
            mins = self.parse_input(self.minutes_entry.get())
            secs = self.parse_input(self.seconds_entry.get())
            repeats = self.parse_input(self.repeat_entry.get(), allowZero=True)
            if repeats == 0:
                repeats = 1
            self.total_seconds = hrs * 3600 + mins * 60 + secs
            if self.total_seconds <= 0:
                raise ValueError("Total time must be greater than 0 seconds.")
            self.repeat = repeats
            self.current_repeat = 1
            self.running = True
            self.progress['maximum'] = self.total_seconds
            self.progress['value'] = 0
            self.start_button.config(state=tk.DISABLED)
            self.start_time = time.time()
            self.countdown()
        except Exception as e:
            log_error("Error starting timer: %s", e)
            log_debug("Error starting timer: %s", e)
            messagebox.showerror("Input Error", f"Error: {e}")

    def parse_input(self, input_str, allowZero=False):
        log_debug("Evaluating input")
        if input_str.strip() == "":
            return 0
        try:
            value = int(input_str)
            if value < 0 or (not allowZero and value == 0):
                raise ValueError("Value must be a positive integer.")
            return value
        except Exception:
            raise ValueError(f"Invalid number provided: {input_str}")

    def countdown(self):
        log_debug("Counting down")
        elapsed = int(time.time() - self.start_time)
        seconds_left = self.total_seconds - elapsed
        if seconds_left >= 0 and self.running:
            hrs, remainder = divmod(seconds_left, 3600)
            mins, secs = divmod(remainder, 60)
            self.countdown_label.config(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")
            self.progress['value'] = elapsed
            self.text_display.config(text=f"Repeat {self.current_repeat} of {self.repeat}")
            self.timer_id = self.master.after(250, self.countdown)
        else:
            self.play_sound()
            if self.current_repeat < self.repeat and self.running:
                self.current_repeat += 1
                self.start_time = time.time()
                self.progress['value'] = 0
                self.timer_id = self.master.after(250, self.countdown)
            else:
                self.running = False
                self.start_button.config(state=tk.NORMAL)
                self.text_display.config(text="Countdown completed!")
                self.timer_id = None

    def play_sound(self):
        if self.configured_mp3 and os.path.isfile(self.configured_mp3):
            try:
                log_debug("Connecting mpv to jack")
                subprocess.run(["mpv", "--ao=jack", self.configured_mp3], check=True)
            except Exception as e:
                log_error("Error playing MP3 via mpv: %s", e)
                log_debug("Error playing MP3 via mpv: %s", e)
        else:
            self.master.bell()

    def on_close(self):
        self.running = False
        if self.timer_id is not None:
            self.master.after_cancel(self.timer_id)
        self.master.destroy()

def main():
    try:
        root = tk.Tk()
        root.configure(bg="black")
        app = CountdownTimer(root)
        root.mainloop()
    except Exception as e:
        log_error("Error in main application: %s", e)

if __name__ == "__main__":
    main()
