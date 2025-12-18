import tkinter as tk
from tkinter import messagebox
import sqlite3
import random
from PIL import Image, ImageTk  # Required for JPG support

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secondary Education Assessment")
        self.root.geometry("450x750") # Height to accommodate the image

        # Color Palette
        self.bg_blue = "#1e3d59"
        self.btn_green = "#2ecc71"
        self.btn_orange = "#ff9933"
        self.text_white = "#ffffff"

        self.root.configure(bg=self.bg_blue)

        # Core variables
        self.last_name = ""
        self.questions = []
        self.current_q_index = 0
        self.quiz_image = None # Keep a reference to prevent garbage collection

        self.scores = {
            "Mathematics": 0, "EnglishLiterature": 0, "EnglishLanguage": 0,
            "Biology": 0, "Chemistry": 0, "Physics": 0,
            "History": 0, "Geography": 0, "ComputerScience": 0, "Art": 0
        }

        try:
            self.conn = sqlite3.connect("prototype.db")
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not find or open database: {e}")

        self.show_login()

    def show_login(self):
        self.clear_screen()
        tk.Label(self.root, text="Student Login", font=("Arial", 20, "bold"),
                 bg=self.bg_blue, fg=self.btn_orange).pack(pady=40)
        tk.Label(self.root, text="Enter Last Name:", font=("Arial", 12),
                 bg=self.bg_blue, fg=self.text_white).pack(pady=5)
        self.name_entry = tk.Entry(self.root, font=("Arial", 12), bd=0)
        self.name_entry.pack(pady=10, ipady=5)
        tk.Button(self.root, text="Start Assessment", font=("Arial", 12, "bold"),
                  bg=self.btn_green, fg="white", activebackground=self.btn_orange,
                  cursor="hand2", padx=20, pady=10, command=self.handle_login).pack(pady=30)

    def handle_login(self):
        self.last_name = self.name_entry.get().strip()
        if not self.last_name:
            messagebox.showwarning("Input Error", "Please enter your last name.")
            return
        try:
            self.cursor.execute("SELECT SUBJECT, QUESTION, Answer, WrongAnswer, BOOL FROM QUESTIONS")
            self.questions = self.cursor.fetchall()
            random.shuffle(self.questions)
            self.start_quiz()
        except sqlite3.Error as e:
            messagebox.showerror("Query Error", f"Database error: {e}")

    def start_quiz(self):
        self.clear_screen()
        if self.current_q_index < len(self.questions):
            subject, q_text, correct, incorrect, is_bool = self.questions[self.current_q_index]

            # 1. Subject Header
            tk.Label(self.root, text=f"Subject: {subject}", font=("Arial", 10, "italic"),
                     bg=self.bg_blue, fg=self.btn_green).pack(pady=10)

            # 2. Question Text
            tk.Label(self.root, text=q_text, wraplength=380, font=("Arial", 14),
                     bg=self.bg_blue, fg=self.text_white).pack(pady=15)

            if is_bool:
                options = ["True", "False"]
            else:
                options = [correct, incorrect]
            random.shuffle(options)

            # 3. Answer Buttons (Orange)
            for opt in options:
                tk.Button(self.root, text=opt, font=("Arial", 11, "bold"), width=25,
                          bg=self.btn_orange, fg="white", activebackground=self.btn_green,
                          cursor="hand2", pady=8,
                          command=lambda o=opt: self.process_answer(o, correct, subject)).pack(pady=10)

            # 4. IMAGE ADDITION (Moved below options)
            try:
                img = Image.open("AAR.jpg")
                img = img.resize((250, 150), Image.Resampling.LANCZOS)
                self.quiz_image = ImageTk.PhotoImage(img)
                img_label = tk.Label(self.root, image=self.quiz_image, bg=self.bg_blue)
                img_label.pack(pady=20) # Added a bit more padding for separation
            except Exception as e:
                print(f"Image load error: {e}")
        else:
            self.save_final_scores()

    def process_answer(self, selected, correct, subject):
        if selected == correct:
            self.scores[subject] += 10
        else:
            self.scores[subject] -= 10
        self.current_q_index += 1
        self.start_quiz()

    def save_final_scores(self):
        try:
            columns = ['LastName'] + list(self.scores.keys())
            values = [self.last_name] + list(self.scores.values())
            placeholders = ', '.join(['?'] * len(columns))
            column_names = ', '.join(columns)
            query = f"INSERT INTO StudentGrades ({column_names}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.conn.commit()
            self.show_results()
        except sqlite3.Error as e:
            messagebox.showerror("Save Error", f"Could not save to 'Results': {e}")

    def show_results(self):
        self.clear_screen()
        tk.Label(self.root, text=f"Results: {self.last_name}", font=("Arial", 18, "bold"),
                 bg=self.bg_blue, fg=self.btn_orange).pack(pady=20)

        score_frame = tk.Frame(self.root, bg=self.bg_blue)
        score_frame.pack()

        for sub, score in self.scores.items():
            # Logic to determine text color based on score
            if score < 0:
                text_color = "#ff4d4d"  # Red
            elif score > 0:
                text_color = "#2ecc71"  # Green
            else:
                text_color = "#ffffff"  # White

            tk.Label(score_frame, text=f"{sub}: {score}", font=("Arial", 10, "bold"),
                     bg=self.bg_blue, fg=text_color).pack(anchor="w", pady=2)

        tk.Button(self.root, text="Finish", font=("Arial", 12, "bold"),
                  bg=self.btn_green, fg="white", width=15,
                  command=self.root.quit).pack(pady=30)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()