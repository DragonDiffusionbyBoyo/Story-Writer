import tkinter as tk
from tkinter import filedialog, scrolledtext
import requests
import json

# Functions (unchanged)
def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, f.read())
        file_label.config(text=f"Loaded: {file_path}")

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_box.get("1.0", tk.END))
        file_label.config(text=f"Saved: {file_path}")

def select_file(label):
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        label.config(text=f"Selected: {file_path}")
    return file_path

def generate_text():
    book_text = text_box.get("1.0", tk.END).strip() if file_label.cget("text") != "No file loaded" else ""
    
    # Read contents of selected files (if any)
    characters_text = ""
    if characters_label.cget("text") != "No file selected":
        with open(characters_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
            characters_text = f.read().strip()
    
    storyboard_text = ""
    if storyboard_label.cget("text") != "No file selected":
        with open(storyboard_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
            storyboard_text = f.read().strip()
    
    prompt_text = ""
    if prompt_label.cget("text") != "No file selected":
        with open(prompt_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
            prompt_text = f.read().strip()
    
    other_info_text = ""
    if other_info_label.cget("text") != "No file selected":
        with open(other_info_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
            other_info_text = f.read().strip()

    # Build the full prompt with optional sections
    full_prompt = ""
    if book_text:
        full_prompt += f"Existing story:\n{book_text}\n\n"
    if characters_text:
        full_prompt += f"Main characters:\n{characters_text}\n\n"
    if storyboard_text:
        full_prompt += f"Storyboard outline:\n{storyboard_text}\n\n"
    if prompt_text:
        full_prompt += f"What should happen next:\n{prompt_text}\n\n"
    if other_info_text:
        full_prompt += f"Other important information:\n{other_info_text}\n\n"
    if not full_prompt:
        full_prompt = "Generate a story from scratch."

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3:8b", "prompt": full_prompt},
            stream=True
        )
        print(f"Status: {response.status_code}, Text: {response.text}")  # Debug
        response.raise_for_status()
        generated_text = ""
        for line in response.iter_lines():
            if line:
                json_line = json.loads(line.decode("utf-8"))
                if "response" in json_line:
                    generated_text += json_line["response"]
        if not generated_text:
            generated_text = "No text generated"
    except Exception as e:
        generated_text = f"Error: {e}"
    text_box.insert(tk.END, "\n\n" + generated_text)

# GUI Setup with Styling
tk_root = tk.Tk()
tk_root.title("Ollama Book Writer")
tk_root.geometry("600x700")  # Set a fixed window size
tk_root.configure(bg="#f0f0f0")  # Light gray background

# Main Frame for Organization
main_frame = tk.Frame(tk_root, bg="#f0f0f0", padx=10, pady=10)
main_frame.grid(row=0, column=0, sticky="nsew")

# Title Label
title_label = tk.Label(main_frame, text="Ollama Book Writer", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

# File Management Section
file_frame = tk.LabelFrame(main_frame, text="Story File Management", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
file_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

file_label = tk.Label(file_frame, text="No file loaded", bg="#f0f0f0", fg="#34495e")
file_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

load_button = tk.Button(file_frame, text="Load Story File", command=load_file, bg="#3498db", fg="white", padx=5, pady=2)
load_button.grid(row=1, column=0, padx=5, pady=5)

save_button = tk.Button(file_frame, text="Save Story File", command=save_file, bg="#3498db", fg="white", padx=5, pady=2)
save_button.grid(row=1, column=1, padx=5, pady=5)

# Additional File Selectors Section
selector_frame = tk.LabelFrame(main_frame, text="Additional Inputs", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
selector_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

# 1. Main Characters
tk.Label(selector_frame, text="Main Characters File:", bg="#f0f0f0", fg="#34495e").grid(row=0, column=0, sticky="e", padx=5, pady=2)
characters_label = tk.Label(selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
characters_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
tk.Button(selector_frame, text="Select", command=lambda: select_file(characters_label), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=0, column=2, padx=5, pady=2)

# 2. Storyboard
tk.Label(selector_frame, text="Storyboard File:", bg="#f0f0f0", fg="#34495e").grid(row=1, column=0, sticky="e", padx=5, pady=2)
storyboard_label = tk.Label(selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
storyboard_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
tk.Button(selector_frame, text="Select", command=lambda: select_file(storyboard_label), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=1, column=2, padx=5, pady=2)

# 3. What Should Happen Next
tk.Label(selector_frame, text="What Should Happen Next File:", bg="#f0f0f0", fg="#34495e").grid(row=2, column=0, sticky="e", padx=5, pady=2)
prompt_label = tk.Label(selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
prompt_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
tk.Button(selector_frame, text="Select", command=lambda: select_file(prompt_label), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=2, column=2, padx=5, pady=2)

# 4. Other Important Information
tk.Label(selector_frame, text="Other Important Info File:", bg="#f0f0f0", fg="#34495e").grid(row=3, column=0, sticky="e", padx=5, pady=2)
other_info_label = tk.Label(selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
other_info_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)
tk.Button(selector_frame, text="Select", command=lambda: select_file(other_info_label), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=3, column=2, padx=5, pady=2)

# Generate Button
generate_button = tk.Button(main_frame, text="Generate Text", command=generate_text, bg="#e74c3c", fg="white", padx=10, pady=5, font=("Arial", 10, "bold"))
generate_button.grid(row=3, column=0, columnspan=2, pady=10)

# Text Box
text_box = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=70, height=20, bg="white", fg="#2c3e50", font=("Arial", 10))
text_box.grid(row=4, column=0, columnspan=2, pady=10, padx=5)

# Configure grid weights for responsiveness
tk_root.grid_rowconfigure(0, weight=1)
tk_root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(4, weight=1)

tk_root.mainloop()