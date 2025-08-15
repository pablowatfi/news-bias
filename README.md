# News Bias Detection

This project implements a news bias detection system using DistilBERT to analyze political bias in news headlines. It includes both a web scraper for collecting headlines from major news sources and a machine learning model for bias classification.

## Features

- Web scraping of major news outlets (The Economist, Washington Post, NYT, Fox News, NBC, HuffPost)
- Robust scraping with retry logic and user-agent rotation
- DistilBERT-based bias classification model
- Real-time analysis of news headlines
- CSV export of analysis results

## Prerequisites

- Python 3.12+
- Poetry (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pablowatfi/news-bias.git
cd news-bias
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Download the model files:

The model files are not included in the repository due to their size. You can either:
- Train your own model using the Jupyter notebook `news_bias_finetune_distilbert_bias.ipynb`
- Request access to the pre-trained model files

Place the model files in `src/news_bias/models/bias_model/`.

## Usage

1. Activate the poetry environment:
```bash
poetry shell
```

2. Run the bias analysis pipeline:
```bash
python -m news_bias
```

This will:
1. Scrape headlines from configured news sources
2. Analyze them for political bias
3. Save results to a CSV file in the `results/` directory

## Project Structure

```
news-bias/
├── src/
│   └── news_bias/
│       ├── __init__.py
│       ├── __main__.py
│       ├── analyzer.py      # Bias detection model implementation
│       ├── pipeline.py      # Main processing pipeline
│       ├── scraper.py       # News website scraping
│       └── models/          # Pre-trained model files (not in repo)
├── tests/
├── results/                 # Analysis output files
├── poetry.lock
└── pyproject.toml
```

## Development

To train your own model:

1. Open the Jupyter notebook:
```bash
poetry run jupyter notebook news_bias_finetune_distilbert_bias.ipynb
```

2. Follow the notebook instructions to:
   - Prepare training data
   - Fine-tune the DistilBERT model
   - Save the model files

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Notes

- The scraper includes rate limiting and respects robots.txt
- Model files are excluded from git due to size (use git LFS if needed)
- Results are saved with timestamps in the `results/` directory
