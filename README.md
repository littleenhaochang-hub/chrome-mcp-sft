# Chrome MCP Supervised Fine-Tuning (SFT)

This repository contains the pipeline to fine-tune edge LLMs (like Llama-3-8B or Qwen-2.5-7B) to natively output Chrome MCP commands for web automation. The goal is to avoid the $O(N^2)$ context penalty of large DOM snapshots on local hardware (e.g., Apple Silicon unified memory).

## Architecture

1.  **Data Generation (`data_gen.py`)**: Uses a powerful cloud model (Gemini 2.5 Flash) acting as an Oracle through the Chrome MCP. It generates state-action pairs: `[Minified DOM -> Action]`. The DOM must be heavily truncated and minified (keeping it under 4K tokens) to mimic the exact input conditions an edge model will face.
2.  **Model Training (`notebooks/sft_chrome_mcp.ipynb`)**: Fine-tunes a base model via Unsloth/QLoRA on the generated JSONL dataset.
3.  **Inference**: The quantized GGUF model runs locally via OpenClaw/Ollama.

## Core Applications (Why We Are Doing This)

By training a local model to handle Chrome MCP, we unlock zero-cost, infinite-concurrency, and 100% private browser automation. Key use cases include:

1.  **Semantic Web Scraping / Alternative Data Extraction:** Scraping financial data, options pricing, or social sentiment (e.g., PTT, Reddit) that lack official APIs. The AI understands the DOM structure, making it immune to minor website redesigns that break traditional XPath scrapers.
2.  **Automated Hardware Research:** Navigating arXiv, ICLR, and GitHub to search, download, and parse new AI accelerator architectures automatically.
3.  **Travel Concierge & Flight Monitoring:** Continuously monitoring flight prices, award seat availability (e.g., EVA Air/ANA mileage tickets), and hotel rates across complex booking flows that block standard scrapers.
4.  **Secure Login Control & Session Management:** Handling complex, multi-step authentication flows (captchas, 2FA prompts, SSO login sequences) locally. Because the model runs on the edge (Mac Mini), sensitive credentials and session cookies never leave the physical machine.
5.  **Agentic RPA (Robotic Process Automation):** Cross-platform data entry and task execution, such as extracting invoices from webmail and automatically filling out ERP expense reports.

## Usage

*WIP*
