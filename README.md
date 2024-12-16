# Automated Data Analysis Project

## Overview

In this project, I have developed an automated Python script, `autolysis.py`, to perform data analysis, create visualizations, and narrate a story from the provided dataset. The script performs various statistical analyses on any given CSV dataset, generates relevant visualizations, and creates a narrative summarizing the findings.

The dataset used can be any of the following:
- `goodreads.csv`: A dataset containing information about 10,000 books, including genres, ratings, etc.
- `happiness.csv`: Data from the World Happiness Report.
- `media.csv`: Ratings of movies, TV series, and books.

The script leverages a Large Language Model (LLM) to analyze the data and summarize the results dynamically.

## How to Use

To run the script and perform automated analysis, use the following command:

```bash
uv run autolysis.py dataset.csv
