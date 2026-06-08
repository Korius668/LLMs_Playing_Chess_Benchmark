import os
import sys
from argparse import ArgumentParser
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from players import OllamaPlayer, RandomMovePlayer
from core.tournament import TournamentRunner

# Load environment variables
load_dotenv()
stockfish_path = os.getenv("STOCKFISH_PATH")

# Model names
MIXTRAL = "mixtral:8x7b"
GEMMA = "gemma2:27b"
QWEN = "qwen2.5:72b"
LLAMA = "llama3.1:8b"
PHI = "phi3:3.8b"

AVAILABLE_MODELS = {
    "mixtral": MIXTRAL,
    "gemma": GEMMA,
    "qwen": QWEN,
    "llama": LLAMA,
    "phi": PHI,
    "random": None
}


def create_player(model_spec):
    """
    Create a player from model specification.
    
    Args:
        model_spec: Either a model name key or a tuple (name, model_name)
    
    Returns:
        Player object
    """
    if isinstance(model_spec, tuple):
        name, model_name = model_spec
    else:
        name = model_spec
        model_name = AVAILABLE_MODELS.get(model_spec.lower())
    
    if model_name is None:
        # Random player
        return RandomMovePlayer(name=name.upper())
    else:
        # Ollama player
        return OllamaPlayer(model_name=model_name, name=name.upper(), cache=True)


def run_tournament(models, tournament_type="round_robin", max_moves=200, verbose=False):
    """
    Run a chess tournament between specified models.
    
    Args:
        models: List of model names (keys from AVAILABLE_MODELS)
        tournament_type: "round_robin" or "single_elimination"
        max_moves: Maximum moves per match
        verbose: Print move-by-move information for each match
    """
    print(f"Initializing players for tournament...")
    
    # Create player objects
    players = [create_player(model) for model in models]
    
    print(f"Players: {[p.name for p in players]}")
    
    # Create and run tournament (auto-numbered folder)
    tournament = TournamentRunner(
        players,
        stockfish_path=stockfish_path,
        tournament_type=tournament_type,
        results_dir=None,  # Auto-generate numbered folder
        verbose=verbose
    )
    
    tournament.generate_bracket()
    tournament.run_tournament(max_moves=max_moves)
    
    # Print final results
    print("\n" + "="*60)
    print("FINAL TOURNAMENT RESULTS")
    print("="*60)
    standings = tournament.get_standings()
    for rank, (player_name, stats) in enumerate(standings, 1):
        print(f"{rank}. {player_name:20} - {stats['points']:.1f} points "
              f"({stats['wins']}W, {stats['draws']}D, {stats['losses']}L)")
    
    print(f"\nTournament Winner: {tournament.get_winner()}")
    print(f"\nResults saved to: {tournament.results_dir}")


def main():
    parser = ArgumentParser(
        description="Run a chess tournament between Ollama models."
    )
    parser.add_argument(
        "-m", "--models",
        type=str,
        default="llama,phi,mixtral,qwen,random",
        help="Comma-separated list of models to include in tournament. "
             "Available: mixtral, gemma, qwen, llama, phi, random. "
             "Default: llama,phi,mixtral,random"
    )
    parser.add_argument(
        "-t", "--tournament-type",
        type=str,
        choices=["round_robin", "single_elimination"],
        default="single_elimination",
        help="Tournament type. Default: single_elimination"
    )
    parser.add_argument(
        "-n", "--max-moves",
        type=int,
        default=200,
        help="Maximum moves per match. Default: 200"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print move-by-move information for each match"
    )
    
    args = parser.parse_args()
    
    # Parse models
    model_names = [m.strip().lower() for m in args.models.split(",")]
    
    # Validate models
    for model in model_names:
        if model not in AVAILABLE_MODELS:
            print(f"Error: Unknown model '{model}'")
            print(f"Available models: {', '.join(AVAILABLE_MODELS.keys())}")
            sys.exit(1)
    
    # Run tournament
    run_tournament(model_names, args.tournament_type, args.max_moves, args.verbose)


if __name__ == "__main__":
    main()

