# ===== BASE =====
FROM python:3.12-slim AS base
WORKDIR /app


ARG GITHUB_TOKEN
RUN --mount=type=secret,id=github_token \
  GITHUB_TOKEN=$(cat /run/secrets/github_token) \
  pip install --no-cache-dir \
  git+https://${GITHUB_TOKEN}@github.com/tiacore-dev/tiacore-lib.git@master


RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*


COPY requirements.txt ./



RUN pip install --no-cache-dir -r requirements.txt


# ===== TESTING =====
FROM base AS test
COPY . .

CMD ruff check .  && pytest --maxfail=3 --disable-warnings
# ===== FINAL =====
FROM base AS prod

COPY . .


