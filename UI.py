import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dotenv import load_dotenv
from google import genai
from google.genai import types
import doc_process
from tts import TTSManager
import json
from datetime import datetime

THEMES = {
    "dark": {
        "bg": "#1E1E2E",
        "chat_bg": "#181825",
        "user_text": "#FFFFFF",
        "bot_text": "#CDD6F4",
        "input_bg": "#313244",
        "input_fg": "#CDD6F4",
        "button_bg": "#3B82F6",
        "button_fg": "#FFFFFF",
        "status_bg": "#11111B",
        "status_fg": "#6C7086",
        "timestamp": "#6C7086",
        "thinking": "#F38BA8",
        "title_bg": "#181825",
        "title_fg": "#CDD6F4",
        "user_name": "#3B82F6",
        "bot_name": "#A6E3A1",
        "system_msg": "#6C7086",
    },
    "light": {
        "bg": "#F5F5F5",
        "chat_bg": "#FFFFFF",
        "user_text": "#1E1E2E",
        "bot_text": "#1E1E2E",
        "input_bg": "#FFFFFF",
        "input_fg": "#1E1E2E",
        "button_bg": "#3B82F6",
        "button_fg": "#FFFFFF",
        "status_bg": "#E0E0E0",
        "status_fg": "#666666",
        "timestamp": "#999999",
        "thinking": "#E05C5C",
        "title_bg": "#FFFFFF",
        "title_fg": "#1E1E2E",
        "user_name": "#3B82F6",
        "bot_name": "#0F6E56",
        "system_msg": "#999999",
    }
}

AVATAR_BOT  = "🤖"
AVATAR_USER = "🧑"

class ChatUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Chatbot")
        self.current_theme = "dark"
        self.bot_started = False
        self.message_count = 0

        screen_width  = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{int(screen_width*0.55)}x{int(screen_height*0.75)}")
        self.root.minsize(600, 500)

        self.font_family = "Arial"
        self.font_size   = 12

        self.tts = TTSManager()
        self.init_genai()
        self.setup_ui()
        self.create_menu()
        self.messages = []
        self.apply_theme()

    def init_genai(self):
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            messagebox.showerror("Error", "GEMINI_API_KEY is not set.")
            sys.exit(1)
        try:
            self.client = genai.Client(api_key=api_key)
            self.model  = "gemini-2.5-flash-lite"
        except Exception as e:
            messagebox.showerror("Error", f"Failed to init Gemini: {e}")
            sys.exit(1)

        prompt_file = "prompt.txt"
        system_text = (
            "You are a helpful multi-lingual assistant. Keep your answers under 10 words. "
            "When the user asks for a translation or speaks in a specific language "
            "(including all global and Indian regional languages like Kannada, Tamil, "
            "Telugu, Hindi, etc.), YOU MUST respond accurately using that precise "
            "language's native script. Do not default to Hindi for other Indian languages. "
            "Provide no English wrapper text."
        )
        if os.path.exists(prompt_file):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                system_text = f.read().strip()

        self.tools = [types.Tool(googleSearch=types.GoogleSearch())]
        self.generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            tools=self.tools,
            system_instruction=[types.Part.from_text(text=system_text)],
        )

    def create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load System Prompt",  command=self.load_system_prompt)
        file_menu.add_command(label="Load Document (QA)",  command=self.load_document)
        file_menu.add_separator()
        file_menu.add_command(label="Save Chat History",   command=self.save_chat_history)
        file_menu.add_command(label="Load Chat History",   command=self.load_chat_history)
        file_menu.add_separator()
        file_menu.add_command(label="Export Chat as TXT",  command=self.export_txt)
        file_menu.add_separator()
        file_menu.add_command(label="Exit",                command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Dark/Light Theme", command=self.toggle_theme)
        view_menu.add_command(label="Increase Font",           command=self.increase_font)
        view_menu.add_command(label="Decrease Font",           command=self.decrease_font)
        menubar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menubar)

    def setup_ui(self):
        # ── Title bar ──────────────────────────────────────────────────────
        self.title_frame = tk.Frame(self.root)
        self.title_frame.pack(side=tk.TOP, fill=tk.X)

        self.title_label = tk.Label(
            self.title_frame,
            text="  🤖  Gemini AI Chatbot",
            font=("Arial", 14, "bold"),
            pady=8,
        )
        self.title_label.pack(side=tk.LEFT, padx=10)

        self.theme_btn = tk.Button(
            self.title_frame,
            text="☀ Light",
            command=self.toggle_theme,
            relief=tk.FLAT,
            cursor="hand2",
            font=("Arial", 10),
            bd=0,
            padx=8,
        )
        self.theme_btn.pack(side=tk.RIGHT, padx=10)

        self.prompt_label = tk.Label(
            self.title_frame,
            text="System: Default",
            font=("Arial", 9),
        )
        self.prompt_label.pack(side=tk.RIGHT, padx=10)

        # ── Top controls ───────────────────────────────────────────────────
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)

        tk.Button(self.top_frame, text="A-", width=3, command=self.decrease_font, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(self.top_frame, text="A+", width=3, command=self.increase_font, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)

        self.voice_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.top_frame, text="🔊 Voice", variable=self.voice_var,
                       command=lambda: self.tts.set_voice_enabled(self.voice_var.get()),
                       relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=5)

        tk.Button(self.top_frame, text="⏸", width=3, command=self.tts.pause,  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(self.top_frame, text="▶", width=3, command=self.tts.resume, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(self.top_frame, text="⏹", width=3, command=self.tts.stop,   relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)

        tk.Button(self.top_frame, text="🗑 Clear", command=self.clear_chat,
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=8)

        self.font_var = tk.StringVar(value=self.font_family)
        font_options  = ["Arial", "Courier New", "Times New Roman", "Verdana"]
        font_dropdown = ttk.Combobox(self.top_frame, textvariable=self.font_var,
                                     values=font_options, state="readonly", width=14)
        font_dropdown.pack(side=tk.LEFT, padx=5)
        font_dropdown.bind("<<ComboboxSelected>>", self.change_font)

        # ── Status bar — pack BOTTOM first ─────────────────────────────────
        self.status_frame = tk.Frame(self.root, height=24)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(
            self.status_frame,
            text="  Model: gemini-2.5-flash-lite   |   Messages: 0   |   Ready",
            font=("Arial", 8),
            anchor=tk.W,
        )
        self.status_label.pack(side=tk.LEFT, padx=6, pady=2)

        # ── Input area — pack BOTTOM before chat ───────────────────────────
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=6)

        self.char_count_label = tk.Label(self.input_frame, text="0 / 500", font=("Arial", 8))
        self.char_count_label.pack(side=tk.BOTTOM, anchor=tk.E, padx=4)

        inner = tk.Frame(self.input_frame)
        inner.pack(fill=tk.X)

        self.entry = tk.Entry(inner, font=(self.font_family, self.font_size), relief=tk.FLAT, bd=6)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        self.entry.bind("<Return>", lambda e: self.send_message())
        self.entry.bind("<KeyRelease>", self.update_char_count)
        self.entry.focus_set()

        self.send_btn = tk.Button(
            inner, text="Send ➤", command=self.send_message,
            relief=tk.FLAT, cursor="hand2",
            padx=12, pady=6, font=("Arial", 10, "bold"),
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(6, 0))

        # ── Chat display — pack LAST fills remaining space ─────────────────
        chat_frame = tk.Frame(self.root)
        chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)

        scrollbar = tk.Scrollbar(chat_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_display = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=(self.font_family, self.font_size),
            yscrollcommand=scrollbar.set,
            padx=12, pady=8,
            spacing1=4, spacing3=4,
            relief=tk.FLAT,
            cursor="arrow",
        )
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.chat_display.yview)

        self.chat_display.tag_config("user_name",  font=("Arial", 9, "bold"))
        self.chat_display.tag_config("bot_name",   font=("Arial", 9, "bold"))
        self.chat_display.tag_config("user_msg",   font=(self.font_family, self.font_size))
        self.chat_display.tag_config("bot_msg",    font=(self.font_family, self.font_size))
        self.chat_display.tag_config("timestamp",  font=("Arial", 8))
        self.chat_display.tag_config("thinking",   font=("Arial", 10, "italic"))
        self.chat_display.tag_config("system_msg", font=("Arial", 9, "italic"))

    # ── Theme ──────────────────────────────────────────────────────────────
    def apply_theme(self):
        t = self.current_theme
        T = THEMES[t]

        self.root.configure(bg=T["bg"])
        self.title_frame.configure(bg=T["title_bg"])
        self.title_label.configure(bg=T["title_bg"], fg=T["title_fg"])
        self.theme_btn.configure(bg=T["title_bg"], fg=T["button_fg"])
        self.prompt_label.configure(bg=T["title_bg"], fg=T["status_fg"])
        self.top_frame.configure(bg=T["bg"])

        for w in self.top_frame.winfo_children():
            try:    w.configure(bg=T["bg"], fg=T["title_fg"])
            except: pass

        self.chat_display.configure(bg=T["chat_bg"], fg=T["bot_text"])
        self.chat_display.tag_config("user_name",  foreground=T["user_name"])
        self.chat_display.tag_config("bot_name",   foreground=T["bot_name"])
        self.chat_display.tag_config("user_msg",   foreground=T["user_text"])
        self.chat_display.tag_config("bot_msg",    foreground=T["bot_text"])
        self.chat_display.tag_config("timestamp",  foreground=T["timestamp"])
        self.chat_display.tag_config("thinking",   foreground=T["thinking"])
        self.chat_display.tag_config("system_msg", foreground=T["system_msg"])

        self.input_frame.configure(bg=T["bg"])
        self.char_count_label.configure(bg=T["bg"], fg=T["status_fg"])
        self.input_frame.winfo_children()[1].configure(bg=T["bg"])
        self.entry.configure(bg=T["input_bg"], fg=T["input_fg"], insertbackground=T["input_fg"])
        self.send_btn.configure(bg=T["button_bg"], fg=T["button_fg"])

        self.status_frame.configure(bg=T["status_bg"])
        self.status_label.configure(bg=T["status_bg"], fg=T["status_fg"])

        self.theme_btn.config(text="☀ Light" if t == "dark" else "🌙 Dark")

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()

    # ── Font ───────────────────────────────────────────────────────────────
    def increase_font(self):
        self.font_size += 2
        self.update_font()

    def decrease_font(self):
        if self.font_size > 6:
            self.font_size -= 2
            self.update_font()

    def change_font(self, event=None):
        self.font_family = self.font_var.get()
        self.update_font()

    def update_font(self):
        f = (self.font_family, self.font_size)
        self.chat_display.configure(font=f)
        self.chat_display.tag_config("user_msg", font=f)
        self.chat_display.tag_config("bot_msg",  font=f)
        self.entry.configure(font=f)

    # ── Char counter ───────────────────────────────────────────────────────
    def update_char_count(self, event=None):
        count = len(self.entry.get())
        self.char_count_label.config(text=f"{count} / 500")
        self.char_count_label.config(fg="#F38BA8" if count > 450 else THEMES[self.current_theme]["status_fg"])

    # ── Status bar ─────────────────────────────────────────────────────────
    def _update_status(self, state="Ready"):
        self.status_label.config(
            text=f"  Model: {self.model}   |   Messages: {self.message_count}   |   {state}"
        )

    # ── Helpers ────────────────────────────────────────────────────────────
    def _timestamp(self):
        return datetime.now().strftime("%H:%M")

    def _clear_display(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def _append_system(self, text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"  ─── {text} ───\n\n", "system_msg")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def _insert_user_bubble(self, text, ts=None):
        ts = ts or self._timestamp()
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{AVATAR_USER}  You", "user_name")
        self.chat_display.insert(tk.END, f"   {ts}\n", "timestamp")
        self.chat_display.insert(tk.END, f"  {text}\n\n", "user_msg")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def _insert_bot_bubble(self, text, ts=None):
        ts = ts or self._timestamp()
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{AVATAR_BOT}  Gemini", "bot_name")
        self.chat_display.insert(tk.END, f"   {ts}\n", "timestamp")
        self.chat_display.insert(tk.END, f"  {text}\n\n", "bot_msg")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    # ── System prompt ──────────────────────────────────────────────────────
    def load_system_prompt(self):
        file_path = filedialog.askopenfilename(
            title="Select System Prompt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    prompt_text = f.read()
                self.generate_content_config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    tools=self.tools,
                    system_instruction=[types.Part.from_text(text=prompt_text)],
                )
                self.messages = []
                self._clear_display()
                filename = os.path.basename(file_path)
                self.prompt_label.config(text=f"System: {filename}", fg="#A6E3A1")
                self._append_system(f"System prompt loaded: {filename}")
                messagebox.showinfo("Success", "System prompt loaded. Conversation reset.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def load_document(self):
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[("All Supported", "*.txt *.pdf *.html *.htm *.docx"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                extracted_text = doc_process.extract_text_from_document(file_path)
                if extracted_text.startswith("Error") or extracted_text.startswith("Unsupported"):
                    messagebox.showerror("Error", extracted_text)
                    return
                self.generate_content_config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    tools=self.tools,
                    system_instruction=[types.Part.from_text(text=f"Use the following document to answer user questions:\n\n{extracted_text}")],
                )
                self.messages = []
                self._clear_display()
                self.prompt_label.config(text=f"Doc: {os.path.basename(file_path)}", fg="#89B4FA")
                self._append_system(f"Document loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process document: {e}")

    # ── Chat history ───────────────────────────────────────────────────────
    def save_chat_history(self):
        if not self.messages:
            messagebox.showinfo("Info", "No messages to save.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Save Chat History",
            initialfile=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({"messages": self.messages, "saved_at": datetime.now().isoformat()}, f, indent=2)
                messagebox.showinfo("Saved", f"Chat saved!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

    def load_chat_history(self):
        file_path = filedialog.askopenfilename(
            title="Load Chat History",
            filetypes=[("JSON Files", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.messages = data.get("messages", [])
                self._clear_display()
                self._append_system(f"Loaded history: {os.path.basename(file_path)}")
                for msg in self.messages:
                    if msg.startswith("User: "):
                        self._insert_user_bubble(msg[6:], "(restored)")
                    elif msg.startswith("Bot: "):
                        self._insert_bot_bubble(msg[5:], "(restored)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {e}")

    def export_txt(self):
        if not self.messages:
            messagebox.showinfo("Info", "No messages to export.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Export Chat",
            initialfile=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Gemini Chatbot Export — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    for msg in self.messages:
                        f.write(msg + "\n\n")
                messagebox.showinfo("Exported", "Chat exported!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")

    # ── Clear ──────────────────────────────────────────────────────────────
    def clear_chat(self):
        if messagebox.askyesno("Clear Chat", "Clear all messages?"):
            self.messages = []
            self.message_count = 0
            self._clear_display()
            self.prompt_label.config(text="System: Default")
            self._update_status("Cleared")

    # ── Send message ───────────────────────────────────────────────────────
    def send_message(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return
        if len(user_text) > 500:
            messagebox.showwarning("Too long", "Message exceeds 500 characters.")
            return

        self.tts.stop()
        self.entry.delete(0, tk.END)
        self.char_count_label.config(text="0 / 500")
        self.message_count += 1

        self._insert_user_bubble(user_text)
        self.messages.append(f"User: {user_text}")
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]

        self._update_status("Thinking...")
        self.send_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.fetch_bot_response, args=(user_text,), daemon=True).start()

    # ── Bot response ───────────────────────────────────────────────────────
    def fetch_bot_response(self, user_text):
        contents = []
        for msg in self.messages:
            if msg.startswith("User: "):
                contents.append(types.Content(role="user",  parts=[types.Part.from_text(text=msg[6:])]))
            elif msg.startswith("Bot: "):
                contents.append(types.Content(role="model", parts=[types.Part.from_text(text=msg[5:])]))

        bot_reply = ""
        self.bot_started = False
        self.bot_ts = self._timestamp()

        try:
            self.root.after(0, self._show_thinking)

            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=self.generate_content_config,
            ):
                if text := chunk.text:
                    bot_reply += text
                    self.root.after(0, self._stream_bot_text, text)

            self.root.after(0, self._finish_bot_response, bot_reply)

            self.messages.append(f"Bot: {bot_reply}")
            self.tts.play_audio(bot_reply)
            if len(self.messages) > 10:
                self.messages = self.messages[-10:]

        except Exception as e:
            self.root.after(0, self._append_system, f"Error: {e}")
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))

    def _show_thinking(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{AVATAR_BOT}  Gemini", "bot_name")
        self.chat_display.insert(tk.END, f"   {self.bot_ts}\n", "timestamp")
        self.chat_display.insert(tk.END, "  ● thinking...\n", "thinking")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def _stream_bot_text(self, text):
        self.chat_display.config(state=tk.NORMAL)
        if not self.bot_started:
            self.chat_display.delete("end-2l linestart", "end-1l")
            self.chat_display.insert(tk.END, "  ", "bot_msg")
            self.bot_started = True
        self.chat_display.insert(tk.END, text, "bot_msg")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def _finish_bot_response(self, full_reply):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "\n\n", "bot_msg")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        self.message_count += 1
        self._update_status("Ready")
        self.send_btn.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatUI(root)
    root.mainloop()