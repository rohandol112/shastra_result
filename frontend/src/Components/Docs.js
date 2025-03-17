import React from 'react';

const Docs = () => {
  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-6">Documentation</h1>
        <p className="text-gray-300 mb-4">
          This repository contains Jupyter Notebook scripts to process and clean HackerRank leaderboard data for Shastra results.
        </p>
        <h2 className="text-2xl font-semibold text-cyan-300 mb-2">Overview</h2>
        <p className="text-gray-300 mb-4">
          The workflow involves three main steps:
        </p>
        <ul className="list-disc list-inside text-gray-300 mb-4">
          <li>Scrape HackerRank Leaderboard: Extracts user IDs and marks from the HackerRank leaderboard.</li>
          <li>Clean Uploaded CSV: Removes '@' symbols from HackerRank IDs in an uploaded CSV.</li>
          <li>Merge Results: Combines marks from the scraped data into the cleaned CSV.</li>
        </ul>
        <h2 className="text-2xl font-semibold text-cyan-300 mb-2">Setup Instructions</h2>
        <p className="text-gray-300 mb-4">
          1. Clone this repository: <code>git clone https://github.com/rohandol112/shastra_result</code>
          <br />
          2. Open Jupyter Notebook and run the scripts in order:
        </p>
        <ul className="list-disc list-inside text-gray-300 mb-4">
          <li>Scrape HackerRank Leaderboard</li>
          <li>Clean Uploaded CSV</li>
          <li>Merge Marks into Cleaned CSV</li>
        </ul>
        <h2 className="text-2xl font-semibold text-cyan-300 mb-2">Output Files</h2>
        <ul className="list-disc list-inside text-gray-300 mb-4">
          <li><code>shastra_hackerrank_results.csv</code>: Scraped leaderboard data</li>
          <li><code>to_get_cleaned_csv.csv</code>: Uploaded CSV after removing '@'</li>
          <li><code>merge_csv.csv</code>: Final merged result with marks</li>
        </ul>
      </div>
    </div>
  );
};

export default Docs; 