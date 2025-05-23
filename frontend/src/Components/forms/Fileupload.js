import React, { useState } from 'react'; 
import { CSVDownload } from "react-csv";

// Update this to your deployed FastAPI backend URL
const API_URL = process.env.REACT_APP_API_URL || "https://shastra-result-2.onrender.com";

const FileUploadPage = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [hackerRankUrl, setHackerRankUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isDownloadable, setDownloadable] = useState(false);
  const [finalData, setFinalData] = useState([]);

  const handleFileUpload = (event) => {
    const selectedFile = event.target.files[0];
    setError('');
    setSuccess('');

    // Accept both CSV and Excel files for FastAPI backend
    if (selectedFile && (selectedFile.type === 'text/csv' ||
        selectedFile.name.endsWith('.csv') ||
        selectedFile.name.endsWith('.xlsx') ||
        selectedFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) {
      setFile(selectedFile);

      // Only preview CSV files
      if (selectedFile.type === 'text/csv' || selectedFile.name.endsWith('.csv')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const text = e.target.result;
          const rows = text.split('\n').slice(0, 5);
          setPreview(rows);
        };
        reader.readAsText(selectedFile);
      } else {
        // For Excel files, show filename only
        setPreview([`Excel file: ${selectedFile.name}`]);
      }
    } else {
      setError('Please upload a valid CSV or Excel (.xlsx) file');
      setFile(null);
      setPreview([]);
    }
  };

  const arrangeData = (data) => {
    const correctOrder = [
      'Sr No.', 'Batch', 'Branch/Div', 'UID', 'Roll No.', 'Student Name', 'HackerRank ID',
      '7-A', '8-A', '9-A', '10-A', '11-A', '12-A', 'Score'
    ];
    return data.map((item) => {
      let orderedItem = {};
      correctOrder.forEach((key) => {
        if (item.hasOwnProperty(key)) {
          orderedItem[key] = item[key];
        }
      });
      return orderedItem;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsProcessing(true);

    try {
      if (!file || !hackerRankUrl) {
        throw new Error('Please provide both a file and HackerRank URL');
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('hackerRankUrl', hackerRankUrl);

      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // FastAPI returns array directly from /upload endpoint
      const arrangedData = arrangeData(data);
      setFinalData(arrangedData);

      setDownloadable(true);
      setSuccess(`Results processed successfully! Found ${data.length} records.`);
    } catch (err) {
      console.error('Processing error:', err);
      setError(`Processing failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    setIsDownloading(true);
    // Trigger the CSVDownload component
    setTimeout(() => {
      setIsDownloading(false);
      // Keep the button available for re-download
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-cyan-400/30">
          <h2 className="text-3xl font-bold mb-6 bg-gradient-to-r from-cyan-400 to-purple-500 text-transparent bg-clip-text">
            Process Shastra Results
          </h2>

          {/* API Status Indicator */}
          <div className="mb-4 p-3 bg-gray-900 rounded-lg border border-cyan-400/30">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-cyan-300">
                Connected to: {API_URL}
              </span>
            </div>
          </div>

          {/* File Upload Section */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-cyan-300 mb-4">
              1. Upload Student Data (CSV or Excel)
            </h3>
            <div className="border-2 border-dashed border-cyan-400/50 rounded-lg p-6 text-center hover:border-purple-500/50 transition-colors">
              <input
                type="file"
                accept=".csv,.xlsx"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer inline-flex items-center px-6 py-3 bg-gradient-to-r from-cyan-400 to-purple-500 text-white rounded-lg transition-all hover:shadow-lg hover:shadow-cyan-400/20 hover:scale-105"
              >
                Select CSV or Excel File
              </label>
              {file && (
                <p className="mt-2 text-cyan-300">
                  Selected: {file.name}
                </p>
              )}
            </div>
          </div>

          {/* HackerRank URL Section */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-cyan-300 mb-4">
              2. Enter HackerRank Leaderboard URL
            </h3>
            <input
              type="url"
              value={hackerRankUrl}
              onChange={(e) => setHackerRankUrl(e.target.value)}
              placeholder="https://www.hackerrank.com/contests/your-contest/leaderboard"
              className="w-full px-4 py-3 bg-gray-900 border border-cyan-400/30 rounded-lg focus:ring-2 focus:ring-purple-500/50 focus:border-transparent text-white placeholder-gray-500"
            />
            <p className="mt-2 text-sm text-gray-400">
              Example: https://www.hackerrank.com/contests/shastra-coding-contest/leaderboard
            </p>
          </div>

          {/* Preview Section */}
          {preview.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-cyan-300 mb-2">
                File Preview
              </h3>
              <div className="bg-gray-900 p-4 rounded-lg border border-cyan-400/30 overflow-x-auto">
                {preview.map((row, index) => (
                  <div key={index} className="font-mono text-sm text-cyan-300/80 whitespace-pre">
                    {row}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error and Success Messages */}
          {error && (
            <div className="mb-4 p-4 bg-red-900/20 border border-red-500/30 rounded-lg">
              <p className="text-red-400">{error}</p>
              <details className="mt-2">
                <summary className="text-sm text-red-300 cursor-pointer">Debug Info</summary>
                <p className="text-xs text-red-300 mt-1">API URL: {API_URL}</p>
              </details>
            </div>
          )}

          {success && (
            <div className="mb-4 p-4 bg-green-900/20 border border-green-500/30 rounded-lg">
              <p className="text-green-400">{success}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={isProcessing || !file || !hackerRankUrl}
            className={`w-full py-3 px-6 rounded-lg text-white font-medium transition-all
              ${(!file || !hackerRankUrl) || isProcessing
                ? 'bg-gray-700 cursor-not-allowed'
                : 'bg-gradient-to-r from-cyan-400 to-purple-500 hover:shadow-lg hover:shadow-cyan-400/20 hover:scale-105'}
            `}
          >
            {isProcessing ? 'Processing Results...' : 'Process Results'}
          </button>

          {/* Download Button */}
          {isDownloadable && (
            <button
              onClick={handleDownload}
              disabled={isDownloading}
              className="mt-4 w-full py-3 px-6 rounded-lg text-white font-medium transition-all bg-gradient-to-r from-purple-500 to-cyan-400 hover:shadow-lg hover:shadow-purple-400/20 hover:scale-105 disabled:bg-gray-700 disabled:cursor-not-allowed"
            >
              {isDownloading ? 'Downloading...' : 'Download Results CSV'}
            </button>
          )}
          {isDownloading && (
            <CSVDownload data={finalData} filename="shastra_results.csv" target="_blank" />
          )}
        </div>

        {/* Processing Overlay */}
        {isProcessing && (
          <div className="fixed inset-0 bg-gray-900/80 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-gray-800 p-8 rounded-lg shadow-lg border border-cyan-400/30 max-w-md">
              <div className="flex flex-col items-center space-y-4">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-cyan-300 mb-2">Processing Results</h3>
                  <p className="text-sm text-gray-400">
                    Scraping HackerRank leaderboard and merging with student data...
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    This may take 30-60 seconds
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUploadPage;