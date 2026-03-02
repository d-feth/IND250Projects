#!/usr/bin/env python3
"""
Project 2: Contact Book (Console Version)

Features (CRUD):
- Create: Add a contact (Name, Phone, Address, Email)
- Read:   View all contacts
- Update: (Not required in MVP list, but CRUD mentions it. This version omits Update.)
- Delete: Delete a contact by name
- Search: Find a contact by name

Persistent Storage:
- Contacts are stored in a JSON file named "contacts.json"
"""

import json
import os
import re


# The JSON file we will use for saving contacts permanently
DATA_FILE = "contacts.json"


# -----------------------------
# Validation Helper Functions
# -----------------------------

def is_valid_name(name: str) -> bool:
    """
    A valid name must NOT contain any digits.
    We'll allow letters, spaces, hyphens, and apostrophes.
    Examples allowed: "John", "Mary Jane", "O'Neil", "Anne-Marie"
    """
    name = name.strip()
    if not name:
        return False

    # Reject if any digit exists
    if any(ch.isdigit() for ch in name):
        return False

    # Optional: ensure it's mostly "name-like"
    # This regex allows letters, spaces, hyphen, apostrophe, and periods
    pattern = r"^[A-Za-z\s\-\.'’]+$"
    return re.match(pattern, name) is not None


def is_valid_phone(phone: str) -> bool:
    """
    Phone must contain digits only (no spaces, dashes, parentheses, etc.)
    Also require a reasonable length (e.g., 7 to 15 digits).
    """
    phone = phone.strip()
    if not phone.isdigit():
        return False
    return 7 <= len(phone) <= 15


def is_valid_email(email: str) -> bool:
    """
    Basic email check (not perfect, but good for this assignment).
    Must contain one '@' and a dot after it with some characters.
    """
    email = email.strip()
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None


# -----------------------------
# JSON Storage Functions
# -----------------------------

def load_contacts() -> list:
    """
    Loads contacts from DATA_FILE.

    Returns:
        A list of contact dictionaries. Example:
        [
          {"name": "Alice", "phone": "1234567890", "address": "...", "email": "..."},
          ...
        ]

    If the file doesn't exist yet, return an empty list.
    If the file exists but is corrupted, we warn and return an empty list.
    """
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # If someone manually edited the file to something unexpected,
            # we ensure we still return a list.
            if isinstance(data, list):
                return data
            else:
                print("Warning: contacts.json structure is not a list. Starting fresh.")
                return []
    except json.JSONDecodeError:
        print("Warning: contacts.json is not valid JSON (file may be corrupted). Starting fresh.")
        return []
    except OSError as e:
        print(f"Warning: Could not read {DATA_FILE}: {e}. Starting fresh.")
        return []


def save_contacts(contacts: list) -> None:
    """
    Saves the full contacts list to DATA_FILE in JSON format.
    We use indent=2 so the file is easy to read for beginners.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=2)
    except OSError as e:
        print(f"Error: Could not save contacts to {DATA_FILE}: {e}")


# -----------------------------
# Core App Functions
# -----------------------------

def display_menu() -> None:
    """
    Prints the main menu options.
    Requirement #5: options are displayed in a menu to the user.
    """
    print("\n--- Contact Book ---")
    print("1) Add contact")
    print("2) View all contacts")
    print("3) Search contact by name")
    print("4) Delete contact by name")
    print("5) Exit")


def normalize_name(name: str) -> str:
    """
    Normalizes a name for matching.
    Example: "  aLiCe  " becomes "alice"
    This lets search/delete work regardless of capitalization.
    """
    return name.strip().lower()


def add_contact(contacts: list) -> None:
    """
    Adds a contact after validating inputs.
    Requirement #1 and #6.
    """
    print("\nAdd Contact")
    name = input("Name: ").strip()

    if not is_valid_name(name):
        print("Error: Please enter a valid name (letters/spaces only; no numbers).")
        return

    phone = input("Phone (digits only): ").strip()
    if not is_valid_phone(phone):
        print("Error: Please enter a valid phone number (digits only, length 7-15).")
        return

    address = input("Address: ").strip()
    # Address can be flexible; not required to validate heavily.

    email = input("Email: ").strip()
    if not is_valid_email(email):
        print("Error: Please enter a valid email address (example: name@example.com).")
        return

    # OPTIONAL: Prevent exact duplicate names (many contact books do).
    # If you want to allow duplicate names, remove this block.
    new_key = normalize_name(name)
    for c in contacts:
        if normalize_name(c.get("name", "")) == new_key:
            print("Error: A contact with that name already exists. Use a different name.")
            return

    # Create the new contact dictionary
    contact = {
        "name": name,
        "phone": phone,
        "address": address,
        "email": email
    }

    # Add to our in-memory list and then save to JSON
    contacts.append(contact)
    save_contacts(contacts)

    print(f"Saved contact: {name}")


def view_contacts(contacts: list) -> None:
    """
    Displays all contacts.
    Requirement #2.
    """
    print("\nAll Contacts")

    if not contacts:
        print("(No contacts saved.)")
        return

    # Print in a nice readable format
    for i, c in enumerate(contacts, start=1):
        print(f"\nContact #{i}")
        print(f"  Name:    {c.get('name', '')}")
        print(f"  Phone:   {c.get('phone', '')}")
        print(f"  Address: {c.get('address', '')}")
        print(f"  Email:   {c.get('email', '')}")


def search_contact(contacts: list) -> None:
    """
    Search contacts by name.
    Requirement #4.
    """
    print("\nSearch Contact")
    query = input("Enter name to search: ").strip()

    if not query:
        print("Error: Please enter a name to search.")
        return

    key = normalize_name(query)

    # Find all contacts whose name matches or contains the search term
    matches = []
    for c in contacts:
        contact_name = normalize_name(c.get("name", ""))
        if key in contact_name:
            matches.append(c)

    if not matches:
        print("No matching contacts found.")
        return

    print(f"\nFound {len(matches)} match(es):")
    for c in matches:
        print("\n---")
        print(f"Name:    {c.get('name', '')}")
        print(f"Phone:   {c.get('phone', '')}")
        print(f"Address: {c.get('address', '')}")
        print(f"Email:   {c.get('email', '')}")


def delete_contact(contacts: list) -> None:
    """
    Deletes a contact by (exact) name match (case-insensitive).
    Requirement #3.
    """
    print("\nDelete Contact")
    name_to_delete = input("Enter the EXACT name to delete: ").strip()

    if not name_to_delete:
        print("Error: Please enter a name to delete.")
        return

    key = normalize_name(name_to_delete)

    # Find the index of the matching contact
    index_to_remove = None
    for i, c in enumerate(contacts):
        if normalize_name(c.get("name", "")) == key:
            index_to_remove = i
            break

    if index_to_remove is None:
        print("No contact found with that exact name.")
        return

    removed = contacts.pop(index_to_remove)
    save_contacts(contacts)
    print(f"Deleted contact: {removed.get('name', '')}")


# -----------------------------
# Main Program Loop
# -----------------------------

def main() -> None:
    """
    Runs the menu loop until the user chooses Exit.
    """
    # Load existing contacts from the JSON file (persistent storage)
    contacts = load_contacts()

    while True:
        display_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_contact(contacts)
        elif choice == "2":
            view_contacts(contacts)
        elif choice == "3":
            search_contact(contacts)
        elif choice == "4":
            delete_contact(contacts)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Error: Please choose a valid option (1-5).")


if __name__ == "__main__":
    main()