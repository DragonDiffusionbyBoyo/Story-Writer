Here’s the entire README content in a single, unformatted text block for easy copying. I've removed all Markdown-specific formatting (like headers and code blocks) to ensure it pastes cleanly:

---

Ollama Book Writer

A Python-based GUI application built with Tkinter to assist writers in generating, reviewing, and expanding stories and world-building content using the Ollama API. The tool features three main tabs: Story, World Building, and Story Review, each designed to streamline the creative writing process.

Installation Instructions for Visual Studio Code

To set up and run this project in Visual Studio Code, follow these steps:

1. Install Visual Studio Code - Download and install VS Code from the official website (https://code.visualstudio.com/). Follow the installation prompts for your operating system (Windows, macOS, or Linux).

2. Install Python - Ensure Python 3.6+ is installed on your system. Download it from python.org (https://www.python.org/downloads/) if needed. Verify the installation by running python --version (or python3 --version on some systems) in your terminal.

3. Install the Python Extension for VS Code - Open VS Code. Go to the Extensions view by clicking the Extensions icon in the Activity Bar on the side (or press Ctrl+Shift+X / Cmd+Shift+X). Search for "Python" by Microsoft. Click "Install" to add the extension, which provides IntelliSense, linting, debugging, and more for Python development.

4. Set Up Your Environment in VS Code - Open the folder containing your project (e.g., File > Open Folder). Select the Python interpreter: Press Ctrl+Shift+P (or Cmd+Shift+P), type "Python: Select Interpreter," and choose your installed Python version.

5. Install Required Python Libraries - Open a terminal in VS Code (Terminal > New Terminal). Run the following command to install the necessary dependencies: pip install requests tkinter. Note: tkinter is typically included with Python, but ensure it’s available by running python -m tkinter in the terminal (a small window should appear).

6. Install Ollama - This script interacts with a local Ollama API at http://localhost:11434/api/generate. Install Ollama by following the instructions on the Ollama GitHub page (https://github.com/jmorganca/ollama). Start the Ollama server locally before running the script: ollama serve.

Overview

The Ollama Book Writer is a desktop application designed for writers to: Generate new story content (before or after existing text). Check story consistency. Expand world-building details (characters, places, lore). Review stories with summaries, structural analysis, and improvement suggestions. The app uses the Ollama API with specific models (HammerAI/mythomax-l2:13b-q4_K_M and nous-hermes2-mixtral:8x7b-dpo-q4_K_M) to process text and generate responses.

Features

Story Tab - Load/Save Story Files: Import and export .txt files containing your story. Additional Inputs: Optionally include files for characters, storyboard, instructions, and other info. Tasks: Generate a page before or after the loaded story. Check consistency (e.g., character details, plot coherence). Generate ~20,000 words for a prequel in 2,000-word chunks (for "before" task). Output: Displays generated text in a scrollable text box.

World Building Tab - Load/Save World Files: Manage .txt files with world-building content. Expansion Prompt: Add instructions to expand characters, places, or lore. Output: Appends generated details to the existing content.

Story Review Tab - Load Story File: Import a story for review. Generate Review: Produces a ~1,000-word summary, structural analysis, and improvement suggestions.

Prerequisites

- Python 3.6+
- Tkinter (included with most Python installations)
- Requests library (pip install requests)
- Ollama installed and running locally (http://localhost:11434)
- Compatible Ollama models: HammerAI/mythomax-l2:13b-q4_K_M, nous-hermes2-mixtral:8x7b-dpo-q4_K_M

How to Run

1. Clone or Download the Script - Save the script as ollama_book_writer.py (or any name you prefer).

2. Start the Ollama Server - In a terminal, run: ollama serve. Ensure the server is running at http://localhost:11434.

3. Run the Application - Open a terminal in the script’s directory and execute: python ollama_book_writer.py. The GUI window titled "Ollama Book Writer" will appear.

4. Usage - Navigate between tabs using the notebook interface. Load files, select tasks, and click "Generate" buttons to process your content. Save your work as needed.

Troubleshooting

- Ollama API Errors: Ensure the Ollama server is running and the correct models are installed. Check the terminal for error messages.
- Tkinter Not Found: Verify Tkinter is installed (python -m tkinter). On Linux, you may need sudo apt-get install python3-tk.
- No Text Generated: Confirm your input files are valid and the API is responding correctly.

Contributing

Feel free to fork this project, submit pull requests, or suggest improvements via issues. Contributions to enhance functionality, UI, or error handling are welcome!

License

This project is open-source and available under the MIT License (https://opensource.org/licenses/MIT).

---

All of this was inspired by Drift Johnson: https://www.youtube.com/@ScuffedEpoch/videos
https://www.scuffedepoch.com/
