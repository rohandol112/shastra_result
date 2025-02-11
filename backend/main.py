import os
import logging
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from collections import OrderedDict
from io import StringIO, BytesIO

# Import your scraper functions
from scrapper import (
    start_driver, open_chrome, change_view_per_page, extract_data,
    move_to_next_page, close_driver, leaderboard_data
)
from cleaner import clean_csv
from combiner import combine_files

# Initialize Flask app
app = Flask(__name__)

# Enable CORS - Allow only specific origins in production
CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_URL", "*")}})

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/upload', methods=['POST'])
def upload_csv():
    try:
        hacker_rank_url = request.form.get('hackerRankUrl')
        if not hacker_rank_url:
            return jsonify({"error": "HackerRank URL is required"}), 400

        if 'file' not in request.files:
            return jsonify({"error": "No file part in request"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Read uploaded file into a DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(StringIO(file.read().decode('utf-8')))
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(file.read()))
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        logger.info("Uploaded file processed successfully.")

        # Clean the CSV data
        cleaned_df = clean_csv(df)

        # Scrape leaderboard data
        start_driver()
        open_chrome(hacker_rank_url)
        change_view_per_page()
        extract_data()
        move_to_next_page(0)
        extract_data()
        move_to_next_page(1)
        extract_data()
        close_driver()

        # Convert scraped data into DataFrame
        leaderboard_df = pd.DataFrame(leaderboard_data, columns=["HackerRank ID", "Score"])

        # Merge cleaned and scraped data
        merged_df = combine_files(cleaned_df, leaderboard_df)
        merged_df = merged_df.replace({np.nan: None})
        merged_df = merged_df.drop_duplicates(subset=['HackerRank ID'], keep='first')

        # Convert DataFrame to JSON
        ordered_json = [OrderedDict(row) for row in merged_df.to_dict(orient='records')]

        return jsonify(ordered_json)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal Server Error"}), 500

# Production setup
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
