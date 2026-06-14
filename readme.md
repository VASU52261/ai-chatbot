# Chatbot Application

A command-line chatbot application using Python and the Gemini API.

## Environment Setup

1. Create the conda environment:
   ```bash
   conda create -n iisc_env python=3.10 -y
   ```
2. Activate the environment:
   ```bash
   conda activate iisc_env
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Setup your API key:
   The `.env` file already contains the API key configuration.
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

Run the chatbot:
```bash
python bot.py
```

To exit the chatbot, type `exit`, `quit`, `stop`, or `end`.
