from aiogram import Bot, types, Dispatcher, executor
from aiogram.types.chat_permissions import ChatPermissions

from aiogram.dispatcher.webhook import PromoteChatMember

from PIL import Image, ImageDraw

import logging
import filters
import config, asyncio, json
from mines import MineGame

ADMINS_B = [1627807288]
PROMOTE_A = [1627807288]
from filters import IsAdminFilter

bot = Bot(token = config.TOKEN)
dp  = Dispatcher(bot)

game = None
gamerid = 0

async def get_keyboard():
	keyboard = types.InlineKeyboardMarkup(row_width=5)
	for y in range(5):
		markup = []
		
		for x in range(5):
			idx = y * 5 + x
			
			markup.append(types.InlineKeyboardButton(str(idx+1), callback_data=str(idx)))
		keyboard.add(markup[0], markup[1], markup[2], markup[3], markup[4])
	return keyboard

async def send_game(message, over, edit):
	global game
	ph = False
	if over == 1:
		ph = False
	else:
		ph = True
	
	game.get_map_image(over)
	photo = types.InputFile("map.png")
	
	text = "[💎] Hollywood Mines"
	reply_markup = None
	if over == 1:
		text = f"Ты проиграл"
		game = None
	elif over == 0:
		reply_markup = await get_keyboard()
		text = f"Game ID: {game.gameid}\n" \
				 f"Количество мин: {game.mines_count}\n" \
			    f"Коэффицент: {config.coefs[game.mines_count][len(game.opens)]}x\n" \
		  	  f"Ставка: {game.bet}₽\n - Выигрыш: {round(config.coefs[game.mines_count][len(game.opens)] * game.bet, 2)}₽"
	elif over == 2:
		text = f"Ты забрал {round(config.coefs[game.mines_count][len(game.opens)] * game.bet, 2)}"
		game = None
	if edit:
		media = types.InputMedia(media=photo, caption=text)
		try:
			await bot.edit_message_media(
				chat_id=message.chat.id,
				message_id=message.message_id,
				media=media,
				reply_markup=reply_markup
			)
		except Exception as er: print(er)
	else:
		await bot.send_photo(
			chat_id=message.chat.id,
			photo=photo,
			caption=text,
			reply_markup=reply_markup
		)

async def open_ceil(message: types.Message, idx):
	global podkrut
	if game is not None:
		if idx not in game.opens:
			if idx not in game.mines:
				game.opens.append(idx)
				await send_game(message, False, True)
			else:
				await send_game(message, True, True)
	else:
		await message.answer("Игра не найдена")
		
dp.filters_factory.bind(IsAdminFilter)

@dp.message_handler(commands=["ban"], user_id=ADMINS_B)
async def cmd_ban(message: types.Message):
	if not message.reply_to_message:
		await message.reply("Эта команда должна быть ответом на сообщение!")
		return
	
	await message.bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
	
	await message.reply_to_message.reply("User was banned!")
	
@dp.message_handler( commands=["unban"], user_id=ADMINS_B)
async def cmd_unban(message: types.Message):
	if not message.reply_to_message:
		await message.reply("Эта команда должна быть ответом на сообщение!")
		return
	
	await message.bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
	
	await message.reply_to_message.reply("User was unbanned!")
	
@dp.message_handler(commands=["mute"], user_id=ADMINS_B)
async def cmd_ban(message: types.Message):
	if not message.reply_to_message:
		await message.reply("Эта команда должна быть ответом на сообщение!")
		return
	
	await message.bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id)
	
	await message.reply_to_message.reply("User was mutted!")
	
@dp.message_handler(commands=["unmute"], user_id=ADMINS_B)
async def cmd_ban(message: types.Message):
	if not message.reply_to_message:
		await message.reply("Эта команда должна быть ответом на сообщение!")
		return
		
	await message.bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, ChatPermissions(can_send_messages=True,
can_send_media_messages=True,
can_invite_users=True))

	await message.reply_to_message.reply("unmutted!")
	
@dp.message_handler(commands=["promote"], user_id=PROMOTE_A)
async def cmd_ban(message: types.Message):
	if not message.reply_to_message:
		await message.reply("Эта команда должна быть ответом на сообщение!")
		return
		
	await message.reply_to_message.reply("Promoted!")
	
@dp.message_handler(commands=["gamer"])
async def set_gamer(message: types.Message):
	global gamerid
	if message.from_user.id in config.ADMINS:
		gamerid = message.reply_to_message.from_user.id
		await message.answer("Игрок установлен")

@dp.message_handler(commands=["stop"])
async def stopgame(message: types.Message):
	if message.from_user.id in config.ADMINS:
		await send_game(message, 2, False)

@dp.message_handler(commands=["game"])
async def create_game(message: types.Message):
	global game
	if message.from_user.id in config.ADMINS:
		args = message.get_args().split()
		game = None
		game = MineGame(int(args[0]), int(args[1]))
	
		await message.answer(f"Game ID: {game.gameid}\nMD5: " + game.gethash())
		await send_game(message, False, False)
		
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
		await message.answer("Mines By @drenix_x.\nДля продолжения вам необходима админка.")
		
@dp.message_handler(commands=["help"])
async def help(message: types.Message):
	global help
	if message.from_user.id in config.ADMINS:
		await message.answer("/game; /stop; /gamer")
		
@dp.message_handler(commands=["how"])
async def how(message: types.Message):
		await message.answer("После того, как вы отправили деньги на депозит пишите ставку и сумму, на которую хотите сыграть. Администратор создаёт вам игру.\n\nНапимер: ставлю 30₽ на 2 мины. Это означает, что ваша ставка = 30 рублей, а количество мин на поле = 2 мины.\n\nВы должны угадывать клетки, в которых нет мин.\n\nЕсли вы хотите забрать, просто напишите: забираю. Администратор остановит игру.\n\nВы должны запомнить свой баланс, чтобы в дальнейшем знать, сколько у вас денег.\n\nЕсли вы хотите вывести заработанные деньги, напишите 1 из администраторов свой киви кошелек и сумму вывода.")
	
@dp.callback_query_handler()
async def callback(call: types.CallbackQuery):
	if call.from_user.id in config.ADMINS or call.from_user.id == gamerid:
		await open_ceil(call.message, int(call.data))
		
if __name__ == "__main__":
	print("[ + ] Бот запущен")
	executor.start_polling(dp)
