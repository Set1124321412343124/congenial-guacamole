import telebot
import random
import os
from telebot.types import Message
import datetime
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

CLAN_PRICE = 100
MIN_CLAN_NAME_LENGTH = 3
MAX_CLAN_NAME_LENGTH = 20
NFT_BASE_PRICE = 1000
ALLOWED_GROUP_ID = -1002966537381
CHANNEL_ID = -1002966537381
HALLOWEEN_EVENT_ACTIVE = False
HALLOWEEN_END_TIME = 1762635600
KILL_COOLDOWN = 2 * 60 * 60
KILL_BAN_DURATION = 2 * 60 * 60
MARKET_TAX_PERCENT = 10
MARKET_MIN_PRICE = 10
MARKET_MAX_DURATION = 7 * 24 * 60 * 60

market_listings = {}
user_nfts = {}
promo_codes = {}
clans = {}
user_balances = {}

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

ADMIN_IDS = [6413063320, 6950398294]

# ==================== ЗАГЛУШКИ ВМЕСТО СОХРАНЕНИЯ ====================
def save_user_data():    pass
def save_clans_data():   pass
def save_promo_data():   pass
def save_nft_data():     pass
def save_market_data():  pass

SHOP_ITEMS = {
    'gold_rise': {'id': 'gold_rise', 'name': '🪙 Золотой червонец', 'description': 'Легендарный предмет. +100% к зарплате', 'price': 5000, 'bonus_type': 'farm', 'bonus_value': 10.0},
    'halloween_pumpkin': {'id': 'halloween_pumpkin', 'name': '🎃 Тыква губернатора', 'description': 'Ивентный предмет. +100% к зарплате', 'price': 150, 'bonus_type': 'farm', 'bonus_value': 1.5},
    'watermelon': {'id': 'watermelon', 'name': '🍉 Священный арбуз', 'description': 'Священный плод полуострова. +50% к зарплате', 'price': 1000, 'bonus_type': 'farm', 'bonus_value': 0.5},
    'dragon': {'id': 'dragon', 'name': '🐉 Китайский дракон', 'description': 'Мифическое существо. +50% к зарплате', 'price': 2000, 'bonus_type': 'farm', 'bonus_value': 0.5},
    'scissors': {'id': 'scissors', 'name': '🔪 Священный серп', 'description': 'Оружие трудовиков. +30% к зарплате', 'price': 700, 'bonus_type': 'farm', 'bonus_value': 0.3},
    'watering_can': {'id': 'watering_can', 'name': '🌱 Царская поливалка', 'description': 'Для полива полей. +20% к зарплате', 'price': 500, 'bonus_type': 'farm', 'bonus_value': 0.2},
    'defender_medal': {'id': 'defender_medal', 'name': '🎖️ Медаль защитника Полуострова', 'description': 'За охрану рубежей. +35% к зарплате', 'price': 1500, 'bonus_type': 'farm', 'bonus_value': 0.35},
    'governor_seal': {'id': 'governor_seal', 'name': '👑 Печать губернатора', 'description': 'Документ власти. +25% к зарплате', 'price': 1200, 'bonus_type': 'farm', 'bonus_value': 0.25},
    'border_flask': {'id': 'border_flask', 'name': '🥃 Фляга пограничника', 'description': 'Поднимает дух. +15% к зарплате', 'price': 350, 'bonus_type': 'farm', 'bonus_value': 0.15},
    'june_sky': {'id': 'june_sky', 'name': '☁️ Ломтик июльского неба', 'description': 'Природа крымская. +10% к зарплате', 'price': 200, 'bonus_type': 'farm', 'bonus_value': 0.1},
    'sharf': {'id': 'sharf', 'name': '🧣 Шарф ополченца', 'description': 'Теплый, но безполезный. Бонусов нет', 'price': 10, 'bonus_type': 'farm', 'bonus_value': 2.0},
    'jade_rod': {'id': 'jade_rod', 'name': '💊 Нефритовый стержень', 'description': 'Экономит 20 Zеток на крафте', 'price': 800, 'bonus_type': 'craft', 'bonus_value': 20},
    'teapot': {'id': 'teapot', 'name': '🫖 Чайник губернатора', 'description': 'Экономит 10 Zеток на крафте', 'price': 400, 'bonus_type': 'craft', 'bonus_value': 10},
    'crimean_ticket': {'id': 'crimean_ticket', 'name': '🎫 Билет в Крымский театр', 'description': 'Экономит 15 Zеток на крафте', 'price': 600, 'bonus_type': 'craft', 'bonus_value': 15},
    'scroll': {'id': 'scroll', 'name': '📜 Свиток мудрости', 'description': 'Уменьшает время фарма на 10 минут', 'price': 1500, 'bonus_type': 'time', 'bonus_value': 600},
}

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
                    f"Спасибо всем за участие!")
            except:
                continue

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

def init_user_data(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = {
            'leaves': 0, 'tea': 0, 'last_farm': 0, 'warnings': [], 'banned': False,
            'ban_reason': '', 'clan': None, 'clan_role': None, 'items': [],
            'custom_work': [], 'used_promos': [], 'nfts': [], 'pumpkins': 0,
            'kills': 0, 'killed_by': None, 'kill_ban_until': 0, 'last_kill_time': 0,
            'daily_streak': 0, 'daily_last': 0, 'daily_wins_today': 0,
            'daily_wins_reset': 0, 'missions': [], 'missions_date': ''
        }
    else:
        d = user_balances[user_id]
        defaults = {
            'used_promos': [], 'nfts': [], 'pumpkins': 0, 'kills': 0,
            'killed_by': None, 'kill_ban_until': 0, 'last_kill_time': 0,
            'daily_streak': 0, 'daily_last': 0, 'daily_wins_today': 0,
            'daily_wins_reset': 0, 'missions': [], 'missions_date': '',
            'last_farm': 0, 'warnings': [], 'banned': False, 'ban_reason': '',
            'clan': None, 'clan_role': None, 'items': [], 'custom_work': []
        }
        for k, v in defaults.items():
            if k not in d:
                d[k] = v

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

def market_cleanup_worker():
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

def check_warnings(user_id):
    if 'warnings' not in user_balances[user_id]:
        return
    current_time = datetime.datetime.now().timestamp()
    active_warnings = []
    for warning in user_balances[user_id]['warnings']:
        if current_time - warning['time'] < WARNING_DURATION:
            active_warnings.append(warning)
    user_balances[user_id]['warnings'] = active_warnings
    if len(active_warnings) >= MAX_WARNINGS:
        user_balances[user_id]['banned'] = True
        user_balances[user_id]['ban_reason'] = f"Автоматическая блокировка за {MAX_WARNINGS} предупреждений"
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

event_thread = threading.Thread(target=check_event_end, daemon=True)
event_thread.start()

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def group_only(func):
    def wrapper(message):
        if message.chat.type == 'private':
            bot.reply_to(message,
                "📣 Бот работает только в группах!\n\n"
                "🔗 Для начала подпишитесь на наш канал:\n"
                "https://t.me/Potuzhiya\n\n"
                "После подписки добавьте бота в любую группу и используйте команды там.")
            return
        if not is_subscribed(message.from_user.id):
            bot.reply_to(message,
                "⚠️ Для использования бота подпишитесь на наш канал!\n\n"
                "🔗 https://t.me/Potuzhiya\n\n"
                "После подписки попробуйте снова.")
            return
        return func(message)
    return wrapper

# ==================== HANDLERS ====================

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
        f"⌛ /farmtime - время до следующего сбора\n"
        f"🔨 /craft [количество] - создать Флаг России(100 Zеток > 1 )\n"
        f"💰 /balance - проверить сокровищницу\n"
        f"📖 /me - свиток познания себя\n"
        f"\n\n🏪 Пользовательский рынок:\n"
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
def handle_price(message: Message):
    init_user_data(message.from_user.id)
    bot.reply_to(message,
        "Приветствую в магазине игровой валюты!\n"
        "Базовая стоимость:\n"
        "1💰 = 50 Zеток!\n"
        "1 звезда = 100 Zеток!\n"
        "По всем вопросам - владельцу(@alexey_navalyov_1976)")

@bot.message_handler(commands=['namaz'])
@group_only
def handle_namaz(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    bot.reply_to(message, "Вы быть признаны плохим Хохлом! -100 социального рейтинга!\n")
    user_balances[user_id]['leaves'] -= 100

@bot.message_handler(commands=['donate', 'don'])
@group_only
def handle_donate(message: Message):
    init_user_data(message.from_user.id)
    bot.reply_to(message, "КУПИТЬ РУБЛЯМИ - недоступно,положи мамену карточку")

@bot.message_handler(commands=['zov', 'z'])
@group_only
def handle_petya(message: Message):
    init_user_data(message.from_user.id)
    bot.reply_to(message, "поздняков гой")

@bot.message_handler(commands=['roblox', 'rb'])
@group_only
def handle_123(message: Message):
    init_user_data(message.from_user.id)
    bot.reply_to(message, "le le le")

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
            bot.reply_to(message, f"💀 Вы мертвы! Не можете фармить еще {hours}ч {minutes}м")
            return
        current_time = datetime.datetime.now().timestamp()
        last_farm = user_balances[user_id]['last_farm']
        if not can_farm(last_farm, user_id):
            time_until_next = 3600 - (current_time - last_farm)
            if 'scroll' in user_balances[user_id]['items']:
                time_until_next -= 600
            remaining_time = format_remaining_time(time_until_next)
            cooldown_message = random.choice(COOLDOWN_MESSAGES).format(time=remaining_time)
            bot.reply_to(message,
                f"{cooldown_message}\n\n"
                f"Текущий баланс:\n"
                f"Zеток: {user_balances[user_id]['leaves']}\n"
                f"🌿 Территории: {user_balances[user_id]['tea']}")
            return
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
        leaves_emoji = "🪙" * min(total_leaves, 20)
        response = (
            f"{farm_message}\n{leaves_emoji}\n\n"
            f"Баланс:\n"
            f"Zеток: {user_balances[user_id]['leaves']}\n"
            f"🌿 Территории: {user_balances[user_id]['tea']}\n"
        )
        response += f"\n\n⏳ Следующий сбор будет доступен через 1 час"
        if 'scroll' in user_balances[user_id]['items']:
            response = response.replace("1 час", "50 минут")
        bot.reply_to(message, response)
        track_mission(user_id, 'farm')
    except Exception as e:
        print(f"Общая ошибка в handle_farm: {e}")
        bot.reply_to(message, "❌ Произошла неизвестная ошибка. Попробуйте позже.")

@bot.message_handler(commands=['balance', 'b'])
@group_only
def handle_balance(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    ban_status = ""
    if user_balances[user_id].get('banned', False):
        ban_status = "\n\n🚫 Ваш аккаунт заблокирован!"
    bot.reply_to(message,
        f"Ваш баланс:\n"
        f"💰 Zеток: {user_balances[user_id]['leaves']}\n"
        f"🌿 Территории: {user_balances[user_id]['tea']}"
        f"{ban_status}")

@bot.message_handler(commands=['add_nft'])
def handle_add_nft(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "🚫 У вас нет прав для использования этой команды!")
            return
        if not message.reply_to_message or not message.reply_to_message.photo:
            bot.reply_to(message,
                "⚠️ Ответьте этой командой на сообщение с фотографией!\n"
                "Формат: /add_nft [описание] [редкость]\n"
                "Пример: /add_nft Редкий свиток мудрости rare")
            return
        command_parts = message.text.split(maxsplit=2)
        if len(command_parts) < 3:
            bot.reply_to(message,
                "⚠️ Неверный формат команды!\n"
                "Используйте: /add_nft [описание] [редкость]\n"
                "Редкости: common, rare, epic, legendary")
            return
        description = command_parts[1]
        rarity = command_parts[2].lower()
        if rarity not in ['common', 'rare', 'epic', 'legendary']:
            bot.reply_to(message, "❌ Неверная редкость!")
            return
        photo = message.reply_to_message.photo[-1]
        nft_id = len(user_nfts) + 1
        user_nfts[nft_id] = {
            'file_id': photo.file_id,
            'description': description,
            'rarity': rarity,
            'created_by': message.from_user.id,
            'created_at': datetime.datetime.now().timestamp(),
            'owner': None
        }
        bot.reply_to(message,
            f"✅ NFT успешно создан!\n\n"
            f"🔗 ID: {nft_id}\n"
            f"📝 Описание: {description}\n"
            f"⭐ Редкость: {rarity}")
    except Exception as e:
        print(f"Ошибка в handle_add_nft: {e}")

@bot.message_handler(commands=['give_nft'])
def handle_give_nft(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "🚫 У вас нет прав!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message, "⚠️ Используйте: /give_nft @username nft_id")
            return
        username = command_parts[1].lstrip('@')
        try:
            nft_id = int(command_parts[2])
        except ValueError:
            bot.reply_to(message, "❌ ID NFT должен быть числом!")
            return
        recipient_id = None
        recipient_name = None
        for user_id in user_balances.keys():
            try:
                user_info = bot.get_chat(user_id)
                if user_info.username and user_info.username.lower() == username.lower():
                    recipient_id = user_id
                    recipient_name = user_info.first_name
                    break
            except:
                continue
        if recipient_id is None:
            bot.reply_to(message, "❌ Пользователь не найден!")
            return
        if nft_id not in user_nfts:
            bot.reply_to(message, "❌ NFT с таким ID не существует!")
            return
        if user_nfts[nft_id]['owner'] is not None:
            bot.reply_to(message, "❌ Этот NFT уже принадлежит другому игроку!")
            return
        init_user_data(recipient_id)
        user_nfts[nft_id]['owner'] = recipient_id
        user_balances[recipient_id]['nfts'].append(nft_id)
        nft = user_nfts[nft_id]
        bot.reply_to(message, f"✅ NFT передан игроку {recipient_name}!")
        try:
            bot.send_photo(recipient_id, nft['file_id'],
                caption=f"🎁 Вы получили NFT!\n\n🎨 {nft['description']}\n🔗 ID: {nft_id}")
        except Exception as e:
            print(f"Ошибка при отправке NFT: {e}")
    except Exception as e:
        print(f"Ошибка в handle_give_nft: {e}")

@bot.message_handler(commands=['my_nfts'])
@group_only
def handle_my_nfts(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if check_ban(user_id, message):
        return
    nft_ids = user_balances[user_id].get('nfts', [])
    if not nft_ids:
        bot.reply_to(message, "📭 У вас пока нет NFT!")
        return
    response = "🖼️ Ваша коллекция NFT:\n\n"
    for nft_id in nft_ids:
        if nft_id in user_nfts:
            nft = user_nfts[nft_id]
            response += f"🎨 {nft_id}: {nft['description']}\n"
    bot.reply_to(message, response)

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
            bot.reply_to(message, "⚠️ Используйте: /buy_nft nft_id")
            return
        try:
            nft_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "❌ ID NFT должен быть числом!")
            return
        if nft_id not in user_nfts:
            bot.reply_to(message, "❌ NFT с таким ID не существует!")
            return
        nft = user_nfts[nft_id]
        if nft['owner'] is not None:
            bot.reply_to(message, "❌ Этот NFT уже принадлежит другому игроку!")
            return
        if user_balances[user_id]['leaves'] < NFT_BASE_PRICE:
            bot.reply_to(message, f"❌ Недостаточно Zеток! Нужно: {NFT_BASE_PRICE}")
            return
        user_balances[user_id]['leaves'] -= NFT_BASE_PRICE
        user_nfts[nft_id]['owner'] = user_id
        user_balances[user_id]['nfts'].append(nft_id)
        bot.reply_to(message, f"✅ Вы купили NFT!\n🎨 {nft['description']}")
        try:
            bot.send_photo(user_id, nft['file_id'],
                caption=f"🎉 Поздравляем с покупкой!\n🎨 {nft['description']}\n🔗 ID: {nft_id}")
        except:
            pass
    except Exception as e:
        print(f"Ошибка в handle_buy_nft: {e}")

@bot.message_handler(commands=['view_nft'])
@group_only
def handle_view_nft(message: Message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "⚠️ Используйте: /view_nft nft_id")
            return
        try:
            nft_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "❌ ID NFT должен быть числом!")
            return
        if nft_id not in user_nfts:
            bot.reply_to(message, "❌ NFT с таким ID не существует!")
            return
        nft = user_nfts[nft_id]
        if nft['owner'] is None:
            owner_info = f"✅ Свободен\n💰 Цена: {NFT_BASE_PRICE} Zеток\n🛒 Купить: /buy_nft {nft_id}"
        else:
            try:
                owner = bot.get_chat(nft['owner'])
                owner_info = f"👤 Владелец: {owner.first_name}"
            except:
                owner_info = "👤 Владелец: Неизвестен"
        bot.send_photo(message.chat.id, nft['file_id'],
            caption=f"🖼️ NFT #{nft_id}\n\n🎨 {nft['description']}\n⭐ Редкость: {nft['rarity']}\n{owner_info}")
    except Exception as e:
        print(f"Ошибка в handle_view_nft: {e}")

@bot.message_handler(commands=['nft_list'])
@group_only
def handle_nft_list(message: Message):
    if not user_nfts:
        bot.reply_to(message, "📭 В системе пока нет NFT!")
        return
    response = "📋 Все NFT в системе:\n\n"
    for nft_id, nft in user_nfts.items():
        status = "✅ Свободен" if nft['owner'] is None else "📦 В коллекции"
        response += f"🎨 {nft_id}: {nft['description']} - {status}\n"
    response += f"\n💰 Все NFT стоят: {NFT_BASE_PRICE} Zеток\n🛒 Для покупки: /buy_nft [id]"
    bot.reply_to(message, response)

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
        ban_status = "\n\n🚫 Ваш аккаунт заблокирован!"
    bot.reply_to(message,
        f"Статистика бота:\n"
        f"👥 Всего пользователей: {users_count}\n"
        f"💰 Всего заработано Zеток: {total_leaves}\n"
        f"🌿 Всего территорий: {total_tea}"
        f"{ban_status}")

@bot.message_handler(commands=['top'])
@group_only
def handle_top(message: Message):
    sorted_users = sorted(user_balances.items(),
        key=lambda x: (x[1]['tea'], x[1]['leaves']), reverse=True)
    top_users = sorted_users[:10]
    response = "🏆 Топ-10 сборщиков:\n\n"
    for index, (user_id, balance) in enumerate(top_users, 1):
        try:
            user = bot.get_chat(user_id)
            user_name = user.first_name
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(index, "🏅")
            response += f"{medal} {index}. {user_name}: 🌿 {balance['tea']} | 💰{balance['leaves']}\n"
        except:
            response += f"🏆 {index}. Пользователь:  🌿 {balance['tea']} | 💰 {balance['leaves']}\n"
    user_id = message.from_user.id
    init_user_data(user_id)
    if user_balances[user_id].get('banned', False):
        response += "\n\n🚫 Ваш аккаунт заблокирован!"
    bot.reply_to(message, response)
    track_mission(user_id, 'top_view')

@bot.message_handler(commands=['craft'])
@group_only
def handle_craft(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        command_parts = message.text.split()
        if len(command_parts) == 1:
            amount = 1
        else:
            try:
                amount = int(command_parts[1])
                if amount <= 0:
                    bot.reply_to(message, "❌ Количество должно быть положительным числом!")
                    return
            except ValueError:
                bot.reply_to(message,
                    "⚠️ Неверный формат команды!\n"
                    "Используйте: /craft [количество]")
                return
        base_cost = 100
        if 'teapot' in user_balances[user_id]['items']:
            base_cost -= SHOP_ITEMS['teapot']['bonus_value']
        total_cost = base_cost * amount
        if user_balances[user_id]['leaves'] < total_cost:
            bot.reply_to(message,
                f"❌ Недостаточно Zеток!\n"
                f"Необходимо: {total_cost} Zеток\n"
                f"У вас есть: {user_balances[user_id]['leaves']} Zеток")
            return
        user_balances[user_id]['leaves'] -= total_cost
        user_balances[user_id]['tea'] += amount
        cost_text = str(base_cost)
        if 'teapot' in user_balances[user_id]['items']:
            cost_text = f"{10}(-{SHOP_ITEMS['teapot']['bonus_value']} = {base_cost})"
        craft_message = random.choice(CRAFT_MESSAGES).format(count=amount)
        bot.reply_to(message,
            f"{craft_message}\n"
            f"Потрачено Zеток: {cost_text} 🪙 {amount} = {total_cost} \n\n"
            f"Баланс:\n"
            f"Zеток: {user_balances[user_id]['leaves']}\n"
            f"🌿 Территории: {user_balances[user_id]['tea']}")
        track_mission(user_id, 'craft', amount)
    except Exception as e:
        print(f"Ошибка в handle_craft: {e}")

@bot.message_handler(commands=['farmtime'])
@group_only
def handle_farmtime(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        current_time = datetime.datetime.now().timestamp()
        last_farm = user_balances[user_id]['last_farm']
        if can_farm(last_farm, user_id):
            bot.reply_to(message, "✅ Вы можете работать\nИспользуйте команду /farm")
        else:
            time_until_next = 3600 - (current_time - last_farm)
            remaining_time = format_remaining_time(time_until_next)
            bot.reply_to(message, f"⏳ Следующая работа будет доступен через {remaining_time}")
    except Exception as e:
        print(f"Ошибка в handle_farmtime: {e}")

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
            bot.reply_to(message, "⚠️ Используйте: /market_sell [id_предмета] [цена]")
            return
        item_id = command_parts[1].lower()
        try:
            price = int(command_parts[2])
        except ValueError:
            bot.reply_to(message, "❌ Цена должна быть числом!")
            return
        if item_id not in SHOP_ITEMS:
            bot.reply_to(message, "❌ Такого предмета не существует!")
            return
        if price < MARKET_MIN_PRICE:
            bot.reply_to(message, f"❌ Минимальная цена: {MARKET_MIN_PRICE} Zеток!")
            return
        if item_id not in user_balances[user_id]['items']:
            bot.reply_to(message, "❌ У вас нет этого предмета!")
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
        bot.reply_to(message,
            f"✅ Предмет выставлен!\n"
            f"📦 {item['name']}\n"
            f"💰 Цена: {price}\n"
            f"📋 ID: #{listing_id}")
    except Exception as e:
        print(f"Ошибка в handle_market_sell: {e}")

@bot.message_handler(commands=['market', 'm'])
@group_only
def handle_market(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    cleanup_expired_listings()
    if not market_listings:
        bot.reply_to(message, "📭 На рынке пока нет предложений!")
        return
    response = "🏪 Пользовательский рынок\n\n"
    for listing_id, listing in list(market_listings.items())[:10]:
        time_left = listing['expires_at'] - datetime.datetime.now().timestamp()
        days = int(time_left // (24 * 60 * 60))
        hours = int((time_left % (24 * 60 * 60)) // 3600)
        response += (f"📋 #{listing_id} - {listing['item_name']}\n"
                     f"💰 Цена: {listing['price']} Zеток\n"
                     f"👤 Продавец: {listing['seller_name']}\n"
                     f"⏳ Осталось: {days}д {hours}ч\n\n")
    response += f"📊 Всего: {len(market_listings)}"
    bot.reply_to(message, response)

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
            bot.reply_to(message, "⚠️ Используйте: /market_buy [id]")
            return
        try:
            listing_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "❌ ID должен быть числом!")
            return
        if listing_id not in market_listings:
            bot.reply_to(message, "❌ Предложение не найдено!")
            return
        listing = market_listings[listing_id]
        if datetime.datetime.now().timestamp() > listing['expires_at']:
            del market_listings[listing_id]
            bot.reply_to(message, "⏳ Предложение истекло!")
            return
        if user_id == listing['seller_id']:
            bot.reply_to(message, "🚫 Нельзя купить у самого себя!")
            return
        if user_balances[user_id]['leaves'] < listing['price']:
            bot.reply_to(message, f"❌ Недостаточно Zеток! Нужно: {listing['price']}")
            return
        if len(user_balances[user_id]['items']) >= 3:
            bot.reply_to(message, "❌ У вас максимум предметов!")
            return
        user_balances[user_id]['leaves'] -= listing['price']
        user_balances[user_id]['items'].append(listing['item_id'])
        seller_id = listing['seller_id']
        init_user_data(seller_id)
        user_balances[seller_id]['leaves'] += listing['seller_receives']
        item_name = listing['item_name']
        del market_listings[listing_id]
        bot.reply_to(message, f"✅ Вы купили {item_name}!")
        try:
            bot.send_message(seller_id, f"🎉 Ваш {item_name} продан! +{listing['seller_receives']} Zеток")
        except:
            pass
    except Exception as e:
        print(f"Ошибка в handle_market_buy: {e}")

@bot.message_handler(commands=['market_cancel', 'mcancel'])
@group_only
def handle_market_cancel(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, "⚠️ Используйте: /market_cancel [id]")
        return
    try:
        listing_id = int(command_parts[1])
    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом!")
        return
    if listing_id not in market_listings:
        bot.reply_to(message, "❌ Предложение не найдено!")
        return
    listing = market_listings[listing_id]
    if user_id != listing['seller_id']:
        bot.reply_to(message, "🚫 Это не ваше предложение!")
        return
    user_balances[user_id]['items'].append(listing['item_id'])
    del market_listings[listing_id]
    bot.reply_to(message, f"✅ Предложение #{listing_id} отменено!")

@bot.message_handler(commands=['market_all', 'mall'])
@group_only
def handle_market_all(message: Message):
    cleanup_expired_listings()
    if not market_listings:
        bot.reply_to(message, "📭 На рынке пока нет предложений!")
        return
    response = "📋 Все предложения:\n\n"
    for listing_id, listing in market_listings.items():
        time_left = listing['expires_at'] - datetime.datetime.now().timestamp()
        days = int(time_left // (24 * 60 * 60))
        hours = int((time_left % (24 * 60 * 60)) // 3600)
        response += (f"📋 #{listing_id} - {listing['item_name']}\n"
                     f"💰 {listing['price']} Zеток\n"
                     f"👤 {listing['seller_name']}\n"
                     f"⏳ {days}д {hours}ч\n\n")
    if len(response) > 4000:
        parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for part in parts:
            bot.send_message(message.from_user.id, part)
    else:
        bot.reply_to(message, response)

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
                bot.reply_to(message, "⚠️ Используйте: /tc количество")
                return
            recipient = message.reply_to_message.from_user
            recipient_id = recipient.id
            recipient_name = recipient.first_name
            amount = int(command_parts[1])
        else:
            if len(command_parts) != 3:
                bot.reply_to(message, "⚠️ Используйте: /tc @username количество")
                return
            recipient_username = command_parts[1].lstrip('@')
            try:
                amount = int(command_parts[2])
            except ValueError:
                bot.reply_to(message, "❌ Количество должно быть числом!")
                return
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
                bot.reply_to(message, "❌ Пользователь не найден!")
                return
        if amount <= 0:
            bot.reply_to(message, "❌ Количество должно быть положительным!")
            return
        if amount > user_balances[sender_id]['leaves']:
            bot.reply_to(message, f"❌ Недостаточно Zеток! Баланс: {user_balances[sender_id]['leaves']}")
            return
        if recipient_id == sender_id:
            bot.reply_to(message, "🚫 Нельзя отправить самому себе!")
            return
        init_user_data(recipient_id)
        user_balances[sender_id]['leaves'] -= amount
        user_balances[recipient_id]['leaves'] += amount
        bot.reply_to(message,
            f"✅ Отправлено {amount} Zеток пользователю {recipient_name}!\n"
            f"Ваш баланс: {user_balances[sender_id]['leaves']}")
        track_mission(sender_id, 'transfer')
        try:
            bot.send_message(recipient_id, f"💰 Вы получили {amount} Zеток от {message.from_user.first_name}!")
        except:
            pass
    except Exception as e:
        print(f"Ошибка в handle_transfer: {e}")

@bot.message_handler(commands=['customwork'])
@group_only
def handle_custom_work(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        command_text = message.text.replace('/customwork', '', 1).strip()
        if not command_text:
            custom_phrases = user_balances[user_id].get('custom_work', [])
            if not custom_phrases:
                bot.reply_to(message,
                    "📝 У вас нет кастомных фраз.\n\n"
                    "Чтобы добавить, отправьте:\n"
                    "/customwork\nВаша фраза 1+{count}\nВаша фраза 2+{count}\n"
                    "(до 5 фраз)")
            else:
                bot.reply_to(message, "📝 Ваши фразы:\n\n" + "\n".join(
                    f"{i+1}. {p}" for i, p in enumerate(custom_phrases)))
            return
        phrases = [p.strip() for p in command_text.split('\n') if p.strip()][:5]
        if len(phrases) < 2:
            bot.reply_to(message, "⚠️ Нужно минимум 2 фразы!")
            return
        user_balances[user_id]['custom_work'] = phrases
        bot.reply_to(message, f"✅ Установлено {len(phrases)} фраз!")
    except Exception as e:
        print(f"Ошибка в handle_custom_work: {e}")

@bot.message_handler(commands=['give'])
def handle_give(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "🚫 У вас нет прав!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message, "⚠️ Используйте: /give @username количество")
            return
        recipient_username = command_parts[1].lstrip('@')
        try:
            amount = int(command_parts[2])
            if amount <= 0:
                bot.reply_to(message, "❌ Количество должно быть положительным!")
                return
        except ValueError:
            bot.reply_to(message, "❌ Количество должно быть числом!")
            return
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
            bot.reply_to(message, "❌ Пользователь не найден!")
            return
        init_user_data(recipient_id)
        user_balances[recipient_id]['leaves'] += amount
        bot.reply_to(message, f"✅ Выдано {amount} Zеток {recipient_name}!")
        try:
            bot.send_message(recipient_id, f"💰 Админ выдал вам {amount} Zеток!")
        except:
            pass
    except Exception as e:
        print(f"Ошибка в handle_give: {e}")

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
            farm_status = "✅ Доступен"
        else:
            time_until_next = 3600 - (current_time - last_farm)
            remaining_time = format_remaining_time(time_until_next)
            farm_status = f"⏳ Через {remaining_time}"
        warnings = user_balances[user_id].get('warnings', [])
        warnings_text = f"\n⚠️ Предупреждений: {len(warnings)}/{MAX_WARNINGS}"
        response = (
            f"👤 Профиль игрока\n\n"
            f"Имя: {user.first_name}\n"
            f"ID: {user.id}\n"
            f"Username: @{user.username if user.username else 'отсутствует'}\n\n"
            f"💰 Баланс:\n"
            f"💰 Zетки: {user_balances[user_id]['leaves']}\n"
            f"🌿 Территории: {user_balances[user_id]['tea']}"
            f"⏳ Следующий сбор: {farm_status}\n"
            f"👑 Администратор: {'Да' if is_admin(user_id) else 'Нет'}"
            f"{warnings_text}"
        )
        if user_balances[user_id].get('banned', False):
            response += f"\n\n🚫 Аккаунт заблокирован!\nПричина: {user_balances[user_id].get('ban_reason', 'не указана')}"
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка в handle_me: {e}")

@bot.message_handler(commands=['end_event'])
def handle_end_event(message: Message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "🚫 У вас нет прав!")
        return
    global HALLOWEEN_EVENT_ACTIVE
    HALLOWEEN_EVENT_ACTIVE = False
    end_halloween_event()
    bot.reply_to(message, "🎃 Ивент завершен досрочно!")

@bot.message_handler(commands=['admin'])
def handle_admin(message: Message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "🚫 У вас нет прав!")
        return
    bot.reply_to(message,
        f"🛡️ Панель администратора\n\n"
        f"💰 /give @username количество\n"
        f"⚠️ /take @username количество\n"
        f"🔄 /reset @username\n"
        f"📊 /stats\n"
        f"📢 /announce текст\n"
        f"⚠️ /warn @username причина\n"
        f"✅ /unwarn @username\n"
        f"🚫 /ban @username причина\n"
        f"✅ /unban @username")

@bot.message_handler(commands=['take'])
def handle_take(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "🚫 У вас нет прав!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message, "⚠️ Используйте: /take @username количество")
            return
        recipient_username = command_parts[1].lstrip('@')
        try:
            amount = int(command_parts[2])
            if amount <= 0:
                bot.reply_to(message, "❌ Количество должно быть положительным!")
                return
        except ValueError:
            bot.reply_to(message, "❌ Количество должно быть числом!")
            return
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
            bot.reply_to(message, "❌ Пользователь не найден!")
            return
        init_user_data(recipient_id)
        if user_balances[recipient_id]['leaves'] < amount:
            bot.reply_to(message, f"❌ У пользователя недостаточно Zеток! Доступно: {user_balances[recipient_id]['leaves']}")
            return
        user_balances[recipient_id]['leaves'] -= amount
        bot.reply_to(message, f"✅ Изъято {amount} Zеток у {recipient_name}!")
        try:
            bot.send_message(recipient_id, f"⚠️ Админ изъял у вас {amount} Zеток!")
        except:
            pass
    except Exception as e:
        print(f"Ошибка в handle_take: {e}")

@bot.message_handler(commands=['stats'])
def handle_stats(message: Message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "🚫 У вас нет прав!")
        return
    users_count = len(user_balances)
    total_leaves = sum(u['leaves'] for u in user_balances.values())
    total_tea = sum(u['tea'] for u in user_balances.values())
    sorted_by_leaves = sorted(user_balances.items(), key=lambda x: x[1]['leaves'], reverse=True)[:5]
    sorted_by_tea = sorted(user_balances.items(), key=lambda x: x[1]['tea'], reverse=True)[:5]
    response = (f"📊 Статистика\n\n"
                f"👥 Пользователей: {users_count}\n"
                f"💰 Всего Zеток: {total_leaves}\n"
                f"🌿 Всего территорий: {total_tea}\n\n"
                f"🏆 Топ-5 по Zетоку:\n")
    for i, (user_id, data) in enumerate(sorted_by_leaves, 1):
        try:
            user = bot.get_chat(user_id)
            response += f"{i}. {user.first_name}: {data['leaves']} 💰\n"
        except:
            continue
    response += f"\n🏆 Топ-5 по территориям:\n"
    for i, (user_id, data) in enumerate(sorted_by_tea, 1):
        try:
            user = bot.get_chat(user_id)
            response += f"{i}. {user.first_name}: {data['tea']} 🌿\n"
        except:
            continue
    bot.reply_to(message, response)

@bot.message_handler(commands=['announce'])
def handle_announce(message: Message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "🚫 У вас нет прав!")
        return
    announcement_text = message.text.replace('/announce', '', 1).strip()
    if not announcement_text:
        bot.reply_to(message, "⚠️ Укажите текст!")
        return
    success = 0
    for user_id in user_balances.keys():
        try:
            bot.send_message(user_id, f"📢 Объявление:\n\n{announcement_text}")
            success += 1
        except:
            continue
    bot.reply_to(message, f"✅ Отправлено: {success}")

@bot.message_handler(commands=['reset'])
def handle_reset(message: Message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "🚫 У вас нет прав!")
        return
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, "⚠️ Используйте: /reset @username")
        return
    recipient_username = command_parts[1].lstrip('@')
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
        bot.reply_to(message, "❌ Пользователь не найден!")
        return
    user_balances[recipient_id]['last_farm'] = 0
    bot.reply_to(message, f"✅ Таймер сброшен для {recipient_name}!")

@bot.message_handler(commands=['warn'])
def handle_warn(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "🚫 У вас нет прав!")
            return
        command_parts = message.text.split()
        if len(command_parts) < 3:
            bot.reply_to(message, "⚠️ Используйте: /warn @username причина")
            return
        recipient_username = command_parts[1].lstrip('@')
        warn_reason = ' '.join(command_parts[2:])
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
            bot.reply_to(message, "❌ Пользователь не найден!")
            return
        init_user_data(recipient_id)
        check_warnings(recipient_id)
        warning = {
            'reason': warn_reason,
            'time': datetime.datetime.now().timestamp(),
            'admin': message.from_user.first_name
        }
        if 'warnings' not in user_balances[recipient_id]:
            user_balances[recipient_id]['warnings'] = []
        user_balances[recipient_id]['warnings'].append(warning)
        warnings_count = len(user_balances[recipient_id]['warnings'])
        bot.reply_to(message,
            f"⚠️ Предупреждение выдано {recipient_name}!\n"
            f"Причина: {warn_reason}\n"
            f"Всего: {warnings_count}/{MAX_WARNINGS}")
        try:
            bot.send_message(recipient_id,
                f"⚠️ Вы получили предупреждение!\n"
                f"Причина: {warn_reason}\n"
                f"Всего: {warnings_count}/{MAX_WARNINGS}")
        except:
            pass
    except Exception as e:
        print(f"Ошибка в handle_warn: {e}")

@bot.message_handler(commands=['ban'])
def handle_ban(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "🚫 У вас нет прав!")
            return
        command_parts = message.text.split()
        if len(command_parts) < 3:
            bot.reply_to(message, "⚠️ Используйте: /ban @username причина")
            return
        recipient_username = command_parts[1].lstrip('@')
        ban_reason = ' '.join(command_parts[2:])
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
            bot.reply_to(message, "❌ Пользователь не найден!")
            return
        init_user_data(recipient_id)
        user_balances[recipient_id]['banned'] = True
        user_balances[recipient_id]['ban_reason'] = ban_reason
        bot.reply_to(message, f"🚫 {recipient_name} заблокирован! Причина: {ban_reason}")
        try:
            bot.send_message(recipient_id, f"🚫 Вы заблокированы!\nПричина: {ban_reason}")
        except:
            pass
    except Exception as e:
        print(f"Ошибка в handle_ban: {e}")

@bot.message_handler(commands=['unwarn'])
def handle_unwarn(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "🚫 У вас нет прав!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "⚠️ Используйте: /unwarn @username")
            return
        recipient_username = command_parts[1].lstrip('@')
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
            bot.reply_to(message, "❌ Пользователь не найден!")
            return
        init_user_data(recipient_id)
        check_warnings(recipient_id)
        if not user_balances[recipient_id].get('warnings', []):
            bot.reply_to(message, f"❌ У {recipient_name} нет активных предупреждений!")
            return
        user_balances[recipient_id]['warnings'].pop()
        warnings_count = len(user_balances[recipient_id]['warnings'])
        bot.reply_to(message, f"✅ Снято предупреждение у {recipient_name}! Осталось: {warnings_count}")
        try:
            bot.send_message(recipient_id, f"✅ С вас снято предупреждение! Осталось: {warnings_count}")
        except:
            pass
    except Exception as e:
        print(f"Ошибка в handle_unwarn: {e}")

@bot.message_handler(commands=['unban'])
def handle_unban(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "🚫 У вас нет прав!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "⚠️ Используйте: /unban @username")
            return
        recipient_username = command_parts[1].lstrip('@')
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
            bot.reply_to(message, "❌ Пользователь не найден!")
            return
        init_user_data(recipient_id)
        if not user_balances[recipient_id].get('banned', False):
            bot.reply_to(message, f"❌ {recipient_name} не заблокирован!")
            return
        user_balances[recipient_id]['banned'] = False
        user_balances[recipient_id]['ban_reason'] = ''
        user_balances[recipient_id]['warnings'] = []
        bot.reply_to(message, f"✅ {recipient_name} разблокирован!")
        try:
            bot.send_message(recipient_id, "✅ Ваш аккаунт разблокирован!")
        except:
            pass
    except Exception as e:
        print(f"Ошибка в handle_unban: {e}")

# ==================== КЛАНЫ ====================

def get_username(user_id):
    try:
        return bot.get_chat(user_id).first_name
    except:
        return "Неизвестный"

def get_role_name(role):
    return {'leader': '👑 Лидер', 'officer': '🛡️ Офицер', 'member': '👤 Участник'}.get(role, '❓ Неизвестно')

@bot.message_handler(commands=['clan'])
@group_only
def handle_clan(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if check_ban(user_id, message):
        return
    if not user_balances[user_id]['clan']:
        bot.reply_to(message,
            f"🏰 Система кланов\n\n"
            f"Вы не состоите в клане.\n"
            f"• /clan_create [название] - создать клан ({CLAN_PRICE} Zеток)\n"
            f"• /clan_join [название] - вступить в клан\n"
            f"• /clan_list - список кланов\n\n"
            f"ℹ️ /clan_help")
    else:
        clan_id = user_balances[user_id]['clan']
        clan = clans[clan_id]
        role = user_balances[user_id]['clan_role']
        members = [uid for uid, data in user_balances.items() if data.get('clan') == clan_id]
        response = (f"🏰 Клан «{clan['name']}»\n\n"
                    f"👑 Лидер: {get_username(clan['leader'])}\n"
                    f"👤 Участников: {len(members)}\n"
                    f"📋 Ваша роль: {get_role_name(role)}\n\n")
        if role in ['leader', 'officer']:
            response += (f"Команды:\n"
                         f"• /clan_invite @username\n"
                         f"• /clan_kick @username\n"
                         f"• /clan_promote @username\n"
                         f"• /clan_demote @username\n")
        response += f"\n• /clan_members\n• /clan_leave"
        bot.reply_to(message, response)

@bot.message_handler(commands=['clan_create'])
@group_only
def handle_clan_create(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if check_ban(user_id, message):
        return
    if user_balances[user_id]['clan']:
        bot.reply_to(message, "❌ Вы уже в клане!")
        return
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) != 2:
        bot.reply_to(message, "⚠️ /clan_create [название]")
        return
    clan_name = command_parts[1].strip()
    if len(clan_name) < MIN_CLAN_NAME_LENGTH or len(clan_name) > MAX_CLAN_NAME_LENGTH:
        bot.reply_to(message, f"❌ Название от {MIN_CLAN_NAME_LENGTH} до {MAX_CLAN_NAME_LENGTH} символов!")
        return
    if any(c['name'].lower() == clan_name.lower() for c in clans.values()):
        bot.reply_to(message, "❌ Такой клан уже существует!")
        return
    if user_balances[user_id]['leaves'] < CLAN_PRICE:
        bot.reply_to(message, f"❌ Нужно {CLAN_PRICE} Zеток!")
        return
    clan_id = str(len(clans) + 1)
    clans[clan_id] = {'name': clan_name, 'leader': user_id, 'created_at': datetime.datetime.now().timestamp()}
    user_balances[user_id]['leaves'] -= CLAN_PRICE
    user_balances[user_id]['clan'] = clan_id
    user_balances[user_id]['clan_role'] = 'leader'
    bot.reply_to(message, f"🎉 Клан «{clan_name}» создан!")

@bot.message_handler(commands=['clan_help'])
@group_only
def handle_clan_help(message: Message):
    bot.reply_to(message,
        f"📖 Руководство по кланам\n\n"
        f"• /clan - информация о клане\n"
        f"• /clan_create [название] - создать ({CLAN_PRICE} Zеток)\n"
        f"• /clan_list - список\n"
        f"• /clan_join [название] - вступить\n"
        f"• /clan_leave - покинуть\n"
        f"• /clan_members - участники\n\n"
        f"Управление (лидер/офицер):\n"
        f"• /clan_invite, /clan_kick, /clan_promote, /clan_demote")

@bot.message_handler(commands=['clan_invite'])
@group_only
def handle_clan_invite(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "❌ Вы не в клане!")
            return
        if user_balances[user_id]['clan_role'] not in ['leader', 'officer']:
            bot.reply_to(message, "🚫 Нет прав!")
            return
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "⚠️ /clan_invite @username")
            return
        target_username = command_parts[1].lstrip('@')
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
            bot.reply_to(message, "❌ Пользователь не найден!")
            return
        if user_balances[target_id]['clan']:
            bot.reply_to(message, "❌ Уже в клане!")
            return
        clan_id = user_balances[user_id]['clan']
        user_balances[target_id]['clan'] = clan_id
        user_balances[target_id]['clan_role'] = 'member'
        bot.reply_to(message, f"✅ {target_name} приглашён!")
        try:
            bot.send_message(target_id, f"🏰 Вас пригласили в клан «{clans[clan_id]['name']}»!")
        except:
            pass
    except Exception as e:
        print(f"Ошибка clan_invite: {e}")

@bot.message_handler(commands=['clan_kick'])
@group_only
def handle_clan_kick(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if not user_balances[user_id]['clan']:
        bot.reply_to(message, "❌ Вы не в клане!")
        return
    if user_balances[user_id]['clan_role'] not in ['leader', 'officer']:
        bot.reply_to(message, "🚫 Нет прав!")
        return
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, "⚠️ /clan_kick @username")
        return
    target_username = command_parts[1].lstrip('@')
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
        bot.reply_to(message, "❌ Не найден!")
        return
    clan_id = user_balances[user_id]['clan']
    if user_balances[target_id].get('clan') != clan_id:
        bot.reply_to(message, "❌ Не в вашем клане!")
        return
    if user_balances[user_id]['clan_role'] == 'officer' and user_balances[target_id]['clan_role'] in ['leader', 'officer']:
        bot.reply_to(message, "🚫 Нельзя исключить лидера/офицера!")
        return
    user_balances[target_id]['clan'] = None
    user_balances[target_id]['clan_role'] = None
    bot.reply_to(message, f"✅ {target_name} исключён!")

@bot.message_handler(commands=['clan_promote'])
@group_only
def handle_clan_promote(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if not user_balances[user_id]['clan']:
        bot.reply_to(message, "❌ Вы не в клане!")
        return
    if user_balances[user_id]['clan_role'] != 'leader':
        bot.reply_to(message, "🚫 Только лидер!")
        return
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, "⚠️ /clan_promote @username")
        return
    target_username = command_parts[1].lstrip('@')
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
        bot.reply_to(message, "❌ Не найден!")
        return
    clan_id = user_balances[user_id]['clan']
    if user_balances[target_id].get('clan') != clan_id:
        bot.reply_to(message, "❌ Не в вашем клане!")
        return
    if user_balances[target_id]['clan_role'] == 'officer':
        bot.reply_to(message, "❌ Уже офицер!")
        return
    user_balances[target_id]['clan_role'] = 'officer'
    bot.reply_to(message, f"✅ {target_name} повышен!")

@bot.message_handler(commands=['clan_demote'])
@group_only
def handle_clan_demote(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if not user_balances[user_id]['clan']:
        bot.reply_to(message, "❌ Вы не в клане!")
        return
    if user_balances[user_id]['clan_role'] != 'leader':
        bot.reply_to(message, "🚫 Только лидер!")
        return
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, "⚠️ /clan_demote @username")
        return
    target_username = command_parts[1].lstrip('@')
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
        bot.reply_to(message, "❌ Не найден!")
        return
    clan_id = user_balances[user_id]['clan']
    if user_balances[target_id].get('clan') != clan_id:
        bot.reply_to(message, "❌ Не в вашем клане!")
        return
    if user_balances[target_id]['clan_role'] != 'officer':
        bot.reply_to(message, "❌ Не офицер!")
        return
    user_balances[target_id]['clan_role'] = 'member'
    bot.reply_to(message, f"✅ {target_name} понижен!")

@bot.message_handler(commands=['clan_members'])
@group_only
def handle_clan_members(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if not user_balances[user_id]['clan']:
        bot.reply_to(message, "❌ Вы не в клане!")
        return
    clan_id = user_balances[user_id]['clan']
    clan = clans[clan_id]
    members = []
    for uid, data in user_balances.items():
        if data.get('clan') == clan_id:
            role = get_role_name(data['clan_role'])
            try:
                username = bot.get_chat(uid).first_name
                members.append((role, username))
            except:
                continue
    role_priority = {'👑 Лидер': 0, '🛡️ Офицер': 1, '👤 Участник': 2}
    members.sort(key=lambda x: role_priority[x[0]])
    response = f"👤 Участники клана «{clan['name']}»:\n\n"
    for role, username in members:
        response += f"{role}: {username}\n"
    bot.reply_to(message, response)

@bot.message_handler(commands=['clan_leave'])
@group_only
def handle_clan_leave(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if not user_balances[user_id]['clan']:
        bot.reply_to(message, "❌ Вы не в клане!")
        return
    clan_id = user_balances[user_id]['clan']
    clan_name = clans[clan_id]['name']
    if user_balances[user_id]['clan_role'] == 'leader':
        new_leader = None
        for uid, data in user_balances.items():
            if data.get('clan') == clan_id and data['clan_role'] == 'officer':
                new_leader = uid
                break
        if new_leader:
            user_balances[new_leader]['clan_role'] = 'leader'
            clans[clan_id]['leader'] = new_leader
            try:
                bot.send_message(new_leader, f"🏆 Вы новый лидер клана «{clan_name}»!")
            except:
                pass
        else:
            del clans[clan_id]
            for uid, data in user_balances.items():
                if data.get('clan') == clan_id:
                    data['clan'] = None
                    data['clan_role'] = None
            bot.reply_to(message, f"🚫 Клан расформирован!")
            return
    user_balances[user_id]['clan'] = None
    user_balances[user_id]['clan_role'] = None
    bot.reply_to(message, f"👋 Вы покинули клан «{clan_name}»")

@bot.message_handler(commands=['clan_list'])
@group_only
def handle_clan_list(message: Message):
    if not clans:
        bot.reply_to(message, "📭 Нет кланов!")
        return
    response = "📋 Список кланов:\n\n"
    for clan_id, clan_data in clans.items():
        members_count = sum(1 for data in user_balances.values() if data.get('clan') == clan_id)
        leader_name = get_username(clan_data['leader'])
        response += f"🏰 «{clan_data['name']}»\n👑 Лидер: {leader_name}\n👤 Участников: {members_count}\n\n"
    response += "Для вступления: /clan_join [название]"
    bot.reply_to(message, response)

@bot.message_handler(commands=['clan_join'])
@group_only
def handle_clan_join(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if check_ban(user_id, message):
        return
    if user_balances[user_id]['clan']:
        bot.reply_to(message, "❌ Вы уже в клане!")
        return
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) != 2:
        bot.reply_to(message, "⚠️ /clan_join [название]")
        return
    clan_name = command_parts[1].strip()
    for clan_id, clan_data in clans.items():
        if clan_data['name'].lower() == clan_name.lower():
            user_balances[user_id]['clan'] = clan_id
            user_balances[user_id]['clan_role'] = 'member'
            bot.reply_to(message, f"✅ Вы вступили в клан «{clan_data['name']}»!")
            return
    bot.reply_to(message, "❌ Клан не найден!")

# ==================== МАГАЗИН ====================

@bot.message_handler(commands=['shop'])
@group_only
def handle_shop(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if check_ban(user_id, message):
        return
    response = "🏪 Магазин предметов\n\n"
    for item in SHOP_ITEMS.values():
        response += (f"{item['name']}\n"
                     f"📝 {item['description']}\n"
                     f"💰 Цена: {item['price']} Zеток\n"
                     f"🛒 /buy {item['id']}\n\n")
    response += (f"У вас: {user_balances[user_id]['leaves']} Zеток\n"
                 f"Максимум предметов: 3\n"
                 f"/inventory\n\n"
                 f"🖼️ NFT: /nft_list")
    bot.reply_to(message, response)
    track_mission(user_id, 'shop')

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
            bot.reply_to(message, "⚠️ /buy [id_предмета]")
            return
        item_id = command_parts[1].lower()
        if item_id not in SHOP_ITEMS:
            bot.reply_to(message, "❌ Предмет не найден!")
            return
        item = SHOP_ITEMS[item_id]
        if len(user_balances[user_id]['items']) >= 3:
            bot.reply_to(message, "❌ Максимум 3 предмета!")
            return
        if item_id in user_balances[user_id]['items']:
            bot.reply_to(message, "❌ У вас уже есть этот предмет!")
            return
        if user_balances[user_id]['leaves'] < item['price']:
            bot.reply_to(message, f"❌ Нужно {item['price']} Zеток!")
            return
        user_balances[user_id]['leaves'] -= item['price']
        user_balances[user_id]['items'].append(item_id)
        bot.reply_to(message, f"✅ Куплено: {item['name']}!")
    except Exception as e:
        print(f"Ошибка buy: {e}")

@bot.message_handler(commands=['inventory'])
@group_only
def handle_inventory(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if check_ban(user_id, message):
        return
    items = user_balances[user_id]['items']
    if not items:
        bot.reply_to(message, "🎒 Инвентарь пуст!")
        return
    response = "🎒 Ваш инвентарь:\n\n"
    for item_id in items:
        item = SHOP_ITEMS[item_id]
        response += f"{item['name']}\n📝 {item['description']}\n🗑️ /drop {item_id}\n\n"
    response += f"Всего: {len(items)}/3"
    bot.reply_to(message, response)

@bot.message_handler(commands=['drop'])
@group_only
def handle_drop(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    if check_ban(user_id, message):
        return
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.reply_to(message, "⚠️ /drop [id]")
        return
    item_id = command_parts[1].lower()
    if item_id not in SHOP_ITEMS:
        bot.reply_to(message, "❌ Предмет не найден!")
        return
    if item_id not in user_balances[user_id]['items']:
        bot.reply_to(message, "❌ У вас нет этого предмета!")
        return
    user_balances[user_id]['items'].remove(item_id)
    bot.reply_to(message, f"🗑️ Выброшено: {SHOP_ITEMS[item_id]['name']}")

# ==================== MATH EVENT ====================

math_active = False
math_answer = 0
math_reward = 0
math_chat_id = None

MATH_REPLIES = [
    "✅ Правильно! Награда: {reward} Zеток!",
    "Победа! Вы получили {reward} Zеток!",
    "Точно! Ваша награда: {reward} Zеток!"
]

def generate_math():
    if random.random() < 0.3:
        a = random.randint(2, 15)
        b = random.randint(2, 10)
        c = random.randint(1, 10)
        op1 = random.choice(['+', '-'])
        op2 = random.choice(['*', '+', '-'])
        expr = f"({a} {op1} {b}) {op2} {c}"
        answer = eval(expr)
        return expr, int(answer)
    op_func, op_symbol = random.choice([
        (lambda a, b: a + b, '+'),
        (lambda a, b: a - b, '-'),
        (lambda a, b: a * b, '*'),
    ])
    a = random.randint(5, 50)
    b = random.randint(2, 20)
    result = op_func(a, b)
    expr = f"{a} {op_symbol} {b}"
    return expr, result

def math_event_loop():
    global math_active, math_answer, math_reward, math_chat_id
    while True:
        time.sleep(random.randint(600, 2400))
        try:
            math_chat_id = ALLOWED_GROUP_ID
            if not math_chat_id:
                continue
            expr, answer = generate_math()
            math_reward = random.randint(10, 100)
            math_answer = answer
            math_active = True
            bot.send_message(math_chat_id,
                f"🧮 МАТЕМАТИЧЕСКИЙ ВЫЗОВ!\n\n{expr} = ?\n\n🏆 Награда: {math_reward} Zеток")
        except Exception as e:
            print(f"Ошибка math_event: {e}")

def handle_math_reply(message: Message):
    global math_active, math_answer, math_reward
    if not math_active:
        return
    if message.chat.type == 'private':
        return
    if not is_subscribed(message.from_user.id):
        return
    try:
        user_answer = int(message.text.strip())
    except (ValueError, AttributeError):
        return
    if user_answer != math_answer:
        return
    math_active = False
    user_id = message.from_user.id
    init_user_data(user_id)
    now = datetime.datetime.now().timestamp()
    user = user_balances[user_id]
    if user.get('daily_wins_reset', 0) < now - 3600:
        user['daily_wins_today'] = 0
        user['daily_wins_reset'] = now
    if user.get('daily_wins_today', 0) >= 3:
        bot.reply_to(message, "⚠️ Вы уже выиграли 3 раза сегодня!")
        return
    user['leaves'] += math_reward
    user['daily_wins_today'] = user.get('daily_wins_today', 0) + 1
    reply = random.choice(MATH_REPLIES).format(reward=math_reward)
    bot.reply_to(message, f"🎯 {message.from_user.first_name}, {reply}")

# ==================== SLOTS ====================

SLOT_SYMBOLS = ['🍒', '🍎', '🍉', '🍀', '💎', '💰']

@bot.message_handler(commands=['slots'])
@group_only
def handle_slots(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ /slots [ставка]\nМин: 10, макс: 500")
            return
        try:
            bet = int(parts[1])
        except ValueError:
            bot.reply_to(message, "❌ Ставка должна быть числом!")
            return
        if bet < 10 or bet > 500:
            bot.reply_to(message, "❌ Ставка от 10 до 500!")
            return
        if user_balances[user_id]['leaves'] < bet:
            bot.reply_to(message, f"❌ Недостаточно Zеток! У вас: {user_balances[user_id]['leaves']}")
            return
        s1 = random.choice(SLOT_SYMBOLS)
        s2 = random.choice(SLOT_SYMBOLS)
        s3 = random.choice(SLOT_SYMBOLS)
        user_balances[user_id]['leaves'] -= bet
        if s1 == s2 == s3:
            win = bet * 5
            emoji = "🎉"
            msg = "ДЖЕКПОТ!"
        elif s1 == s2 or s2 == s3 or s1 == s3:
            win = bet * 2
            emoji = "⭐"
            msg = "Два одинаковых!"
        else:
            win = 0
            emoji = "❌"
            msg = "Ничего :("
        user_balances[user_id]['leaves'] += win
        bot.reply_to(message,
            f"🎰 СЛОТЫ!\n[ {s1} | {s2} | {s3} ]\n\n"
            f"{emoji} {msg}\n"
            f"💰 Ставка: {bet} | Выигрыш: {win}\n"
            f"💰 Баланс: {user_balances[user_id]['leaves']}")
        track_mission(user_id, 'slots')
    except Exception as e:
        print(f"Ошибка slots: {e}")

# ==================== DAILY ====================

DAILY_REWARDS = [20, 40, 60, 80, 100, 120, 140]

@bot.message_handler(commands=['daily'])
@group_only
def handle_daily(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        now = datetime.datetime.now().timestamp()
        user = user_balances[user_id]
        last = user.get('daily_last', 0)
        streak = user.get('daily_streak', 0)
        elapsed = now - last
        if elapsed < 86400 and last > 0:
            hours_left = int((86400 - elapsed) // 3600)
            mins_left = int(((86400 - elapsed) % 3600) // 60)
            bot.reply_to(message, f"⏰ Следующий бонус через: {hours_left}ч {mins_left}м")
            return
        if elapsed > 172800:
            streak = 0
        streak = min(streak + 1, 7)
        reward = DAILY_REWARDS[streak - 1]
        user['leaves'] += reward
        user['daily_streak'] = streak
        user['daily_last'] = now
        bar = "█" * streak + "░" * (7 - streak)
        bot.reply_to(message,
            f"🎁 ЕЖЕДНЕВНЫЙ БОНУС!\n\n"
            f"💰 Награда: {reward} Zеток\n"
            f"🔥 Серия: {streak}/7\n{bar}\n\n"
            f"💰 Баланс: {user['leaves']}")
        track_mission(user_id, 'daily_claim')
    except Exception as e:
        print(f"Ошибка daily: {e}")

# ==================== MISSIONS ====================

MISSION_TEMPLATES = [
    ("Профарми {n} раз", "farm", 3, 50),
    ("Скрафти {n} территорий", "craft", 2, 40),
    ("Отправь {n} Zеток", "transfer", 1, 30),
    ("Посети /shop", "shop", 1, 15),
    ("Войди /daily", "daily_claim", 1, 20),
    ("Посмотри /top", "top_view", 1, 10),
    ("Крутни {n} раз слоты", "slots", 3, 45),
]

def generate_missions(user_id):
    user = user_balances[user_id]
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if user.get('missions_date') == today and user.get('missions'):
        return user['missions']
    pool = random.sample(MISSION_TEMPLATES, min(3, len(MISSION_TEMPLATES)))
    missions = []
    for template, action, n, reward in pool:
        missions.append({
            'text': template.format(n=n),
            'action': action,
            'target': n,
            'progress': 0,
            'reward': reward,
            'done': False
        })
    user['missions'] = missions
    user['missions_date'] = today
    return missions

def track_mission(user_id, action, amount=1):
    if user_id not in user_balances:
        return
    user = user_balances[user_id]
    missions = user.get('missions', [])
    for m in missions:
        if m['action'] == action and not m['done']:
            m['progress'] = min(m['progress'] + amount, m['target'])
            if m['progress'] >= m['target']:
                m['done'] = True
                user['leaves'] += m['reward']

@bot.message_handler(commands=['missions'])
@group_only
def handle_missions(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        missions = generate_missions(user_id)
        response = "📋 МИССИИ НА СЕГОДНЯ:\n\n"
        for i, m in enumerate(missions, 1):
            status = "✅" if m['done'] else f"{m['progress']}/{m['target']}"
            response += f"{i}. {m['text']}\n   {status} | 💰 {m['reward']} Zеток\n"
        done_count = sum(1 for m in missions if m['done'])
        if done_count == len(missions):
            response += "\n🎉 Все миссии выполнены!"
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка missions: {e}")

# ==================== DUELS ====================

pending_duels = {}
duel_cooldowns = {}

@bot.message_handler(commands=['duel'])
@group_only
def handle_duel(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if check_ban(user_id, message):
            return
        now = datetime.datetime.now().timestamp()
        if duel_cooldowns.get(user_id, 0) > now:
            remaining = int((duel_cooldowns[user_id] - now) // 60)
            bot.reply_to(message, f"⏰ Кулдаун дуэли: {remaining} мин")
            return
        if not message.reply_to_message:
            bot.reply_to(message, "⚠️ Ответьте на сообщение игрока\n/duel [ставка]")
            return
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ /duel [ставка]\nМин: 50, макс: 500")
            return
        try:
            bet = int(parts[1])
        except ValueError:
            bot.reply_to(message, "❌ Ставка должна быть числом!")
            return
        if bet < 50 or bet > 500:
            bot.reply_to(message, "❌ Ставка от 50 до 500!")
            return
        target_id = message.reply_to_message.from_user.id
        if target_id == user_id:
            bot.reply_to(message, "🚫 Нельзя дуэлиться с собой!")
            return
        init_user_data(target_id)
        if user_balances[user_id]['leaves'] < bet:
            bot.reply_to(message, f"❌ У вас недостаточно {bet} Zеток")
            return
        if user_balances[target_id]['leaves'] < bet:
            bot.reply_to(message, f"❌ У цели недостаточно {bet} Zеток")
            return
        if target_id in pending_duels:
            bot.reply_to(message, "❌ Этот игрок уже в дуэли!")
            return
        pending_duels[target_id] = {'challenger': user_id, 'bet': bet, 'time': now}
        bot.reply_to(message,
            f"⚔️ ДУЭЛЬ!\n"
            f"{message.from_user.first_name} вызывает {message.reply_to_message.from_user.first_name}\n"
            f"💰 Ставка: {bet}\n\n"
            f"/accept или /decline")
    except Exception as e:
        print(f"Ошибка duel: {e}")

@bot.message_handler(commands=['accept'])
@group_only
def handle_accept(message: Message):
    try:
        user_id = message.from_user.id
        if user_id not in pending_duels:
            bot.reply_to(message, "❌ У вас нет активных дуэлей!")
            return
        duel = pending_duels[user_id]
        challenger_id = duel['challenger']
        bet = duel['bet']
        del pending_duels[user_id]
        if user_balances[challenger_id]['leaves'] < bet or user_balances[user_id]['leaves'] < bet:
            bot.reply_to(message, "❌ У кого-то недостаточно Zеток.")
            return
        user_balances[challenger_id]['leaves'] -= bet
        user_balances[user_id]['leaves'] -= bet
        winner_id = challenger_id if random.random() < 0.5 else user_id
        user_balances[winner_id]['leaves'] += bet * 2
        duel_cooldowns[challenger_id] = datetime.datetime.now().timestamp() + 600
        duel_cooldowns[user_id] = datetime.datetime.now().timestamp() + 600
        winner_name = bot.get_chat(winner_id).first_name
        bot.reply_to(message,
            f"⚔️ РЕЗУЛЬТАТ ДУЭЛИ!\n\n"
            f"🏆 Победитель: {winner_name}\n"
            f"💰 Награда: {bet * 2} Zеток")
    except Exception as e:
        print(f"Ошибка accept: {e}")

@bot.message_handler(commands=['decline'])
@group_only
def handle_decline(message: Message):
    user_id = message.from_user.id
    if user_id in pending_duels:
        del pending_duels[user_id]
        bot.reply_to(message, "❌ Дуэль отклонена.")
    else:
        bot.reply_to(message, "❌ У вас нет активных дуэлей!")

# ==================== EXTENDED TOPS ====================

@bot.message_handler(commands=['top_t'])
@group_only
def handle_top_t(message: Message):
    sorted_users = sorted(user_balances.items(), key=lambda x: x[1].get('tea', 0), reverse=True)[:10]
    response = "🏰 Топ-10 по территориям:\n\n"
    for index, (uid, data) in enumerate(sorted_users, 1):
        try:
            name = bot.get_chat(uid).first_name
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(index, "🏅")
            response += f"{medal} {index}. {name}: {data.get('tea', 0)} 🌿\n"
        except:
            continue
    bot.reply_to(message, response)

@bot.message_handler(commands=['top_clans'])
@group_only
def handle_top_clans(message: Message):
    if not clans:
        bot.reply_to(message, "📭 Ещё нет кланов!")
        return
    sorted_clans = sorted(clans.items(), key=lambda x: x[1].get('total_donated', 0), reverse=True)[:10]
    response = "🏰 Топ-10 кланов:\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (cid, data) in enumerate(sorted_clans, 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        members = sum(1 for d in user_balances.values() if d.get('clan') == cid)
        response += f"{medal} {data['name']} | {members} участников\n"
    bot.reply_to(message, response)

@bot.message_handler(commands=['top_kills'])
@group_only
def handle_top_kills(message: Message):
    sorted_users = sorted(user_balances.items(), key=lambda x: x[1].get('kills', 0), reverse=True)[:10]
    response = "💀 Топ-10 убийц:\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for index, (uid, data) in enumerate(sorted_users, 1):
        try:
            name = bot.get_chat(uid).first_name
            medal = medals[index-1] if index <= 3 else f"{index}."
            kills = data.get('kills', 0)
            if kills > 0:
                response += f"{medal} {name}: {kills} убийств\n"
        except:
            continue
    if len(response) < 50:
        response += "Пока никто никого не убил!"
    bot.reply_to(message, response)

@bot.message_handler(commands=['killstats', 'kills'])
def handle_killstats(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)
        if not HALLOWEEN_EVENT_ACTIVE:
            bot.reply_to(message, "🎃 Хэллоуинский ивент завершен!")
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
        response = "💀 Статистика убийств\n\n🏆 Топ убийц:\n"
        for i, (name, kills) in enumerate(killers[:10], 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "🏅")
            response += f"{medal} {i}. {name}: {kills} убийств\n"
        user_kills = user_balances[user_id].get('kills', 0)
        response += f"\nВаша статистика:\n💀 Убийств: {user_kills}\n"
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Ошибка killstats: {e}")

@bot.message_handler(commands=['event', 'event_check'])
@group_only
def handle_event(message: Message):
    init_user_data(message.from_user.id)
    if not HALLOWEEN_EVENT_ACTIVE:
        bot.reply_to(message, "🎃 Хэллоуинский ивент завершен!")
    else:
        time_left = HALLOWEEN_END_TIME - datetime.datetime.now().timestamp()
        days = int(time_left // (24 * 60 * 60))
        hours = int((time_left % (24 * 60 * 60)) // 3600)
        bot.reply_to(message,
            f"🎃 ХЭЛЛОУИНСКИЙ ИВЕНТ! 🎃\n\n"
            f"💥 /kill (ответом на сообщение)\n"
            f"⚔️ Убивать раз в 2 часа\n"
            f"💀 Убитый не может фармить 2 часа\n"
            f"🏆 Приз: 🎃 Хэллоуинская тыква\n\n"
            f"📊 /killstats\n"
            f"⏳ Осталось: {days}д {hours}ч")

@bot.message_handler(commands=['pumpkins', 'my_pumpkins'])
@group_only
def handle_my_pumpkins(message: Message):
    init_user_data(message.from_user.id)
    bot.reply_to(message, "Осенний ивент окончен\n\n")

# ==================== WEB / PING ====================

def self_ping():
    import urllib.request
    while True:
        time.sleep(300)
        try:
            url = os.environ.get('RENDER_EXTERNAL_URL', '')
            if not url:
                return
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req, timeout=15)
            print(f"[PING] {resp.status} OK")
        except Exception as e:
            print(f"[PING] Error: {e}")

LANDING_HTML = """<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>ПОТУЖИЯ БОТ</title></head>
<body style="background:#0f0c29;color:#fff;font-family:sans-serif;text-align:center;padding:60px">
<h1>⚔️ ПОТУЖНО БОТ</h1>
<p>Экономика, кланы, дуэли в Telegram</p>
<a href="https://t.me/BotPutinaPatriot_ZOV_RussiaBot" style="color:#ffd200">🚀 Запустить бота</a>
<hr><a href="https://t.me/Potuzhiya" style="color:#ffd200">📰 Наш канал</a>
</body></html>"""

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(LANDING_HTML.encode('utf-8'))
    def log_message(self, format, *args):
        pass

def run_web():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

if __name__ == '__main__':
    print("Bot started...")

    commands = [
        telebot.types.BotCommand("start", "Запустить бота"),
        telebot.types.BotCommand("farm", "Фармить Zетки"),
        telebot.types.BotCommand("craft", "Захватить территорию"),
        telebot.types.BotCommand("balance", "Мой баланс"),
        telebot.types.BotCommand("me", "Мой профиль"),
        telebot.types.BotCommand("inventory", "Мой инвентарь"),
        telebot.types.BotCommand("shop", "Магазин предметов"),
        telebot.types.BotCommand("buy", "Купить предмет"),
        telebot.types.BotCommand("drop", "Выбросить предмет"),
        telebot.types.BotCommand("nft_list", "Каталог NFT"),
        telebot.types.BotCommand("buy_nft", "Купить NFT"),
        telebot.types.BotCommand("tc", "Перевести Zетки"),
        telebot.types.BotCommand("duel", "Вызвать на дуэль"),
        telebot.types.BotCommand("accept", "Принять дуэль"),
        telebot.types.BotCommand("decline", "Отклонить дуэль"),
        telebot.types.BotCommand("daily", "Ежедневный бонус"),
        telebot.types.BotCommand("missions", "Мои миссии"),
        telebot.types.BotCommand("slots", "Слоты"),
        telebot.types.BotCommand("top", "Топ Zеток"),
        telebot.types.BotCommand("top_t", "Топ территорий"),
        telebot.types.BotCommand("top_clans", "Топ кланов"),
        telebot.types.BotCommand("top_kills", "Топ убийц"),
        telebot.types.BotCommand("clan", "Управление кланом"),
        telebot.types.BotCommand("help", "Помощь"),
    ]
    bot.set_my_commands(commands)

    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()

    event_thread = threading.Thread(target=check_event_end, daemon=True)
    event_thread.start()
    math_thread = threading.Thread(target=math_event_loop, daemon=True)
    math_thread.start()
    ping_thread = threading.Thread(target=self_ping, daemon=True)
    ping_thread.start()

    @bot.message_handler(func=lambda m: math_active and m.chat.type != 'private' and m.text and m.text.strip().lstrip('-').isdigit(), content_types=['text'])
    def _math_handler(message: Message):
        handle_math_reply(message)

    bot.infinity_polling()
