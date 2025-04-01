from keep_alive import keep_alive
import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile
)
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup

API_TOKEN = "7653537069:AAGXfNno-UqWoujFMmRECbJYqCpzdtJkEfQ"

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Состояния
class QuizCreation(StatesGroup):
    waiting_for_image = State()
    waiting_for_question = State()

# Команда /start или /new — показать кнопку "Создать новую викторину"
@router.message(Command("start"))
@router.message(Command("new"))
async def send_start_menu(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать новую викторину", callback_data="create_quiz")]
    ])
    await message.answer("Добро пожаловать! Что хотите сделать?", reply_markup=keyboard)

# Нажата кнопка "Создать новую викторину" — спросить про изображение
@router.callback_query(F.data == "create_quiz")
async def ask_for_image(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Загрузить изображение", callback_data="upload_image")],
        [InlineKeyboardButton(text="Пропустить изображение", callback_data="skip_image")]
    ])
    await state.clear()
    await callback.message.answer("Хочешь добавить изображение к вопросу?", reply_markup=keyboard)
    await state.set_state(QuizCreation.waiting_for_image)
    await callback.answer()

# Обработка "Пропустить изображение"
@router.callback_query(F.data == "skip_image", QuizCreation.waiting_for_image)
async def handle_skip_image(callback: CallbackQuery, state: FSMContext):
    await state.update_data(photo_id=None)
    await callback.message.answer("Изображение пропущено. Дальше — текст вопроса (будет следующим этапом).")
    await callback.answer()
    # здесь мы можем перейти к следующему шагу FSM

# Обработка отправленного фото
@router.message(QuizCreation.waiting_for_image, F.photo)
async def handle_uploaded_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(photo_id=photo.file_id)
    await message.answer("Изображение сохранено! Дальше — текст вопроса (будет следующим этапом).")
    # здесь мы можем перейти к следующему шагу FSM

# Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())