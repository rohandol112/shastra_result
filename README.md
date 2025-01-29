# Shastra Result Processing

This repository contains scripts to process and clean HackerRank leaderboard data for Shastra results.

## Overview

The workflow involves three main steps:

1. **Scrape HackerRank Leaderboard**: Extracts user IDs and marks from the HackerRank leaderboard.
2. **Clean Uploaded CSV**: Removes '@' symbols from HackerRank IDs in an uploaded CSV.
3. **Merge Results**: Combines marks from the scraped data into the cleaned CSV.

## Setup Instructions

1. Clone this repository:

   ```sh
   git clone <repo-url>
   cd shastra-result-processing
   ```

2. Install dependencies:

   ```sh
   pip install pandas beautifulsoup4 requests
   ```

3. Run the scripts in order:

   - **Scrape HackerRank Leaderboard**

     ```sh
     python scrape_hackerrank.py
     ```

   - **Clean Uploaded CSV**

     ```sh
     python clean_csv.py
     ```

   - **Merge Marks into Cleaned CSV**

     ```sh
     python merge_results.py
     ```

## Output Files

- `shastra_hackerrank_results.ipynb`: Scraped leaderboard data
- `to_get_cleaned_csv.ipynb`: Uploaded CSV after removing '@'
- `final_shastra_results.ipynb`: Final merged result with marks

