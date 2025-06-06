# ===== BASE =====
FROM python:3.12-slim AS base
WORKDIR /app


ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=${GITHUB_TOKEN}


RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*


COPY requirements.txt ./
RUN sed -i "s|\${GITHUB_TOKEN}|${GITHUB_TOKEN}|g" requirements.txt


RUN pip install --no-cache-dir -r requirements.txt


# ===== TESTING =====
FROM base AS test
COPY . .

CMD ruff check .  && pytest --maxfail=3 --disable-warnings
# ===== FINAL =====
FROM base AS prod

COPY . .


