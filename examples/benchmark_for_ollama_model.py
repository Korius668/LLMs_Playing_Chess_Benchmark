import pandas as pd
from argparse import ArgumentParser

from players import OllamaPlayer
from benchmark import benchmark
from langchain_community.cache import SQLiteCache
import langchain

MIXTRAL = "mixtral:8x7b"
GEMMA = "gemma2:27b"
QWEN = "qwen2.5:72b"
LLAMA = "llama3:3.1b"
PHI = "phi3:3.8b"

MODEL_NAME = PHI
cache_db_path = "chess_benchmark_cache.db"
langchain.cache = SQLiteCache(database_path=cache_db_path)

fen_data = pd.read_csv("data/fen_analysis.csv")


def main():
    argParser = ArgumentParser(prog=f"benchmark_for_{MODEL_NAME}", description="Benchmarking Ollama model on chess positions.")
    argParser.add_argument("-l","--limit", type=int, default=1000, help="Number of chess positions to evaluate.")
    argParser.add_argument("-nc","--ignore_cache", default=True, action='store_false', help="Whether to use caching.")
    args = argParser.parse_args()
    
    model = OllamaPlayer(model_name=MODEL_NAME, verbose=True, cache=args.ignore_cache)
    benchmark(model, fen_data, results_path=f"results/{MODEL_NAME}_results.csv",  limit=args.limit)

if __name__ == "__main__":
    main()