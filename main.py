import config
import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, F
#from aiogram.client.session.aiohttp import AiohttpSession#для хостинга
from aiohttp_socks import ProxyConnector

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, InputMediaPhoto
from base import SQL  # подключение класса SQL из файла base

db = SQL('db.db')  # соединение с БД
#session = AiohttpSession(proxy='http://proxy.server:3128') # в proxy указан прокси сервер pythonanywhere, он нужен для подключения
bot = Bot(token=config.TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
if not os.path.exists("images"):
    os.makedirs("images")

#inline клавиатура
kb_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Активные пользователи", callback_data="act")],
    [InlineKeyboardButton(text="Библиотека рецептов", callback_data="bibl")],
    [InlineKeyboardButton(text="Комментарии", callback_data="komm")],
    [InlineKeyboardButton(text="Добавить рецепт", callback_data="add_rec")],
    [InlineKeyboardButton(text="Импорт с сайта", callback_data="import_recipe")]
])
buttons2 = [
        [InlineKeyboardButton(text="Узнать новый рецепт", callback_data="new")],
        [InlineKeyboardButton(text="Мои рецепты", callback_data="my rec")],
        [InlineKeyboardButton(text="Добавить рецепт", callback_data="add")]
    ]
kb2 = InlineKeyboardMarkup(inline_keyboard=buttons2)

#статусы пользователя
# 0 - новый пользователь
# 1 -
# 2 -
# 3 -
# 4 -
# 5 - введи название рецепта
# 6 - введи основные шаги
# 7 - отправь фото

#статусы заказа
# 0 - в корзине
# 1 - заказан
#временные переменные для добавления товара
name_rec=''
step_rec=''
ingred_rec=''


@dp.message(F.photo)
async def photo_handler(message):
    global step_rec, name_rec, ingred_rec
    user_id = message.from_user.id
    status = db.get_field("users", user_id, "status")
    if status == 8:
        # Добавляем рецепт со статусом 1 (сразу одобрен)
        db.add_rec(name_rec, step_rec, ingred_rec, 1)
        rec_id = db.get_recept_id(name_rec)

        # Сохраняем фото
        await bot.download(message.photo[-1], destination=f"images/{rec_id}.png")

        # Автоматически добавляем рецепт в избранное пользователя
        db.add_my_rec(user_id, rec_id)

        await message.answer("Рецепт успешно добавлен и сохранен в ваши рецепты!")
        db.update_field("users", user_id, "status", 1)

#когда пользователь написал сообщение
@dp.message()
async def start(message):
    global step_rec, name_rec, ingred_rec
    user_id = message.from_user.id
    if not db.user_exist(user_id):#если пользователя нет в бд
        db.add_user(user_id)#добавляем
    status = db.get_field("users", user_id, "status")# получаем статус пользователя
    if status==0:
        await message.answer(f'Прежде чем начнем, введите свое имя:')
        s = message.text
        db.update_field('users', user_id, 'name', s)
        db.update_field("users", user_id, "status", 0.5) #изменяем статус пользователя
    elif status == 0.5:
        name = message.text
        db.update_field('users', user_id, 'name', name)
        db.update_field("users", user_id, "status", 1)
        await message.answer("Давайте начнем?", reply_markup=kb2)

        # Здесь проверка на админа
        if db.get_field("users", user_id, "admin") == 1:
            await message.answer("Панель администратора", reply_markup=kb_admin)

    elif status == 1:
        await message.answer("Выберите действие:", reply_markup=kb2)
        if db.get_field("users", user_id, "admin") == 1:
            await message.answer("Панель администратора", reply_markup=kb_admin)
    if status == 5:
        name_rec = message.text
        db.update_field("users", user_id, "status", 6)
        await message.answer("Напишите свой рецепт, постарайтесь максимально передать суть. Мы отправим его на рассмотрение администраторам.")

    if status == 6:
        ingred_rec = message.text
        db.update_field("users", user_id, "status", 7)
        await message.answer("Теперь напишите ингредиенты своего рецепта.")
    if status == 7:
        step_rec= message.text
        await message.answer("Отправьте фото вашего блюда!")
        db.update_field("users", user_id, "status", 8)
    if status==8:
        db.update_field("users", user_id, "status", 1)
        recipe_id=db.get_recept_id(name_rec)
        db.add_my_rec(user_id, recipe_id)


#когда пользователь нажал на inline кнопку
@dp.callback_query()
async def start_call(call):
    user_id = call.from_user.id
    if not db.user_exist(user_id):#если пользователя нет в бд
        db.add_user(user_id)
    if call.data == 'add':
        await call.answer("Введите название рецепта")
        db.update_field("users", user_id, "status", 5)
    elif call.data == "my rec":
        # Получаем рецепты пользователя из favourite_recipe
        query = """
              SELECT r.id, r.name, r.rec, r.spisok 
              FROM recept r 
              JOIN favourite_recipe f ON r.id = f.recipe_id 
              WHERE f.user_id = ?
          """
        with db.connection:
            recipes = db.cursor.execute(query, (user_id,)).fetchall()

        if not recipes:
            await call.answer("У вас пока нет сохраненных рецептов!")
            return

        await call.message.answer("Ваши рецепты:")
        for recipe in recipes:
            recipe_id, name, rec, spisok = recipe
            photo_path = None
            for ext in ['.png', '.jpg', '.jpeg']:
                if os.path.exists(f"images/{recipe_id}{ext}"):
                    photo_path = f"images/{recipe_id}{ext}"
                    break

            if photo_path:
                try:
                    image = FSInputFile(photo_path)
                    await bot.send_photo(call.message.chat.id, image)
                except:
                    await call.message.answer("Фото не загрузилось")
            else:
                await call.message.answer("(фото отсутствует)")

            # Кнопки для рецепта
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Посмотреть рецепт", callback_data=f"view_{recipe_id}")],
                [InlineKeyboardButton(text="Удалить из моих", callback_data=f"delete_{recipe_id}")]
            ])

            await call.message.answer(
                f"Название: {name}\n\nОписание: {rec}\n\nИнгредиенты: {spisok}",
                reply_markup=kb
            )
    elif call.data == "new":
            # Получаем случайный рецепт из базы
        query = "SELECT id, name, rec, spisok FROM recept WHERE status = 1 ORDER BY RANDOM() LIMIT 1"
        with db.connection:
            recipe = db.cursor.execute(query).fetchone()

        if recipe:
            recipe_id, name, rec, spisok = recipe

                # Пытаемся отправить фото
            try:
                    # Проверяем разные расширения файла
                photo_path = None
                for ext in ['.png', '.jpg', '.jpeg']:
                    if os.path.exists(f"images/{recipe_id}{ext}"):
                        photo_path = f"images/{recipe_id}{ext}"
                        break

                if photo_path:
                    image = FSInputFile(photo_path)
                    await bot.send_photo(call.message.chat.id, image)
                else:
                    await call.message.answer("(фото не найдено)")
            except:
                await call.message.answer("(фото не загрузилось)")

                # Кнопки для этого рецепта
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Сохранить в мои рецепты", callback_data=f"save_{recipe_id}")],
                [InlineKeyboardButton(text="Другой рецепт", callback_data="new")]
            ])

            await call.message.answer(
                f"🍽 {name}\n\n📝 {rec}\n\n🥄 Ингредиенты:\n{spisok}",
                reply_markup=kb
            )
        else:
            await call.message.answer("Рецепты пока не добавлены")

        await call.answer()
    elif call.data.startswith("save_"):
        recipe_id = int(call.data.split("_")[1])
        user_id = call.from_user.id

        # Проверяем, не сохранен ли уже рецепт
        check_query = "SELECT * FROM favourite_recipe WHERE user_id = ? AND recipe_id = ?"
        with db.connection:
            existing = db.cursor.execute(check_query, (user_id, recipe_id)).fetchone()

        if existing:
            await call.answer("Этот рецепт уже у вас в сохраненных!")
        else:
            db.add_my_rec(user_id, recipe_id)
            await call.answer("Рецепт сохранен в ваши рецепты!")
    await bot.answer_callback_query(call.id)

'''Поменять верхнюю функцию'''
        #добавляем
    #if call.data == "yes": проверка нажатия на кнопку
    #await call.answer("Оповещение сверху")
    #await call.message.answer("Отправка сообщения")
    #await call.message.edit_text("Редактирование сообщения")
    #await call.message.delete()#удаление сообщения
                      #ответ на запрос, чтобы бот не зависал

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
