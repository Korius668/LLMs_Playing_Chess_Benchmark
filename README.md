# LLMs Playing Chess Benchmark

A benchmark project for evaluating Large Language Models (LLMs) in playing chess. This project allows you to pit LLMs against each other or against simple bots in a chess game, with an optional GUI for visualization.

## Features

- Modular player system (LLM players, random bots)
- Chess engine integration using python-chess
- GUI visualization using CustomTkinter and SVG rendering
- Support for Ollama-based LLMs

## Installation

### Prerequisites

- Python 3.8 or higher
- Ollama installed and running (for LLM players)
- Virtual environment (recommended)

### Steps

1. Clone or download the project repository.

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install the project and its dependencies:
   ```bash
   pip install -e .
   ```

   This will install all required dependencies including:
   - python-chess: Chess engine
   - customtkinter: GUI framework
   - langchain-community: For Ollama integration
   - svglib, reportlab, pillow: For SVG to image conversion in GUI

### Optional Dependencies

If you only need the core functionality without GUI:
```bash
pip install -e .[gui]
```

## Usage

### Running the Benchmark

To start the chess benchmark with GUI:

```bash
chess-benchmark
```

Or directly:

```bash
python -m src.main
```

This will launch a GUI where you can watch LLMs play against each other.

### Configuration

In `src/main.py`, you can configure the players:

- `RandomMockModel`: A simple random move bot
- `OllamaPlayer`: An LLM player using Ollama (requires Ollama running with a model like llama3)

Example:
```python
player_white = RandomMockModel(name="RandomBot")
player_black = OllamaPlayer(model_name="llama3", name="Llama-AI")
```

### Running Without GUI

Modify `src/main.py` to remove the GUI parts if you want a headless benchmark.

## Requirements

- **Ollama**: For LLM players, install Ollama from [ollama.ai](https://ollama.ai) and pull a model:
  ```bash
  ollama pull llama3
  ```

## Project Structure

```
src/
├── main.py              # Entry point
├── engine.py            # (Currently empty)
├── core/
│   ├── game_manager.py  # Game logic
│   └── player_base.py   # Base player class
├── gui/
│   └── board_view.py    # GUI components
└── players/
    └── ollama_player.py # Ollama-based player
examples/
├── play_GUI.py
└── play_with_LLM.py
```

## Contributing

Feel free to add more player types, improve the GUI, or enhance the benchmark logic.

## License

[Add your license here]</content>
<parameter name="filePath">d:\Projekty\LLMs_Playing_Chess_Benchmark\README.md