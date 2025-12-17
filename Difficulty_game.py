import random
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter.ttk import Progressbar, Style

from datasets import load_dataset
from transformers import pipeline
import textstat

# Load dataset and model
dataset = load_dataset("squad")
simplifier = pipeline(
    "text2text-generation",
    model="t5-base",
    framework="pt"
)

# ---------------- Utility Functions ---------------- #

def analyze_readability(text):
    fk_grade = textstat.flesch_kincaid_grade(text)
    if fk_grade < 5.0:
        level = "Very easy (elementary)"
    elif 5.0 <= fk_grade < 8.0:
        level = "Moderate (middle school)"
    else:
        level = "Difficult (high school/college)"
    return fk_grade, level


def replace_pronouns(text, answer):
    pronouns = ["it", "they", "them", "its"]
    pattern = re.compile(r'\b(' + '|'.join(pronouns) + r')\b', re.IGNORECASE)
    return pattern.sub(answer, text)


def simplify_text_keep_answer(text, answer):
    """
    Simplifies each sentence individually while preserving
    sentences containing the answer.
    """
    sentences = text.split(". ")
    final_sentences = []

    for s in sentences:
        if answer.lower() in s.lower():
            final_sentences.append(s)
        else:
            simplified = simplifier(
                "simplify: " + s,
                max_length=100,
                do_sample=False
            )
            simplified_text = simplified[0]['generated_text']
            simplified_text = replace_pronouns(simplified_text, answer)
            final_sentences.append(simplified_text)

    return ". ".join(final_sentences).strip()

# ---------------- Main Game Class ---------------- #

class LanguageGame:
    def __init__(self, root, num_rounds=3):
        self.root = root
        self.root.title("🎮 Dynamic Language Game")
        self.root.configure(bg="#f0f8ff")

        # Window centering
        window_width, window_height = 900, 650
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.num_rounds = num_rounds
        self.current_round = 0

        self.indices = random.sample(
            range(len(dataset['train'])),
            num_rounds
        )
        self.passages = [dataset['train'][i] for i in self.indices]

        self.create_widgets()
        self.load_next_passage()

    def create_widgets(self):
        self.title_label = tk.Label(
            self.root,
            text="🎯 Dynamic Language Difficulty Game",
            font=("Comic Sans MS", 22, "bold"),
            fg="#2f4f4f",
            bg="#f0f8ff"
        )
        self.title_label.pack(pady=10)

        self.round_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 14, "bold"),
            bg="#f0f8ff",
            fg="#4b0082"
        )
        self.round_label.pack(pady=5)

        self.passage_text = scrolledtext.ScrolledText(
            self.root,
            width=100,
            height=12,
            wrap=tk.WORD,
            font=("Arial", 12),
            bg="#fffafa",
            fg="#00008b"
        )
        self.passage_text.pack(padx=20, pady=10)
        self.passage_text.config(state=tk.DISABLED)

        self.readability_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 12, "italic"),
            bg="#f0f8ff",
            fg="#ff4500"
        )
        self.readability_label.pack(pady=5)

        self.question_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 14, "bold"),
            bg="#f0f8ff",
            fg="#006400"
        )
        self.question_label.pack(pady=5)

        self.answer_entry = tk.Entry(
            self.root,
            width=60,
            font=("Arial", 12)
        )
        self.answer_entry.pack(pady=5)

        self.submit_btn = tk.Button(
            self.root,
            text="Submit Answer",
            font=("Arial", 12, "bold"),
            bg="#20b2aa",
            fg="#ffffff",
            activebackground="#008080",
            command=self.check_answer
        )
        self.submit_btn.pack(pady=10)

        style = Style()
        style.theme_use('clam')
        style.configure(
            "TProgressbar",
            thickness=20,
            troughcolor='#d3d3d3',
            background='#32cd32'
        )

        self.progress = Progressbar(
            self.root,
            length=700,
            mode='determinate',
            style="TProgressbar"
        )
        self.progress.pack(pady=10)

    def load_next_passage(self, simplified=False):
        if self.current_round >= self.num_rounds:
            messagebox.showinfo(
                "Game Over",
                "🎉 Game Over! Thanks for playing."
            )
            self.root.destroy()
            return

        self.current_data = self.passages[self.current_round]
        self.passage = self.current_data['context']
        self.question = self.current_data['question']
        self.answer = self.current_data['answers']['text'][0]

        if simplified:
            self.passage = simplify_text_keep_answer(
                self.passage,
                self.answer
            )

        fk_grade, level = analyze_readability(self.passage)

        self.round_label.config(
            text=f"Round {self.current_round + 1} of {self.num_rounds}"
        )
        self.progress['value'] = (
            self.current_round / self.num_rounds
        ) * 100

        self.passage_text.config(state=tk.NORMAL)
        self.passage_text.delete(1.0, tk.END)
        self.passage_text.insert(tk.END, self.passage)
        self.passage_text.config(state=tk.DISABLED)

        self.readability_label.config(
            text=f"Readability Grade: {fk_grade:.2f} ({level})"
        )
        self.question_label.config(
            text=f"❓ {self.question}"
        )
        self.answer_entry.delete(0, tk.END)

    def check_answer(self):
        user_ans = self.answer_entry.get().strip().lower()

        if self.answer.lower() in user_ans:
            messagebox.showinfo(
                "Correct",
                "✅ Correct! Moving to next passage..."
            )
            self.current_round += 1
            self.load_next_passage()
        else:
            simplified_passage = simplify_text_keep_answer(
                self.current_data['context'],
                self.answer
            )
            fk_grade, level = analyze_readability(simplified_passage)
            messagebox.showwarning(
                "Incorrect",
                f"❌ Incorrect.\nTrying simplified passage!\n"
                f"New Readability: {fk_grade:.2f} ({level})"
            )
            self.load_next_passage(simplified=True)

# ---------------- Run App ---------------- #

if __name__ == "__main__":
    root = tk.Tk()
    game = LanguageGame(root, num_rounds=3)
    root.mainloop()
