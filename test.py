import tkinter as tk

root = tk.Tk()
root.title("TEST")
root.geometry("400x300")

label = tk.Label(root, text="GUI działa")
label.pack()

root.mainloop()