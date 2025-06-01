import asyncio

from app.utils.entity_data_get import fetch_egrul_data


async def main():
    data = await fetch_egrul_data("7710140679")
    print(data)


if __name__ == "__main__":
    asyncio.run(main())
