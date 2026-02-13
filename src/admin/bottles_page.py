import tkinter as tk
from tkinter import messagebox, ttk


class BottlesPage(tk.Frame):
    def __init__(self, parent, database):
        super().__init__(parent, bg="white")
        self.database = database
        self._create_ui()
        self.refresh()

    def _create_ui(self):
        # List section
        list_frame = tk.Frame(self, bg="white")
        list_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            list_frame,
            text="Bottles",
            font=("Arial", 14, "bold"),
            bg="white",
        ).pack(anchor="w", pady=(0, 10))

        # Table
        columns = ("ID", "Position", "Name", "Enabled")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        tk.Button(
            btn_frame,
            text="Add Bottle",
            command=self._add_bottle,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Edit Selected",
            command=self._edit_bottle,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Delete Selected",
            command=self._delete_bottle,
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

        bottles = self.database.get_all_bottles()
        for bottle in bottles:
            enabled = "Yes" if bottle["enabled"] else "No"
            self.tree.insert(
                "",
                "end",
                values=(bottle["id"], bottle["position"], bottle["name"], enabled),
            )

    def _add_bottle(self):
        dialog = BottleDialog(self, self.database, mode="add")
        self.wait_window(dialog)
        self.refresh()

    def _edit_bottle(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a bottle to edit")
            return

        item = self.tree.item(selection[0])
        bottle_id = item["values"][0]

        bottles = self.database.get_all_bottles()
        bottle = next((b for b in bottles if b["id"] == bottle_id), None)

        if bottle:
            dialog = BottleDialog(self, self.database, mode="edit", bottle=bottle)
            self.wait_window(dialog)
            self.refresh()

    def _delete_bottle(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a bottle to delete")
            return

        item = self.tree.item(selection[0])
        bottle_id = item["values"][0]

        if messagebox.askyesno("Confirm Delete", "Delete this bottle?"):
            try:
                self.database.delete_bottle(bottle_id)
                messagebox.showinfo("Success", "Bottle deleted")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete bottle:\n{e}")


class BottleDialog(tk.Toplevel):
    def __init__(self, parent, database, mode="add", bottle=None):
        super().__init__(parent)
        self.database = database
        self.mode = mode
        self.bottle = bottle

        self.title("Add Bottle" if mode == "add" else "Edit Bottle")
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

        tk.Label(frame, text="Position:", bg="white", font=("Arial", 11)).grid(
            row=1, column=0, sticky="w", pady=10
        )
        self.position_entry = tk.Entry(frame, font=("Arial", 11), width=25)
        self.position_entry.grid(row=1, column=1, pady=10)

        tk.Label(frame, text="Enabled:", bg="white", font=("Arial", 11)).grid(
            row=2, column=0, sticky="w", pady=10
        )
        self.enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, variable=self.enabled_var, bg="white").grid(
            row=2, column=1, sticky="w", pady=10
        )

        if self.mode == "edit" and self.bottle:
            self.name_entry.insert(0, self.bottle["name"])
            self.position_entry.insert(0, str(self.bottle["position"]))
            self.enabled_var.set(bool(self.bottle["enabled"]))

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
        position_str = self.position_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Name is required")
            return

        try:
            position = int(position_str)
            if position < 1:
                raise ValueError("Position must be >= 1")
        except ValueError:
            messagebox.showerror("Error", "Position must be a positive integer")
            return

        enabled = 1 if self.enabled_var.get() else 0

        try:
            if self.mode == "add":
                self.database.add_bottle(name, position)
                messagebox.showinfo("Success", "Bottle added")
            else:
                self.database.update_bottle(self.bottle["id"], name, position, enabled)
                messagebox.showinfo("Success", "Bottle updated")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")
