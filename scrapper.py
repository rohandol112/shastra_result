import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Global Variables
hacker_rank_url = "https://www.hackerrank.com/contests/tcet-shastra-coding-contest-9-a/leaderboard/"
options = Options()

# Add the headless argument to Chrome options
# options.add_argument("--headless")  # This will hide the browser window
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)  # Prevents auto-close

# Initialize WebDriver
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)
leaderboard_data = []


def open_chrome():
    """Open the HackerRank URL"""
    driver.get(hacker_rank_url)


def change_view_per_page():
    """Extract leaderboard data"""
    # Wait for leaderboard to load
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".leaderboard-list-view .row")))

    # Click dropdown for pagination
    dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="s2id_pagination-length"]/a')))
    dropdown.click()

    # Click "100" option
    option_100 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="select2-drop"]/ul/li[4]/div')))
    option_100.click()


def extract_data():
    """Extract leaderboard usernames and scores"""
    global leaderboard_data
    time.sleep(5)  # Ensure content is fully loaded

    # Wait for leaderboard containers
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "leaderboard-list-view")))

    # Extract leaderboard entries
    leaderboards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "leaderboard-list-view")))

    for leaderboard in leaderboards:
        try:
            # Extract Username
            username_element = leaderboard.find_element(By.CSS_SELECTOR, ".span-flex-4 a")
            username = username_element.text.strip()

            # Extract Score
            score_element = leaderboard.find_element(By.CSS_SELECTOR, ".span-flex-3")
            score = score_element.text.strip()

            # Store data
            leaderboard_data.append([username, score])
        except Exception as e:
            print("Skipping leaderboard due to error:", e)
    
def sleep():
    time.sleep(3)       # 3 seconds


def save_data():
    """Save leaderboard data to CSV"""
    csv_filename = "hackerrank_leaderboard.csv"
    if leaderboard_data:
        with open(csv_filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["HackerRank ID", "Score"])
            writer.writerows(leaderboard_data)

        print(f"Data saved successfully to {csv_filename}")
    else:
        print("No data extracted! Check element selectors.")
    


page_path = [
    '//*[@id="content"]/div/div/section/div[4]/div[1]/ul/li[4]/a',
    '//*[@id="content"]/div/div/section/div[4]/div[1]/ul/li[5]/a'
]

def move_to_next_page(idx):
    """Move to the next page"""
    try:
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, page_path[idx])))
        next_button.click()
        time.sleep(3)  # Wait for page to load
        return True  # Indicate success
    except Exception as e:
        print("No more pages or error clicking Next:", e)
        return False  # Stop loop if no more pages

def close_driver():
    # close window
    driver.quit()


# **Main Execution**
if __name__ == "__main__":
    open_chrome()
    change_view_per_page()

    extract_data()      # 1st page
    move_to_next_page(0)     # 2nd page

    extract_data()      # 2nd 
    move_to_next_page(1)

    extract_data()  # 3rd

    # save data
    save_data()
    close_driver()

    print("Total data:", len(leaderboard_data))
