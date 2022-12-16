import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardMarkup,KeyboardButton
from mysql import *


API_TOKEN='5947520458:AAF1hmQmvxRoIaFd1kXaVVAG9eNKg41g05s'
logging.basicConfig(level=logging.INFO)
bot=Bot(token=API_TOKEN)
dp=Dispatcher(bot=bot,storage=MemoryStorage())
db= Database("database.db")

class Mahalla(StatesGroup):
    nomi = State()
    uzunlik = State() # longitude
    kenglik = State() # latitude
    rais = State()
    xojaliklar_soni = State()


@dp.message_handler(commands='start')
async def start(mess:types.Message):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    menu = KeyboardButton(text="Menyu")
    markup.add(menu)
    await mess.answer(f"Salom,{mess.from_user.full_name}",reply_markup=markup)

@dp.message_handler(text="Menyu")
async def help(mess:types.Message):
    markup = InlineKeyboardMarkup(row_width=2)
    qoshish = InlineKeyboardButton(text="O'z mahallamni qo'shish",callback_data="qoshish")
    royxat = InlineKeyboardButton(text="Mahallalar ro'yxati",callback_data="list")
    markup.add(qoshish).add(royxat)

    await mess.answer("Quyidagilardan birini tanlang",reply_markup=markup)

@dp.callback_query_handler(text="list")
async def list(call:types.CallbackQuery):
    result = db.mahallalar_royxati()
    await call.message.answer(result)

@dp.callback_query_handler(text = "qoshish", state=None)
async def qoshish(call:types.CallbackQuery):
    await call.message.answer("Mahalla nomini kiriting")
    await  Mahalla.nomi.set()

@dp.message_handler(state=Mahalla.nomi)
async def mahalla_nomi(mess:types.Message,state:FSMContext):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    location = KeyboardButton(text="Joylashuv ulashish",request_location=True)
    markup.add(location)
    await state.update_data({"nomi":mess.text})
    await Mahalla.next()
    await mess.answer("Mahllangiz joylashuvini kiritish uchun joylashuvingizni kiriting",reply_markup=markup)

@dp.message_handler(content_types="location",state=Mahalla.kenglik and Mahalla.uzunlik)
async def location(mess:types.Message,state:FSMContext):
    markup  = ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    cancel= KeyboardButton(text="Bekor qilish")
    markup.add(cancel)
    await state.update_data({"uzunlik":mess.location.longitude,"kenglik":mess.location.latitude})
    await Mahalla.rais.set()
    await mess.answer("Mahlla raisi ism familiyasini kiriting",reply_markup=markup)
    markup2 = InlineKeyboardMarkup(row_width=2)
    qoshish = InlineKeyboardButton(text="O'z mahallamni qo'shish",callback_data="qoshish")
    royxat = InlineKeyboardButton(text="Mahallalar ro'yxati",callback_data="list")
    markup2.add(qoshish).add(royxat)

    if mess.text=="Bekor qilish":
        await state.finish()
        await mess.answer("Ro'yxatga olish tugatildi",reply_markup=markup2)

@dp.message_handler(state=Mahalla.rais)
async def mahalla_rais(mess:types.Message,state:FSMContext):
    markup  = ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    cancel= KeyboardButton(text="Bekor qilish")
    markup.add(cancel)
    await state.update_data({"rais":mess.text})
    await mess.answer("Mahalladagi xo'jaliklar sonini kiriting",reply_markup=markup)
    await Mahalla.next()
    markup2 = InlineKeyboardMarkup(row_width=2)
    qoshish = InlineKeyboardButton(text="O'z mahallamni qo'shish",callback_data="qoshish")
    royxat = InlineKeyboardButton(text="Mahallalar ro'yxati",callback_data="list")
    markup2.add(qoshish).add(royxat)

    if mess.text=="Bekor qilish":
        await state.finish()
        await mess.answer("Ro'yxatga olish tugatildi",reply_markup=markup2)

@dp.message_handler(state=Mahalla.xojaliklar_soni)
async def xojalilar_soni(mess:types.Message,state:FSMContext):
    markup  = ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    cancel= KeyboardButton(text="Bekor qilish")
    markup.add(cancel)
    if mess.text.isdigit():
        await state.update_data({"xojaliklar_soni":mess.text})
        
        data = await state.get_data()
        db.mahalla_kiritish(nomi=data['nomi'],kenglik=data['kenglik'],uzunlik=data['uzunlik'],rais=data['rais'],xojaliklar_soni=data['xojaliklar_soni'])        
        await mess.answer(f"Mahalla nomi:{data['nomi']}\nShimoliy uzunlik:{data['uzunlik']}\nShimoliy kenglik:{data['kenglik']}\nMahalla raisi:{data['rais']}\nMahalladagi xo'jaliklar soni:{data['xojaliklar_soni']}")
        await state.finish()

    else:
        await mess.answer("Son yuboring",reply_markup=markup)

if __name__=='__main__':
    executor.start_polling(dp,skip_updates=True)