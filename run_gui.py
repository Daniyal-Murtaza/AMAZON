# run_gui.py
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import glob
import csv
from tkinter import ttk
import threading
import time

# Store the latest data for export
latest_headers = []
latest_data = []

def run_spider_thread():
    # This runs in a background thread
    try:
        process = subprocess.Popen(
            ["python", "-m", "scrapy", "runspider", "AMAZON/spiders/amazon.py"],
            shell=True
        )
        # Wait for the process to finish
        while process.poll() is None:
            status_label.config(text="Spider running...")
            progress_bar.start()
            time.sleep(1)
        progress_bar.stop()
        status_label.config(text="Spider finished! Click 'Show Results'.")
        run_button.config(state=tk.NORMAL)
        show_button.config(state=tk.NORMAL)
    except Exception as e:
        progress_bar.stop()
        status_label.config(text=f"Error: {e}")
        run_button.config(state=tk.NORMAL)
        show_button.config(state=tk.NORMAL)

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

    status_label.config(text="Starting spider...")
    run_button.config(state=tk.DISABLED)
    show_button.config(state=tk.DISABLED)
    progress_bar.start()
    threading.Thread(target=run_spider_thread, daemon=True).start()

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
    global latest_headers, latest_data
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

    latest_headers = headers
    latest_data = data

    tree = ttk.Treeview(table_frame, columns=headers, show='headings')
    for col in headers:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor='center')
    for row in data:
        tree.insert('', tk.END, values=row)
    tree.pack(fill='both', expand=True)

def export_results():
    if not latest_headers or not latest_data:
        messagebox.showinfo("No Data", "No results to export. Please load results first.")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if file_path:
        try:
            with open(file_path, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(latest_headers)
                writer.writerows(latest_data)
            messagebox.showinfo("Exported", f"Results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

def clear_results():
    global latest_headers, latest_data
    for widget in table_frame.winfo_children():
        widget.destroy()
    latest_headers = []
    latest_data = []
    status_label.config(text="Results cleared.")

root = tk.Tk()
root.title("Amazon Spider GUI")

tk.Label(root, text="Input_ASIN.txt Path:").grid(row=0, column=0, padx=5, pady=5)
asin_entry = tk.Entry(root, width=50)
asin_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

run_button = tk.Button(root, text="Run Spider", command=run_spider, bg="green", fg="white")
run_button.grid(row=1, column=1, pady=10)
show_button = tk.Button(root, text="Show Results", command=show_results, bg="blue", fg="white")
show_button.grid(row=1, column=2, pady=10)

export_button = tk.Button(root, text="Export Results", command=export_results, bg="orange", fg="black")
export_button.grid(row=1, column=3, pady=10, padx=5)
clear_button = tk.Button(root, text="Clear Results", command=clear_results, bg="gray", fg="white")
clear_button.grid(row=1, column=4, pady=10, padx=5)

status_label = tk.Label(root, text="")
status_label.grid(row=2, column=0, columnspan=5, pady=5)

# Progress bar for loading indication
progress_bar = ttk.Progressbar(root, mode='indeterminate')
progress_bar.grid(row=3, column=0, columnspan=5, sticky='ew', padx=5, pady=2)

# Add a frame for the table
table_frame = tk.Frame(root)
table_frame.grid(row=4, column=0, columnspan=5, sticky='nsew')
root.grid_rowconfigure(4, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()