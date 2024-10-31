import os
import random
import aiohttp

async def download_image_from_url(url, save_dir='images'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    path = url.split('/')[-1]
    path = path.split('.')[0]
    random_number = random.randint(1000, 10000)
    path = os.path.join(save_dir, f"{random_number}_{path}.jpg") 
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(path, "wb") as out:
                        out.write(await response.read())
                    return path
                else:
                    print(f"Ошибка при скачивании: статус {response.status}")
                    return None
    except Exception as err:
        print(f"Произошла ошибка: {err}")
        return None
