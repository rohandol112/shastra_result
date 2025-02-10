# Shastra Result Processing Application

## Overview

The Shastra Result Processing Application is a web-based tool designed to upload student data in CSV format, process the results, and download the final results as a CSV file. The application integrates a frontend built with React and a backend powered by Flask, allowing users to easily manage and analyze student performance data.

## Features

- Upload student data in CSV format.
- Enter a HackerRank leaderboard URL for additional data.
- Process the uploaded data and merge it with leaderboard information.
- Download the final processed results as a CSV file.
- User-friendly interface with real-time feedback.

## Technologies Used

### Frontend
- **React**: JavaScript library for building user interfaces.
- **Tailwind CSS**: Utility-first CSS framework for styling.
- **Framer Motion**: Library for animations in React.
- **Lucide React**: Icon library for React.
- **react-csv**: Library for handling CSV downloads.

### Backend
- **Flask**: Python web framework for building APIs.
- **Pandas**: Data manipulation and analysis library.
- **BeautifulSoup**: Library for web scraping.
- **Selenium**: Tool for automating web browsers.
- **NumPy**: Library for numerical operations.

## Prerequisites

Before you begin, ensure you have the following installed:

- Node.js (v14 or later)
- npm (Node package manager)
- Python (v3.6 or later)
- pip (Python package manager)
- Chrome WebDriver (for Selenium)
- Redis (if using Celery for asynchronous tasks)

## Setup Instructions

### Frontend Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/shastra-results-app.git
   cd shastra-results-app/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`.

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd shastra-results-app/backend
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask application**:
   ```bash
   python main.py
   ```

   The backend will be available at `http://127.0.0.1:5000`.

### Environment Variables

If your application requires any environment variables (e.g., API keys, database URLs), create a `.env` file in the backend directory and add the necessary variables.

### Running Tests

To run tests for the frontend and backend, follow these steps:

- **Frontend Tests**:
  ```bash
  npm test
  ```

- **Backend Tests**:
  ```bash
  python -m unittest discover
  ```

## Usage

1. Open your web browser and navigate to `http://localhost:3000`.
2. Upload a CSV file containing student data.
3. Enter the HackerRank leaderboard URL if applicable.
4. Click the "Process Results" button to process the data.
5. Once processing is complete, click the "Download Results CSV" button to download the final results.

## Project Structure
shastra-results-app/
├── frontend/
│ ├── public/
│ ├── src/
│ ├── package.json
│ └── README.md
└── backend/
| ├── scrapper.py
| ├── cleaner.py
| ├── combiner.py
| ├── main.py
| ├── requirements.txt
└── README.md
