import random
import os
import pandas as pd
from itertools import combinations
from datetime import datetime

from core.match import play_match_with_random_colors, MatchResult


def get_next_tournament_number(base_dir="results"):
    """
    Get the next available tournament number.
    
    Args:
        base_dir: Base directory for tournaments
        
    Returns:
        Next tournament number
    """
    tournaments_dir = os.path.join(base_dir, "tournaments")
    os.makedirs(tournaments_dir, exist_ok=True)
    
    # Find the highest tournament number
    max_num = 0
    for item in os.listdir(tournaments_dir):
        if item.startswith("tournament_") and item[11:].isdigit():
            num = int(item[11:])
            max_num = max(max_num, num)
    
    return max_num + 1


class TournamentBracket:
    def __init__(self, players, tournament_type="round_robin"):
        """
        Initialize a tournament bracket.
        
        Args:
            players: List of Player objects
            tournament_type: "round_robin" or "single_elimination"
        """
        self.players = players
        self.tournament_type = tournament_type
        self.rounds = []
        self.matches = []
        
        if tournament_type == "round_robin":
            self._generate_round_robin()
        elif tournament_type == "single_elimination":
            self._generate_single_elimination()
    
    def _generate_round_robin(self):
        """Generate round-robin tournament (every player plays every other player once)."""
        # Generate all possible pairings
        all_pairings = list(combinations(self.players, 2))
        
        # Shuffle the pairings to randomize order
        random.shuffle(all_pairings)
        
        # Organize into rounds (can be played concurrently in theory)
        # For simplicity, we'll organize them sequentially
        self.rounds = []
        current_round = []
        used_players = set()
        
        for match in all_pairings:
            if match[0].name not in used_players and match[1].name not in used_players:
                current_round.append(match)
                used_players.add(match[0].name)
                used_players.add(match[1].name)
                
                if len(current_round) == len(self.players) // 2:
                    self.rounds.append(current_round)
                    current_round = []
                    used_players = set()
        
        # Add remaining matches
        if current_round:
            self.rounds.append(current_round)
        
        # Flatten rounds to matches list
        self.matches = [match for round_matches in self.rounds for match in round_matches]
    
    def _generate_single_elimination(self):
        """Generate single elimination tournament bracket (First round only)."""
        # Shuffle players
        players = self.players.copy()
        random.shuffle(players)
        
        self.round_byes = {}  # Słownik do śledzenia modeli z wolnym losem
        round_matches = []
        
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                round_matches.append((players[i], players[i + 1]))
            else:
                # Obsługa nieparzystego gracza (otrzymuje wolny los w 1. rundzie)
                self.round_byes[0] = players[i] # 0 oznacza pierwszą rundę
                
        self.rounds.append(round_matches)
        self.matches = round_matches.copy()
    
    def get_matches(self):
        """Return all matches as a flat list."""
        return self.matches
    
    def get_rounds(self):
        """Return rounds structure."""
        return self.rounds


class TournamentRunner:
    def __init__(self, players, stockfish_path=None, tournament_type="round_robin", results_dir=None, verbose=False):
        """
        Initialize tournament runner.
        
        Args:
            players: List of Player objects
            stockfish_path: Path to stockfish executable
            tournament_type: "round_robin" or "single_elimination"
            results_dir: Directory to save tournament results (auto-numbered if None)
            verbose: Print move-by-move information for each match
        """
        self.players = players
        self.stockfish_path = stockfish_path
        self.tournament_type = tournament_type
        self.verbose = verbose
        self.bracket = None
        self.match_results = []
        self.tournament_results = []
        self.standings = {}
        self.tournament_start_time = datetime.now()
        
        # Auto-generate numbered tournament folder if not specified
        if results_dir is None:
            tournament_num = get_next_tournament_number()
            results_dir = os.path.join("results", "tournaments", f"tournament_{tournament_num}")
        
        self.results_dir = results_dir
        
        # Initialize standings
        for player in players:
            self.standings[player.name] = {
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'points': 0.0  # 1 for win, 0.5 for draw, 0 for loss
            }
    
    def generate_bracket(self):
        """Generate tournament bracket."""
        self.bracket = TournamentBracket(self.players, self.tournament_type)
        print(f"Tournament bracket generated ({self.tournament_type})")
        print(f"Total matches: {len(self.bracket.get_matches())}")
        print(f"Rounds: {len(self.bracket.get_rounds())}")
    
    def run_tournament(self, max_moves=200):
        """
        Run the tournament.
        
        Args:
            max_moves: Maximum moves per match
        """
        if not self.bracket:
            self.generate_bracket()
            
        os.makedirs(self.results_dir, exist_ok=True)
        print(f"\nRunning {self.tournament_type} tournament with {len(self.players)} players...")
        
        match_id = 1
        round_idx = 1
        
        # Używamy pętli while, ponieważ w single_elimination rundy dodają się w trakcie
        while round_idx <= len(self.bracket.get_rounds()):
            round_matches = self.bracket.rounds[round_idx - 1]
            
            # Print round schedule before executing
            print(f"\n{'='*70}")
            print(f"ROUND {round_idx} - Schedule")
            print(f"{'='*70}")
            for match_idx, (player1, player2) in enumerate(round_matches, 1):
                print(f"  Match {match_idx}: {player1.name} vs {player2.name}")
                
            # Wyświetlanie informacji o wolnym losie
            if hasattr(self.bracket, 'round_byes') and (round_idx - 1) in self.bracket.round_byes:
                print(f"  Bye: {self.bracket.round_byes[round_idx - 1].name} automatycznie awansuje dalej.")
            print()
            
            if not self.verbose:
                print(f"--- Round {round_idx} ---")
                
            advancing_players = []
            
            for match_idx, (player1, player2) in enumerate(round_matches, 1):
                match_id_str = f"R{round_idx}_M{match_idx}"
                
                # Play the match
                result = play_match_with_random_colors(
                    player1, player2, 
                    match_id_str,
                    self.stockfish_path,
                    max_moves,
                    self.results_dir,
                    verbose=self.verbose
                )
                
                self.match_results.append(result)
                
                # Update standings
                self._update_standings(result)
                
                # Record tournament result
                self.tournament_results.append({
                    'round': round_idx,
                    'match_id': match_id_str,
                    'white_player': result.white_player.name,
                    'black_player': result.black_player.name,
                    'winner': result.winner,
                    'result': result.result,
                    'termination_reason': result.termination_reason,
                    'total_moves': len(result.moves_data)
                })
                

                if self.tournament_type == "single_elimination":
                    if result.result == "win":
                        winner_player = result.white_player if result.winner == result.white_player.name else result.black_player
                    else:
                        # --- ROZSTRZYGANIE REMISU NA BAZIE CENTIPAWN ---
                        final_cp = 0
                        # Szukamy ostatniego ruchu, dla którego CP nie było None
                        for move_info in reversed(result.moves_data):
                            if move_info['centipawn_score'] is not None:
                                final_cp = move_info['centipawn_score']
                                break
                        
                        # UWAGA: Zakładamy, że wynik CP jest zawsze z perspektywy białych 
                        # (dodatni = przewaga białych, ujemny = przewaga czarnych)
                        if final_cp > 0:
                            winner_player = result.white_player
                            print(f"  [!] Remis. Przewagę pozycji (+{final_cp/100:.2f}) miał: {winner_player.name} (Białe).")
                        elif final_cp < 0:
                            winner_player = result.black_player
                            print(f"  [!] Remis. Przewagę pozycji ({final_cp/100:.2f}) miał: {winner_player.name} (Czarne).")
                        else:
                            # 0.0 oznacza idealną równość, wtedy używamy rzutu monetą
                            winner_player = random.choice([result.white_player, result.black_player])
                            print(f"  [!] Remis i pozycja całkowicie równa. Rzut monetą wygrywa: {winner_player.name}.")
                        # ------------------------------------------------
                            
                    advancing_players.append(winner_player)
                    
                match_id += 1
                
            # Generowanie kolejnej fazy dla trybu pucharowego
            if self.tournament_type == "single_elimination":
                # Dodajemy model, który pauzował (miał wolny los w tej rundzie)
                if hasattr(self.bracket, 'round_byes') and (round_idx - 1) in self.bracket.round_byes:
                    advancing_players.append(self.bracket.round_byes[round_idx - 1])
                
                # Jeśli mamy więcej niż 1 zawodnika, budujemy kolejną fazę
                if len(advancing_players) > 1:
                    next_round_matches = []
                    
                    for i in range(0, len(advancing_players), 2):
                        if i + 1 < len(advancing_players):
                            next_round_matches.append((advancing_players[i], advancing_players[i + 1]))
                        else:
                            # Zapisanie modelu na kolejny wolny los, jeśli ich liczba znów jest nieparzysta
                            self.bracket.round_byes[round_idx] = advancing_players[i]
                            
                    if next_round_matches:
                        self.bracket.rounds.append(next_round_matches)
                        self.bracket.matches.extend(next_round_matches)
                        
            round_idx += 1
            
        print("\n=== Tournament Complete ===")
        self._print_standings()
        self._save_tournament_results()
    
    def _update_standings(self, match_result: MatchResult):
        """Update standings based on match result."""
        white_name = match_result.white_player.name
        black_name = match_result.black_player.name
        
        if match_result.result == "win":
            winner = match_result.winner
            loser = black_name if winner == white_name else white_name
            
            self.standings[winner]['wins'] += 1
            self.standings[winner]['points'] += 1.0
            
            self.standings[loser]['losses'] += 1
        
        elif match_result.result == "draw":
            self.standings[white_name]['draws'] += 1
            self.standings[white_name]['points'] += 0.5
            
            self.standings[black_name]['draws'] += 1
            self.standings[black_name]['points'] += 0.5
    
    def _print_standings(self):
        """Print current tournament standings."""
        print("\nTournament Standings:")
        print("-" * 60)
        
        # Sort by points (descending)
        sorted_standings = sorted(
            self.standings.items(),
            key=lambda x: x[1]['points'],
            reverse=True
        )
        
        for rank, (player_name, stats) in enumerate(sorted_standings, 1):
            print(f"{rank}. {player_name:20} | Points: {stats['points']:5.1f} | "
                  f"W: {stats['wins']} D: {stats['draws']} L: {stats['losses']}")
    
    def _save_tournament_results(self):
        """Save tournament results to CSV files and generate summary bracket file."""
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Save match results
        results_df = pd.DataFrame(self.tournament_results)
        results_path = os.path.join(self.results_dir, "tournament_results.csv")
        results_df.to_csv(results_path, index=False)
        print(f"\nTournament results saved to: {results_path}")
        
        # Save final standings
        standings_data = []
        for rank, (player_name, stats) in enumerate(
            sorted(self.standings.items(), key=lambda x: x[1]['points'], reverse=True), 
            1
        ):
            standings_data.append({
                'rank': rank,
                'player': player_name,
                'points': stats['points'],
                'wins': stats['wins'],
                'draws': stats['draws'],
                'losses': stats['losses']
            })
        
        standings_df = pd.DataFrame(standings_data)
        standings_path = os.path.join(self.results_dir, "final_standings.csv")
        standings_df.to_csv(standings_path, index=False)
        print(f"Final standings saved to: {standings_path}")
        
        # Generate summary bracket file
        self._generate_bracket_summary()
    
    def _generate_bracket_summary(self):
        """Generate a text file with tournament bracket and results."""
        summary_path = os.path.join(self.results_dir, "tournament_bracket.txt")
        
        with open(summary_path, 'w') as f:
            # Header
            f.write("="*80 + "\n")
            f.write("TOURNAMENT BRACKET AND RESULTS\n")
            f.write("="*80 + "\n\n")
            
            # Tournament info
            f.write(f"Tournament Type: {self.tournament_type.upper()}\n")
            f.write(f"Total Players: {len(self.players)}\n")
            f.write(f"Players: {', '.join([p.name for p in self.players])}\n")
            f.write(f"Started: {self.tournament_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n" + "="*80 + "\n\n")
            
            # Match schedule and results by round
            for round_idx in range(1, len(self.bracket.get_rounds()) + 1):
                f.write(f"ROUND {round_idx}\n")
                f.write("-"*80 + "\n")
                
                round_results = [r for r in self.tournament_results if r['round'] == round_idx]
                
                for match_num, match_result in enumerate(round_results, 1):
                    f.write(f"\nMatch {match_num}: {match_result['match_id']}\n")
                    f.write(f"  White: {match_result['white_player']}\n")
                    f.write(f"  Black: {match_result['black_player']}\n")
                    f.write(f"  Result: {match_result['result'].upper()}\n")
                    
                    if match_result['winner']:
                        f.write(f"  Winner: {match_result['winner']}\n")
                    else:
                        f.write(f"  Result: DRAW\n")
                    
                    f.write(f"  Moves: {match_result['total_moves']}\n")
                    f.write(f"  Termination: {match_result['termination_reason']}\n")
                
                f.write("\n")
            
            # Final standings
            f.write("="*80 + "\n")
            f.write("FINAL STANDINGS\n")
            f.write("="*80 + "\n\n")
            
            sorted_standings = sorted(
                self.standings.items(),
                key=lambda x: x[1]['points'],
                reverse=True
            )
            
            for rank, (player_name, stats) in enumerate(sorted_standings, 1):
                f.write(f"{rank}. {player_name:20} - {stats['points']:5.1f} points ")
                f.write(f"({stats['wins']}W, {stats['draws']}D, {stats['losses']}L)\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write(f"TOURNAMENT WINNER: {sorted_standings[0][0] if sorted_standings else 'N/A'}\n")
            f.write("="*80 + "\n")
        
        print(f"Tournament bracket summary saved to: {summary_path}")
    
    def get_standings(self):
        """Return current standings sorted by points."""
        return sorted(
            self.standings.items(),
            key=lambda x: x[1]['points'],
            reverse=True
        )
    
    def get_winner(self):
        """Return tournament winner."""
        if self.standings:
            return self.get_standings()[0][0]
        return None
