
FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg2 \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libappindicator1 \
    fonts-liberation \
    libu2f-udev \
    libgbm-dev \
    xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y google-chrome-stable

RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -N https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

ENV DISPLAY=:99
WORKDIR /app
COPY req.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /app
RUN apt-get update && apt-get install -y redis-server
RUN service redis-server start
CMD ["python", "scraper.py"]
