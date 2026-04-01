"""
Project 5: GUI Tip Tool
Analog Gear Style Version

This program creates a graphical tip calculator using Tkinter
and ttkbootstrap with a hardware-inspired interface.

Requirements satisfied:
- GUI built with Tkinter
- Bill entry field
- Tip percentage selection (10%, 15%, 20%)
- Number of diners (1 to 6)
- Automatic recalculation on change
- Handles invalid/non-numeric input
- Quit button included

Extra:
- Styled to resemble a piece of analog / retro electronic gear
"""

# Import the standard Tkinter library and rename it as tk
# Tkinter provides the main GUI functionality
import tkinter as tk

# Import ttkbootstrap and rename it as ttk
# ttkbootstrap adds modern themes and improved styling to Tkinter widgets
import ttkbootstrap as ttk

# Import helpful layout constants like LEFT, X, BOTH, Y, etc.
from ttkbootstrap.constants import *


def update_calculations(*args):
    """
    Recalculate the tip, the total bill, and the amount each person pays.

    This function runs automatically whenever the user changes:
    - the bill amount
    - the selected tip percentage
    - the number of diners

    *args is included because Tkinter's trace_add() sends extra arguments
    to callback functions automatically.
    """

    # Get the text currently typed into the bill entry box
    # .strip() removes extra spaces from the beginning/end
    bill_text = bill_var.get().strip()

    # If the field is empty, clear errors and reset the displays to $0.00
    if bill_text == "":
        error_label.config(text="")
        tip_display.config(text="$0.00")
        total_display.config(text="$0.00")
        split_display.config(text="$0.00")
        diners_caption.config(text="Split between 1 diner")
        return

    try:
        # Try converting the user's input into a decimal number
        # This will fail if the user types letters or symbols
        bill_amount = float(bill_text)

        # Prevent negative bill amounts
        # If the number is less than 0, force it into the error handling section
        if bill_amount < 0:
            raise ValueError

        # Get the selected tip percentage and convert it to decimal form
        # Example: 15 becomes 0.15
        tip_percent = tip_var.get() / 100

        # Get the number of diners selected in the spinbox
        diners = diners_var.get()

        # Calculate the tip amount
        tip_amount = bill_amount * tip_percent

        # Add the tip to the original bill
        total_bill = bill_amount + tip_amount

        # Divide the total bill by the number of diners
        split_amount = total_bill / diners

        # If everything worked, clear any old error message
        error_label.config(text="")

        # Update the three display outputs with the new calculated values
        # :.2f means "format as a float with 2 decimal places"
        tip_display.config(text=f"${tip_amount:.2f}")
        total_display.config(text=f"${total_bill:.2f}")
        split_display.config(text=f"${split_amount:.2f}")

        # Update the caption under the large split display
        # This makes the text grammatically correct for 1 diner vs multiple diners
        if diners == 1:
            diners_caption.config(text="Split between 1 diner")
        else:
            diners_caption.config(text=f"Split between {diners} diners")

    except ValueError:
        # If the user's input cannot be converted into a valid number,
        # show an error and reset all displayed values
        error_label.config(text="Enter a valid non-negative number.")
        tip_display.config(text="$0.00")
        total_display.config(text="$0.00")
        split_display.config(text="$0.00")
        diners_caption.config(text="Split between 1 diner")


# --------------------------------------------------
# Create the main window
# --------------------------------------------------

# Create the application window using ttkbootstrap
# "cyborg" is the chosen theme name
app = ttk.Window(themename="cyborg")

# Set the text shown in the title bar of the window
app.title("Tip Splitter Unit")

# Set the starting size of the window
app.geometry("860x600")

# Set the minimum size the user is allowed to resize the window to
# In your case, resizing is disabled later, but this still sets a lower limit
app.minsize(860, 690)

# Prevent the user from resizing the window horizontally or vertically
app.resizable(False, False)


# --------------------------------------------------
# Tkinter variables used to store user selections
# --------------------------------------------------

# StringVar holds the bill entry text exactly as typed
bill_var = tk.StringVar()

# IntVar holds the selected tip percentage
# Default value is 15
tip_var = tk.IntVar(value=15)

# IntVar holds the selected number of diners
# Default value is 1
diners_var = tk.IntVar(value=1)


# --------------------------------------------------
# Custom styling to create a hardware / panel look
# --------------------------------------------------

# Access the style system from ttkbootstrap
# This lets us create custom appearances for our widgets
style = app.style

# Create a custom frame style called "Panel.TFrame"
# This is used for the dark main background panel
style.configure(
    "Panel.TFrame",
    background="#2b2b2b"
)

# Create a custom labelframe style for boxed sections
# This gives sections a dark background, light text, and grooved border
style.configure(
    "PanelBox.TLabelframe",
    background="#2b2b2b",
    foreground="#d8d8d8",
    borderwidth=2,
    relief="groove"
)

# Style the title text that appears on those labelframes
style.configure(
    "PanelBox.TLabelframe.Label",
    background="#2b2b2b",
    foreground="#d8d8d8",
    font=("Segoe UI", 10, "bold")
)

# General text label style used across the panel
style.configure(
    "Panel.TLabel",
    background="#2b2b2b",
    foreground="#d8d8d8",
    font=("Segoe UI", 10)
)

# Larger title label style used for section headers
style.configure(
    "Title.TLabel",
    background="#2b2b2b",
    foreground="#c9c9c9",
    font=("Segoe UI", 18, "bold")
)

# Smaller caption label style for subtext / notes
style.configure(
    "Caption.TLabel",
    background="#2b2b2b",
    foreground="#9a9a9a",
    font=("Segoe UI", 9)
)

# Style for the smaller digital-looking displays
# These are the TIP AMOUNT and TOTAL WITH TIP boxes
style.configure(
    "DisplayLabel.TLabel",
    background="#171717",
    foreground="#ffbf4d",
    font=("Consolas", 20, "bold"),
    anchor="center",
    relief="sunken",
    borderwidth=3,
    padding=10
)

# Style for the large main output display
# This is the "PER PERSON OUTPUT" box
style.configure(
    "BigDisplay.TLabel",
    background="#101010",
    foreground="#ffd166",
    font=("Consolas", 28, "bold"),
    anchor="center",
    relief="sunken",
    borderwidth=4,
    padding=12
)


# --------------------------------------------------
# Main panel container
# --------------------------------------------------

# Create the outermost frame that fills the window
# This acts like the main metal panel body
outer_frame = ttk.Frame(app, style="Panel.TFrame", padding=16)
outer_frame.pack(fill=BOTH, expand=True)


# --------------------------------------------------
# Header section
# --------------------------------------------------

# Create a frame at the top for the title and subtitle
header_frame = ttk.Frame(outer_frame, style="Panel.TFrame")
header_frame.pack(fill=X, pady=(0, 12))

# Main title text
title_label = ttk.Label(
    header_frame,
    text="TIP SPLITTER UNIT",
    style="Title.TLabel"
)
title_label.pack()

# Smaller subtitle / model information under the title
subtitle_label = ttk.Label(
    header_frame,
    text="MODEL TS-6  |  SERVICE PANEL  |  AUTO COMPUTE ENABLED",
    style="Caption.TLabel"
)
subtitle_label.pack(pady=(2, 0))


# --------------------------------------------------
# Main content area: left controls, right displays
# --------------------------------------------------

# This frame holds the two major columns of the interface
content_frame = ttk.Frame(outer_frame, style="Panel.TFrame")
content_frame.pack(fill=BOTH, expand=True)

# Left column: user input controls
left_panel = ttk.Frame(content_frame, style="Panel.TFrame")
left_panel.pack(side=LEFT, fill=Y, padx=(0, 10))

# Right column: calculated output displays
right_panel = ttk.Frame(content_frame, style="Panel.TFrame")
right_panel.pack(side=LEFT, fill=BOTH, expand=True)


# --------------------------------------------------
# BILL INPUT SECTION
# --------------------------------------------------

# Create a boxed section on the left for the bill input
bill_frame = ttk.Labelframe(
    left_panel,
    text="BILL INPUT",
    style="PanelBox.TLabelframe",
    padding=14
)
bill_frame.pack(fill=X, pady=(0, 10))

# Instruction label above the entry box
bill_label = ttk.Label(
    bill_frame,
    text="Enter total bill amount ($)",
    style="Panel.TLabel"
)
bill_label.pack(anchor="w", pady=(0, 6))

# Entry box where the user types the bill amount
# textvariable=bill_var links this entry box to the StringVar
bill_entry = ttk.Entry(
    bill_frame,
    textvariable=bill_var,
    font=("Consolas", 14),
    width=18
)
bill_entry.pack(fill=X)

# Error message label shown when input is invalid
error_label = ttk.Label(
    bill_frame,
    text="",
    foreground="#ff6b6b",
    background="#2b2b2b",
    font=("Segoe UI", 9)
)
error_label.pack(anchor="w", pady=(6, 0))


# --------------------------------------------------
# TIP SELECT SECTION
# --------------------------------------------------

# Create the section for selecting tip %
tip_frame = ttk.Labelframe(
    left_panel,
    text="TIP SELECT",
    style="PanelBox.TLabelframe",
    padding=14
)
tip_frame.pack(fill=X, pady=(0, 10))

# Label above the tip buttons
tip_label = ttk.Label(
    tip_frame,
    text="Choose tip percentage",
    style="Panel.TLabel"
)
tip_label.pack(anchor="w", pady=(0, 8))

# Inner frame to hold the three tip buttons in one row
tip_buttons = ttk.Frame(tip_frame, style="Panel.TFrame")
tip_buttons.pack(fill=X)

# Radio button for 10%
# All three radio buttons share the same variable (tip_var),
# so only one can be selected at a time
tip_10 = ttk.Radiobutton(
    tip_buttons,
    text="10%",
    variable=tip_var,
    value=10,
    bootstyle="warning-toolbutton"
)
tip_10.pack(side=LEFT, expand=True, fill=X, padx=3)

# Radio button for 15%
tip_15 = ttk.Radiobutton(
    tip_buttons,
    text="15%",
    variable=tip_var,
    value=15,
    bootstyle="warning-toolbutton"
)
tip_15.pack(side=LEFT, expand=True, fill=X, padx=3)

# Radio button for 20%
tip_20 = ttk.Radiobutton(
    tip_buttons,
    text="20%",
    variable=tip_var,
    value=20,
    bootstyle="warning-toolbutton"
)
tip_20.pack(side=LEFT, expand=True, fill=X, padx=3)


# --------------------------------------------------
# DINER SECTION
# --------------------------------------------------

# Create the section that lets the user choose how many people are splitting the bill
diners_frame = ttk.Labelframe(
    left_panel,
    text="SPLIT CONTROL",
    style="PanelBox.TLabelframe",
    padding=14
)
diners_frame.pack(fill=X, pady=(0, 10))

# Label describing the spinbox
diners_label = ttk.Label(
    diners_frame,
    text="Number of diners (1 to 6)",
    style="Panel.TLabel"
)
diners_label.pack(anchor="w", pady=(0, 6))

# Spinbox lets the user choose a number from 1 to 6
# textvariable=diners_var connects it to the IntVar
diners_spinbox = ttk.Spinbox(
    diners_frame,
    from_=1,
    to=6,
    textvariable=diners_var,
    width=10,
    font=("Consolas", 14)
)
diners_spinbox.pack(anchor="w")

# Small explanation note under the spinbox
diners_note = ttk.Label(
    diners_frame,
    text="Adjust this to change the per-person amount.",
    style="Caption.TLabel"
)
diners_note.pack(anchor="w", pady=(8, 0))


# --------------------------------------------------
# QUIT / POWER SECTION
# --------------------------------------------------

# Create the final left-side section for exiting the app
power_frame = ttk.Labelframe(
    left_panel,
    text="POWER",
    style="PanelBox.TLabelframe",
    padding=14
)
power_frame.pack(fill=X)

# Button that closes the entire application window
# app.destroy tells Tkinter to terminate the program
quit_button = ttk.Button(
    power_frame,
    text="POWER OFF",
    command=app.destroy,
    bootstyle="danger",
    width=18
)
quit_button.pack(pady=4)


# --------------------------------------------------
# DISPLAY SECTION ON RIGHT
# --------------------------------------------------

# Header for the output side of the interface
display_title = ttk.Label(
    right_panel,
    text="OUTPUT METERS",
    style="Title.TLabel"
)
display_title.pack(anchor="w", pady=(0, 10))

# Create a row that holds the two smaller displays side by side
top_displays = ttk.Frame(right_panel, style="Panel.TFrame")
top_displays.pack(fill=X, pady=(0, 12))


# --------------------------------------------------
# TIP DISPLAY BOX
# --------------------------------------------------

# Box that shows the tip amount only
tip_box = ttk.Labelframe(
    top_displays,
    text="TIP AMOUNT",
    style="PanelBox.TLabelframe",
    padding=12
)
tip_box.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 6))

# Label that displays the calculated tip amount
tip_display = ttk.Label(
    tip_box,
    text="$0.00",
    style="DisplayLabel.TLabel"
)
tip_display.pack(fill=X)


# --------------------------------------------------
# TOTAL DISPLAY BOX
# --------------------------------------------------

# Box that shows the full bill including tip
total_box = ttk.Labelframe(
    top_displays,
    text="TOTAL WITH TIP",
    style="PanelBox.TLabelframe",
    padding=12
)
total_box.pack(side=LEFT, fill=BOTH, expand=True, padx=(6, 0))

# Label that displays the calculated total
total_display = ttk.Label(
    total_box,
    text="$0.00",
    style="DisplayLabel.TLabel"
)
total_display.pack(fill=X)


# --------------------------------------------------
# LARGE SPLIT DISPLAY
# --------------------------------------------------

# Large box for the per-person split amount
# This is the most important output when splitting the bill
split_box = ttk.Labelframe(
    right_panel,
    text="PER PERSON OUTPUT",
    style="PanelBox.TLabelframe",
    padding=16
)
split_box.pack(fill=BOTH, expand=True)

# Large digital-style display showing what each person pays
split_display = ttk.Label(
    split_box,
    text="$0.00",
    style="BigDisplay.TLabel"
)
split_display.pack(fill=X, pady=(8, 10))

# Caption showing how many diners the total is split between
diners_caption = ttk.Label(
    split_box,
    text="Split between 1 diner",
    style="Caption.TLabel"
)
diners_caption.pack()

# Extra explanation label under the main display
explain_label = ttk.Label(
    split_box,
    text="This is the amount each person should pay.",
    style="Panel.TLabel"
)
explain_label.pack(pady=(14, 0))


# --------------------------------------------------
# Automatic updating when any value changes
# --------------------------------------------------

# These three trace_add calls tell Tkinter:
# "Whenever this variable changes, run update_calculations()"
# This is what makes the program update automatically
# without needing a Calculate button
bill_var.trace_add("write", update_calculations)
tip_var.trace_add("write", update_calculations)
diners_var.trace_add("write", update_calculations)


# --------------------------------------------------
# Startup behavior
# --------------------------------------------------

# Place the text cursor in the bill entry box as soon as the app opens
bill_entry.focus()

# Start the Tkinter event loop
# This keeps the window running and waiting for user interaction
app.mainloop()