from g4f.client import Client
from sentence_transformers import SentenceTransformer, util
from config import IMAGE_MODEL_LIST, TEXT_MODEL_LIST, negative_responses
from app.images import download_image_from_url

class InvalidAnswerError(Exception):
    def __init__(self, message):
        super().__init__(message)
        print(message)  


similarity_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def check_similarity(prompt, response, threshold=0.7):
    embeddings = similarity_model.encode([prompt, response])
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
    return similarity >= threshold

async def ask_gpt(response):
    client = Client()
    
    for model in TEXT_MODEL_LIST:
        try:
            # Первый запрос
            answer = await client.chat.completions.async_create(
                model=model,
                messages=[{"role": "user", "content": response}],
            )
            answer_content = answer.choices[0].message.content # Извлекаем текст ответа
            
            # Второй запрос для проверки
            validation_response = await client.chat.completions.async_create(
                model=model,
                messages=[{
                    "role": "user", 
                    "content": (f'Проверь свой ответ на мой запрос: запрос - {response} | '
                                f'твой ответ - {answer_content}. В случае, если ты ответил верно, '
                                'просто снова дай такой же ответ, если нет, напиши сначала.')
                }],
            )
            validation_content = validation_response.choices[0].message.content  # Извлекаем проверочный ответ
            print(validation_content)
            # Семантическое сравнение
            if not check_similarity(answer_content, validation_content):
                raise InvalidAnswerError("Ответ нейросети недостаточно похож на проверочный ответ.")
            
            return f'{model}: {validation_content}'

        except Exception as err:
            print(f'Ошибка: {err}')
    
    return None

async def generate_image_gpt(response):
    client = Client()
    img_path = []

    try:
        # Первый запрос для генерации текста-промта для изображения
        answer = await client.chat.completions.async_create(
            model="gpt-4o",
            messages=[{"role": "user", "content": response}],
        )
        first_answer_content = answer.choices[0].message.content
        second_answer = await client.chat.completions.async_create(
            model="gpt-4o",
            messages=[{"role": "user", "content": response}],
        )
        second_answer_content = second_answer.choices[0].message.content
        # Проверка: семантическое сходство и ключевые слова
        if not check_similarity(second_answer_content, first_answer_content):
            print("Ответ GPT не соответствует запросу, требуется повторный запрос.")
            answer = await client.chat.completions.async_create(
                model="gpt-4o",
                messages=[{"role": "user", "content": response}],
            )
            answer_content = answer.choices[0].message.content
        
        # Проверка наличия ключевых слов
        if any(neg_response in answer_content for neg_response in negative_responses):
            raise InvalidAnswerError("Ответ нейросети содержит негативный результат")  

        print(f'Промт - {answer_content}')
        response = answer_content

    except Exception as err:
        print(f'Ошибка при получении ответа от GPT: {err}')
        return img_path  # Возвращаем пустой список, если произошла ошибка
    
    # Запуск генерации изображения
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
                print(f'!!!\nОшибка: \nМодель: {model}\nОшибка: {err}!!!')

    return img_path