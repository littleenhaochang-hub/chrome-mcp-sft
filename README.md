# Chrome MCP Supervised Fine-Tuning (SFT)

This repository contains the pipeline to fine-tune edge LLMs (like Llama-3-8B or Qwen-2.5-7B) to natively output Chrome MCP commands for web automation. The goal is to avoid the $O(N^2)$ context penalty of large DOM snapshots on local hardware (e.g., Apple Silicon unified memory).

## Architecture

1.  **Data Generation (`data_gen.py`)**: Uses a powerful cloud model (Gemini 2.5 Flash) acting as an Oracle through the Chrome MCP. It generates state-action pairs: `[Minified DOM -> Action]`. The DOM must be heavily truncated and minified (keeping it under 4K tokens) to mimic the exact input conditions an edge model will face.
2.  **Model Training (`notebooks/sft_chrome_mcp.ipynb`)**: Fine-tunes a base model via Unsloth/QLoRA on the generated JSONL dataset.
3.  **Inference**: The quantized GGUF model runs locally via OpenClaw/Ollama.

## Usage

*WIP*
