from g4f.client import Client
import difflib
from config import IMAGE_MODEL_LIST, TEXT_MODEL_LIST, negative_responses
from app.images import download_image_from_url

class InvalidAnswerError(Exception):
    def __init__(self, message):
        super().__init__(message)

def check_similarity(prompt, response, threshold=0.6):
    similarity_ratio = difflib.SequenceMatcher(None, prompt, response).ratio()
    print('СХОЖЕСТЬ ТЕКСТОВ -', similarity_ratio)
    return similarity_ratio >= threshold

async def ask_gpt(response):
    client = Client()
    attemps = 0
    while True:
        for model in TEXT_MODEL_LIST:
            try:
                answer = await client.chat.completions.async_create(
                    model=model,
                    messages=[{"role": "user", "content": response}],
                )
                answer_content = answer.choices[0].message.content
            
            
                validation_response = await client.chat.completions.async_create(
                    model=model,
                    messages=[{
                        "role": "user", 
                        "content": (f'Проверь свой ответ на мой запрос: запрос - {response} | '
                                    f'твой ответ - {answer_content}. В случае, если ты ответил верно, '
                                    'просто снова дай такой же ответ, если нет, напиши сначала.')
                        }],
                )
                validation_content = validation_response.choices[0].message.content
            
                if not check_similarity(answer_content, validation_content):
                    raise InvalidAnswerError("Ответ нейросети недостаточно похож на проверочный ответ.")
                
                if any(neg_response in validation_content for neg_response in negative_responses):
                    raise InvalidAnswerError("Ответ нейросети Содержит нежелательные слова!")
            
                return f'{model}: {validation_content}'

            except Exception as err:
                print(f'Ошибка: {err}')
                attemps += 1
                if attemps >= 10:
                    return None
                
    

async def generate_image_gpt(response):
    client = Client()
    img_path = []
    while True:
        try:
            answer = await client.chat.completions.async_create(
                model="gpt-4o",
                messages=[{"role": "user", "content": response}],
            )
            second_answer = await client.chat.completions.async_create(
                model="gpt-4o",
                messages=[{"role": "user", "content": response}],
            )
            second_answer_content = second_answer.choices[0].message.content
            first_answer_content = answer.choices[0].message.content
            if not check_similarity(second_answer_content, first_answer_content, threshold=0.5):
                print("Ответы не прошли проверку на сходство. Повторный запрос...")
                continue
        
            if any(neg_response in second_answer_content for neg_response in negative_responses):
                print("Ответы Содержат негативные результат")
                continue

            print(f'Промт- {second_answer_content}')
            response = second_answer_content
            break

        except Exception as err:
            print(f'Ошибка при получении ответа от GPT: {err}')
            return img_path  
    
    for i in range(2):
        for model in IMAGE_MODEL_LIST:
            try:
                answer = await client.images.async_generate(
                    model=model,
                    prompt=response,
                )
                if answer.data:  
                    image_url = answer.data[0].url
                    img = await download_image_from_url(url=image_url)
                    img_path.append(img)
                else:
                    print(f'Нет данных для модели: {model}')
            except Exception as err:
                print(f'!!!\nОшибка: \nМодель: {model}\nОшибка: {err}\n!!!')

    return img_path
