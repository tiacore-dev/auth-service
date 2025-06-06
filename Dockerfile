# ===== BASE =====
FROM python:3.12-slim AS base
WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*


ARG LIB_TOKEN
RUN --mount=type=secret,id=lib_repo_token \
  LIB_TOKEN=$(cat /run/secrets/lib_repo_token) \
  pip install git+https://${LIB_TOKEN}@github.com/tiacore-dev/tiacore-lib.git@master



COPY requirements.txt ./



RUN pip install --no-cache-dir -r requirements.txt


# ===== TESTING =====
FROM base AS test
COPY . .

CMD ruff check .  && pytest --maxfail=3 --disable-warnings
# ===== FINAL =====
FROM base AS prod

COPY . .


