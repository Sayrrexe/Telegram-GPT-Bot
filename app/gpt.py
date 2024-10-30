from os import error
from g4f.client import Client
import requests

from config import IMAGE_MODEL_LIST, TEXT_MODEL_LIST
from app.images import download_image_from_url
    
async def ask_gpt(response):
    client = Client()
    
    for model in TEXT_MODEL_LIST:
        try:
            answer = await client.chat.completions.async_create(
                model=model,
                messages=[{"role": "user", "content": response}],
            )
            response = await client.chat.completions.async_create(
                model=model,
                messages=[{"role": "user", "content": f'Проверь свой ответ на мой запрос: запрос - {response} | твой ответ  - {answer}, в случае если ты ответил верно, просто сного дай такой же ответ, если нет напиши сначала'}],
            )
            
            return f'{model}: {response.choices[0].message.content}'
        except Exception as err:
            print(f'Ошибка: {err}')
        continue
    
async def generate_image_gpt(response):
    client = Client()
    img_path = []
    
    
    try:
        answer = await client.chat.completions.async_create(
            model="gpt-4o",
            messages=[{"role": "user", "content": response}],
        )
        if len(answer.choices[0].message.content) > 200:
            answer = await client.chat.completions.async_create(
            model="gpt-4o",
            messages=[{"role": "user", "content": response}],
        )
        print(f'Промт - {answer.choices[0].message.content}')
        response = answer.choices[0].message.content
    except Exception as err:
        print(f'Ошибка при получении ответа от GPT: {err}')
        return img_path  # Возвращаем пустой список, если произошла ошибка
    
    for i in range(2):
        for model in IMAGE_MODEL_LIST:
            try:
                answer = await client.images.async_generate(
                    model=model,
                    prompt=response,
                )
                if answer.data:  # Проверяем, что данные не пустые
                    image_url = answer.data[0].url
                    img = await download_image_from_url(url=image_url)
                    img_path.append(img)
                else:
                    print(f'Нет данных для модели: {model}')
            except Exception as err:
                print(f'!!!\nОшибка: \nМодель: {model}\nОшибка: {err}!!!')

    return img_path
