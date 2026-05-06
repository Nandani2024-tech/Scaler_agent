# Scaler Agent — CLI AI Agent

A conversational CLI agent designed to clone the Scaler Academy website dynamically using NVIDIA's API (moonshotai/kimi-k2-instruct model). The agent follows a strict reasoning loop (START → THINK → TOOL → OBSERVE → OUTPUT) to perform tasks like file creation and browser integration.

## Features
- **Conversational CLI**: Chat directly with the agent in your terminal.
- **Dynamic Web Cloning**: Generates a visually similar clone of scaler.com.
- **Real-Time Research**: Fetches live data (colors, text, structure) from websites to ensure high-fidelity clones.
- **Tool-Based Execution**: Uses specialized tools to research, create folders, files, and open them in the browser.
- **Transparent Reasoning**: View the agent's thought process step-by-step.

## Folder Structure
```text
scaler-agent/
├── main.py                  # CLI entry point
├── agent.py                 # Core agent reasoning loop
├── tools/
│   ├── __init__.py          # Tool registry
│   ├── file_tools.py        # File and folder utilities
│   ├── browser_tools.py     # Browser integration
│   └── web_tools.py         # Real-time website data fetching
├── prompts/
│   └── system_prompt.py     # System instructions for Claude
├── output/                  # Generated assets and HTML files
├── .env                     # API key configuration
├── requirements.txt         # Project dependencies
└── README.md                # Documentation
```

## Setup Instructions

1. **Clone the repository** (if not already done).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure API Key**:
   Create a `.env` file in the root directory and add your NVIDIA API key:
   ```text
   NVIDIA_API_KEY=nvapi-your_key_here
   ```

## How to Run

Start the agent by running:
```bash
python main.py
```

### Example Prompts
- "Clone the Scaler website and open it in my browser."
- "Create a new folder called 'scaler_test' and save a welcome note there."
- "Build a hero section for a coding platform using Scaler's colors."

## Important Notes
- The agent is configured to use the `meta/llama-3.3-70b-instruct` model via NVIDIA.
- All generated web content is saved in the `output/` directory by default.
