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

# Selenium imports with multiple browser support
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HackerRank Leaderboard Scraper API",
    description="Fast and scalable API for scraping HackerRank leaderboards with multiple browser support",
    version="3.0.0"
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


def get_firefox_options() -> FirefoxOptions:
    """Get optimized Firefox options for scraping"""
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.set_preference("general.useragent.override",
                           "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    return options


def get_chrome_options() -> ChromeOptions:
    """Get optimized Chrome options for scraping"""
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    return options


def get_edge_options() -> EdgeOptions:
    """Get optimized Edge options for scraping"""
    options = EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    return options


def create_driver(browser_preference=None):
    """Create a WebDriver instance with fallback options"""
    browsers_to_try = []

    # Set browser preference order
    if browser_preference:
        browsers_to_try.append(browser_preference.lower())

    # Default fallback order: Firefox -> Chrome -> Edge
    default_order = ['firefox', 'chrome', 'edge']
    for browser in default_order:
        if browser not in browsers_to_try:
            browsers_to_try.append(browser)

    last_error = None

    for browser in browsers_to_try:
        try:
            logger.info(f"Attempting to create {browser} driver...")

            if browser == 'firefox':
                options = get_firefox_options()
                service = FirefoxService(GeckoDriverManager().install())
                driver = webdriver.Firefox(service=service, options=options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                logger.info("Firefox driver created successfully")
                return driver

            elif browser == 'chrome':
                options = get_chrome_options()
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                logger.info("Chrome driver created successfully")
                return driver

            elif browser == 'edge':
                options = get_edge_options()
                service = EdgeService(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service, options=options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                logger.info("Edge driver created successfully")
                return driver

        except Exception as e:
            logger.warning(f"Failed to create {browser} driver: {e}")
            last_error = e
            continue

    # If all browsers failed, raise the last error
    raise ScrapingError(f"Failed to initialize any browser. Last error: {last_error}")


class HackerRankScraper:
    def __init__(self, browser_preference=None):
        self.driver = None
        self.wait = None
        self.leaderboard_data = []
        self.browser_preference = browser_preference

    def initialize(self):
        """Initialize the scraper"""
        try:
            self.driver = create_driver(self.browser_preference)
            self.wait = WebDriverWait(self.driver, 15)
            logger.info("Scraper initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {e}")
            raise ScrapingError(f"Scraper initialization failed: {e}")

    def scrape_leaderboard(self, url: str) -> List[List[str]]:
        """Main scraping method"""
        try:
            self.initialize()
            self._navigate_to_url(url)
            self._setup_pagination()

            # Scrape multiple pages
            page_selectors = [
                '//*[@id="content"]/div/div/section/div[4]/div[1]/ul/li[4]/a',
                '//*[@id="content"]/div/div/section/div[4]/div[1]/ul/li[5]/a'
            ]

            # Extract first page
            self._extract_page_data()

            # Extract subsequent pages
            for i, selector in enumerate(page_selectors):
                if self._navigate_to_next_page(selector):
                    self._extract_page_data()
                else:
                    logger.warning(f"Could not navigate to page {i + 2}")
                    break

            logger.info(f"Successfully scraped {len(self.leaderboard_data)} entries")
            return self.leaderboard_data

        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise ScrapingError(f"Failed to scrape leaderboard: {e}")
        finally:
            self._cleanup()

    def _navigate_to_url(self, url: str):
        """Navigate to the HackerRank URL"""
        try:
            self.driver.get(url)
            time.sleep(2)
        except Exception as e:
            raise ScrapingError(f"Failed to navigate to URL: {e}")

    def _setup_pagination(self):
        """Set up pagination to show 100 entries per page"""
        try:
            # Wait for leaderboard to load
            self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".leaderboard-list-view .row")
            ))

            # Click dropdown
            dropdown = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="s2id_pagination-length"]/a')
            ))
            dropdown.click()

            # Select 100 entries option
            option_100 = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="select2-drop"]/ul/li[4]/div')
            ))
            option_100.click()

            time.sleep(2)

        except TimeoutException:
            logger.warning("Could not set pagination - continuing with default")
        except Exception as e:
            logger.warning(f"Pagination setup failed: {e}")

    def _extract_page_data(self):
        """Extract data from current page"""
        try:
            time.sleep(3)

            self.wait.until(EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "leaderboard-list-view")
            ))

            leaderboards = self.driver.find_elements(By.CLASS_NAME, "leaderboard-list-view")

            for leaderboard in leaderboards:
                try:
                    username_element = leaderboard.find_element(By.CSS_SELECTOR, ".span-flex-4 a")
                    username = username_element.text.strip()

                    score_element = leaderboard.find_element(By.CSS_SELECTOR, ".span-flex-3")
                    score = score_element.text.strip()

                    if username and score:
                        self.leaderboard_data.append([username, score])

                except Exception as e:
                    logger.debug(f"Skipping entry due to error: {e}")
                    continue

        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            raise ScrapingError(f"Failed to extract page data: {e}")

    def _navigate_to_next_page(self, xpath: str) -> bool:
        """Navigate to next page"""
        try:
            next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            next_button.click()
            time.sleep(3)
            return True
        except Exception as e:
            logger.info(f"No more pages or navigation failed: {e}")
            return False

    def _cleanup(self):
        """Clean up driver resources"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")


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
        "message": "FastAPI HackerRank Scraper is running (Multi-browser support)",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "supported_browsers": ["firefox", "chrome", "edge"]
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
        "supported_browsers": ["firefox", "chrome", "edge"],
        "timestamp": datetime.now().isoformat()
    }


@app.post("/upload", tags=["Main Operations"])
def process_leaderboard(
        hackerRankUrl: str = Form(...),
        file: UploadFile = File(...),
        browser: str = Form(default="firefox")  # New parameter for browser choice
):
    """
    Main endpoint to process student file and merge with HackerRank leaderboard data
    (Compatible with original Flask frontend)
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

        # Validate browser choice
        supported_browsers = ["firefox", "chrome", "edge"]
        if browser.lower() not in supported_browsers:
            logger.warning(f"Unsupported browser '{browser}', defaulting to firefox")
            browser = "firefox"

        logger.info(f"Processing request for URL: {hackerRankUrl} using {browser}")

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

        # Scrape leaderboard data with specified browser
        scraper = HackerRankScraper(browser_preference=browser)
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

        logger.info(f"Request processed successfully in {processing_time:.2f} seconds using {browser}")

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


@app.post("/process-leaderboard", tags=["New API"])
def process_leaderboard_v2(
        hackerRankUrl: str = Form(...),
        file: UploadFile = File(...),
        browser: str = Form(default="firefox")
):
    """
    Enhanced endpoint with detailed response format
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

        # Validate browser choice
        supported_browsers = ["firefox", "chrome", "edge"]
        if browser.lower() not in supported_browsers:
            logger.warning(f"Unsupported browser '{browser}', defaulting to firefox")
            browser = "firefox"

        logger.info(f"Processing request for URL: {hackerRankUrl} using {browser}")

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

        # Scrape leaderboard data with specified browser
        scraper = HackerRankScraper(browser_preference=browser)
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

        logger.info(f"Request processed successfully in {processing_time:.2f} seconds using {browser}")

        return JSONResponse(
            content={
                "success": True,
                "data": result_json,
                "metadata": {
                    "total_records": len(result_json),
                    "processing_time_seconds": round(processing_time, 2),
                    "scraped_entries": len(leaderboard_data),
                    "browser_used": browser,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )

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


@app.post("/scrape-only", tags=["Utilities"])
def scrape_leaderboard_only(
        hackerRankUrl: str = Form(...),
        browser: str = Form(default="firefox")
):
    """
    Utility endpoint to only scrape leaderboard data without merging
    """
    try:
        if not hackerRankUrl:
            raise HTTPException(status_code=400, detail="HackerRank URL is required")

        # Validate browser choice
        supported_browsers = ["firefox", "chrome", "edge"]
        if browser.lower() not in supported_browsers:
            logger.warning(f"Unsupported browser '{browser}', defaulting to firefox")
            browser = "firefox"

        scraper = HackerRankScraper(browser_preference=browser)
        leaderboard_data = scraper.scrape_leaderboard(hackerRankUrl)

        if not leaderboard_data:
            raise HTTPException(status_code=404, detail="No leaderboard data found")

        # Convert to DataFrame for consistency
        leaderboard_df = pd.DataFrame(leaderboard_data, columns=["HackerRank ID", "Score"])
        result_json = DataProcessor.dataframe_to_json(leaderboard_df)

        return JSONResponse(content={
            "success": True,
            "data": result_json,
            "metadata": {
                "total_records": len(result_json),
                "browser_used": browser,
                "timestamp": datetime.now().isoformat()
            }
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Set to False for production
        log_level="info"
    )