from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
import json
from keyboards.help_req_menu import help_req_kb, type_btn
from states.add_credit_states import Credit
from states.help_request_states import Request
from config import BOT_TOKEN
import db
from keyboards.main_menu import level_0_kb, level_1_kb


bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# /start
@dp.message_handler(commands='start', state="*")
async def say_hi(message: types.Message, state: FSMContext):
    await state.finish()
    record_user = db.get_user(message.from_user.username)
    if record_user is None:
        db.create_user(message.from_user.username)
        await bot.send_message(chat_id=message.from_user.id, reply_markup=level_0_kb,
                            text="Привет, тебе доступны следующие функции: ")
        return
    await bot.send_message(chat_id=message.from_user.id, reply_markup=level_0_kb,
                            text=f"Привет, {message.from_user.username}! Тебе доступны следующие функции: ")


# /menu
@dp.message_handler(commands='menu', state="*")
async def call_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(chat_id=message.from_user.id, reply_markup=level_0_kb,
                               text="Привет! Это мое главное меню: ")


# lvl 1 menu
@dp.callback_query_handler(lambda c: c.data == 'credit')
async def add_credit(call: types.CallbackQuery):
    await call.message.edit_text("Работа с кредитами", reply_markup=level_1_kb)
    await call.answer()


# back to lvl 0
@dp.callback_query_handler(lambda c: c.data == 'to_lvl_0')
async def go_back(call: types.CallbackQuery):
    await call.message.edit_text(f"Привет! Это мое главное меню: ", reply_markup=level_0_kb)
    await call.answer()


# add credit
@dp.callback_query_handler(lambda c: c.data == 'add_credit')
async def get_new_credit(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, "Для добавления нового кредита " 
                                              "необходимо ввести наименование банка")
    await call.answer()
    await Credit.Bank_name.set()


# get bankname
@dp.message_handler(state=Credit.Bank_name)
async def get_bank_name(message: types.Message, state: FSMContext):
    await state.update_data(bank_name=message.text.lower())
    await bot.send_message(message.from_user.id, "Хорошо, на какую сумму кредит?")
    await Credit.next()


# get credit summ
@dp.message_handler(state=Credit.Summ)
async def get_summ_credit(message: types.Message, state: FSMContext):
    try:
        summ = float(message.text.replace(',', '.'))
        if summ <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        await message.answer(f"Необходимо ввести целое либо дробное число")
    else:
        await state.update_data(summ=summ)
        credit_data = await state.get_data()
        owner_info = db.get_user(message.from_user.username)
        record_credit = db.get_credit(owner_info[0], credit_data['bank_name'])
        if record_credit is None:
            db.create_credit(owner_info[0], credit_data['bank_name'], credit_data['summ'])
            await bot.send_message(message.from_user.id, f"Кредит в банке {credit_data['bank_name'].upper()} "
                                                         f"на сумму {round(credit_data['summ'], 3)} успешно добавлен!")
            await state.finish()
            return
        db.update_credit(owner_info[0], credit_data['summ'], credit_data['bank_name'])
        updated_record_credit = db.get_credit(owner_info[0], credit_data['bank_name'])
        await bot.send_message(message.from_user.id, f"Кредит успешно добавлен! \n" 
                                                     f" Общая задолженность в банк {credit_data['bank_name'].upper()} "
                                                     f"составляет: {updated_record_credit[3]} ")
        await state.finish()
# end create credit


# full_credit_info n credit package in percent
@dp.callback_query_handler(lambda c: c.data == 'calculate')
async def get_full_credit_info(call: types.CallbackQuery):
    owner_info = db.get_user(call.from_user.username)
    full_info = db.info_credit(owner_info[0])
    summ_all_credit = db.summ_credit(owner_info[0])
    message_to_user = ""
    if not full_info:
        await bot.send_message(call.from_user.id, 'На твое имя не найдено кредитов, но ты можешь'
                                                  ' добавить их в разделе "Работа с кредитами", '
                                                  'вызвав команду /menu.')
        return
    for info in full_info:
        proc = round(info[1] / summ_all_credit[0] * 100, 3)
        cute_border = "_____________________________________"
        message_to_user += f"Банк: {info[0].upper()} \n Сумма задолженности: {round(info[1], 3)} \n " \
                           f"Процентное соотношение: {proc} % \n {cute_border} \n"
    await bot.send_message(call.from_user.id, message_to_user)
    await call.answer()


# help requests
@dp.callback_query_handler(lambda c: c.data == 'request')
async def get_help_request(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, "Для отправки запроса необходимо заполнить некоторые данные о нем. \n"
                                              "Выбери, к какому типу относится твой запрос: ", reply_markup=help_req_kb)
    await call.answer()
    await Request.Type.set()


# get type request
@dp.message_handler(state=Request.Type)
async def get_type_request(message: types.Message, state: FSMContext):
    if message.text not in type_btn:
        await message.answer("Необходимо выбрать тип проблемы, используя клавиатуру ниже.")
        return
    await state.update_data(type_request=message.text.lower())
    await Request.next()
    await bot.send_message(message.from_user.id, "Хорошо! Опиши проблему детальнее", reply_markup=types.ReplyKeyboardRemove())


# get desc request
@dp.message_handler(state=Request.Description)
async def get_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.lower())
    await Request.next()
    await bot.send_message(message.from_user.id, "Прикрепи скриншот/фотографию проблемы. \n"
                                                 "Для загрузки доступны файлы с расширениями: .png и .jpg")


# request attachments
@dp.message_handler(content_types=["photo", "text"], state=Request.Attachments)
async def get_attachments(message: types.Message, state: FSMContext):
    if message.text:
        await bot.send_message(message.from_user.id, "Необходимо загрузить картинку")
        return
    owner_info = db.get_user(message.from_user.username)
    request_data = await state.get_data()
    attach_type = request_data['type_request']
    id_photo = message.photo[-1].file_id
    db.create_request(owner_info[0], attach_type, request_data['description'], id_photo)
    await state.finish()
    await bot.send_message(message.from_user.id, "Спасибо! Твой запрос отправлен")

# save picture in dir
    record_request = db.get_request(owner_info[0], attach_type, request_data['description'])
    path_to_attach = 'req_attachments/' + str(record_request[0]) + '_' + message.photo[-1].file_unique_id + '.jpg'
    await message.photo[-1].download(path_to_attach)

# create json-file
    req_data = {'request': {'owner': owner_info[1], 'type': attach_type, 'desc': request_data['description'],
                            'attach': path_to_attach}}
    jsonstr = json.dumps(req_data, indent=2)
    json_file = open("help_requests/" + str(record_request[0]) + "req_data.json", "w")
    json_file.write(jsonstr)
    json_file.close()

if __name__ == "__main__":
    executor.start_polling(dp)
# end!
