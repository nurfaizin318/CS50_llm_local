# Local LLM Chat Application

## Video Demo : https://youtu.be/ck39K0Dcbec
## Description
This project is a web-based chat application similar to ChatGPT that runs a local Large Language Model using MLX on Apple Silicon.

Users can register, log in, and chat with a locally hosted LLM. Conversations are saved per user and can be revisited.

## Features
- User authentication (JWT)
- Local LLM inference using MLX
- Chat history per user
- ChatGPT-like UI
- Runs fully offline

## Technologies
- Python (Flask)
- MLX (Apple Silicon)
- MySQL
- Tailwind CSS
- JavaScript (Fetch API)

## How to Run
```bash
source venv/bin/activate
python download_model.py
pip install -r requirements.txt
execute mysql script on "schema_db.txt"
python app.py