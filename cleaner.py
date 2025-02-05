import pandas as pd
import os

def clean_csv():
    # Load the CSV file
    file_path = "BT_Results.csv" # Change to your file path
    df = pd.read_csv(file_path)

    # Remove '@' from the HackerRank ID column
    df["HackerRank ID"] = df["HackerRank ID"].astype(str).str.lstrip("@")

    # Save the cleaned file
    cleaned_file_path = "cleaned_results.csv"
    df.to_csv(cleaned_file_path, index=False)

    # Get and print the absolute path of the saved file
    absolute_path = os.path.abspath(cleaned_file_path)
    print(f"Cleaned file saved at: {absolute_path}")