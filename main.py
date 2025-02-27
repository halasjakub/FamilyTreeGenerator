import tkinter as tk
from tkinter import Menu
from tkinter import simpledialog
from tkinter import filedialog
import sqlite3
import os
import networkx as nx
import matplotlib.pyplot as plt


def draw_family_tree():
    if db_path is None:
        print("Database has not been opened or created.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Retrieve data from the 'family' table (parents, children)
        cursor.execute("SELECT id_parent1, id_parent2, id_child FROM family")
        family_records = cursor.fetchall()

        if not family_records:
            print("No family records found.")
            return

        # Create a graph
        G = nx.DiGraph()

        # Create a dictionary to hold the generation level for each person
        generations = {}
        fathers = {}  # Dictionary to store fathers and their children
        mothers = {}  # Dictionary to store mothers and their children

        # Add initial nodes and generations based on the family records
        for record in family_records:
            parent1_id, parent2_id, child_id = record

            # Retrieve names of parents and the child
            cursor.execute("SELECT surname, given FROM person WHERE id = ?", (parent1_id,))
            parent1 = cursor.fetchone()
            cursor.execute("SELECT surname, given FROM person WHERE id = ?", (parent2_id,))
            parent2 = cursor.fetchone()
            cursor.execute("SELECT surname, given FROM person WHERE id = ?", (child_id,))
            child = cursor.fetchone()

            if parent1 and parent2 and child:
                parent1_name = f"{parent1[0]} {parent1[1]}"  # Father
                parent2_name = f"{parent2[0]} {parent2[1]}"  # Mother
                child_name = f"{child[0]} {child[1]}"

                # Add nodes to the graph
                G.add_node(parent1_name)
                G.add_node(parent2_name)
                G.add_node(child_name)

                # Add edges to represent the parent-child relationship
                G.add_edge(parent1_name, child_name)
                G.add_edge(parent2_name, child_name)

                # Set generations for the child and parents
                if child_name not in generations:
                    generations[child_name] = 0  # The child is at generation 0
                if parent1_name not in generations:
                    generations[parent1_name] = generations[child_name] - 1  # Parent is one generation older
                if parent2_name not in generations:
                    generations[parent2_name] = generations[child_name] - 1  # Parent is one generation older

                # Group fathers and mothers separately
                if parent1_name not in fathers:
                    fathers[parent1_name] = []
                fathers[parent1_name].append(child_name)

                if parent2_name not in mothers:
                    mothers[parent2_name] = []
                mothers[parent2_name].append(child_name)

        # Now, compute the layout
        pos = {}
        for person, generation in generations.items():
            if person in fathers:
                # Fathers are placed on the left side (negative x-axis)
                pos[person] = (-generation, generations.get(person, 0))
            elif person in mothers:
                # Mothers are placed on the right side (positive x-axis)
                pos[person] = (generation, generations.get(person, 0))
            else:
                # If the person is neither a father nor a mother, place them in the middle
                pos[person] = (0, generations.get(person, 0))  # (generation, horizontal position)

        # Draw the graph with adjusted layout
        plt.figure(figsize=(12, 10))
        nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", font_size=10, font_weight="bold", arrows=True)

        # Add title
        plt.title("Family Tree")

        # Show the plot
        plt.show()

        # Close the connection to the database
        conn.close()

    except sqlite3.Error as e:
        print(f"Error fetching data: {e}")


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
                    id_marriage INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_husband INTEGER NOT NULL,
                    id_wife INTEGER NOT NULL,
                    FOREIGN KEY (id_husband) REFERENCES person(id),
                    FOREIGN KEY (id_wife) REFERENCES person(id)
                );
            '''
            conn.execute(create_marriage_table_query)
            print("Table 'marriage' created.")

            # Create the "family" table if it doesn't exist
            create_family_table_query = '''
                CREATE TABLE IF NOT EXISTS family (
                    id_family INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_parent1 INTEGER NOT NULL,
                    id_parent2 INTEGER NOT NULL,
                    id_child INTEGER NOT NULL,
                    FOREIGN KEY (id_parent1) REFERENCES person(id),
                    FOREIGN KEY (id_parent2) REFERENCES person(id),
                    FOREIGN KEY (id_child) REFERENCES person(id)
                );
            '''
            conn.execute(create_family_table_query)
            print("Table 'family' created.")

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
            cursor.execute("SELECT id_marriage, id_husband, id_wife FROM marriage LIMIT 10")
            marriage_records = cursor.fetchall()

            # Display the first 10 records from the marriage table in the terminal
            if marriage_records:
                print("\nFirst 10 records from 'marriage' table:")
                for record in marriage_records:
                    print(record)
            else:
                print("No records in the 'marriage' table.")

            # SQL query to get the first 10 records from the family table
            cursor.execute("SELECT id_family, id_parent1, id_parent2, id_child FROM family LIMIT 10")
            family_records = cursor.fetchall()

            # Display the first 10 records from the family table in the terminal
            if family_records:
                print("\nFirst 10 records from 'family' table:")
                for record in family_records:
                    print(record)
            else:
                print("No records in the 'family' table.")

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


def open_marriage_window():
    if db_path is None:
        print("Database has not been opened or created.")
        return

    marriage_window = tk.Toplevel(window)
    marriage_window.title("Add Marriage")
    marriage_window.geometry("400x300")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, surname, given FROM person WHERE gender = 'male'")
        male_records = cursor.fetchall()

        cursor.execute("SELECT id, surname, given FROM person WHERE gender = 'female'")
        female_records = cursor.fetchall()

        if male_records:
            male_listbox = tk.Listbox(marriage_window)
            male_listbox.pack(side=tk.LEFT, padx=20, pady=20)

            for record in male_records:
                male_listbox.insert(tk.END, f"{record[0]}: {record[1]} {record[2]}")

        else:
            print("No male records in the 'person' table.")

        if female_records:
            female_listbox = tk.Listbox(marriage_window)
            female_listbox.pack(side=tk.LEFT, padx=20, pady=20)

            for record in female_records:
                female_listbox.insert(tk.END, f"{record[0]}: {record[1]} {record[2]}")

        else:
            print("No female records in the 'person' table.")

        male_id = None
        female_id = None

        male_label = tk.Label(marriage_window, text="Selected Male: None")
        male_label.pack(pady=10)

        female_label = tk.Label(marriage_window, text="Selected Female: None")
        female_label.pack(pady=10)

        def on_male_selected(event):
            nonlocal male_id
            selected_male_indices = male_listbox.curselection()
            if selected_male_indices:
                selected_male = male_listbox.get(selected_male_indices)
                male_id = selected_male.split(":")[0]
                male_name = selected_male.split(":")[1].strip()
                male_label.config(text=f"Selected Male: {male_name}")
                print(f"Selected Male ID: {male_id}")

        def on_female_selected(event):
            nonlocal female_id
            selected_female_indices = female_listbox.curselection()
            if selected_female_indices:
                selected_female = female_listbox.get(selected_female_indices)
                female_id = selected_female.split(":")[0]
                female_name = selected_female.split(":")[1].strip()
                female_label.config(text=f"Selected Female: {female_name}")
                print(f"Selected Female ID: {female_id}")

        male_listbox.bind('<<ListboxSelect>>', on_male_selected)
        female_listbox.bind('<<ListboxSelect>>', on_female_selected)

        def save_marriage():
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
                    print(f"Marriage saved between Male ID: {male_id} and Female ID: {female_id}")
                    conn.close()

                except sqlite3.Error as e:
                    print(f"Failed to save marriage: {e}")
            else:
                print("Please select both a male and a female.")

        save_button = tk.Button(marriage_window, text="Save Marriage", command=save_marriage)
        save_button.pack(pady=10)

        conn.close()

    except sqlite3.Error as e:
        print(f"Failed to retrieve data: {e}")


def open_child_window():
    if db_path is None:
        print("Database has not been opened or created.")
        return

    child_window = tk.Toplevel(window)
    child_window.title("Add Child")
    child_window.geometry("400x300")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id_marriage, id_husband, id_wife FROM marriage")
        marriage_records = cursor.fetchall()

        cursor.execute("SELECT id, surname, given FROM person")
        person_records = cursor.fetchall()

        # Listbox for marriages
        marriage_listbox = tk.Listbox(child_window)
        marriage_listbox.pack(side=tk.LEFT, padx=20, pady=20)
        for record in marriage_records:
            marriage_listbox.insert(tk.END, f"Marriage {record[0]}: Husband {record[1]}, Wife {record[2]}")

        # Listbox for persons (children)
        person_listbox = tk.Listbox(child_window)
        person_listbox.pack(side=tk.LEFT, padx=20, pady=20)
        for record in person_records:
            person_listbox.insert(tk.END, f"{record[0]}: {record[1]} {record[2]}")

        # Variables to hold selected records
        selected_marriage_id = None
        selected_person_id = None

        # Labels to show selected records
        marriage_label = tk.Label(child_window, text="Selected Marriage: None")
        marriage_label.pack(pady=10)

        person_label = tk.Label(child_window, text="Selected Person: None")
        person_label.pack(pady=10)

        # Event handler for marriage selection
        def on_select_marriage(event):
            nonlocal selected_marriage_id
            selected_indices = marriage_listbox.curselection()
            if selected_indices:
                selected_record = marriage_listbox.get(selected_indices)
                selected_marriage_id = selected_record.split(":")[0]
                marriage_label.config(text=f"Selected Marriage ID: {selected_marriage_id}")
                print(f"Selected Marriage ID: {selected_marriage_id}")

        # Event handler for person (child) selection
        def on_select_person(event):
            nonlocal selected_person_id
            selected_indices = person_listbox.curselection()
            if selected_indices:
                selected_record = person_listbox.get(selected_indices)
                selected_person_id = selected_record.split(":")[0]
                person_label.config(text=f"Selected Person ID: {selected_person_id}")
                print(f"Selected Person ID: {selected_person_id}")

        marriage_listbox.bind('<<ListboxSelect>>', on_select_marriage)
        person_listbox.bind('<<ListboxSelect>>', on_select_person)

        def save_child():
            if selected_marriage_id and selected_person_id:
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()

                    cursor.execute("INSERT INTO family (id_parent1, id_parent2, id_child) VALUES (?, ?, ?)",
                                   (selected_marriage_id[1], selected_marriage_id[2], selected_person_id))
                    conn.commit()
                    print(f"Child saved for marriage {selected_marriage_id}")
                    conn.close()

                except sqlite3.Error as e:
                    print(f"Failed to save child: {e}")
            else:
                print("Select both marriage and child.")

        save_button = tk.Button(child_window, text="Save Child", command=save_child)
        save_button.pack(pady=10)

        conn.close()
    except sqlite3.Error as e:
        print(f"Failed to retrieve data: {e}")


window = tk.Tk()
window.title("Family Tree Application")
window.geometry("400x300")

menu = Menu(window)
window.config(menu=menu)

file_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_existing_file)
file_menu.add_command(label="New", command=open_new_window)

add_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="Add", menu=add_menu)
add_menu.add_command(label="Person", command=open_person_window)
add_menu.add_command(label="Marriage", command=open_marriage_window)
add_menu.add_command(label="Child", command=open_child_window)

view_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="View", menu=view_menu)
view_menu.add_command(label="Family Tree", command=draw_family_tree)

window.mainloop()
