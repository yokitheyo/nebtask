import os
import subprocess
import logging
import asyncio

from app.db.init_db import init_db
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations() -> None:
    logger.info("Запуск миграций базы данных")

    try:
        if not os.path.exists("alembic/versions"):
            os.makedirs("alembic/versions", exist_ok=True)

        try:
            subprocess.run(
                ["alembic", "current"], check=True, capture_output=True, text=True
            )
        except subprocess.CalledProcessError:
            logger.info("Создание начальной миграции")
            subprocess.run(
                ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
                check=True,
            )

        logger.info("Применение миграций")
        subprocess.run(["alembic", "upgrade", "head"], check=True)

        logger.info("Миграции успешно применены")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении миграций: {e}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при выполнении миграций: {e}")
        raise


async def setup_db() -> None:
    run_migrations()

    await init_db()


if __name__ == "__main__":
    asyncio.run(setup_db())
