import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class AdvancedWallet:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Wallet - Advanced Version")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # Data
        self.transactions = []
        self.budgets = {}
        self.data_file = Path("wallet_data_v2.json")
        self.load_data()

        # Categories
        self.income_categories = ["Salary", "Freelance", "Investment", "Gift", "Other"]
        self.expense_categories = ["Food", "Transport", "Shopping", "Bills",
                                   "Entertainment", "Healthcare", "Other"]

        # Search filters
        self.search_var = tk.StringVar()
        self.filter_type_var = tk.StringVar(value="all")
        self.filter_category_var = tk.StringVar(value="all")

        # Create UI
        self.create_menu()
        self.create_widgets()
        self.update_all()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export JSON", command=self.export_json)
        file_menu.add_command(label="Import JSON", command=self.import_json)
        file_menu.add_command(label="Export CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Budget Menu
        budget_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Budget", menu=budget_menu)
        budget_menu.add_command(label="Set Budget", command=self.open_budget_window)
        budget_menu.add_command(label="View Budget Status", command=self.show_budget_status)

        # Analytics Menu
        analytics_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analytics", menu=analytics_menu)
        analytics_menu.add_command(label="Expense Pie Chart", command=self.show_expense_chart)
        analytics_menu.add_command(label="Monthly Statistics", command=self.show_monthly_stats)
        analytics_menu.add_command(label="Category Analysis", command=self.show_category_analysis)

    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Dashboard
        self.create_dashboard_tab()

        # Tab 2: Transactions
        self.create_transactions_tab()

        # Tab 3: Analytics
        self.create_analytics_tab()

    def create_dashboard_tab(self):
        dashboard_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(dashboard_frame, text="📊 Dashboard")

        # Title
        title_frame = tk.Frame(dashboard_frame, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=10, pady=10)
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="💰 Personal Wallet Dashboard",
                font=('Arial', 20, 'bold'), bg='#2c3e50', fg='white').pack(pady=10)

        # Balance Summary
        summary_frame = tk.Frame(dashboard_frame, bg='white')
        summary_frame.pack(fill='x', padx=20, pady=10)

        # Income Box
        income_box = tk.Frame(summary_frame, bg='#27ae60', relief='raised', bd=2)
        income_box.pack(side='left', expand=True, fill='both', padx=5)
        tk.Label(income_box, text="Total Income", font=('Arial', 12),
                bg='#27ae60', fg='white').pack(pady=5)
        self.dash_income_label = tk.Label(income_box, text="$0.00",
                                         font=('Arial', 20, 'bold'), bg='#27ae60', fg='white')
        self.dash_income_label.pack(pady=10)

        # Expense Box
        expense_box = tk.Frame(summary_frame, bg='#e74c3c', relief='raised', bd=2)
        expense_box.pack(side='left', expand=True, fill='both', padx=5)
        tk.Label(expense_box, text="Total Expense", font=('Arial', 12),
                bg='#e74c3c', fg='white').pack(pady=5)
        self.dash_expense_label = tk.Label(expense_box, text="$0.00",
                                          font=('Arial', 20, 'bold'), bg='#e74c3c', fg='white')
        self.dash_expense_label.pack(pady=10)

        # Balance Box
        balance_box = tk.Frame(summary_frame, bg='#3498db', relief='raised', bd=2)
        balance_box.pack(side='left', expand=True, fill='both', padx=5)
        tk.Label(balance_box, text="Current Balance", font=('Arial', 12),
                bg='#3498db', fg='white').pack(pady=5)
        self.dash_balance_label = tk.Label(balance_box, text="$0.00",
                                          font=('Arial', 20, 'bold'), bg='#3498db', fg='white')
        self.dash_balance_label.pack(pady=10)

        # Statistics Frame
        stats_frame = tk.Frame(dashboard_frame, bg='white')
        stats_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Left: Recent Transactions
        recent_frame = tk.LabelFrame(stats_frame, text="Recent Transactions (Last 5)",
                                     font=('Arial', 12, 'bold'), bg='white')
        recent_frame.pack(side='left', fill='both', expand=True, padx=5)

        self.recent_listbox = tk.Listbox(recent_frame, font=('Courier', 9), height=15)
        self.recent_listbox.pack(fill='both', expand=True, padx=10, pady=10)

        # Right: Budget Alerts
        budget_frame = tk.LabelFrame(stats_frame, text="Budget Alerts & Warnings",
                                     font=('Arial', 12, 'bold'), bg='white')
        budget_frame.pack(side='right', fill='both', expand=True, padx=5)

        self.budget_text = tk.Text(budget_frame, font=('Arial', 10), height=15, wrap='word')
        self.budget_text.pack(fill='both', expand=True, padx=10, pady=10)

    def create_transactions_tab(self):
        trans_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(trans_frame, text="💳 Transactions")

        # Top Frame: Add Transaction
        add_frame = tk.LabelFrame(trans_frame, text="Add New Transaction",
                                 font=('Arial', 12, 'bold'), bg='white')
        add_frame.pack(fill='x', padx=10, pady=10)

        form_frame = tk.Frame(add_frame, bg='white')
        form_frame.pack(padx=20, pady=10)

        # Row 1: Type and Amount
        row1 = tk.Frame(form_frame, bg='white')
        row1.pack(fill='x', pady=5)

        tk.Label(row1, text="Type:", font=('Arial', 10), bg='white', width=10).pack(side='left')
        self.type_var = tk.StringVar(value="expense")
        tk.Radiobutton(row1, text="Income", variable=self.type_var, value="income",
                      bg='white', command=self.update_categories).pack(side='left', padx=5)
        tk.Radiobutton(row1, text="Expense", variable=self.type_var, value="expense",
                      bg='white', command=self.update_categories).pack(side='left', padx=5)

        tk.Label(row1, text="Amount:", font=('Arial', 10), bg='white', width=10).pack(side='left', padx=(20,0))
        self.amount_entry = tk.Entry(row1, font=('Arial', 10), width=15)
        self.amount_entry.pack(side='left', padx=5)

        # Row 2: Category and Date
        row2 = tk.Frame(form_frame, bg='white')
        row2.pack(fill='x', pady=5)

        tk.Label(row2, text="Category:", font=('Arial', 10), bg='white', width=10).pack(side='left')
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(row2, textvariable=self.category_var,
                                          font=('Arial', 10), width=15, state='readonly')
        self.category_combo.pack(side='left', padx=5)
        self.update_categories()

        tk.Label(row2, text="Date:", font=('Arial', 10), bg='white', width=10).pack(side='left', padx=(20,0))
        self.date_entry = tk.Entry(row2, font=('Arial', 10), width=15)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(side='left', padx=5)

        # Row 3: Description
        row3 = tk.Frame(form_frame, bg='white')
        row3.pack(fill='x', pady=5)

        tk.Label(row3, text="Description:", font=('Arial', 10), bg='white', width=10).pack(side='left')
        self.desc_entry = tk.Entry(row3, font=('Arial', 10), width=50)
        self.desc_entry.pack(side='left', padx=5)

        tk.Button(row3, text="Add Transaction", font=('Arial', 10, 'bold'),
                 bg='#3498db', fg='white', command=self.add_transaction,
                 width=15).pack(side='left', padx=20)

        # Middle Frame: Search and Filter
        search_frame = tk.LabelFrame(trans_frame, text="Search & Filter",
                                    font=('Arial', 12, 'bold'), bg='white')
        search_frame.pack(fill='x', padx=10, pady=5)

        filter_controls = tk.Frame(search_frame, bg='white')
        filter_controls.pack(padx=20, pady=10)

        tk.Label(filter_controls, text="Search:", font=('Arial', 10), bg='white').pack(side='left', padx=5)
        search_entry = tk.Entry(filter_controls, textvariable=self.search_var,
                               font=('Arial', 10), width=20)
        search_entry.pack(side='left', padx=5)

        tk.Label(filter_controls, text="Type:", font=('Arial', 10), bg='white').pack(side='left', padx=(20,5))
        type_filter = ttk.Combobox(filter_controls, textvariable=self.filter_type_var,
                                  values=["all", "income", "expense"], width=10, state='readonly')
        type_filter.pack(side='left', padx=5)

        tk.Label(filter_controls, text="Category:", font=('Arial', 10), bg='white').pack(side='left', padx=(20,5))
        all_cats = ["all"] + self.income_categories + self.expense_categories
        cat_filter = ttk.Combobox(filter_controls, textvariable=self.filter_category_var,
                                 values=list(set(all_cats)), width=15, state='readonly')
        cat_filter.pack(side='left', padx=5)

        tk.Button(filter_controls, text="Apply Filter", font=('Arial', 10),
                 bg='#16a085', fg='white', command=self.apply_filter).pack(side='left', padx=20)
        tk.Button(filter_controls, text="Clear Filter", font=('Arial', 10),
                 bg='#95a5a6', fg='white', command=self.clear_filter).pack(side='left', padx=5)

        # Bottom Frame: Transaction List
        list_frame = tk.LabelFrame(trans_frame, text="All Transactions",
                                  font=('Arial', 12, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Create Treeview
        tree_scroll = tk.Scrollbar(list_frame)
        tree_scroll.pack(side='right', fill='y')

        self.trans_tree = ttk.Treeview(list_frame, yscrollcommand=tree_scroll.set,
                                       columns=("Date", "Type", "Category", "Amount", "Description"),
                                       show='headings', height=15)
        self.trans_tree.pack(fill='both', expand=True, padx=10, pady=10)
        tree_scroll.config(command=self.trans_tree.yview)

        # Configure columns
        self.trans_tree.heading("Date", text="Date")
        self.trans_tree.heading("Type", text="Type")
        self.trans_tree.heading("Category", text="Category")
        self.trans_tree.heading("Amount", text="Amount")
        self.trans_tree.heading("Description", text="Description")

        self.trans_tree.column("Date", width=100)
        self.trans_tree.column("Type", width=80)
        self.trans_tree.column("Category", width=120)
        self.trans_tree.column("Amount", width=100)
        self.trans_tree.column("Description", width=300)

        # Configure tags for colors
        self.trans_tree.tag_configure('income', foreground='#27ae60')
        self.trans_tree.tag_configure('expense', foreground='#e74c3c')

        # Delete button
        tk.Button(list_frame, text="Delete Selected", font=('Arial', 10, 'bold'),
                 bg='#e74c3c', fg='white', command=self.delete_transaction).pack(pady=5)

    def create_analytics_tab(self):
        analytics_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(analytics_frame, text="📈 Analytics")

        # Chart Frame
        chart_frame = tk.Frame(analytics_frame, bg='white')
        chart_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Create figure for chart
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Button Frame
        button_frame = tk.Frame(analytics_frame, bg='white')
        button_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(button_frame, text="Expense Pie Chart", font=('Arial', 10, 'bold'),
                 bg='#9b59b6', fg='white', command=self.show_expense_chart,
                 width=20).pack(side='left', padx=5)
        tk.Button(button_frame, text="Income Pie Chart", font=('Arial', 10, 'bold'),
                 bg='#27ae60', fg='white', command=self.show_income_chart,
                 width=20).pack(side='left', padx=5)
        tk.Button(button_frame, text="Monthly Trend", font=('Arial', 10, 'bold'),
                 bg='#3498db', fg='white', command=self.show_monthly_trend,
                 width=20).pack(side='left', padx=5)

    def update_categories(self):
        if self.type_var.get() == "income":
            self.category_combo['values'] = self.income_categories
        else:
            self.category_combo['values'] = self.expense_categories
        self.category_combo.set('')

    def add_transaction(self):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_var.get()
            date = self.date_entry.get()
            description = self.desc_entry.get()
            trans_type = self.type_var.get()

            if not category:
                messagebox.showwarning("Warning", "Please select a category!")
                return

            if amount <= 0:
                messagebox.showwarning("Warning", "Amount must be greater than 0!")
                return

            transaction = {
                'id': datetime.now().timestamp(),
                'type': trans_type,
                'amount': amount,
                'category': category,
                'date': date,
                'description': description,
                'timestamp': datetime.now().isoformat()
            }

            self.transactions.append(transaction)
            self.save_data()
            self.update_all()

            # Clear form
            self.amount_entry.delete(0, 'end')
            self.category_var.set('')
            self.desc_entry.delete(0, 'end')
            self.date_entry.delete(0, 'end')
            self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

            # Check budget after adding expense
            if trans_type == 'expense':
                self.check_budget_alert(category, amount)

            messagebox.showinfo("Success", "Transaction added successfully!")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")

    def check_budget_alert(self, category, amount):
        if category in self.budgets:
            budget_limit = self.budgets[category]
            current_month = datetime.now().strftime("%Y-%m")

            # Calculate current month spending for this category
            monthly_spending = sum(
                t['amount'] for t in self.transactions
                if t['type'] == 'expense' and t['category'] == category
                and t['date'].startswith(current_month)
            )

            percentage = (monthly_spending / budget_limit) * 100

            if monthly_spending > budget_limit:
                messagebox.showwarning(
                    "Budget Exceeded!",
                    f"You have exceeded your budget for {category}!\n"
                    f"Budget: ${budget_limit:.2f}\n"
                    f"Spent: ${monthly_spending:.2f}\n"
                    f"Over by: ${monthly_spending - budget_limit:.2f}"
                )
            elif percentage >= 80:
                messagebox.showinfo(
                    "Budget Warning",
                    f"You have used {percentage:.1f}% of your {category} budget.\n"
                    f"Budget: ${budget_limit:.2f}\n"
                    f"Spent: ${monthly_spending:.2f}\n"
                    f"Remaining: ${budget_limit - monthly_spending:.2f}"
                )

    def update_all(self):
        self.update_dashboard()
        self.refresh_transaction_tree()
        self.update_budget_alerts()

    def update_dashboard(self):
        total_income = sum(t['amount'] for t in self.transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in self.transactions if t['type'] == 'expense')
        balance = total_income - total_expense

        self.dash_income_label.config(text=f"${total_income:.2f}")
        self.dash_expense_label.config(text=f"${total_expense:.2f}")
        self.dash_balance_label.config(text=f"${balance:.2f}")

        # Update recent transactions
        self.recent_listbox.delete(0, 'end')
        sorted_trans = sorted(self.transactions, key=lambda x: x['timestamp'], reverse=True)[:5]

        for t in sorted_trans:
            sign = "+" if t['type'] == 'income' else "-"
            display = f"{t['date']} | {t['category']:12} | {sign}${t['amount']:.2f}"
            self.recent_listbox.insert('end', display)
            index = self.recent_listbox.size() - 1
            color = '#27ae60' if t['type'] == 'income' else '#e74c3c'
            self.recent_listbox.itemconfig(index, fg=color)

    def update_budget_alerts(self):
        self.budget_text.delete('1.0', 'end')

        if not self.budgets:
            self.budget_text.insert('end', "No budgets set. Go to Budget > Set Budget to create one.\n\n")
            return

        current_month = datetime.now().strftime("%Y-%m")
        self.budget_text.insert('end', f"Budget Status for {current_month}:\n\n", 'title')

        for category, budget_limit in self.budgets.items():
            monthly_spending = sum(
                t['amount'] for t in self.transactions
                if t['type'] == 'expense' and t['category'] == category
                and t['date'].startswith(current_month)
            )

            remaining = budget_limit - monthly_spending
            percentage = (monthly_spending / budget_limit) * 100 if budget_limit > 0 else 0

            status_text = f"📊 {category}:\n"
            status_text += f"   Budget: ${budget_limit:.2f}\n"
            status_text += f"   Spent: ${monthly_spending:.2f} ({percentage:.1f}%)\n"
            status_text += f"   Remaining: ${remaining:.2f}\n"

            if monthly_spending > budget_limit:
                status_text += "   ⚠️ EXCEEDED!\n\n"
                self.budget_text.insert('end', status_text, 'exceeded')
            elif percentage >= 80:
                status_text += "   ⚠️ Warning: Approaching limit\n\n"
                self.budget_text.insert('end', status_text, 'warning')
            else:
                status_text += "   ✅ On track\n\n"
                self.budget_text.insert('end', status_text, 'ok')

        # Configure tags
        self.budget_text.tag_config('title', font=('Arial', 11, 'bold'))
        self.budget_text.tag_config('exceeded', foreground='#e74c3c')
        self.budget_text.tag_config('warning', foreground='#e67e22')
        self.budget_text.tag_config('ok', foreground='#27ae60')

    def refresh_transaction_tree(self):
        # Clear existing items
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)

        # Sort transactions by date (newest first)
        sorted_trans = sorted(self.transactions, key=lambda x: x['timestamp'], reverse=True)

        for t in sorted_trans:
            sign = "+" if t['type'] == 'income' else "-"
            amount_str = f"{sign}${t['amount']:.2f}"
            tag = 'income' if t['type'] == 'income' else 'expense'

            self.trans_tree.insert('', 'end', values=(
                t['date'], t['type'].capitalize(), t['category'],
                amount_str, t['description']
            ), tags=(tag,))

    def apply_filter(self):
        # Clear existing items
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)

        search_term = self.search_var.get().lower()
        type_filter = self.filter_type_var.get()
        category_filter = self.filter_category_var.get()

        filtered_trans = self.transactions

        # Apply type filter
        if type_filter != "all":
            filtered_trans = [t for t in filtered_trans if t['type'] == type_filter]

        # Apply category filter
        if category_filter != "all":
            filtered_trans = [t for t in filtered_trans if t['category'] == category_filter]

        # Apply search filter
        if search_term:
            filtered_trans = [
                t for t in filtered_trans
                if search_term in t['description'].lower() or search_term in t['category'].lower()
            ]

        # Display filtered results
        sorted_trans = sorted(filtered_trans, key=lambda x: x['timestamp'], reverse=True)

        for t in sorted_trans:
            sign = "+" if t['type'] == 'income' else "-"
            amount_str = f"{sign}${t['amount']:.2f}"
            tag = 'income' if t['type'] == 'income' else 'expense'

            self.trans_tree.insert('', 'end', values=(
                t['date'], t['type'].capitalize(), t['category'],
                amount_str, t['description']
            ), tags=(tag,))

    def clear_filter(self):
        self.search_var.set("")
        self.filter_type_var.set("all")
        self.filter_category_var.set("all")
        self.refresh_transaction_tree()

    def delete_transaction(self):
        selection = self.trans_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a transaction to delete!")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?"):
            item = self.trans_tree.item(selection[0])
            values = item['values']

            # Find and remove transaction
            date, trans_type, category, amount_str, description = values
            trans_type = trans_type.lower()
            amount = float(amount_str.replace('+', '').replace('-', '').replace('$', ''))

            for t in self.transactions:
                if (t['date'] == date and t['type'] == trans_type and
                    t['category'] == category and t['amount'] == amount):
                    self.transactions.remove(t)
                    break

            self.save_data()
            self.update_all()
            messagebox.showinfo("Success", "Transaction deleted successfully!")

    def open_budget_window(self):
        budget_win = tk.Toplevel(self.root)
        budget_win.title("Set Monthly Budget")
        budget_win.geometry("400x500")
        budget_win.configure(bg='white')

        tk.Label(budget_win, text="Set Monthly Budget by Category",
                font=('Arial', 14, 'bold'), bg='white').pack(pady=20)

        budget_frame = tk.Frame(budget_win, bg='white')
        budget_frame.pack(fill='both', expand=True, padx=20, pady=10)

        budget_entries = {}

        for category in self.expense_categories:
            cat_frame = tk.Frame(budget_frame, bg='white')
            cat_frame.pack(fill='x', pady=5)

            tk.Label(cat_frame, text=f"{category}:", font=('Arial', 10),
                    bg='white', width=15, anchor='w').pack(side='left')

            entry = tk.Entry(cat_frame, font=('Arial', 10), width=15)
            entry.pack(side='left', padx=10)

            # Set current budget value if exists
            if category in self.budgets:
                entry.insert(0, str(self.budgets[category]))

            budget_entries[category] = entry

        def save_budgets():
            try:
                for category, entry in budget_entries.items():
                    value = entry.get()
                    if value:
                        self.budgets[category] = float(value)
                    elif category in self.budgets:
                        del self.budgets[category]

                self.save_data()
                self.update_budget_alerts()
                messagebox.showinfo("Success", "Budgets saved successfully!")
                budget_win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers!")

        tk.Button(budget_win, text="Save Budgets", font=('Arial', 11, 'bold'),
                 bg='#27ae60', fg='white', command=save_budgets,
                 width=20).pack(pady=20)

    def show_budget_status(self):
        status_win = tk.Toplevel(self.root)
        status_win.title("Budget Status Report")
        status_win.geometry("600x500")
        status_win.configure(bg='white')

        tk.Label(status_win, text="Monthly Budget Status",
                font=('Arial', 16, 'bold'), bg='white').pack(pady=20)

        # Create text widget with scrollbar
        text_frame = tk.Frame(status_win, bg='white')
        text_frame.pack(fill='both', expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')

        text_widget = tk.Text(text_frame, font=('Arial', 10),
                             yscrollcommand=scrollbar.set, wrap='word')
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=text_widget.yview)

        # Generate report
        current_month = datetime.now().strftime("%Y-%m")

        if not self.budgets:
            text_widget.insert('end', "No budgets have been set yet.\n\n")
        else:
            text_widget.insert('end', f"Budget Report for {current_month}\n", 'title')
            text_widget.insert('end', "=" * 60 + "\n\n")

            total_budget = 0
            total_spent = 0

            for category, budget_limit in self.budgets.items():
                monthly_spending = sum(
                    t['amount'] for t in self.transactions
                    if t['type'] == 'expense' and t['category'] == category
                    and t['date'].startswith(current_month)
                )

                total_budget += budget_limit
                total_spent += monthly_spending

                remaining = budget_limit - monthly_spending
                percentage = (monthly_spending / budget_limit) * 100 if budget_limit > 0 else 0

                text_widget.insert('end', f"\n{category}\n", 'category')
                text_widget.insert('end', f"  Budget Limit:  ${budget_limit:.2f}\n")
                text_widget.insert('end', f"  Amount Spent:  ${monthly_spending:.2f}\n")
                text_widget.insert('end', f"  Remaining:     ${remaining:.2f}\n")
                text_widget.insert('end', f"  Usage:         {percentage:.1f}%\n")

                if monthly_spending > budget_limit:
                    text_widget.insert('end', f"  Status:        ⚠️ EXCEEDED by ${monthly_spending - budget_limit:.2f}\n", 'exceeded')
                elif percentage >= 80:
                    text_widget.insert('end', f"  Status:        ⚠️ Warning - Approaching limit\n", 'warning')
                else:
                    text_widget.insert('end', f"  Status:        ✅ On track\n", 'ok')

            text_widget.insert('end', "\n" + "=" * 60 + "\n")
            text_widget.insert('end', f"\nTotal Budget:  ${total_budget:.2f}\n", 'bold')
            text_widget.insert('end', f"Total Spent:   ${total_spent:.2f}\n", 'bold')
            text_widget.insert('end', f"Total Remaining: ${total_budget - total_spent:.2f}\n", 'bold')

        # Configure tags
        text_widget.tag_config('title', font=('Arial', 12, 'bold'))
        text_widget.tag_config('category', font=('Arial', 11, 'bold'), foreground='#2c3e50')
        text_widget.tag_config('bold', font=('Arial', 11, 'bold'))
        text_widget.tag_config('exceeded', foreground='#e74c3c', font=('Arial', 10, 'bold'))
        text_widget.tag_config('warning', foreground='#e67e22', font=('Arial', 10, 'bold'))
        text_widget.tag_config('ok', foreground='#27ae60', font=('Arial', 10, 'bold'))

        text_widget.config(state='disabled')

    def show_expense_chart(self):
        expenses = [t for t in self.transactions if t['type'] == 'expense']

        if not expenses:
            messagebox.showinfo("No Data", "No expense transactions to display!")
            return

        # Calculate expenses by category
        category_totals = defaultdict(float)
        for t in expenses:
            category_totals[t['category']] += t['amount']

        # Clear previous chart
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # Create pie chart
        categories = list(category_totals.keys())
        amounts = list(category_totals.values())
        colors = plt.cm.Set3(range(len(categories)))

        wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%',
                                           colors=colors, startangle=90)

        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('Expense Distribution by Category', fontsize=14, fontweight='bold')

        self.canvas.draw()

        # Switch to analytics tab
        self.notebook.select(2)

    def show_income_chart(self):
        incomes = [t for t in self.transactions if t['type'] == 'income']

        if not incomes:
            messagebox.showinfo("No Data", "No income transactions to display!")
            return

        # Calculate income by category
        category_totals = defaultdict(float)
        for t in incomes:
            category_totals[t['category']] += t['amount']

        # Clear previous chart
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # Create pie chart
        categories = list(category_totals.keys())
        amounts = list(category_totals.values())
        colors = plt.cm.Set2(range(len(categories)))

        wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%',
                                           colors=colors, startangle=90)

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('Income Distribution by Category', fontsize=14, fontweight='bold')

        self.canvas.draw()
        self.notebook.select(2)

    def show_monthly_trend(self):
        if not self.transactions:
            messagebox.showinfo("No Data", "No transactions to display!")
            return

        # Group by month
        monthly_income = defaultdict(float)
        monthly_expense = defaultdict(float)

        for t in self.transactions:
            month = t['date'][:7]  # YYYY-MM
            if t['type'] == 'income':
                monthly_income[month] += t['amount']
            else:
                monthly_expense[month] += t['amount']

        # Get all months and sort
        all_months = sorted(set(list(monthly_income.keys()) + list(monthly_expense.keys())))

        income_values = [monthly_income[m] for m in all_months]
        expense_values = [monthly_expense[m] for m in all_months]

        # Clear previous chart
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # Create bar chart
        x = range(len(all_months))
        width = 0.35

        ax.bar([i - width/2 for i in x], income_values, width, label='Income', color='#27ae60')
        ax.bar([i + width/2 for i in x], expense_values, width, label='Expense', color='#e74c3c')

        ax.set_xlabel('Month', fontweight='bold')
        ax.set_ylabel('Amount ($)', fontweight='bold')
        ax.set_title('Monthly Income vs Expense Trend', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(all_months, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw()
        self.notebook.select(2)

    def show_monthly_stats(self):
        stats_win = tk.Toplevel(self.root)
        stats_win.title("Monthly Statistics")
        stats_win.geometry("700x600")
        stats_win.configure(bg='white')

        tk.Label(stats_win, text="Monthly Financial Statistics",
                font=('Arial', 16, 'bold'), bg='white').pack(pady=20)

        # Create text widget
        text_frame = tk.Frame(stats_win, bg='white')
        text_frame.pack(fill='both', expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')

        text_widget = tk.Text(text_frame, font=('Courier', 10),
                             yscrollcommand=scrollbar.set, wrap='word')
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=text_widget.yview)

        # Group transactions by month
        monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0, 'count': 0})

        for t in self.transactions:
            month = t['date'][:7]
            if t['type'] == 'income':
                monthly_data[month]['income'] += t['amount']
            else:
                monthly_data[month]['expense'] += t['amount']
            monthly_data[month]['count'] += 1

        # Display statistics
        text_widget.insert('end', "Month      | Income    | Expense   | Balance   | Trans. Count\n")
        text_widget.insert('end', "-" * 70 + "\n")

        for month in sorted(monthly_data.keys(), reverse=True):
            data = monthly_data[month]
            balance = data['income'] - data['expense']

            line = f"{month}  | ${data['income']:8.2f} | ${data['expense']:8.2f} | ${balance:8.2f} | {data['count']:6d}\n"
            text_widget.insert('end', line)

        text_widget.config(state='disabled')

    def show_category_analysis(self):
        analysis_win = tk.Toplevel(self.root)
        analysis_win.title("Category Analysis")
        analysis_win.geometry("700x600")
        analysis_win.configure(bg='white')

        tk.Label(analysis_win, text="Category-wise Analysis",
                font=('Arial', 16, 'bold'), bg='white').pack(pady=20)

        # Create notebook for income and expense tabs
        notebook = ttk.Notebook(analysis_win)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)

        # Expense analysis
        expense_frame = tk.Frame(notebook, bg='white')
        notebook.add(expense_frame, text="Expenses")

        expense_text = tk.Text(expense_frame, font=('Courier', 10), wrap='word')
        expense_text.pack(fill='both', expand=True, padx=10, pady=10)

        expense_by_cat = defaultdict(lambda: {'total': 0, 'count': 0})
        for t in self.transactions:
            if t['type'] == 'expense':
                expense_by_cat[t['category']]['total'] += t['amount']
                expense_by_cat[t['category']]['count'] += 1

        total_expense = sum(data['total'] for data in expense_by_cat.values())

        expense_text.insert('end', "Category      | Total      | Count | Avg/Trans | % of Total\n")
        expense_text.insert('end', "-" * 70 + "\n")

        for category in sorted(expense_by_cat.keys(), key=lambda x: expense_by_cat[x]['total'], reverse=True):
            data = expense_by_cat[category]
            avg = data['total'] / data['count']
            percentage = (data['total'] / total_expense * 100) if total_expense > 0 else 0

            line = f"{category:13} | ${data['total']:9.2f} | {data['count']:5d} | ${avg:8.2f} | {percentage:5.1f}%\n"
            expense_text.insert('end', line)

        expense_text.insert('end', "-" * 70 + "\n")
        expense_text.insert('end', f"{'TOTAL':13} | ${total_expense:9.2f}\n")
        expense_text.config(state='disabled')

        # Income analysis
        income_frame = tk.Frame(notebook, bg='white')
        notebook.add(income_frame, text="Income")

        income_text = tk.Text(income_frame, font=('Courier', 10), wrap='word')
        income_text.pack(fill='both', expand=True, padx=10, pady=10)

        income_by_cat = defaultdict(lambda: {'total': 0, 'count': 0})
        for t in self.transactions:
            if t['type'] == 'income':
                income_by_cat[t['category']]['total'] += t['amount']
                income_by_cat[t['category']]['count'] += 1

        total_income = sum(data['total'] for data in income_by_cat.values())

        income_text.insert('end', "Category      | Total      | Count | Avg/Trans | % of Total\n")
        income_text.insert('end', "-" * 70 + "\n")

        for category in sorted(income_by_cat.keys(), key=lambda x: income_by_cat[x]['total'], reverse=True):
            data = income_by_cat[category]
            avg = data['total'] / data['count']
            percentage = (data['total'] / total_income * 100) if total_income > 0 else 0

            line = f"{category:13} | ${data['total']:9.2f} | {data['count']:5d} | ${avg:8.2f} | {percentage:5.1f}%\n"
            income_text.insert('end', line)

        income_text.insert('end', "-" * 70 + "\n")
        income_text.insert('end', f"{'TOTAL':13} | ${total_income:9.2f}\n")
        income_text.config(state='disabled')

    def export_json(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"wallet_export_{datetime.now().strftime('%Y%m%d')}.json"
        )
        if filename:
            try:
                data = {
                    'transactions': self.transactions,
                    'budgets': self.budgets,
                    'export_date': datetime.now().isoformat()
                }
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")

    def import_json(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    if 'transactions' in data:
                        self.transactions = data['transactions']
                    if 'budgets' in data:
                        self.budgets = data['budgets']

                    self.save_data()
                    self.update_all()
                    messagebox.showinfo("Success", "Data imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {str(e)}")

    def export_csv(self):
        if not self.transactions:
            messagebox.showwarning("No Data", "No transactions to export!")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"wallet_export_{datetime.now().strftime('%Y%m%d')}.csv"
        )

        if filename:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description', 'Timestamp'])

                    for t in sorted(self.transactions, key=lambda x: x['date']):
                        writer.writerow([
                            t['date'], t['type'], t['category'],
                            t['amount'], t['description'], t['timestamp']
                        ])

                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")

    def save_data(self):
        data = {
            'transactions': self.transactions,
            'budgets': self.budgets,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.transactions = data.get('transactions', [])
                    self.budgets = data.get('budgets', {})
            except:
                self.transactions = []
                self.budgets = {}

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedWallet(root)
    root.mainloop()
