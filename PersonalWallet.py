import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

class BasicWallet:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Personal Wallet - Basic Version")
        self.window.geometry("800x550")
        self.window.config(bg="#f2f2f2")

        self.transactions = []
        self.balance = 0.0
        self.data_file = "wallet_data.json"

        self.setup_ui()
        self.load_data()
        self.update_display()

    def setup_ui(self):
        # ===== Balance Display =====
        balance_frame = tk.Frame(self.window, bg="#2e2e2e", height=80)
        balance_frame.pack(fill="x")
        self.balance_label = tk.Label(balance_frame,
                                      text="Current Balance: $0.00",
                                      font=("Segoe UI", 22, "bold"),
                                      fg="#00FF7F", bg="#2e2e2e")
        self.balance_label.pack(pady=20)

        # ===== Add Transaction Section =====
        form_frame = tk.LabelFrame(self.window, text="Add Transaction", font=("Segoe UI", 10, "bold"), bg="#f2f2f2")
        form_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(form_frame, text="Amount:", font=("Segoe UI", 10), bg="#f2f2f2").grid(row=0, column=0, padx=5, pady=8)
        self.amount_entry = ttk.Entry(form_frame, width=12)
        self.amount_entry.grid(row=0, column=1, padx=5)

        tk.Label(form_frame, text="Type:", font=("Segoe UI", 10), bg="#f2f2f2").grid(row=0, column=2, padx=5)
        self.type_var = tk.StringVar(value="income")
        self.type_menu = ttk.Combobox(form_frame, textvariable=self.type_var,
                                      values=["income", "expense"], width=10, state="readonly")
        self.type_menu.grid(row=0, column=3, padx=5)

        tk.Label(form_frame, text="Category:", font=("Segoe UI", 10), bg="#f2f2f2").grid(row=0, column=4, padx=5)
        self.category_entry = ttk.Entry(form_frame, width=15)
        self.category_entry.grid(row=0, column=5, padx=5)

        tk.Label(form_frame, text="Description:", font=("Segoe UI", 10), bg="#f2f2f2").grid(row=0, column=6, padx=5)
        self.desc_entry = ttk.Entry(form_frame, width=20)
        self.desc_entry.grid(row=0, column=7, padx=5)

        # ===== Buttons =====
        button_frame = tk.Frame(self.window, bg="#f2f2f2")
        button_frame.pack(pady=5)

        self.income_btn = tk.Button(button_frame, text="+ Add Income", bg="#4CAF50", fg="white",
                                    font=("Segoe UI", 10, "bold"), width=14, command=lambda: self.add_transaction("income"))
        self.income_btn.grid(row=0, column=0, padx=5, pady=5)

        self.expense_btn = tk.Button(button_frame, text="- Add Expense", bg="#E74C3C", fg="white",
                                     font=("Segoe UI", 10, "bold"), width=14, command=lambda: self.add_transaction("expense"))
        self.expense_btn.grid(row=0, column=1, padx=5, pady=5)

        self.clear_btn = tk.Button(button_frame, text="Clear Form", bg="#95A5A6", fg="white",
                                   font=("Segoe UI", 10, "bold"), width=12, command=self.clear_form)
        self.clear_btn.grid(row=0, column=2, padx=5, pady=5)

        # ===== Transaction History =====
        history_frame = tk.LabelFrame(self.window, text="Transaction History", font=("Segoe UI", 10, "bold"), bg="#f2f2f2")
        history_frame.pack(fill="both", expand=True, padx=15, pady=10)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)

        columns = ("amount", "type", "category", "description", "date")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("type", text="Type")
        self.tree.heading("category", text="Category")
        self.tree.heading("description", text="Description")
        self.tree.heading("date", text="Date")

        self.tree.column("amount", width=100, anchor="center")
        self.tree.column("type", width=90, anchor="center")
        self.tree.column("category", width=130, anchor="center")
        self.tree.column("description", width=200)
        self.tree.column("date", width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

    def add_transaction(self, type_):
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return

        if type_ == "expense":
            amount = -abs(amount)

        category = self.category_entry.get().strip() or "General"
        description = self.desc_entry.get().strip() or "No description"
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        transaction = {
            "amount": amount,
            "type": "Income" if amount > 0 else "Expense",
            "category": category,
            "description": description,
            "date": date
        }

        self.transactions.append(transaction)
        self.save_data()
        self.update_display()
        self.clear_form()

    def update_display(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.balance = sum(t["amount"] for t in self.transactions)
        color = "#00FF7F" if self.balance >= 0 else "#FF6347"
        self.balance_label.config(text=f"Current Balance: ${self.balance:,.2f}", fg=color)

        for t in reversed(self.transactions):
            self.tree.insert("", "end", values=(
                f"${t['amount']:,.2f}",
                t["type"],
                t["category"],
                t["description"],
                t["date"]
            ))

    def clear_form(self):
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.type_var.set("income")

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.transactions, f, indent=4)

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                self.transactions = json.load(f)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = BasicWallet()
    app.run()
