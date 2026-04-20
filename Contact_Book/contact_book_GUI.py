#!/usr/bin/env python3
"""
Project: Contact Book (GUI Version)
Tech: tkinter + ttkbootstrap

Key requirements covered:
1) Add contact (Name, Phone, Address, Email)
2) Persistent storage in JSON
3) View list of contacts (Treeview)
4) Delete contact by name (and/or selection)
5) Menu/options in GUI (buttons + menus)
6) Reject improper data (name with digits, phone non-digits, etc.)
7) Contacts stored in JSON file (default contacts.json)
8) Code commented for novices

New requirements for upgraded rubric:
- Load a different JSON file via file dialog OR command line argument
- Update an existing contact
- Descriptive comments (functions)
"""

import json
import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *


# -----------------------------
# Validation Helper Functions
# -----------------------------

def is_valid_name(name: str) -> bool:
    """
    Valid name rules:
    - Must not be empty
    - Must NOT contain digits
    - Allows letters, spaces, hyphens, apostrophes, periods
    """
    name = name.strip()
    if not name:
        return False
    if any(ch.isdigit() for ch in name):
        return False
    pattern = r"^[A-Za-z\s\-\.'’]+$"
    return re.match(pattern, name) is not None


def is_valid_phone(phone: str) -> bool:
    """
    Valid phone rules:
    - Digits only
    - Reasonable length (7 to 15 digits)
    """
    phone = phone.strip()
    if not phone.isdigit():
        return False
    return 7 <= len(phone) <= 15


def is_valid_email(email: str) -> bool:
    """
    Basic email validation (simple but decent for class projects).
    """
    email = email.strip()
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None


def normalize_name(name: str) -> str:
    """
    Standardize names for case-insensitive matching.
    """
    return name.strip().lower()


# -----------------------------
# JSON Storage Functions
# -----------------------------

def load_contacts_from_file(filepath: str) -> list:
    """
    Load contacts from a JSON file.
    Expected file format:
    [
      {"name": "...", "phone": "...", "address": "...", "email": "..."},
      ...
    ]

    Returns a list (empty if file missing or invalid).
    """
    if not filepath:
        return []

    if not os.path.exists(filepath):
        # If the user picked a new file path that doesn't exist yet,
        # we treat it as "no contacts" until saved.
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # Ensure each item is at least a dict
                return [x for x in data if isinstance(x, dict)]
            return []
    except json.JSONDecodeError:
        messagebox.showwarning(
            "Invalid JSON",
            "That file is not valid JSON (or is corrupted). Starting with an empty list."
        )
        return []
    except OSError as e:
        messagebox.showerror("File Error", f"Could not read file:\n{e}")
        return []


def save_contacts_to_file(filepath: str, contacts: list) -> bool:
    """
    Save the full contact list to disk.
    Returns True on success, False on failure.
    """
    if not filepath:
        return False
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=2)
        return True
    except OSError as e:
        messagebox.showerror("Save Error", f"Could not save file:\n{e}")
        return False


# -----------------------------
# GUI Application Class
# -----------------------------

class ContactBookGUI:
    """
    Encapsulates the entire GUI contact book.
    Keeps:
    - contacts list in memory (Python list of dicts)
    - current JSON file path (for saving/loading)
    - Treeview UI displaying contacts
    - Entry fields for CRUD actions
    """

    def __init__(self, root: tb.Window, initial_file: str):
        self.root = root
        self.root.title("Contact Book (GUI)")
        self.root.geometry("980x560")
        self.root.minsize(900, 520)

        # The currently-open JSON file path
        self.filepath = initial_file or "contacts.json"

        # In-memory list of contacts (list[dict])
        self.contacts = []

        # --- Build UI ---
        self._build_menu()
        self._build_layout()
        self._bind_events()

        # Load initial data (from default or command-line file)
        self.load_file(self.filepath)

    # -----------------------------
    # UI Construction
    # -----------------------------

    def _build_menu(self):
        """
        Creates the top menu bar with:
        - File -> Open JSON, Save, Save As, Exit
        """
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open JSON...", command=self.open_file_dialog)
        file_menu.add_command(label="Save", command=self.save_current_file)
        file_menu.add_command(label="Save As...", command=self.save_as_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def _build_layout(self):
        """
        Builds:
        - Left: contact list (Treeview) + search bar
        - Right: form (name/phone/email/address) + CRUD buttons
        - Bottom: status bar
        """
        outer = tb.Frame(self.root, padding=12)
        outer.pack(fill=BOTH, expand=True)

        outer.columnconfigure(0, weight=3)  # left panel
        outer.columnconfigure(1, weight=2)  # right panel
        outer.rowconfigure(0, weight=1)

        # -------------------------
        # LEFT PANEL (List + Search)
        # -------------------------
        left = tb.Labelframe(outer, text="Contacts", padding=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        # Search row
        search_row = tb.Frame(left)
        search_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        search_row.columnconfigure(1, weight=1)

        tb.Label(search_row, text="Search:").grid(row=0, column=0, sticky="w", padx=(0, 6))

        self.search_var = tk.StringVar()
        self.search_entry = tb.Entry(search_row, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew")

        self.search_btn = tb.Button(search_row, text="Find", bootstyle=INFO, command=self.search_contacts)
        self.search_btn.grid(row=0, column=2, padx=(8, 0))

        self.clear_search_btn = tb.Button(search_row, text="Clear", bootstyle=SECONDARY, command=self.clear_search)
        self.clear_search_btn.grid(row=0, column=3, padx=(8, 0))

        # Treeview for contacts
        columns = ("name", "phone", "email", "address")
        self.tree = tb.Treeview(left, columns=columns, show="headings", height=16)
        self.tree.grid(row=1, column=0, sticky="nsew")

        self.tree.heading("name", text="Name")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("email", text="Email")
        self.tree.heading("address", text="Address")

        self.tree.column("name", width=180, anchor="w")
        self.tree.column("phone", width=110, anchor="w")
        self.tree.column("email", width=200, anchor="w")
        self.tree.column("address", width=350, anchor="w")

        # Add scrollbar for the Treeview
        scrollbar = tb.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")

        # -------------------------
        # RIGHT PANEL (Form + Buttons)
        # -------------------------
        right = tb.Labelframe(outer, text="Contact Details", padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)

        # Form fields
        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()

        tb.Label(right, text="Name:").grid(row=0, column=0, sticky="w", pady=6)
        self.name_entry = tb.Entry(right, textvariable=self.name_var)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=6)

        tb.Label(right, text="Phone:").grid(row=1, column=0, sticky="w", pady=6)
        self.phone_entry = tb.Entry(right, textvariable=self.phone_var)
        self.phone_entry.grid(row=1, column=1, sticky="ew", pady=6)

        tb.Label(right, text="Email:").grid(row=2, column=0, sticky="w", pady=6)
        self.email_entry = tb.Entry(right, textvariable=self.email_var)
        self.email_entry.grid(row=2, column=1, sticky="ew", pady=6)

        tb.Label(right, text="Address:").grid(row=3, column=0, sticky="nw", pady=6)
        self.address_text = tk.Text(right, height=6, wrap="word")
        self.address_text.grid(row=3, column=1, sticky="ew", pady=6)

        # Button row
        btn_frame = tb.Frame(right)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        btn_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.add_btn = tb.Button(btn_frame, text="Add", bootstyle=SUCCESS, command=self.add_contact)
        self.add_btn.grid(row=0, column=0, sticky="ew", padx=4)

        self.update_btn = tb.Button(btn_frame, text="Update", bootstyle=WARNING, command=self.update_contact)
        self.update_btn.grid(row=0, column=1, sticky="ew", padx=4)

        self.delete_btn = tb.Button(btn_frame, text="Delete", bootstyle=DANGER, command=self.delete_contact)
        self.delete_btn.grid(row=0, column=2, sticky="ew", padx=4)

        self.clear_btn = tb.Button(btn_frame, text="Clear Form", bootstyle=SECONDARY, command=self.clear_form)
        self.clear_btn.grid(row=0, column=3, sticky="ew", padx=4)

        # Extra help text
        help_box = tb.Label(
            right,
            text=(
                "Tips:\n"
                "- Click a contact in the list to load it into the form.\n"
                "- Update edits the selected contact.\n"
                "- Delete removes the selected contact (or deletes by matching Name if none selected)."
            ),
            justify="left"
        )
        help_box.grid(row=5, column=0, columnspan=2, sticky="w", pady=(14, 0))

        # -------------------------
        # STATUS BAR (Bottom)
        # -------------------------
        self.status_var = tk.StringVar(value="Ready.")
        status = tb.Label(self.root, textvariable=self.status_var, anchor="w", padding=8)
        status.pack(fill="x")

    def _bind_events(self):
        """
        Binds UI events:
        - Selecting a Treeview row loads that contact into the form
        - Enter key in search triggers search
        """
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.search_entry.bind("<Return>", lambda e: self.search_contacts())

    # -----------------------------
    # File / Load / Save Actions
    # -----------------------------

    def load_file(self, filepath: str):
        """
        Loads contacts from the given JSON file path and refreshes the UI.
        """
        self.filepath = filepath
        self.contacts = load_contacts_from_file(filepath)
        self.refresh_treeview()
        self.set_status(f"Loaded {len(self.contacts)} contact(s) from: {self.filepath}")

    def open_file_dialog(self):
        """
        Opens a file dialog so the user can choose a JSON file to load.
        This satisfies the 'load different json file' requirement.
        """
        path = filedialog.askopenfilename(
            title="Open contacts JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.load_file(path)

    def save_current_file(self):
        """
        Saves the in-memory contacts list back to the current file path.
        """
        ok = save_contacts_to_file(self.filepath, self.contacts)
        if ok:
            self.set_status(f"Saved {len(self.contacts)} contact(s) to: {self.filepath}")

    def save_as_dialog(self):
        """
        Allows saving to a new JSON file path (useful if instructor tests multiple files).
        """
        path = filedialog.asksaveasfilename(
            title="Save contacts JSON as...",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.filepath = path
            self.save_current_file()

    # -----------------------------
    # Contact CRUD Operations
    # -----------------------------

    def get_form_data(self) -> dict:
        """
        Reads the GUI form fields and returns a contact dict.
        """
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        address = self.address_text.get("1.0", "end").strip()

        return {
            "name": name,
            "phone": phone,
            "email": email,
            "address": address
        }

    def validate_contact(self, contact: dict) -> bool:
        """
        Ensures contact data is valid.
        If invalid, shows a messagebox and returns False.
        """
        if not is_valid_name(contact["name"]):
            messagebox.showerror("Invalid Name", "Name must be letters/spaces only (no numbers).")
            return False

        if not is_valid_phone(contact["phone"]):
            messagebox.showerror("Invalid Phone", "Phone must be digits only (length 7–15).")
            return False

        if not is_valid_email(contact["email"]):
            messagebox.showerror("Invalid Email", "Please enter a valid email (example: name@example.com).")
            return False

        # Address can be empty, but you can enforce it if you want:
        # if not contact["address"]:
        #     messagebox.showerror("Invalid Address", "Address cannot be empty.")
        #     return False

        return True

    def add_contact(self):
        """
        Adds a new contact:
        - Validate inputs
        - Prevent duplicate name (case-insensitive)
        - Append and save
        """
        contact = self.get_form_data()
        if not self.validate_contact(contact):
            return

        new_key = normalize_name(contact["name"])
        for c in self.contacts:
            if normalize_name(c.get("name", "")) == new_key:
                messagebox.showerror("Duplicate Name", "A contact with that name already exists.")
                return

        self.contacts.append(contact)
        self.save_current_file()
        self.refresh_treeview()
        self.clear_form()
        self.set_status(f"Added contact: {contact['name']}")

    def update_contact(self):
        """
        Updates the selected contact (or tries to match by name if nothing selected):
        - Validate inputs
        - Find target contact
        - Replace its fields
        - Save
        """
        contact = self.get_form_data()
        if not self.validate_contact(contact):
            return

        selected_index = self.get_selected_contact_index()

        if selected_index is None:
            # If nothing selected, fallback to exact name match (requirement style: update by name)
            idx = self.find_exact_name_index(contact["name"])
            if idx is None:
                messagebox.showerror("Update Failed", "No contact selected and no exact name match found.")
                return
            selected_index = idx

        # If user changed the name, ensure it won't collide with another contact
        target_name_key = normalize_name(contact["name"])
        for i, c in enumerate(self.contacts):
            if i != selected_index and normalize_name(c.get("name", "")) == target_name_key:
                messagebox.showerror("Duplicate Name", "Another contact already has that name.")
                return

        # Perform the update
        self.contacts[selected_index] = contact

        self.save_current_file()
        self.refresh_treeview()
        self.set_status(f"Updated contact: {contact['name']}")

    def delete_contact(self):
        """
        Deletes a contact:
        - If a row is selected: delete that contact
        - Else: delete by exact name match from the Name field
        This satisfies "delete by name" while also being usable as a GUI.
        """
        selected_index = self.get_selected_contact_index()

        if selected_index is None:
            # Delete by exact name match from the form name field
            name = self.name_var.get().strip()
            if not name:
                messagebox.showerror("Delete Failed", "Select a contact or type an exact Name to delete.")
                return

            idx = self.find_exact_name_index(name)
            if idx is None:
                messagebox.showerror("Delete Failed", "No contact found with that exact name.")
                return

            selected_index = idx

        victim = self.contacts[selected_index]
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete contact:\n\n{victim.get('name','')}\n{victim.get('phone','')}\n{victim.get('email','')}?"
        )
        if not confirm:
            return

        self.contacts.pop(selected_index)
        self.save_current_file()
        self.refresh_treeview()
        self.clear_form()
        self.set_status(f"Deleted contact: {victim.get('name','')}")

    # -----------------------------
    # Search / Selection / UI Helpers
    # -----------------------------

    def refresh_treeview(self, show_contacts: list | None = None):
        """
        Clears and repopulates the Treeview.
        If show_contacts is provided, display those instead of all contacts (used by search).
        """
        # Remove all rows from Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = show_contacts if show_contacts is not None else self.contacts

        # Insert contacts
        for i, c in enumerate(data):
            self.tree.insert(
                "",
                "end",
                iid=str(i),  # store index as string id
                values=(
                    c.get("name", ""),
                    c.get("phone", ""),
                    c.get("email", ""),
                    c.get("address", "")
                )
            )

    def on_tree_select(self, event=None):
        """
        When user clicks a row, load it into the form fields.
        """
        idx = self.get_selected_contact_index()
        if idx is None:
            return

        # IMPORTANT:
        # Treeview row indexes match the currently displayed data.
        # If we were showing a filtered list, iid indexes would differ.
        # To keep it simple, we only use selection loading reliably when showing full list.
        #
        # So: if you want selection to work with filtered lists,
        # you’d store a stable unique ID per contact. Not required for this class.
        if self.is_filtered_view_active():
            messagebox.showinfo(
                "Selection Note",
                "Selection-to-form is disabled while filtered search is active.\n"
                "Click Clear to return to full list, then select."
            )
            self.tree.selection_remove(self.tree.selection())
            return

        contact = self.contacts[idx]
        self.populate_form(contact)

    def populate_form(self, contact: dict):
        """
        Writes a contact dict into the GUI form fields.
        """
        self.name_var.set(contact.get("name", ""))
        self.phone_var.set(contact.get("phone", ""))
        self.email_var.set(contact.get("email", ""))
        self.address_text.delete("1.0", "end")
        self.address_text.insert("1.0", contact.get("address", ""))

    def clear_form(self):
        """
        Clears the form fields.
        """
        self.name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_text.delete("1.0", "end")
        self.tree.selection_remove(self.tree.selection())
        self.set_status("Form cleared.")

    def search_contacts(self):
        """
        Filters the Treeview to show contacts whose name contains the search text.
        Satisfies the 'search by name' requirement.
        """
        query = self.search_var.get().strip()
        if not query:
            messagebox.showerror("Search", "Type a name (or partial name) to search.")
            return

        key = normalize_name(query)
        matches = [c for c in self.contacts if key in normalize_name(c.get("name", ""))]

        self.refresh_treeview(show_contacts=matches)
        self.set_status(f"Search '{query}' -> {len(matches)} match(es). (Click Clear to show all)")

        # Mark that we are currently showing a filtered list
        self._filtered_view = True

    def clear_search(self):
        """
        Clears search and restores full contact list.
        """
        self.search_var.set("")
        self.refresh_treeview()
        self._filtered_view = False
        self.set_status("Search cleared. Showing all contacts.")

    def is_filtered_view_active(self) -> bool:
        """
        Returns True if the Treeview is currently showing filtered search results.
        """
        return getattr(self, "_filtered_view", False)

    def get_selected_contact_index(self):
        """
        Returns the selected contact index (int) if a row is selected.
        Otherwise returns None.
        """
        selection = self.tree.selection()
        if not selection:
            return None
        try:
            return int(selection[0])
        except ValueError:
            return None

    def find_exact_name_index(self, name: str):
        """
        Finds a contact index by exact name match (case-insensitive).
        Returns index int or None.
        """
        key = normalize_name(name)
        for i, c in enumerate(self.contacts):
            if normalize_name(c.get("name", "")) == key:
                return i
        return None

    def set_status(self, msg: str):
        """
        Updates the status bar text.
        """
        self.status_var.set(msg)


# -----------------------------
# Main Entrypoint
# -----------------------------

def main():
    """
    Startup logic:
    - If user passes a JSON file path via command line, try to load it.
      Example:
        python contact_book_gui.py my_contacts.json
    - Otherwise default to contacts.json in current directory.
    """
    # Determine initial file path
    initial_file = "contacts.json"
    if len(sys.argv) >= 2:
        initial_file = sys.argv[1]

    # ttkbootstrap window (modern themed Tk)
    root = tb.Window(themename="flatly")  # try: "flatly", "cyborg", "superhero", "minty", etc.
    app = ContactBookGUI(root, initial_file)
    root.mainloop()


if __name__ == "__main__":
    main()