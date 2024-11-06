import logging
import time
import redis
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Redis configuration
redis_host = "localhost"
redis_port = 6379
r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

# Logging configuration
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/linkedin_profiles_scraper2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInProfileScraper:
    def __init__(self):
        logger.info("Initializing Chrome WebDriver...")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def login(self, username, password):
        logger.info("Logging into LinkedIn...")
        self.driver.get('https://www.linkedin.com/login')
        time.sleep(3)
        self.driver.find_element(By.ID, 'username').send_keys(username)
        self.driver.find_element(By.ID, 'password').send_keys(password)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)

    def infinite_scroll(self, profile_url):
        """Perform infinite scroll until all posts are loaded.(For testing purpose 3 scrolls are taken into account)"""
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
        """Scrape posts along with post dates, lengths, likes, and comments, and queue new profile URLs."""
        self.infinite_scroll(profile_url)

        posts = []
        try:
            post_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2")
            logger.info(f"Found {len(post_elements)} posts on profile: {profile_url}")

            for post in post_elements:
                post_text = post.text
                post_length = len(post_text.split())

                # Extract post date
                try:
                    post_date = post.find_element(By.CSS_SELECTOR, "span.update-components-actor__sub-description").text
                except Exception as e:
                    post_date = "Unknown"
                    logger.error(f"Error extracting date from post: {e}")

                # Extract likes count
                try:
                    likes = post.find_element(By.CSS_SELECTOR, ".social-details-social-counts__reactions-count").text
                except:
                    likes = "0"

                # Extract comments count
                try:
                    comments = post.find_element(By.CSS_SELECTOR, ".social-details-social-counts__comments").text
                except:
                    comments = "0"

                # Detect new LinkedIn profile URLs within the post content and comments
                new_profiles = self.detect_new_profiles(post)
                for new_profile in new_profiles:
                    if not r.sismember('processed_profiles', new_profile):
                        r.lpush('profile_queue', new_profile)
                        r.sadd('processed_profiles', new_profile)
                        logger.info(f"New profile URL {new_profile} added to queue.")

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
        self.save_posts_to_file(posts, profile_url)

    def detect_new_profiles(self, post):
        """Detect LinkedIn profile URLs in comments or post content."""
        profile_urls = set()

        try:
            # Detect profile URLs in the main post content
            profile_urls.update(re.findall(r'https://www\.linkedin\.com/in/[\w-]+', post.text))

            # Find LinkedIn profile links in the comments
            try:
                comment_container = post.find_element(By.CSS_SELECTOR, "div.comments-comment-list__container")
                profile_links = comment_container.find_elements(By.CSS_SELECTOR, "a.app-aware-link.tap-target.overflow-hidden")
                for link in profile_links:
                    href = link.get_attribute("href")
                    if href and "linkedin.com/in/" in href:
                        profile_urls.add(href)
                        logger.info(f"Profile URL detected in comments: {href}")
            except Exception as e:
                logger.warning(f"Error detecting profile URLs in comments: {e}")

        except Exception as e:
            logger.error(f"Error detecting new profiles in post: {e}")
        
        return list(profile_urls)

    def save_posts_to_file(self, posts, profile_url):
        """Save the posts data to an individual JSON file."""
        os.makedirs("profile_data", exist_ok=True)
        file_name = f'profile_data/{profile_url.split("/")[-2]}_posts.json'
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=4)
            logger.info(f"Data for {profile_url} saved to {file_name}")
        except Exception as e:
            logger.error(f"Error saving posts to file {file_name}: {e}")

    def run(self):
        empty_check_count = 0
        max_empty_checks = 5
        while True:
            profile_url = r.rpop('profile_queue')
            if profile_url:
                empty_check_count = 0
                self.scrape_posts(profile_url)
            else:
                empty_check_count += 1
                if empty_check_count >= max_empty_checks:
                    logger.info("No new URLs found, stopping after multiple checks.")
                    break
                logger.info("Queue is empty, waiting for new URLs...")
                time.sleep(10)

    def quit(self):
        logger.info("Closing WebDriver...")
        self.driver.quit()


if __name__ == "__main__":
    scraper = LinkedInProfileScraper()
    scraper.login('account@gmail.com', 'password') 
    scraper.run()
    scraper.quit()
