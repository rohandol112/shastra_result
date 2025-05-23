from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import asyncio
from typing import List, Dict, Any
import os
import time
from datetime import datetime
import logging
from collections import OrderedDict
from io import StringIO, BytesIO
import platform

# Playwright imports
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HackerRank Leaderboard Scraper API",
    description="Fast and scalable API for scraping HackerRank leaderboards with Playwright",
    version="4.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScrapingError(Exception):
    """Custom exception for scraping errors"""
    pass


class DataProcessingError(Exception):
    """Custom exception for data processing errors"""
    pass


class HackerRankScraper:
    def __init__(self):
        self.leaderboard_data = []

    def scrape_leaderboard(self, url: str) -> List[List[str]]:
        """Main scraping method using Playwright"""
        try:
            with sync_playwright() as p:
                # Launch browser with optimized settings for cloud environments
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-extensions',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--single-process'
                    ]
                )

                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )

                page = context.new_page()

                # Navigate to URL
                logger.info(f"Navigating to URL: {url}")
                page.goto(url, wait_until='networkidle', timeout=30000)

                # Wait for leaderboard to load
                page.wait_for_selector('.leaderboard-list-view', timeout=20000)

                # Setup pagination - try to show 100 entries per page
                try:
                    # Click dropdown
                    page.click('#s2id_pagination-length a', timeout=10000)
                    page.wait_for_timeout(1000)

                    # Select 100 entries option
                    page.click('#select2-drop ul li:nth-child(4) div', timeout=10000)
                    page.wait_for_timeout(3000)

                    logger.info("Set pagination to 100 entries per page")
                except Exception as e:
                    logger.warning(f"Could not set pagination: {e}")

                # Extract data from multiple pages
                self._extract_page_data(page)

                # Try to navigate to additional pages
                page_selectors = [
                    '//*[@id="content"]/div/div/section/div[4]/div[1]/ul/li[4]/a',
                    '//*[@id="content"]/div/div/section/div[4]/div[1]/ul/li[5]/a'
                ]

                for i, selector in enumerate(page_selectors, 2):
                    try:
                        # Click next page
                        page.click(f'xpath={selector}', timeout=10000)
                        page.wait_for_timeout(4000)

                        # Extract data from this page
                        self._extract_page_data(page)
                        logger.info(f"Scraped page {i}")

                    except Exception as e:
                        logger.info(f"Could not navigate to page {i}: {e}")
                        break

                browser.close()

            logger.info(f"Successfully scraped {len(self.leaderboard_data)} entries")
            return self.leaderboard_data

        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise ScrapingError(f"Failed to scrape leaderboard: {e}")

    def _extract_page_data(self, page):
        """Extract data from current page"""
        try:
            # Wait for content to load
            page.wait_for_selector('.leaderboard-list-view', timeout=10000)

            # Get all leaderboard entries
            entries = page.query_selector_all('.leaderboard-list-view')
            logger.info(f"Found {len(entries)} entries on current page")

            for entry in entries:
                try:
                    # Extract username
                    username_element = entry.query_selector('.span-flex-4 a')
                    username = username_element.inner_text().strip() if username_element else ""

                    # Extract score
                    score_element = entry.query_selector('.span-flex-3')
                    score = score_element.inner_text().strip() if score_element else ""

                    if username and score:
                        self.leaderboard_data.append([username, score])

                except Exception as e:
                    logger.debug(f"Skipping entry due to error: {e}")
                    continue

        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            raise ScrapingError(f"Failed to extract page data: {e}")


class DataProcessor:
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Clean the uploaded CSV data"""
        try:
            # Remove '@' from HackerRank ID column
            if "HackerRank ID" in df.columns:
                df["HackerRank ID"] = df["HackerRank ID"].astype(str).str.lstrip("@")

            # Replace NaN with empty strings
            df = df.replace({np.nan: ""})

            logger.info(f"Cleaned dataframe with {len(df)} rows")
            return df

        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            raise DataProcessingError(f"Failed to clean data: {e}")

    @staticmethod
    def merge_data(student_df: pd.DataFrame, leaderboard_df: pd.DataFrame) -> pd.DataFrame:
        """Merge student data with leaderboard data"""
        try:
            # Merge on HackerRank ID
            merged_df = student_df.merge(leaderboard_df, on="HackerRank ID", how="left")

            # Remove duplicates
            merged_df = merged_df.drop_duplicates(subset=['HackerRank ID'], keep='first')

            # Replace NaN with None for JSON serialization
            merged_df = merged_df.replace({np.nan: None})

            logger.info(f"Merged data: {len(merged_df)} rows")
            return merged_df

        except Exception as e:
            logger.error(f"Data merging failed: {e}")
            raise DataProcessingError(f"Failed to merge data: {e}")

    @staticmethod
    def dataframe_to_json(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to JSON format"""
        try:
            # Convert to ordered dictionary to maintain column order
            return [OrderedDict(row) for row in df.to_dict(orient='records')]
        except Exception as e:
            logger.error(f"JSON conversion failed: {e}")
            raise DataProcessingError(f"Failed to convert to JSON: {e}")


# API Routes
@app.get("/", tags=["Health Check"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "FastAPI HackerRank Scraper is running with Playwright",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0",
        "browser_engine": "Chromium (Playwright)",
        "system_info": {
            "platform": os.name,
            "python_version": os.sys.version,
            "system": platform.system(),
            "machine": platform.machine()
        }
    }


@app.get("/status", tags=["Health Check"])
async def detailed_status():
    """Detailed status endpoint"""
    return {
        "status": "operational",
        "services": {
            "scraper": "available",
            "data_processor": "available",
            "file_handler": "available"
        },
        "browser_engine": "Chromium (Playwright)",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "render_detected": any([
                os.environ.get('RENDER'),
                os.environ.get('RENDER_SERVICE_ID'),
                '/opt/render' in os.environ.get('PATH', ''),
                platform.system() == 'Linux' and 'render' in platform.node().lower()
            ])
        }
    }


@app.post("/upload", tags=["Main Operations"])
def process_leaderboard(
        hackerRankUrl: str = Form(...),
        file: UploadFile = File(...),
        browser: str = Form(default="chromium")  # Only chromium supported with Playwright
):
    """
    Main endpoint to process student file and merge with HackerRank leaderboard data
    """
    start_time = time.time()

    try:
        # Validate inputs
        if not hackerRankUrl:
            raise HTTPException(status_code=400, detail="HackerRank URL is required")

        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")

        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx')):
            raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported")

        logger.info(f"Processing request for URL: {hackerRankUrl}")

        # Read uploaded file
        file_content = file.file.read()

        if file.filename.endswith('.csv'):
            student_df = pd.read_csv(StringIO(file_content.decode('utf-8')))
        else:  # xlsx
            student_df = pd.read_excel(BytesIO(file_content))

        logger.info(f"Loaded file with {len(student_df)} rows")

        # Process data
        data_processor = DataProcessor()
        cleaned_df = data_processor.clean_dataframe(student_df)

        # Scrape leaderboard data
        scraper = HackerRankScraper()
        leaderboard_data = scraper.scrape_leaderboard(hackerRankUrl)

        if not leaderboard_data:
            raise HTTPException(status_code=404, detail="No leaderboard data found")

        # Create leaderboard DataFrame
        leaderboard_df = pd.DataFrame(leaderboard_data, columns=["HackerRank ID", "Score"])

        # Merge data
        merged_df = data_processor.merge_data(cleaned_df, leaderboard_df)

        # Convert to JSON
        result_json = data_processor.dataframe_to_json(merged_df)

        processing_time = time.time() - start_time

        logger.info(f"Request processed successfully in {processing_time:.2f} seconds")

        # Return the data directly as array (compatible with frontend)
        return result_json

    except HTTPException:
        raise
    except ScrapingError as e:
        logger.error(f"Scraping error: {e}")
        raise HTTPException(status_code=422, detail=f"Scraping failed: {str(e)}")
    except DataProcessingError as e:
        logger.error(f"Data processing error: {e}")
        raise HTTPException(status_code=422, detail=f"Data processing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )