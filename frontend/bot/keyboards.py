from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Клавиатура для оплаты
def get_pay_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", callback_data="qr_code")]
        ]
    )

# Клавиатура для проверки опплаты
def already_pay_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Уже оплатил", callback_data="check_payment")]
        ]
    )