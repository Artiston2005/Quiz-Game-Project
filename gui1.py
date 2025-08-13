import tkinter as tk
from tkinter import messagebox, ttk
import requests
import random
import html

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Quiz Game")
        self.root.geometry("600x450")
        self.root.configure(bg="#f0f4f8")

        self.timer_seconds = 15
        self.timer_id = None
        self.q_index = 0
        self.score = 0
        self.questions = []

        self.q_count_var = tk.StringVar(value="5")
        self.diff_var = tk.StringVar()
        self.cat_var = tk.StringVar()
        self.timer_input_var = tk.StringVar(value="15")

        self.build_start_screen()

    def build_start_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        title = tk.Label(self.root, text="Quiz Game by Ashwin Yadav", font=("Helvetica", 22, "bold"), bg="#f0f4f8", fg="#1a237e")
        title.pack(pady=20)

        def field(label_text, var, values=None):
            tk.Label(self.root, text=label_text, bg="#f0f4f8", fg="#333", font=("Arial", 12)).pack()
            if values:
                ttk.Combobox(self.root, textvariable=var, values=values, state="readonly", width=25).pack(pady=5)
            else:
                tk.Entry(self.root, textvariable=var, font=("Arial", 12)).pack(pady=5)

        field("Number of Questions:", self.q_count_var)
        field("Difficulty:", self.diff_var, ["easy", "medium", "hard"])
        field("Category:", self.cat_var, ["9: General Knowledge", "18: Computers", "23: History", "21: Sports"])
        field("Time per Question (in seconds):", self.timer_input_var)

        start_btn = tk.Button(self.root, text="Start Quiz", command=self.start_quiz,
                              bg="#1976d2", fg="white", font=("Arial", 13, "bold"),
                              activebackground="#1565c0", padx=10, pady=5)
        start_btn.pack(pady=25)

        start_btn.bind("<Enter>", lambda e: start_btn.config(bg="#1565c0"))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg="#1976d2"))

    def start_quiz(self):
        try:
            amount = int(self.q_count_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid number of questions.")
            return

        try:
            timer_value = int(self.timer_input_var.get())
            if timer_value <= 0:
                raise ValueError
            self.timer_seconds = timer_value
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid timer value.")
            return

        difficulty = self.diff_var.get()
        category = self.cat_var.get().split(":")[0] if self.cat_var.get() else None

        self.questions = self.fetch_questions(amount, difficulty, category)
        if not self.questions:
            messagebox.showerror("Error", "Could not fetch questions. Try again later.")
            return

        self.q_index = 0
        self.score = 0
        self.show_question_screen()

    def fetch_questions(self, amount, difficulty, category):
        url = f"https://opentdb.com/api.php?amount={amount}&type=multiple"
        if difficulty:
            url += f"&difficulty={difficulty}"
        if category:
            url += f"&category={category}"

        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data["response_code"] != 0:
                return None

            questions = []
            for item in data["results"]:
                q = {
                    "question": html.unescape(item["question"]),
                    "correct": item["correct_answer"],
                    "options": item["incorrect_answers"] + [item["correct_answer"]]
                }
                random.shuffle(q["options"])
                questions.append(q)
            return questions
        except:
            return None

    def show_question_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.question_label = tk.Label(self.root, text="", wraplength=500, font=("Arial", 14), bg="#f0f4f8", fg="#1b1b1b")
        self.question_label.pack(pady=20)

        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(self.root, text="", width=60,
                            font=("Arial", 11), bg="#eeeeee", activebackground="#cccccc",
                            command=lambda idx=i: self.check_answer(idx))
            btn.pack(pady=5)
            self.option_buttons.append(btn)

        self.timer_label = tk.Label(self.root, text="", font=("Arial", 12, "italic"), bg="#f0f4f8", fg="#d32f2f")
        self.timer_label.pack(pady=10)

        self.load_question()

    def load_question(self):
        if self.q_index >= len(self.questions):
            self.show_result()
            return

        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        self.time_left = self.timer_seconds
        self.timer_label.config(text=f"Time left: {self.time_left}s")

        q = self.questions[self.q_index]
        self.question_label.config(text=f"Q{self.q_index + 1}: {q['question']}")

        for i in range(4):
            self.option_buttons[i].config(
                text=q["options"][i],
                state="normal"
            )

        self.update_timer()

    def update_timer(self):
        self.timer_label.config(text=f"Time left: {self.time_left}s")
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.disable_options()
            messagebox.showinfo("Time's up!", "You ran out of time!")
            self.q_index += 1
            self.load_question()

    def disable_options(self):
        for btn in self.option_buttons:
            btn.config(state="disabled")

    def check_answer(self, index):
        selected = self.option_buttons[index].cget("text")
        correct = self.questions[self.q_index]["correct"]
        if selected == correct:
            self.score += 1

        self.q_index += 1
        self.load_question()

    def show_result(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="🎉 Quiz Completed!", font=("Arial", 18, "bold"), bg="#f0f4f8", fg="#388e3c").pack(pady=20)
        tk.Label(self.root, text=f"Your Score: {self.score}/{len(self.questions)}",
                 font=("Arial", 14), bg="#f0f4f8", fg="#333").pack(pady=10)

        try:
            with open("scores.txt", "a", encoding="utf-8") as f:
                f.write(f"Score: {self.score}/{len(self.questions)}\n")
        except:
            pass

        tk.Button(self.root, text="Play Again", command=self.build_start_screen,
                  font=("Arial", 12), bg="#1976d2", fg="white", activebackground="#1565c0").pack(pady=10)
        tk.Button(self.root, text="Exit", command=self.root.quit,
                  font=("Arial", 12), bg="#d32f2f", fg="white", activebackground="#b71c1c").pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    QuizApp(root)
    root.mainloop()
