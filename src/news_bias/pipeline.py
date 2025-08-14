from news_bias.scraper import NewsScraper
from news_bias.analyzer import BiasAnalyzer
import pandas as pd
import time
import random
from pathlib import Path
from typing import Optional

def run_analysis(model_path: str, output_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Run the news bias analysis pipeline.

    Args:
        model_path: Path to the saved DistilBERT model
        output_dir: Optional directory to save results

    Returns:
        DataFrame with analysis results
    """
    # Initialize components
    scraper = NewsScraper()
    analyzer = BiasAnalyzer(model_path)

    # Collect headlines from all sources
    headlines_by_source = {}
    for source, url in scraper.sources.items():
        print(f"Scraping {source}...")
        headlines = scraper.get_headlines(source, url)
        headlines_by_source[source] = headlines

        # Be nice to servers
        time.sleep(random.uniform(1, 3))

    # Analyze headlines
    df = analyzer.analyze_sources(headlines_by_source)

    # Save results if output directory is provided
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        filename = output_path / f'bias_analysis_{df["timestamp"].iloc[0]}.csv'
        df.to_csv(filename, index=False)
        print(f"\nResults saved to: {filename}")

    # Print summary
    print("\nAnalysis Summary:")
    print("-" * 50)
    summary = df.groupby(['source', 'bias']).size().unstack(fill_value=0)
    summary['total'] = summary.sum(axis=1)
    print(summary)

    # Calculate bias percentages
    print("\nBias Percentages by Source:")
    print("-" * 50)
    percentages = summary.div(summary['total'], axis=0) * 100
    print(percentages[['Left', 'Right']].round(2))

    return df
