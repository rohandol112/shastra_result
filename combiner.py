import pandas as pd
import os

def combine_files():
    # Load both CSV files
    scraped_file_path = "hackerrank_leaderboard.csv"  # First CSV (scraped results)
    cleaned_file_path = "cleaned_results.csv"  # Second CSV (cleaned IDs)

    scraped_df = pd.read_csv(scraped_file_path)
    cleaned_df = pd.read_csv(cleaned_file_path)

    # Merge data on HackerRank ID
    merged_df = cleaned_df.merge(scraped_df, on="HackerRank ID", how="left")

    # Save the final results
    final_file_path = "final_shastra_results.csv"
    merged_df.to_csv(final_file_path, index=False)

    # Get and print the absolute path of the saved file
    absolute_path = os.path.abspath(final_file_path) 
    print(f"Final results saved at: {absolute_path}")

