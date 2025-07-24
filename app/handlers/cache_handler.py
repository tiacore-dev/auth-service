from fastapi_cache import FastAPICache


async def blacklist_token(jti: str):
    backend = FastAPICache.get_backend()
    await backend.set(f"blacklist:{jti}", "true".encode("utf-8"))
