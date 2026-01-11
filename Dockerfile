FROM ubuntu:22.04


RUN apt-get update && apt-get install -y \
    libreoffice \
    python3 \
    python3-pip \
    ghostscript \
    build-essential \
    libmagic1 \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
