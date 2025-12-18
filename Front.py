import tkinter as tk
from tkinter import messagebox
import sqlite3
import random
import pandas as pd
from sqlalchemy import create_engine
from PIL import Image, ImageTk


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secondary Education Assessment")
        self.root.geometry("450x750")

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
        self.quiz_image = None

        # DATABASE SETTINGS
        self.LOCAL_DB_PATH = 'prototype.db'
        # IMPORTANT: Replace [PASSWORD] and [REF] with your actual Supabase DB credentials
        #sb_secret_ggJTY5zeZ_thb_LdQsk3uw_2F61pC4B
        self.SUPABASE_URL = "postgresql://postgres.mpceskickykhyxkjrgfz:hulmehackthon@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"

        self.scores = {
            "Mathematics": 0, "EnglishLiterature": 0, "EnglishLanguage": 0,
            "Biology": 0, "Chemistry": 0, "Physics": 0,
            "History": 0, "Geography": 0, "ComputerScience": 0, "Art": 0
        }

        try:
            self.conn = sqlite3.connect(self.LOCAL_DB_PATH)
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

            tk.Label(self.root, text=f"Subject: {subject}", font=("Arial", 10, "italic"),
                     bg=self.bg_blue, fg=self.btn_green).pack(pady=10)

            tk.Label(self.root, text=q_text, wraplength=380, font=("Arial", 14),
                     bg=self.bg_blue, fg=self.text_white).pack(pady=15)

            options = ["True", "False"] if is_bool else [correct, incorrect]
            random.shuffle(options)

            for opt in options:
                tk.Button(self.root, text=opt, font=("Arial", 11, "bold"), width=25,
                          bg=self.btn_orange, fg="white", activebackground=self.btn_green,
                          cursor="hand2", pady=8,
                          command=lambda o=opt: self.process_answer(o, correct, subject)).pack(pady=10)

            try:
                img = Image.open("AAR.jpg")
                img = img.resize((250, 150), Image.Resampling.LANCZOS)
                self.quiz_image = ImageTk.PhotoImage(img)
                tk.Label(self.root, image=self.quiz_image, bg=self.bg_blue).pack(pady=20)
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
            user_id = self.cursor.lastrowid  # Correct way to get ID after execute
            self.conn.commit()
            self.show_results(user_id)
        except sqlite3.Error as e:
            messagebox.showerror("Save Error", f"Could not save scores: {e}")

    def push_local_to_supabase(self):
        """Migrates the local SQLite data to Supabase PostgreSQL."""
        try:
            remote_engine = create_engine(self.SUPABASE_URL)
            local_conn = sqlite3.connect(self.LOCAL_DB_PATH)

            # Get list of tables
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", local_conn)

            for table_name in tables['name']:
                if table_name.startswith('sqlite_'):
                    continue

                df = pd.read_sql_query(f"SELECT * FROM {table_name}", local_conn)
                # Syncing to Supabase
                df.to_sql(table_name, remote_engine, if_exists='replace', index=False)

            print("Successfully pushed to Supabase.")
            local_conn.close()
        except Exception as e:
            print(f"Supabase Sync Error: {e}")

    def show_results(self, user_id):
        self.clear_screen()

        tk.Label(self.root, text="Assessment Complete", font=("Arial", 14),
                 bg=self.bg_blue, fg=self.text_white).pack(pady=(20, 0))
        tk.Label(self.root, text=f"Student ID: {user_id}", font=("Arial", 12, "bold"),
                 bg=self.bg_blue, fg=self.btn_green).pack(pady=5)
        tk.Label(self.root, text=f"Results: {self.last_name}", font=("Arial", 18, "bold"),
                 bg=self.bg_blue, fg=self.btn_orange).pack(pady=10)

        score_frame = tk.Frame(self.root, bg=self.bg_blue)
        score_frame.pack()

        for sub, score in self.scores.items():
            text_color = "#ff4d4d" if score < 0 else ("#2ecc71" if score > 0 else "#ffffff")
            tk.Label(score_frame, text=f"{sub}: {score}", font=("Arial", 10, "bold"),
                     bg=self.bg_blue, fg=text_color).pack(anchor="w", pady=2)

        # TRIGGER SYNC
        self.push_local_to_supabase()

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