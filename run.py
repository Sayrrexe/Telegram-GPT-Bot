import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.user import user
from config import TOKEN

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создание обработчика для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Форматирование вывода
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logger.addHandler(console_handler)

# Создание бота
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def startup(dispatcher: Dispatcher):
    logger.info('Bot is starting up...')

async def shutdown(dispatcher: Dispatcher):
    logger.info('Bot is shutting down...')
    exit(0)

async def main():
    dp = Dispatcher()
    dp.include_router(user)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
