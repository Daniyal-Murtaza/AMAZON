# run_gui.py
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

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

root = tk.Tk()
root.title("Amazon Spider GUI")

tk.Label(root, text="Input_ASIN.txt Path:").grid(row=0, column=0, padx=5, pady=5)
asin_entry = tk.Entry(root, width=50)
asin_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

tk.Button(root, text="Run Spider", command=run_spider, bg="green", fg="white").grid(row=1, column=1, pady=10)

status_label = tk.Label(root, text="")
status_label.grid(row=2, column=0, columnspan=3, pady=5)

root.mainloop()