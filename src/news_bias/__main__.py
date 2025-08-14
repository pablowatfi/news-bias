from news_bias.pipeline import run_analysis
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='News Bias Analysis Tool')
    parser.add_argument('model_path', type=str, help='Path to the saved DistilBERT model')
    parser.add_argument('--output-dir', type=str, default='results',
                      help='Directory to save analysis results (default: results)')

    args = parser.parse_args()

    # Run analysis
    run_analysis(args.model_path, args.output_dir)

if __name__ == "__main__":
    main()
