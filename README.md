# Shastra Result Processing 

This repository contains Jupyter Notebook scripts to process and clean HackerRank leaderboard data for Shastra results.

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

3. Open Jupyter Notebook and run the scripts in order:

   - **Scrape HackerRank Leaderboard** (`scrape_hackerrank.ipynb`)
   - **Clean Uploaded CSV** (`to_get_cleaned_csv.ipynb`)
   - **Merge Marks into Cleaned CSV** (`merge_csv.ipynb`)

## Output Files
- `shastra_hackerrank_results.csv`: Scraped leaderboard data
- `to_get_cleaned_csv.csv`: Uploaded CSV after removing '@'
- `merge_csv.csv`: Final merged result with marks

## Notes
- Ensure that the uploaded CSV file follows the correct format.
- Modify selectors in `scrape_hackerrank.ipynb` if the HackerRank website structure changes.
- The final script prints the absolute path of the merged CSV file for easy access.
- Run the notebooks in order to avoid missing dependencies.

