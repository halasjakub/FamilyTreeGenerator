import tkinter as tk
from tkinter import Menu
from tkinter import simpledialog
from tkinter import filedialog
import sqlite3
import os


def open_new_window():
    global db_path  # Using a global variable to store the database path

    # Open a new window to ask for the database name
    db_name = simpledialog.askstring("Database Name", "Enter the name of the new database:")
    if db_name:
        print(f"New database name: {db_name}")

        # Path to the directory where the script is running
        db_path = os.path.join(os.getcwd(), f"{db_name}.db")

        # Create the SQLite3 database
        try:
            conn = sqlite3.connect(db_path)
            print(f"Database {db_name} created at: {db_path}")

            # Create the "person" table if it doesn't exist
            create_person_table_query = '''
                CREATE TABLE IF NOT EXISTS person (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    surname TEXT NOT NULL,
                    given TEXT NOT NULL,
                    gender TEXT CHECK(gender IN ('male', 'female')) NOT NULL
                );
            '''
            conn.execute(create_person_table_query)
            print("Table 'person' created.")

            # Create the "marriage" table if it doesn't exist
            create_marriage_table_query = '''
                CREATE TABLE IF NOT EXISTS marriage (
                    id_relation INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_husband INTEGER NOT NULL,
                    id_wife INTEGER NOT NULL,
                    FOREIGN KEY (id_husband) REFERENCES person(id),
                    FOREIGN KEY (id_wife) REFERENCES person(id)
                );
            '''
            conn.execute(create_marriage_table_query)
            print("Table 'marriage' created.")

            conn.close()  # Close the connection
        except sqlite3.Error as e:
            print(f"Failed to create database: {e}")


def open_existing_file():
    global db_path  # Using a global variable to store the database path

    # Open a file dialog to select an existing database file
    file_path = filedialog.askopenfilename(
        title="Select an existing database",
        filetypes=[("SQLite Database", "*.db")]
    )
    if file_path:
        db_path = file_path  # Assign the path to the global variable
        print(f"Selected file: {db_path}")

        # Open the existing database and fetch the first 10 records
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # SQL query to get the first 10 records from the person table
            cursor.execute("SELECT id, surname, given, gender FROM person LIMIT 10")
            person_records = cursor.fetchall()

            # Display the first 10 records from the person table in the terminal
            if person_records:
                print("\nFirst 10 records from 'person' table:")
                for record in person_records:
                    print(record)
            else:
                print("No records in the 'person' table.")

            # SQL query to get the first 10 records from the marriage table
            cursor.execute("SELECT id_relation, id_husband, id_wife FROM marriage LIMIT 10")
            relation_records = cursor.fetchall()

            # Display the first 10 records from the marriage table in the terminal
            if relation_records:
                print("\nFirst 10 records from 'marriage' table:")
                for record in relation_records:
                    print(record)
            else:
                print("No records in the 'marriage' table.")

            conn.close()  # Close the connection
        except sqlite3.Error as e:
            print(f"Failed to open database: {e}")


def open_person_window():
    # Function to open a window for entering person data
    if db_path is None:
        print("Database has not been opened or created.")
        return

    def save_person():
        surname = surname_entry.get()
        given = given_entry.get()
        gender = gender_var.get()

        if surname and given and gender:
            try:
                # Save the data to the database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute("INSERT INTO person (surname, given, gender) VALUES (?, ?, ?)",
                               (surname, given, gender))
                conn.commit()

                # Fetch the ID of the last inserted person
                person_id = cursor.lastrowid
                print(f"Saved person: {surname} {given}, Gender: {gender}, ID: {person_id}")

                conn.close()  # Close the connection
            except sqlite3.Error as e:
                print(f"Failed to save person: {e}")
            # Close the window after saving
            person_window.destroy()
        else:
            print("All fields must be filled.")

    # Create a new window for person data
    person_window = tk.Toplevel(window)
    person_window.title("Add Person")
    person_window.geometry("300x200")

    # Labels and entry fields for surname, given name, and gender
    surname_label = tk.Label(person_window, text="Surname:")
    surname_label.pack()
    surname_entry = tk.Entry(person_window)
    surname_entry.pack()

    given_label = tk.Label(person_window, text="Given Name:")
    given_label.pack()
    given_entry = tk.Entry(person_window)
    given_entry.pack()

    gender_label = tk.Label(person_window, text="Gender:")
    gender_label.pack()

    gender_var = tk.StringVar()
    gender_var.set("male")  # Set gender to male by default

    male_rb = tk.Radiobutton(person_window, text="Male", variable=gender_var, value="male")
    male_rb.pack()
    female_rb = tk.Radiobutton(person_window, text="Female", variable=gender_var, value="female")
    female_rb.pack()

    # Button to save the data
    save_button = tk.Button(person_window, text="Save Person", command=save_person)
    save_button.pack()


def open_relation_window():
    if db_path is None:
        print("Database has not been opened or created.")
        return

    relation_window = tk.Toplevel(window)
    relation_window.title("Add Relation")
    relation_window.geometry("400x300")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, surname, given FROM person WHERE gender = 'male'")
        male_records = cursor.fetchall()

        cursor.execute("SELECT id, surname, given FROM person WHERE gender = 'female'")
        female_records = cursor.fetchall()

        if male_records:
            male_listbox = tk.Listbox(relation_window)
            male_listbox.pack(side=tk.LEFT, padx=20, pady=20)

            for record in male_records:
                male_listbox.insert(tk.END, f"{record[0]}: {record[1]} {record[2]}")

        else:
            print("No male records in the 'person' table.")

        if female_records:
            female_listbox = tk.Listbox(relation_window)
            female_listbox.pack(side=tk.LEFT, padx=20, pady=20)

            for record in female_records:
                female_listbox.insert(tk.END, f"{record[0]}: {record[1]} {record[2]}")

        else:
            print("No female records in the 'person' table.")

        male_id = None
        female_id = None

        def on_male_selected(event):
            nonlocal male_id
            selected_male_indices = male_listbox.curselection()
            if selected_male_indices:
                selected_male = male_listbox.get(selected_male_indices)
                male_id = selected_male.split(":")[0]
                print(f"Selected Male ID: {male_id}")

        def on_female_selected(event):
            nonlocal female_id
            selected_female_indices = female_listbox.curselection()
            if selected_female_indices:
                selected_female = female_listbox.get(selected_female_indices)
                female_id = selected_female.split(":")[0]
                print(f"Selected Female ID: {female_id}")

        male_listbox.bind('<<ListboxSelect>>', on_male_selected)
        female_listbox.bind('<<ListboxSelect>>', on_female_selected)

        def save_relation():
            nonlocal male_id, female_id

            if male_id and female_id:
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()

                    cursor.execute(
                        "INSERT INTO marriage (id_husband, id_wife) VALUES (?, ?)",
                        (male_id, female_id)
                    )
                    conn.commit()
                    print(f"Relation saved between Male ID: {male_id} and Female ID: {female_id}")
                    conn.close()

                except sqlite3.Error as e:
                    print(f"Failed to save relation: {e}")
            else:
                print("Please select both a male and a female.")

        save_button = tk.Button(relation_window, text="Save Relation", command=save_relation)
        save_button.pack(pady=10)

        conn.close()

    except sqlite3.Error as e:
        print(f"Failed to retrieve data: {e}")


window = tk.Tk()
window.title("Family Tree Generator")
window.geometry("800x600")

# Path to the database (initially None, will change after creating or opening the database)
db_path = None

# Set up the main window
menu_bar = Menu(window)
window.config(menu=menu_bar)

# File options
file_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=open_new_window)  # Function activated by the New button
file_menu.add_command(label="Open", command=open_existing_file)  # Function activated by the Open button
file_menu.add_command(label="Close")

# Add options
add_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Add", menu=add_menu)
add_menu.add_command(label="Person", command=open_person_window)  # Function to open the add person window
add_menu.add_command(label="Relation", command=open_relation_window)  # Function to open the add relation window

window.mainloop()
