import pandas as pd
import os
import numpy as np

def clean_csv(df):
    # Remove '@' from the HackerRank ID column
    df["HackerRank ID"] = df["HackerRank ID"].astype(str).str.lstrip("@")
    df = df.replace(np.nan, "") 

    return df


if __name__ == '__main__':
    clean_csv()
