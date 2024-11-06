import logging
import json
import time
import re
import os
import redis
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Initialize Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/linkedin_profiles_crawler2.log'),  
        logging.StreamHandler()  
    ]
)

logger = logging.getLogger(__name__)

class LinkedInProfileCrawler:
    def __init__(self):
        logger.info("Initializing Chrome WebDriver...")
        options = Options()
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        options.add_argument(f"user-agent={user_agent}")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.profile_urls = []

    def login(self, username, password):
        logger.info("Logging into LinkedIn...")
        self.driver.get('https://www.linkedin.com/login')
        time.sleep(3)
        self.driver.find_element(By.ID, 'username').send_keys(username)
        self.driver.find_element(By.ID, 'password').send_keys(password)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)

    def gather_profile_urls(self, base_url):
        logger.info(f"Visiting {base_url} to gather profile URLs...")
        self.driver.get(base_url)
        time.sleep(3)
        self.extract_profile_urls()
        logger.info("Profile URLs collected and added to Redis queue.")

    def extract_profile_urls(self):
        links = self.driver.find_elements(By.CSS_SELECTOR, "a.app-aware-link")
        for link in links:
            url = link.get_attribute('href')
            if self.is_valid_profile_url(url):
                # url = url.rstrip('/') + '/recent-activity/all/'
                print(url)
                r.lpush('profile_queue', url)

                logger.info(f"Added to queue: {url}")

    def is_valid_profile_url(self, url):
        return bool(re.match(r'https?://(www\.)?linkedin\.com/in/', url))

    def quit(self):
        logger.info("Closing WebDriver...")
        self.driver.quit()

if __name__ == "__main__":
    crawler = LinkedInProfileCrawler()
    crawler.login('account@gmail.com', 'password')  
    crawler.gather_profile_urls('https://www.linkedin.com/in/ansuman-simanta-sekhar-bhujabala/')
    crawler.quit()
