# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
#   "numpy",
#   "matplotlib",
#   "seaborn",
#   "pillow",
#   "python-dotenv",
#   "requests",
# ]
# ///

# Import necessary modules
from dotenv import load_dotenv
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# Load environment variables from the .env file
load_dotenv()

# Retrieve API key from environment variables
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    print("Error: AIPROXY_TOKEN environment variable is not set in the .env file.")
    sys.exit(1)

# Define the AI Proxy URL
AI_PROXY_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

def analyze_dataset(file_path):
    """
    Analyze the dataset and return summaries, statistics, and insights.

    Args:
        file_path (str): Path to the CSV file to analyze.

    Returns:
        df (DataFrame): The dataset as a pandas DataFrame.
        summary (dict): Basic information about the dataset.
        numeric_summary (dict): Statistical summary of numeric columns.
        correlation_matrix (DataFrame): Correlation matrix of numeric columns.
    """
    try:
        # Load the dataset with explicit encoding
        df = pd.read_csv(file_path, encoding='ISO-8859-1')  # Use a common encoding

        # Gather basic information about the dataset
        summary = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "example_values": df.head(3).to_dict(),
        }

        # Generate a statistical summary for numeric columns
        numeric_summary = df.describe().to_dict()

        # Compute the correlation matrix for numeric data
        correlation_matrix = df.corr(numeric_only=True)

        return df, summary, numeric_summary, correlation_matrix

    except UnicodeDecodeError as e:
        # Handle dataset encoding errors
        print(f"Error decoding the dataset: {e}")
        print("Try using a different encoding, e.g., 'ISO-8859-1' or 'latin1'.")
        sys.exit(1)
    except Exception as e:
        # Handle other exceptions during dataset loading or analysis
        print(f"Error loading or analyzing the dataset: {e}")
        sys.exit(1)

def visualize_dataset(df, correlation_matrix, file_path):
    """
    Generate visualizations specific to the dataset and save as PNG files.

    Args:
        df (DataFrame): The dataset to generate visualizations for.
        correlation_matrix (DataFrame): The correlation matrix for the dataset.
        file_path (str): The path to the dataset file.

    Returns:
        charts (list): A list of filenames for the generated charts.
    """
    charts = []
    dataset_name = os.path.splitext(os.path.basename(file_path))[0]

    # Create visualizations based on dataset type
    if "goodreads" in file_path.lower():
        # Histogram: Distribution of Goodreads ratings
        if "average_rating" in df.columns:
            plt.figure(figsize=(8, 6))
            df["average_rating"].hist(bins=30, color="purple", edgecolor="black")
            plt.title("Distribution of Goodreads Ratings")
            plt.xlabel("Average Rating")
            plt.ylabel("Frequency")
            plt.savefig("goodreads_ratings.png")
            charts.append("goodreads_ratings.png")
            plt.close()
        else:
            print("Column 'average_rating' is missing. Skipping histogram.")

        # Bar chart: Top 10 authors by total ratings count
        if "authors" in df.columns and "ratings_count" in df.columns:
            plt.figure(figsize=(10, 6))
            top_authors = df.groupby("authors")["ratings_count"].sum().nlargest(10)
            top_authors.plot(kind="bar", color="lightblue", edgecolor="black")
            plt.title("Top 10 Authors by Total Ratings Count")
            plt.xlabel("Authors")
            plt.ylabel("Total Ratings Count")
            plt.tight_layout()
            plt.savefig("goodreads_top_authors.png")
            charts.append("goodreads_top_authors.png")
            plt.close()
        else:
            print("Required columns for bar chart are missing. Skipping top authors chart.")

        # Scatter plot: Average rating vs ratings count
        if "average_rating" in df.columns and "ratings_count" in df.columns:
            plt.figure(figsize=(8, 6))
            sns.scatterplot(data=df, x="average_rating", y="ratings_count", alpha=0.6)
            plt.title("Average Rating vs Ratings Count")
            plt.xlabel("Average Rating")
            plt.ylabel("Ratings Count")
            plt.tight_layout()
            plt.savefig("goodreads_ratings_vs_count.png")
            charts.append("goodreads_ratings_vs_count.png")
            plt.close()
        else:
            print("Required columns for scatter plot are missing. Skipping ratings vs count.")

        # Line plot: Average rating over years
        if "original_publication_year" in df.columns and "average_rating" in df.columns:
            plt.figure(figsize=(12, 6))
            avg_rating_by_year = df.groupby("original_publication_year")["average_rating"].mean()
            avg_rating_by_year.plot(kind="line", color="orange", linewidth=2)
            plt.title("Average Rating Over Years")
            plt.xlabel("Original Publication Year")
            plt.ylabel("Average Rating")
            plt.grid()
            plt.tight_layout()
            plt.savefig("goodreads_rating_over_years.png")
            charts.append("goodreads_rating_over_years.png")
            plt.close()
        else:
            print("Required columns for line plot are missing. Skipping rating over years.")

        # Correlation heatmap (fallback visualization)
        if len(charts) < 2 and not correlation_matrix.empty:
            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
            plt.title("Correlation Heatmap")
            heatmap_name = f"goodreads_correlation_heatmap.png"
            plt.savefig(heatmap_name)
            charts.append(heatmap_name)
            plt.close()

    return charts

def generate_story(summary, numeric_summary, charts, file_path):
    """
    Use the AI Proxy (GPT-4o-Mini) to generate a story about the analysis.

    Args:
        summary (dict): Summary of the dataset.
        numeric_summary (dict): Statistical summary of numeric columns.
        charts (list): List of visualizations created.
        file_path (str): Path to the dataset file.

    Returns:
        story (str): A detailed analysis report.
    """
    # Determine the dataset type based on the file name
    dataset_type = "Goodreads dataset" if "goodreads" in file_path.lower() else (
        "Happiness dataset" if "happiness" in file_path.lower() else "Media dataset"
    )

    # Prepare the prompt for generating the story
    prompt = f"""
    I analyzed a {dataset_type} with the following characteristics:
    - Shape: {summary['shape']}
    - Columns: {summary['columns']}
    - Data Types: {summary['dtypes']}
    - Missing Values: {summary['missing_values']}
    - Example Values: {summary['example_values']}

    I performed basic statistics and found the following:
    {numeric_summary}

    I created the following visualizations:
    - {', '.join(charts)}

    Write a detailed story about the dataset, the analysis performed, the insights discovered, and the implications of the findings.
    """
    try:
        # Set up request headers and data for the AI Proxy
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AIPROXY_TOKEN}",
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a data analysis expert."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 800,
            "temperature": 0.7,
        }

        # Send a POST request to the AI Proxy API
        response = requests.post(AI_PROXY_URL, headers=headers, json=data)
        response.raise_for_status()  # Raise an error if the response contains an HTTP error
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        # Handle errors during story generation
        print(f"Error generating story: {e}")
        sys.exit(1)


def save_readme(story, charts, dataset_name):
    """
    Save the story and charts into a dataset-specific README file.

    Args:
        story (str): The generated story from the AI.
        charts (list): List of chart file names.
        dataset_name (str): Name of the dataset.
    """
    # Set the filename for the README
    readme_filename = f"README_{dataset_name}.md"

    # Write the story and chart references to the README file
    with open(readme_filename, "w") as f:
        f.write("# Analysis Report\n\n")
        f.write(story)
        f.write("\n\n## Visualizations\n")
        for chart in charts:
            f.write(f"![{chart}]({chart})\n")

    # Confirm that the results were saved successfully
    print(f"Results saved to {readme_filename}")


if __name__ == "__main__":
    # Check if the script is run with a CSV file as an argument
    if len(sys.argv) < 2:
        print("Usage: uv run autolysis.py <dataset.csv>")
        sys.exit(1)

    # Extract the file path and dataset name from the command-line arguments
    file_path = sys.argv[1]
    dataset_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"Running analysis for: {file_path}")

    # Step 1: Analyze the dataset
    print("Step 1: Analyzing dataset...")
    df, summary, numeric_summary, correlation_matrix = analyze_dataset(file_path)
    print("Dataset analyzed successfully.")

    # Step 2: Generate visualizations
    print("Step 2: Generating visualizations...")
    charts = visualize_dataset(df, correlation_matrix, file_path)
    print(f"Visualizations created: {charts}")

    # Step 3: Generate a story using AI Proxy
    print("Step 3: Generating story using AI Proxy...")
    story = generate_story(summary, numeric_summary, charts, file_path)
    print("Story generated successfully.")

    # Step 4: Save the analysis results to a README file
    print(f"Step 4: Saving results to README_{dataset_name}.md...")
    save_readme(story, charts, dataset_name)
    print(f"Analysis complete for {file_path}. Results saved to README_{dataset_name}.md and PNG files.")

