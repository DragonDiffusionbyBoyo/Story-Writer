import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import requests
import json

# Functions for Story Tab
def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            story_text_box.delete("1.0", tk.END)
            story_text_box.insert(tk.END, f.read())
        story_file_label.config(text=f"Loaded: {file_path}")

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(story_text_box.get("1.0", tk.END))
        story_file_label.config(text=f"Saved: {file_path}")

def select_file(label):
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        label.config(text=f"Selected: {file_path}")
    return file_path

def generate_story_text():
    book_text = story_text_box.get("1.0", tk.END).strip() if story_file_label.cget("text") != "No file loaded" else ""
    
    characters_text = ""
    if characters_label.cget("text") != "No file selected":
        with open(characters_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
            characters_text = f.read().strip()
    
    storyboard_text = ""
    if storyboard_label.cget("text") != "No file selected":
        with open(storyboard_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
            storyboard_text = f.read().strip()
    
    instruction_text = ""
    if instruction_label.cget("text") != "No file selected":
        with open(instruction_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
            instruction_text = f.read().strip()
    
    other_info_text = ""
    if other_info_label.cget("text") != "No file selected":
        with open(other_info_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
            other_info_text = f.read().strip()

    task = story_task_var.get()
    full_prompt = ""
    if task == "consistency":
        full_prompt = f"Review the following story for consistency (e.g., character details, plot coherence, timeline). Provide feedback on any issues found. Suggest improvements:\n\n{book_text}"
    else:
        if book_text:
            full_prompt += f"Existing story:\n{book_text}\n\n"
        if characters_text:
            full_prompt += f"Main characters:\n{characters_text}\n\n"
        if storyboard_text:
            full_prompt += f"Storyboard outline:\n{storyboard_text}\n\n"
        if instruction_text:
            full_prompt += f"Instructions:\n{instruction_text}\n\n"
        if other_info_text:
            full_prompt += f"Other important information:\n{other_info_text}\n\n"
        
        if task == "before":
            full_prompt += "Generate the story that happens BEFORE the existing story, aiming for approximately 20,000 words. Provide a detailed narrative with clear progression."
        elif task == "after":
            full_prompt += "Generate the page that happens AFTER the existing story."
        if not full_prompt:
            full_prompt = "Generate a story from scratch."

    generated_text = ""
    try:
        if task == "before":
            # Target 20,000 words (~26,667 tokens), chunk into 2,000-word (~2,667-token) segments
            target_words = 20000
            words_per_chunk = 2000  # ~2,667 tokens
            chunks = target_words // words_per_chunk  # 10 chunks
            current_text = book_text

            for i in range(chunks):
                chunk_prompt = full_prompt + f"\n\nThis is part {i+1} of {chunks}. Generate approximately {words_per_chunk} words of the story leading up to the existing text. Continue from where the previous part left off (or start if this is part 1). Ensure narrative continuity."
                
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "HammerAI/mythomax-l2:13b-q4_K_M",
                        "prompt": chunk_prompt,
                        "max_tokens": 2667,  # ~2,000 words
                        "temperature": 0.7,  # Balanced output
                        "top_p": 0.9        # Focused generation
                    },
                    stream=True
                )
                response.raise_for_status()
                chunk_text = ""
                for line in response.iter_lines():
                    if line:
                        json_line = json.loads(line.decode("utf-8"))
                        if "response" in json_line:
                            chunk_text += json_line["response"]
                if chunk_text:
                    generated_text += f"\n\n--- Part {i+1} ---\n{chunk_text}"
                    current_text = chunk_text + "\n\n" + current_text
                else:
                    generated_text += f"\n\nNo text generated for part {i+1}"
        else:
            # Non-"before" tasks
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "HammerAI/mythomax-l2:13b-q4_K_M", "prompt": full_prompt},
                stream=True
            )
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    json_line = json.loads(line.decode("utf-8"))
                    if "response" in json_line:
                        generated_text += json_line["response"]
            if not generated_text:
                generated_text = "No text generated"

    except Exception as e:
        generated_text = f"Error: {e}"
    
    story_text_box.insert(tk.END, "\n\n" + generated_text)

# Functions for World Building Tab
def load_world_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            world_text_box.delete("1.0", tk.END)
            world_text_box.insert(tk.END, f.read())
        world_file_label.config(text=f"Loaded: {file_path}")

def save_world_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(world_text_box.get("1.0", tk.END))
        world_file_label.config(text=f"Saved: {file_path}")

def generate_world_text():
    existing_text = world_text_box.get("1.0", tk.END).strip() if world_file_label.cget("text") != "No file loaded" else ""
    prompt_text = world_prompt_entry.get("1.0", tk.END).strip()

    full_prompt = ""
    if existing_text:
        full_prompt += f"Existing content (characters, places, lore, or world details):\n{existing_text}\n\n"
    if prompt_text:
        full_prompt += f"Instructions for expansion:\n{prompt_text}\n\n"
    if not full_prompt:
        full_prompt = "Generate a description of a character or place from scratch."

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "nous-hermes2-mixtral:8x7b-dpo-q4_K_M", "prompt": full_prompt},
            stream=True
        )
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
    world_text_box.delete("1.0", tk.END)
    world_text_box.insert(tk.END, existing_text + "\n\n" + generated_text if existing_text else generated_text)

# Functions for Story Review Tab
def load_review_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            review_text_box.delete("1.0", tk.END)
            review_text_box.insert(tk.END, f.read())
        review_file_label.config(text=f"Loaded: {file_path}")

def generate_review_text():
    story_text = review_text_box.get("1.0", tk.END).strip() if review_file_label.cget("text") != "No file loaded" else ""
    
    full_prompt = f"""
Step 1: Summarize the entire story in approximately 1000 words, covering key events, characters, and themes.
Step 2: Analyze the story’s structure, pacing, and character development. Identify inconsistencies or weak areas and provide constructive feedback.
Step 3: Suggest improvements for plot coherence, dialogue, and engagement.

Story:\n\n{story_text}
"""

    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "HammerAI/mythomax-l2:13b-q4_K_M", "prompt": full_prompt},
            stream=True
        )
        response.raise_for_status()
        generated_text = ""
        for line in response.iter_lines():
            if line:
                json_line = json.loads(line.decode("utf-8"))
                if "response" in json_line:
                    generated_text += json_line["response"]
        if not generated_text:
            generated_text = "No review generated"
    except Exception as e:
        generated_text = f"Error: {e}"
    review_text_box.delete("1.0", tk.END)
    review_text_box.insert(tk.END, generated_text)

# GUI Setup with Tabs
tk_root = tk.Tk()
tk_root.title("Ollama Book Writer")
tk_root.geometry("600x700")
tk_root.configure(bg="#f0f0f0")

notebook = ttk.Notebook(tk_root)
notebook.grid(row=0, column=0, sticky="nsew")

story_frame = tk.Frame(notebook, bg="#f0f0f0", padx=10, pady=10)
notebook.add(story_frame, text="Story")

story_title_label = tk.Label(story_frame, text="Ollama Book Writer", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
story_title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

story_file_frame = tk.LabelFrame(story_frame, text="Story File Management", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
story_file_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

story_file_label = tk.Label(story_file_frame, text="No file loaded", bg="#f0f0f0", fg="#34495e")
story_file_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

tk.Button(story_file_frame, text="Load Story File", command=load_file, bg="#3498db", fg="white", padx=5, pady=2).grid(row=1, column=0, padx=5, pady=5)
tk.Button(story_file_frame, text="Save Story File", command=save_file, bg="#3498db", fg="white", padx=5, pady=2).grid(row=1, column=1, padx=5, pady=5)

story_selector_frame = tk.LabelFrame(story_frame, text="Additional Inputs", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
story_selector_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

tk.Label(story_selector_frame, text="Main Characters File:", bg="#f0f0f0", fg="#34495e").grid(row=0, column=0, sticky="e", padx=5, pady=2)
characters_label = tk.Label(story_selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
characters_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
tk.Button(story_selector_frame, text="Select", command=lambda: select_file(characters_label), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=0, column=2, padx=5, pady=2)

tk.Label(story_selector_frame, text="Storyboard File:", bg="#f0f0f0", fg="#34495e").grid(row=1, column=0, sticky="e", padx=5, pady=2)
storyboard_label = tk.Label(story_selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
storyboard_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
tk.Button(story_selector_frame, text="Select", command=lambda: select_file(storyboard_label), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=1, column=2, padx=5, pady=2)

tk.Label(story_selector_frame, text="Instructions File:", bg="#f0f0f0", fg="#34495e").grid(row=2, column=0, sticky="e", padx=5, pady=2)
instruction_label = tk.Label(story_selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
instruction_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
tk.Button(story_selector_frame, text="Select", command=lambda: select_file(instruction_label), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=2, column=2, padx=5, pady=2)

tk.Label(story_selector_frame, text="Other Important Info File:", bg="#f0f0f0", fg="#34495e").grid(row=3, column=0, sticky="e", padx=5, pady=2)
other_info_label = tk.Label(story_selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
other_info_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)
tk.Button(story_selector_frame, text="Select", command=lambda: select_file(other_info_label), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=3, column=2, padx=5, pady=2)

story_task_frame = tk.LabelFrame(story_frame, text="Task", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
story_task_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
story_task_var = tk.StringVar(value="after")
tk.Radiobutton(story_task_frame, text="Generate Page Before", variable=story_task_var, value="before", bg="#f0f0f0", fg="#34495e").grid(row=0, column=0, padx=5, pady=2)
tk.Radiobutton(story_task_frame, text="Generate Page After", variable=story_task_var, value="after", bg="#f0f0f0", fg="#34495e").grid(row=0, column=1, padx=5, pady=2)
tk.Radiobutton(story_task_frame, text="Check Consistency", variable=story_task_var, value="consistency", bg="#f0f0f0", fg="#34495e").grid(row=0, column=2, padx=5, pady=2)

tk.Button(story_frame, text="Generate Text", command=generate_story_text, bg="#e74c3c", fg="white", padx=10, pady=5, font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=2, pady=10)

story_text_box = scrolledtext.ScrolledText(story_frame, wrap=tk.WORD, width=70, height=20, bg="white", fg="#2c3e50", font=("Arial", 10))
story_text_box.grid(row=5, column=0, columnspan=2, pady=10, padx=5)

world_frame = tk.Frame(notebook, bg="#f0f0f0", padx=10, pady=10)
notebook.add(world_frame, text="World Building")

world_title_label = tk.Label(world_frame, text="World Building Helper", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
world_title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

world_file_frame = tk.LabelFrame(world_frame, text="World File Management", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
world_file_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

world_file_label = tk.Label(world_file_frame, text="No file loaded", bg="#f0f0f0", fg="#34495e")
world_file_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

tk.Button(world_file_frame, text="Load File", command=load_world_file, bg="#3498db", fg="white", padx=5, pady=2).grid(row=1, column=0, padx=5, pady=5)
tk.Button(world_file_frame, text="Save File", command=save_world_file, bg="#3498db", fg="white", padx=5, pady=2).grid(row=1, column=1, padx=5, pady=5)

world_prompt_frame = tk.LabelFrame(world_frame, text="Expansion Prompt", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
world_prompt_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

tk.Label(world_prompt_frame, text="Enter prompt to expand characters/places:", bg="#f0f0f0", fg="#34495e").grid(row=0, column=0, sticky="w", padx=5, pady=2)
world_prompt_entry = scrolledtext.ScrolledText(world_prompt_frame, wrap=tk.WORD, width=50, height=5, bg="white", fg="#2c3e50", font=("Arial", 10))
world_prompt_entry.grid(row=1, column=0, columnspan=2, pady=5, padx=5)

tk.Button(world_frame, text="Generate Expansion", command=generate_world_text, bg="#e74c3c", fg="white", padx=10, pady=5, font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=2, pady=10)

world_text_box = scrolledtext.ScrolledText(world_frame, wrap=tk.WORD, width=70, height=15, bg="white", fg="#2c3e50", font=("Arial", 10))
world_text_box.grid(row=4, column=0, columnspan=2, pady=10, padx=5)

review_frame = tk.Frame(notebook, bg="#f0f0f0", padx=10, pady=10)
notebook.add(review_frame, text="Story Review")

review_title_label = tk.Label(review_frame, text="Story Review Tool", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
review_title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

review_file_frame = tk.LabelFrame(review_frame, text="Review File Management", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
review_file_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

review_file_label = tk.Label(review_file_frame, text="No file loaded", bg="#f0f0f0", fg="#34495e")
review_file_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

tk.Button(review_file_frame, text="Load Story File", command=load_review_file, bg="#3498db", fg="white", padx=5, pady=2).grid(row=1, column=0, padx=5, pady=5)

tk.Button(review_frame, text="Generate Review", command=generate_review_text, bg="#e74c3c", fg="white", padx=10, pady=5, font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=2, pady=10)

review_text_box = scrolledtext.ScrolledText(review_frame, wrap=tk.WORD, width=70, height=20, bg="white", fg="#2c3e50", font=("Arial", 10))
review_text_box.grid(row=3, column=0, columnspan=2, pady=10, padx=5)

tk_root.grid_rowconfigure(0, weight=1)
tk_root.grid_columnconfigure(0, weight=1)
story_frame.grid_rowconfigure(5, weight=1)
world_frame.grid_rowconfigure(4, weight=1)
review_frame.grid_rowconfigure(3, weight=1)

tk_root.mainloop()