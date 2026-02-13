import tkinter as tk
from tkinter import messagebox


class LimitsPage(tk.Frame):
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
            text="Custom Pour Limits",
            font=("Arial", 14, "bold"),
            bg="white",
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            main_frame,
            text="Set minimum and maximum pour amounts (ml) for each bottle.",
            font=("Arial", 10),
            bg="white",
            fg="#7f8c8d",
        ).pack(anchor="w", pady=(0, 20))

        self.limits_frame = tk.Frame(main_frame, bg="white")
        self.limits_frame.pack(fill="both", expand=True, pady=(0, 20))

        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(fill="x")

        tk.Button(
            btn_frame,
            text="Save All Limits",
            command=self._save_limits,
            bg="#27ae60",
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

        self.limit_entries = []

    def refresh(self):
        for widget in self.limits_frame.winfo_children():
            widget.destroy()

        self.limit_entries.clear()

        limits = self.database.get_all_limits()

        if not limits:
            tk.Label(
                self.limits_frame,
                text="No bottles with limits found. Add bottles first.",
                bg="white",
                fg="#e74c3c",
                font=("Arial", 11),
            ).pack(pady=20)
            return

        header = tk.Frame(self.limits_frame, bg="white")
        header.pack(fill="x", pady=(0, 10))

        tk.Label(
            header,
            text="Bottle",
            bg="white",
            font=("Arial", 11, "bold"),
            width=25,
            anchor="w",
        ).pack(side="left", padx=5)

        tk.Label(
            header,
            text="Min (ml)",
            bg="white",
            font=("Arial", 11, "bold"),
            width=10,
        ).pack(side="left", padx=5)

        tk.Label(
            header,
            text="Max (ml)",
            bg="white",
            font=("Arial", 11, "bold"),
            width=10,
        ).pack(side="left", padx=5)

        for limit in limits:
            row = tk.Frame(self.limits_frame, bg="white")
            row.pack(fill="x", pady=5)

            label_text = f"{limit['bottle_name']} (Pos {limit['position']})"
            tk.Label(
                row,
                text=label_text,
                bg="white",
                font=("Arial", 11),
                width=25,
                anchor="w",
            ).pack(side="left", padx=5)

            min_entry = tk.Entry(row, font=("Arial", 11), width=10)
            min_entry.pack(side="left", padx=5)
            min_entry.insert(0, str(limit["min_ml"]))

            max_entry = tk.Entry(row, font=("Arial", 11), width=10)
            max_entry.pack(side="left", padx=5)
            max_entry.insert(0, str(limit["max_ml"]))

            self.limit_entries.append(
                {
                    "bottle_id": limit["bottle_id"],
                    "min_entry": min_entry,
                    "max_entry": max_entry,
                }
            )

    def _save_limits(self):
        try:
            for entry_data in self.limit_entries:
                min_str = entry_data["min_entry"].get().strip()
                max_str = entry_data["max_entry"].get().strip()

                try:
                    min_ml = int(min_str)
                    max_ml = int(max_str)

                    if min_ml < 0 or max_ml < 0:
                        raise ValueError("Values cannot be negative")

                    if min_ml > max_ml:
                        raise ValueError("Min cannot be greater than max")

                except ValueError as e:
                    messagebox.showerror(
                        "Error",
                        f"Invalid values for bottle ID {entry_data['bottle_id']}:\n{e}",
                    )
                    return

                self.database.update_limit(entry_data["bottle_id"], min_ml, max_ml)

            messagebox.showinfo("Success", "All limits saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save limits:\n{e}")
