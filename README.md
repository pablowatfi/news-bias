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

3. Set up the model:

The DistilBERT model was trained in Google Colab due to its computational requirements. The model files are not included in the repository due to their size. You have two options:

Option A: Train your own model
- Open `news_bias_finetune_distilbert_bias.ipynb` in Google Colab
- Follow the notebook instructions to train the model
- Download the resulting `bias_model` folder
- Place it in `src/news_bias/models/bias_model/`

Option B: Request access to the pre-trained model files and place them in the same location.

## Usage

1. Activate the poetry environment:
```bash
poetry shell
```

2. Run the bias analysis pipeline with the model path:
```bash
export MODEL_PATH=/path/to/news-bias/src/news_bias/models/bias_model
python -m news_bias
```

Or specify the model path directly:
```bash
MODEL_PATH=/path/to/news-bias/src/news_bias/models/bias_model python -m news_bias
```

This will:
1. Load the model from the specified path
2. Scrape headlines from configured news sources
3. Analyze them for political bias
4. Save results to a timestamped CSV file in the `results/` directory

Note: Make sure to replace `/path/to/news-bias` with your actual project path.

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

The model training process:

1. The included notebook `news_bias_finetune_distilbert_bias.ipynb` was developed and run in Google Colab to utilize its GPU resources
2. After training, the model files were downloaded and added to the project structure
3. The notebook remains in the repository for reference and reproducibility

To train your own model:

1. Open the notebook in Google Colab (recommended) or locally:
```bash
# Local execution (if you have sufficient GPU resources)
poetry run jupyter notebook news_bias_finetune_distilbert_bias.ipynb
```

2. Follow the notebook instructions to:
   - Prepare the training dataset
   - Fine-tune the DistilBERT model
   - Export and save the model files

3. Move the resulting `bias_model` folder to:
   ```
   src/news_bias/models/bias_model/
   ```

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
