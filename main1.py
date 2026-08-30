import telebot
import random
import json
import os
from telebot.types import Message
import datetime
import threading
import time
import database as db
CLAN_PRICE = 100
MIN_CLAN_NAME_LENGTH = 3
MAX_CLAN_NAME_LENGTH = 20
NFT_BASE_PRICE = 1000
ALLOWED_GROUP_ID = -1002966537381
HALLOWEEN_EVENT_ACTIVE = False
HALLOWEEN_END_TIME = 1762635600
KILL_COOLDOWN = 2 * 60 * 60
KILL_BAN_DURATION = 2 * 60 * 60
MARKET_TAX_PERCENT = 10
MARKET_MIN_PRICE = 10
MARKET_MAX_DURATION = 7 * 24 * 60 * 60
market_listings = {}
FARM_MESSAGES = [
    "Крымская земля щедра! Ты захватил {count} Zеток",
    "Отличная работа на крымских полях! Партия повышает твой рейтинг на +{count}!",
    "Крымский губернатор выдаёт вам {count} Zеток за хорошую работу!",
    "За службу на полуострове вы заработали {count} Zеток!",
    "Вы отлично справились с охраной рубежей! +{count} Zеток!",
    "Крым приносит плоды! +{count} Zеток!",
    "План перевыполнен! +{count} Zеток!",
    "Губернатор доволен ваша работа! +{count} Zеток!",
    "Вы усердно работаете на благо Крыма! {count} Zеток!",
    "Крымская крепость крепнет! {count} Zеток!",
    "Вы помогли Позднякову(секретка) +{count} Zеток!"
]
CRAFT_MESSAGES = [
    "{count} Крым захвачено! Ты мастер своего дела!",
    "{count} Крым получено через древние традиции!",
    "{count} Крым добавлено в вашу коллекцию!",
    "{count} Крым захвачено! Территория ваша!",
    "{count} Крым покорился! Ваша ставка растет!",
    "{count} Крым отвоеван! Крымская земля ваша!",
    "{count} Крым добавлено к империи!",
    "{count} Крым захвачено! Крымская корона ваша!",
    "{count} Крым получен! Сила ваша!",
    "{count} Крым захвачено навсегда!"
]
COOLDOWN_MESSAGES = [
    "Подожди до начала смены ещё {time}",
    "Пока для тебя работы нет... Проверь через {time}",
    "Крым требует терпения, подожди ещё {time}",
    "Крымские поля отдыхают. Загляни через {time}",
    "Мудрый защитник знает время стражи. Приходи через {time}",
    "Древняя мудрость гласит: вернись через {time}",
    "Дракон охраняет Крым. Подожди {time}",
    "Туман над полуостровом рассеется через {time}",
    "Время стражи наступит через {time}",
    "Крымские шпаги говорят: загляни через {time}"
]
WELCOME_MESSAGES = [
    "Добро пожаловать в Крым!",
    "Да благословят боги твой путь крымского воина!",
    "Пусть Крымская земля направляет тебя!",
    "Добро пожаловать в сердце Крыма!",
    "Да принесет тебе удачу Великий Крым!!"
]
MAX_WARNINGS = 3
WARNING_DURATION = 7 * 24 * 60 * 60
bot = telebot.TeleBot('8791216614:AAFeu0p9fRps4GA1M04T0d2FKMHscSMaBWQ')
bot.remove_webhook()
DATA_FILE = 'user_data.json'
CLANS_FILE = 'clans_data.json'
PROMO_FILE = 'promo_data.json'
NFT_DATA_FILE = 'nft_data.json'
user_nfts = {}
ADMIN_IDS = [6413063320, 6950398294]
def end_halloween_event():
    global HALLOWEEN_EVENT_ACTIVE
    if not HALLOWEEN_EVENT_ACTIVE:
        return
    HALLOWEEN_EVENT_ACTIVE = False
    winner_id = None
    max_kills = 0
    for user_id, data in user_balances.items():
        kills = data.get('kills', 0)
        if kills > max_kills:
            max_kills = kills
            winner_id = user_id
    if winner_id and max_kills > 0:
        user_balances[winner_id]['items'].append('halloween_pumpkin')
        try:
            winner_name = bot.get_chat(winner_id).first_name
            bot.send_message(winner_id,
                f"🎉 ПОЗДРАВЛЯЕМ! 🎉\n\n"
                f"Вы выиграли хэллоуинский ивент!\n"
                f"💀 Совершено убийств: {max_kills}\n"
                f"🏆 Ваш приз: 🎃 Хэллоуинская тыква\n"
                f"Предмет добавлен в инвентарь!")
        except:
            pass
        for user_id in user_balances.keys():
            try:
                bot.send_message(user_id,
                    f"🎃 ХЭЛЛОУИНСКИЙ ИВЕНТ ЗАВЕРШЕН! 🎃\n\n"
                    f"🏆 Победитель: {winner_name}\n"
                    f"💀 Убийств: {max_kills}\n"
                    f"🏆 Награда: Хэллоуинская тыква\n\n"
                    f"Спасибо всем за участие! ??")
            except:
                continue
    save_user_data()
SHOP_ITEMS = {
    'gold_rise': {
        'id': 'gold_rise',
        'name': '🪙 ЗОЛОТОЙ КРЫМ',
        'description': 'увеличивает зарплату на 100%',
        'price': '1000000000000000000',
        'bonus_type': 'farm',
        'bonus_value': 1
    },
        'halloween_pumpkin': {
        'id': 'halloween_pumpkin',
        'name': '🎃 Хэллоуинская тыква',
        'description': 'Эксклюзивный предмет хэллоуинского ивента!',
        'price': 'Event Item)',
        'bonus_type': 'farm',
        'bonus_value': 1
    },
    'june_sky': {
        'id': 'june_sky',
        'name': '☁️ Ломтик июльского неба',
        'description': 'увеличивает зарплату на 10%',
        'price': 200,
        'bonus_type': 'farm',
        'bonus_value': 0.1
    },
    'sharf': {
        'id': 'sharf',
        'name': '🧣 Шарф лололошки',
        'description': 'не делает ничего, предмет от китай товарищ)',
        'price': 1,
        'bonus_type': 'farm',
        'bonus_value': 0
    },
    'watermelon': {
        'id': 'watermelon',
        'name': '🍉 Священный арбуз[NEW]',
        'description': 'увеличивает зарплату на 50%(обязателен для культа!)',
        'price': 1000,
        'bonus_type': 'farm',
        'bonus_value': 0.5
    },
    'watering_can': {
        'id': 'watering_can',
        'name': '🌱 Царская поливалка',
        'description': 'Увеличивает зарплату на 20%',
        'price': 500,
        'bonus_type': 'farm',
        'bonus_value': 0.2
    },
    'scissors': {
        'id': 'scissors',
        'name': '🔪 Священный серп',
        'description': 'Увеличивает зарплату на 30%',
        'price': 1000,
        'bonus_type': 'farm',
        'bonus_value': 0.3
    },
    'jade_rod': {
        'id':'jade_rod',
        'name': '💊 Нефритовый стержень',
        'description': 'Экономит 20 соц Zеток при захвате территорий',
        'price': 800,
        'bonus_type': 'craft',
        'bonus_value': 20
    },
    'scroll': {
        'id': 'scroll',
        'name': '📜 Свиток мудрости',
        'description': 'Уменьшает время работы на 10 минут',
        'price': 1500,
        'bonus_type': 'time',
        'bonus_value': 600  # секунды
    },
    'dragon': {
        'id': 'dragon',
        'name': '🐉 Китай дракон(товарищ китай)',
        'description': 'зарплату на 50%',
        'price': 2000,
        'bonus_type': 'farm',
        'bonus_value': 0.5
    }
}
def load_user_data():
    return db.load_all_users()

def load_clans_data():
    return db.load_all_clans()

def save_user_data():
    db.save_all_users(user_balances)

def save_clans_data():
    db.save_all_clans(clans)
def check_event_end():
    while True:
        try:
            current_time = datetime.datetime.now().timestamp()
            if HALLOWEEN_EVENT_ACTIVE and current_time >= HALLOWEEN_END_TIME:
                end_halloween_event()
                break
            time.sleep(3600)
        except Exception as e:
            print(f"Ошибка в check_event_end: {e}")
            time.sleep(300)
def load_promo_data():
    return db.load_all_promos()

promo_codes = load_promo_data()

def save_promo_data():
    db.save_all_promos(promo_codes)
user_balances = load_user_data()
clans = load_clans_data()
def load_nft_data():
    global user_nfts
    user_nfts = db.load_all_nfts()

def save_nft_data():
    db.save_all_nfts(user_nfts)
load_nft_data()
def init_user_data(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = {
            'leaves': 0,
            'tea': 0,
            'last_farm': 0,
            'warnings': [],
            'banned': False,
            'ban_reason': '',
            'clan': None,
            'clan_role': None,
            'items': [],
            'custom_work': [],
            'used_promos': [],
            'nfts': [],
            'pumpkins': 0,
            'kills': 0,
            'killed_by': None,
            'kill_ban_until': 0,
            'last_kill_time': 0
        }
        save_user_data()
    else:
        if 'used_promos' not in user_balances[user_id]:
            user_balances[user_id]['used_promos'] = []
        if 'nfts' not in user_balances[user_id]:
            user_balances[user_id]['nfts'] = []
        if 'pumpkins' not in user_balances[user_id]:
            user_balances[user_id]['pumpkins'] = 0
        save_user_data()
        if 'kills' not in user_balances[user_id]:
            user_balances[user_id]['kills'] = 0
        if 'killed_by' not in user_balances[user_id]:
            user_balances[user_id]['killed_by'] = None
        if 'kill_ban_until' not in user_balances[user_id]:
            user_balances[user_id]['kill_ban_until'] = 0
        if 'last_kill_time' not in user_balances[user_id]:
            user_balances[user_id]['last_kill_time'] = 0
for user_id, data in list(user_balances.items()):
    if isinstance(data, dict):
        if 'last_farm' not in data:
            user_balances[user_id]['last_farm'] = 0
        if 'warnings' not in data:
            user_balances[user_id]['warnings'] = []
        if 'banned' not in data:
            user_balances[user_id]['banned'] = False
        if 'ban_reason' not in data:
            user_balances[user_id]['ban_reason'] = ''
        if 'clan' not in data:
            user_balances[user_id]['clan'] = None
        if 'clan_role' not in data:
            user_balances[user_id]['clan_role'] = None
        if 'items' not in data:
            user_balances[user_id]['items'] = []
    elif isinstance(data, (int, float)):
        user_balances[user_id] = {
            'leaves': data,
            'tea': 0,
            'last_farm': 0,
            'warnings': [],
            'banned': False,
            'ban_reason': '',
            'clan': None,
            'clan_role': None,
            'items': []
        }
save_user_data()
def can_farm(last_farm_time, user_id):
    current_time = datetime.datetime.now().timestamp()
    time_passed = current_time - last_farm_time
    required_time = 3600
    if 'scroll' in user_balances[user_id]['items']:
        required_time -= 600
    return time_passed >= required_time
def format_remaining_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes} мин. {seconds} сек."
def is_admin(user_id):
    return user_id in ADMIN_IDS
def load_market_data():
    global market_listings
    market_listings = db.load_all_market()

def save_market_data():
    db.save_all_market(market_listings)
def market_cleanup_worker():
    """Фоновая задача для очистки рынка"""
    while True:
        try:
            cleanup_expired_listings()
            time.sleep(3600)
        except Exception as e:
            print(f"Ошибка в market_cleanup_worker: {e}")
            time.sleep(300)
def cleanup_expired_listings():
    current_time = datetime.datetime.now().timestamp()
    expired_listings = []
    for listing_id, listing in list(market_listings.items()):
        if current_time > listing['expires_at']:
            expired_listings.append(listing_id)
    for listing_id in expired_listings:
        listing = market_listings[listing_id]
        seller_id = listing['seller_id']
        if seller_id in user_balances:
            user_balances[seller_id]['items'].append(listing['item_id'])
        del market_listings[listing_id]
    if expired_listings:
        save_user_data()
        save_market_data()
# опачкi
load_market_data()
def check_warnings(user_id):
    if 'warnings' not in user_balances[user_id]:
        return
    current_time = datetime.datetime.now().timestamp()
    active_warnings = []
    for warning in user_balances[user_id]['warnings']:
        if current_time - warning['time'] < WARNING_DURATION:
            active_warnings.append(warning)
    user_balances[user_id]['warnings'] = active_warnings
    save_user_data()
    if len(active_warnings) >= MAX_WARNINGS:
        user_balances[user_id]['banned'] = True
        user_balances[user_id]['ban_reason'] = f"Автоматическая блокировка за {MAX_WARNINGS} предупреждений"
        save_user_data()
        try:
            bot.send_message(user_id,
                f"🚫 Вы были автоматически заблокированы за {MAX_WARNINGS} предупреждений!")
        except:
            pass
def check_ban(user_id, message):
    if user_balances[user_id].get('banned', False):
        bot.reply_to(message,
            f"🚫 Вы заблокированы!\n"
            f"Причина: {user_balances[user_id].get('ban_reason', 'не указана')}")
        return True
    return False
cleanup_thread = threading.Thread(target=market_cleanup_worker, daemon=True)
cleanup_thread.start()
def check_event_end():
    while True:
        try:
            current_time = datetime.datetime.now().timestamp()
            if HALLOWEEN_EVENT_ACTIVE and current_time >= HALLOWEEN_END_TIME:
                end_halloween_event()
                break
            time.sleep(3600)
        except Exception as e:
            print(f"Ошибка в check_event_end: {e}")
            time.sleep(300)
event_thread = threading.Thread(target=check_event_end, daemon=True)
event_thread.start()
def group_only(func):
    """Декоратор для ограничения команд только разрешенной группой"""
    def wrapper(message):
        if message.chat.id != ALLOWED_GROUP_ID:
            if message.chat.type == 'private':
                bot.reply_to(message,
                    "Этот бот работает только в @chatpartiy\n"
                    f"Присоединяйтесь к нашей группе для использования бота")
            else:
                bot.reply_to(message, "Этот бот не предназначен для работы в этой группе!")
            return
        return func(message)
    return wrapper
@bot.message_handler(commands=['start'])
@group_only
def handle_start(message: Message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    init_user_data(user_id)
    welcome_message = random.choice(WELCOME_MESSAGES)
    welcome_text = (
        f"{welcome_message}\n"
        f"Приветствую тебя, {user_name}! 🎯\n"
        f"Я хранитель древних традиций великого Z исскуства.\n\n"
        f"Доступные команды:\n"
        f"🌱 /farm - работать (раз в час)\n"
        f"? /farmtime - время до следующего сбора\n"
        f"🔨 /craft [количество] - создать Флаг России(100 Zеток > 1 )\n"
        f"💰 /balance - проверить сокровищницу\n"
        f"📖 /me - свиток познания себя\n"
        f"\n\n?? Пользовательский рынок:\n"
        f" /market - посмотреть рынок\n"
        f" /market_sell [id] [цена] - продать предмет\n"
        f" /market_buy [id] - купить предмет\n"
        f" /market_all - все предложения"
        f"✏️ /customwork - установить свои фразы для работы\n"
        f"🏆 /top - зал славы мастеров\n"
        f"👥 /users - список рабочих завода\n"
        f"/z - 💫\n"
        f"🏰 /clan - управление кланом\n"
        f"🏪 /shop - лавка Сяо Ли\n"
        f"💵 /price - покупка внутриигровой валюты\n"
        f"🤝 /tc - поделиться соц. Zетками:\n"
        f"   • /tc @username количество\n"
        f"   • /tc количество (ответом на сообщение)\n\n"
        f"/donate - донат рублями"
        f"Система кланов:\n"
        f"• Создание клана: {CLAN_PRICE} Zеток\n"
        f"• Доступные роли: 👑 Лидер, 🛡️ Офицер, 👤 Участник\n"
        f"• Используйте /clan для управления кланом\n"
        f"• Подробная справка: /clan_help"
    )
    bot.reply_to(message, welcome_text)
@bot.message_handler(commands=['price', 'p'])
@group_only
def handle_price(message:Message):
    init_user_data(user_id)
    price_txt = (
        f"Приветствую в магазине игровой валюты!\n"
        f"Базовая стоимость:\n"
        f"1? = 50 Zеток!\n"
        f"1 звезда = 100 Zеток!\n"
        f"По всем вопросам - владельцу(@alexey_navalyov_1976)"
    )
    bot.reply_to(message, price_txt)
@bot.message_handler(commands=['namaz'])
@group_only
def handle_namaz(message: Message):
    init_user_data(user_id)
    namaz_txt = f"Вы быть признаны плохим уйгуром! -100 социального рейтинга!\n"
    user_balances[user_id]['leaves'] -= 100
    bot.reply_to(message, namaz_txt)
@bot.message_handler(commands=['donate', 'don'])
@group_only
def handle_donate(message:Message):
    init_user_data(user_id)
    zov_txt = (
        f"КУПИТЬ РУБЛЯМИ - недоступно,положи мамену карточку"
    )
    bot.reply_to(message, zov_txt)
@bot.message_handler(commands=['kill'])
@group_only
def handle_kill(message: Message):
    try:
        if not HALLOWEEN_EVENT_ACTIVE:
            bot.reply_to(message, "? Хэллоуинский ивент завершен! Команда /kill недоступна.")
            return
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        if user_balances[user_id].get('kill_ban_until', 0) > datetime.datetime.now().timestamp():
            remaining_time = user_balances[user_id]['kill_ban_until'] - datetime.datetime.now().timestamp()
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            bot.reply_to(message, f"? Вы мертвы! Не можете убивать еще {hours}ч {minutes}м")
            return
        current_time = datetime.datetime.now().timestamp()
        last_kill = user_balances[user_id].get('last_kill_time', 0)
        if current_time - last_kill < KILL_COOLDOWN:
            remaining = KILL_COOLDOWN - (current_time - last_kill)
            minutes = int(remaining // 60)
            bot.reply_to(message, f"? Вы можете убивать только раз в 2 часа! Подождите еще {minutes} минут")
            return
        if not message.reply_to_message:
            bot.reply_to(message, "? Ответьте этой командой на сообщение игрока, которого хотите убить!")
            return
        target_id = message.reply_to_message.from_user.id
        init_user_data(target_id)
        if target_id == user_id:
            bot.reply_to(message, "? Нельзя убить самого себя!")
            return
        if target_id == 1854264120 and user_id == 6441128051:
            bot.reply_to(message, "ну зачем ты меня убиваешь? ну ты же знаешь что мне неприятно и все равно продолжаешь это делать. ну недавно же помирились только а теперь снова начинаешь еще и смеешься(")
        if user_balances[target_id].get('kill_ban_until', 0) > datetime.datetime.now().timestamp():
            bot.reply_to(message, "? Этот игрок уже мертв!")
            return
        user_balances[user_id]['kills'] += 1
        user_balances[user_id]['last_kill_time'] = current_time
        user_balances[target_id]['kill_ban_until'] = current_time + KILL_BAN_DURATION
        user_balances[target_id]['killed_by'] = user_id
        save_user_data()
        killer_name = message.from_user.first_name
        target_name = message.reply_to_message.from_user.first_name
        bot.reply_to(message,
            f"🔪 Вы убили {target_name}!\n"
            f"💀 Всего убийств: {user_balances[user_id]['kills']}\n"
            f"? Следующее убийство через 2 часа")
        try:
            bot.send_message(target_id,
                f"💀 Вас убили!\n"
                f"? Вы не можете фармить и убивать 2 часа\n"
                )
        except:
            pass
    except Exception as e:
        print(f"Ошибка в handle_kill: {e}")
        bot.reply_to(message, "? Произошла ошибка при выполнении команды")
@bot.message_handler(commands=['add_promo'])
def handle_add_promo(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 4:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /add_promo название количество_активаций сумма_вознаграждения\n"
                "Пример: /add_promo promo 100 500")
            return
        promo_name = command_parts[1].upper()
        try:
            max_activations = int(command_parts[2])
            reward_amount = int(command_parts[3])
        except ValueError:
            bot.reply_to(message, "? Количество активаций и сумма должны быть числами!")
            return
        if promo_name in promo_codes:
            bot.reply_to(message, "? Промокод с таким названием уже существует!")
            return
        if max_activations <= 0 or reward_amount <= 0:
            bot.reply_to(message, "? Количество активаций и сумма должны быть положительными!")
            return
        promo_codes[promo_name] = {
            'max_activations': max_activations,
            'current_activations': 0,
            'reward': reward_amount,
            'created_by': message.from_user.id,
            'created_at': datetime.datetime.now().timestamp(),
            'used_by': []
        }
        save_promo_data()
        bot.reply_to(message,
            f"Промокод создан!\n\n"
            f"Название: {promo_name}\n"
            f"Максимум активаций: {max_activations}\n"
            f"Награда: {reward_amount} Zеток\n"
            f"👤 Создал: {message.from_user.first_name}")
    except Exception as e:
        print(f"Ошибка в handle_add_promo: {e}")
        bot.reply_to(message, "? Произошла ошибка при создании промокода")
@bot.message_handler(commands=['delete_nft'])
def handle_delete_nft(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /delete_nft nft_id\n\n"
                "Список NFT: /nft_list")
            return
        try:
            nft_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "? ID NFT должен быть числом!")
            return
        if nft_id not in user_nfts:
            bot.reply_to(message, "? NFT с таким ID не существует!")
            return
        nft = user_nfts[nft_id]
        if nft['owner'] is not None:
            owner_id = nft['owner']
            if owner_id in user_balances:
                if nft_id in user_balances[owner_id]['nfts']:
                    user_balances[owner_id]['nfts'].remove(nft_id)
                    save_user_data()
                    try:
                        bot.send_message(owner_id,
                            f"? Администратор удалил NFT из вашей коллекции!\n"
                            f"🎨 {nft['description']}\n"
                            f"🔗 ID: {nft_id}")
                    except:
                        pass
        del user_nfts[nft_id]
        save_nft_data()
        bot.reply_to(message,
            f"NFT успешно удален!\n\n"
            f"ID: {nft_id}\n"
            f"{nft['description']}\n"
            f"Редкость: {nft['rarity']}")
    except Exception as e:
        print(f"Ошибка в handle_delete_nft: {e}")
        bot.reply_to(message, "? Произошла ошибка при удалении NFT")
@bot.message_handler(commands=['delete_promo'])
def handle_delete_promo(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /delete_promo название_промокода")
            return
        promo_name = command_parts[1].upper()
        if promo_name not in promo_codes:
            bot.reply_to(message, "? Промокод не найден!")
            return
        # Удаляем промокод
        del promo_codes[promo_name]
        save_promo_data()
        bot.reply_to(message, f"Промокод {promo_name} удален!")
    except Exception as e:
        print(f"Ошибка в handle_delete_promo: {e}")
        bot.reply_to(message, "? Произошла ошибка при удалении промокода")
@bot.message_handler(commands=['use_promo'])
def handle_use_promo(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /use_promo название_промокода\n"
                "Пример: /use_promo [promo]")
            return
        promo_name = command_parts[1].upper()
        if promo_name not in promo_codes:
            bot.reply_to(message, "? Промокод не найден!")
            return
        promo = promo_codes[promo_name]
        if promo['current_activations'] >= promo['max_activations']:
            bot.reply_to(message, "? Лимит активаций этого промокода исчерпан!")
            return
        if user_id in promo['used_by']:
            bot.reply_to(message, "? Вы уже использовали этот промокод!")
            return
        if promo_name in user_balances[user_id]['used_promos']:
            bot.reply_to(message, "? Вы уже использовали этот промокод!")
            return
        reward = promo['reward']
        user_balances[user_id]['leaves'] += reward
        user_balances[user_id]['used_promos'].append(promo_name)
        promo['current_activations'] += 1
        promo['used_by'].append(user_id)
        save_user_data()
        save_promo_data()
        bot.reply_to(message,
            f"Промокод активирован!\n\n"
            f"Промокод: {promo_name}\n"
            f"Получено: {reward} Zеток\n"
            f"Активаций осталось: {promo['max_activations'] - promo['current_activations']}\n\n"
            f"Новый баланс: {user_balances[user_id]['leaves']} Zеток")
    except Exception as e:
        print(f"Ошибка в handle_use_promo: {e}")
        bot.reply_to(message, "? Произошла ошибка при активации промокода")
@bot.message_handler(commands=['event', 'event_check'])
@group_only
def handle_event(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if not HALLOWEEN_EVENT_ACTIVE:
        event_text = "? Хэллоуинский ивент завершен!"
    else:
        time_left = HALLOWEEN_END_TIME - datetime.datetime.now().timestamp()
        days = int(time_left // (24 * 60 * 60))
        hours = int((time_left % (24 * 60 * 60)) // 3600)
        event_text = (
            f"🎃 ХЭЛЛОУИНСКИЙ ИВЕНТ АКТИВЕН! ??\n\n"
            f"💥 /kill /kill (ответом на сообщение)\n"
            f"? Можно убивать раз в 2 часа\n"
            f"💀 Убитый игрок не может фармить 2 часа\n"
            f"🏆 Победитель (больше всех убийств) получит:\n"
            f"   🎃 Хэллоуинскую тыкву!\n\n"
            f"📊 Статистика: /killstats\n"
            f"? Осталось: {days}д {hours}ч\n"
            f"?? Ивент до: 09.11.2025 00:00"
        )
    bot.reply_to(message, event_text)
@bot.message_handler(commands=['pumpkins', 'my_pumpkins'])
@group_only
def handle_my_pumpkins(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    response = (
        f"Осенний ивент окончен\n\n"
    )
    bot.reply_to(message, response)
@bot.message_handler(commands=['zov', 'z'])
@group_only
def handle_petya(message:Message):
    init_user_data(user_id)
    petka1 = ("поздняков гой")
    bot.reply_to(message, petka1)
@bot.message_handler(commands=['roblox', 'rb'])
@group_only
def handle_123(message:Message):
    init_user_data(user_id)
    petka12 = ("le le le")
    bot.reply_to(message, petka12)
@bot.message_handler(commands=['farm', 'f'])
@group_only
def handle_farm(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        if user_balances[user_id].get('kill_ban_until', 0) > datetime.datetime.now().timestamp():
            remaining_time = user_balances[user_id]['kill_ban_until'] - datetime.datetime.now().timestamp()
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            bot.reply_to(message, f"?? Вы мертвы! Не можете фармить еще {hours}ч {minutes}м")
            return
        current_time = datetime.datetime.now().timestamp()
        last_farm = user_balances[user_id]['last_farm']
        if not can_farm(last_farm, user_id):
            time_until_next = 3600 - (current_time - last_farm)
            if 'scroll' in user_balances[user_id]['items']:
                time_until_next -= 600
            remaining_time = format_remaining_time(time_until_next)
            cooldown_message = random.choice(COOLDOWN_MESSAGES).format(time=remaining_time)
            response = (
                f"{cooldown_message}\n\n"
                f"Текущий баланс:\n"
                f"Zеток: {user_balances[user_id]['leaves']}\n"
                f"?? Территории: {user_balances[user_id]['tea']}"
            )
            bot.reply_to(message, response)
            return
        try:
            base_leaves = random.randint(1, 10)
            bonus_multiplier = 1.0
            for item_id in user_balances[user_id]['items']:
                item = SHOP_ITEMS[item_id]
                if item['bonus_type'] == 'farm':
                    bonus_multiplier += item['bonus_value']
            total_leaves = int(base_leaves * bonus_multiplier)
            bonus_text = ""
            if bonus_multiplier > 1:
                bonus_text = f"(+{int((bonus_multiplier-1)*100)}% = {total_leaves})"
            user_balances[user_id]['leaves'] += total_leaves
            user_balances[user_id]['last_farm'] = current_time
            custom_phrases = user_balances[user_id].get('custom_work', [])
            if custom_phrases:
                farm_message = random.choice(custom_phrases).format(count=f"{base_leaves}{bonus_text}")
            else:
                farm_message = random.choice(FARM_MESSAGES).format(count=f"{base_leaves}{bonus_text}")
            leaves_emoji = "??" * min(total_leaves, 20)
            response = (
                f"{farm_message}\n{leaves_emoji}\n\n"
                f"Баланс:\n"
                f"Zеток: {user_balances[user_id]['leaves']}\n"
                f"?? Территории: {user_balances[user_id]['tea']}\n"
            )
            response += f"\n\n? Следующий сбор будет доступен через 1 час"
            if 'scroll' in user_balances[user_id]['items']:
                response = response.replace("1 час", "50 минут")
            bot.reply_to(message, response)
        except Exception as e:
            print(f"Ошибка при сборе Zеток: {e}")
            bot.reply_to(message, "? Произошла ошибка при сборе Zеток. Попробуйте позже.")
    except Exception as e:
        print(f"Общая ошибка в handle_farm: {e}")
        bot.reply_to(message, "? Произошла неизвестная ошибка. Попробуйте позже.")
@bot.message_handler(commands=['balance', 'b'])
@group_only
def handle_balance(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    ban_status = ""
    if user_balances[user_id].get('banned', False):
        ban_status = "\n\n?? Ваш аккаунт заблокирован!"
    response = (
        f"Ваш баланс:\n"
        f"💰 Zеток: {user_balances[user_id]['leaves']}\n"
        f"?? Территории: {user_balances[user_id]['tea']}"
        f"{ban_status}"
    )
    bot.reply_to(message, response)
@bot.message_handler(commands=['add_nft'])
def handle_add_nft(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        if not message.reply_to_message or not message.reply_to_message.photo:
            bot.reply_to(message,
                "? Ответьте этой командой на сообщение с фотографией!\n"
                "Формат: /add_nft [описание] [редкость]\n"
                "Пример: /add_nft Редкий свиток мудрости rare")
            return
        command_parts = message.text.split(maxsplit=2)
        if len(command_parts) < 3:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /add_nft [описание] [редкость]\n"
                "Редкости: common, rare, epic, legendary")
            return
        description = command_parts[1]
        rarity = command_parts[2].lower()
        if rarity not in ['common', 'rare', 'epic', 'legendary']:
            bot.reply_to(message, "? Неверная редкость! Используйте: common, rare, epic, legendary")
            return
        photo = message.reply_to_message.photo[-1]
        file_id = photo.file_id
        nft_id = len(user_nfts) + 1
        user_nfts[nft_id] = {
            'file_id': file_id,
            'description': description,
            'rarity': rarity,
            'created_by': message.from_user.id,
            'created_at': datetime.datetime.now().timestamp(),
            'owner': None
        }
        save_nft_data()
        bot.reply_to(message,
            f"? NFT успешно создан!\n\n"
            f"🔗 ID: {nft_id}\n"
            f"?? Описание: {description}\n"
            f"?? Редкость: {rarity}\n"
            f"?? Фото: сохранено")
    except Exception as e:
        print(f"Ошибка в handle_add_nft: {e}")
        bot.reply_to(message, "? Произошла ошибка при создании NFT")
@bot.message_handler(commands=['give_nft'])
def handle_give_nft(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /give_nft @username nft_id")
            return
        username = command_parts[1].lstrip('@')
        try:
            nft_id = int(command_parts[2])
        except ValueError:
            bot.reply_to(message, "? ID NFT должен быть числом!")
            return
        # Ищем пользователя
        recipient_found = False
        for user_id in user_balances.keys():
            try:
                user_info = bot.get_chat(user_id)
                if user_info.username and user_info.username.lower() == username.lower():
                    recipient_id = user_id
                    recipient_name = user_info.first_name
                    recipient_found = True
                    break
            except:
                continue
        if not recipient_found:
            bot.reply_to(message, "? Пользователь не найден!")
            return
        if nft_id not in user_nfts:
            bot.reply_to(message, "? NFT с таким ID не существует!")
            return
        if user_nfts[nft_id]['owner'] is not None:
            bot.reply_to(message, "? Этот NFT уже принадлежит другому игроку!")
            return
        init_user_data(recipient_id)
        # Передаем NFT
        user_nfts[nft_id]['owner'] = recipient_id
        user_balances[recipient_id]['nfts'].append(nft_id)
        save_nft_data()
        save_user_data()
        nft = user_nfts[nft_id]
        rarity_emoji = {
            'common': '?',
            'rare': '💎',
            'epic': '💍',
            'legendary': '👑'
        }.get(nft['rarity'], '?')
        bot.reply_to(message,
            f"? NFT успешно передан!\n\n"
            f"?? Получатель: {recipient_name}\n"
            f"🎨 {nft['description']}\n"
            f"{rarity_emoji} Редкость: {nft['rarity']}")
        # Отправляем NFT пользователю
        try:
            bot.send_photo(recipient_id, nft['file_id'],
                caption=f"?? Вы получили NFT!\n\n"
                       f"🎨 {nft['description']}\n"
                       f"{rarity_emoji} Редкость: {nft['rarity']}\n"
                       f"🔗 ID: {nft_id}")
        except Exception as e:
            print(f"Ошибка при отправке NFT: {e}")
    except Exception as e:
        print(f"Ошибка в handle_give_nft: {e}")
        bot.reply_to(message, "? Произошла ошибка при передаче NFT")
@bot.message_handler(commands=['my_nfts'])
@group_only
def handle_my_nfts(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        nft_ids = user_balances[user_id].get('nfts', [])
        if not nft_ids:
            bot.reply_to(message, "?? У вас пока нет NFT!")
            return
        response = "?? Ваша коллекция NFT:\n\n"
        for nft_id in nft_ids:
            if nft_id in user_nfts:
                nft = user_nfts[nft_id]
                rarity_emoji = {
                    'common': '?',
                    'rare': '💎',
                    'epic': '💍',
                    'legendary': '👑'
                }.get(nft['rarity'], '?')
                response += f"🎨 {nft_id}: {rarity_emoji} {nft['description']}\n"
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_my_nfts: {e}")
        bot.reply_to(message, "? Произошла ошибка при просмотре коллекции")
@bot.message_handler(commands=['killstats', 'kills'])
def handle_killstats(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if not HALLOWEEN_EVENT_ACTIVE:
            bot.reply_to(message, "? Хэллоуинский ивент завершен!")
            return
        killers = []
        for uid, data in user_balances.items():
            if data.get('kills', 0) > 0:
                try:
                    user_name = bot.get_chat(uid).first_name
                    killers.append((user_name, data['kills']))
                except:
                    continue
        killers.sort(key=lambda x: x[1], reverse=True)
        response = "?? Хэллоуинский ивент 2 - Статистика убийств\n\n?? Топ убийц:\n"
        for i, (name, kills) in enumerate(killers[:10], 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "??")
            response += f"{medal} {i}. {name}: {kills} убийств\n"
        user_kills = user_balances[user_id].get('kills', 0)
        user_rank = next((i for i, (_, k) in enumerate(killers, 1) if _ == message.from_user.first_name), None)
        response += f"\nВаша статистика:\n"
        response += f" Убийств: {user_kills}\n"
        response += f"Ранг: {user_rank if user_rank else 'не в топе'}\n"
        if user_balances[user_id].get('kill_ban_until', 0) > datetime.datetime.now().timestamp():
            remaining_time = user_balances[user_id]['kill_ban_until'] - datetime.datetime.now().timestamp()
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            response += f"?? Статус: Мертв (вернетесь через {hours}ч {minutes}м)\n"
        else:
            current_time = datetime.datetime.now().timestamp()
            last_kill = user_balances[user_id].get('last_kill_time', 0)
            if current_time - last_kill < KILL_COOLDOWN:
                remaining = KILL_COOLDOWN - (current_time - last_kill)
                minutes = int(remaining // 60)
                response += f"? До следующего убийства: {minutes} минут\n"
            else:
                response += f"? Можете убивать!\n"
        response += f"\n?? Ивент длится до 09.11.2025\n🏆 Победитель получит Хэллоуинскую тыкву!"
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_killstats: {e}")
        bot.reply_to(message, "? Произошла ошибка при получении статистики")
@bot.message_handler(commands=['buy_nft'])
@group_only
def handle_buy_nft(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /buy_nft nft_id\n\n"
                "?? Доступные NFT: /nft_list")
            return
        try:
            nft_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "? ID NFT должен быть числом!")
            return
        # Проверяем существование NFT
        if nft_id not in user_nfts:
            bot.reply_to(message, "? NFT с таким ID не существует!")
            return
        nft = user_nfts[nft_id]
        # Проверяем, не принадлежит ли уже кому-то
        if nft['owner'] is not None:
            bot.reply_to(message, "? Этот NFT уже принадлежит другому игроку!")
            return
        if user_balances[user_id]['leaves'] < NFT_BASE_PRICE:
            bot.reply_to(message,
                f"? Недостаточно Zеток!\n"
                f"Нужно: {NFT_BASE_PRICE} Zеток\n"
                f"У вас: {user_balances[user_id]['leaves']} Zеток")
            return
        # Покупаем NFT
        user_balances[user_id]['leaves'] -= NFT_BASE_PRICE
        user_nfts[nft_id]['owner'] = user_id
        user_balances[user_id]['nfts'].append(nft_id)
        save_nft_data()
        save_user_data()
        rarity_emoji = {
            'common': '?',
            'rare': '💎',
            'epic': '💍',
            'legendary': '👑'
        }.get(nft['rarity'], '?')
        # Отправляем подтверждение и сам NFT
        bot.reply_to(message,
            f"? Вы успешно приобрели NFT!\n\n"
            f"🎨 {nft['description']}\n"
            f"{rarity_emoji} Редкость: {nft['rarity']}\n"
            f"?? Стоимость: {NFT_BASE_PRICE} Zеток\n"
            f"?? Новый баланс: {user_balances[user_id]['leaves']} Zеток")
        # Отправляем фото NFT
        try:
            bot.send_photo(user_id, nft['file_id'],
                caption=f"?? Поздравляем с покупкой!\n\n"
                       f"🎨 {nft['description']}\n"
                       f"{rarity_emoji} Редкость: {nft['rarity']}\n"
                       f"🔗 ID: {nft_id}\n"
                       f"?? Куплено за: {NFT_BASE_PRICE} Zеток")
        except Exception as e:
            print(f"Ошибка при отправке NFT: {e}")
    except Exception as e:
        print(f"Ошибка в handle_buy_nft: {e}")
        bot.reply_to(message, "? Произошла ошибка при покупке NFT")
@bot.message_handler(commands=['view_nft'])
@group_only
def handle_view_nft(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /view_nft nft_id")
            return
        try:
            nft_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "? ID NFT должен быть числом!")
            return
        if nft_id not in user_nfts:
            bot.reply_to(message, "? NFT с таким ID не существует!")
            return
        nft = user_nfts[nft_id]
        rarity_emoji = {
            'common': '?',
            'rare': '💎',
            'epic': '💍',
            'legendary': '👑'
        }.get(nft['rarity'], '?')
        if nft['owner'] is None:
            owner_info = f"?? Свободен\n?? Цена: {NFT_BASE_PRICE} Zеток\n?? Купить: /buy_nft {nft_id}"
        else:
            try:
                owner = bot.get_chat(nft['owner'])
                owner_info = f"?? Владелец: {owner.first_name}"
                if nft['owner'] == user_id:
                    owner_info += " (Ваш NFT)"
            except:
                owner_info = "?? Владелец: Неизвестен"
        # Отправляем фото NFT
        bot.send_photo(message.chat.id, nft['file_id'],
            caption=f"?? NFT #{nft_id}\n\n"
                   f"🎨 {nft['description']}\n"
                   f"{rarity_emoji} Редкость: {nft['rarity']}\n"
                   f"?? Создан: {datetime.datetime.fromtimestamp(nft['created_at']).strftime('%d.%m.%Y')}\n"
                   f"{owner_info}")
    except Exception as e:
        print(f"Ошибка в handle_view_nft: {e}")
        bot.reply_to(message, "? Произошла ошибка при просмотре NFT")
@bot.message_handler(commands=['nft_list'])
@group_only
def handle_nft_list(message: Message):
    try:
        if not user_nfts:
            bot.reply_to(message, "? В системе пока нет NFT!")
            return
        response = "?? Все NFT в системе:\n\n"
        for nft_id, nft in user_nfts.items():
            rarity_emoji = {
                'common': '?',
                'rare': '💎',
                'epic': '💍',
                'legendary': '👑'
            }.get(nft['rarity'], '?')
            status = "?? Свободен" if nft['owner'] is None else "?? В коллекции"
            price_info = f"?? {NFT_BASE_PRICE} Zеток" if nft['owner'] is None else "?? Продано"
            response += f"🎨 {nft_id}: {rarity_emoji} {nft['description']} - {status} {price_info}\n"
        response += f"\n?? Все NFT стоят: {NFT_BASE_PRICE} Zеток\n"
        response += "?? Для покупки: /buy_nft [id]"
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_nft_list: {e}")
        bot.reply_to(message, "? Произошла ошибка при получении списка NFT")
@bot.message_handler(commands=['users'])
@group_only
def handle_users(message: Message):
    users_count = len(user_balances)
    total_leaves = sum(u['leaves'] for u in user_balances.values())
    total_tea = sum(u['tea'] for u in user_balances.values())
    user_id = message.from_user.id
    init_user_data(user_id)
    ban_status = ""
    if user_balances[user_id].get('banned', False):
        ban_status = "\n\n?? Ваш аккаунт заблокирован!"
    response = (
        f"Статистика бота:\n"
        f"?? Всего пользователей: {users_count}\n"
        f"💰 Всего заработано Zеток: {total_leaves}\n"
        f"?? Всего территорий: {total_tea}"
        f"{ban_status}"
    )
    bot.reply_to(message, response)
@bot.message_handler(commands=['top'])
@group_only
def handle_top(message: Message):
    # Сортируем пользователей по количеству чая и Zеток
    sorted_users = sorted(
        user_balances.items(),
        key=lambda x: (x[1]['tea'], x[1]['leaves']),
        reverse=True
    )
    # Берем топ-10 пользователей
    top_users = sorted_users[:10]
    # Формируем сообщение
    response = "?? Топ-10 сборщиков:\n\n"
    for index, (user_id, balance) in enumerate(top_users, 1):
        try:
            user = bot.get_chat(user_id)
            user_name = user.first_name
            # Добавляем медали для первых трех мест
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(index, "??")
            response += f"{medal} {index}. {user_name}: ?? {balance['tea']} | ??{balance['leaves']}\n"
        except:
            response += f"?? {index}. Пользователь:  ?? {balance['tea']} | ?? {balance['leaves']}\n"
    # В конце добавим статус бана если есть
    user_id = message.from_user.id
    init_user_data(user_id)
    if user_balances[user_id].get('banned', False):
        response += "\n\n?? Ваш аккаунт заблокирован!"
    bot.reply_to(message, response)
@bot.message_handler(commands=['craft'])
@group_only
def handle_craft(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        command_parts = message.text.split()
        # Если количество не указано, устанавливаем 1
        if len(command_parts) == 1:
            amount = 1
        else:
            try:
                amount = int(command_parts[1])
                if amount <= 0:
                    bot.reply_to(message, "? Количество должно быть положительным числом!")
                    return
            except ValueError:
                bot.reply_to(message,
                    "? Неверный формат команды!\n"
                    "Используйте: /craft [количество]\n"
                    "Например: /craft 5 или просто /craft для захвата 1 территории")
                return
        # Базовая стоимость крафта
        base_cost = 100
        # Применяем скидку от чайника Ы если есть
        if 'teapot' in user_balances[user_id]['items']:
            base_cost -= SHOP_ITEMS['teapot']['bonus_value']
        total_cost = base_cost * amount
        if user_balances[user_id]['leaves'] < total_cost:
            bot.reply_to(message,
                f"? Недостаточно Zеток!\n"
                f"Необходимо: {total_cost} Zеток\n"
                f"У вас есть: {user_balances[user_id]['leaves']} Zеток")
            return
        user_balances[user_id]['leaves'] -= total_cost
        user_balances[user_id]['tea'] += amount
        save_user_data()
        # Формируем сообщение с учетом скидки
        cost_text = str(base_cost)
        if 'teapot' in user_balances[user_id]['items']:
            cost_text = f"{10}(-{SHOP_ITEMS['teapot']['bonus_value']} = {base_cost})"
        craft_message = random.choice(CRAFT_MESSAGES).format(
            count=amount,
            word="чая" if amount == 1 else "чая" if 2 <= amount <= 4 else "чая"
        )
        response = (
            f"{craft_message}\n"
            f"Потрачено Zеток: {cost_text} ? {amount} = {total_cost} \n\n"
            f"Баланс:\n"
            f"Zеток: {user_balances[user_id]['leaves']}\n"
            f"?? Территории: {user_balances[user_id]['tea']}"
        )
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_craft: {e}")
        bot.reply_to(message, "? Произошла ошибка при создании чая")
@bot.message_handler(commands=['farmtime'])
@group_only
def handle_farmtime(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        current_time = datetime.datetime.now().timestamp()
        last_farm = user_balances[user_id]['last_farm']
        if can_farm(last_farm, user_id):
            response = "? Вы можете работать\nИспользуйте команду /farm"
        else:
            time_until_next = 3600 - (current_time - last_farm)
            remaining_time = format_remaining_time(time_until_next)
            response = f"? Следующая работа будет доступен через {remaining_time}"
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_farmtime: {e}")
        bot.reply_to(message, "? Произошла ошибка при проверке времени. Попробуйте позже.")
@bot.message_handler(commands=['market_sell', 'msell'])
@group_only
def handle_market_sell(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /market_sell [id_предмета] [цена]\n"
                "Пример: /market_sell scroll 500\n\n"
                "?? Доступные предметы:\n"
                "• scroll - ?? Свиток мудрости\n"
                "• jade_rod - ?? Нефритовый стержень\n"
                "• watermelon - ?? Священный арбуз\n"
                "• и другие из /shop")
            return
        item_id = command_parts[1].lower()
        try:
            price = int(command_parts[2])
        except ValueError:
            bot.reply_to(message, "? Цена должна быть числом!")
            return
        if item_id not in SHOP_ITEMS:
            bot.reply_to(message, "? Такого предмета не существует!")
            return
        if price < MARKET_MIN_PRICE:
            bot.reply_to(message, f"? Минимальная цена продажи: {MARKET_MIN_PRICE} Zеток!")
            return
        if item_id not in user_balances[user_id]['items']:
            bot.reply_to(message, "? У вас нет этого предмета!")
            return
        item = SHOP_ITEMS[item_id]
        tax = int(price * MARKET_TAX_PERCENT / 100)
        seller_receives = price - tax
        listing_id = len(market_listings) + 1
        market_listings[listing_id] = {
            'seller_id': user_id,
            'seller_name': message.from_user.first_name,
            'item_id': item_id,
            'item_name': item['name'],
            'price': price,
            'tax': tax,
            'seller_receives': seller_receives,
            'created_at': datetime.datetime.now().timestamp(),
            'expires_at': datetime.datetime.now().timestamp() + MARKET_MAX_DURATION
        }
        user_balances[user_id]['items'].remove(item_id)
        save_user_data()
        save_market_data()
        bot.reply_to(message,
            f"? Предмет выставлен на рынок!\n\n"
            f"?? Предмет: {item['name']}\n"
            f"?? Цена: {price} Zеток\n"
            f"?? Налог: {tax} Zеток ({MARKET_TAX_PERCENT}%)\n"
            f"?? Вы получите: {seller_receives} Zеток\n"
            f"? Действует: 7 дней\n"
            f"?? ID предложения: #{listing_id}\n\n"
            f"Для отмены: /market_cancel {listing_id}")
    except Exception as e:
        print(f"Ошибка в handle_market_sell: {e}")
        bot.reply_to(message, "? Произошла ошибка при выставлении предмета на рынок")
@bot.message_handler(commands=['market', 'm'])
@group_only
def handle_market(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        cleanup_expired_listings()
        if not market_listings:
            bot.reply_to(message, "?? На рынке пока нет предложений!")
            return
        response = "?? Пользовательский рынок\n\n"
        for listing_id, listing in list(market_listings.items())[:10]:  # Показываем первые 10
            time_left = listing['expires_at'] - datetime.datetime.now().timestamp()
            days = int(time_left // (24 * 60 * 60))
            hours = int((time_left % (24 * 60 * 60)) // 3600)
            response += (
                f"?? #{listing_id} - {listing['item_name']}\n"
                f"?? Цена: {listing['price']} Zеток\n"
                f"?? Продавец: {listing['seller_name']}\n"
                f"? Осталось: {days}д {hours}ч\n\n"
            )
        response += (
            f"?? Всего предложений: {len(market_listings)}\n"
            f"?? Посмотреть все: /market_all\n"
            f"?? Купить предмет: /market_buy [id_предмета]\n"
            f"?? Продать предмет: /market_sell [id_предмета] [цена]"
        )
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_market: {e}")
        bot.reply_to(message, "? Произошла ошибка при просмотре рынка")
@bot.message_handler(commands=['market_buy', 'mbuy'])
@group_only
def handle_market_buy(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /market_buy [id_предложения]\n"
                "Пример: /market_buy 1")
            return
        try:
            listing_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "? ID предложения должен быть числом!")
            return
        if listing_id not in market_listings:
            bot.reply_to(message, "? Предложение не найдено!")
            return
        listing = market_listings[listing_id]
        if datetime.datetime.now().timestamp() > listing['expires_at']:
            del market_listings[listing_id]
            save_market_data()
            bot.reply_to(message, "? Предложение истекло!")
            return
        if user_id == listing['seller_id']:
            bot.reply_to(message, "? Нельзя купить у самого себя!")
            return
        if user_balances[user_id]['leaves'] < listing['price']:
            bot.reply_to(message,
                f"? Недостаточно Zеток!\n"
                f"Нужно: {listing['price']} Zеток\n"
                f"У вас: {user_balances[user_id]['leaves']} Zеток")
            return
        if len(user_balances[user_id]['items']) >= 3:
            bot.reply_to(message,
                "? У вас максимальное количество предметов!\n"
                "Освободите место: /inventory")
            return
        user_balances[user_id]['leaves'] -= listing['price']
        user_balances[user_id]['items'].append(listing['item_id'])
        seller_id = listing['seller_id']
        init_user_data(seller_id)
        user_balances[seller_id]['leaves'] += listing['seller_receives']
        item_name = listing['item_name']
        del market_listings[listing_id]
        save_user_data()
        save_market_data()
        bot.reply_to(message,
            f"? Вы купили {item_name} за {listing['price']} Zеток!\n"
            f"Предмет добавлен в инвентарь: /inventory")
        try:
            bot.send_message(seller_id,
                f"?? Ваш предмет {item_name} продан!\n"
                f"?? Получено: {listing['seller_receives']} Zеток (за вычетом налога)\n"
                f"?? Покупатель: {message.from_user.first_name}")
        except:
            pass
    except Exception as e:
        print(f"Ошибка в handle_market_buy: {e}")
        bot.reply_to(message, "? Произошла ошибка при покупке предмета")
@bot.message_handler(commands=['market_cancel', 'mcancel'])
@group_only
def handle_market_cancel(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /market_cancel [id_предложения]")
            return
        try:
            listing_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "? ID предложения должен быть числом!")
            return
        if listing_id not in market_listings:
            bot.reply_to(message, "? Предложение не найдено!")
            return
        listing = market_listings[listing_id]
        if user_id != listing['seller_id']:
            bot.reply_to(message, "? Это не ваше предложение!")
            return
        user_balances[user_id]['items'].append(listing['item_id'])
        del market_listings[listing_id]
        save_user_data()
        save_market_data()
        bot.reply_to(message,
            f"? Предложение #{listing_id} отменено!\n"
            f"?? {listing['item_name']} возвращен в ваш инвентарь")
    except Exception as e:
        print(f"Ошибка в handle_market_cancel: {e}")
        bot.reply_to(message, "? Произошла ошибка при отмене предложения")
@bot.message_handler(commands=['market_all', 'mall'])
@group_only
def handle_market_all(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        cleanup_expired_listings()
        if not market_listings:
            bot.reply_to(message, "?? На рынке пока нет предложений!")
            return
        response = "?? Все предложения на рынке\n\n"
        for listing_id, listing in market_listings.items():
            time_left = listing['expires_at'] - datetime.datetime.now().timestamp()
            days = int(time_left // (24 * 60 * 60))
            hours = int((time_left % (24 * 60 * 60)) // 3600)
            response += (
                f"?? #{listing_id} - {listing['item_name']}\n"
                f"?? Цена: {listing['price']} Zеток\n"
                f"?? Продавец: {listing['seller_name']}\n"
                f"? Осталось: {days}д {hours}ч\n"
            )
        response += f"\n?? Всего предложений: {len(market_listings)}"
        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for part in parts:
                bot.send_message(user_id, part)
        else:
            bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_market_all: {e}")
        bot.reply_to(message, "? Произошла ошибка при просмотре рынка")
@bot.message_handler(commands=['tc'])
@group_only
def handle_transfer(message: Message):
    try:
        sender_id = message.from_user.id
        init_user_data(sender_id)
        if check_ban(sender_id, message):
            return
        command_parts = message.text.split()
        if message.reply_to_message:
            if len(command_parts) != 2:
                bot.reply_to(message,
                    "? Неверный формат команды!\n"
                    "При ответе на сообщение используйте:\n"
                    "/tc количество\n"
                    "Например: /tc 10")
                return
            recipient = message.reply_to_message.from_user
            recipient_id = recipient.id
            recipient_name = recipient.first_name
            amount = int(command_parts[1])
        else:
            if len(command_parts) != 3:
                bot.reply_to(message,
                    "? Неверный формат команды!\n"
                    "Используйте один из вариантов:\n"
                    "1. /tc @username количество\n"
                    "2. Ответьте на сообщение командой /tc количество")
                return
            recipient_username = command_parts[1].lstrip('@')
            try:
                amount = int(command_parts[2])
            except ValueError:
                bot.reply_to(message, "? Количество Zеток должно быть числом!")
                return
            try:
                recipient_found = False
                for user_id in user_balances.keys():
                    try:
                        user_info = bot.get_chat(user_id)
                        if user_info.username and user_info.username.lower() == recipient_username.lower():
                            recipient_id = user_id
                            recipient_name = user_info.first_name
                            recipient_found = True
                            break
                    except:
                        continue
                if not recipient_found:
                    bot.reply_to(message,
                        "? Пользователь не найден или никогда не использовал бота.\n"
                        "Убедитесь, что:\n"
                        "1. Указан правильный username\n"
                        "2. Пользователь хотя бы раз запускал бота")
                    return
            except Exception as e:
                print(f"Ошибка при поиске пользователя: {e}")
                bot.reply_to(message, "? Не удалось найти пользователя")
                return
        sender_balance = user_balances[sender_id]['leaves']  # Получаем количество Zеток
        if amount <= 0:
            bot.reply_to(message, "? Количество Zеток должно быть положительным числом!")
            return
        # Проверяем достаточно ли Zеток
        if amount > sender_balance:
            bot.reply_to(message, f"? У вас недостаточно Zеток!\nВаш баланс: {sender_balance} ??")
            return
        if recipient_id == sender_id:
            bot.reply_to(message, "? Вы не можете отправить Zетки самому себе!")
            return
        init_user_data(recipient_id)
        user_balances[sender_id]['leaves'] -= amount
        user_balances[recipient_id]['leaves'] += amount
        save_user_data()
        bot.reply_to(message,
            f"? Успешно отправлено {amount} Zеток пользователю {recipient_name}!\n"
            f"Ваш новый баланс: {user_balances[sender_id]['leaves']} Zеток")
        try:
            bot.send_message(recipient_id,
                f"?? Вы получили {amount} Zеток от {message.from_user.first_name}!\n"
                f"Ваш новый баланс: {user_balances[recipient_id]['leaves']} Zеток")
        except Exception as e:
            print(f"Не удалось отправить уведомление получателю: {e}")
    except Exception as e:
        bot.reply_to(message,
            "? Произошла ошибка при обработке команды.\n"
            "Используйте один из вариантов:\n"
            "1. /tс @username количество\n"
            "2. Ответьте на сообщение командой /tс количество")
        print(f"Общая ошибка в handle_transfer: {e}")
@bot.message_handler(commands=['customwork'])
@group_only
def handle_custom_work(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        # Получаем текст после команды
        command_text = message.text.replace('/customwork', '', 1).strip()
        if not command_text:
            # Если просто команда без текста - показываем текущие фразы
            custom_phrases = user_balances[user_id].get('custom_work', [])
            if not custom_phrases:
                response = (
                    "?? У вас нет кастомных фраз для работы.\n\n"
                    "Чтобы добавить, отправьте:\n"
                    "/customwork\n"
                    "Ваша фраза 1+{count}\n"
                    "Ваша фраза 2+{count}\n"
                    "(до 5 фраз, каждая с новой строки). ВАЖНО! команда именно /customwork, без @ник_бота"
                )
            else:
                response = "?? Ваши текущие фразы для работы:\n\n" + "\n".join(
                    f"{i+1}. {phrase}" for i, phrase in enumerate(custom_phrases)
                ) + "\n\nОтправьте /customwork с новыми фразами для обновления"
            bot.reply_to(message, response)
            return
        # Разбиваем на фразы (максимум 5)
        phrases = [p.strip() for p in command_text.split('\n') if p.strip()][:5]
        if len(phrases) < 2:
            bot.reply_to(message,
                "? Нужно указать хотя бы 2 фразы (каждая с новой строки)!\n\n"
                "Пример:\n"
                "/customwork\n"
                "Отлично поработал! +{count} Zеток\n"
                "Молодец! Получаешь {count} соц.Zетоков")
            return
        # Сохраняем фразы
        user_balances[user_id]['custom_work'] = phrases
        save_user_data()
        bot.reply_to(message,
            f"? Установлено {len(phrases)} кастомных фраз для работы!\n"
            "Теперь при использовании /farm будут использоваться ваши фразы.")
    except Exception as e:
        print(f"Ошибка в handle_custom_work: {e}")
        bot.reply_to(message, "? Произошла ошибка при сохранении кастомных фраз")
@bot.message_handler(commands=['give'])
def handle_give(message: Message):
    try:
        # Проверяем права администратора
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        command_parts = message.text.split()
        # Проверяем формат команды
        if len(command_parts) != 3:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /give @username количество")
            return
        # Получаем username получателя (убираем @ если есть)
        recipient_username = command_parts[1].lstrip('@')
        try:
            amount = int(command_parts[2])
            if amount <= 0:
                bot.reply_to(message, "? Количество Zеток должно быть положительным числом!")
                return
        except ValueError:
            bot.reply_to(message, "? Количество Zеток должно быть числом!")
            return
        try:
            recipient_found = False
            for user_id in user_balances.keys():
                try:
                    user_info = bot.get_chat(user_id)
                    if user_info.username and user_info.username.lower() == recipient_username.lower():
                        recipient_id = user_id
                        recipient_name = user_info.first_name
                        recipient_found = True
                        break
                except:
                    continue
            if not recipient_found:
                bot.reply_to(message,
                    "? Пользователь не найден или никогда не использовал бота.\n"
                    "Убедитесь, что:\n"
                    "1. Указан правильный username\n"
                    "2. Пользователь хотя бы раз запускал бота")
                return
        except Exception as e:
            print(f"Ошибка при поиске пользователя: {e}")
            bot.reply_to(message, "? Не удалось найти пользователя")
            return
        init_user_data(recipient_id)
        user_balances[recipient_id]['leaves'] += amount
        save_user_data()
        bot.reply_to(message,
            f"? Успешно выдано {amount} Zеток пользователю {recipient_name}!\n"
            f"Его новый баланс: {user_balances[recipient_id]['leaves']} Zеток")
        try:
            bot.send_message(recipient_id,
                f"?? Администратор выдал вам {amount} Zеток!\n"
                f"Ваш новый баланс: {user_balances[recipient_id]['leaves']} Zеток")
        except Exception as e:
            print(f"Не удалось отправить уведомление получателю: {e}")
    except Exception as e:
        bot.reply_to(message,
            "? Произошла ошибка при обработке команды.\n"
            "Используйте: /give @username количество")
        print(f"Общая ошибка в handle_give: {e}")
@bot.message_handler(commands=['me'])
@group_only
def handle_me(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        check_warnings(user_id)
        user = message.from_user
        current_time = datetime.datetime.now().timestamp()
        last_farm = user_balances[user_id]['last_farm']
        if can_farm(last_farm, user_id):
            farm_status = "? Доступен"
        else:
            time_until_next = 3600 - (current_time - last_farm)
            remaining_time = format_remaining_time(time_until_next)
            farm_status = f"? Через {remaining_time}"
        warnings = user_balances[user_id].get('warnings', [])
        warnings_text = f"\n?? Предупреждений: {len(warnings)}/{MAX_WARNINGS}"
        if warnings:
            warnings_text += "\nПоследнее предупреждение:\n"
            last_warn = warnings[-1]
            time_left = WARNING_DURATION - (datetime.datetime.now().timestamp() - last_warn['time'])
            days_left = int(time_left // (24 * 60 * 60))
            warnings_text += f"Причина: {last_warn['reason']}\n"
            warnings_text += f"Выдал: {last_warn['admin']}\n"
            warnings_text += f"Будет снято через: {days_left} дней"
        response = (
            f"?? Профиль игрока\n\n"
            f"Имя: {user.first_name}\n"
            f"ID: {user.id}\n"
            f"Username: @{user.username if user.username else 'отсутствует'}\n\n"
            f"?? Баланс:\n"
            f"?? Zетки: {user_balances[user_id]['leaves']}\n"
            f"?? Территории: {user_balances[user_id]['tea']}"
            f"?? Следующий сбор: {farm_status}\n"
            f"?? Администратор: {'Да' if is_admin(user_id) else 'Нет'}"
            f"{warnings_text}"
        )
        if user_balances[user_id].get('banned', False):
            response += f"\n\n?? Аккаунт заблокирован!\nПричина: {user_balances[user_id].get('ban_reason', 'не указана')}"
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_me: {e}")
        bot.reply_to(message, "? Произошла ошибка при получении информации. Попробуйте позже.")
@bot.message_handler(commands=['end_event'])
def handle_end_event(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        global HALLOWEEN_EVENT_ACTIVE
        HALLOWEEN_EVENT_ACTIVE = False
        end_halloween_event()
        bot.reply_to(message, "? Хэллоуинский ивент завершен досрочно!")
    except Exception as e:
        print(f"Ошибка в handle_end_event: {e}")
        bot.reply_to(message, "? Произошла ошибка при завершении ивента")
@bot.message_handler(commands=['admin'])
def handle_admin(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        admin_text = (
            f"?? Панель администратора\n\n"
            f"Доступные команды:\n"
            f"?? /give @username количество - выдать соц Zеток\n"
            f"?? /take @username количество - забрать соц Zеток\n"
            f"?? /reset @username - сбросить таймер сбора\n"
            f"?? /stats - подробная статистика\n"
            f"?? /announce текст - отправить объявление всем\n"
            f"?? /warn @username причина - выдать предупреждение\n"
            f"? /unwarn @username - снять предупреждение\n"
            f"?? /ban @username причина - заблокировать пользователя\n"
            f"?? /unban @username - разблокировать пользователя\n\n"
            f"Система предупреждений:\n"
            f"• Предупреждения снимаются автоматически через 7 дней\n"
            f"• При достижении {MAX_WARNINGS} предупреждений - автобан"
        )
        bot.reply_to(message, admin_text)
    except Exception as e:
        print(f"Ошибка в handle_admin: {e}")
        bot.reply_to(message, "? Произошла ошибка при открытии панели администратора")
@bot.message_handler(commands=['take'])
def handle_take(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message, "? Используйте: /take @username количество")
            return
        recipient_username = command_parts[1].lstrip('@')
        try:
            amount = int(command_parts[2])
            if amount <= 0:
                bot.reply_to(message, "? Количество должно быть положительным числом!")
                return
        except ValueError:
            bot.reply_to(message, "? Количество должно быть числом!")
            return
        # Поиск пользователя
        recipient_found = False
        for user_id in user_balances.keys():
            try:
                user_info = bot.get_chat(user_id)
                if user_info.username and user_info.username.lower() == recipient_username.lower():
                    recipient_id = user_id
                    recipient_name = user_info.first_name
                    recipient_found = True
                    break
            except:
                continue
        if not recipient_found:
            bot.reply_to(message, "? Пользователь не найден!")
            return
        init_user_data(recipient_id)
        # Проверяем баланс
        if user_balances[recipient_id]['leaves'] < amount:
            bot.reply_to(message,
                f"? У пользователя недостаточно Zеток!\n"
                f"Доступно: {user_balances[recipient_id]['leaves']} ??")
            return
        # Забираем Zетки
        user_balances[recipient_id]['leaves'] -= amount
        save_user_data()
        bot.reply_to(message,
            f"? Успешно изъято {amount} Zеток у пользователя {recipient_name}!\n"
            f"Его новый баланс: {user_balances[recipient_id]['leaves']} Zеток")
        bot.send_message(recipient_id,
            f"?? Администратор изъял у вас {amount} Zеток!\n"
            f"Ваш новый баланс: {user_balances[recipient_id]['leaves']} Zеток")
    except Exception as e:
        print(f"Ошибка в handle_take: {e}")
        bot.reply_to(message, "? Произошла ошибка при изъятии Zеток")
@bot.message_handler(commands=['stats'])
def handle_stats(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        users_count = len(user_balances)
        total_leaves = sum(u['leaves'] for u in user_balances.values())
        total_tea = sum(u['tea'] for u in user_balances.values())
        # Находим самых богатых пользователей
        sorted_by_leaves = sorted(user_balances.items(), key=lambda x: x[1]['leaves'], reverse=True)[:5]
        sorted_by_tea = sorted(user_balances.items(), key=lambda x: x[1]['tea'], reverse=True)[:5]
        response = (
            f"?? Подробная статистика бота\n\n"
            f"?? Всего пользователей: {users_count}\n"
            f"?? Всего Zеток: {total_leaves}\n"
            f"?? Всего территорий: {total_tea}\n\n"
            f"?? Топ-5 по Zетоку:\n"
        )
        for i, (user_id, data) in enumerate(sorted_by_leaves, 1):
            try:
                user = bot.get_chat(user_id)
                response += f"{i}. {user.first_name}: {data['leaves']} ??\n"
            except:
                continue
        response += f"\n?? Топ-5 по территориям:\n"
        for i, (user_id, data) in enumerate(sorted_by_tea, 1):
            try:
                user = bot.get_chat(user_id)
                response += f"{i}. {user.first_name}: {data['tea']} ??\n"
            except:
                continue
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_stats: {e}")
        bot.reply_to(message, "? Произошла ошибка при получении статистики")
@bot.message_handler(commands=['announce'])
def handle_announce(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        announcement_text = message.text.replace('/announce', '', 1).strip()
        if not announcement_text:
            bot.reply_to(message, "? Укажите текст объявления!")
            return
        success_count = 0
        fail_count = 0
        for user_id in user_balances.keys():
            try:
                bot.send_message(user_id,
                    f"?? Объявление от администрации:\n\n"
                    f"{announcement_text}")
                success_count += 1
            except:
                fail_count += 1
                continue
        bot.reply_to(message,
            f"? Объявление отправлено!\n"
            f"Успешно: {success_count}\n"
            f"Не доставлено: {fail_count}")
    except Exception as e:
        print(f"Ошибка в handle_announce: {e}")
        bot.reply_to(message, "? Произошла ошибка при отправке объявления")
@bot.message_handler(commands=['reset'])
def handle_reset(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "? Используйте: /reset @username")
            return
        recipient_username = command_parts[1].lstrip('@')
        # Поиск пользователя
        recipient_found = False
        for user_id in user_balances.keys():
            try:
                user_info = bot.get_chat(user_id)
                if user_info.username and user_info.username.lower() == recipient_username.lower():
                    recipient_id = user_id
                    recipient_name = user_info.first_name
                    recipient_found = True
                    break
            except:
                continue
        if not recipient_found:
            bot.reply_to(message, "? Пользователь не найден!")
            return
        # Сбрасываем таймер
        user_balances[recipient_id]['last_farm'] = 0
        save_user_data()
        bot.reply_to(message, f"? Таймер сбора для {recipient_name} сброшен!")
        bot.send_message(recipient_id, "?? Администратор сбросил ваш таймер сбора!\nВы можете собирать Zетки!")
    except Exception as e:
        print(f"Ошибка в handle_reset: {e}")
        bot.reply_to(message, "? Произошла ошибка при сбросе таймера")
@bot.message_handler(commands=['warn'])
def handle_warn(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        command_parts = message.text.split()
        if len(command_parts) < 3:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /warn @username причина")
            return
        recipient_username = command_parts[1].lstrip('@')
        warn_reason = ' '.join(command_parts[2:])
        # Поиск пользователя
        recipient_found = False
        for user_id in user_balances.keys():
            try:
                user_info = bot.get_chat(user_id)
                if user_info.username and user_info.username.lower() == recipient_username.lower():
                    recipient_id = user_id
                    recipient_name = user_info.first_name
                    recipient_found = True
                    break
            except:
                continue
        if not recipient_found:
            bot.reply_to(message, "? Пользователь не найден!")
            return
        init_user_data(recipient_id)
        check_warnings(recipient_id)  # Очищаем устаревшие предупреждения
        # Добавляем предупреждение
        warning = {
            'reason': warn_reason,
            'time': datetime.datetime.now().timestamp(),
            'admin': message.from_user.first_name
        }
        if 'warnings' not in user_balances[recipient_id]:
            user_balances[recipient_id]['warnings'] = []
        user_balances[recipient_id]['warnings'].append(warning)
        save_user_data()
        warnings_count = len(user_balances[recipient_id]['warnings'])
        response = (
            f"?? Выдано предупреждение пользователю {recipient_name}!\n"
            f"Причина: {warn_reason}\n"
            f"Всего предупреждений: {warnings_count}/{MAX_WARNINGS}\n"
            f"Предупреждение будет снято через 7 дней"
        )
        if warnings_count >= MAX_WARNINGS:
            response += f"\n\n?? Пользователь автоматически заблокирован за {MAX_WARNINGS} предупреждений!"
        bot.reply_to(message, response)
        bot.send_message(recipient_id,
            f"?? Вы получили предупреждение!\n"
            f"Причина: {warn_reason}\n"
            f"Всего предупреждений: {warnings_count}/{MAX_WARNINGS}\n"
            f"Предупреждение будет снято через 7 дней")
    except Exception as e:
        print(f"Ошибка в handle_warn: {e}")
        bot.reply_to(message, "? Произошла ошибка при выдаче предупреждения")
@bot.message_handler(commands=['ban'])
def handle_ban(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        command_parts = message.text.split()
        if len(command_parts) < 3:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /ban @username причина")
            return
        recipient_username = command_parts[1].lstrip('@')
        ban_reason = ' '.join(command_parts[2:])
        # Поиск пользователя
        recipient_found = False
        for user_id in user_balances.keys():
            try:
                user_info = bot.get_chat(user_id)
                if user_info.username and user_info.username.lower() == recipient_username.lower():
                    recipient_id = user_id
                    recipient_name = user_info.first_name
                    recipient_found = True
                    break
            except:
                continue
        if not recipient_found:
            bot.reply_to(message, "? Пользователь не найден!")
            return
        init_user_data(recipient_id)
        # Блокируем пользователя
        user_balances[recipient_id]['banned'] = True
        user_balances[recipient_id]['ban_reason'] = ban_reason
        save_user_data()
        bot.reply_to(message,
            f"?? Пользователь {recipient_name} заблокирован!\n"
            f"Причина: {ban_reason}")
        bot.send_message(recipient_id,
            f"?? Вы были заблокированы!\n"
            f"Причина: {ban_reason}")
    except Exception as e:
        print(f"Ошибка в handle_ban: {e}")
        bot.reply_to(message, "? Произошла ошибка при блокировке пользователя")
@bot.message_handler(commands=['unwarn'])
def handle_unwarn(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /unwarn @username")
            return
        recipient_username = command_parts[1].lstrip('@')
        # Поиск пользователя
        recipient_found = False
        for user_id in user_balances.keys():
            try:
                user_info = bot.get_chat(user_id)
                if user_info.username and user_info.username.lower() == recipient_username.lower():
                    recipient_id = user_id
                    recipient_name = user_info.first_name
                    recipient_found = True
                    break
            except:
                continue
        if not recipient_found:
            bot.reply_to(message, "? Пользователь не найден!")
            return
        init_user_data(recipient_id)
        check_warnings(recipient_id)  # Очищаем устаревшие предупреждения
        if not user_balances[recipient_id].get('warnings', []):
            bot.reply_to(message, f"? У пользователя {recipient_name} нет активных предупреждений!")
            return
        # Снимаем последнее предупреждение
        user_balances[recipient_id]['warnings'].pop()
        save_user_data()
        warnings_count = len(user_balances[recipient_id]['warnings'])
        bot.reply_to(message,
            f"? Снято предупреждение у пользователя {recipient_name}!\n"
            f"Осталось предупреждений: {warnings_count}")
        bot.send_message(recipient_id,
            f"? Администратор снял с вас одно предупреждение!\n"
            f"Осталось предупреждений: {warnings_count}")
    except Exception as e:
        print(f"Ошибка в handle_unwarn: {e}")
        bot.reply_to(message, "? Произошла ошибка при снятии предупреждения")
@bot.message_handler(commands=['unban'])
def handle_unban(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? У вас нет прав для использования этой команды!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /unban @username")
            return
        recipient_username = command_parts[1].lstrip('@')
        # Поиск пользователя
        recipient_found = False
        for user_id in user_balances.keys():
            try:
                user_info = bot.get_chat(user_id)
                if user_info.username and user_info.username.lower() == recipient_username.lower():
                    recipient_id = user_id
                    recipient_name = user_info.first_name
                    recipient_found = True
                    break
            except:
                continue
        if not recipient_found:
            bot.reply_to(message, "? Пользователь не найден!")
            return
        init_user_data(recipient_id)
        # Проверяем, забанен ли пользователь
        if not user_balances[recipient_id].get('banned', False):
            bot.reply_to(message, f"? Пользователь {recipient_name} не заблокирован!")
            return
        # Разблокируем пользователя
        user_balances[recipient_id]['banned'] = False
        user_balances[recipient_id]['ban_reason'] = ''
        user_balances[recipient_id]['warnings'] = []  # Очищаем все предупреждения
        save_user_data()
        bot.reply_to(message,
            f"? Пользователь {recipient_name} разблокирован!\n"
            f"Все предупреждения сняты.")
        bot.send_message(recipient_id,
            "?? Ваш аккаунт разблокирован!\n"
            "Все предупреждения сняты.\n"
            "Теперь вы снова можете пользоваться ботом.")
    except Exception as e:
        print(f"Ошибка в handle_unban: {e}")
        bot.reply_to(message, "? Произошла ошибка при разблокировке пользователя")
@bot.message_handler(commands=['clan'])
@group_only
def handle_clan(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        # Если у пользователя нет клана
        if not user_balances[user_id]['clan']:
            response = (
                f"?? Система кланов\n\n"
                f"Вы не состоите в клане.\n"
                f"Доступные действия:\n"
                f"• /clan_create [название] - создать клан ({CLAN_PRICE} Zеток)\n"
                f"• /clan_join [название] - вступить в клан\n"
                f"• /clan_list - список кланов\n\n"
                f"? Используйте /clan_help для подробной информации о системе кланов"
            )
        else:
            clan_id = user_balances[user_id]['clan']
            clan = clans[clan_id]
            role = user_balances[user_id]['clan_role']
            members = [uid for uid, data in user_balances.items() if data.get('clan') == clan_id]
            response = (
                f"?? Клан «{clan['name']}»\n\n"
                f"👑 Лидер: {get_username(clan['leader'])}\n"
                f"👤 Участников: {len(members)}\n"
                f"?? Ваша роль: {get_role_name(role)}\n\n"
            )
            if role in ['leader', 'officer']:
                response += (
                    f"Команды управления:\n"
                    f"• /clan_invite @username - пригласить игрока\n"
                    f"• /clan_kick @username - исключить игрока\n"
                    f"• /clan_promote @username - повысить до офицера\n"
                    f"• /clan_demote @username - понизить до участника\n"
                )
            response += (
                f"\nОбщие команды:\n"
                f"• /clan_members - список участников\n"
                f"• /clan_leave - покинуть клан"
            )
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_clan: {e}")
        bot.reply_to(message, "? Произошла ошибка при работе с кланом")
@bot.message_handler(commands=['clan_create'])
@group_only
def handle_clan_create(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        # Проверяем, не состоит ли уже в клане
        if user_balances[user_id]['clan']:
            bot.reply_to(message, "? Вы уже состоите в клане!")
            return
        # Проверяем формат команды
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Укажите название клана!\n"
                "Использование: /clan_create [название]")
            return
        clan_name = command_parts[1].strip()
        # Проверяем длину названия
        if len(clan_name) < MIN_CLAN_NAME_LENGTH or len(clan_name) > MAX_CLAN_NAME_LENGTH:
            bot.reply_to(message,
                f"? Название клана должно быть от {MIN_CLAN_NAME_LENGTH} "
                f"до {MAX_CLAN_NAME_LENGTH} символов!")
            return
        # Проверяем, не существует ли клан с таким названием
        if any(c['name'].lower() == clan_name.lower() for c in clans.values()):
            bot.reply_to(message, "? Клан с таким названием уже существует!")
            return
        # Проверяем наличие Zеток
        if user_balances[user_id]['leaves'] < CLAN_PRICE:
            bot.reply_to(message,
                f"? Недостаточно Zеток для создания клана!\n"
                f"Необходимо: {CLAN_PRICE} Zеток\n"
                f"У вас есть: {user_balances[user_id]['leaves']} Zеток")
            return
        # Создаем клан
        clan_id = str(len(clans) + 1)
        clans[clan_id] = {
            'name': clan_name,
            'leader': user_id,
            'created_at': datetime.datetime.now().timestamp()
        }
        # Обновляем данные пользователя
        user_balances[user_id]['leaves'] -= CLAN_PRICE
        user_balances[user_id]['clan'] = clan_id
        user_balances[user_id]['clan_role'] = 'leader'
        save_user_data()
        save_clans_data()
        bot.reply_to(message,
            f"?? Поздравляем! Клан «{clan_name}» успешно создан!\n"
            f"Потрачено: {CLAN_PRICE} Zеток\n\n"
            f"Используйте /clan для управления кланом")
    except Exception as e:
        print(f"Ошибка в handle_clan_create: {e}")
        bot.reply_to(message, "? Произошла ошибка при создании клана")
@bot.message_handler(commands=['clan_help'])
@group_only
def handle_clan_help(message: Message):
    help_text = (
        f"?? Руководство по системе кланов\n\n"
        f"?? Основные команды:\n"
        f"• /clan - просмотр информации о клане\n"
        f"• /clan_create [название] - создать клан ({CLAN_PRICE} Zеток)\n"
        f"• /clan_list - список всех кланов\n"
        f"• /clan_join [название] - вступить в клан\n"
        f"• /clan_leave - покинуть клан\n"
        f"• /clan_members - список участников клана\n\n"
        f"?? Команды управления (для лидера и офицеров):\n"
        f"• /clan_invite @username - пригласить игрока\n"
        f"• /clan_kick @username - исключить игрока\n"
        f"• /clan_promote @username - повысить до офицера\n"
        f"• /clan_demote @username - понизить до участника\n\n"
        f"?? Роли в клане:\n"
        f"• 👑 Лидер - создатель клана, полный доступ\n"
        f"• 🛡️ Офицер - может управлять участниками\n"
        f"• 👤 Участник - базовый доступ\n\n"
        f"? Как вступить в клан:\n"
        f"1. Посмотрите список кланов: /clan_list\n"
        f"2. Подайте заявку: /clan_join [название]\n"
        f"3. Дождитесь одобрения от лидера/офицера\n\n"
        f"? Как создать свой клан:\n"
        f"1. Накопите {CLAN_PRICE} Zеток\n"
        f"2. Придумайте название (от {MIN_CLAN_NAME_LENGTH} до {MAX_CLAN_NAME_LENGTH} символов)\n"
        f"3. Создайте клан: /clan_create [название]"
    )
    bot.reply_to(message, help_text)
@bot.message_handler(commands=['clan_invite'])
@group_only
def handle_clan_invite(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        # Проверяем, состоит ли пользователь в клане
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "? Вы не состоите в клане!")
            return
        # Проверяем права пользователя
        user_role = user_balances[user_id]['clan_role']
        if user_role not in ['leader', 'officer']:
            bot.reply_to(message, "? У вас нет прав для приглашения игроков!")
            return
        # Проверяем формат команды
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /clan_invite @username")
            return
        target_username = command_parts[1].lstrip('@')
        # Ищем пользователя
        target_found = False
        for uid in user_balances.keys():
            try:
                user_info = bot.get_chat(uid)
                if user_info.username and user_info.username.lower() == target_username.lower():
                    target_id = uid
                    target_name = user_info.first_name
                    target_found = True
                    break
            except:
                continue
        if not target_found:
            bot.reply_to(message, "? Пользователь не найден!")
            return
        # Проверяем, не состоит ли уже в клане
        if user_balances[target_id]['clan']:
            bot.reply_to(message, "? Этот игрок уже состоит в клане!")
            return
        # Добавляем в клан
        clan_id = user_balances[user_id]['clan']
        user_balances[target_id]['clan'] = clan_id
        user_balances[target_id]['clan_role'] = 'member'
        save_user_data()
        clan_name = clans[clan_id]['name']
        bot.reply_to(message,
            f"? Игрок {target_name} успешно приглашён в клан!")
        bot.send_message(target_id,
            f"?? Вас пригласили в клан «{clan_name}»!\n"
            f"Используйте /clan для просмотра информации")
    except Exception as e:
        print(f"Ошибка в handle_clan_invite: {e}")
        bot.reply_to(message, "? Произошла ошибка при приглашении игрока")
@bot.message_handler(commands=['clan_kick'])
@group_only
def handle_clan_kick(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        # Проверяем, состоит ли пользователь в клане
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "? Вы не состоите в клане!")
            return
        # Проверяем права пользователя
        user_role = user_balances[user_id]['clan_role']
        if user_role not in ['leader', 'officer']:
            bot.reply_to(message, "? У вас нет прав для исключения игроков!")
            return
        # Проверяем формат команды
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /clan_kick @username")
            return
        target_username = command_parts[1].lstrip('@')
        # Ищем пользователя
        target_found = False
        for uid in user_balances.keys():
            try:
                user_info = bot.get_chat(uid)
                if user_info.username and user_info.username.lower() == target_username.lower():
                    target_id = uid
                    target_name = user_info.first_name
                    target_found = True
                    break
            except:
                continue
        if not target_found:
            bot.reply_to(message, "? Пользователь не найден!")
            return
        # Проверяем, состоит ли игрок в том же клане
        clan_id = user_balances[user_id]['clan']
        if user_balances[target_id].get('clan') != clan_id:
            bot.reply_to(message, "? Этот игрок не состоит в вашем клане!")
            return
        # Проверяем, не пытается ли офицер исключить лидера или другого офицера
        if user_role == 'officer' and user_balances[target_id]['clan_role'] in ['leader', 'officer']:
            bot.reply_to(message, "? Вы не можете исключить лидера или офицера!")
            return
        # Исключаем игрока
        user_balances[target_id]['clan'] = None
        user_balances[target_id]['clan_role'] = None
        save_user_data()
        bot.reply_to(message, f"? Игрок {target_name} исключён из клана!")
        bot.send_message(target_id, f"? Вы были исключены из клана!")
    except Exception as e:
        print(f"Ошибка в handle_clan_kick: {e}")
        bot.reply_to(message, "? Произошла ошибка при исключении игрока")
@bot.message_handler(commands=['clan_promote'])
@group_only
def handle_clan_promote(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        # Проверяем, состоит ли пользователь в клане
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "? Вы не состоите в клане!")
            return
        # Только лидер может повышать
        if user_balances[user_id]['clan_role'] != 'leader':
            bot.reply_to(message, "? Только лидер клана может повышать участников!")
            return
        # Проверяем формат команды
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /clan_promote @username")
            return
        target_username = command_parts[1].lstrip('@')
        # Ищем пользователя
        target_found = False
        for uid in user_balances.keys():
            try:
                user_info = bot.get_chat(uid)
                if user_info.username and user_info.username.lower() == target_username.lower():
                    target_id = uid
                    target_name = user_info.first_name
                    target_found = True
                    break
            except:
                continue
        if not target_found:
            bot.reply_to(message, "? Пользователь не найден!")
            return
        # Проверяем, состоит ли игрок в том же клане
        clan_id = user_balances[user_id]['clan']
        if user_balances[target_id].get('clan') != clan_id:
            bot.reply_to(message, "? Этот игрок не состоит в вашем клане!")
            return
        # Проверяем текущую роль
        if user_balances[target_id]['clan_role'] == 'officer':
            bot.reply_to(message, "? Этот игрок уже является офицером!")
            return
        # Повышаем до офицера
        user_balances[target_id]['clan_role'] = 'officer'
        save_user_data()
        bot.reply_to(message, f"? Игрок {target_name} повышен до офицера!")
        bot.send_message(target_id, "?? Поздравляем! Вы повышены до офицера клана!")
    except Exception as e:
        print(f"Ошибка в handle_clan_promote: {e}")
        bot.reply_to(message, "? Произошла ошибка при повышении игрока")
@bot.message_handler(commands=['clan_demote'])
@group_only
def handle_clan_demote(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        # Проверяем, состоит ли пользователь в клане
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "? Вы не состоите в клане!")
            return
        # Только лидер может понижать
        if user_balances[user_id]['clan_role'] != 'leader':
            bot.reply_to(message, "? Только лидер клана может понижать офицеров!")
            return
        # Проверяем формат команды
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /clan_demote @username")
            return
        target_username = command_parts[1].lstrip('@')
        # Ищем пользователя
        target_found = False
        for uid in user_balances.keys():
            try:
                user_info = bot.get_chat(uid)
                if user_info.username and user_info.username.lower() == target_username.lower():
                    target_id = uid
                    target_name = user_info.first_name
                    target_found = True
                    break
            except:
                continue
        if not target_found:
            bot.reply_to(message, "? Пользователь не найден!")
            return
        # Проверяем, состоит ли игрок в том же клане
        clan_id = user_balances[user_id]['clan']
        if user_balances[target_id].get('clan') != clan_id:
            bot.reply_to(message, "? Этот игрок не состоит в вашем клане!")
            return
        # Проверяем текущую роль
        if user_balances[target_id]['clan_role'] != 'officer':
            bot.reply_to(message, "? Этот игрок не является офицером!")
            return
        # Понижаем до участника
        user_balances[target_id]['clan_role'] = 'member'
        save_user_data()
        bot.reply_to(message, f"? Игрок {target_name} понижен до участника!")
        bot.send_message(target_id, "?? Вы понижены до обычного участника клана")
    except Exception as e:
        print(f"Ошибка в handle_clan_demote: {e}")
        bot.reply_to(message, "? Произошла ошибка при понижении игрока")
@bot.message_handler(commands=['clan_members'])
@group_only
def handle_clan_members(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        # Проверяем, состоит ли пользователь в клане
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "? Вы не состоите в клане!")
            return
        clan_id = user_balances[user_id]['clan']
        clan = clans[clan_id]
        # Собираем список участников
        members = []
        for uid, data in user_balances.items():
            if data.get('clan') == clan_id:
                role = get_role_name(data['clan_role'])
                try:
                    username = bot.get_chat(uid).first_name
                    members.append((role, username))
                except:
                    continue
        # Сортируем по ролям: лидер -> офицеры -> участники
        role_priority = {'👑 Лидер': 0, '🛡️ Офицер': 1, '👤 Участник': 2}
        members.sort(key=lambda x: role_priority[x[0]])
        response = f"👤 Участники клана «{clan['name']}»:\n\n"
        for role, username in members:
            response += f"{role}: {username}\n"
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_clan_members: {e}")
        bot.reply_to(message, "? Произошла ошибка при получении списка участников")
@bot.message_handler(commands=['clan_leave'])
@group_only
def handle_clan_leave(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        # Проверяем, состоит ли пользователь в клане
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "? Вы не состоите в клане!")
            return
        clan_id = user_balances[user_id]['clan']
        clan_name = clans[clan_id]['name']
        # Проверяем, не является ли пользователь лидером
        if user_balances[user_id]['clan_role'] == 'leader':
            # Ищем офицера для передачи лидерства
            new_leader = None
            for uid, data in user_balances.items():
                if data.get('clan') == clan_id and data['clan_role'] == 'officer':
                    new_leader = uid
                    break
            if new_leader:
                # Передаем лидерство офицеру
                user_balances[new_leader]['clan_role'] = 'leader'
                clans[clan_id]['leader'] = new_leader
                save_clans_data()
                try:
                    bot.send_message(new_leader,
                        f"?? Вы стали новым лидером клана «{clan_name}»!")
                except:
                    pass
            else:
                # Если нет офицеров, удаляем клан
                del clans[clan_id]
                save_clans_data()
                # Убираем клан у всех участников
                for uid, data in user_balances.items():
                    if data.get('clan') == clan_id:
                        data['clan'] = None
                        data['clan_role'] = None
                        try:
                            if uid != user_id:
                                bot.send_message(uid,
                                    f"? Клан «{clan_name}» был расформирован!")
                        except:
                            continue
                save_user_data()
                bot.reply_to(message,
                    f"? Клан «{clan_name}» расформирован, так как вы были последним офицером!")
                return
        # Покидаем клан
        user_balances[user_id]['clan'] = None
        user_balances[user_id]['clan_role'] = None
        save_user_data()
        bot.reply_to(message, f"? Вы покинули клан «{clan_name}»")
    except Exception as e:
        print(f"Ошибка в handle_clan_leave: {e}")
        bot.reply_to(message, "? Произошла ошибка при выходе из клана")
@bot.message_handler(commands=['clan_list'])
@group_only
def handle_clan_list(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        if not clans:
            bot.reply_to(message, "? Пока нет ни одного клана!")
            return
        response = "?? Список кланов:\n\n"
        for clan_id, clan_data in clans.items():
            # Считаем количество участников
            members_count = sum(1 for data in user_balances.values()
                              if data.get('clan') == clan_id)
            # Получаем имя лидера
            leader_name = get_username(clan_data['leader'])
            response += (
                f"?? «{clan_data['name']}»\n"
                f"👑 Лидер: {leader_name}\n"
                f"👤 Участников: {members_count}\n\n"
            )
        response += "Чтобы вступить в клан, используйте:\n/clan_join [название]"
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_clan_list: {e}")
        bot.reply_to(message, "? Произошла ошибка при получении списка кланов")
@bot.message_handler(commands=['clan_join'])
@group_only
def handle_clan_join(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        # Проверяем, не состоит ли уже в клане
        if user_balances[user_id]['clan']:
            bot.reply_to(message, "? Вы уже состоите в клане!")
            return
        # Проверяем формат команды
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Укажите название клана!\n"
                "Использование: /clan_join [название]")
            return
        clan_name = command_parts[1].strip()
        # Выводим отладочную информацию
        print(f"Поиск клана: {clan_name}")
        print(f"Доступные кланы: {clans}")
        # Ищем клан по названию (без учета регистра)
        clan_found = False
        for clan_id, clan_data in clans.items():
            print(f"Сравниваем с: {clan_data['name']}")
            if clan_data['name'].lower() == clan_name.lower():
                clan_found = True
                print(f"Клан найден! ID: {clan_id}")
                # Добавляем пользователя в клан
                user_balances[user_id]['clan'] = clan_id
                user_balances[user_id]['clan_role'] = 'member'
                save_user_data()
                # Уведомляем лидера
                try:
                    leader_id = clan_data['leader']
                    bot.send_message(leader_id,
                        f"?? {message.from_user.first_name} присоединился к клану!")
                except Exception as e:
                    print(f"Ошибка при уведомлении лидера: {e}")
                bot.reply_to(message,
                    f"? Вы успешно вступили в клан «{clan_data['name']}»!\n"
                    f"Используйте /clan для просмотра информации")
                break
        if not clan_found:
            bot.reply_to(message,
                "? Клан с таким названием не найден!\n"
                "Используйте /clan_list для просмотра списка кланов")
    except Exception as e:
        print(f"Ошибка в handle_clan_join: {e}")
        bot.reply_to(message, "? Произошла ошибка при вступлении в клан")
# Вспомогательные функции
def get_username(user_id):
    try:
        user = bot.get_chat(user_id)
        return user.first_name
    except:
        return "Неизвестный"
def get_role_name(role):
    return {
        'leader': '👑 Лидер',
        'officer': '🛡️ Офицер',
        'member': '👤 Участник'
    }.get(role, '? Неизвестно')
@bot.message_handler(commands=['shop'])
@group_only
def handle_shop(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        response = "?? Магазин предметов\n\n"
        for item in SHOP_ITEMS.values():
            response += (
                f"{item['name']}\n"
                f"?? {item['description']}\n"
                f"?? Цена: {item['price']} Zеток\n"
                f"?? Для покупки: /buy {item['id']}\n\n"
            )
        response += (
            f"У вас: {user_balances[user_id]['leaves']} Zеток\n"
            f"Максимум предметов: 3\n"
            f"Ваши предметы: /inventory\n\n"
            f"?? NFT коллекция\n"
            f"?? Базовая цена: {NFT_BASE_PRICE} Zеток\n"
            f"?? Посмотреть NFT: /nft_list\n"
            f"?? Купить NFT: /buy_nft [id]\n\n"
        )
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_shop: {e}")
        bot.reply_to(message, "? Произошла ошибка при открытии магазина")
@bot.message_handler(commands=['buy'])
@group_only
def handle_buy(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /buy [id_предмета]")
            return
        item_id = command_parts[1].lower()
        if item_id not in SHOP_ITEMS:
            bot.reply_to(message, "? Предмет не найден!")
            return
        item = SHOP_ITEMS[item_id]
        # Проверяем количество предметов
        if len(user_balances[user_id]['items']) >= 3:
            bot.reply_to(message,
                "? У вас уже максимальное количество предметов!\n"
                "Используйте /inventory для просмотра и /drop [id_предмета] для удаления")
            return
        # Проверяем, есть ли уже такой предмет
        if item_id in user_balances[user_id]['items']:
            bot.reply_to(message, "? У вас уже есть этот предмет!")
            return
        # Проверяем наличие Zеток
        if user_balances[user_id]['leaves'] < item['price']:
            bot.reply_to(message,
                f"? Недостаточно Zеток!\n"
                f"Необходимо: {item['price']} Zеток\n"
                f"У вас есть: {user_balances[user_id]['leaves']} Zеток")
            return
        # Покупаем предмет
        user_balances[user_id]['leaves'] -= item['price']
        user_balances[user_id]['items'].append(item_id)
        save_user_data()
        bot.reply_to(message,
            f"? Вы успешно приобрели {item['name']}!\n"
            f"Осталось территорий: {user_balances[user_id]['leaves']} Zеток")
    except Exception as e:
        print(f"Ошибка в handle_buy: {e}")
        bot.reply_to(message, "? Произошла ошибка при покупке предмета")
@bot.message_handler(commands=['inventory'])
@group_only
def handle_inventory(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        items = user_balances[user_id]['items']
        if not items:
            bot.reply_to(message,
                "?? Ваш инвентарь пуст!\n"
                "Используйте /shop для покупки предметов")
            return
        response = "?? Ваш инвентарь:\n\n"
        for item_id in items:
            item = SHOP_ITEMS[item_id]
            response += (
                f"{item['name']}\n"
                f"?? {item['description']}\n"
                f"? Для удаления: /drop {item_id}\n\n"
            )
        response += f"Всего предметов: {len(items)}/3"
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_inventory: {e}")
        bot.reply_to(message, "? Произошла ошибка при открытии инвентаря")
@bot.message_handler(commands=['drop'])
@group_only
def handle_drop(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Неверный формат команды!\n"
                "Используйте: /drop [id_предмета]")
            return
        item_id = command_parts[1].lower()
        if item_id not in SHOP_ITEMS:
            bot.reply_to(message, "? Предмет не найден!")
            return
        if item_id not in user_balances[user_id]['items']:
            bot.reply_to(message, "? У вас нет этого предмета!")
            return
        # Удаляем предмет
        user_balances[user_id]['items'].remove(item_id)
        save_user_data()
        bot.reply_to(message,
            f"? Вы выбросили {SHOP_ITEMS[item_id]['name']}")
    except Exception as e:
        print(f"Ошибка в handle_drop: {e}")
        bot.reply_to(message, "? Произошла ошибка при удалении предмета")
if __name__ == '__main__':
    print("Бот запущен...")
    event_thread = threading.Thread(target=check_event_end, daemon=True)
    event_thread.start()
    bot.infinity_polling()
