
---

# LinkedIn Scraper

This project is a LinkedIn scraper built using Python, Selenium, and Redis. The scraper logs into LinkedIn and scrapes profile posts, comments, and metadata such as likes and comments count. Extracted profile URLs are stored in a Redis queue for further processing.

**Note**: This project is still a work in progress, with certain features yet to be fully implemented, such as scraping 500 profiles and complete Redis functionality.
## Architecture
![Screenshot from 2024-10-23 17-25-28](https://github.com/user-attachments/assets/26cde223-1afb-43cb-83bf-86715cfb0e3c)
![Screenshot from 2024-10-23 17-25-51](https://github.com/user-attachments/assets/50c1fd7e-92b6-4197-93cc-4d4d0c2c894d)
![Screenshot from 2024-10-23 17-26-06](https://github.com/user-attachments/assets/56d4fa4e-efd4-4ece-b1aa-b8ed5125784e)

## Output
![Screenshot from 2024-11-06 08-27-54](https://github.com/user-attachments/assets/f8642c57-028c-4ca7-a8a9-68e0787717fb)

![Screenshot from 2024-10-23 17-38-22](https://github.com/user-attachments/assets/432857d6-5c8d-4a3e-bf90-a100ae1ae747)



## Features

- Logs into LinkedIn using provided credentials.
- Infinite scroll functionality to scrape all posts from a profile.
- Scrapes post text, post date, number of likes, comments, and more.
- Extracts profile URLs from the comments section of each post.
- Stores profile URLs in Redis for further processing.
- Saves scraped data in JSON files.

## Limitations and Future Work

- **LinkedIn Account Restrictions**: Due to limitations and restrictions from LinkedIn, this scraper has not been tested on scraping 500 profiles to avoid triggering LinkedIn's security mechanisms and getting my account blocked.
- **Google Captcha / Network Blocking**: The scraper may encounter Google captchas, which could block your IP from continuing. This is a potential roadblock when scaling the number of profiles scraped.
- **IP Rotation**: To avoid IP blocks and scraping limits, a rotating IP or proxy setup would be needed to scale this project effectively. I have not yet implemented this solution but plan to include it in the future.
- **Redis Queue Functionality**: The part of the project involving Redis for queue management is partially implemented. Although URLs are being stored in Redis, the full functionality for profile URL queue processing, tracking, and logging is incomplete and needs further work.

## Installation

### Prerequisites

- Python 3.9+
- Docker
- Redis

### Steps to Run

1. Clone the repository:

   ```bash
   git clone https://github.com/Ansumanbhujabal/Linkedin_Scraper.git
   ```

2. Build the Docker image:

   ```bash
   docker build -t linkedin-scraper .
   ```

3. Run the Docker container:

   ```bash
   docker run -d linkedin-scraper
   ```

   This will launch the scraper inside a Docker container.

4. To stop the container:

   ```bash
   docker stop <container_id>
   ```

### Requirements

All Python dependencies are listed in `requirements.txt` and are installed automatically during the Docker build.

- Selenium
- WebDriver Manager
- Redis
- Other dependencies listed in `requirements.txt`

### Redis

To start the Redis server locally:

```bash
redis-server
```

## Future Improvements

- **Rotating IP Support**: Implement IP rotation using proxy services to avoid network blocks from LinkedIn.
- **Complete Redis Integration**: Fully implement Redis for managing profile queues and retry mechanisms for failed attempts.
- **Handling LinkedIn Limits**: Implement better handling of LinkedIn's rate limits and account restrictions.

## Disclaimer

This project is for educational purposes only. Be aware of LinkedIn's terms and conditions regarding web scraping and automated actions. Always ensure that your use of scraping tools complies with applicable terms of service.

---

### License

Usage Restricted to Author 

---
