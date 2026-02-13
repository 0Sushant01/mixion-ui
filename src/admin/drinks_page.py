import tkinter as tk
from tkinter import messagebox, ttk


class DrinksPage(tk.Frame):
    def __init__(self, parent, database):
        super().__init__(parent, bg="white")
        self.database = database
        self._create_ui()
        self.refresh()

    def _create_ui(self):
        list_frame = tk.Frame(self, bg="white")
        list_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            list_frame,
            text="Drinks",
            font=("Arial", 14, "bold"),
            bg="white",
        ).pack(anchor="w", pady=(0, 10))

        columns = ("ID", "Name", "Price", "Active")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(fill="both", expand=True)

        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        tk.Button(
            btn_frame,
            text="Add Drink",
            command=self._add_drink,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Edit Selected",
            command=self._edit_drink,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Delete Selected",
            command=self._delete_drink,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Refresh",
            command=self.refresh,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
        ).pack(side="right", padx=5)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        drinks = self.database.get_all_drinks()
        for drink in drinks:
            active = "Yes" if drink["active"] else "No"
            self.tree.insert(
                "",
                "end",
                values=(drink["id"], drink["name"], drink["price"], active),
            )

    def _add_drink(self):
        dialog = DrinkDialog(self, self.database, mode="add")
        self.wait_window(dialog)
        self.refresh()

    def _edit_drink(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a drink to edit")
            return

        item = self.tree.item(selection[0])
        drink_id = item["values"][0]

        drinks = self.database.get_all_drinks()
        drink = next((d for d in drinks if d["id"] == drink_id), None)

        if drink:
            dialog = DrinkDialog(self, self.database, mode="edit", drink=drink)
            self.wait_window(dialog)
            self.refresh()

    def _delete_drink(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a drink to delete")
            return

        item = self.tree.item(selection[0])
        drink_id = item["values"][0]

        if messagebox.askyesno("Confirm Delete", "Delete this drink and its recipes?"):
            try:
                self.database.delete_drink(drink_id)
                messagebox.showinfo("Success", "Drink deleted")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete drink:\n{e}")


class DrinkDialog(tk.Toplevel):
    def __init__(self, parent, database, mode="add", drink=None):
        super().__init__(parent)
        self.database = database
        self.mode = mode
        self.drink = drink

        self.title("Add Drink" if mode == "add" else "Edit Drink")
        self.geometry("400x250")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_ui()

    def _create_ui(self):
        frame = tk.Frame(self, bg="white", padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Name:", bg="white", font=("Arial", 11)).grid(
            row=0, column=0, sticky="w", pady=10
        )
        self.name_entry = tk.Entry(frame, font=("Arial", 11), width=25)
        self.name_entry.grid(row=0, column=1, pady=10)

        tk.Label(frame, text="Price:", bg="white", font=("Arial", 11)).grid(
            row=1, column=0, sticky="w", pady=10
        )
        self.price_entry = tk.Entry(frame, font=("Arial", 11), width=25)
        self.price_entry.grid(row=1, column=1, pady=10)

        tk.Label(frame, text="Active:", bg="white", font=("Arial", 11)).grid(
            row=2, column=0, sticky="w", pady=10
        )
        self.active_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, variable=self.active_var, bg="white").grid(
            row=2, column=1, sticky="w", pady=10
        )

        if self.mode == "edit" and self.drink:
            self.name_entry.insert(0, self.drink["name"])
            self.price_entry.insert(0, str(self.drink["price"]))
            self.active_var.set(bool(self.drink["active"]))

        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        tk.Button(
            btn_frame,
            text="Save",
            command=self._save,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
        ).pack(side="left", padx=10)

    def _save(self):
        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Name is required")
            return

        try:
            price = int(price_str)
            if price < 0:
                raise ValueError("Price cannot be negative")
        except ValueError:
            messagebox.showerror("Error", "Price must be a non-negative integer")
            return

        active = 1 if self.active_var.get() else 0

        try:
            if self.mode == "add":
                self.database.add_drink(name, price, active)
                messagebox.showinfo("Success", "Drink added")
            else:
                self.database.update_drink(self.drink["id"], name, price, active)
                messagebox.showinfo("Success", "Drink updated")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")
