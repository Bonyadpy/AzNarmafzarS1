import tkinter as tk
from tkinter import ttk, messagebox
import json, os, datetime, uuid

DATA_FILE = "tasks_v6.json"
CATEGORIES = ["General", "Work", "Study", "Home", "Shopping", "Personal", "Health"]

class TodoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Advanced To-Do List v6 (Modern UI)")
        self.root.geometry("850x720")
        self.root.configure(bg='#edf2f7')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", font=('Segoe UI', 10), rowheight=26, background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=('Segoe UI Semibold', 10), background="#2c3e50", foreground="white")
        style.map("Treeview", background=[('selected', '#cce5ff')])

        self.metas = {}
        self.fullscreen = False
        self.setup_ui()
        self.load_tasks()

        self.root.bind("<Escape>", lambda e: self.set_fullscreen(False))
        self.root.mainloop()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="🚀 Advanced Task Manager",
                 font=('Segoe UI Semibold', 20),
                 bg='#2c3e50', fg='white').pack(pady=14)

        # Search + Filters
        top_frame = tk.Frame(self.root, bg='#edf2f7')
        top_frame.pack(fill='x', padx=20, pady=(10, 0))

        # Search
        tk.Label(top_frame, text="🔍 Search:", bg='#edf2f7', font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, padx=5)
        search_entry.bind("<KeyRelease>", self.filter_tasks)

        # Status filter
        tk.Label(top_frame, text="Status:", bg='#edf2f7', font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, padx=(15,5))
        self.filter_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(top_frame, textvariable=self.filter_var, values=["All","Pending","Completed"], state="readonly", width=12)
        status_combo.grid(row=0, column=3)
        status_combo.bind("<<ComboboxSelected>>", self.filter_tasks)

        # Category filter
        tk.Label(top_frame, text="Category:", bg='#edf2f7', font=('Segoe UI', 10, 'bold')).grid(row=0, column=4, padx=(15,5))
        self.category_filter_var = tk.StringVar(value="All")
        cat_combo = ttk.Combobox(top_frame, textvariable=self.category_filter_var, values=["All"]+CATEGORIES, state="readonly", width=14)
        cat_combo.grid(row=0, column=5)
        cat_combo.bind("<<ComboboxSelected>>", self.filter_tasks)

        # Divider
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', padx=20, pady=10)

        # Add Task Section
        add_frame = tk.LabelFrame(self.root, text="➕ Add New Task", bg='#edf2f7', font=('Segoe UI', 10, 'bold'))
        add_frame.pack(fill='x', padx=20, pady=(0,10))

        tk.Label(add_frame, text="Task:", bg='#edf2f7', font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_text = ttk.Entry(add_frame, width=45)
        self.entry_text.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_frame, text="Category:", bg='#edf2f7', font=('Segoe UI', 10)).grid(row=0, column=2, padx=(15,5))
        self.category_var = tk.StringVar(value="General")
        cat_add = ttk.Combobox(add_frame, textvariable=self.category_var, values=CATEGORIES, state="readonly", width=14)
        cat_add.grid(row=0, column=3, pady=5)

        tk.Label(add_frame, text="Priority:", bg='#edf2f7', font=('Segoe UI', 10)).grid(row=0, column=4, padx=(15,5))
        self.priority_var = tk.StringVar(value="Medium")
        pri_add = ttk.Combobox(add_frame, textvariable=self.priority_var, values=["Low","Medium","High","Urgent"], state="readonly", width=10)
        pri_add.grid(row=0, column=5, pady=5)

        ttk.Button(add_frame, text="Add Task", command=self.add_task).grid(row=0, column=6, padx=(20,0))

        # Task List
        list_frame = tk.Frame(self.root, bg='#edf2f7')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0,10))

        columns = ('Status', 'Priority', 'Category', 'Task', 'Created')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=18)
        for col, text in zip(columns, ['📊 Status', '🎯 Priority', '📁 Category', '📝 Task', '⏰ Created']):
            self.tree.heading(col, text=text)
        self.tree.column('Status', width=90, anchor='center')
        self.tree.column('Priority', width=120, anchor='center')
        self.tree.column('Category', width=120, anchor='center')
        self.tree.column('Task', width=350, anchor='w')
        self.tree.column('Created', width=150, anchor='center')

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # Bottom buttons
        bottom = tk.Frame(self.root, bg='#edf2f7')
        bottom.pack(fill='x', padx=20, pady=(0,10))

        btn_style = {'font':('Segoe UI', 9, 'bold'), 'padx':10, 'pady':4}
        tk.Button(bottom, text="✅ Toggle Done", bg="#c8e6c9", relief='flat', command=self.toggle_done_selected, **btn_style).pack(side='left', padx=4)
        tk.Button(bottom, text="✏️ Edit", bg="#ffe0b2", relief='flat', command=self.edit_selected, **btn_style).pack(side='left', padx=4)
        tk.Button(bottom, text="🗑️ Delete", bg="#ffcdd2", relief='flat', command=self.delete_selected, **btn_style).pack(side='left', padx=4)
        tk.Button(bottom, text="📊 Stats", bg="#d1c4e9", relief='flat', command=self.show_stats, **btn_style).pack(side='left', padx=4)
        tk.Button(bottom, text="🔄 Refresh", bg="#bbdefb", relief='flat', command=self.load_tasks, **btn_style).pack(side='left', padx=4)
        tk.Button(bottom, text="⛶ Fullscreen", bg="#b2dfdb", relief='flat', command=self.toggle_fullscreen, **btn_style).pack(side='right', padx=4)

        self.stats_label = tk.Label(self.root, text="", bg='#edf2f7', font=('Segoe UI', 10, 'bold'))
        self.stats_label.pack(fill='x', pady=(0,8))
        self.update_stats()

    # === Functional methods (same as before) ===
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
        self.metas[self.tree.insert('', 'end', values=(
            status,
            task.get('priority', 'Medium'),
            task.get('category', 'General'),
            task['text'],
            task['created']
        ))] = json.dumps(task)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        if messagebox.askyesno("Confirm", "Delete selected task(s)?"):
            for item in sel:
                if item in self.metas: del self.metas[item]
                self.tree.delete(item)
            self.save_tasks(); self.update_stats()

    def toggle_done_selected(self):
        for item in self.tree.selection():
            task = json.loads(self.metas[item])
            task['done'] = not task.get('done', False)
            vals = list(self.tree.item(item, 'values'))
            vals[0] = "✅" if task['done'] else "⏰"
            self.tree.item(item, values=vals)
            self.metas[item] = json.dumps(task)
        self.save_tasks(); self.update_stats()

    def on_tree_double_click(self, e): self.toggle_done_selected()
    def edit_selected(self):
        sel = self.tree.selection()
        if not sel: return
        item = sel[0]
        task = json.loads(self.metas[item])
        new_text = tk.simpledialog.askstring("Edit Task", "Edit task text:", initialvalue=task['text'])
        if new_text:
            task['text'] = new_text
            vals = list(self.tree.item(item, 'values'))
            vals[3] = new_text
            self.tree.item(item, values=vals)
            self.metas[item] = json.dumps(task)
            self.save_tasks()

    def save_tasks(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([json.loads(m) for m in self.metas.values()], f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        self.metas.clear()
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    for t in json.load(f): self.display_task(t)
            except: pass
        self.update_stats()

    def show_stats(self):
        total=len(self.metas)
        done=sum(1 for m in self.metas.values() if json.loads(m).get('done',False))
        pend=total-done
        messagebox.showinfo("Stats", f"✅ Done: {done}\n⏰ Pending: {pend}\n📈 Total: {total}")

    def update_stats(self):
        total=len(self.metas)
        done=sum(1 for m in self.metas.values() if json.loads(m).get('done',False))
        pend=total-done
        self.stats_label.config(text=f"📊 Tasks → {done} Done | {pend} Pending | {total} Total")

    def filter_tasks(self, e=None):
        s=self.search_var.get().lower(); st=self.filter_var.get(); cat=self.category_filter_var.get()
        for i in self.tree.get_children():
            v=self.tree.item(i)['values']; hide=False
            if s and s not in v[3].lower(): hide=True
            if st!="All" and st!=("Completed" if v[0]=="✅" else "Pending"): hide=True
            if cat!="All" and cat!=v[2]: hide=True
            self.tree.detach(i) if hide else self.tree.reattach(i,'','end')

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.set_fullscreen(self.fullscreen)

    def set_fullscreen(self, flag):
        self.root.attributes("-fullscreen", flag)
        self.fullscreen = flag


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
