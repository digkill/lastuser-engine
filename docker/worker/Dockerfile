FROM python:3.12

WORKDIR /worker

# Установка системных зависимостей для Playwright
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*


COPY ./worker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps


COPY ./worker ./
COPY ./shared ./shared

ENV PYTHONPATH=/worker

CMD ["python", "main.py"]