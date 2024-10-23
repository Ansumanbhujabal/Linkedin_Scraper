import logging
import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_profiles_scraper.log'),  
        logging.StreamHandler()  
    ]
)

logger = logging.getLogger(__name__)

class LinkedInProfileScraper:
    def __init__(self):
        logger.info("Initializing the Chrome WebDriver...")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.profile_urls = [] 

    def login(self, username, password):
        """Log into LinkedIn with provided credentials."""
        logger.info("Attempting to log into LinkedIn...")
        self.driver.get('https://www.linkedin.com/login')
        time.sleep(5)
        
        try:
            self.driver.find_element(By.ID, 'username').send_keys(username)
            self.driver.find_element(By.ID, 'password').send_keys(password)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(5)
            logger.info("Login successful!")
        except Exception as e:
            logger.error(f"Error during login: {e}")

    def infinite_scroll(self, base_url):
        logger.info(f"URL: {base_url}")
        self.driver.get(base_url)
        time.sleep(5)

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0

        while len(self.profile_urls) < 100: 
            logger.info("Scrolling to load more content...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5) 

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts >= 3:
                    logger.info("No more content to scroll through.")
                    break
            else:
                scroll_attempts = 0
                last_height = new_height

            self.extract_profile_urls()

        logger.info(f"Finished scraping. Total profiles collected: {len(self.profile_urls)}")

    def extract_profile_urls(self):
        """Extract profile URLs from the visible page."""
        profile_links = self.driver.find_elements(By.CSS_SELECTOR, "a.app-aware-link")

        for link in profile_links:
            profile_url = link.get_attribute('href')
            if self.is_linked_in_profile(profile_url):
                profile_url = profile_url.rstrip('/') + '/recent-activity/all/'
                
                if profile_url not in self.profile_urls:  
                    self.profile_urls.append(profile_url)
                    logger.info(f"Profile URL extracted: {profile_url}")

        logger.info(f"Current number of unique profiles collected: {len(self.profile_urls)}")

    def is_linked_in_profile(self, url):
        return bool(re.match(r'https?://(www\.)?linkedin\.com/in/', url))

    def save_profile_urls_to_json(self):
        file_name = 'scraped_profile_urls.json'
        with open(file_name, 'w') as f:
            json.dump(self.profile_urls, f, indent=4)
        logger.info(f"Profile URLs saved to {file_name}")

    def quit(self):
        logger.info("Closing the Chrome WebDriver...")
        self.driver.quit()


if __name__ == "__main__":
    scraper = LinkedInProfileScraper()
    scraper.login('account@gmail.com', 'password') 
    target_url = 'https://www.linkedin.com/school/netaji-subhas-university-of-technology-nsut/people/'  
    scraper.infinite_scroll(target_url)
    scraper.save_profile_urls_to_json()
    scraper.quit()
