import tkinter as tk
from tkinter import ttk, messagebox

def convert_to_luau():
    raw_text = input_text.get("1.0", tk.END).strip()
    if not raw_text:
        messagebox.showwarning("No input", "Please enter at least one word.")
        return

    words = raw_text.splitlines()
    lines = ["["]

    for word in words:
        word = word.strip()
        if word:
            lines.append(f'    "{word}",')

    lines.append("]")
    output = "\n".join(lines)

    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, output)

def copy_to_clipboard():
    result = output_text.get("1.0", tk.END).strip()
    if not result:
        messagebox.showwarning("Nothing to copy", "Generate the Luau list first.")
        return

    root.clipboard_clear()
    root.clipboard_append(result)
    root.update()  # keeps clipboard after app closes

    messagebox.showinfo("Copied", "Luau list copied to clipboard.")

# =========================
# GUI Setup
# =========================

root = tk.Tk()
root.title("Words → Luau Array Converter")
root.geometry("700x450")
root.resizable(False, False)

main_frame = ttk.Frame(root, padding=12)
main_frame.pack(fill="both", expand=True)

# =========================
# Input
# =========================

ttk.Label(main_frame, text="Input words (one per line):").pack(anchor="w")

input_text = tk.Text(main_frame, height=10, font=("Consolas", 11))
input_text.pack(fill="x", pady=(4, 10))

# =========================
# Buttons
# =========================

button_frame = ttk.Frame(main_frame)
button_frame.pack(fill="x", pady=5)

convert_btn = ttk.Button(button_frame, text="Convert to Luau", command=convert_to_luau)
convert_btn.pack(side="left")

copy_btn = ttk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard)
copy_btn.pack(side="left", padx=10)

# =========================
# Output
# =========================

ttk.Label(main_frame, text="Luau output:").pack(anchor="w", pady=(10, 0))

output_text = tk.Text(main_frame, height=10, font=("Consolas", 11))
output_text.pack(fill="x", pady=(4, 0))

# =========================
# Run
# =========================

root.mainloop()