import React, { useState } from 'react'; 
import { CSVDownload } from "react-csv";

const FileUploadPage = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(''); 
  const [hackerRankUrl, setHackerRankUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const [isDownloadable, setDownloadable] = useState(false);
  const [resData, setData] = useState([]); 

  const handleFileUpload = (event) => {
    const selectedFile = event.target.files[0];
    setError('');
    setSuccess('');
    
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target.result;
        const rows = text.split('\n').slice(0, 5);
        setPreview(rows); 
      };
      reader.readAsText(selectedFile);
    } else {
      setError('Please upload a valid CSV file');
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
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      }
      if (hackerRankUrl) {
        formData.append('hackerRankUrl', hackerRankUrl); 
      }

      const response = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST', 
        body: formData
      });

      const data = await response.json();
      const arrangedData = arrangeData(data);
      setData(arrangedData);
      console.log(arrangedData);
        
      if (!response.ok) {
        throw new Error(data.message || 'Processing failed');
      }
      setDownloadable(true);
      setSuccess('Results processed successfully!');
    } catch (err) {
      setError("The error is: "+err.message);
      console.log(err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-cyan-400/30">
          <h2 className="text-3xl font-bold mb-6 bg-gradient-to-r from-cyan-400 to-purple-500 text-transparent bg-clip-text">
            Process Shastra Results
          </h2>

          {/* CSV Upload Section */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-cyan-300 mb-4">
              1. Upload Student Data CSV
            </h3>
            <div className="border-2 border-dashed border-cyan-400/50 rounded-lg p-6 text-center hover:border-purple-500/50 transition-colors">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer inline-flex items-center px-6 py-3 bg-gradient-to-r from-cyan-400 to-purple-500 text-white rounded-lg transition-all hover:shadow-lg hover:shadow-cyan-400/20 hover:scale-105"
              >
                Select CSV File
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
              placeholder="https://www.hackerrank.com/contests/..."
              className="w-full px-4 py-3 bg-gray-900 border border-cyan-400/30 rounded-lg focus:ring-2 focus:ring-purple-500/50 focus:border-transparent text-white placeholder-gray-500"
            />
          </div>

          {/* Preview Section */}
          {preview.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-cyan-300 mb-2">
                CSV Preview
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
            disabled={isProcessing || (!file && !hackerRankUrl)}
            className={`w-full py-3 px-6 rounded-lg text-white font-medium transition-all
              ${(!file && !hackerRankUrl) || isProcessing
                ? 'bg-gray-700 cursor-not-allowed'
                : 'bg-gradient-to-r from-cyan-400 to-purple-500 hover:shadow-lg hover:shadow-cyan-400/20 hover:scale-105'}
            `}
          >
            {isProcessing ? 'Processing...' : 'Process Results'}
          </button>
        </div>

        {/* Processing Overlay */}
        {isProcessing && (
          <div className="fixed inset-0 bg-gray-900/80 backdrop-blur-sm flex items-center justify-center">
            <div className="bg-gray-800 p-6 rounded-lg shadow-lg border border-cyan-400/30">
              <div className="flex items-center space-x-3">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyan-400"></div>
                <span className="text-cyan-300">Processing Results...</span>
              </div>
            </div>
          </div>
        )}
        {isDownloadable && <CSVDownload data={resData} />} 
      </div>
    </div>
  );
};

// {isDownloadable && <CSVDownload data={resData} />} 

export default FileUploadPage;
