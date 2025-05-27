FROM python:3.11-slim

# Instalar libs para rodar navegadores (base Ubuntu)
RUN apt update && apt install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 libgtk-3-0 libdrm2 libxss1 libxcb1 libxshmfence1 libxext6 wget curl unzip gnupg && \
    rm -rf /var/lib/apt/lists/*

# Diretório do app
WORKDIR /app

# Copia requirements e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala navegadores do Playwright
RUN python -m playwright install --with-deps

# Copia o código
COPY . .

# Expor porta
EXPOSE 8000

# Comando para rodar FastAPI
CMD ["uvicorn", "api.core:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
