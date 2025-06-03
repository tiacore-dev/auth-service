import os

from dotenv import load_dotenv

from app import create_app
from app.config import ConfigName

load_dotenv()

# Порт и биндинг
PORT = 8000
CONFIG_NAME = ConfigName(os.getenv("CONFIG_NAME", "Development"))


app = create_app(config_name=CONFIG_NAME)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(PORT), reload=True)
