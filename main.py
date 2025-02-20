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

            # Create the "relations" table if it doesn't exist
            create_relations_table_query = '''
            CREATE TABLE IF NOT EXISTS relations (
                id_relation INTEGER PRIMARY KEY AUTOINCREMENT,
                id_husband INTEGER NOT NULL,
                id_wife INTEGER NOT NULL,
                FOREIGN KEY (id_husband) REFERENCES person(id),
                FOREIGN KEY (id_wife) REFERENCES person(id)
            );
            '''
            conn.execute(create_relations_table_query)
            print("Table 'relations' created.")

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

            # SQL query to get the first 10 records from the relations table
            cursor.execute("SELECT id_relation, id_husband, id_wife FROM relations LIMIT 10")
            relation_records = cursor.fetchall()

            # Display the first 10 records from the relations table in the terminal
            if relation_records:
                print("\nFirst 10 records from 'relations' table:")
                for record in relation_records:
                    print(record)
            else:
                print("No records in the 'relations' table.")

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
                print(f"Saved person: {surname} {given}, Gender: {gender}")

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
    # Function to open a window for selecting husband and wife
    if db_path is None:
        print("Database has not been opened or created.")
        return

    def save_relation():
        husband_id = husband_listbox.curselection()
        wife_id = wife_listbox.curselection()

        if husband_id and wife_id:
            husband_id = husband_listbox.get(husband_id)
            wife_id = wife_listbox.get(wife_id)

            # Save the relation to the database
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Insert the relation into the "relations" table
                cursor.execute("INSERT INTO relations (id_husband, id_wife) VALUES (?, ?)", (husband_id, wife_id))
                conn.commit()
                print(f"Relation saved: Husband - {husband_id}, Wife - {wife_id}")

                conn.close()  # Close the connection
                relation_window.destroy()  # Close the window after saving the relation
            except sqlite3.Error as e:
                print(f"Failed to save relation: {e}")
        else:
            print("Select both husband and wife.")

    # Create a new window for relations
    relation_window = tk.Toplevel(window)
    relation_window.title("Add Relation")
    relation_window.geometry("600x300")

    # Load list of males (husband) and females (wife)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, surname, given FROM person WHERE gender='male'")
    husbands = cursor.fetchall()
    cursor.execute("SELECT id, surname, given FROM person WHERE gender='female'")
    wives = cursor.fetchall()

    conn.close()

    # Listbox for males (left column)
    husband_label = tk.Label(relation_window, text="Select Husband:")
    husband_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
    husband_listbox = tk.Listbox(relation_window, height=10, width=30)
    for husband in husbands:
        husband_listbox.insert(tk.END, f"{husband[1]} {husband[2]}")  # Display surname and given name
    husband_listbox.grid(row=1, column=0, padx=10, pady=10)

    # Button to confirm husband selection
    def select_husband():
        selected_husband = husband_listbox.curselection()
        if selected_husband:
            husband_name = husband_listbox.get(selected_husband)
            husband_label_selected.config(text=f"Selected Husband: {husband_name}")
        else:
            husband_label_selected.config(text="No husband selected")

    husband_button = tk.Button(relation_window, text="Confirm Husband", command=select_husband)
    husband_button.grid(row=2, column=0, padx=10, pady=10)

    # Label to display the selected husband
    husband_label_selected = tk.Label(relation_window, text="Selected Husband: None")
    husband_label_selected.grid(row=3, column=0, padx=10, pady=10)

    # Listbox for females (right column)
    wife_label = tk.Label(relation_window, text="Select Wife:")
    wife_label.grid(row=0, column=1, padx=10, pady=10, sticky='w')
    wife_listbox = tk.Listbox(relation_window, height=10, width=30)
    for wife in wives:
        wife_listbox.insert(tk.END, f"{wife[1]} {wife[2]}")  # Display surname and given name
    wife_listbox.grid(row=1, column=1, padx=10, pady=10)

    # Button to confirm wife selection
    def select_wife():
        selected_wife = wife_listbox.curselection()
        if selected_wife:
            wife_name = wife_listbox.get(selected_wife)
            wife_label_selected.config(text=f"Selected Wife: {wife_name}")
        else:
            wife_label_selected.config(text="No wife selected")

    wife_button = tk.Button(relation_window, text="Confirm Wife", command=select_wife)
    wife_button.grid(row=2, column=1, padx=10, pady=10)

    # Label to display the selected wife
    wife_label_selected = tk.Label(relation_window, text="Selected Wife: None")
    wife_label_selected.grid(row=3, column=1, padx=10, pady=10)

    # Button to save the relation
    save_button = tk.Button(relation_window, text="Save Relation", command=save_relation)
    save_button.grid(row=4, column=0, columnspan=2, padx=10, pady=20)


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
