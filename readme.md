

# AI Chatbot

A feature-rich AI chatbot built with Google Gemini and Python Tkinter.
Supports voice output, document QA, multilingual conversations, 
dark/light themes, and chat history management.

## Features

- Real-time streaming responses from Gemini 2.5 Flash
- Text-to-speech voice output with pause, resume, stop controls
- Document QA — upload PDF, DOCX, TXT and ask questions about it
- Dynamic system prompt loading — change bot behavior at runtime
- Dark and light theme toggle
- Chat history save and load as JSON
- Export conversations as TXT
- Multilingual support — responds in Kannada, Tamil, Telugu, Hindi and more
- Message avatars and timestamps on every message
- Typing indicator while bot is thinking
- Character counter on input box
- Font size and font family controls
- Status bar showing model name and message count

## Tech Stack

- Language: Python 3.10+
- UI Framework: Tkinter
- AI Model: Google Gemini 2.5 Flash Lite
- Text to Speech: Edge TTS + Pygame
- Document Processing: PyMuPDF, python-docx, BeautifulSoup
- Environment: python-dotenv

## Project Structure
ai-chatbot/
├── UI.py 
├── bot.py 
├── tts.py 
├── doc_process.py 
├── requirements.txt 
└── README.md


## Getting Started

### Prerequisites
- Python 3.10+


### Installation

```bash
git clone 
cd ai-chatbot
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root folder

### Run the Chatbot

```bash
python UI.py
```

Or if using Anaconda:
```bash
C:\Users\Dell\anaconda3\python.exe UI.py
```

## Usage

- Type your message and press Enter or click Send
- Use File menu to load a system prompt or document
- Use File menu to save or load chat history
- Toggle dark/light theme using the button in the top right
- Enable or disable voice output using the Voice checkbox

## Supported Languages

Responds accurately in native script for:
Kannada, Tamil, Telugu, Hindi, Malayalam, Bengali,
and all major global languages.


