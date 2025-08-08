# ChatGPT Micro-Cap Experiment
Welcome to the repo behind my 6-month live trading experiment where ChatGPT manages a real-money micro-cap portfolio.

# The Concept
Everyday, I kept seeing the same ad about having an some A.I. pick undervalued stocks. It was obvious it was trying to get me to subscribe to some garbage, so I just rolled my eyes. 
Then I started wondering, "How well would that actually work?".

So, starting with just $100, I wanted to answer a simple but powerful question:

**Can powerful large language models like ChatGPT actually generate alpha (or at least make smart trading decisions) using real-time data?**

## Each trading day:

- I provide it trading data on the stocks in it's portfolio.

- Strict stop-loss rules apply.

- Everyweek I allow it to use deep research to reevaluate it's account.

- I track and publish performance data weekly on my blog. [SubStack Link](https://nathanbsmith729.substack.com)

## Documentation

Additional project notes, prompts, and disclaimers live in [`docs/experiment_details`](docs/experiment_details).

# Performance Example (6/30 – 7/25)

---

![Week 4 Performance](docs/results-6-30-7-25.png)

---
- Currently stomping on the Russell 2K.

# Features of This Repo
Live trading scripts — Used to evaluate prices and update holdings daily

LLM-powered decision engine — ChatGPT picks the trades

Performance tracking — CSVs with daily PnL, total equity, and trade history

Visualization tools — Matplotlib graphs comparing ChatGPT vs Index

Logs & trade data — Auto-saved logs for transparency

# Why This Matters
AI is being hyped across every industry, but can it really manage money without guidance?

This project is an attempt to find out, with transparency, data, and a real budget.

# Tech Stack
Basic Python 

Pandas + yFinance for data & logic

Matplotlib for visualizations

ChatGPT for decision-making

# Installation
To run the scripts locally, install the Python dependencies:

```
pip install -r requirements.txt
```

# Supported Scripts

- `scripts/generate_graph.py` — plot portfolio performance against the S&P 500.

# Testing and Code Coverage

Unit tests live in the `tests/` directory. A helper script `scripts/run_tests_with_coverage.py` runs the suite and enforces a default 95% coverage threshold.

```
python scripts/run_tests_with_coverage.py
```

To view coverage without failing on the current percentage, supply a lower minimum:

```
python scripts/run_tests_with_coverage.py --min 0
```

Additional tests should be added until the 95% requirement is met.

# Follow Along
The experiment runs June 2025 to December 2025.
Every trading day I will update the portfolio CSV file.
If you feel inspired to do something simiar, feel free to use this as a blueprint.

Updates are posted weekly on my blog — more coming soon!

One final shameless plug: (https://substack.com/@nathanbsmith?utm_source=edit-profile-page)

Find a mistake in the logs or have advice?
Please Reach out here: nathanbsmith.business@gmail.com

## Streamlit Dashboard

This repository now ships with a lightweight Streamlit dashboard for managing
the experimental portfolio locally.

### Installation

```
pip install -r requirements.txt
```

### Running the App

```
streamlit run app.py
```

The application stores data in the `data/` directory so it survives across
restarts.  If you encounter issues, ensure this folder is writable and that the
CSV files are not open in another program.
