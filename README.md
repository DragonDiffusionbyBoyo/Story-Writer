Windows instructions:

Install Ollama 
https://ollama.com/download/windows
Run the command ollama run <model name> “The code is set to llama3:8b by default, change this to the one you download. So for no buggering around just do olllama run llama3:8b in VS code or your preferred IDE type thing. 
Then in another terminal window in VS code for example run the python script: ollama_book_writer.py
A Gui will then appear.
Text File Formats for Ollama Book Writer GUI
- All files must be plain text (.txt), UTF-8 encoded.
- No strict structure required; write naturally.

1. Story File (Load Story File)
 Purpose: Existing story context.
 Content: Narrative fragment or full story so far.
 Example:
 Sir Eldric ventured into the Dark Forest, his armor glinting in the dim light.

2. Main Characters File (Select Characters File)
 Purpose: Describe main characters.
 Content: Names and traits, freeform.
 Example:
 Sir Eldric - Brave knight, seeking glory.
 Lady Mira - Cunning sorceress, fire magic expert.

3. Storyboard File (Select Storyboard File)
 Purpose: Outline story progression.
 Content: Sequence of events or scenes.
 Example:
 - Enter forest
 - Meet wolf
 - Find cave

4. What Should Happen Next File (Select Prompt File)
 Purpose: Guide next story part.
 Content: Directive or question.
 Example:
 What happens when Sir Eldric meets the lady?
5. Other Important Info File (Select Other Info File)
 Purpose: Extra story context.
 Content: World details or rules.
 Example:
Lady Mira has a really bad stutter. The world is set in a magical world but parodying real life. 
Sir eldric although gallant struggles to get around in his wheelchair. the roads and paths in the world are just grass tracks or mud tracks which complicate mobility for Sir Eldric.

Notes:
- Files are optional; unused sections are skipped.
- If no files, prompt becomes "Generate a story from scratch."
- Save with UTF-8 encoding (default in most editors).


All of this was inspired by Drift Johnson:
https://www.youtube.com/@ScuffedEpoch/videos

https://www.scuffedepoch.com/


