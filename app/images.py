from aiogram import F
import requests
import os
import random


async def download_image_from_url(url, save_dir='images'):
    # Создаем директорию, если её нет
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    path = url.split('/')[-1]
    print(path)
    path = path.split('.')[0]
    random_number = random.randint(1000, 10000)
    path = os.path.join(save_dir, f"{random_number}_{path}.jpg")  # Сохраняем в директорию с уникальным именем
    p = requests.get(url)
    
    with open(path, "wb") as out:
        out.write(p.content)
    
    return path