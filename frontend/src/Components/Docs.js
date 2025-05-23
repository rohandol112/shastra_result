import React from 'react';

const Docs = () => {
  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-6">Documentation</h1>
        <p className="text-gray-300 mb-4">
          This repository contains python scripts to process and clean HackerRank leaderboard data for Shastra results.
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
          2. to run backend locally ; open the folder shastra_result
          3. cd FastAPI
          4. pip install -r requirements.txt
          5. python main.py to run backend locally
        </p>

      </div>
    </div>
  );
};

export default Docs; 