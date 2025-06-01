import httpx


async def fetch_egrul_data(inn: str) -> dict:
    url = f"https://egrul.itsoft.ru/{inn}.json"  # Лучше без .gz, чтобы не путаться
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
