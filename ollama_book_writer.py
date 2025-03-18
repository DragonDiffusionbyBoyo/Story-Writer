import tkinter as tk
from tkinter import filedialog, scrolledtext
import requests
import json

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

# GUI Setup
tk_root = tk.Tk()
tk_root.title("Ollama Book Writer")

file_label = tk.Label(tk_root, text="No file loaded")
file_label.pack()

load_button = tk.Button(tk_root, text="Load Story File", command=load_file)
load_button.pack()

save_button = tk.Button(tk_root, text="Save Story File", command=save_file)
save_button.pack()

# New File Selectors
# 1. Main Characters
tk.Label(tk_root, text="Main Characters File:").pack()
characters_label = tk.Label(tk_root, text="No file selected")
characters_label.pack()
tk.Button(tk_root, text="Select Characters File", command=lambda: select_file(characters_label)).pack()

# 2. Simple Storyboard
tk.Label(tk_root, text="Storyboard File:").pack()
storyboard_label = tk.Label(tk_root, text="No file selected")
storyboard_label.pack()
tk.Button(tk_root, text="Select Storyboard File", command=lambda: select_file(storyboard_label)).pack()

# 3. What Should Happen Next
tk.Label(tk_root, text="What Should Happen Next File:").pack()
prompt_label = tk.Label(tk_root, text="No file selected")
prompt_label.pack()
tk.Button(tk_root, text="Select Prompt File", command=lambda: select_file(prompt_label)).pack()

# 4. Other Important Information
tk.Label(tk_root, text="Other Important Info File:").pack()
other_info_label = tk.Label(tk_root, text="No file selected")
other_info_label.pack()
tk.Button(tk_root, text="Select Other Info File", command=lambda: select_file(other_info_label)).pack()

generate_button = tk.Button(tk_root, text="Generate Text", command=generate_text)
generate_button.pack()

text_box = scrolledtext.ScrolledText(tk_root, wrap=tk.WORD, width=80, height=20)
text_box.pack()

tk_root.mainloop()