import logging
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.enums import ChatAction

from app.gpt import ask_gpt, generate_image_gpt
import os

from config import TEXT_RULERS

# Словарь для хранения истории запросов каждого пользователя
user_data = {}

user = Router()
logger = logging.getLogger(__name__)

@user.message(CommandStart())
async def cmd_start(message: types.Message):
    logger.info(f"Received /start command from user {message.from_user.id}")
    await message.answer('Добро пожаловать в бот!\nЧто напишешь, то и будет запросом\nКартинки генерируются следующим образом\n"/img text" в 1 сообщение')
    

class UserHistory:
    def __init__(self, max_size=10):
        self.max_size = max_size
        self.history = []

    def add_query(self, query):
        if len(self.history) >= self.max_size:
            self.history.pop(0)  # Удаляем самый старый запрос
        self.history.append(query)

    def get_history(self):
        return self.history
    
    def clear_history(self):
        self.history = []
        return


@user.message(Command('history'))
async def send_history(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"Received /history command from user {user_id}")
    if user_id in user_data:
        history = user_data[user_id].get_history()
        if history:
            history_text = "\n".join(history)
            await message.reply(f"Твоя история:\n{history_text}")
        else:
            await message.reply("У тебя ещё нет истории!")
    else:
        await message.reply("У тебя ещё нет истории!")
        
@user.message(Command('clear'))
async def clear_history(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"Received /clear command from user {user_id}")
    if user_id in user_data:
        user_data[user_id].clear_history()
    await message.answer('Удалил!')
    
@user.message(Command('img'))
async def start_command(message: types.Message):
    logger.info(f"Received /img command from user {message.from_user.id} with args: {message.text}")
    args = message.text.split(' ')
    args.pop(0)
    result = ' '.join(args)
    media_group = MediaGroupBuilder()

    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.UPLOAD_DOCUMENT)

    if args:
        await message.answer('Генерируем...')
        paths = await generate_image_gpt(response=f'Составь промт для генерации картинки с моими параметрами, если нужно переведи на английский язык: {result} ! Пожалуйста, оставь только промт и ничего более, что бы я мог его использовать в своей программе!')

        await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.UPLOAD_PHOTO)

        for answer in paths:
            logger.info(f"Generated image path: {answer}")
            try:
                if os.path.exists(f'{answer}.jpg'):
                    media_group.add(type="photo", media=open(f'{answer}.jpg', 'rb'))
                elif os.path.exists(answer):
                    media_group.add(type="photo", media=types.FSInputFile(answer))
                else:
                    logger.error(f"File not found: {answer} or {answer}.jpg")
            except Exception as e:
                logger.error(f"Error adding media: {e}")

        try:
            await message.answer_media_group(media_group.build())
        except Exception as e:
            logger.error(f"Error sending media group: {e}")
            await message.answer_media_group(media_group)

        for answer in paths:
            try:
                if os.path.exists(answer):
                    os.remove(answer)
                    logger.info(f"Deleted file: {answer}")
            except Exception as e:
                logger.error(f"Error deleting file: {e}")
    else:
        await message.reply("Ты не передал никаких аргументов.")


@user.message(F.text)
async def generate(message: types.Message):
    text = message.text
    user_id = message.from_user.id
    logger.info(f"Received text message from user {user_id}: {text}")
    
    if user_id not in user_data:
        user_data[user_id] = UserHistory()
    
    history = user_data[user_id].get_history()
    history_text = "\n".join(history) if history else ""

    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    answer = await ask_gpt(f'{TEXT_RULERS} старые сообщения:{history_text}\nВот мой запрос сейчас, постарайся дать на него ответ соблюдая правила {message.text} ')
    logger.info(f"Generated response to user {user_id}: {answer}")

    try:
        await message.answer(answer, parse_mode='MARKDOWN')
    except Exception as error:
        logger.error(f"Error sending message to user {user_id}: {error}")
        answer = await ask_gpt(f'! Внимание прошлый ответ не был отправлен из-за ошибки {error} Постарайся перефразировать ответ! {TEXT_RULERS}начало памяти прошлых сообщений {history_text}!конец памяти!Я:{message.text}')
        await message.answer(answer, parse_mode='MARKDOWN')
    user_data[user_id].add_query(f'Я: {message.text}')
    user_data[user_id].add_query(f'Ты: {answer}')
