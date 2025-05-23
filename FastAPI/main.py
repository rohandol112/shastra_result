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
import subprocess
import shutil
import platform

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
    version="3.2.0"
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


def install_chrome_on_render():
    """Install Chrome on Render.com if not present"""
    try:
        # Check if we're on Render (common environment indicators)
        is_render = any([
            os.environ.get('RENDER'),
            os.environ.get('RENDER_SERVICE_ID'),
            '/opt/render' in os.environ.get('PATH', ''),
            platform.system() == 'Linux' and 'render' in platform.node().lower()
        ])

        if not is_render:
            logger.info("Not detected as Render environment, skipping Chrome installation")
            return False

        logger.info("Render environment detected, attempting Chrome installation...")

        # Commands to install Chrome on Ubuntu/Debian (Render uses Ubuntu)
        commands = [
            "apt-get update",
            "apt-get install -y wget gnupg",
            "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -",
            "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list",
            "apt-get update",
            "apt-get install -y google-chrome-stable",
            "apt-get install -y xvfb"  # Virtual framebuffer for headless operation
        ]

        for cmd in commands:
            try:
                result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=120)
                if result.returncode != 0:
                    logger.warning(f"Command failed: {cmd}, Error: {result.stderr}")
                else:
                    logger.info(f"Successfully executed: {cmd}")
            except subprocess.TimeoutExpired:
                logger.warning(f"Command timed out: {cmd}")
            except Exception as e:
                logger.warning(f"Command execution error: {cmd}, Error: {e}")

        # Verify installation
        if shutil.which('google-chrome') or shutil.which('google-chrome-stable'):
            logger.info("Chrome installed successfully on Render")
            return True
        else:
            logger.warning("Chrome installation verification failed")
            return False

    except Exception as e:
        logger.error(f"Chrome installation failed: {e}")
        return False


def check_browser_installation():
    """Check which browsers are available on the system with Render-specific handling"""
    available_browsers = []

    # First, try to install Chrome on Render if no browsers are found
    initial_check = False

    # Check Chrome/Chromium
    chrome_paths = [
        'google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser',
        '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium', '/usr/bin/chromium-browser',
        '/opt/google/chrome/chrome'
    ]

    for path in chrome_paths:
        if shutil.which(path) or os.path.exists(path):
            available_browsers.append('chrome')
            logger.info(f"Found Chrome/Chromium at: {path}")
            initial_check = True
            break

    # Check Firefox
    firefox_paths = [
        'firefox', '/usr/bin/firefox', '/opt/firefox/firefox',
        '/snap/bin/firefox', '/usr/local/bin/firefox'
    ]
    for path in firefox_paths:
        if shutil.which(path) or os.path.exists(path):
            available_browsers.append('firefox')
            logger.info(f"Found Firefox at: {path}")
            initial_check = True
            break

    # Check Edge
    edge_paths = ['microsoft-edge', 'microsoft-edge-stable']
    for path in edge_paths:
        if shutil.which(path):
            available_browsers.append('edge')
            logger.info(f"Found Edge at: {path}")
            initial_check = True
            break

    # If no browsers found, try to install Chrome on Render
    if not initial_check:
        logger.warning("No browsers found initially, attempting Chrome installation...")
        if install_chrome_on_render():
            # Re-check for Chrome after installation
            for path in chrome_paths:
                if shutil.which(path) or os.path.exists(path):
                    available_browsers.append('chrome')
                    logger.info(f"Found Chrome after installation at: {path}")
                    break

    logger.info(f"Available browsers: {available_browsers}")
    return available_browsers


def get_chrome_options() -> ChromeOptions:
    """Get optimized Chrome options for scraping with Render compatibility"""
    options = ChromeOptions()

    # Essential headless options
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--ignore-certificate-errors-spki-list")
    options.add_argument("--disable-features=VizDisplayCompositor")

    # Additional options for cloud/container environments
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-features=TranslateUI")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument("--remote-debugging-port=9222")

    # Window and display options
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")

    # User agent and automation detection bypass
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Memory and performance options
    options.add_argument("--memory-pressure-off")
    options.add_argument("--max_old_space_size=4096")

    # Set Chrome binary location for different environments
    chrome_binaries = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/opt/google/chrome/chrome',
        'google-chrome',
        'google-chrome-stable'
    ]

    for binary in chrome_binaries:
        if shutil.which(binary) or os.path.exists(binary):
            options.binary_location = binary
            logger.info(f"Using Chrome binary: {binary}")
            break

    return options


def get_firefox_options() -> FirefoxOptions:
    """Get optimized Firefox options for scraping"""
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Firefox-specific preferences
    options.set_preference("general.useragent.override",
                           "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0")
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("media.volume_scale", "0.0")

    return options


def get_edge_options() -> EdgeOptions:
    """Get optimized Edge options for scraping"""
    options = EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
    return options


def create_driver(browser_preference=None):
    """Create a WebDriver instance with fallback options based on available browsers"""

    # Check available browsers first
    available_browsers = check_browser_installation()

    if not available_browsers:
        raise ScrapingError("No browsers found on system. Please install Chrome, Firefox, or Edge.")

    browsers_to_try = []

    # Set browser preference order based on availability
    if browser_preference and browser_preference.lower() in available_browsers:
        browsers_to_try.append(browser_preference.lower())

    # Add remaining available browsers
    for browser in available_browsers:
        if browser not in browsers_to_try:
            browsers_to_try.append(browser)

    last_error = None

    for browser in browsers_to_try:
        try:
            logger.info(f"Attempting to create {browser} driver...")

            if browser == 'chrome':
                options = get_chrome_options()

                try:
                    service = ChromeService(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                except Exception as e:
                    logger.warning(f"ChromeDriverManager failed: {e}, trying manual setup...")
                    # Try without service if ChromeDriverManager fails
                    driver = webdriver.Chrome(options=options)

                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                logger.info("Chrome driver created successfully")
                return driver

            elif browser == 'firefox':
                options = get_firefox_options()

                try:
                    service = FirefoxService(GeckoDriverManager().install())
                    driver = webdriver.Firefox(service=service, options=options)
                except Exception as e:
                    logger.warning(f"GeckoDriverManager failed: {e}, trying manual setup...")
                    driver = webdriver.Firefox(options=options)

                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                logger.info("Firefox driver created successfully")
                return driver

            elif browser == 'edge':
                options = get_edge_options()

                try:
                    service = EdgeService(EdgeChromiumDriverManager().install())
                    driver = webdriver.Edge(service=service, options=options)
                except Exception as e:
                    logger.warning(f"EdgeChromiumDriverManager failed: {e}, trying manual setup...")
                    driver = webdriver.Edge(options=options)

                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                logger.info("Edge driver created successfully")
                return driver

        except Exception as e:
            logger.warning(f"Failed to create {browser} driver: {e}")
            last_error = e
            continue

    # If all browsers failed, raise the last error
    raise ScrapingError(f"Failed to initialize any browser. Available: {available_browsers}. Last error: {last_error}")


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
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("Scraper initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {e}")
            raise ScrapingError(f"Scraper initialization failed: {e}")

    def scrape_leaderboard(self, url: str) -> List[List[str]]:
        """Main scraping method with improved error handling"""
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
        """Navigate to the HackerRank URL with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Navigating to URL (attempt {attempt + 1}): {url}")
                self.driver.get(url)
                time.sleep(3)

                # Wait for page to load
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                return

            except Exception as e:
                if attempt == max_retries - 1:
                    raise ScrapingError(f"Failed to navigate to URL after {max_retries} attempts: {e}")
                logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                time.sleep(2)

    def _setup_pagination(self):
        """Set up pagination to show 100 entries per page"""
        try:
            # Wait for leaderboard to load with increased timeout
            self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".leaderboard-list-view .row")
            ))

            # Click dropdown
            dropdown = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="s2id_pagination-length"]/a')
            ))
            self.driver.execute_script("arguments[0].click();", dropdown)

            # Select 100 entries option
            option_100 = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="select2-drop"]/ul/li[4]/div')
            ))
            self.driver.execute_script("arguments[0].click();", option_100)

            time.sleep(3)

        except TimeoutException:
            logger.warning("Could not set pagination - continuing with default")
        except Exception as e:
            logger.warning(f"Pagination setup failed: {e}")

    def _extract_page_data(self):
        """Extract data from current page with improved error handling"""
        try:
            time.sleep(4)

            self.wait.until(EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "leaderboard-list-view")
            ))

            leaderboards = self.driver.find_elements(By.CLASS_NAME, "leaderboard-list-view")
            logger.info(f"Found {len(leaderboards)} leaderboard entries on current page")

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
        """Navigate to next page with improved error handling"""
        try:
            next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(4)
            return True
        except Exception as e:
            logger.info(f"No more pages or navigation failed: {e}")
            return False

    def _cleanup(self):
        """Clean up driver resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver cleanup completed")
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
    """Health check endpoint with browser availability info"""
    available_browsers = check_browser_installation()
    return {
        "status": "healthy",
        "message": "FastAPI HackerRank Scraper is running (Multi-browser support with Render compatibility)",
        "timestamp": datetime.now().isoformat(),
        "version": "3.2.0",
        "available_browsers": available_browsers,
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
    available_browsers = check_browser_installation()
    return {
        "status": "operational",
        "services": {
            "scraper": "available",
            "data_processor": "available",
            "file_handler": "available"
        },
        "available_browsers": available_browsers,
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
        browser: str = Form(default="auto")
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

        # Check available browsers and set preference
        available_browsers = check_browser_installation()
        if not available_browsers:
            raise HTTPException(status_code=500, detail="No browsers available on system")

        if browser.lower() == "auto":
            browser = available_browsers[0]  # Use first available browser
        elif browser.lower() not in available_browsers:
            logger.warning(f"Requested browser '{browser}' not available, using {available_browsers[0]}")
            browser = available_browsers[0]

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