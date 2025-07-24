import tkinter as tk
from tkinter import messagebox
import requests
import random
import html

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Quiz Game")
        self.root.geometry("500x400")

        self.timer_seconds = 15
        self.timer_id = None
        self.q_index = 0
        self.score = 0
        self.questions = []

        self.q_count_var = tk.StringVar(value="5")
        self.diff_var = tk.StringVar(value="Any")
        self.cat_var = tk.StringVar(value="Any")
        self.timer_input_var = tk.StringVar(value="15")

        self.start_screen()

    def start_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Quiz Game", font=("Arial", 18, "bold")).pack(pady=15)

        tk.Label(self.root, text="Number of Questions:").pack()
        tk.Entry(self.root, textvariable=self.q_count_var).pack(pady=5)

        tk.Label(self.root, text="Difficulty (Any/easy/medium/hard):").pack()
        tk.Entry(self.root, textvariable=self.diff_var).pack(pady=5)

        tk.Label(self.root, text="Category (Any or ID like 9, 18, 21):").pack()
        tk.Entry(self.root, textvariable=self.cat_var).pack(pady=5)

        tk.Label(self.root, text="Time per Question (in seconds):").pack()
        tk.Entry(self.root, textvariable=self.timer_input_var).pack(pady=5)

        tk.Button(self.root, text="Start Quiz", command=self.start_quiz).pack(pady=20)

    def start_quiz(self):
        try:
            amount = int(self.q_count_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number of questions.")
            return

        try:
            timer_value = int(self.timer_input_var.get())
            if timer_value <= 0:
                raise ValueError
            self.timer_seconds = timer_value
        except ValueError:
            messagebox.showerror("Error", "Enter a valid timer value.")
            return

        difficulty = self.diff_var.get().lower()
        if difficulty == "any":
            difficulty = None

        category = self.cat_var.get()
        if category.lower() == "any" or not category:
            category = None

        self.questions = self.fetch_questions(amount, difficulty, category)
        if not self.questions:
            messagebox.showerror("Error", "Could not get questions. Try again.")
            return

        self.q_index = 0
        self.score = 0
        self.show_question()

    def fetch_questions(self, amount, difficulty, category):
        url = f"https://opentdb.com/api.php?amount={amount}&type=multiple"
        if difficulty:
            url += f"&difficulty={difficulty}"
        if category:
            url += f"&category={category}"

        try:
            res = requests.get(url)
            data = res.json()
            if data["response_code"] != 0:
                return None

            questions = []
            for item in data["results"]:
                question = html.unescape(item["question"])
                correct = item["correct_answer"]
                options = item["incorrect_answers"] + [correct]
                random.shuffle(options)
                questions.append({"question": question, "correct": correct, "options": options})
            return questions
        except:
            return None

    def show_question(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        if self.q_index >= len(self.questions):
            self.show_result()
            return

        self.time_left = self.timer_seconds

        self.q_label = tk.Label(self.root, text=f"Q{self.q_index+1}: {self.questions[self.q_index]['question']}", wraplength=400)
        self.q_label.pack(pady=10)

        self.option_buttons = []
        for i, opt in enumerate(self.questions[self.q_index]['options']):
            btn = tk.Button(self.root, text=opt, width=50, command=lambda i=i: self.check_answer(i))
            btn.pack(pady=5)
            self.option_buttons.append(btn)

        self.timer_label = tk.Label(self.root, text=f"Time left: {self.time_left}s")
        self.timer_label.pack(pady=10)

        self.update_timer()

    def update_timer(self):
        self.timer_label.config(text=f"Time left: {self.time_left}s")
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.disable_options()
            messagebox.showinfo("Time's Up!", "You ran out of time!")
            self.q_index += 1
            self.show_question()

    def disable_options(self):
        for btn in self.option_buttons:
            btn.config(state="disabled")

    def check_answer(self, index):
        selected = self.option_buttons[index].cget("text")
        correct = self.questions[self.q_index]["correct"]
        if selected == correct:
            self.score += 1
        self.q_index += 1
        self.show_question()

    def show_result(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Quiz Over!", font=("Arial", 16)).pack(pady=15)
        tk.Label(self.root, text=f"Score: {self.score} out of {len(self.questions)}").pack(pady=10)

        tk.Button(self.root, text="Play Again", command=self.start_screen).pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
