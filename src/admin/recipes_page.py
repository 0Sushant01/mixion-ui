import tkinter as tk
from tkinter import messagebox, ttk


class RecipesPage(tk.Frame):
    def __init__(self, parent, database):
        super().__init__(parent, bg="white")
        self.database = database
        self._create_ui()
        self.refresh()

    def _create_ui(self):
        main_frame = tk.Frame(self, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            main_frame,
            text="Drink Recipes",
            font=("Arial", 14, "bold"),
            bg="white",
        ).pack(anchor="w", pady=(0, 10))

        # Drink selection
        select_frame = tk.Frame(main_frame, bg="white")
        select_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            select_frame,
            text="Select Drink:",
            bg="white",
            font=("Arial", 11),
        ).pack(side="left", padx=(0, 10))

        self.drink_var = tk.StringVar()
        self.drink_combo = ttk.Combobox(
            select_frame,
            textvariable=self.drink_var,
            state="readonly",
            width=30,
            font=("Arial", 11),
        )
        self.drink_combo.pack(side="left", padx=(0, 10))
        self.drink_combo.bind("<<ComboboxSelected>>", self._on_drink_selected)

        tk.Button(
            select_frame,
            text="Load Recipe",
            command=self._load_recipe,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
        ).pack(side="left")

        # Recipe editor
        editor_frame = tk.LabelFrame(
            main_frame,
            text="Recipe Editor",
            bg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15,
        )
        editor_frame.pack(fill="both", expand=True, pady=(0, 20))

        self.bottle_entries = []
        self.bottle_labels = []

        # Buttons
        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(fill="x")

        tk.Button(
            btn_frame,
            text="Save Recipe",
            command=self._save_recipe,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Clear Recipe",
            command=self._clear_recipe,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Refresh",
            command=self.refresh,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
        ).pack(side="right", padx=5)

        self.editor_frame_ref = editor_frame

    def refresh(self):
        self._load_drinks()
        self._load_bottles()

    def _load_drinks(self):
        drinks = self.database.get_all_drinks()
        self.drinks_map = {f"{d['name']} (ID: {d['id']})": d for d in drinks}
        self.drink_combo["values"] = list(self.drinks_map.keys())

    def _load_bottles(self):
        for widget in self.editor_frame_ref.winfo_children():
            widget.destroy()

        self.bottle_entries.clear()
        self.bottle_labels.clear()

        bottles = self.database.get_all_bottles()

        if not bottles:
            tk.Label(
                self.editor_frame_ref,
                text="No bottles configured. Add bottles first.",
                bg="white",
                fg="#e74c3c",
                font=("Arial", 11),
            ).pack(pady=20)
            return

        for idx, bottle in enumerate(bottles):
            row = tk.Frame(self.editor_frame_ref, bg="white")
            row.pack(fill="x", pady=5)

            label_text = f"{bottle['name']} (Pos {bottle['position']}):"
            label = tk.Label(
                row,
                text=label_text,
                bg="white",
                font=("Arial", 11),
                width=25,
                anchor="w",
            )
            label.pack(side="left", padx=(0, 10))

            entry = tk.Entry(row, font=("Arial", 11), width=10)
            entry.pack(side="left")
            entry.insert(0, "0")

            tk.Label(row, text="ml", bg="white", font=("Arial", 11)).pack(
                side="left", padx=(5, 0)
            )

            self.bottle_entries.append((bottle["id"], entry))
            self.bottle_labels.append(label)

    def _on_drink_selected(self, event=None):
        self._load_recipe()

    def _load_recipe(self):
        selected = self.drink_var.get()
        if not selected or selected not in self.drinks_map:
            messagebox.showwarning("No Selection", "Please select a drink")
            return

        drink = self.drinks_map[selected]
        recipes = self.database.get_recipes_for_drink(drink["id"])

        recipe_map = {r["bottle_id"]: r["amount_ml"] for r in recipes}

        for bottle_id, entry in self.bottle_entries:
            amount = recipe_map.get(bottle_id, 0)
            entry.delete(0, tk.END)
            entry.insert(0, str(amount))

    def _save_recipe(self):
        selected = self.drink_var.get()
        if not selected or selected not in self.drinks_map:
            messagebox.showwarning("No Selection", "Please select a drink")
            return

        drink = self.drinks_map[selected]

        try:
            for bottle_id, entry in self.bottle_entries:
                amount_str = entry.get().strip()
                try:
                    amount = int(amount_str)
                    if amount < 0:
                        raise ValueError()
                except ValueError:
                    messagebox.showerror(
                        "Error",
                        f"Invalid amount for bottle ID {bottle_id}. Must be >= 0.",
                    )
                    return

                self.database.set_recipe(drink["id"], bottle_id, amount)

            messagebox.showinfo("Success", f"Recipe saved for {drink['name']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save recipe:\n{e}")

    def _clear_recipe(self):
        selected = self.drink_var.get()
        if not selected or selected not in self.drinks_map:
            messagebox.showwarning("No Selection", "Please select a drink")
            return

        drink = self.drinks_map[selected]

        if messagebox.askyesno(
            "Confirm Clear", f"Clear all recipe data for {drink['name']}?"
        ):
            try:
                self.database.delete_all_recipes_for_drink(drink["id"])
                for _, entry in self.bottle_entries:
                    entry.delete(0, tk.END)
                    entry.insert(0, "0")
                messagebox.showinfo("Success", "Recipe cleared")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear recipe:\n{e}")
