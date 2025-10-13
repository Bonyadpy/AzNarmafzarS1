import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from tkinter import ttk



def add_task():
    task = task_entry.get()
    category = category_var.get()
    if task != "":
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        task_with_time = f"[{category}] {task}  ({current_time})"
        tasks_listbox.insert(tk.END, task_with_time)
        task_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Warning", "لطفاً یک تسک وارد کنید!")


def mark_done(): 
    try:
        selected_index = tasks_listbox.curselection()[0]
        task_text = tasks_listbox.get(selected_index)

        if task_text.startswith("✔ "):
            tasks_listbox.delete(selected_index)
            tasks_listbox.insert(selected_index, task_text[2:])
        else:
            tasks_listbox.delete(selected_index)
            tasks_listbox.insert(selected_index, "✔ " + task_text)
    except IndexError:
        messagebox.showwarning("Warning", "لطفاً یک تسک انتخاب کنید!")

def delete_task():
    try:
        selected_index = tasks_listbox.curselection()[0]
        tasks_listbox.delete(selected_index)
    except IndexError:
        messagebox.showwarning("Warning", "هیچ تسکی انتخاب نشده است!")

def clear_all():
    tasks_listbox.delete(0, tk.END)

root = tk.Tk()
root.title("To-Do List v1 - Basic")
root.geometry("500x500")
root.resizable(False, False)

task_entry = tk.Entry(root, width=25, font=('Arial', 14))
task_entry.pack(pady=10)

top_frame = tk.Frame(root)
top_frame.pack(pady=10)

task_entry = tk.Entry(top_frame, width=25, font=('Arial', 14))
task_entry.grid(row=0, column=0, padx=5)

categories = ["General", "Home", "Study", "Shopping", "Work"]
category_var = tk.StringVar(value=categories[0])
category_menu = ttk.Combobox(top_frame, textvariable=category_var, values=categories, width=10, state="readonly")
category_menu.grid(row=0, column=1, padx=5)

add_button = tk.Button(top_frame, text="Add Task", width=10, bg="green", fg="white", font=('Arial', 10, 'bold'), command=add_task)
add_button.grid(row=0, column=2, padx=5)


tasks_listbox = tk.Listbox(root, width=50, height=10, selectmode=tk.SINGLE, font=('Arial', 12))
tasks_listbox.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

delete_button = tk.Button(frame, text="Delete Task", bg="red", fg="white", width=12, font=('Arial', 10, 'bold'), command=delete_task)
delete_button.grid(row=0, column=0, padx=5)

done_button = tk.Button(frame, text="Mark Done", bg="dodgerblue", fg="white", width=12, font=('Arial', 10, 'bold'), command=mark_done)
done_button.grid(row=0, column=1, padx=5)

clear_button = tk.Button(frame, text="Clear All", bg="purple", fg="white", width=12, font=('Arial', 10, 'bold'), command=clear_all)
clear_button.grid(row=0, column=2, padx=5)

root.mainloop()
