# run_gui.py
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import glob
import csv
from tkinter import ttk

def run_spider():
    asin_path = asin_entry.get()
    if not os.path.isfile(asin_path):
        messagebox.showerror("Error", "ASIN file not found!")
        return

    # Copy the selected ASIN file to the expected location
    target_path = os.path.join(os.path.dirname(__file__), "AMAZON", "spiders", "Input_ASIN.txt")
    try:
        with open(asin_path, "r", encoding="utf-8") as src, open(target_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy ASIN file: {e}")
        return

    # Run the spider
    status_label.config(text="Running spider...")
    try:
        subprocess.Popen(
            ["python", "-m", "scrapy", "runspider", "AMAZON/spiders/amazon.py"],
            shell=True
        )
        status_label.config(text="Spider started! Check Results_CSV_Files for output.")
    except Exception as e:
        status_label.config(text=f"Error: {e}")

def browse_file():
    filename = filedialog.askopenfilename(
        title="Select Input_ASIN.txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if filename:
        asin_entry.delete(0, tk.END)
        asin_entry.insert(0, filename)

def get_latest_csv():
    # Find the latest CSV in Results_CSV_Files
    csv_files = glob.glob(os.path.join("Results_CSV_Files", "*.csv"))
    if not csv_files:
        return None
    latest_file = max(csv_files, key=os.path.getctime)
    return latest_file

def show_results():
    # Remove any existing table
    for widget in table_frame.winfo_children():
        widget.destroy()

    csv_file = get_latest_csv()
    if not csv_file:
        messagebox.showinfo("No Results", "No CSV results found.")
        return

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        if not rows:
            messagebox.showinfo("Empty File", "CSV file is empty.")
            return
        headers = rows[0]
        data = rows[1:]

    tree = ttk.Treeview(table_frame, columns=headers, show='headings')
    for col in headers:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor='center')
    for row in data:
        tree.insert('', tk.END, values=row)
    tree.pack(fill='both', expand=True)

root = tk.Tk()
root.title("Amazon Spider GUI")

tk.Label(root, text="Input_ASIN.txt Path:").grid(row=0, column=0, padx=5, pady=5)
asin_entry = tk.Entry(root, width=50)
asin_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

tk.Button(root, text="Run Spider", command=run_spider, bg="green", fg="white").grid(row=1, column=1, pady=10)
tk.Button(root, text="Show Results", command=show_results, bg="blue", fg="white").grid(row=1, column=2, pady=10)

status_label = tk.Label(root, text="")
status_label.grid(row=2, column=0, columnspan=3, pady=5)

# Add a frame for the table
table_frame = tk.Frame(root)
table_frame.grid(row=3, column=0, columnspan=3, sticky='nsew')
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()