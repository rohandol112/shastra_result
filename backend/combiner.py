import pandas as pd
import os

def combine_files(cleaned_df, leaderboard_df):
    
    # Merge data on HackerRank ID
    merged_df = cleaned_df.merge(leaderboard_df, on="HackerRank ID", how="left")
    return merged_df

if __name__ == '__main__':
    combine_files()

