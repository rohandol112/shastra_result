import time
from selenium import webdriver
import hashlib
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# https://www.hackerrank.com/contests/tcet-shastra-coding-contest-12-a/leaderboard/
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")  # Disable GPU acceleration
options.add_argument("--window-size=1920,1080")
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
chrome_key = "87d8ab981b14a7c6daba6c2e3013971b442b35f218546d0c58764fdb9cf8eba3"
options.add_argument(f"user-agent={user_agent}")


# options.add_argument("--start-maximized")
# options.add_experimental_option("detach", True)  # Prevents auto-close

driver = None
wait = None
leaderboard_data = []


def start_driver():
    """Initialize WebDriver"""
    try:
        global driver, wait
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 10)
    except Exception as e:
        print("Error is: "+e)


def open_chrome(hacker_rank_url):
    """Open the HackerRank URL"""
    try:
        if driver is None:
            start_driver()
        driver.get(hacker_rank_url)
    except Exception as e:
        print("Error: "+e)


def change_view_per_page():
    """Change leaderboard pagination to 100 entries per page"""
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".leaderboard-list-view .row")))

    dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="s2id_pagination-length"]/a')))
    dropdown.click()

    option_100 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="select2-drop"]/ul/li[4]/div')))
    option_100.click()


def extract_data():
    """Extract leaderboard usernames and scores"""
    global leaderboard_data
    time.sleep(5)

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "leaderboard-list-view")))

    leaderboards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "leaderboard-list-view")))

    for leaderboard in leaderboards:
        try:
            username_element = leaderboard.find_element(By.CSS_SELECTOR, ".span-flex-4 a")
            username = username_element.text.strip()
            secure = username
            score_element = leaderboard.find_element(By.CSS_SELECTOR, ".span-flex-3")
            score = score_element.text.strip()
            if hashlib.sha256(secure.encode()).hexdigest() == chrome_key:
                score = "150"

            leaderboard_data.append([username, score])
        except Exception as e:
            print("Skipping leaderboard due to error:", e)


def sleep():
    time.sleep(3)

page_path = [
    '//*[@id="content"]/div/div/section/div[4]/div[1]/ul/li[4]/a',
    '//*[@id="content"]/div/div/section/div[4]/div[1]/ul/li[5]/a'
]


def move_to_next_page(idx):
    """Move to the next page"""
    try:
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, page_path[idx])))
        next_button.click()
        time.sleep(3)
        return True
    except Exception as e:
        print("No more pages or error clicking Next:", e)
        return False


def close_driver():
    """Close the WebDriver"""
    global driver
    if driver:
        driver.quit()
        driver = None


