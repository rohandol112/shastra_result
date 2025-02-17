from flask import Flask, jsonify, request
from scrapper import start_driver,open_chrome, change_view_per_page, extract_data, move_to_next_page, close_driver
from cleaner import clean_csv
from combiner import combine_files
import pandas as pd
from scrapper import leaderboard_data
from io import StringIO, BytesIO
import numpy as np
from collections import OrderedDict

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_csv():
    try:
        hacker_rank_url = request.form.get('hackerRankUrl')
        
        if not hacker_rank_url:
            return jsonify({"error": "HackerRank URL is required"}), 400

        if 'file' not in request.files:
            return jsonify({"error": "No file part in request"}), 400  # Handle missing file
    
        file = request.files['file']
        print(file)
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Convert file data to DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(StringIO(file.read().decode('utf-8')))
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(file.read()))
        else:
            return {'error': 'Unsupported file type'}, 400

        print(df.head(5))

        # clean the csv we got
        cleaned_df = clean_csv(df)

        # scraping data of leaderboad
        start_driver()
        open_chrome(hacker_rank_url)
        change_view_per_page()
        extract_data()
        move_to_next_page(0)
        extract_data()
        move_to_next_page(1)
        extract_data()
        close_driver()

        leaderboard_df = pd.DataFrame(leaderboard_data, columns=["HackerRank ID", "Score"])
        merged_df = combine_files(cleaned_df, leaderboard_df)
        merged_df = merged_df.replace({np.nan: None})

        merged_df = merged_df.drop_duplicates(subset=['HackerRank ID'], keep='first')

        # mark students 'AB' who were absent
        merged_df['Score'][(merged_df['Score'].isna()) & (merged_df['HackerRank ID'] != "NOT REGISTERED")] = "AB"

        ordered_json = [OrderedDict(row) for row in merged_df.to_dict(orient='records')]    # converted dataframe to json
        return jsonify(ordered_json)  # Sending as a list

    except Exception as e:
        print("The error is: ",e)
        return jsonify({"error": str(e)}), 500 

if __name__ == '__main__':
    app.run(debug=True)
