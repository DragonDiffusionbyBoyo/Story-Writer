

### README.md

```markdown
# Ollama Book Writer

Welcome to **Ollama Book Writer**, a Python tool that uses the Ollama API to craft, enhance, review, and fix stories! Whether you're spinning a tale of interdimensional chickens or gritty detective dramas, this script has you covered. Feed it a storyboard, characters, and some instructions, and watch it churn out chapters faster than you can say "plot twist."

## Features

- **Story Tab**: Generate chapters (2000+ words) based on a JSON storyboard, starting from an initial text file.
- **WIP World Building Tab**: Expand your world’s characters, places, or lore with custom prompts.
- **WIP Story Review Tab**: Get a detailed summary, analysis, and improvement suggestions for your story.
- **Fixer Tab**: Fix language issues or align your story to its storyboard.
- **GUI**: A sleek Tkinter interface to manage files and generation tasks.

## Prerequisites

- Python 3.6+
- Required libraries: `tkinter`, `requests`, `json`, `os`, `logging`, `langdetect`, `googletrans==3.1.0a0`
- Ollama server running locally (`http://localhost:11434`)
Get Ollama from HERE https://ollama.com/download download windows version as I have only tested this on windows.
Once Ollama is installed do this
Suggested model I have tested on is gemma3:27b so open command prompt and copy and paste this  ollama pull gemma3:27b

Install dependencies:
```bash
pip install requests langdetect googletrans==3.1.0a0
```

## Setup

1. Clone this repository:
   ```bash
   https://github.com/DragonDiffusionbyBoyo/Story-Writer
   cd ollama-book-writer
   ```
2. Start your Ollama server:
   ```bash
   ollama serve
   ```
3. Run the script:
   ```bash
   python ollama_book_writer.py
   ```

## Usage

1. **Load Files**: Use the GUI to load your initial story, storyboard (JSON), characters (JSON), instructions (TXT), and other info (TXT).
2. **Select Model**: Choose an Ollama model from the dropdown (fetches available models automatically).
3. **Generate**: Click "Generate Text" to write chapters, "Enhance Story" to double the size, or explore other tabs.
4. **Save**: Export your masterpiece!

Files are saved to a temp folder (default: current directory) as `temp_chapter_X.txt` or `temp_story_final.txt`.

## Example Files

Here’s a silly story about **Bingo the Chicken** and **Waffle the Waffle** to get you started:

### 1. Initial Story File (`initial_story.txt`)
```
Bingo the Chicken clucked furiously at the sky, wondering why it glowed purple. Waffle the Waffle, her crispy companion, just sighed and dripped syrup.
```

### 2. Storyboard File (`storyboard.json`)
```json
{
  "chapters": [
    {
      "number": 8,
      "title": "The Syrup Siege",
      "setting": "A sticky battlefield of pancakes",
      "characters_present": ["Bingo", "Waffle"],
      "sections": [
        {"task": "Bingo rallies the chickens against syrup cannons", "word_count": 500, "instructions": "Show her pluckiness"},
        {"task": "Waffle gets stuck, whines about his batter", "word_count": 400, "instructions": "Add melodrama"}
      ],
      "goal": "Bingo takes charge, Waffle flounders"
    },
    {
      "number": 9,
      "title": "Feathers vs. Flapjacks",
      "setting": "A diner in chaos",
      "characters_present": ["Bingo", "Waffle"],
      "sections": [
        {"task": "Bingo negotiates with a rogue toaster", "word_count": 400, "instructions": "Witty banter"},
        {"task": "Waffle accidentally starts a butter avalanche", "word_count": 500, "instructions": "Slapstick chaos"}
      ],
      "goal": "Escalating absurdity"
    },
    {
      "number": 10,
      "title": "The Great Breakfast Brawl",
      "setting": "A breakfast dimension",
      "characters_present": ["Bingo", "Waffle"],
      "sections": [
        {"task": "Bingo rides a bacon dragon", "word_count": 500, "instructions": "Epic and ridiculous"},
        {"task": "Waffle crowns himself Syrup King", "word_count": 400, "instructions": "Over-the-top glory"}
      ],
      "goal": "A tasty finale"
    }
  ],
  "notes": {
    "tone": "Silly and absurd",
    "word_count": "Aim for ~2,000 words per chapter",
    "focus": "Bingo’s bravery, Waffle’s whining"
  }
}
```

### 3. Characters File (`characters.json`)
```json
{
  "Bingo": {
    "full_name": "Bingo Bawksworth",
    "role": "Fearless chicken leader",
    "traits": ["Brave", "Clucky", "Sassy"],
    "quotes": ["Cluck first, ask later!", "This sky’s gone bonkers!"],
    "arc": "From farmyard hen to breakfast hero",
    "details": "Fluffy feathers, tiny crown"
  },
  "Waffle": {
    "full_name": "Waffle W. Crispinton",
    "role": "Whiny sidekick",
    "traits": ["Crispy", "Dramatic", "Sticky"],
    "quotes": ["My batter’s ruined!", "Syrup’s my destiny!"],
    "arc": "From snack to reluctant royalty",
    "details": "Golden brown, soggy edges"
  }
}
```

### 4. Instructions File (`instructions.txt`)
```
Focus on absurd humor and breakfast puns. Keep Bingo bold and Waffle over-the-top whiny. Each chapter should escalate the silliness while sticking to the storyboard’s goals. Use vivid food imagery!
```

### 5. Other Important Information (`other_info.txt`)
```
The world is a chaotic breakfast dimension where food fights for dominance. Purple skies signal the Breakfast Overlord’s return. Bingo and Waffle are the last hope against a syrup-soaked doom.
```

## Contributing

Feel free to fork, tweak, or add your own absurd stories! Submit a pull request with your changes.

## License

MIT License - free to use, modify, and share. Happy writing!
```

---

### Notes on Example Files

- **Initial Story**: Two lines as requested, setting up Bingo and Waffle.
- **Storyboard**: Chapters 8-10 with random, silly tasks, adhering to the JSON format from your example.
- **Characters**: Two characters in the same JSON structure, with fun traits and arcs.
- **Instructions**: Derived from the script’s use of `instruction_text` in prompts, tailored to the silly story.
- **Other Info**: Adds world context, as used in the script’s `other_info_text`.

Let me know if you’d like me to refine the code fixes or tweak anything else before you push to GitHub!
