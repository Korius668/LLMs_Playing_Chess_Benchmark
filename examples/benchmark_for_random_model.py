import pandas as pd
from argparse import ArgumentParser

from players import RandomMovePlayer
from benchmark import benchmark

MODEL_NAME = "random"
fen_data = pd.read_csv("data/fen_analysis.csv")

def main():
    argParser = ArgumentParser(prog=f"benchmark_for_{MODEL_NAME}", description="Benchmarking Random model on chess positions.")
    argParser.add_argument("-l","--limit", type=int, default=1000, help="Number of chess positions to evaluate.")
    argParser.add_argument("-nc","--ignore_cache", default=True, action='store_false', help="Whether to use caching.")
    args = argParser.parse_args()
    
    model = RandomMovePlayer(name=MODEL_NAME)
    
    benchmark(model, fen_data, results_path=f"results/{MODEL_NAME}_model_results.csv", limit=args.limit)



if __name__ == "__main__":
    main()