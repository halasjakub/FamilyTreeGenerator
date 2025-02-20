import tkinter as tk
from tkinter import Menu



window = tk.Tk()
window.title("Family Tree Generator")
window.geometry("800x600")

# Set up the main window
menu_bar = Menu(window)
window.config(menu=menu_bar)

# File options
file_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New")
file_menu.add_command(label="Open")
file_menu.add_command(label="Close")

# Add options
add_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Add", menu=add_menu)
add_menu.add_command(label="Person")
add_menu.add_command(label="Relation")


window.mainloop()