import asyncio
import os
import sys
from alembic.config import Config
from alembic import command

async def main():
    print("Running Alembic migrations...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Database initialized successfully.")

if __name__ == "__main__":
    asyncio.run(main())
