import asyncio
import logging
import random
import threading
from os import getenv
from dotenv import load_dotenv

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api import VkApi
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery

# Инициализируем логгер
logger = logging.getLogger(__name__)
# Конфигурируем логирование
logging.basicConfig(
    level=logging.INFO,
    format='[{asctime}] #{levelname:8} {filename}:{lineno} - {name} - "{message}"',
    style='{')

load_dotenv()

# Настройки VK API
VK_TOKEN = getenv('VK_TOKEN')
GROUP_ID = getenv('VK_GROUP_ID')
vk_session = VkApi(token=VK_TOKEN)
longpoll = VkBotLongPoll(vk_session, GROUP_ID)
vk_api = vk_session.get_api()

# Настройки Aiogram
TG_TOKEN = getenv('TG_TOKEN')
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()



# Ответ на сообщения
COMMON_RESPONSE = ("Бот временно не работает, так как полное расписание ещё не опубликовано на сайте(https://cchgeu.ru/studentu/schedule).\n"
                   "Мы ждём обновления данных и сразу восстановим работу, как только информация появится.\n"
                   "Спасибо за понимание! 😊")

### VK BOT ###

def vk_bot():
    logger.info("VK Bot started")
    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
                    logger.info('New_message_VK')
                    user_id = event.message["peer_id"]
                    vk_api.messages.send(
                        peer_id=user_id,
                        random_id=random.randint(1,99999),
                        message=COMMON_RESPONSE,
                    )
                # обрабатываем клики по callback кнопкам
                elif event.type == VkBotEventType.MESSAGE_EVENT:
                    logger.info('New_callback_VK')
                    # id пользователя
                    user_id = event.object.user_id
                    vk_api.messages.send(
                        peer_id=user_id,
                        random_id=random.randint(1, 99999),
                        message=COMMON_RESPONSE,
                    )
        except Exception as e:
            logger.error(f'Ошибка vk_bot: {e}')

### TELEGRAM BOT ###

@dp.message()
async def wtf_send(message: Message):
    await message.answer(COMMON_RESPONSE)

@dp.callback_query()
async def wtf_send(callback: CallbackQuery, bot: Bot):
    await bot.send_message(callback.from_user.id, COMMON_RESPONSE)

async def tg_bot():
    logger.info("Telegram Bot started")
    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot, )

### ЗАПУСК ###
# async def main():
#     # # Запускаем оба бота параллельно
#     # await asyncio.gather(
#     #     vk_bot(),
#     #     tg_bot()
#     # )
#     # Поток для VK API
#     vk_thread = threading.Thread(target=vk_bot)
#     vk_thread.start()
#
#     # Основной поток для Telegram-бота
#     asyncio.run(tg_bot())
#
# Асинхронный запуск синхронного кода
async def run_vk_bot():
    await asyncio.to_thread(vk_bot)

# Основная функция
async def main():
    # Запуск VK и Telegram-ботов одновременно
    await asyncio.gather(
        run_vk_bot(),
        tg_bot()
    )


if __name__ == "__main__":
    asyncio.run(main())