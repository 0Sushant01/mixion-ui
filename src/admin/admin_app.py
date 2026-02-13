import tkinter as tk
from tkinter import ttk

from src.admin.bottles_page import BottlesPage
from src.admin.drinks_page import DrinksPage
from src.admin.limits_page import LimitsPage
from src.admin.recipes_page import RecipesPage


class AdminApp(tk.Tk):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.title("Mixion Database Manager")
        self.geometry("900x600")
        self.configure(bg="#f0f0f0")

        self._create_header()
        self._create_tabs()

    def _create_header(self):
        header = tk.Frame(self, bg="#2c3e50", height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="Mixion Database Manager",
            fg="white",
            bg="#2c3e50",
            font=("Arial", 18, "bold"),
        )
        title.pack(pady=15)

    def _create_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.bottles_page = BottlesPage(notebook, self.database)
        self.drinks_page = DrinksPage(notebook, self.database)
        self.recipes_page = RecipesPage(notebook, self.database)
        self.limits_page = LimitsPage(notebook, self.database)

        notebook.add(self.bottles_page, text="Bottles")
        notebook.add(self.drinks_page, text="Drinks")
        notebook.add(self.recipes_page, text="Recipes")
        notebook.add(self.limits_page, text="Custom Limits")

    def refresh_all(self):
        self.bottles_page.refresh()
        self.drinks_page.refresh()
        self.recipes_page.refresh()
        self.limits_page.refresh()

    def run(self):
        self.mainloop()
