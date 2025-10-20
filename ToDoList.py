import tkinter as tk
from tkinter import ttk, messagebox
import json, os, datetime, uuid

# ----- constants -----
DATA_FILE = "tasks_v6.json"
CATEGORIES = ["General", "Work", "Study", "Home", "Shopping", "Personal", "Health"]

class TodoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Advanced To-Do List v6 (Final)")
        self.root.geometry("700x700")
        self.root.configure(bg='#f8f9fa')

        self.metas = {}   # mapping tree item id -> serialized task
        self.setup_ui()
        self.load_tasks()  # call the loader properly

        self.root.mainloop()

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=70)
        header_frame.pack(fill='x', padx=12, pady=12)
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text="🚀 Advanced Task Manager",
                 font=('Arial', 18, 'bold'),
                 bg='#2c3e50', fg='white').pack(pady=12)

        # Search & Filters
        search_frame = tk.Frame(self.root, bg='#f8f9fa')
        search_frame.pack(fill='x', padx=20, pady=(0,10))

        tk.Label(search_frame, text="🔍 Search:",
                 font=('Arial', 10, 'bold'), bg='#f8f9fa').grid(row=0, column=0, sticky='w')
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                    font=('Arial', 10), width=28, bd=1, relief='solid')
        self.search_entry.grid(row=0, column=1, padx=6)
        self.search_entry.bind('<KeyRelease>', self.filter_tasks)

        # Status filter (All / Pending / Completed)
        tk.Label(search_frame, text="Status:",
                 font=('Arial', 10, 'bold'), bg='#f8f9fa').grid(row=0, column=2, padx=(12,4))
        self.filter_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(search_frame, textvariable=self.filter_var,
                                    values=["All", "Pending", "Completed"], state="readonly", width=12)
        status_combo.grid(row=0, column=3)
        status_combo.bind('<<ComboboxSelected>>', self.filter_tasks)

        # Category filter
        tk.Label(search_frame, text="Category:",
                 font=('Arial', 10, 'bold'), bg='#f8f9fa').grid(row=0, column=4, padx=(12,4))
        self.category_filter_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(search_frame, textvariable=self.category_filter_var,
                                      values=["All"] + CATEGORIES, state="readonly", width=14)
        category_combo.grid(row=0, column=5)
        category_combo.bind('<<ComboboxSelected>>', self.filter_tasks)

        # Add Task area
        add_frame = tk.Frame(self.root, bg='#f8f9fa')
        add_frame.pack(fill='x', padx=20, pady=(0,8))

        tk.Label(add_frame, text="📝 Task:", bg='#f8f9fa').grid(row=0, column=0, sticky='w')
        self.entry_text = tk.Entry(add_frame, width=40)
        self.entry_text.grid(row=0, column=1, padx=6)

        tk.Label(add_frame, text="Priority:", bg='#f8f9fa').grid(row=0, column=2, padx=(10,4))
        self.priority_var = tk.StringVar(value="Medium")
        priorities = ["Low", "Medium", "High", "Urgent"]
        priority_combo = ttk.Combobox(add_frame, textvariable=self.priority_var,
                                      values=priorities, state="readonly", width=10)
        priority_combo.grid(row=0, column=3)

        tk.Label(add_frame, text="Category:", bg='#f8f9fa').grid(row=0, column=4, padx=(10,4))
        self.category_var = tk.StringVar(value="General")
        category_add_combo = ttk.Combobox(add_frame, textvariable=self.category_var,
                                          values=CATEGORIES, state="readonly", width=12)
        category_add_combo.grid(row=0, column=5, padx=(0,6))

        tk.Button(add_frame, text="➕ Add Task", command=self.add_task).grid(row=0, column=6, padx=(6,0))

        # List frame with Treeview
        list_frame = tk.Frame(self.root, bg='#f8f9fa')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(list_frame,
                                 columns=('Status', 'Priority', 'Category', 'Task', 'Time'),
                                 show='headings', height=18)
        # headings
        self.tree.heading('Status', text='📊 Status')
        self.tree.heading('Priority', text='🎯 Priority')
        self.tree.heading('Category', text='📁 Category')
        self.tree.heading('Task', text='📝 Task')
        self.tree.heading('Time', text='⏰ Created')
        # columns config
        self.tree.column('Status', width=80, anchor='center')
        self.tree.column('Priority', width=100, anchor='center')
        self.tree.column('Category', width=100, anchor='center')
        self.tree.column('Task', width=320, anchor='w')
        self.tree.column('Time', width=140, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Bind double-click to toggle done
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # Controls (mark done, delete, save, stats, fullscreen)
        controls_frame = tk.Frame(self.root, bg='#f8f9fa')
        controls_frame.pack(fill='x', padx=20, pady=(0,12))

        tk.Button(controls_frame, text="✅ Mark Done/Undone", command=self.toggle_done_selected).pack(side='left', padx=6)
        tk.Button(controls_frame, text="🗑️ Delete", command=self.delete_selected).pack(side='left', padx=6)
        tk.Button(controls_frame, text="💾 Save", command=self.save_tasks).pack(side='left', padx=6)
        tk.Button(controls_frame, text="📊 Stats", command=self.show_stats).pack(side='left', padx=6)
        tk.Button(controls_frame, text="⛶ Toggle Fullscreen", command=self.toggle_fullscreen).pack(side='right', padx=6)

        # Stats label
        self.stats_label = tk.Label(self.root, text="", bg='#f8f9fa', font=('Arial', 10))
        self.stats_label.pack(fill='x', padx=20)
        self.update_stats()

        # Tree tag configuration for filtering visuals
        self.tree.tag_configure('hidden', foreground='gray')

        # fullscreen state
        self.fullscreen = False
        self.root.bind("<Escape>", lambda e: self.set_fullscreen(False))

    # ----------------- task operations -----------------
    def add_task(self):
        text = self.entry_text.get().strip()
        if not text:
            messagebox.showwarning("Warning", "Task text cannot be empty.")
            return
        task = {
            "id": str(uuid.uuid4()),
            "text": text,
            "priority": self.priority_var.get(),
            "category": self.category_var.get(),
            "done": False,
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.display_task(task)
        self.entry_text.delete(0, tk.END)
        self.save_tasks()
        self.update_stats()

    def display_task(self, task):
        status = "✅" if task.get("done") else "⏰"
        priority_emojis = {
            "Low": "🟢 Low",
            "Medium": "🟡 Medium",
            "High": "🟠 High",
            "Urgent": "🔴 Urgent"
        }
        priority_display = priority_emojis.get(task.get('priority', 'Medium'), task.get('priority', 'Medium'))
        display_values = (
            status,
            priority_display,
            task.get('category', 'General'),
            task['text'],
            task['created']
        )
        item_id = self.tree.insert('', 'end', values=display_values)
        # store full task as json string in metas
        self.metas[item_id] = json.dumps(task)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "No task selected.")
            return
        if messagebox.askyesno("Confirm", "Do you really want to delete the selected task(s)?"):
            for item in sel:
                if item in self.metas:
                    del self.metas[item]
                try:
                    self.tree.delete(item)
                except Exception:
                    pass
            self.save_tasks()
            self.update_stats()

    def toggle_done_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "No task selected.")
            return
        for item in sel:
            if item in self.metas:
                task = json.loads(self.metas[item])
                task['done'] = not task.get('done', False)
                self.metas[item] = json.dumps(task)
                # update display row
                status = "✅" if task['done'] else "⏰"
                # update tree values (Status is index 0)
                vals = list(self.tree.item(item, 'values'))
                vals[0] = status
                self.tree.item(item, values=vals)
        self.save_tasks()
        self.update_stats()

    def on_tree_double_click(self, event):
        # toggle done on double click
        item = self.tree.identify_row(event.y)
        if item:
            if item in self.metas:
                task = json.loads(self.metas[item])
                task['done'] = not task.get('done', False)
                self.metas[item] = json.dumps(task)
                vals = list(self.tree.item(item, 'values'))
                vals[0] = "✅" if task['done'] else "⏰"
                self.tree.item(item, values=vals)
                self.save_tasks()
                self.update_stats()

    # ----------------- persistence -----------------
    def save_tasks(self):
        try:
            tasks = []
            # iterate over metas to collect task dicts
            for meta_json in self.metas.values():
                tasks.append(json.loads(meta_json))
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tasks: {e}")

    def load_tasks(self):
        # clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.metas.clear()

        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
            for task in tasks:
                # ensure created exists
                if 'created' not in task:
                    task['created'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.display_task(task)
            self.update_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {e}")

    # ----------------- filtering & stats -----------------
    def filter_tasks(self, event=None):
        """Filter tasks based on search text, status, and category"""
        search_text = self.search_var.get().lower().strip()
        status_filter = self.filter_var.get()
        category_filter = self.category_filter_var.get()

        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            task_text = values[3].lower() if len(values) > 3 else ""
            category = values[2] if len(values) > 2 else ""
            status = "Completed" if values[0] == "✅" else "Pending"

            hide = False
            if search_text and search_text not in task_text:
                hide = True
            if status_filter != "All" and status_filter != status:
                hide = True
            if category_filter != "All" and category_filter != category:
                hide = True

            if hide:
                # add hidden tag
                cur_tags = set(self.tree.item(item, 'tags'))
                cur_tags.add('hidden')
                self.tree.item(item, tags=tuple(cur_tags))
            else:
                # remove hidden tag
                cur_tags = set(self.tree.item(item, 'tags'))
                if 'hidden' in cur_tags:
                    cur_tags.remove('hidden')
                self.tree.item(item, tags=tuple(cur_tags))

    def show_stats(self):
        total = len(self.metas)
        completed = sum(1 for meta in self.metas.values() if json.loads(meta).get('done', False))
        pending = total - completed
        # category stats
        category_stats = {}
        for meta in self.metas.values():
            task_data = json.loads(meta)
            cat = task_data.get('category', 'General')
            category_stats[cat] = category_stats.get(cat, 0) + 1

        stats_text = f"📊 Statistics:\n\n✅ Completed: {completed}\n⏰ Pending: {pending}\n📈 Total: {total}\n\n"
        stats_text += "📁 Categories:\n" + "\n".join([f"- {k}: {v}" for k, v in category_stats.items()])
        messagebox.showinfo("Detailed Statistics", stats_text)

    def update_stats(self):
        total = len(self.metas)
        completed = sum(1 for meta in self.metas.values() if json.loads(meta).get('done', False))
        pending = total - completed
        stats_text = f"📊 Tasks: {completed} Completed | {pending} Pending | {total} Total"
        self.stats_label.config(text=stats_text)

    # ----------------- fullscreen -----------------
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.set_fullscreen(self.fullscreen)

    def set_fullscreen(self, flag: bool):
        self.fullscreen = flag
        self.root.attributes("-fullscreen", flag)


if __name__ == "__main__":
    TodoApp()




# *********************************************************************************************************
# *********************************************************************************************************


# import tkinter as tk
# from tkinter import ttk, messagebox
# import json, os, datetime, uuid

# # Step 2: Define constants and class structure
# DATA_FILE = "tasks_v6.json"
# CATEGORIES = ["General", "Work", "Study", "Home", "Shopping", "Personal", "Health"]
# class TodoApp:
#     def __init__(self):
#         self.root = tk.Tk()
#         self.root.title("🚀 Advanced To-Do List v6")
#         self.root.geometry("600x650")
#         self.root.configure(bg='#f8f9fa')       
#         self.metas = {}
#         self.setup_ui()
#         self.load_task


#     def setup_ui(self):
#         # Modern Header
#         header_frame = tk.Frame(self.root, bg='#2c3e50', height=100)
#         header_frame.pack(fill='x', padx=15, pady=15)
#         header_frame.pack_propagate(False)  
#         tk.Label(header_frame, text="🚀 Advanced Task Manager",
#         font=('Arial', 18, 'bold'),
#         bg='#2c3e50', fg='white').pack(pady=20) 
#         # Search and Filter Section
#         search_frame = tk.Frame(self.root, bg='#f8f9fa')
#         search_frame.pack(fill='x', padx=20, pady=10)   
#         # Search Entry
#         tk.Label(search_frame, text="🔍 Search:",
#         font=('Arial', 10, 'bold'), bg='#f8f9fa').grid(row=0, column=0, sticky='w') 
#         self.search_var = tk.StringVar()
#         self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
#         font=('Arial', 10), width=25, bd=1, relief='solid')
#         self.search_entry.grid(row=0, column=1, padx=5)
#         self.search_entry.bind('<KeyRelease>', self.filter_tasks)

#         # Priority Selection
#         tk.Label(options_frame, text="Priority:",
#         font=('Arial', 10), bg='#f8f9fa').pack(side='left', padx=(0,10))        
#         self.priority_var = tk.StringVar(value="Medium")
#         priorities = ["Low", "Medium", "High", "Urgent"]
#         priority_combo = ttk.Combobox(options_frame, textvariable=self.priority_var,
#         values=priorities, state="readonly", width=10)
#         priority_combo.pack(side='left')        
#         # Category Filter
#         tk.Label(search_frame, text="Category:",
#         font=('Arial', 10, 'bold'), bg='#f8f9fa').grid(row=0, column=4, padx=(20,5))        
#         self.category_filter_var = tk.StringVar(value="All")
#         category_combo = ttk.Combobox(search_frame, textvariable=self.category_filter_var,values=["All"] + CATEGORIES, state="readonly", width=10)
#         category_combo.grid(row=0, column=5, padx=5)
#         category_combo.bind('<<ComboboxSelected>>', self.filter_tasks) 


#         # Modern Task List with Treeview
#         list_frame = tk.Frame(self.root, bg='#f8f9fa')
#         list_frame.pack(fill='both', expand=True, padx=20, pady=10)     
#         # Create Treeview with better columns
#         self.tree = ttk.Treeview(list_frame,
#         columns=('Status', 'Priority', 'Category', 'Task', 'Time'),
#         show='headings', height=15)     
#         # Configure columns
#         self.tree.heading('Status', text='📊 Status')
#         self.tree.heading('Priority', text='🎯 Priority')
#         self.tree.heading('Category', text='📁 Category')
#         self.tree.heading('Task', text='📝 Task')
#         self.tree.heading('Time', text='⏰ Created')        
#         self.tree.column('Status', width=80, anchor='center')
#         self.tree.column('Priority', width=80, anchor='center')
#         self.tree.column('Category', width=80, anchor='center')
#         self.tree.column('Task', width=250, anchor='w')
#         self.tree.column('Time', width=120, anchor='center')        
#         # Add scrollbar
#         scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
#         self.tree.configure(yscrollcommand=scrollbar.set)
#         self.tree.pack(side='left', fill='both', expand=True)
#         scrollbar.pack(side='right', fill='y')

#     def filter_tasks(self, event=None):
#         """Filter tasks based on search text and status"""
#         search_text = self.search_var.get().lower()
#         status_filter = self.filter_var.get()
#         category_filter = self.category_filter_var.get()        
#         # Show all items first
#         for item in self.tree.get_children():
#             self.tree.item(item, tags=('visible',))     
#         # Apply filters
#         for item in self.tree.get_children():
#             values = self.tree.item(item)['values']
#             task_text = values[3].lower() if len(values) > 3 else ""
#             category = values[2] if len(values) > 2 else ""
#             status = "Completed" if values[0] == "✅" else "Pending"        
#             # Search filter
#             if search_text and search_text not in task_text:
#                 self.tree.item(item, tags=('hidden',))
#                 continu
#             # Status filter
#             if status_filter != "All" and status_filter != status:
#                 self.tree.item(item, tags=('hidden',))
#                 continue        
#             # Category filter
#             if category_filter != "All" and category_filter != category:
#                 self.tree.item(item, tags=('hidden',))
#                 continue        
#         # Hide filtered items
#         self.tree.tag_configure('hidden', foreground='gray')

#     def display_task(self, task):
#         """Display task with complete information"""
#         status = "✅" if task.get("done") else "⏰"     
#         # Priority emojis
#         priority_emojis = {
#             "Low": "⏰",
#             "Medium": "⏰",
#             "High": "⏰",
#             "Urgent": "🔴"
#         }       
#         priority = priority_emojis.get(task.get('priority', 'Medium'), '⏰')        
#         display_values = (
#             status,
#             priority,
#             task.get('category', 'General'),
#             task['text'],
#             task['created']
#         )       
#         item_id = self.tree.insert('', 'end', values=display_values)
#         self.metas[item_id] = json.dumps(task)

#     def show_stats(self):
#         """Display comprehensive statistics"""
#         total = len(self.metas)
#         completed = sum(1 for meta in self.metas.values()
#             if json.loads(meta).get('done', False))
#         pending = total - completed     
#         # Category stats
#         category_stats = {}
#         for meta in self.metas.values():
#             task_data = json.loads(meta)
#             cat = task_data.get('category', 'General')
#             category_stats[cat] = category_stats.get(cat, 0) + 1        
#         stats_text = f"📊 Statistics:\n"
#         stats_text += f"✅ Completed: {completed}\n"
#         stats_text += f"⏰ Pending: {pending}\n"
#         stats_text += f"📈 Total: {total}\n"
#         stats_text += f"📁 Categories: {', '.join([f'{k}({v})' for k, v in category_stats.items()])}"       
#         messagebox.showinfo("Detailed Statistics", stats_text)

#     def save_tasks(self):
#         """Save tasks to JSON file"""
#         try:
#         # Correct method: use keys from metas
#             tasks = []
#             for item_id in self.tree.get_children():
#                 if item_id in self.metas:
#                     tasks.append(json.loads(self.metas[item_id]))       
#             with open(DATA_FILE, "w", encoding="utf-8") as f:
#                 json.dump(tasks, f, ensure_ascii=False, indent=2)
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to save tasks: {e}")     

#     def update_stats(self):
#         """Update statistics display"""
#         total = len(self.metas)
#         completed = sum(1 for meta in self.metas.values()
#             if json.loads(meta).get('done', False))
#         pending = total - completed     
#         stats_text = f"📊 Tasks: {completed} Completed | {pending} Pending | {total} Total"
#         self.stats_label.config(text=stats_text)


# *********************************************************************************************************
# *********************************************************************************************************

# def add_task():
#     task = task_entry.get()
#     category = category_var.get()
#     if task != "":
#         from datetime import datetime
#         current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
#         task_with_time = f"[{category}] {task}  ({current_time})"
#         tasks_listbox.insert(tk.END, task_with_time)
#         task_entry.delete(0, tk.END)
#     else:
#         messagebox.showwarning("Warning", "لطفاً یک تسک وارد کنید!")


# def mark_done(): 
#     try:
#         selected_index = tasks_listbox.curselection()[0]
#         task_text = tasks_listbox.get(selected_index)

#         if task_text.startswith("✔ "):
#             tasks_listbox.delete(selected_index)
#             tasks_listbox.insert(selected_index, task_text[2:])
#         else:
#             tasks_listbox.delete(selected_index)
#             tasks_listbox.insert(selected_index, "✔ " + task_text)
#     except IndexError:
#         messagebox.showwarning("Warning", "لطفاً یک تسک انتخاب کنید!")

# def delete_task():
#     try:
#         selected_index = tasks_listbox.curselection()[0]
#         tasks_listbox.delete(selected_index)
#     except IndexError:
#         messagebox.showwarning("Warning", "هیچ تسکی انتخاب نشده است!")

# def clear_all():
#     tasks_listbox.delete(0, tk.END)

# root = tk.Tk()
# root.title("To-Do List v1 - Basic")
# root.geometry("500x500")
# root.resizable(False, False)

# task_entry = tk.Entry(root, width=25, font=('Arial', 14))
# task_entry.pack(pady=10)

# top_frame = tk.Frame(root)
# top_frame.pack(pady=10)

# task_entry = tk.Entry(top_frame, width=25, font=('Arial', 14))
# task_entry.grid(row=0, column=0, padx=5)

# categories = ["General", "Home", "Study", "Shopping", "Work"]
# category_var = tk.StringVar(value=categories[0])
# category_menu = ttk.Combobox(top_frame, textvariable=category_var, values=categories, width=10, state="readonly")
# category_menu.grid(row=0, column=1, padx=5)

# add_button = tk.Button(top_frame, text="Add Task", width=10, bg="green", fg="white", font=('Arial', 10, 'bold'), command=add_task)
# add_button.grid(row=0, column=2, padx=5)


# tasks_listbox = tk.Listbox(root, width=50, height=10, selectmode=tk.SINGLE, font=('Arial', 12))
# tasks_listbox.pack(pady=10)

# frame = tk.Frame(root)
# frame.pack(pady=10)

# delete_button = tk.Button(frame, text="Delete Task", bg="red", fg="white", width=12, font=('Arial', 10, 'bold'), command=delete_task)
# delete_button.grid(row=0, column=0, padx=5)

# done_button = tk.Button(frame, text="Mark Done", bg="dodgerblue", fg="white", width=12, font=('Arial', 10, 'bold'), command=mark_done)
# done_button.grid(row=0, column=1, padx=5)

# clear_button = tk.Button(frame, text="Clear All", bg="purple", fg="white", width=12, font=('Arial', 10, 'bold'), command=clear_all)
# clear_button.grid(row=0, column=2, padx=5)

# root.mainloop()
