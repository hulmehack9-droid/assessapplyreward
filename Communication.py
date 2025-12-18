import sqlite3


def add_student_record(last_name, grades_dict):
    """
    Inputs data into prototype.db.
    :param last_name: String (The student's name)
    :param grades_dict: Dictionary (e.g., {"Mathematics": 90, "History": 85})
    """
    # 1. Connect to the database
    conn = sqlite3.connect('prototype.db')
    cursor = conn.cursor()

    # 2. Prepare the columns and values dynamically
    # This allows you to submit only the grades you have
    columns = ['LastName'] + list(grades_dict.keys())
    values = [last_name] + list(grades_dict.values())

    # Create placeholders (e.g., "?, ?, ?")
    placeholders = ', '.join(['?'] * len(columns))
    column_names = ', '.join(columns)

    query = f"INSERT INTO StudentGrades ({column_names}) VALUES ({placeholders})"

    try:
        # 3. Execute and COMMIT
        cursor.execute(query, values)
        conn.commit()
        print(f"Success: Record for {last_name} committed with ID {cursor.lastrowid}")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # 4. Always close the connection
        conn.close()


def insert_new_question(question_text, subject_name, answer,wrong, is_active=0):
    """
    Inserts a single new question into the QUESTIONS table.
    :param question_text: String (The question itself)
    :param subject_name: String (The category/subject)
    :param is_active: Integer (0 or 1 for the BOOL column)
    """
    conn = sqlite3.connect('prototype.db')
    cursor = conn.cursor()

    # We only specify the columns we are providing.
    # QID is skipped because it is AUTOINCREMENT.
    query = "INSERT INTO QUESTIONS (QUESTION, SUBJECT, ANSWER,WRONGANSWER, BOOL) VALUES (?, ?, ?, ?, ?)"
    values = (question_text, subject_name, answer,wrong,is_active)

    try:
        cursor.execute(query, values)
        conn.commit()
        print(f"Success: Added question with ID {cursor.lastrowid}")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# --- Example Usage ---
insert_new_question("What is the value of x in the equation 3x + 7 = 22","Mathematics",5, 4,0)
insert_new_question("In J.B. Priestley's An Inspector Calls, what does the Inspector represent?","EnglishLiterature", "Social Conscience", "Social Togetherness",0)
insert_new_question("What is the term for a figure of speech that combines two contradictory terms, such as bittersweet?","EnglishLanguage","Oxymoron","Metaphor",0)
insert_new_question("Which organelle is known as the powerhouse of the cell where aerobic respiration occurs?","Biology","Mitochondria","Ribosomes",0)
insert_new_question("On the pH scale, what number represents a neutral substance (like pure water)?","Chemistry",7,5,0)
insert_new_question("How many continents are there?", "Geography", 7, 6, 0)
insert_new_question("What is the standard formula for calculating Force?","Physics","F=mxa","F=m/a",0)
insert_new_question("The assassination of which Archduke in 1914 is considered the trigger for WWI?","History", "Franz Ferdinand","Willhem II",0)
insert_new_question("Which logic gate only outputs a $1$ (True) if both of its inputs are also $1$ (True)?","ComputerScience","AND gate","OR gate",0)
insert_new_question("Which 19th-century art movement, focused on light and brushstrokes, was led by Claude Monet?","Art","Impressionism","Imperialism",0)

#add_student_record("Johnson", student_data)