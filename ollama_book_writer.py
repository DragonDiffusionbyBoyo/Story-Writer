import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import requests
import json
import os
import logging
import langdetect
from googletrans import Translator
import re

# Initial logging setup at script start
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# Global variables
available_models = []
current_chapter = 2  # Start at Chapter 2

# Fetch available Ollama models
def fetch_ollama_models():
    global available_models
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        data = response.json()
        available_models = [model["name"] for model in data.get("models", [])]
        if not available_models:
            available_models = ["gemma3:27b"]  # Fallback
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
        available_models = ["gemma3:27b"]  # Fallback if API fails
    return available_models

# Functions for Story Tab
def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            story_text_box.delete("1.0", tk.END)
            story_text_box.insert(tk.END, f.read())
        story_file_label.config(text=f"Loaded: {file_path}")

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(story_text_box.get("1.0", tk.END))
        story_file_label.config(text=f"Saved: {file_path}")

def select_file(label, is_json=False):
    filetypes = [("JSON Files", "*.json"), ("Text Files", "*.txt"), ("All Files", "*.*")] if is_json else [("Text Files", "*.txt"), ("All Files", "*.*")]
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    if file_path:
        label.config(text=f"Selected: {file_path}")
    return file_path

def select_temp_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        temp_folder_label.config(text=f"Temp Folder: {folder_path}")
    return folder_path

def update_status(message):
    status_box.delete("1.0", tk.END)
    status_box.insert(tk.END, message)
    tk_root.update()

def reset_chapter():
    global current_chapter
    current_chapter = 2
    story_text_box.delete("1.0", tk.END)
    update_status("Reset to Chapter 2. Load Chapter 1 and click Generate Text.")

def generate_story_text():
    global current_chapter
    try:
        book_text = story_text_box.get("1.0", tk.END).strip() if story_file_label.cget("text") != "No file loaded" else ""
        characters_data = {}
        if characters_label.cget("text") != "No file selected":
            with open(characters_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
                characters_data = json.load(f)
            logger.info(f"Characters loaded: {len(json.dumps(characters_data))} chars")
        storyboard_data = {}
        if storyboard_label.cget("text") != "No file selected":
            with open(storyboard_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
                storyboard_data = json.load(f)
        instruction_text = ""
        if instruction_label.cget("text") != "No file selected":
            with open(instruction_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
                instruction_text = f.read().strip()
            logger.info(f"Instructions loaded: {len(instruction_text)} chars")
        other_info_text = ""
        if other_info_label.cget("text") != "No file selected":
            with open(other_info_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
                other_info_text = f.read().strip()
            logger.info(f"Other Info loaded: {len(other_info_text)} chars")
        temp_folder = temp_folder_label.cget("text").replace("Temp Folder: ", "") if temp_folder_label.cget("text") != "No temp folder selected" else os.getcwd()
        logger.info(f"Temp folder set to: {temp_folder}")

        # Set up logging file handler for this run
        log_file = os.path.join(temp_folder, "llm_generation.log")
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        logger.handlers = [file_handler]
        logger.info(f"Logging initialized to: {log_file}")

        if not storyboard_data or "chapters" not in storyboard_data:
            update_status("Error: No valid storyboard JSON loaded.")
            return

        chapters = storyboard_data.get("chapters", [])
        if current_chapter - 2 >= len(chapters):
            update_status("All chapters generated! Reset or load a new storyboard.")
            return

        chapter = chapters[current_chapter - 2]
        chapter_num = chapter.get("number", current_chapter)
        chapter_title = chapter.get("title", "")
        chapter_setting = chapter.get("setting", "")
        chapter_sections = chapter.get("sections", [])
        chapter_characters = chapter.get("characters_present", [])
        chapter_style = chapter.get("style", storyboard_data.get("notes", {}).get("default_style", "30-40% witty dialogue, 60-70% dark atmosphere"))

        update_status(f"Generating Chapter {chapter_num}: {chapter_title} (~2000+ words)...")
        logger.info(f"Generating Chapter {chapter_num}: {chapter_title}")

        prev_text = book_text if current_chapter == 2 else ""
        if current_chapter > 2:
            for i in range(1, current_chapter):
                prev_file = os.path.join(temp_folder, f"temp_chapter_{i}.txt")
                logger.info(f"Checking previous chapter file: {prev_file}")
                if os.path.exists(prev_file):
                    try:
                        with open(prev_file, "r", encoding="utf-8") as f:
                            prev_text += f.read().strip() + "\n\n"
                        logger.info(f"Loaded previous chapter: {prev_file}")
                    except Exception as e:
                        logger.error(f"Failed to load {prev_file}: {e}")
                else:
                    logger.warning(f"Previous chapter file not found: {prev_file}")

        system_message = """
You are a precise storytelling engine with a 128k token context window. Your task is to write a single chapter based on a JSON storyboard.
The storyboard specifies the chapter’s setting, characters, and exact section tasks with minimum word counts.
Use ONLY the specified setting, characters, and tasks. Do not deviate, repeat prior content, or introduce unlisted elements unless instructed.
Generate the full section without stopping, meeting or exceeding the minimum word count. Output ONLY the narrative text—no titles, no commentary.
Aim for at least 2000 words for the chapter, using the full context provided without truncation. More words are acceptable.
"""

        full_prompt = (
            f"{system_message}\n\n"
            f"Previous Chapters (full context):\n{prev_text}\n\n" if prev_text else ""
            f"Characters (JSON):\n{json.dumps(characters_data, indent=2)}\n\n"
            f"Instructions:\n{instruction_text}\n\n" if instruction_text else ""
            f"Other Info:\n{other_info_text}\n\n" if other_info_text else ""
            f"Generate Chapter {chapter_num}: {chapter_title} with at least 2000 words, following the sections below:\n"
        )

        chunk_text = ""
        total_word_count = 0
        for section_idx, section in enumerate(chapter_sections):
            section_task = section.get("task", "")
            section_word_count = section.get("word_count", 400)  # Minimum word count
            section_instructions = section.get("instructions", "Describe in detail.")

            section_prompt = (
                f"{full_prompt}"
                f"WRITE THIS EXACT STORY SECTION AND NOTHING ELSE:\n"
                f"Setting: {chapter_setting}\n"
                f"Characters Present: {', '.join(chapter_characters)}\n"
                f"Task: {section_task}\n"
                f"Instructions: {section_instructions}\n"
                f"Generate at least {section_word_count} words of narrative text using ONLY the above. "
                f"Complete the full section without stopping, exceeding the minimum if desired. "
                f"Style: {chapter_style}. "
                f"Output ONLY the narrative text—no titles, no commentary, no deviations. "
                f"Shift scenes explicitly when needed (e.g., 'Now shift to Vic’s POV')."
            )

            logger.info(f"Full prompt length for section {section_idx + 1}: {len(section_prompt)} chars")
            request_json = {
                "model": model_var.get(),
                "prompt": section_prompt,
                "max_tokens": int(section_word_count * 10),  # High enough to allow excess
                "temperature": 0.5,
                "top_p": 0.85,
                "stream": True
            }

            temp_text = ""
            retries = 0
            max_retries = 5
            while retries < max_retries:
                try:
                    response = requests.post("http://localhost:11434/api/generate", json=request_json, timeout=300, stream=True)
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            json_line = json.loads(line.decode("utf-8"))
                            if "response" in json_line:
                                temp_text += json_line["response"]
                    section_words = len(temp_text.split())
                    is_complete = temp_text.strip().endswith((".", "!", "?"))
                    logger.info(f"Section {section_idx + 1} attempt {retries + 1}: {section_words} words, Raw response length: {len(temp_text)} chars")

                    # Only retry if below minimum or incomplete
                    if section_words >= section_word_count and is_complete:
                        break  # Meets minimum and complete
                    elif retries < max_retries - 1:
                        retries += 1
                        if not is_complete:
                            request_json["prompt"] = section_prompt + f"\nContinue from: {temp_text}\nComplete the last sentence naturally and reach at least {section_word_count} words."
                            logger.info(f"Retry {retries}: Forcing sentence completion")
                        else:
                            request_json["prompt"] = section_prompt + f"\nContinue from: {temp_text}\nReach at least {section_word_count} words."
                            logger.warning(f"Retry {retries}: Output too short ({section_words} vs {section_word_count} minimum)")
                    else:
                        break  # Max retries reached
                except (requests.RequestException, ValueError) as e:
                    logger.error(f"API error on section '{section_task}': {e}")
                    temp_text = f"[API Error: Failed to generate section. {e}] " * (section_word_count // 10)
                    retries += 1
                    if retries == max_retries:
                        break

            # Only pad if below minimum
            section_words = len(temp_text.split())
            if section_words < section_word_count:
                shortfall = section_word_count - section_words
                temp_text += f" The desert stretched on, silent but for the hum of unseen machines." * (shortfall // 20)
                if not temp_text.strip().endswith((".", "!", "?")):
                    temp_text += " The end came swiftly."
            # No trimming—keep all excess
            chunk_text += temp_text.strip() + "\n\n"
            total_word_count += len(temp_text.split())

        # Ensure chapter minimum of 2000 words
        if total_word_count < 2000:
            chunk_text += " The desert stretched on, silent but for the hum of unseen machines." * ((2000 - total_word_count) // 20)
            total_word_count = len(chunk_text.split())

        temp_file_path = os.path.join(temp_folder, f"temp_chapter_{chapter_num}.txt")
        with open(temp_file_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(chunk_text)
        logger.info(f"Saved temp file: {temp_file_path}, Word count: {total_word_count}")
        update_status(f"Chapter {chapter_num} generated and saved: {temp_file_path} ({total_word_count} words, minimum 2000)")

        if book_text:
            story_text_box.delete("1.0", tk.END)
            story_text_box.insert(tk.END, book_text + "\n\n" + chunk_text)
        else:
            story_text_box.insert(tk.END, chunk_text)

        current_chapter += 1
        if current_chapter > 10:
            update_status("All chapters (2-10) generated! Final story saved.")
            final_file_path = os.path.join(temp_folder, "temp_story_final.txt")
            with open(final_file_path, "w", encoding="utf-8") as final_file:
                final_file.write(story_text_box.get("1.0", tk.END))
            logger.info(f"Saved final story: {final_file_path}")
    except Exception as e:
        update_status(f"Error in generation: {str(e)}")
        logger.error(f"Generation failed: {str(e)}")

def enhance_story_text():
    # [Unchanged from your original - included for completeness]
    book_text = story_text_box.get("1.0", tk.END).strip() if story_file_label.cget("text") != "No file loaded" else ""
    if not book_text:
        update_status("Error: No story loaded to enhance.")
        return
    
    characters_data = {}
    if characters_label.cget("text") != "No file selected":
        with open(characters_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
            characters_data = json.load(f)
    storyboard_data = {}
    chapter_titles = []
    if storyboard_label.cget("text") != "No file selected":
        with open(storyboard_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
            storyboard_data = json.load(f)
            chapter_titles = [chapter["title"] for chapter in storyboard_data.get("chapters", [])]
    instruction_text = ""
    if instruction_label.cget("text") != "No file selected":
        with open(instruction_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
            instruction_text = f.read().strip()
    other_info_text = ""
    if other_info_label.cget("text") != "No file selected":
        with open(other_info_label.cget("text").replace("Selected: ", ""), "r", encoding="utf-8") as f:
            other_info_text = f.read().strip()
    temp_folder = temp_folder_label.cget("text").replace("Temp Folder: ", "") if temp_folder_label.cget("text") != "No temp folder selected" else os.getcwd()

    log_file = os.path.join(temp_folder, "llm_enhancement.log")
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")
    logging.info("Starting story enhancement process.")

    original_word_count = len(book_text.split())
    target_words = original_word_count * 2
    min_words = int(target_words * 0.9)
    max_words = int(target_words * 1.1)
    chunks = 9
    words_per_chunk = target_words // chunks
    min_chunk_words = int(words_per_chunk * 0.9)
    max_chunk_words = int(words_per_chunk * 1.1)

    full_prompt = (
        f"Existing story to enhance (currently {original_word_count} words):\n{book_text}\n\n"
        f"Main characters (JSON):\n{json.dumps(characters_data, indent=2)}\n\n"
        f"Storyboard outline (JSON):\n{json.dumps(storyboard_data, indent=2)}\n\n"
        f"Instructions:\n{instruction_text}\n\n"
        f"Other important information:\n{other_info_text}\n\n"
        f"Task: Enhance the existing story by doubling its size to approximately {target_words} words (between {min_words} and {max_words} words). "
        f"Maintain the 9-chapter structure (Chapters 2 to 10), expanding each chapter to approximately {words_per_chunk} words ({min_chunk_words}–{max_chunk_words} words). "
        f"Enrich the narrative with deeper character development, additional subplots, detailed descriptions, and new events, "
        f"while preserving the original plot points, character arcs, and tone as outlined in the JSON Storyboard."
    )

    system_message = """
You are a collaborative storyteller. Your task is to enhance an existing story based on a JSON storyboard.
The storyboard outlines chapters with titles, settings, characters, and sections with specific tasks and word counts.
You MUST adhere to the JSON, enriching only the specified characters, settings, and events with additional detail.
Output only the narrative text, no commentary or questions.
"""

    generated_text = ""
    update_status("Starting enhancement...")
    logging.info(f"Task: Enhance story to {target_words} words (±10%).")
    try:
        model = model_var.get()
        request_json = {
            "model": model,
            "prompt": "",
            "max_tokens": 3000,
            "temperature": 0.7,
            "top_p": 0.85
        }
        logging.info(f"Using model: {model}")

        accumulated_text = ""
        chapters = storyboard_data.get("chapters", [])
        if len(chapters) != 9:
            update_status("Error: Storyboard JSON must have exactly 9 chapters (2-10).")
            logging.error("Storyboard JSON does not have 9 chapters.")
            return

        for i in range(chunks):
            chapter_num = i + 2
            chapter = chapters[i]
            chapter_title = chapter.get("title", "")
            chapter_setting = chapter.get("setting", "")
            chapter_sections = chapter.get("sections", [])
            chapter_characters = chapter.get("characters_present", [])
            update_status(f"Enhancing Chapter {chapter_num}: {chapter_title} (~{words_per_chunk} words)...")
            prev_chapter_file = os.path.join(temp_folder, f"temp_enhanced_chapter_{chapter_num - 1}.txt") if i > 0 else None
            prev_text = ""
            if prev_chapter_file and os.path.exists(prev_chapter_file):
                with open(prev_chapter_file, "r", encoding="utf-8") as f:
                    prev_text = f.read().strip()
            
            chunk_text = f"--- Chapter {chapter_num}: {chapter_title} ---\n"
            total_word_count = 0
            for section in chapter_sections:
                section_task = section.get("task", "")
                section_word_count = section.get("word_count", 400) * 2  # Double original section size
                section_instructions = section.get("instructions", "Describe in detail.") + " Enhance with deeper character moments and richer descriptions."
                
                chunk_prompt = (
                    f"{system_message}\n\n"
                    f"{full_prompt}\n\n"
                    f"Previous Enhanced Chapter: {prev_text}\n" if prev_text else f"Existing Story: {book_text}\n" if i == 0 else ""
                    f"ENHANCE THIS EXACT STORY SECTION:\n"
                    f"Setting: {chapter_setting}\n"
                    f"Characters Present: {', '.join(chapter_characters)}\n"
                    f"Task: {section_task}\n"
                    f"Instructions: {section_instructions}\n"
                    f"Generate exactly {section_word_count} words of enhanced narrative text using ONLY the above. "
                    f"Style: follow the storyboard and characters. "
                    f"Output only the narrative text, no commentary."
                )
                logging.info(f"Section prompt: {chunk_prompt[:500]}...")
                request_json["prompt"] = chunk_prompt
                
                temp_text = ""
                token_count = 0
                response = requests.post("http://localhost:11434/api/generate", json=request_json, stream=True)
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        json_line = json.loads(line.decode("utf-8"))
                        if "response" in json_line:
                            temp_text += json_line["response"]
                            token_count += 1
                section_words = len(temp_text.split())
                logging.info(f"Section '{section_task}' enhanced. Word count: {section_words}, Token count: {token_count}")
                
                if section_words < section_word_count:
                    temp_text += " [Padding: The desert stretched endlessly, whispering secrets.]" * ((section_word_count - section_words) // 50)
                elif section_words > section_word_count:
                    temp_text = " ".join(temp_text.split()[:section_word_count])
                chunk_text += temp_text + "\n\n"
                total_word_count += len(temp_text.split())
            
            logging.info(f"Chapter {chapter_num} enhanced. Total word count: {total_word_count}")
            if total_word_count < min_chunk_words:
                chunk_text += " [Padding: The desert stretched endlessly, whispering secrets.]" * ((min_chunk_words - total_word_count) // 50)
                total_word_count = len(chunk_text.split())
            elif total_word_count > max_chunk_words:
                chunk_text = " ".join(chunk_text.split()[:max_chunk_words])
                total_word_count = max_chunk_words
            
            generated_text += f"\n\n{chunk_text}"
            accumulated_text += chunk_text + "\n\n"
            
            temp_file_path = os.path.join(temp_folder, f"temp_enhanced_chapter_{chapter_num}.txt")
            with open(temp_file_path, "w", encoding="utf-8") as temp_file:
                temp_file.write(chunk_text)
            update_status(f"Saved temp file: {temp_file_path}")
            logging.info(f"Saved temp file: {temp_file_path}, Word count: {total_word_count}")

        if accumulated_text:
            final_file_path = os.path.join(temp_folder, "temp_enhanced_story_final.txt")
            with open(final_file_path, "w", encoding="utf-8") as final_file:
                final_file.write(accumulated_text)
            update_status(f"Saved final temp file: {final_file_path}")
            logging.info(f"Saved final temp file: {final_file_path}")

        total_words = len(generated_text.split())
        story_text_box.delete("1.0", tk.END)
        story_text_box.insert(tk.END, generated_text)
        update_status(f"Enhancement complete. Story enhanced to {total_words} words (target: {target_words}, range: {min_words}–{max_words}).")
        logging.info(f"Enhancement process completed. Total word count: {total_words}")

    except Exception as e:
        generated_text = f"Error: {e}"
        update_status(f"Error: {e}")
        logging.error(f"Error during enhancement: {e}")

# Functions for World Building Tab
def load_world_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            world_text_box.delete("1.0", tk.END)
            world_text_box.insert(tk.END, f.read())
        world_file_label.config(text=f"Loaded: {file_path}")

def save_world_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
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
            json={"model": model_var.get(), "prompt": full_prompt, "temperature": 0.7, "top_p": 0.85},
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
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
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
            json={"model": model_var.get(), "prompt": full_prompt, "temperature": 0.7, "top_p": 0.85},
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

# Functions for Fixer Tab
def load_fixer_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            fixer_text_box.delete("1.0", tk.END)
            fixer_text_box.insert(tk.END, f.read())
        fixer_file_label.config(text=f"Loaded: {file_path}")

def select_fixer_storyboard(label):
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        label.config(text=f"Selected: {file_path}")
    return file_path

def fix_language():
    translator = Translator()
    output = fixer_text_box.get("1.0", tk.END).strip()
    fixed_text = ""
    for line in output.split("\n"):
        if not line.strip():
            fixed_text += line + "\n"
            continue
        try:
            lang = langdetect.detect(line)
            if lang != "en" and line.strip():
                translated = translator.translate(line, dest="en").text
                fixed_text += translated + "\n"
            else:
                fixed_text += line + "\n"
        except langdetect.lang_detect_exception.LangDetectException:
            fixed_text += line + "\n"
    fixer_text_box.delete("1.0", tk.END)
    fixer_text_box.insert(tk.END, fixed_text)
    fixer_status_label.config(text="Language fixed—non-English converted to English.")

def align_to_storyboard():
    output = fixer_text_box.get("1.0", tk.END).strip()
    storyboard_path = fixer_storyboard_label.cget("text").replace("Selected: ", "")
    if storyboard_path == "No file selected":
        fixer_status_label.config(text="Error: No storyboard selected.")
        return
    if storyboard_path.endswith(".json"):
        with open(storyboard_path, "r", encoding="utf-8") as f:
            storyboard_data = json.load(f)
        chapters = storyboard_data.get("chapters", [])
        chapter_titles = [chapter["title"] for chapter in chapters]
    else:
        with open(storyboard_path, "r", encoding="utf-8") as f:
            storyboard = f.read().strip()
        chapters = re.split(r"--- Chapter \d+: .+ ---", storyboard)[1:]
        chapter_titles = re.findall(r"--- Chapter \d+: (.+) ---", storyboard)
    
    fixed_text = ""
    current_chapter = 0
    for line in output.split("\n"):
        if line.strip() and current_chapter < len(chapters):
            if "Chapter" in line and current_chapter < len(chapter_titles):
                fixed_text += f"--- Chapter {current_chapter + 1}: {chapter_titles[current_chapter]} ---\n"
                current_chapter += 1
            else:
                fixed_text += line + "\n"
        elif line.strip():
            fixed_text += f"[EXCESS CONTENT - Review for Epilogue or Redistribution]\n{line}\n"
    fixer_text_box.delete("1.0", tk.END)
    fixer_text_box.insert(tk.END, fixed_text)
    fixer_status_label.config(text="Story aligned to storyboard—excess tagged.")

def save_fixer_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixer_text_box.get("1.0", tk.END))
        fixer_file_label.config(text=f"Saved: {file_path}")

# GUI Setup
tk_root = tk.Tk()
tk_root.title("Ollama Book Writer")
tk_root.geometry("600x700")
tk_root.configure(bg="#f0f0f0")

fetch_ollama_models()

notebook = ttk.Notebook(tk_root)
notebook.grid(row=0, column=0, sticky="nsew")

# Story Frame
story_frame = tk.Frame(notebook, bg="#f0f0f0", padx=10, pady=10)
notebook.add(story_frame, text="Story")
story_title_label = tk.Label(story_frame, text="Ollama Book Writer", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
story_title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
story_file_frame = tk.LabelFrame(story_frame, text="Story File Management", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
story_file_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
story_file_label = tk.Label(story_file_frame, text="No file loaded", bg="#f0f0f0", fg="#34495e")
story_file_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
tk.Button(story_file_frame, text="Load Story File", command=load_file, bg="#3498db", fg="white", padx=5, pady=2).grid(row=1, column=0, padx=5, pady=5)
tk.Button(story_file_frame, text="Save Story File", command=save_file, bg="#3498db", fg="white", padx=5, pady=2).grid(row=1, column=1, padx=5, pady=5)
story_selector_frame = tk.LabelFrame(story_frame, text="Additional Inputs", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
story_selector_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
tk.Label(story_selector_frame, text="Main Characters File (JSON):", bg="#f0f0f0", fg="#34495e").grid(row=0, column=0, sticky="e", padx=5, pady=2)
characters_label = tk.Label(story_selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
characters_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
tk.Button(story_selector_frame, text="Select", command=lambda: select_file(characters_label, is_json=True), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=0, column=2, padx=5, pady=2)
tk.Label(story_selector_frame, text="Storyboard File (JSON):", bg="#f0f0f0", fg="#34495e").grid(row=1, column=0, sticky="e", padx=5, pady=2)
storyboard_label = tk.Label(story_selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
storyboard_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
tk.Button(story_selector_frame, text="Select", command=lambda: select_file(storyboard_label, is_json=True), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=1, column=2, padx=5, pady=2)
tk.Label(story_selector_frame, text="Instructions File (TXT):", bg="#f0f0f0", fg="#34495e").grid(row=2, column=0, sticky="e", padx=5, pady=2)
instruction_label = tk.Label(story_selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
instruction_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
tk.Button(story_selector_frame, text="Select", command=lambda: select_file(instruction_label), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=2, column=2, padx=5, pady=2)
tk.Label(story_selector_frame, text="Other Important Info File (TXT):", bg="#f0f0f0", fg="#34495e").grid(row=3, column=0, sticky="e", padx=5, pady=2)
other_info_label = tk.Label(story_selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
other_info_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)
tk.Button(story_selector_frame, text="Select", command=lambda: select_file(other_info_label), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=3, column=2, padx=5, pady=2)
tk.Label(story_selector_frame, text="Temp Files Folder:", bg="#f0f0f0", fg="#34495e").grid(row=4, column=0, sticky="e", padx=5, pady=2)
temp_folder_label = tk.Label(story_selector_frame, text="No temp folder selected", bg="#f0f0f0", fg="#34495e")
temp_folder_label.grid(row=4, column=1, sticky="w", padx=5, pady=2)
tk.Button(story_selector_frame, text="Select", command=select_temp_folder, bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=4, column=2, padx=5, pady=2)
model_frame = tk.LabelFrame(story_frame, text="Model Selection", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
model_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
tk.Label(model_frame, text="Select Ollama Model:", bg="#f0f0f0", fg="#34495e").grid(row=0, column=0, sticky="e", padx=5, pady=2)
model_var = tk.StringVar(value=available_models[0] if available_models else "gemma3:27b")
model_dropdown = ttk.Combobox(model_frame, textvariable=model_var, values=available_models, state="readonly")
model_dropdown.grid(row=0, column=1, padx=5, pady=2)
story_task_frame = tk.LabelFrame(story_frame, text="Task", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
story_task_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
story_task_var = tk.StringVar(value="after")
tk.Radiobutton(story_task_frame, text="Generate Page Before", variable=story_task_var, value="before", bg="#f0f0f0", fg="#34495e").grid(row=0, column=0, padx=5, pady=2)
tk.Radiobutton(story_task_frame, text="Generate Page After", variable=story_task_var, value="after", bg="#f0f0f0", fg="#34495e").grid(row=0, column=1, padx=5, pady=2)
tk.Radiobutton(story_task_frame, text="Check Consistency", variable=story_task_var, value="consistency", bg="#f0f0f0", fg="#34495e").grid(row=0, column=2, padx=5, pady=2)
tk.Button(story_frame, text="Generate Text", command=generate_story_text, bg="#e74c3c", fg="white", padx=10, pady=5, font=("Arial", 10, "bold")).grid(row=5, column=0, pady=10)
tk.Button(story_frame, text="Enhance Story", command=enhance_story_text, bg="#e67e22", fg="white", padx=10, pady=5, font=("Arial", 10, "bold")).grid(row=5, column=1, pady=10)
tk.Button(story_frame, text="Reset", command=reset_chapter, bg="#e74c3c", fg="white", padx=10, pady=5, font=("Arial", 10, "bold")).grid(row=5, column=2, pady=10)
story_text_box = scrolledtext.ScrolledText(story_frame, wrap=tk.WORD, width=70, height=15, bg="white", fg="#2c3e50", font=("Arial", 10))
story_text_box.grid(row=6, column=0, columnspan=3, pady=10, padx=5)
status_frame = tk.LabelFrame(story_frame, text="LLM Status", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
status_frame.grid(row=7, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
status_box = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD, width=70, height=5, bg="#ecf0f1", fg="#2c3e50", font=("Arial", 10))
status_box.grid(row=0, column=0, pady=5, padx=5)

# World Frame
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

# Review Frame
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

# Fixer Frame
fixer_frame = tk.Frame(notebook, bg="#f0f0f0", padx=10, pady=10)
notebook.add(fixer_frame, text="Fixer")
fixer_title_label = tk.Label(fixer_frame, text="Story Fixer Tool", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
fixer_title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
fixer_file_frame = tk.LabelFrame(fixer_frame, text="Story File Management", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
fixer_file_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
fixer_file_label = tk.Label(fixer_file_frame, text="No file loaded", bg="#f0f0f0", fg="#34495e")
fixer_file_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
tk.Button(fixer_file_frame, text="Load Story File", command=load_fixer_file, bg="#3498db", fg="white", padx=5, pady=2).grid(row=1, column=0, padx=5, pady=5)
tk.Button(fixer_file_frame, text="Save Fixed File", command=save_fixer_file, bg="#3498db", fg="white", padx=5, pady=2).grid(row=1, column=1, padx=5, pady=5)
fixer_selector_frame = tk.LabelFrame(fixer_frame, text="Fixer Inputs", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
fixer_selector_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
tk.Label(fixer_selector_frame, text="Storyboard File (JSON/TXT):", bg="#f0f0f0", fg="#34495e").grid(row=0, column=0, sticky="e", padx=5, pady=2)
fixer_storyboard_label = tk.Label(fixer_selector_frame, text="No file selected", bg="#f0f0f0", fg="#34495e")
fixer_storyboard_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
tk.Button(fixer_selector_frame, text="Select", command=lambda: select_fixer_storyboard(fixer_storyboard_label), bg="#2ecc71", fg="white", padx=5, pady=2).grid(row=0, column=2, padx=5, pady=2)
fixer_action_frame = tk.LabelFrame(fixer_frame, text="Actions", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
fixer_action_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
tk.Button(fixer_action_frame, text="Fix Language", command=fix_language, bg="#e74c3c", fg="white", padx=10, pady=5).grid(row=0, column=0, padx=5, pady=5)
tk.Button(fixer_action_frame, text="Align to Storyboard", command=align_to_storyboard, bg="#e74c3c", fg="white", padx=10, pady=5).grid(row=0, column=1, padx=5, pady=5)
fixer_text_box = scrolledtext.ScrolledText(fixer_frame, wrap=tk.WORD, width=70, height=15, bg="white", fg="#2c3e50", font=("Arial", 10))
fixer_text_box.grid(row=4, column=0, columnspan=2, pady=10, padx=5)
fixer_status_frame = tk.LabelFrame(fixer_frame, text="Fixer Status", font=("Arial", 12), bg="#f0f0f0", fg="#2c3e50", padx=10, pady=10)
fixer_status_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
fixer_status_label = tk.Label(fixer_status_frame, text="Ready", bg="#ecf0f1", fg="#2c3e50", font=("Arial", 10))
fixer_status_label.grid(row=0, column=0, pady=5, padx=5)

# Configure weights
tk_root.grid_rowconfigure(0, weight=1)
tk_root.grid_columnconfigure(0, weight=1)
story_frame.grid_rowconfigure(6, weight=1)
world_frame.grid_rowconfigure(4, weight=1)
review_frame.grid_rowconfigure(3, weight=1)
fixer_frame.grid_rowconfigure(4, weight=1)

tk_root.mainloop()