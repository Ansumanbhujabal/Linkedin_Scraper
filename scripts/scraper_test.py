import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import redis
import json
from datetime import datetime
import re

r = redis.Redis(host='localhost', port=6379, db=0)

logging.basicConfig(
    level=logging.INFO,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_scraper.log'),  
        logging.StreamHandler()  
    ]
)


logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self):
        logger.info("Initializing the Chrome WebDriver...")
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

    def infinite_scroll(self, profile_url):
        """Perform infinite scroll until all posts are loaded."""
        logger.info(f"Navigating to profile URL: {profile_url}")
        self.driver.get(profile_url)
        time.sleep(5)

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0

        while True:
            logger.info("Scrolling to load more posts...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5) 
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts >= 3:
                    break
            else:
                scroll_attempts = 0
                last_height = new_height

    def scrape_posts(self, profile_url):
        """Scrape posts along with post dates and lengths."""
        self.infinite_scroll(profile_url)

        posts = []
        try:
            post_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2")
            logger.info(f"Found {len(post_elements)} posts on profile: {profile_url}")
            
            for post in post_elements:
                post_text = post.text
                post_length = len(post_text.split())  
                

                try:
                    post_date = post.find_element(By.CSS_SELECTOR, "span.update-components-actor__sub-description").text
                except Exception as e:
                    post_date = "Unknown"
                    logger.error(f"Error extracting date from post: {e}")

               
                try:
                    likes = post.find_element(By.CSS_SELECTOR, ".social-details-social-counts__reactions-count").text
                except:
                    likes = "0"
                try:
                    comments = post.find_element(By.CSS_SELECTOR, ".social-details-social-counts__comments").text
                except:
                    comments = "0"
                
                
                self.extract_profile_urls(post)
                
                post_data = {
                    'post_text': post_text,
                    'post_length': post_length,  
                    'post_date': post_date,      
                    'likes': likes,
                    'comments': comments
                }
                posts.append(post_data)
        except Exception as e:
            logger.error(f"Error while scraping posts from {profile_url}: {e}")

        return posts

    def extract_profile_urls(self, post):
        try:
            
            comment_container = post.find_element(By.CSS_SELECTOR, "div.comments-comment-list__container")
            logger.info(f"Comment container found: {comment_container}")
            
            
            profile_links = comment_container.find_elements(By.CSS_SELECTOR, "a.app-aware-link.tap-target.overflow-hidden")
            
           
            if not profile_links:
                logger.info("No profile links found in the comment section.")
            else:
                logger.info(f"Number of profile links found: {len(profile_links)}")

            
            for link in profile_links:
                profile_url = link.get_attribute('href')
                
                
                if self.is_linked_in_profile(profile_url):
                    if profile_url not in self.profile_urls:  
                        self.profile_urls.append(profile_url)
                        logger.info(f"Extracted profile URL: {profile_url}")
                    else:
                        logger.info(f"Duplicate profile URL skipped: {profile_url}")

        except Exception as e:
            logger.error(f"Error extracting profile URLs from post: {e}")

    def is_linked_in_profile(self, url):
        """Check if the URL is a LinkedIn profile URL."""
        return bool(re.match(r'https?://(www\.)?linkedin\.com/in/', url))

    def push_profiles_to_queue(self, profile_urls):
        logger.info(f"Pushing {len(profile_urls)} profile URLs to the Redis queue...")
        for url in profile_urls:
            r.lpush('profile_queue', url)
        logger.info("Profile URLs added to the queue successfully.")

    def process_next_profile(self):
        try:
            profile_url = r.lpop('profile_queue').decode('utf-8')
            logger.info(f"Processing profile: {profile_url}")
            posts = self.scrape_posts(profile_url)
            
            file_name = f'{profile_url.split("/")[-4]}_new.json'
            logger.info(f"File name is {file_name}")
            with open(file_name, 'w') as f:
                json.dump(posts, f, indent=4)
            logger.info(f"Data for {profile_url} saved to {file_name}")

           
            self.save_extracted_profile_urls()
        except Exception as e:
            logger.error(f"Error while processing profile: {e}")

    def save_extracted_profile_urls(self):
        """Save extracted profile URLs to a separate JSON file."""
        if self.profile_urls:
            with open('extracted_profile_urls.json', 'w') as f:
                json.dump(list(set(self.profile_urls)), f, indent=4) 
            logger.info(f"Extracted profile URLs saved to extracted_profile_urls.json")
        else:
            logger.info("No new profile URLs extracted.")

    def quit(self):
        logger.info("Closing the Chrome WebDriver...")
        self.driver.quit()

if __name__ == "__main__":
    scraper = LinkedInScraper()
    scraper.login('account@gmail.com', 'password') 

    scraper.push_profiles_to_queue(
    [
    "https://www.linkedin.com/in/parthmahajan08?miniProfileUrn=urn%3Ali%3Afsd_profile%3AACoAADgXi6ABhdLb2hPI0JbjcHOXYarasOo3U8Y",
    "https://www.linkedin.com/in/thesayansapui?miniProfileUrn=urn%3Ali%3Afsd_profile%3AACoAABLvt5EBM4ipDqL9lnMdKfGzrNuleJyDX2c",
    "https://www.linkedin.com/in/antrixshgupta?miniProfileUrn=urn%3Ali%3Afsd_profile%3AACoAACS2JSYBd4pvOYaBkYgGJq5d1VDH5F53OjA"
])
    
    scraper.process_next_profile()
    scraper.save_extracted_profile_urls()
    
    scraper.quit()
