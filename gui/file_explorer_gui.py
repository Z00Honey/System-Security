import tkinter as tk
from explorer_interface import list_files

def show_files():
    directory = entry.get()
    list_files(directory)

root = tk.Tk()
root.title("File Explorer")

entry = tk.Entry(root)
entry.pack()

button = tk.Button(root, text="List Files", command=show_files)
button.pack()

root.mainloop()
