
# GameAssets AI ⚔️

AI-powered tool for generating and transforming **game assets** (sprites, weapons, shields, relics, etc.) using FLUX.1 Kontext [dev]. Built for the **Black Forest Labs Hackathon**.

## 🚀 Features

-   Transform base sprites into fantasy-themed variations.
    
-   Generate assets like swords, shields, helmets, relics.
    
-   Powered by **fal.ai** API (FLUX.1 Kontext [dev]).
    
-   Local Python client with Gradio UI (planned).

## 📦 Installation

Clone the repo and create virtual environment:

```bash
git clone https://github.com/vero-code/gameassets-ai.git
cd gameassets-ai

python -m venv venv
venv\Scripts\activate
```

Install dependencies:
`pip install requirements.txt`

## 🔑 Setup

1.  Get your API key from fal.ai.
    
2.  Create a `.env` file in project root:
    
    `FAL_KEY=your_api_key_here`

## ▶️ Usage

Run test script:

`python src/test_api.py` 

It will send a request to FLUX.1 Kontext [dev] and return a generated image URL.

Example output:

`Generated image URL:  https://v3b.fal.media/files/...jpg  Size:  832  x  448  Inference time:  1.26  seconds` 

----------

## 📂 Project structure

```
gameassets-ai/
 ├─ src/
 │   └─ test_api.py
 ├─ venv/
 ├─ .env.example
 ├─ .gitignore
 ├─ README.md
 └─ requirements.txt
```