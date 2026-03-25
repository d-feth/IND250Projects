import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


# ============================================================
# Expense Tracker
# Project requirements covered:
# 1. Edit any existing expense
# 2. Delete any expense by index
# 3. Sort expense list by amount whenever written to file
# 4. Add Average Expense to summary output
# 5. Generate a pie chart using matplotlib
#
# This version also makes:
# - EACH EXPENSE its own pie slice
# - slices COLOR-CODED by category
# - a LEGEND showing category -> color
# ============================================================


# Name of the CSV file used for persistent storage
FILE_NAME = "expenses.csv"


def initialize_df():
    """
    Create the CSV file if it does not already exist.

    If the file exists, this function also checks that it has the
    correct column names. If not, it rebuilds the file with the
    expected structure.
    """
    expected_columns = ["Date", "Category", "Description", "Amount"]

    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)

        # If the CSV structure is wrong, rebuild it
        if list(df.columns) != expected_columns:
            df = pd.DataFrame(columns=expected_columns)
            df.to_csv(FILE_NAME, index=False)

        return df

    else:
        # Create a new empty DataFrame with the correct columns
        df = pd.DataFrame(columns=expected_columns)
        df.to_csv(FILE_NAME, index=False)
        return df


def load_expenses():
    """
    Load all expenses from the CSV file into a pandas DataFrame.
    """
    return pd.read_csv(FILE_NAME)


def save_expenses(df):
    """
    Save expenses back to the CSV file.

    IMPORTANT:
    The assignment requires the list to be sorted by amount whenever
    it is written to a file, so sorting happens here every time
    this function is called.
    """
    if not df.empty:
        # Make sure Amount is treated as numeric data
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

        # Sort from smallest to largest amount
        df = df.sort_values(by="Amount", ascending=True).reset_index(drop=True)

    df.to_csv(FILE_NAME, index=False)


def add_expense(category, description, amount):
    """
    Add a new expense to the CSV file.

    Parameters:
        category (str): expense category such as Food, Rent, Fun, etc.
        description (str): short description of the expense
        amount (str or number): dollar amount of the expense
    """
    try:
        amount = float(amount)
    except ValueError:
        print("\n❌ Invalid amount. Please enter a number.")
        return

    df = load_expenses()

    # Build a new row as a dictionary
    new_entry = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Category": category,
        "Description": description,
        "Amount": amount
    }

    # Append the new row to the DataFrame
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

    # Save back to file (this also sorts automatically)
    save_expenses(df)

    print("\n✅ Expense added successfully!")


def display_expenses():
    """
    Display all current expenses with index numbers.

    Returning the reset-index DataFrame makes it easier to show
    the user which row number they can edit or delete.
    """
    df = load_expenses()

    if df.empty:
        print("\n📭 No expenses recorded yet.")
        return df

    print("\n--- Current Expenses ---")
    print(df.reset_index())
    return df.reset_index()


def delete_expense(index):
    """
    Delete an expense by its index number.
    """
    df = load_expenses()

    if df.empty:
        print("\n📭 No expenses to delete.")
        return

    try:
        index = int(index)
    except ValueError:
        print("\n❌ Invalid index. Please enter a whole number.")
        return

    # Make sure the index exists
    if index < 0 or index >= len(df):
        print("\n❌ Index out of range.")
        return

    # Store the deleted row for confirmation output
    deleted_row = df.iloc[index]

    # Remove the selected row
    df = df.drop(index=index).reset_index(drop=True)

    # Save updated file
    save_expenses(df)

    print("\n✅ Expense deleted successfully!")
    print(
        f"Deleted: {deleted_row['Category']} | "
        f"{deleted_row['Description']} | "
        f"${deleted_row['Amount']:.2f}"
    )


def edit_expense(index):
    """
    Edit an existing expense by index.

    Per the project requirements, when an expense is edited,
    the date/time should be automatically updated.
    """
    df = load_expenses()

    if df.empty:
        print("\n📭 No expenses to edit.")
        return

    try:
        index = int(index)
    except ValueError:
        print("\n❌ Invalid index. Please enter a whole number.")
        return

    if index < 0 or index >= len(df):
        print("\n❌ Index out of range.")
        return

    # Show the row before editing
    print("\n--- Expense to Edit ---")
    print(df.iloc[index])

    # Get new values from the user
    new_category = input("Enter new Category: ").strip()
    new_description = input("Enter new Description: ").strip()
    new_amount = input("Enter new Amount: ").strip()

    # Validate amount
    try:
        new_amount = float(new_amount)
    except ValueError:
        print("\n❌ Invalid amount. Please enter a number.")
        return

    # Update the row
    df.at[index, "Category"] = new_category
    df.at[index, "Description"] = new_description
    df.at[index, "Amount"] = new_amount

    # Automatically update date/time when edited
    df.at[index, "Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save updated data
    save_expenses(df)

    print("\n✅ Expense updated successfully!")


def sort_expenses():
    """
    Manually sort expenses and display them.

    Even though sorting already happens automatically during save,
    this function gives the user a direct menu option for sorting.
    """
    df = load_expenses()

    if df.empty:
        print("\n📭 No expenses to sort.")
        return

    save_expenses(df)
    print("\n✅ Expenses sorted by amount successfully!")
    display_expenses()


def view_summary():
    """
    Display:
    - all expenses
    - total spent
    - average expense
    - spending totals by category
    """
    df = load_expenses()

    if df.empty:
        print("\n📭 No expenses recorded yet.")
        return

    # Make sure Amount is numeric
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    print("\n--- Current Expenses ---")
    print(df.reset_index())

    total = df["Amount"].sum()
    average = df["Amount"].mean()

    print(f"\n💰 Total Spent: ${total:.2f}")
    print(f"📊 Average Expense: ${average:.2f}")

    print("\n--- Spending by Category ---")
    print(df.groupby("Category")["Amount"].sum())


def plot_expenses():
    """
    Create a pie chart where:
    - each INDIVIDUAL EXPENSE is its own slice
    - slices are GROUPED together by category
    - categories are ordered by TOTAL category amount
    - expenses inside each category are ordered by individual amount
    - slices are color-coded by category
    - the legend shows category -> color

    This makes the pie chart more readable than random individual ordering.
    """
    df = load_expenses()

    if df.empty:
        print("\n📭 No expenses to plot.")
        return

    # Make sure Amount is numeric
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    # Remove invalid rows and zero/negative amounts for pie chart safety
    df = df.dropna(subset=["Amount"])
    df = df[df["Amount"] > 0]

    if df.empty:
        print("\n📭 No valid positive expense data to plot.")
        return

    # ------------------------------------------------------------
    # STEP 1: Compute total spending per category
    # ------------------------------------------------------------
    category_totals = (
        df.groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    # ------------------------------------------------------------
    # STEP 2: Build a new DataFrame sorted specifically for plotting
    #
    # Categories are ordered by category total amount.
    # Expenses inside each category are ordered by individual amount.
    # This keeps slices grouped visually by category.
    # ------------------------------------------------------------
    ordered_parts = []

    for category in category_totals.index:
        category_df = df[df["Category"] == category].copy()

        # Sort expenses inside this category by amount (largest first)
        category_df = category_df.sort_values(by="Amount", ascending=False)

        ordered_parts.append(category_df)

    plot_df = pd.concat(ordered_parts, ignore_index=True)

    # ------------------------------------------------------------
    # STEP 3: Assign one color per category
    # Every expense in the same category gets the same color
    # ------------------------------------------------------------
    categories = list(category_totals.index)

    # Use a colormap with many distinct colors if needed
    cmap = plt.get_cmap("tab20")
    category_colors = {}

    for i, category in enumerate(categories):
        category_colors[category] = cmap(i % 20)

    slice_colors = [category_colors[cat] for cat in plot_df["Category"]]

    # ------------------------------------------------------------
    # STEP 4: Build shorter labels
    #
    # Long labels cause overlap and clipping.
    # Keep labels compact so they fit better.
    # Example: "Coffee\n$5.50"
    # ------------------------------------------------------------
    labels = []

    for desc, amt in zip(plot_df["Description"], plot_df["Amount"]):
        short_desc = str(desc)

        # Shorten long descriptions so they do not explode the layout
        if len(short_desc) > 12:
            short_desc = short_desc[:12] + "..."

        labels.append(f"{short_desc}\n${amt:.2f}")

    # ------------------------------------------------------------
    # STEP 5: Create the chart with a larger figure and better spacing
    # ------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(13, 10))

    wedges, texts, autotexts = ax.pie(
        plot_df["Amount"],
        labels=labels,
        colors=slice_colors,
        autopct="%1.1f%%",
        startangle=90,
        labeldistance=1.08,   # keep labels close enough to fit
        pctdistance=0.72      # percent text slightly inward
    )

    ax.set_title(
        "Expenses Pie Chart\n(Expenses grouped by category, categories ordered by total amount)",
        pad=20
    )
    ax.axis("equal")  # keep pie circular

    # Make label text smaller so it fits better
    for text in texts:
        text.set_fontsize(9)

    for autotext in autotexts:
        autotext.set_fontsize(8)

    # ------------------------------------------------------------
    # STEP 6: Add a legend for categories and totals
    # This gives the viewer a clean color key.
    # ------------------------------------------------------------
    legend_handles = [
        Patch(
            facecolor=category_colors[category],
            label=f"{category} (${category_totals[category]:.2f})"
        )
        for category in categories
    ]

    ax.legend(
        handles=legend_handles,
        title="Categories",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=9,
        title_fontsize=10
    )

    # ------------------------------------------------------------
    # STEP 7: Adjust margins so nothing gets cut off
    #
    # The right side is widened to make room for the legend.
    # ------------------------------------------------------------
    plt.subplots_adjust(left=0.05, right=0.72, top=0.88, bottom=0.05)

    plt.show()



def main():
    """
    Main program loop.
    Shows the menu and calls the appropriate function depending
    on the user's choice.
    """
    initialize_df()

    while True:
        print("\n--- 📈 Expense Tracker CLI ---")
        print("1. Add Expense")
        print("2. View Summary")
        print("3. Delete Expense")
        print("4. Edit Expense")
        print("5. Generate Pie Chart")
        print("6. Sort Expenses")
        print("7. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            cat = input("Enter Category (e.g., Food, Rent, Fun): ").strip()
            desc = input("Short Description: ").strip()
            amt = input("Amount: ").strip()
            add_expense(cat, desc, amt)

        elif choice == "2":
            view_summary()

        elif choice == "3":
            display_expenses()
            idx = input("Enter the index of the expense to delete: ").strip()
            delete_expense(idx)

        elif choice == "4":
            display_expenses()
            idx = input("Enter the index of the expense to edit: ").strip()
            edit_expense(idx)

        elif choice == "5":
            plot_expenses()

        elif choice == "6":
            sort_expenses()

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("❌ Invalid choice, try again.")


# This line makes sure main() only runs when this file is executed directly
if __name__ == "__main__":
    main()
