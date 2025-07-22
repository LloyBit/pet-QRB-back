import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
import aiohttp # переписать на fastapi
from config import BOT_TOKEN   # QR_SERVICE_URL, TOKEN_SERVICE_URL
from aiogram.filters import Command
from bot.models import qr_code_query, qr_code_response, access_token_request, access_token_response
from bot.keyboards import get_pay_keyboard, already_pay_keyboard

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)    
# Тарифы. Вынести из клиента в сервер
TARIFFS = ["basic", "premium", "enterprise"]


bot = Bot(token=str(BOT_TOKEN))
dp = Dispatcher(bot=bot)


# /start обработчик
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    logger.info(f"Start command received from user {message.from_user.id}")
    await message.answer(
        "Привет, Я бот для оплаты токенов.\nНажми кнопку ниже, чтобы получить QR-код для оплаты.",
        reply_markup=get_pay_keyboard()
    )


# Запрос QR-кода от сервера
@dp.callback_query(lambda c: c.data == "qr_code")
async def process_payment_qr(callback: types.CallbackQuery):
    if callback.message:
        # Используем pydantic модель для формирования запроса на QR-код
        query = qr_code_query(
            user_id=callback.from_user.id,
            tarif="basic"  # Здесь можно добавить выбор тарифа, сейчас по умолчанию "basic"
        )
        
        # Отправляем запрос на сервер
        async with aiohttp.ClientSession() as session:
            logger.info(f"Query: {query.model_dump()}")
            async with session.post(f"http://localhost:8000/qr_code/image/", json=query.model_dump()) as resp:
                if resp.status == 200:
                    # Получаем изображение QR-кода
                    qr_image_data = await resp.read()
                    
                    # Создаем InputFile для отправки изображения
                    input_file = BufferedInputFile(
                        qr_image_data, 
                        filename=f"qr_code_{query.user_id}_{query.tarif}.png"
                    )
                    
                    # Отправляем изображение в Telegram
                    await callback.message.answer_photo(
                        photo=input_file,
                        caption=f"QR Code для оплаты\nUser ID: {query.user_id}\nTariff: {query.tarif}"
                    )
                else:
                    await callback.message.answer(f"Ошибка получения QR-кода: {resp.status}")

# Запрос токена если оплата прошла на апи check_payment


# Запуск бота
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))