import logging

from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.enums import ChatAction
from pydantic import ValidationError

from app.gpt import ask_gpt, generate_image_gpt
import os

from config import TEXT_RULERS

# Словарь для хранения истории запросов каждого пользователя
user_data = {}

user = Router()
logger = logging.getLogger(__name__)

@user.message(CommandStart())
async def cmd_start(message: types.Message):
    print(f"Received /start command from user {message.from_user.id}")
    await message.answer('Добро пожаловать в бот!\nЧто напишешь, то и будет запросом\nКартинки генерируются следующим образом\n"/img text" в 1 сообщение')
    

class UserHistory:
    def __init__(self, max_size=6):
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
    print(f"Received /history command from user {user_id}")
    if user_id in user_data:
        history = user_data[user_id].get_history()
        if history:
            history_text = "\n".join(history)
            await message.reply(f"Твоя история:\n{history_text}", parse_mode="MARKDOWN")
        else:
            await message.reply("У тебя ещё нет истории!")
    else:
        await message.reply("У тебя ещё нет истории!")
        
@user.message(Command('clear'))
async def clear_history(message: types.Message):
    user_id = message.from_user.id
    print(f"Received /clear command from user {user_id}")
    if user_id in user_data:
        user_data[user_id].clear_history()
    await message.answer('Удалил!')
    
@user.message(Command('img'))
async def start_command(message: types.Message):
    print(f"Received /img command from user {message.from_user.id} with args: {message.text}")
    args = message.text.split(' ')
    args.pop(0)
    result = ' '.join(args)
    media_group = MediaGroupBuilder()

    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.UPLOAD_PHOTO)

    if args:
        await message.answer('Генерируем...')
        paths = await generate_image_gpt(response=f'Сгенерируй промт изображения, которое передает основные черты и настроение. Добавь в него такие детали, как детали о персонаже. Пусть изображение выглядит. Вот конкретные детали, которые нужно включить: {result}. Оставь только промт и переведи его на английский!')

        await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.UPLOAD_PHOTO)

        for answer in paths:
            print(f"Generated image path: {answer}")
            try:
                if os.path.exists(f'{answer}.jpg'):
                    media_group.add(type="photo", media=open(f'{answer}.jpg', 'rb'))
                elif os.path.exists(answer):
                    media_group.add(type="photo", media=types.FSInputFile(answer))
                else:
                    print(f"File not found: {answer} or {answer}.jpg")
            except Exception as e:
                print(f"Error adding media: {e}")

        try:
            await message.answer_media_group(media_group.build())
        except Exception as e:
            print(f"Error sending media group: {e}")
            await message.answer_media_group(media_group)

        for answer in paths:
            try:
                if os.path.exists(answer):
                    os.remove(answer)
                    print(f"Deleted file: {answer}")
            except Exception as e:
                print(f"Error deleting file: {e}")
    else:
        await message.reply("Ты не передал никаких аргументов.")


@user.message(F.text)
async def generate(message: types.Message):
    text = message.text
    user_id = message.from_user.id
    if text == '/clear':
        return
    print(f"Received text message from user {user_id}: {text}")
    
    if user_id not in user_data:
        user_data[user_id] = UserHistory()
    
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    
    history = user_data[user_id].get_history()
    history_text = "\n".join(history) if history else ""
    if history_text == '':
        answer = await ask_gpt(text)
        print(f"Generated First response to user {user_id}: {answer}")
    else:
        answer = await ask_gpt(f'{TEXT_RULERS} Память:{history_text}\nЗапрос: {message.text} ')
        print(f"Generated response to user {user_id}: {answer}")
        answer = answer.replace("_", "\_").replace("*", "\*").replace("[", "\[").replace("]", "\]").replace("(", "\(").replace(")", "\)").replace("~", "\~").replace("`", "\`")
    try:
        if answer == None:
            await message.answer('При генерации произошла ошибка, попробуйте ещё 1 раз!')
        else:
            await message.answer(answer, parse_mode='MARKDOWN')
    except Exception as error:
        print(f"Error sending message to user {user_id}: {error}")
        answer = await ask_gpt(f'! Внимание прошлый ответ не был отправлен из-за ошибки {error} Постарайся перефразировать ответ! {TEXT_RULERS} память:{history_text}. запрос:{message.text}')
        await message.answer(answer, parse_mode='MARKDOWN')
    user_data[user_id].add_query(f'Пользователь: <{message.text}>')
    user_data[user_id].add_query(f'Ответ: <{answer}>')
