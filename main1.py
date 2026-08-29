import telebot
import random
import json
import os
from telebot.types import Message
import datetime
import threading
import time

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
    "Êðûìñêàÿ çåìëÿ ùåäðà! Òû çàõâàòèë {count} Zåòîê",
    "Îòëè÷íàÿ ðàáîòà íà êðûìñêèõ ïîëÿõ! Ïàðòèÿ ïîâûøàåò òâîé ðåéòèíã íà +{count}!",
    "Êðûìñêèé ãóáåðíàòîð âûäà¸ò âàì {count} Zåòîê çà õîðîøóþ ðàáîòó!",
    "Çà ñëóæáó íà ïîëóîñòðîâå âû çàðàáîòàëè {count} Zåòîê!",
    "Âû îòëè÷íî ñïðàâèëèñü ñ îõðàíîé ðóáåæåé! +{count} Zåòîê!",
    "Êðûì ïðèíîñèò ïëîäû! +{count} Zåòîê!",
    "Ïëàí ïåðåâûïîëíåí! +{count} Zåòîê!",
    "Ãóáåðíàòîð äîâîëåí âàøà ðàáîòà! +{count} Zåòîê!",
    "Âû óñåðäíî ðàáîòàåòå íà áëàãî Êðûìà! {count} Zåòîê!",
    "Êðûìñêàÿ êðåïîñòü êðåïíåò! {count} Zåòîê!",
    "Âû ïîìîãëè Ïîçäíÿêîâó(ñåêðåòêà) +{count} Zåòîê!"
]

CRAFT_MESSAGES = [
    "{count} Êðûì çàõâà÷åíî! Òû ìàñòåð ñâîåãî äåëà!",
    "{count} Êðûì ïîëó÷åíî ÷åðåç äðåâíèå òðàäèöèè!",
    "{count} Êðûì äîáàâëåíî â âàøó êîëëåêöèþ!",
    "{count} Êðûì çàõâà÷åíî! Òåððèòîðèÿ âàøà!",
    "{count} Êðûì ïîêîðèëñÿ! Âàøà ñòàâêà ðàñòåò!",
    "{count} Êðûì îòâîåâàí! Êðûìñêàÿ çåìëÿ âàøà!",
    "{count} Êðûì äîáàâëåíî ê èìïåðèè!",
    "{count} Êðûì çàõâà÷åíî! Êðûìñêàÿ êîðîíà âàøà!",
    "{count} Êðûì ïîëó÷åí! Ñèëà âàøà!",
    "{count} Êðûì çàõâà÷åíî íàâñåãäà!"
]

COOLDOWN_MESSAGES = [
    "Ïîäîæäè äî íà÷àëà ñìåíû åù¸ {time}",
    "Ïîêà äëÿ òåáÿ ðàáîòû íåò... Ïðîâåðü ÷åðåç {time}",
    "Êðûì òðåáóåò òåðïåíèÿ, ïîäîæäè åù¸ {time}",
    "Êðûìñêèå ïîëÿ îòäûõàþò. Çàãëÿíè ÷åðåç {time}",
    "Ìóäðûé çàùèòíèê çíàåò âðåìÿ ñòðàæè. Ïðèõîäè ÷åðåç {time}",
    "Äðåâíÿÿ ìóäðîñòü ãëàñèò: âåðíèñü ÷åðåç {time}",
    "Äðàêîí îõðàíÿåò Êðûì. Ïîäîæäè {time}",
    "Òóìàí íàä ïîëóîñòðîâîì ðàññååòñÿ ÷åðåç {time}",
    "Âðåìÿ ñòðàæè íàñòóïèò ÷åðåç {time}",
    "Êðûìñêèå øïàãè ãîâîðÿò: çàãëÿíè ÷åðåç {time}"
]

WELCOME_MESSAGES = [
    "Äîáðî ïîæàëîâàòü â Êðûì!",
    "Äà áëàãîñëîâÿò áîãè òâîé ïóòü êðûìñêîãî âîèíà!",
    "Ïóñòü Êðûìñêàÿ çåìëÿ íàïðàâëÿåò òåáÿ!",
    "Äîáðî ïîæàëîâàòü â ñåðäöå Êðûìà!",
    "Äà ïðèíåñåò òåáå óäà÷ó Âåëèêèé Êðûì!!"
]

MAX_WARNINGS = 3
WARNING_DURATION = 7 * 24 * 60 * 60

bot = telebot.TeleBot('8791216614:AAFeu0p9fRps4GA1M04T0d2FKMHscSMaBWQ')

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
                f"?? ÏÎÇÄÐÀÂËßÅÌ! ??\n\n"
                f"Âû âûèãðàëè õýëëîóèíñêèé èâåíò!\n"
                f"?? Ñîâåðøåíî óáèéñòâ: {max_kills}\n"
                f"?? Âàø ïðèç: ?? Õýëëîóèíñêàÿ òûêâà\n"
                f"Ïðåäìåò äîáàâëåí â èíâåíòàðü!")
        except:
            pass

        for user_id in user_balances.keys():
            try:
                bot.send_message(user_id,
                    f"?? ÕÝËËÎÓÈÍÑÊÈÉ ÈÂÅÍÒ ÇÀÂÅÐØÅÍ! ??\n\n"
                    f"?? Ïîáåäèòåëü: {winner_name}\n"
                    f"?? Óáèéñòâ: {max_kills}\n"
                    f"?? Íàãðàäà: Õýëëîóèíñêàÿ òûêâà\n\n"
                    f"Ñïàñèáî âñåì çà ó÷àñòèå! ??")
            except:
                continue

    save_user_data()




SHOP_ITEMS = {


    'gold_rise': {
        'id': 'gold_rise',
        'name': 'ÇÎËÎÒÎÉ ÊÐÛÌ??',
        'description': 'óâåëè÷èâàåò çàðïëàòó íà 100%',
        'price': '1000000000000000000',
        'bonus_type': 'farm',
        'bonus_value': 1
    },
        'halloween_pumpkin': {
        'id': 'halloween_pumpkin',
        'name': '?? Õýëëîóèíñêàÿ òûêâà',
        'description': 'Ýêñêëþçèâíûé ïðåäìåò õýëëîóèíñêîãî èâåíòà!',
        'price': 'Event Item)',
        'bonus_type': 'farm',
        'bonus_value': 1
    },
    'june_sky': {
        'id': 'june_sky',
        'name': '?ëîìòèê èþëüñêîãî íåáà',
        'description': 'óâåëè÷èâàåò çàðïëàòó íà 10%',
        'price': 200,
        'bonus_type': 'farm',
        'bonus_value': 0.1
    },
    'sharf': {
        'id': 'sharf',
        'name': '??Øàðô ëîëîëîøêè',
        'description': 'íå äåëàåò íè÷åãî, ïðåäìåò îò êèòàé òîâàðèù)',
        'price': 1,
        'bonus_type': 'farm',
        'bonus_value': 0
    },
    'watermelon': {
        'id': 'watermelon',
        'name': '??Ñâÿùåííûé àðáóç[NEW]',
        'description': 'óâåëè÷èâàåò çàðïëàòó íà 50%(îáÿçàòåëåí äëÿ êóëüòà!)',
        'price': 1000,
        'bonus_type': 'farm',
        'bonus_value': 0.5
    },
    'watering_can': {
        'id': 'watering_can',
        'name': '?? öàðñêàÿ ïîëèâàëêà',
        'description': 'Óâåëè÷èâàåò çàðïëàòó íà 20%',
        'price': 500,
        'bonus_type': 'farm',
        'bonus_value': 0.2
    },
    'scissors': {
        'id': 'scissors',
        'name': '?? Ñâÿùåííûé ñåðï',
        'description': 'Óâåëè÷èâàåò çàðïëàòó íà 30%',
        'price': 1000,
        'bonus_type': 'farm',
        'bonus_value': 0.3
    },
    'jade_rod': {
        'id':'jade_rod',
        'name': '?? Íåôðèòîâûé ñòåðæåíü',
        'description': 'Ýêîíîìèò 20 ñîö Zåòîê ïðè çàõâàòå òåððèòîðèé',
        'price': 800,
        'bonus_type': 'craft',
        'bonus_value': 20
    },
    'scroll': {
        'id': 'scroll',
        'name': '?? Ñâèòîê ìóäðîñòè',
        'description': 'Óìåíüøàåò âðåìÿ ðàáîòû íà 10 ìèíóò',
        'price': 1500,
        'bonus_type': 'time',
        'bonus_value': 600  # ñåêóíäû
    },
    'dragon': {
        'id': 'dragon',
        'name': '?? Êèòàé äðàêîí(òîâàðèù êèòàé)',
        'description': 'çàðïëàòó íà 50%',
        'price': 2000,
        'bonus_type': 'farm',
        'bonus_value': 0.5
    }
}



def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return {int(k): v for k, v in data.items()}
    return {}

def load_clans_data():
    if os.path.exists(CLANS_FILE):
        try:
            with open(CLANS_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except:
            return {}
    return {}

def save_user_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(user_balances, file, ensure_ascii=False, indent=2)

def save_clans_data():
    with open(CLANS_FILE, 'w', encoding='utf-8') as file:
        json.dump(clans, file, ensure_ascii=False, indent=2)

def check_event_end():
    while True:
        try:
            current_time = datetime.datetime.now().timestamp()
            if HALLOWEEN_EVENT_ACTIVE and current_time >= HALLOWEEN_END_TIME:
                end_halloween_event()
                break
            time.sleep(3600)
        except Exception as e:
            print(f"Îøèáêà â check_event_end: {e}")
            time.sleep(300)

def load_promo_data():
    if os.path.exists(PROMO_FILE):
        try:
            with open(PROMO_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except:
            return {}
    return {}
promo_codes = load_promo_data()

def save_promo_data():
    with open(PROMO_FILE, 'w', encoding='utf-8') as file:
        json.dump(promo_codes, file, ensure_ascii=False, indent=2)

user_balances = load_user_data()
clans = load_clans_data()

def load_nft_data():
    global user_nfts
    if os.path.exists(NFT_DATA_FILE):
        try:
            with open(NFT_DATA_FILE, 'r', encoding='utf-8') as file:
                user_nfts = json.load(file)

                user_nfts = {int(k): v for k, v in user_nfts.items()}
        except:
            user_nfts = {}
    else:
        user_nfts = {}

def save_nft_data():
    with open(NFT_DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(user_nfts, file, ensure_ascii=False, indent=2)


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
    return f"{minutes} ìèí. {seconds} ñåê."


def is_admin(user_id):
    return user_id in ADMIN_IDS





def load_market_data():
    global market_listings
    if os.path.exists('market_data.json'):
        try:
            with open('market_data.json', 'r', encoding='utf-8') as file:
                market_listings = json.load(file)
                # Êîíâåðòèðóåì ñòðîêîâûå êëþ÷è â int
                market_listings = {int(k): v for k, v in market_listings.items()}
        except:
            market_listings = {}

def save_market_data():
    with open('market_data.json', 'w', encoding='utf-8') as file:
        json.dump(market_listings, file, ensure_ascii=False, indent=2)

def market_cleanup_worker():
    """Ôîíîâàÿ çàäà÷à äëÿ î÷èñòêè ðûíêà"""
    while True:
        try:
            cleanup_expired_listings()
            time.sleep(3600)
        except Exception as e:
            print(f"Îøèáêà â market_cleanup_worker: {e}")
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

# îïà÷êi
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
        user_balances[user_id]['ban_reason'] = f"Àâòîìàòè÷åñêàÿ áëîêèðîâêà çà {MAX_WARNINGS} ïðåäóïðåæäåíèé"
        save_user_data()

        try:
            bot.send_message(user_id,
                f"?? Âû áûëè àâòîìàòè÷åñêè çàáëîêèðîâàíû çà {MAX_WARNINGS} ïðåäóïðåæäåíèé!")
        except:
            pass

def check_ban(user_id, message):
    if user_balances[user_id].get('banned', False):
        bot.reply_to(message,
            f"?? Âû çàáëîêèðîâàíû!\n"
            f"Ïðè÷èíà: {user_balances[user_id].get('ban_reason', 'íå óêàçàíà')}")
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
            print(f"Îøèáêà â check_event_end: {e}")
            time.sleep(300)


event_thread = threading.Thread(target=check_event_end, daemon=True)
event_thread.start()

def group_only(func):
    """Äåêîðàòîð äëÿ îãðàíè÷åíèÿ êîìàíä òîëüêî ðàçðåøåííîé ãðóïïîé"""
    def wrapper(message):
        if message.chat.id != ALLOWED_GROUP_ID:
            if message.chat.type == 'private':
                bot.reply_to(message,
                    "Ýòîò áîò ðàáîòàåò òîëüêî â @chatpartiy\n"
                    f"Ïðèñîåäèíÿéòåñü ê íàøåé ãðóïïå äëÿ èñïîëüçîâàíèÿ áîòà")
            else:
                bot.reply_to(message, "Ýòîò áîò íå ïðåäíàçíà÷åí äëÿ ðàáîòû â ýòîé ãðóïïå!")
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
        f"Ïðèâåòñòâóþ òåáÿ, {user_name}! ??\n"
        f"ß õðàíèòåëü äðåâíèõ òðàäèöèé âåëèêîãî Z èññêóñòâà.\n\n"
        f"Äîñòóïíûå êîìàíäû:\n"
        f"?? /farm - ðàáîòàòü (ðàç â ÷àñ)\n"
        f"? /farmtime - âðåìÿ äî ñëåäóþùåãî ñáîðà\n"
        f"?? /craft [êîëè÷åñòâî] - ñîçäàòü Ôëàã Ðîññèè(100 Zåòîê > 1 )\n"
        f"?? /balance - ïðîâåðèòü ñîêðîâèùíèöó\n"
        f"?? /me - ñâèòîê ïîçíàíèÿ ñåáÿ\n"
        f"\n\n?? Ïîëüçîâàòåëüñêèé ðûíîê:\n"
        f" /market - ïîñìîòðåòü ðûíîê\n"
        f" /market_sell [id] [öåíà] - ïðîäàòü ïðåäìåò\n"
        f" /market_buy [id] - êóïèòü ïðåäìåò\n"
        f" /market_all - âñå ïðåäëîæåíèÿ"
        f"?? /customwork - óñòàíîâèòü ñâîè ôðàçû äëÿ ðàáîòû\n"
        f"?? /top - çàë ñëàâû ìàñòåðîâ\n"
        f"?? /users - ñïèñîê ðàáî÷èõ çàâîäà\n"
        f"/z - ????\n"
        f"?? /clan - óïðàâëåíèå êëàíîì\n"
        f"?? /shop - ëàâêà Ñÿî Ëè\n"
        f"??/price - ïîêóïêà âíóòðèèãðîâîé âàëþòû\n"
        f"?? /tc - ïîäåëèòüñÿ ñîö. Zåòêàìè:\n"
        f"    /tc @username êîëè÷åñòâî\n"
        f"    /tc êîëè÷åñòâî (îòâåòîì íà ñîîáùåíèå)\n\n"
        f"/donate - äîíàò ðóáëÿìè"
        f"Ñèñòåìà êëàíîâ:\n"
        f" Ñîçäàíèå êëàíà: {CLAN_PRICE} Zåòîê\n"
        f" Äîñòóïíûå ðîëè: ?? Ëèäåð, ?? Îôèöåð, ?? Ó÷àñòíèê\n"
        f" Èñïîëüçóéòå /clan äëÿ óïðàâëåíèÿ êëàíîì\n"
        f" Ïîäðîáíàÿ ñïðàâêà: /clan_help"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['price', 'p'])
@group_only
def handle_price(message:Message):
    init_user_data(user_id)

    price_txt = (
        f"Ïðèâåòñòâóþ â ìàãàçèíå èãðîâîé âàëþòû!\n"
        f"Áàçîâàÿ ñòîèìîñòü:\n"
        f"1? = 50 Zåòîê!\n"
        f"1 çâåçäà = 100 Zåòîê!\n"
        f"Ïî âñåì âîïðîñàì - âëàäåëüöó(@alexey_navalyov_1976)"

    )
    bot.reply_to(message, price_txt)

@bot.message_handler(commands=['namaz'])
@group_only
def handle_namaz(message: Message):
    init_user_data(user_id)

    namaz_txt = f"Âû áûòü ïðèçíàíû ïëîõèì óéãóðîì! -100 ñîöèàëüíîãî ðåéòèíãà!\n"
    user_balances[user_id]['leaves'] -= 100

    bot.reply_to(message, namaz_txt)

@bot.message_handler(commands=['donate', 'don'])
@group_only
def handle_donate(message:Message):
    init_user_data(user_id)

    zov_txt = (
        f"ÊÓÏÈÒÜ ÐÓÁËßÌÈ - íåäîñòóïíî,ïîëîæè ìàìåíó êàðòî÷êó"

    )
    bot.reply_to(message, zov_txt)

@bot.message_handler(commands=['kill'])
@group_only
def handle_kill(message: Message):
    try:
        if not HALLOWEEN_EVENT_ACTIVE:
            bot.reply_to(message, "? Õýëëîóèíñêèé èâåíò çàâåðøåí! Êîìàíäà /kill íåäîñòóïíà.")
            return

        user_id = message.from_user.id
        init_user_data(user_id)

        if check_ban(user_id, message):
            return
        if user_balances[user_id].get('kill_ban_until', 0) > datetime.datetime.now().timestamp():
            remaining_time = user_balances[user_id]['kill_ban_until'] - datetime.datetime.now().timestamp()
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            bot.reply_to(message, f"? Âû ìåðòâû! Íå ìîæåòå óáèâàòü åùå {hours}÷ {minutes}ì")
            return

        current_time = datetime.datetime.now().timestamp()
        last_kill = user_balances[user_id].get('last_kill_time', 0)
        if current_time - last_kill < KILL_COOLDOWN:
            remaining = KILL_COOLDOWN - (current_time - last_kill)
            minutes = int(remaining // 60)
            bot.reply_to(message, f"? Âû ìîæåòå óáèâàòü òîëüêî ðàç â 2 ÷àñà! Ïîäîæäèòå åùå {minutes} ìèíóò")
            return

        if not message.reply_to_message:
            bot.reply_to(message, "? Îòâåòüòå ýòîé êîìàíäîé íà ñîîáùåíèå èãðîêà, êîòîðîãî õîòèòå óáèòü!")
            return

        target_id = message.reply_to_message.from_user.id
        init_user_data(target_id)

        if target_id == user_id:
            bot.reply_to(message, "? Íåëüçÿ óáèòü ñàìîãî ñåáÿ!")
            return
        if target_id == 1854264120 and user_id == 6441128051:
            bot.reply_to(message, "íó çà÷åì òû ìåíÿ óáèâàåøü? íó òû æå çíàåøü ÷òî ìíå íåïðèÿòíî è âñå ðàâíî ïðîäîëæàåøü ýòî äåëàòü. íó íåäàâíî æå ïîìèðèëèñü òîëüêî à òåïåðü ñíîâà íà÷èíàåøü åùå è ñìååøüñÿ(")
        if user_balances[target_id].get('kill_ban_until', 0) > datetime.datetime.now().timestamp():
            bot.reply_to(message, "? Ýòîò èãðîê óæå ìåðòâ!")
            return

        user_balances[user_id]['kills'] += 1
        user_balances[user_id]['last_kill_time'] = current_time

        user_balances[target_id]['kill_ban_until'] = current_time + KILL_BAN_DURATION
        user_balances[target_id]['killed_by'] = user_id

        save_user_data()

        killer_name = message.from_user.first_name
        target_name = message.reply_to_message.from_user.first_name

        bot.reply_to(message,
            f"?? Âû óáèëè {target_name}!\n"
            f"?? Âñåãî óáèéñòâ: {user_balances[user_id]['kills']}\n"
            f"? Ñëåäóþùåå óáèéñòâî ÷åðåç 2 ÷àñà")

        try:
            bot.send_message(target_id,
                f"?? Âàñ óáèëè!\n"
                f"? Âû íå ìîæåòå ôàðìèòü è óáèâàòü 2 ÷àñà\n"
                )
        except:
            pass

    except Exception as e:
        print(f"Îøèáêà â handle_kill: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè âûïîëíåíèè êîìàíäû")
@bot.message_handler(commands=['add_promo'])

def handle_add_promo(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 4:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /add_promo íàçâàíèå êîëè÷åñòâî_àêòèâàöèé ñóììà_âîçíàãðàæäåíèÿ\n"
                "Ïðèìåð: /add_promo promo 100 500")
            return

        promo_name = command_parts[1].upper()
        try:
            max_activations = int(command_parts[2])
            reward_amount = int(command_parts[3])
        except ValueError:
            bot.reply_to(message, "? Êîëè÷åñòâî àêòèâàöèé è ñóììà äîëæíû áûòü ÷èñëàìè!")
            return

        if promo_name in promo_codes:
            bot.reply_to(message, "? Ïðîìîêîä ñ òàêèì íàçâàíèåì óæå ñóùåñòâóåò!")
            return

        if max_activations <= 0 or reward_amount <= 0:
            bot.reply_to(message, "? Êîëè÷åñòâî àêòèâàöèé è ñóììà äîëæíû áûòü ïîëîæèòåëüíûìè!")
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
            f"Ïðîìîêîä ñîçäàí!\n\n"
            f"Íàçâàíèå: {promo_name}\n"
            f"Ìàêñèìóì àêòèâàöèé: {max_activations}\n"
            f"Íàãðàäà: {reward_amount} Zåòîê\n"
            f"?? Ñîçäàë: {message.from_user.first_name}")

    except Exception as e:
        print(f"Îøèáêà â handle_add_promo: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ñîçäàíèè ïðîìîêîäà")

@bot.message_handler(commands=['delete_nft'])
def handle_delete_nft(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /delete_nft nft_id\n\n"
                "Ñïèñîê NFT: /nft_list")
            return

        try:
            nft_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "? ID NFT äîëæåí áûòü ÷èñëîì!")
            return


        if nft_id not in user_nfts:
            bot.reply_to(message, "? NFT ñ òàêèì ID íå ñóùåñòâóåò!")
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
                            f"? Àäìèíèñòðàòîð óäàëèë NFT èç âàøåé êîëëåêöèè!\n"
                            f"?? {nft['description']}\n"
                            f"?? ID: {nft_id}")
                    except:
                        pass


        del user_nfts[nft_id]
        save_nft_data()

        bot.reply_to(message,
            f"NFT óñïåøíî óäàëåí!\n\n"
            f"ID: {nft_id}\n"
            f"{nft['description']}\n"
            f"Ðåäêîñòü: {nft['rarity']}")

    except Exception as e:
        print(f"Îøèáêà â handle_delete_nft: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè óäàëåíèè NFT")

@bot.message_handler(commands=['delete_promo'])
def handle_delete_promo(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /delete_promo íàçâàíèå_ïðîìîêîäà")
            return

        promo_name = command_parts[1].upper()

        if promo_name not in promo_codes:
            bot.reply_to(message, "? Ïðîìîêîä íå íàéäåí!")
            return

        # Óäàëÿåì ïðîìîêîä
        del promo_codes[promo_name]
        save_promo_data()

        bot.reply_to(message, f"Ïðîìîêîä {promo_name} óäàëåí!")

    except Exception as e:
        print(f"Îøèáêà â handle_delete_promo: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè óäàëåíèè ïðîìîêîäà")

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
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /use_promo íàçâàíèå_ïðîìîêîäà\n"
                "Ïðèìåð: /use_promo [promo]")
            return

        promo_name = command_parts[1].upper()


        if promo_name not in promo_codes:
            bot.reply_to(message, "? Ïðîìîêîä íå íàéäåí!")
            return

        promo = promo_codes[promo_name]


        if promo['current_activations'] >= promo['max_activations']:
            bot.reply_to(message, "? Ëèìèò àêòèâàöèé ýòîãî ïðîìîêîäà èñ÷åðïàí!")
            return


        if user_id in promo['used_by']:
            bot.reply_to(message, "? Âû óæå èñïîëüçîâàëè ýòîò ïðîìîêîä!")
            return


        if promo_name in user_balances[user_id]['used_promos']:
            bot.reply_to(message, "? Âû óæå èñïîëüçîâàëè ýòîò ïðîìîêîä!")
            return

        reward = promo['reward']
        user_balances[user_id]['leaves'] += reward
        user_balances[user_id]['used_promos'].append(promo_name)


        promo['current_activations'] += 1
        promo['used_by'].append(user_id)

        save_user_data()
        save_promo_data()

        bot.reply_to(message,
            f"Ïðîìîêîä àêòèâèðîâàí!\n\n"
            f"Ïðîìîêîä: {promo_name}\n"
            f"Ïîëó÷åíî: {reward} Zåòîê\n"
            f"Àêòèâàöèé îñòàëîñü: {promo['max_activations'] - promo['current_activations']}\n\n"
            f"Íîâûé áàëàíñ: {user_balances[user_id]['leaves']} Zåòîê")

    except Exception as e:
        print(f"Îøèáêà â handle_use_promo: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè àêòèâàöèè ïðîìîêîäà")

@bot.message_handler(commands=['event', 'event_check'])
@group_only
def handle_event(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)

    if not HALLOWEEN_EVENT_ACTIVE:
        event_text = "? Õýëëîóèíñêèé èâåíò çàâåðøåí!"
    else:
        time_left = HALLOWEEN_END_TIME - datetime.datetime.now().timestamp()
        days = int(time_left // (24 * 60 * 60))
        hours = int((time_left % (24 * 60 * 60)) // 3600)

        event_text = (
            f"?? ÕÝËËÎÓÈÍÑÊÈÉ ÈÂÅÍÒ ÀÊÒÈÂÅÍ! ??\n\n"
            f"?? Êîìàíäà: /kill (îòâåòîì íà ñîîáùåíèå)\n"
            f"? Ìîæíî óáèâàòü ðàç â 2 ÷àñà\n"
            f"?? Óáèòûé èãðîê íå ìîæåò ôàðìèòü 2 ÷àñà\n"
            f"?? Ïîáåäèòåëü (áîëüøå âñåõ óáèéñòâ) ïîëó÷èò:\n"
            f"   ?? Õýëëîóèíñêóþ òûêâó!\n\n"
            f"?? Ñòàòèñòèêà: /killstats\n"
            f"? Îñòàëîñü: {days}ä {hours}÷\n"
            f"?? Èâåíò äî: 09.11.2025 00:00"
        )

    bot.reply_to(message, event_text)

@bot.message_handler(commands=['pumpkins', 'my_pumpkins'])
@group_only
def handle_my_pumpkins(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    response = (
        f"Îñåííèé èâåíò îêîí÷åí\n\n"
    )

    bot.reply_to(message, response)
@bot.message_handler(commands=['zov', 'z'])
@group_only
def handle_petya(message:Message):
    init_user_data(user_id)

    petka1 = ("ïîçäíÿêîâ ãîé")
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
            bot.reply_to(message, f"?? Âû ìåðòâû! Íå ìîæåòå ôàðìèòü åùå {hours}÷ {minutes}ì")
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
                f"Òåêóùèé áàëàíñ:\n"
                f"Zåòîê: {user_balances[user_id]['leaves']}\n"
                f"?? Òåððèòîðèè: {user_balances[user_id]['tea']}"
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
                f"Áàëàíñ:\n"
                f"Zåòîê: {user_balances[user_id]['leaves']}\n"
                f"?? Òåððèòîðèè: {user_balances[user_id]['tea']}\n"
            )



            response += f"\n\n? Ñëåäóþùèé ñáîð áóäåò äîñòóïåí ÷åðåç 1 ÷àñ"

            if 'scroll' in user_balances[user_id]['items']:
                response = response.replace("1 ÷àñ", "50 ìèíóò")

            bot.reply_to(message, response)

        except Exception as e:
            print(f"Îøèáêà ïðè ñáîðå Zåòîê: {e}")
            bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ñáîðå Zåòîê. Ïîïðîáóéòå ïîçæå.")

    except Exception as e:
        print(f"Îáùàÿ îøèáêà â handle_farm: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà íåèçâåñòíàÿ îøèáêà. Ïîïðîáóéòå ïîçæå.")

@bot.message_handler(commands=['balance', 'b'])
@group_only
def handle_balance(message: Message):
    user_id = message.from_user.id
    init_user_data(user_id)

    ban_status = ""
    if user_balances[user_id].get('banned', False):
        ban_status = "\n\n?? Âàø àêêàóíò çàáëîêèðîâàí!"

    response = (
        f"Âàø áàëàíñ:\n"
        f"????Zåòîê: {user_balances[user_id]['leaves']}\n"
        f"?? Òåððèòîðèè: {user_balances[user_id]['tea']}"
        f"{ban_status}"
    )
    bot.reply_to(message, response)
@bot.message_handler(commands=['add_nft'])
def handle_add_nft(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        if not message.reply_to_message or not message.reply_to_message.photo:
            bot.reply_to(message,
                "? Îòâåòüòå ýòîé êîìàíäîé íà ñîîáùåíèå ñ ôîòîãðàôèåé!\n"
                "Ôîðìàò: /add_nft [îïèñàíèå] [ðåäêîñòü]\n"
                "Ïðèìåð: /add_nft Ðåäêèé ñâèòîê ìóäðîñòè rare")
            return

        command_parts = message.text.split(maxsplit=2)
        if len(command_parts) < 3:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /add_nft [îïèñàíèå] [ðåäêîñòü]\n"
                "Ðåäêîñòè: common, rare, epic, legendary")
            return

        description = command_parts[1]
        rarity = command_parts[2].lower()

        if rarity not in ['common', 'rare', 'epic', 'legendary']:
            bot.reply_to(message, "? Íåâåðíàÿ ðåäêîñòü! Èñïîëüçóéòå: common, rare, epic, legendary")
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
            f"? NFT óñïåøíî ñîçäàí!\n\n"
            f"?? ID: {nft_id}\n"
            f"?? Îïèñàíèå: {description}\n"
            f"?? Ðåäêîñòü: {rarity}\n"
            f"?? Ôîòî: ñîõðàíåíî")

    except Exception as e:
        print(f"Îøèáêà â handle_add_nft: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ñîçäàíèè NFT")

@bot.message_handler(commands=['give_nft'])
def handle_give_nft(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /give_nft @username nft_id")
            return

        username = command_parts[1].lstrip('@')
        try:
            nft_id = int(command_parts[2])
        except ValueError:
            bot.reply_to(message, "? ID NFT äîëæåí áûòü ÷èñëîì!")
            return

        # Èùåì ïîëüçîâàòåëÿ
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
            bot.reply_to(message, "? Ïîëüçîâàòåëü íå íàéäåí!")
            return

        if nft_id not in user_nfts:
            bot.reply_to(message, "? NFT ñ òàêèì ID íå ñóùåñòâóåò!")
            return

        if user_nfts[nft_id]['owner'] is not None:
            bot.reply_to(message, "? Ýòîò NFT óæå ïðèíàäëåæèò äðóãîìó èãðîêó!")
            return

        init_user_data(recipient_id)

        # Ïåðåäàåì NFT
        user_nfts[nft_id]['owner'] = recipient_id
        user_balances[recipient_id]['nfts'].append(nft_id)

        save_nft_data()
        save_user_data()

        nft = user_nfts[nft_id]
        rarity_emoji = {
            'common': '?',
            'rare': '??',
            'epic': '??',
            'legendary': '??'
        }.get(nft['rarity'], '?')

        bot.reply_to(message,
            f"? NFT óñïåøíî ïåðåäàí!\n\n"
            f"?? Ïîëó÷àòåëü: {recipient_name}\n"
            f"?? {nft['description']}\n"
            f"{rarity_emoji} Ðåäêîñòü: {nft['rarity']}")

        # Îòïðàâëÿåì NFT ïîëüçîâàòåëþ
        try:
            bot.send_photo(recipient_id, nft['file_id'],
                caption=f"?? Âû ïîëó÷èëè NFT!\n\n"
                       f"?? {nft['description']}\n"
                       f"{rarity_emoji} Ðåäêîñòü: {nft['rarity']}\n"
                       f"?? ID: {nft_id}")
        except Exception as e:
            print(f"Îøèáêà ïðè îòïðàâêå NFT: {e}")

    except Exception as e:
        print(f"Îøèáêà â handle_give_nft: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïåðåäà÷å NFT")

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
            bot.reply_to(message, "?? Ó âàñ ïîêà íåò NFT!")
            return

        response = "?? Âàøà êîëëåêöèÿ NFT:\n\n"

        for nft_id in nft_ids:
            if nft_id in user_nfts:
                nft = user_nfts[nft_id]
                rarity_emoji = {
                    'common': '?',
                    'rare': '??',
                    'epic': '??',
                    'legendary': '??'
                }.get(nft['rarity'], '?')

                response += f"?? {nft_id}: {rarity_emoji} {nft['description']}\n"

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_my_nfts: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïðîñìîòðå êîëëåêöèè")

@bot.message_handler(commands=['killstats', 'kills'])
def handle_killstats(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        if not HALLOWEEN_EVENT_ACTIVE:
            bot.reply_to(message, "? Õýëëîóèíñêèé èâåíò çàâåðøåí!")
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

        response = "?? Õýëëîóèíñêèé èâåíò 2 - Ñòàòèñòèêà óáèéñòâ\n\n?? Òîï óáèéö:\n"

        for i, (name, kills) in enumerate(killers[:10], 1):
            medal = {1: "??", 2: "??", 3: "??"}.get(i, "??")
            response += f"{medal} {i}. {name}: {kills} óáèéñòâ\n"

        user_kills = user_balances[user_id].get('kills', 0)
        user_rank = next((i for i, (_, k) in enumerate(killers, 1) if _ == message.from_user.first_name), None)

        response += f"\nÂàøà ñòàòèñòèêà:\n"
        response += f" Óáèéñòâ: {user_kills}\n"
        response += f"Ðàíã: {user_rank if user_rank else 'íå â òîïå'}\n"

        if user_balances[user_id].get('kill_ban_until', 0) > datetime.datetime.now().timestamp():
            remaining_time = user_balances[user_id]['kill_ban_until'] - datetime.datetime.now().timestamp()
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            response += f"?? Ñòàòóñ: Ìåðòâ (âåðíåòåñü ÷åðåç {hours}÷ {minutes}ì)\n"
        else:
            current_time = datetime.datetime.now().timestamp()
            last_kill = user_balances[user_id].get('last_kill_time', 0)
            if current_time - last_kill < KILL_COOLDOWN:
                remaining = KILL_COOLDOWN - (current_time - last_kill)
                minutes = int(remaining // 60)
                response += f"? Äî ñëåäóþùåãî óáèéñòâà: {minutes} ìèíóò\n"
            else:
                response += f"? Ìîæåòå óáèâàòü!\n"

        response += f"\n?? Èâåíò äëèòñÿ äî 09.11.2025\n?? Ïîáåäèòåëü ïîëó÷èò Õýëëîóèíñêóþ òûêâó!"

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_killstats: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïîëó÷åíèè ñòàòèñòèêè")

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
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /buy_nft nft_id\n\n"
                "?? Äîñòóïíûå NFT: /nft_list")
            return

        try:
            nft_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "? ID NFT äîëæåí áûòü ÷èñëîì!")
            return

        # Ïðîâåðÿåì ñóùåñòâîâàíèå NFT
        if nft_id not in user_nfts:
            bot.reply_to(message, "? NFT ñ òàêèì ID íå ñóùåñòâóåò!")
            return

        nft = user_nfts[nft_id]

        # Ïðîâåðÿåì, íå ïðèíàäëåæèò ëè óæå êîìó-òî
        if nft['owner'] is not None:
            bot.reply_to(message, "? Ýòîò NFT óæå ïðèíàäëåæèò äðóãîìó èãðîêó!")
            return

        if user_balances[user_id]['leaves'] < NFT_BASE_PRICE:
            bot.reply_to(message,
                f"? Íåäîñòàòî÷íî Zåòîê!\n"
                f"Íóæíî: {NFT_BASE_PRICE} Zåòîê\n"
                f"Ó âàñ: {user_balances[user_id]['leaves']} Zåòîê")
            return

        # Ïîêóïàåì NFT
        user_balances[user_id]['leaves'] -= NFT_BASE_PRICE
        user_nfts[nft_id]['owner'] = user_id
        user_balances[user_id]['nfts'].append(nft_id)

        save_nft_data()
        save_user_data()

        rarity_emoji = {
            'common': '?',
            'rare': '??',
            'epic': '??',
            'legendary': '??'
        }.get(nft['rarity'], '?')

        # Îòïðàâëÿåì ïîäòâåðæäåíèå è ñàì NFT
        bot.reply_to(message,
            f"? Âû óñïåøíî ïðèîáðåëè NFT!\n\n"
            f"?? {nft['description']}\n"
            f"{rarity_emoji} Ðåäêîñòü: {nft['rarity']}\n"
            f"?? Ñòîèìîñòü: {NFT_BASE_PRICE} Zåòîê\n"
            f"?? Íîâûé áàëàíñ: {user_balances[user_id]['leaves']} Zåòîê")

        # Îòïðàâëÿåì ôîòî NFT
        try:
            bot.send_photo(user_id, nft['file_id'],
                caption=f"?? Ïîçäðàâëÿåì ñ ïîêóïêîé!\n\n"
                       f"?? {nft['description']}\n"
                       f"{rarity_emoji} Ðåäêîñòü: {nft['rarity']}\n"
                       f"?? ID: {nft_id}\n"
                       f"?? Êóïëåíî çà: {NFT_BASE_PRICE} Zåòîê")
        except Exception as e:
            print(f"Îøèáêà ïðè îòïðàâêå NFT: {e}")

    except Exception as e:
        print(f"Îøèáêà â handle_buy_nft: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïîêóïêå NFT")
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
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /view_nft nft_id")
            return

        try:
            nft_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "? ID NFT äîëæåí áûòü ÷èñëîì!")
            return

        if nft_id not in user_nfts:
            bot.reply_to(message, "? NFT ñ òàêèì ID íå ñóùåñòâóåò!")
            return

        nft = user_nfts[nft_id]
        rarity_emoji = {
            'common': '?',
            'rare': '??',
            'epic': '??',
            'legendary': '??'
        }.get(nft['rarity'], '?')

        if nft['owner'] is None:
            owner_info = f"?? Ñâîáîäåí\n?? Öåíà: {NFT_BASE_PRICE} Zåòîê\n?? Êóïèòü: /buy_nft {nft_id}"
        else:
            try:
                owner = bot.get_chat(nft['owner'])
                owner_info = f"?? Âëàäåëåö: {owner.first_name}"
                if nft['owner'] == user_id:
                    owner_info += " (Âàø NFT)"
            except:
                owner_info = "?? Âëàäåëåö: Íåèçâåñòåí"

        # Îòïðàâëÿåì ôîòî NFT
        bot.send_photo(message.chat.id, nft['file_id'],
            caption=f"?? NFT #{nft_id}\n\n"
                   f"?? {nft['description']}\n"
                   f"{rarity_emoji} Ðåäêîñòü: {nft['rarity']}\n"
                   f"?? Ñîçäàí: {datetime.datetime.fromtimestamp(nft['created_at']).strftime('%d.%m.%Y')}\n"
                   f"{owner_info}")

    except Exception as e:
        print(f"Îøèáêà â handle_view_nft: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïðîñìîòðå NFT")

@bot.message_handler(commands=['nft_list'])
@group_only
def handle_nft_list(message: Message):
    try:
        if not user_nfts:
            bot.reply_to(message, "? Â ñèñòåìå ïîêà íåò NFT!")
            return

        response = "?? Âñå NFT â ñèñòåìå:\n\n"

        for nft_id, nft in user_nfts.items():
            rarity_emoji = {
                'common': '?',
                'rare': '??',
                'epic': '??',
                'legendary': '??'
            }.get(nft['rarity'], '?')

            status = "?? Ñâîáîäåí" if nft['owner'] is None else "?? Â êîëëåêöèè"
            price_info = f"?? {NFT_BASE_PRICE} Zåòîê" if nft['owner'] is None else "?? Ïðîäàíî"
            response += f"?? {nft_id}: {rarity_emoji} {nft['description']} - {status} {price_info}\n"

        response += f"\n?? Âñå NFT ñòîÿò: {NFT_BASE_PRICE} Zåòîê\n"
        response += "?? Äëÿ ïîêóïêè: /buy_nft [id]"

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_nft_list: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïîëó÷åíèè ñïèñêà NFT")
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
        ban_status = "\n\n?? Âàø àêêàóíò çàáëîêèðîâàí!"

    response = (
        f"Ñòàòèñòèêà áîòà:\n"
        f"?? Âñåãî ïîëüçîâàòåëåé: {users_count}\n"
        f"???? Âñåãî çàðàáîòàíî Zåòîê: {total_leaves}\n"
        f"?? Âñåãî òåððèòîðèé: {total_tea}"
        f"{ban_status}"
    )
    bot.reply_to(message, response)

@bot.message_handler(commands=['top'])
@group_only
def handle_top(message: Message):
    # Ñîðòèðóåì ïîëüçîâàòåëåé ïî êîëè÷åñòâó ÷àÿ è Zåòîê
    sorted_users = sorted(
        user_balances.items(),
        key=lambda x: (x[1]['tea'], x[1]['leaves']),
        reverse=True
    )

    # Áåðåì òîï-10 ïîëüçîâàòåëåé
    top_users = sorted_users[:10]

    # Ôîðìèðóåì ñîîáùåíèå
    response = "?? Òîï-10 ñáîðùèêîâ:\n\n"

    for index, (user_id, balance) in enumerate(top_users, 1):
        try:
            user = bot.get_chat(user_id)
            user_name = user.first_name
            # Äîáàâëÿåì ìåäàëè äëÿ ïåðâûõ òðåõ ìåñò
            medal = {1: "??", 2: "??", 3: "??"}.get(index, "??")
            response += f"{medal} {index}. {user_name}: ?? {balance['tea']} | ??{balance['leaves']}\n"
        except:
            response += f"?? {index}. Ïîëüçîâàòåëü:  ?? {balance['tea']} | ?? {balance['leaves']}\n"

    # Â êîíöå äîáàâèì ñòàòóñ áàíà åñëè åñòü
    user_id = message.from_user.id
    init_user_data(user_id)

    if user_balances[user_id].get('banned', False):
        response += "\n\n?? Âàø àêêàóíò çàáëîêèðîâàí!"

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

        # Åñëè êîëè÷åñòâî íå óêàçàíî, óñòàíàâëèâàåì 1
        if len(command_parts) == 1:
            amount = 1
        else:
            try:
                amount = int(command_parts[1])
                if amount <= 0:
                    bot.reply_to(message, "? Êîëè÷åñòâî äîëæíî áûòü ïîëîæèòåëüíûì ÷èñëîì!")
                    return
            except ValueError:
                bot.reply_to(message,
                    "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                    "Èñïîëüçóéòå: /craft [êîëè÷åñòâî]\n"
                    "Íàïðèìåð: /craft 5 èëè ïðîñòî /craft äëÿ çàõâàòà 1 òåððèòîðèè")
                return

        # Áàçîâàÿ ñòîèìîñòü êðàôòà
        base_cost = 100

        # Ïðèìåíÿåì ñêèäêó îò ÷àéíèêà Û åñëè åñòü
        if 'teapot' in user_balances[user_id]['items']:
            base_cost -= SHOP_ITEMS['teapot']['bonus_value']

        total_cost = base_cost * amount

        if user_balances[user_id]['leaves'] < total_cost:
            bot.reply_to(message,
                f"? Íåäîñòàòî÷íî Zåòîê!\n"
                f"Íåîáõîäèìî: {total_cost} Zåòîê\n"
                f"Ó âàñ åñòü: {user_balances[user_id]['leaves']} Zåòîê")
            return

        user_balances[user_id]['leaves'] -= total_cost
        user_balances[user_id]['tea'] += amount
        save_user_data()

        # Ôîðìèðóåì ñîîáùåíèå ñ ó÷åòîì ñêèäêè
        cost_text = str(base_cost)
        if 'teapot' in user_balances[user_id]['items']:
            cost_text = f"{10}(-{SHOP_ITEMS['teapot']['bonus_value']} = {base_cost})"

        craft_message = random.choice(CRAFT_MESSAGES).format(
            count=amount,
            word="÷àÿ" if amount == 1 else "÷àÿ" if 2 <= amount <= 4 else "÷àÿ"
        )

        response = (
            f"{craft_message}\n"
            f"Ïîòðà÷åíî Zåòîê: {cost_text} ? {amount} = {total_cost} \n\n"
            f"Áàëàíñ:\n"
            f"Zåòîê: {user_balances[user_id]['leaves']}\n"
            f"?? Òåððèòîðèè: {user_balances[user_id]['tea']}"
        )

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_craft: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ñîçäàíèè ÷àÿ")




@bot.message_handler(commands=['farmtime'])
@group_only
def handle_farmtime(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        current_time = datetime.datetime.now().timestamp()
        last_farm = user_balances[user_id]['last_farm']

        if can_farm(last_farm, user_id):
            response = "? Âû ìîæåòå ðàáîòàòü\nÈñïîëüçóéòå êîìàíäó /farm"
        else:
            time_until_next = 3600 - (current_time - last_farm)
            remaining_time = format_remaining_time(time_until_next)
            response = f"? Ñëåäóþùàÿ ðàáîòà áóäåò äîñòóïåí ÷åðåç {remaining_time}"

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_farmtime: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïðîâåðêå âðåìåíè. Ïîïðîáóéòå ïîçæå.")

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
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /market_sell [id_ïðåäìåòà] [öåíà]\n"
                "Ïðèìåð: /market_sell scroll 500\n\n"
                "?? Äîñòóïíûå ïðåäìåòû:\n"
                " scroll - ?? Ñâèòîê ìóäðîñòè\n"
                " jade_rod - ?? Íåôðèòîâûé ñòåðæåíü\n"
                " watermelon - ?? Ñâÿùåííûé àðáóç\n"
                " è äðóãèå èç /shop")
            return

        item_id = command_parts[1].lower()
        try:
            price = int(command_parts[2])
        except ValueError:
            bot.reply_to(message, "? Öåíà äîëæíà áûòü ÷èñëîì!")
            return

        if item_id not in SHOP_ITEMS:
            bot.reply_to(message, "? Òàêîãî ïðåäìåòà íå ñóùåñòâóåò!")
            return

        if price < MARKET_MIN_PRICE:
            bot.reply_to(message, f"? Ìèíèìàëüíàÿ öåíà ïðîäàæè: {MARKET_MIN_PRICE} Zåòîê!")
            return

        if item_id not in user_balances[user_id]['items']:
            bot.reply_to(message, "? Ó âàñ íåò ýòîãî ïðåäìåòà!")
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
            f"? Ïðåäìåò âûñòàâëåí íà ðûíîê!\n\n"
            f"?? Ïðåäìåò: {item['name']}\n"
            f"?? Öåíà: {price} Zåòîê\n"
            f"?? Íàëîã: {tax} Zåòîê ({MARKET_TAX_PERCENT}%)\n"
            f"?? Âû ïîëó÷èòå: {seller_receives} Zåòîê\n"
            f"? Äåéñòâóåò: 7 äíåé\n"
            f"?? ID ïðåäëîæåíèÿ: #{listing_id}\n\n"
            f"Äëÿ îòìåíû: /market_cancel {listing_id}")

    except Exception as e:
        print(f"Îøèáêà â handle_market_sell: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè âûñòàâëåíèè ïðåäìåòà íà ðûíîê")

@bot.message_handler(commands=['market', 'm'])
@group_only
def handle_market(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        cleanup_expired_listings()

        if not market_listings:
            bot.reply_to(message, "?? Íà ðûíêå ïîêà íåò ïðåäëîæåíèé!")
            return

        response = "?? Ïîëüçîâàòåëüñêèé ðûíîê\n\n"

        for listing_id, listing in list(market_listings.items())[:10]:  # Ïîêàçûâàåì ïåðâûå 10
            time_left = listing['expires_at'] - datetime.datetime.now().timestamp()
            days = int(time_left // (24 * 60 * 60))
            hours = int((time_left % (24 * 60 * 60)) // 3600)

            response += (
                f"?? #{listing_id} - {listing['item_name']}\n"
                f"?? Öåíà: {listing['price']} Zåòîê\n"
                f"?? Ïðîäàâåö: {listing['seller_name']}\n"
                f"? Îñòàëîñü: {days}ä {hours}÷\n\n"
            )

        response += (
            f"?? Âñåãî ïðåäëîæåíèé: {len(market_listings)}\n"
            f"?? Ïîñìîòðåòü âñå: /market_all\n"
            f"?? Êóïèòü ïðåäìåò: /market_buy [id_ïðåäìåòà]\n"
            f"?? Ïðîäàòü ïðåäìåò: /market_sell [id_ïðåäìåòà] [öåíà]"
        )

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_market: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïðîñìîòðå ðûíêà")

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
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /market_buy [id_ïðåäëîæåíèÿ]\n"
                "Ïðèìåð: /market_buy 1")
            return

        try:
            listing_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "? ID ïðåäëîæåíèÿ äîëæåí áûòü ÷èñëîì!")
            return

        if listing_id not in market_listings:
            bot.reply_to(message, "? Ïðåäëîæåíèå íå íàéäåíî!")
            return

        listing = market_listings[listing_id]

        if datetime.datetime.now().timestamp() > listing['expires_at']:
            del market_listings[listing_id]
            save_market_data()
            bot.reply_to(message, "? Ïðåäëîæåíèå èñòåêëî!")
            return

        if user_id == listing['seller_id']:
            bot.reply_to(message, "? Íåëüçÿ êóïèòü ó ñàìîãî ñåáÿ!")
            return

        if user_balances[user_id]['leaves'] < listing['price']:
            bot.reply_to(message,
                f"? Íåäîñòàòî÷íî Zåòîê!\n"
                f"Íóæíî: {listing['price']} Zåòîê\n"
                f"Ó âàñ: {user_balances[user_id]['leaves']} Zåòîê")
            return

        if len(user_balances[user_id]['items']) >= 3:
            bot.reply_to(message,
                "? Ó âàñ ìàêñèìàëüíîå êîëè÷åñòâî ïðåäìåòîâ!\n"
                "Îñâîáîäèòå ìåñòî: /inventory")
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
            f"? Âû êóïèëè {item_name} çà {listing['price']} Zåòîê!\n"
            f"Ïðåäìåò äîáàâëåí â èíâåíòàðü: /inventory")

        try:
            bot.send_message(seller_id,
                f"?? Âàø ïðåäìåò {item_name} ïðîäàí!\n"
                f"?? Ïîëó÷åíî: {listing['seller_receives']} Zåòîê (çà âû÷åòîì íàëîãà)\n"
                f"?? Ïîêóïàòåëü: {message.from_user.first_name}")
        except:
            pass

    except Exception as e:
        print(f"Îøèáêà â handle_market_buy: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïîêóïêå ïðåäìåòà")

@bot.message_handler(commands=['market_cancel', 'mcancel'])
@group_only
def handle_market_cancel(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /market_cancel [id_ïðåäëîæåíèÿ]")
            return

        try:
            listing_id = int(command_parts[1])
        except ValueError:
            bot.reply_to(message, "? ID ïðåäëîæåíèÿ äîëæåí áûòü ÷èñëîì!")
            return

        if listing_id not in market_listings:
            bot.reply_to(message, "? Ïðåäëîæåíèå íå íàéäåíî!")
            return

        listing = market_listings[listing_id]

        if user_id != listing['seller_id']:
            bot.reply_to(message, "? Ýòî íå âàøå ïðåäëîæåíèå!")
            return

        user_balances[user_id]['items'].append(listing['item_id'])
        del market_listings[listing_id]

        save_user_data()
        save_market_data()

        bot.reply_to(message,
            f"? Ïðåäëîæåíèå #{listing_id} îòìåíåíî!\n"
            f"?? {listing['item_name']} âîçâðàùåí â âàø èíâåíòàðü")

    except Exception as e:
        print(f"Îøèáêà â handle_market_cancel: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè îòìåíå ïðåäëîæåíèÿ")

@bot.message_handler(commands=['market_all', 'mall'])
@group_only
def handle_market_all(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        cleanup_expired_listings()

        if not market_listings:
            bot.reply_to(message, "?? Íà ðûíêå ïîêà íåò ïðåäëîæåíèé!")
            return

        response = "?? Âñå ïðåäëîæåíèÿ íà ðûíêå\n\n"

        for listing_id, listing in market_listings.items():
            time_left = listing['expires_at'] - datetime.datetime.now().timestamp()
            days = int(time_left // (24 * 60 * 60))
            hours = int((time_left % (24 * 60 * 60)) // 3600)

            response += (
                f"?? #{listing_id} - {listing['item_name']}\n"
                f"?? Öåíà: {listing['price']} Zåòîê\n"
                f"?? Ïðîäàâåö: {listing['seller_name']}\n"
                f"? Îñòàëîñü: {days}ä {hours}÷\n"
                f"????????????????????\n"
            )

        response += f"\n?? Âñåãî ïðåäëîæåíèé: {len(market_listings)}"

        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for part in parts:
                bot.send_message(user_id, part)
        else:
            bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_market_all: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïðîñìîòðå ðûíêà")




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
                    "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                    "Ïðè îòâåòå íà ñîîáùåíèå èñïîëüçóéòå:\n"
                    "/tc êîëè÷åñòâî\n"
                    "Íàïðèìåð: /tc 10")
                return

            recipient = message.reply_to_message.from_user
            recipient_id = recipient.id
            recipient_name = recipient.first_name
            amount = int(command_parts[1])

        else:
            if len(command_parts) != 3:
                bot.reply_to(message,
                    "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                    "Èñïîëüçóéòå îäèí èç âàðèàíòîâ:\n"
                    "1. /tc @username êîëè÷åñòâî\n"
                    "2. Îòâåòüòå íà ñîîáùåíèå êîìàíäîé /tc êîëè÷åñòâî")
                return

            recipient_username = command_parts[1].lstrip('@')

            try:
                amount = int(command_parts[2])
            except ValueError:
                bot.reply_to(message, "? Êîëè÷åñòâî Zåòîê äîëæíî áûòü ÷èñëîì!")
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
                        "? Ïîëüçîâàòåëü íå íàéäåí èëè íèêîãäà íå èñïîëüçîâàë áîòà.\n"
                        "Óáåäèòåñü, ÷òî:\n"
                        "1. Óêàçàí ïðàâèëüíûé username\n"
                        "2. Ïîëüçîâàòåëü õîòÿ áû ðàç çàïóñêàë áîòà")
                    return

            except Exception as e:
                print(f"Îøèáêà ïðè ïîèñêå ïîëüçîâàòåëÿ: {e}")
                bot.reply_to(message, "? Íå óäàëîñü íàéòè ïîëüçîâàòåëÿ")
                return

        sender_balance = user_balances[sender_id]['leaves']  # Ïîëó÷àåì êîëè÷åñòâî Zåòîê

        if amount <= 0:
            bot.reply_to(message, "? Êîëè÷åñòâî Zåòîê äîëæíî áûòü ïîëîæèòåëüíûì ÷èñëîì!")
            return

        # Ïðîâåðÿåì äîñòàòî÷íî ëè Zåòîê
        if amount > sender_balance:
            bot.reply_to(message, f"? Ó âàñ íåäîñòàòî÷íî Zåòîê!\nÂàø áàëàíñ: {sender_balance} ??")
            return

        if recipient_id == sender_id:
            bot.reply_to(message, "? Âû íå ìîæåòå îòïðàâèòü Zåòêè ñàìîìó ñåáå!")
            return

        init_user_data(recipient_id)

        user_balances[sender_id]['leaves'] -= amount
        user_balances[recipient_id]['leaves'] += amount

        save_user_data()

        bot.reply_to(message,
            f"? Óñïåøíî îòïðàâëåíî {amount} Zåòîê ïîëüçîâàòåëþ {recipient_name}!\n"
            f"Âàø íîâûé áàëàíñ: {user_balances[sender_id]['leaves']} Zåòîê")

        try:
            bot.send_message(recipient_id,
                f"?? Âû ïîëó÷èëè {amount} Zåòîê îò {message.from_user.first_name}!\n"
                f"Âàø íîâûé áàëàíñ: {user_balances[recipient_id]['leaves']} Zåòîê")
        except Exception as e:
            print(f"Íå óäàëîñü îòïðàâèòü óâåäîìëåíèå ïîëó÷àòåëþ: {e}")

    except Exception as e:
        bot.reply_to(message,
            "? Ïðîèçîøëà îøèáêà ïðè îáðàáîòêå êîìàíäû.\n"
            "Èñïîëüçóéòå îäèí èç âàðèàíòîâ:\n"
            "1. /tñ @username êîëè÷åñòâî\n"
            "2. Îòâåòüòå íà ñîîáùåíèå êîìàíäîé /tñ êîëè÷åñòâî")
        print(f"Îáùàÿ îøèáêà â handle_transfer: {e}")

@bot.message_handler(commands=['customwork'])
@group_only
def handle_custom_work(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        if check_ban(user_id, message):
            return

        # Ïîëó÷àåì òåêñò ïîñëå êîìàíäû
        command_text = message.text.replace('/customwork', '', 1).strip()

        if not command_text:
            # Åñëè ïðîñòî êîìàíäà áåç òåêñòà - ïîêàçûâàåì òåêóùèå ôðàçû
            custom_phrases = user_balances[user_id].get('custom_work', [])

            if not custom_phrases:
                response = (
                    "?? Ó âàñ íåò êàñòîìíûõ ôðàç äëÿ ðàáîòû.\n\n"
                    "×òîáû äîáàâèòü, îòïðàâüòå:\n"
                    "/customwork\n"
                    "Âàøà ôðàçà 1+{count}\n"
                    "Âàøà ôðàçà 2+{count}\n"
                    "(äî 5 ôðàç, êàæäàÿ ñ íîâîé ñòðîêè). ÂÀÆÍÎ! êîìàíäà èìåííî /customwork, áåç @íèê_áîòà"
                )
            else:
                response = "?? Âàøè òåêóùèå ôðàçû äëÿ ðàáîòû:\n\n" + "\n".join(
                    f"{i+1}. {phrase}" for i, phrase in enumerate(custom_phrases)
                ) + "\n\nÎòïðàâüòå /customwork ñ íîâûìè ôðàçàìè äëÿ îáíîâëåíèÿ"

            bot.reply_to(message, response)
            return

        # Ðàçáèâàåì íà ôðàçû (ìàêñèìóì 5)
        phrases = [p.strip() for p in command_text.split('\n') if p.strip()][:5]

        if len(phrases) < 2:
            bot.reply_to(message,
                "? Íóæíî óêàçàòü õîòÿ áû 2 ôðàçû (êàæäàÿ ñ íîâîé ñòðîêè)!\n\n"
                "Ïðèìåð:\n"
                "/customwork\n"
                "Îòëè÷íî ïîðàáîòàë! +{count} Zåòîê\n"
                "Ìîëîäåö! Ïîëó÷àåøü {count} ñîö.Zåòîêîâ")
            return

        # Ñîõðàíÿåì ôðàçû
        user_balances[user_id]['custom_work'] = phrases
        save_user_data()

        bot.reply_to(message,
            f"? Óñòàíîâëåíî {len(phrases)} êàñòîìíûõ ôðàç äëÿ ðàáîòû!\n"
            "Òåïåðü ïðè èñïîëüçîâàíèè /farm áóäóò èñïîëüçîâàòüñÿ âàøè ôðàçû.")

    except Exception as e:
        print(f"Îøèáêà â handle_custom_work: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ñîõðàíåíèè êàñòîìíûõ ôðàç")

@bot.message_handler(commands=['give'])
def handle_give(message: Message):
    try:
        # Ïðîâåðÿåì ïðàâà àäìèíèñòðàòîðà
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        command_parts = message.text.split()

        # Ïðîâåðÿåì ôîðìàò êîìàíäû
        if len(command_parts) != 3:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /give @username êîëè÷åñòâî")
            return

        # Ïîëó÷àåì username ïîëó÷àòåëÿ (óáèðàåì @ åñëè åñòü)
        recipient_username = command_parts[1].lstrip('@')

        try:
            amount = int(command_parts[2])
            if amount <= 0:
                bot.reply_to(message, "? Êîëè÷åñòâî Zåòîê äîëæíî áûòü ïîëîæèòåëüíûì ÷èñëîì!")
                return
        except ValueError:
            bot.reply_to(message, "? Êîëè÷åñòâî Zåòîê äîëæíî áûòü ÷èñëîì!")
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
                    "? Ïîëüçîâàòåëü íå íàéäåí èëè íèêîãäà íå èñïîëüçîâàë áîòà.\n"
                    "Óáåäèòåñü, ÷òî:\n"
                    "1. Óêàçàí ïðàâèëüíûé username\n"
                    "2. Ïîëüçîâàòåëü õîòÿ áû ðàç çàïóñêàë áîòà")
                return

        except Exception as e:
            print(f"Îøèáêà ïðè ïîèñêå ïîëüçîâàòåëÿ: {e}")
            bot.reply_to(message, "? Íå óäàëîñü íàéòè ïîëüçîâàòåëÿ")
            return

        init_user_data(recipient_id)

        user_balances[recipient_id]['leaves'] += amount

        save_user_data()

        bot.reply_to(message,
            f"? Óñïåøíî âûäàíî {amount} Zåòîê ïîëüçîâàòåëþ {recipient_name}!\n"
            f"Åãî íîâûé áàëàíñ: {user_balances[recipient_id]['leaves']} Zåòîê")

        try:
            bot.send_message(recipient_id,
                f"?? Àäìèíèñòðàòîð âûäàë âàì {amount} Zåòîê!\n"
                f"Âàø íîâûé áàëàíñ: {user_balances[recipient_id]['leaves']} Zåòîê")
        except Exception as e:
            print(f"Íå óäàëîñü îòïðàâèòü óâåäîìëåíèå ïîëó÷àòåëþ: {e}")

    except Exception as e:
        bot.reply_to(message,
            "? Ïðîèçîøëà îøèáêà ïðè îáðàáîòêå êîìàíäû.\n"
            "Èñïîëüçóéòå: /give @username êîëè÷åñòâî")
        print(f"Îáùàÿ îøèáêà â handle_give: {e}")

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
            farm_status = "? Äîñòóïåí"
        else:
            time_until_next = 3600 - (current_time - last_farm)
            remaining_time = format_remaining_time(time_until_next)
            farm_status = f"? ×åðåç {remaining_time}"

        warnings = user_balances[user_id].get('warnings', [])
        warnings_text = f"\n?? Ïðåäóïðåæäåíèé: {len(warnings)}/{MAX_WARNINGS}"
        if warnings:
            warnings_text += "\nÏîñëåäíåå ïðåäóïðåæäåíèå:\n"
            last_warn = warnings[-1]
            time_left = WARNING_DURATION - (datetime.datetime.now().timestamp() - last_warn['time'])
            days_left = int(time_left // (24 * 60 * 60))
            warnings_text += f"Ïðè÷èíà: {last_warn['reason']}\n"
            warnings_text += f"Âûäàë: {last_warn['admin']}\n"
            warnings_text += f"Áóäåò ñíÿòî ÷åðåç: {days_left} äíåé"
        response = (
            f"?? Ïðîôèëü èãðîêà\n\n"
            f"Èìÿ: {user.first_name}\n"
            f"ID: {user.id}\n"
            f"Username: @{user.username if user.username else 'îòñóòñòâóåò'}\n\n"
            f"?? Áàëàíñ:\n"
            f"?? Zåòêè: {user_balances[user_id]['leaves']}\n"
            f"?? Òåððèòîðèè: {user_balances[user_id]['tea']}"
            f"?? Ñëåäóþùèé ñáîð: {farm_status}\n"
            f"?? Àäìèíèñòðàòîð: {'Äà' if is_admin(user_id) else 'Íåò'}"
            f"{warnings_text}"
        )

        if user_balances[user_id].get('banned', False):
            response += f"\n\n?? Àêêàóíò çàáëîêèðîâàí!\nÏðè÷èíà: {user_balances[user_id].get('ban_reason', 'íå óêàçàíà')}"

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_me: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïîëó÷åíèè èíôîðìàöèè. Ïîïðîáóéòå ïîçæå.")
@bot.message_handler(commands=['end_event'])
def handle_end_event(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        global HALLOWEEN_EVENT_ACTIVE
        HALLOWEEN_EVENT_ACTIVE = False
        end_halloween_event()

        bot.reply_to(message, "? Õýëëîóèíñêèé èâåíò çàâåðøåí äîñðî÷íî!")

    except Exception as e:
        print(f"Îøèáêà â handle_end_event: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè çàâåðøåíèè èâåíòà")
@bot.message_handler(commands=['admin'])
def handle_admin(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        admin_text = (
            f"?? Ïàíåëü àäìèíèñòðàòîðà\n\n"
            f"Äîñòóïíûå êîìàíäû:\n"
            f"?? /give @username êîëè÷åñòâî - âûäàòü ñîö Zåòîê\n"
            f"?? /take @username êîëè÷åñòâî - çàáðàòü ñîö Zåòîê\n"
            f"?? /reset @username - ñáðîñèòü òàéìåð ñáîðà\n"
            f"?? /stats - ïîäðîáíàÿ ñòàòèñòèêà\n"
            f"?? /announce òåêñò - îòïðàâèòü îáúÿâëåíèå âñåì\n"
            f"?? /warn @username ïðè÷èíà - âûäàòü ïðåäóïðåæäåíèå\n"
            f"? /unwarn @username - ñíÿòü ïðåäóïðåæäåíèå\n"
            f"?? /ban @username ïðè÷èíà - çàáëîêèðîâàòü ïîëüçîâàòåëÿ\n"
            f"?? /unban @username - ðàçáëîêèðîâàòü ïîëüçîâàòåëÿ\n\n"
            f"Ñèñòåìà ïðåäóïðåæäåíèé:\n"
            f" Ïðåäóïðåæäåíèÿ ñíèìàþòñÿ àâòîìàòè÷åñêè ÷åðåç 7 äíåé\n"
            f" Ïðè äîñòèæåíèè {MAX_WARNINGS} ïðåäóïðåæäåíèé - àâòîáàí"
        )
        bot.reply_to(message, admin_text)

    except Exception as e:
        print(f"Îøèáêà â handle_admin: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè îòêðûòèè ïàíåëè àäìèíèñòðàòîðà")

@bot.message_handler(commands=['take'])
def handle_take(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message, "? Èñïîëüçóéòå: /take @username êîëè÷åñòâî")
            return

        recipient_username = command_parts[1].lstrip('@')
        try:
            amount = int(command_parts[2])
            if amount <= 0:
                bot.reply_to(message, "? Êîëè÷åñòâî äîëæíî áûòü ïîëîæèòåëüíûì ÷èñëîì!")
                return
        except ValueError:
            bot.reply_to(message, "? Êîëè÷åñòâî äîëæíî áûòü ÷èñëîì!")
            return

        # Ïîèñê ïîëüçîâàòåëÿ
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
            bot.reply_to(message, "? Ïîëüçîâàòåëü íå íàéäåí!")
            return

        init_user_data(recipient_id)

        # Ïðîâåðÿåì áàëàíñ
        if user_balances[recipient_id]['leaves'] < amount:
            bot.reply_to(message,
                f"? Ó ïîëüçîâàòåëÿ íåäîñòàòî÷íî Zåòîê!\n"
                f"Äîñòóïíî: {user_balances[recipient_id]['leaves']} ??")
            return

        # Çàáèðàåì Zåòêè
        user_balances[recipient_id]['leaves'] -= amount
        save_user_data()

        bot.reply_to(message,
            f"? Óñïåøíî èçúÿòî {amount} Zåòîê ó ïîëüçîâàòåëÿ {recipient_name}!\n"
            f"Åãî íîâûé áàëàíñ: {user_balances[recipient_id]['leaves']} Zåòîê")

        bot.send_message(recipient_id,
            f"?? Àäìèíèñòðàòîð èçúÿë ó âàñ {amount} Zåòîê!\n"
            f"Âàø íîâûé áàëàíñ: {user_balances[recipient_id]['leaves']} Zåòîê")

    except Exception as e:
        print(f"Îøèáêà â handle_take: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè èçúÿòèè Zåòîê")

@bot.message_handler(commands=['stats'])
def handle_stats(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        users_count = len(user_balances)
        total_leaves = sum(u['leaves'] for u in user_balances.values())
        total_tea = sum(u['tea'] for u in user_balances.values())

        # Íàõîäèì ñàìûõ áîãàòûõ ïîëüçîâàòåëåé
        sorted_by_leaves = sorted(user_balances.items(), key=lambda x: x[1]['leaves'], reverse=True)[:5]
        sorted_by_tea = sorted(user_balances.items(), key=lambda x: x[1]['tea'], reverse=True)[:5]

        response = (
            f"?? Ïîäðîáíàÿ ñòàòèñòèêà áîòà\n\n"
            f"?? Âñåãî ïîëüçîâàòåëåé: {users_count}\n"
            f"?? Âñåãî Zåòîê: {total_leaves}\n"
            f"?? Âñåãî òåððèòîðèé: {total_tea}\n\n"
            f"?? Òîï-5 ïî Zåòîêó:\n"
        )

        for i, (user_id, data) in enumerate(sorted_by_leaves, 1):
            try:
                user = bot.get_chat(user_id)
                response += f"{i}. {user.first_name}: {data['leaves']} ??\n"
            except:
                continue

        response += f"\n?? Òîï-5 ïî òåððèòîðèÿì:\n"

        for i, (user_id, data) in enumerate(sorted_by_tea, 1):
            try:
                user = bot.get_chat(user_id)
                response += f"{i}. {user.first_name}: {data['tea']} ??\n"
            except:
                continue

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_stats: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïîëó÷åíèè ñòàòèñòèêè")

@bot.message_handler(commands=['announce'])
def handle_announce(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        announcement_text = message.text.replace('/announce', '', 1).strip()
        if not announcement_text:
            bot.reply_to(message, "? Óêàæèòå òåêñò îáúÿâëåíèÿ!")
            return

        success_count = 0
        fail_count = 0

        for user_id in user_balances.keys():
            try:
                bot.send_message(user_id,
                    f"?? Îáúÿâëåíèå îò àäìèíèñòðàöèè:\n\n"
                    f"{announcement_text}")
                success_count += 1
            except:
                fail_count += 1
                continue

        bot.reply_to(message,
            f"? Îáúÿâëåíèå îòïðàâëåíî!\n"
            f"Óñïåøíî: {success_count}\n"
            f"Íå äîñòàâëåíî: {fail_count}")

    except Exception as e:
        print(f"Îøèáêà â handle_announce: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè îòïðàâêå îáúÿâëåíèÿ")

@bot.message_handler(commands=['reset'])
def handle_reset(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "? Èñïîëüçóéòå: /reset @username")
            return

        recipient_username = command_parts[1].lstrip('@')

        # Ïîèñê ïîëüçîâàòåëÿ
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
            bot.reply_to(message, "? Ïîëüçîâàòåëü íå íàéäåí!")
            return

        # Ñáðàñûâàåì òàéìåð
        user_balances[recipient_id]['last_farm'] = 0
        save_user_data()

        bot.reply_to(message, f"? Òàéìåð ñáîðà äëÿ {recipient_name} ñáðîøåí!")
        bot.send_message(recipient_id, "?? Àäìèíèñòðàòîð ñáðîñèë âàø òàéìåð ñáîðà!\nÂû ìîæåòå ñîáèðàòü Zåòêè!")

    except Exception as e:
        print(f"Îøèáêà â handle_reset: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ñáðîñå òàéìåðà")

@bot.message_handler(commands=['warn'])
def handle_warn(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        command_parts = message.text.split()
        if len(command_parts) < 3:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /warn @username ïðè÷èíà")
            return

        recipient_username = command_parts[1].lstrip('@')
        warn_reason = ' '.join(command_parts[2:])

        # Ïîèñê ïîëüçîâàòåëÿ
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
            bot.reply_to(message, "? Ïîëüçîâàòåëü íå íàéäåí!")
            return

        init_user_data(recipient_id)
        check_warnings(recipient_id)  # Î÷èùàåì óñòàðåâøèå ïðåäóïðåæäåíèÿ

        # Äîáàâëÿåì ïðåäóïðåæäåíèå
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
            f"?? Âûäàíî ïðåäóïðåæäåíèå ïîëüçîâàòåëþ {recipient_name}!\n"
            f"Ïðè÷èíà: {warn_reason}\n"
            f"Âñåãî ïðåäóïðåæäåíèé: {warnings_count}/{MAX_WARNINGS}\n"
            f"Ïðåäóïðåæäåíèå áóäåò ñíÿòî ÷åðåç 7 äíåé"
        )

        if warnings_count >= MAX_WARNINGS:
            response += f"\n\n?? Ïîëüçîâàòåëü àâòîìàòè÷åñêè çàáëîêèðîâàí çà {MAX_WARNINGS} ïðåäóïðåæäåíèé!"

        bot.reply_to(message, response)

        bot.send_message(recipient_id,
            f"?? Âû ïîëó÷èëè ïðåäóïðåæäåíèå!\n"
            f"Ïðè÷èíà: {warn_reason}\n"
            f"Âñåãî ïðåäóïðåæäåíèé: {warnings_count}/{MAX_WARNINGS}\n"
            f"Ïðåäóïðåæäåíèå áóäåò ñíÿòî ÷åðåç 7 äíåé")

    except Exception as e:
        print(f"Îøèáêà â handle_warn: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè âûäà÷å ïðåäóïðåæäåíèÿ")

@bot.message_handler(commands=['ban'])
def handle_ban(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        command_parts = message.text.split()
        if len(command_parts) < 3:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /ban @username ïðè÷èíà")
            return

        recipient_username = command_parts[1].lstrip('@')
        ban_reason = ' '.join(command_parts[2:])

        # Ïîèñê ïîëüçîâàòåëÿ
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
            bot.reply_to(message, "? Ïîëüçîâàòåëü íå íàéäåí!")
            return

        init_user_data(recipient_id)

        # Áëîêèðóåì ïîëüçîâàòåëÿ
        user_balances[recipient_id]['banned'] = True
        user_balances[recipient_id]['ban_reason'] = ban_reason
        save_user_data()

        bot.reply_to(message,
            f"?? Ïîëüçîâàòåëü {recipient_name} çàáëîêèðîâàí!\n"
            f"Ïðè÷èíà: {ban_reason}")

        bot.send_message(recipient_id,
            f"?? Âû áûëè çàáëîêèðîâàíû!\n"
            f"Ïðè÷èíà: {ban_reason}")

    except Exception as e:
        print(f"Îøèáêà â handle_ban: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè áëîêèðîâêå ïîëüçîâàòåëÿ")

@bot.message_handler(commands=['unwarn'])
def handle_unwarn(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /unwarn @username")
            return

        recipient_username = command_parts[1].lstrip('@')

        # Ïîèñê ïîëüçîâàòåëÿ
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
            bot.reply_to(message, "? Ïîëüçîâàòåëü íå íàéäåí!")
            return

        init_user_data(recipient_id)
        check_warnings(recipient_id)  # Î÷èùàåì óñòàðåâøèå ïðåäóïðåæäåíèÿ

        if not user_balances[recipient_id].get('warnings', []):
            bot.reply_to(message, f"? Ó ïîëüçîâàòåëÿ {recipient_name} íåò àêòèâíûõ ïðåäóïðåæäåíèé!")
            return

        # Ñíèìàåì ïîñëåäíåå ïðåäóïðåæäåíèå
        user_balances[recipient_id]['warnings'].pop()
        save_user_data()

        warnings_count = len(user_balances[recipient_id]['warnings'])

        bot.reply_to(message,
            f"? Ñíÿòî ïðåäóïðåæäåíèå ó ïîëüçîâàòåëÿ {recipient_name}!\n"
            f"Îñòàëîñü ïðåäóïðåæäåíèé: {warnings_count}")

        bot.send_message(recipient_id,
            f"? Àäìèíèñòðàòîð ñíÿë ñ âàñ îäíî ïðåäóïðåæäåíèå!\n"
            f"Îñòàëîñü ïðåäóïðåæäåíèé: {warnings_count}")

    except Exception as e:
        print(f"Îøèáêà â handle_unwarn: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ñíÿòèè ïðåäóïðåæäåíèÿ")

@bot.message_handler(commands=['unban'])
def handle_unban(message: Message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñïîëüçîâàíèÿ ýòîé êîìàíäû!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /unban @username")
            return

        recipient_username = command_parts[1].lstrip('@')

        # Ïîèñê ïîëüçîâàòåëÿ
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
            bot.reply_to(message, "? Ïîëüçîâàòåëü íå íàéäåí!")
            return

        init_user_data(recipient_id)

        # Ïðîâåðÿåì, çàáàíåí ëè ïîëüçîâàòåëü
        if not user_balances[recipient_id].get('banned', False):
            bot.reply_to(message, f"? Ïîëüçîâàòåëü {recipient_name} íå çàáëîêèðîâàí!")
            return

        # Ðàçáëîêèðóåì ïîëüçîâàòåëÿ
        user_balances[recipient_id]['banned'] = False
        user_balances[recipient_id]['ban_reason'] = ''
        user_balances[recipient_id]['warnings'] = []  # Î÷èùàåì âñå ïðåäóïðåæäåíèÿ
        save_user_data()

        bot.reply_to(message,
            f"? Ïîëüçîâàòåëü {recipient_name} ðàçáëîêèðîâàí!\n"
            f"Âñå ïðåäóïðåæäåíèÿ ñíÿòû.")

        bot.send_message(recipient_id,
            "?? Âàø àêêàóíò ðàçáëîêèðîâàí!\n"
            "Âñå ïðåäóïðåæäåíèÿ ñíÿòû.\n"
            "Òåïåðü âû ñíîâà ìîæåòå ïîëüçîâàòüñÿ áîòîì.")

    except Exception as e:
        print(f"Îøèáêà â handle_unban: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ðàçáëîêèðîâêå ïîëüçîâàòåëÿ")

@bot.message_handler(commands=['clan'])
@group_only
def handle_clan(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        if check_ban(user_id, message):
            return

        # Åñëè ó ïîëüçîâàòåëÿ íåò êëàíà
        if not user_balances[user_id]['clan']:
            response = (
                f"?? Ñèñòåìà êëàíîâ\n\n"
                f"Âû íå ñîñòîèòå â êëàíå.\n"
                f"Äîñòóïíûå äåéñòâèÿ:\n"
                f" /clan_create [íàçâàíèå] - ñîçäàòü êëàí ({CLAN_PRICE} Zåòîê)\n"
                f" /clan_join [íàçâàíèå] - âñòóïèòü â êëàí\n"
                f" /clan_list - ñïèñîê êëàíîâ\n\n"
                f"? Èñïîëüçóéòå /clan_help äëÿ ïîäðîáíîé èíôîðìàöèè î ñèñòåìå êëàíîâ"
            )
        else:
            clan_id = user_balances[user_id]['clan']
            clan = clans[clan_id]
            role = user_balances[user_id]['clan_role']

            members = [uid for uid, data in user_balances.items() if data.get('clan') == clan_id]

            response = (
                f"?? Êëàí «{clan['name']}»\n\n"
                f"?? Ëèäåð: {get_username(clan['leader'])}\n"
                f"?? Ó÷àñòíèêîâ: {len(members)}\n"
                f"?? Âàøà ðîëü: {get_role_name(role)}\n\n"
            )

            if role in ['leader', 'officer']:
                response += (
                    f"Êîìàíäû óïðàâëåíèÿ:\n"
                    f" /clan_invite @username - ïðèãëàñèòü èãðîêà\n"
                    f" /clan_kick @username - èñêëþ÷èòü èãðîêà\n"
                    f" /clan_promote @username - ïîâûñèòü äî îôèöåðà\n"
                    f" /clan_demote @username - ïîíèçèòü äî ó÷àñòíèêà\n"
                )

            response += (
                f"\nÎáùèå êîìàíäû:\n"
                f" /clan_members - ñïèñîê ó÷àñòíèêîâ\n"
                f" /clan_leave - ïîêèíóòü êëàí"
            )

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_clan: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ðàáîòå ñ êëàíîì")

@bot.message_handler(commands=['clan_create'])
@group_only
def handle_clan_create(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        if check_ban(user_id, message):
            return

        # Ïðîâåðÿåì, íå ñîñòîèò ëè óæå â êëàíå
        if user_balances[user_id]['clan']:
            bot.reply_to(message, "? Âû óæå ñîñòîèòå â êëàíå!")
            return

        # Ïðîâåðÿåì ôîðìàò êîìàíäû
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Óêàæèòå íàçâàíèå êëàíà!\n"
                "Èñïîëüçîâàíèå: /clan_create [íàçâàíèå]")
            return

        clan_name = command_parts[1].strip()

        # Ïðîâåðÿåì äëèíó íàçâàíèÿ
        if len(clan_name) < MIN_CLAN_NAME_LENGTH or len(clan_name) > MAX_CLAN_NAME_LENGTH:
            bot.reply_to(message,
                f"? Íàçâàíèå êëàíà äîëæíî áûòü îò {MIN_CLAN_NAME_LENGTH} "
                f"äî {MAX_CLAN_NAME_LENGTH} ñèìâîëîâ!")
            return

        # Ïðîâåðÿåì, íå ñóùåñòâóåò ëè êëàí ñ òàêèì íàçâàíèåì
        if any(c['name'].lower() == clan_name.lower() for c in clans.values()):
            bot.reply_to(message, "? Êëàí ñ òàêèì íàçâàíèåì óæå ñóùåñòâóåò!")
            return

        # Ïðîâåðÿåì íàëè÷èå Zåòîê
        if user_balances[user_id]['leaves'] < CLAN_PRICE:
            bot.reply_to(message,
                f"? Íåäîñòàòî÷íî Zåòîê äëÿ ñîçäàíèÿ êëàíà!\n"
                f"Íåîáõîäèìî: {CLAN_PRICE} Zåòîê\n"
                f"Ó âàñ åñòü: {user_balances[user_id]['leaves']} Zåòîê")
            return

        # Ñîçäàåì êëàí
        clan_id = str(len(clans) + 1)
        clans[clan_id] = {
            'name': clan_name,
            'leader': user_id,
            'created_at': datetime.datetime.now().timestamp()
        }

        # Îáíîâëÿåì äàííûå ïîëüçîâàòåëÿ
        user_balances[user_id]['leaves'] -= CLAN_PRICE
        user_balances[user_id]['clan'] = clan_id
        user_balances[user_id]['clan_role'] = 'leader'

        save_user_data()
        save_clans_data()

        bot.reply_to(message,
            f"?? Ïîçäðàâëÿåì! Êëàí «{clan_name}» óñïåøíî ñîçäàí!\n"
            f"Ïîòðà÷åíî: {CLAN_PRICE} Zåòîê\n\n"
            f"Èñïîëüçóéòå /clan äëÿ óïðàâëåíèÿ êëàíîì")

    except Exception as e:
        print(f"Îøèáêà â handle_clan_create: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ñîçäàíèè êëàíà")

@bot.message_handler(commands=['clan_help'])
@group_only
def handle_clan_help(message: Message):
    help_text = (
        f"?? Ðóêîâîäñòâî ïî ñèñòåìå êëàíîâ\n\n"
        f"?? Îñíîâíûå êîìàíäû:\n"
        f" /clan - ïðîñìîòð èíôîðìàöèè î êëàíå\n"
        f" /clan_create [íàçâàíèå] - ñîçäàòü êëàí ({CLAN_PRICE} Zåòîê)\n"
        f" /clan_list - ñïèñîê âñåõ êëàíîâ\n"
        f" /clan_join [íàçâàíèå] - âñòóïèòü â êëàí\n"
        f" /clan_leave - ïîêèíóòü êëàí\n"
        f" /clan_members - ñïèñîê ó÷àñòíèêîâ êëàíà\n\n"

        f"?? Êîìàíäû óïðàâëåíèÿ (äëÿ ëèäåðà è îôèöåðîâ):\n"
        f" /clan_invite @username - ïðèãëàñèòü èãðîêà\n"
        f" /clan_kick @username - èñêëþ÷èòü èãðîêà\n"
        f" /clan_promote @username - ïîâûñèòü äî îôèöåðà\n"
        f" /clan_demote @username - ïîíèçèòü äî ó÷àñòíèêà\n\n"

        f"?? Ðîëè â êëàíå:\n"
        f" ?? Ëèäåð - ñîçäàòåëü êëàíà, ïîëíûé äîñòóï\n"
        f" ?? Îôèöåð - ìîæåò óïðàâëÿòü ó÷àñòíèêàìè\n"
        f" ?? Ó÷àñòíèê - áàçîâûé äîñòóï\n\n"

        f"? Êàê âñòóïèòü â êëàí:\n"
        f"1. Ïîñìîòðèòå ñïèñîê êëàíîâ: /clan_list\n"
        f"2. Ïîäàéòå çàÿâêó: /clan_join [íàçâàíèå]\n"
        f"3. Äîæäèòåñü îäîáðåíèÿ îò ëèäåðà/îôèöåðà\n\n"

        f"? Êàê ñîçäàòü ñâîé êëàí:\n"
        f"1. Íàêîïèòå {CLAN_PRICE} Zåòîê\n"
        f"2. Ïðèäóìàéòå íàçâàíèå (îò {MIN_CLAN_NAME_LENGTH} äî {MAX_CLAN_NAME_LENGTH} ñèìâîëîâ)\n"
        f"3. Ñîçäàéòå êëàí: /clan_create [íàçâàíèå]"
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

        # Ïðîâåðÿåì, ñîñòîèò ëè ïîëüçîâàòåëü â êëàíå
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "? Âû íå ñîñòîèòå â êëàíå!")
            return

        # Ïðîâåðÿåì ïðàâà ïîëüçîâàòåëÿ
        user_role = user_balances[user_id]['clan_role']
        if user_role not in ['leader', 'officer']:
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ ïðèãëàøåíèÿ èãðîêîâ!")
            return

        # Ïðîâåðÿåì ôîðìàò êîìàíäû
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /clan_invite @username")
            return

        target_username = command_parts[1].lstrip('@')

        # Èùåì ïîëüçîâàòåëÿ
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
            bot.reply_to(message, "? Ïîëüçîâàòåëü íå íàéäåí!")
            return

        # Ïðîâåðÿåì, íå ñîñòîèò ëè óæå â êëàíå
        if user_balances[target_id]['clan']:
            bot.reply_to(message, "? Ýòîò èãðîê óæå ñîñòîèò â êëàíå!")
            return

        # Äîáàâëÿåì â êëàí
        clan_id = user_balances[user_id]['clan']
        user_balances[target_id]['clan'] = clan_id
        user_balances[target_id]['clan_role'] = 'member'
        save_user_data()

        clan_name = clans[clan_id]['name']

        bot.reply_to(message,
            f"? Èãðîê {target_name} óñïåøíî ïðèãëàø¸í â êëàí!")

        bot.send_message(target_id,
            f"?? Âàñ ïðèãëàñèëè â êëàí «{clan_name}»!\n"
            f"Èñïîëüçóéòå /clan äëÿ ïðîñìîòðà èíôîðìàöèè")

    except Exception as e:
        print(f"Îøèáêà â handle_clan_invite: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïðèãëàøåíèè èãðîêà")

@bot.message_handler(commands=['clan_kick'])
@group_only
def handle_clan_kick(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        if check_ban(user_id, message):
            return

        # Ïðîâåðÿåì, ñîñòîèò ëè ïîëüçîâàòåëü â êëàíå
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "? Âû íå ñîñòîèòå â êëàíå!")
            return

        # Ïðîâåðÿåì ïðàâà ïîëüçîâàòåëÿ
        user_role = user_balances[user_id]['clan_role']
        if user_role not in ['leader', 'officer']:
            bot.reply_to(message, "? Ó âàñ íåò ïðàâ äëÿ èñêëþ÷åíèÿ èãðîêîâ!")
            return

        # Ïðîâåðÿåì ôîðìàò êîìàíäû
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /clan_kick @username")
            return

        target_username = command_parts[1].lstrip('@')

        # Èùåì ïîëüçîâàòåëÿ
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
            bot.reply_to(message, "? Ïîëüçîâàòåëü íå íàéäåí!")
            return

        # Ïðîâåðÿåì, ñîñòîèò ëè èãðîê â òîì æå êëàíå
        clan_id = user_balances[user_id]['clan']
        if user_balances[target_id].get('clan') != clan_id:
            bot.reply_to(message, "? Ýòîò èãðîê íå ñîñòîèò â âàøåì êëàíå!")
            return

        # Ïðîâåðÿåì, íå ïûòàåòñÿ ëè îôèöåð èñêëþ÷èòü ëèäåðà èëè äðóãîãî îôèöåðà
        if user_role == 'officer' and user_balances[target_id]['clan_role'] in ['leader', 'officer']:
            bot.reply_to(message, "? Âû íå ìîæåòå èñêëþ÷èòü ëèäåðà èëè îôèöåðà!")
            return

        # Èñêëþ÷àåì èãðîêà
        user_balances[target_id]['clan'] = None
        user_balances[target_id]['clan_role'] = None
        save_user_data()

        bot.reply_to(message, f"? Èãðîê {target_name} èñêëþ÷¸í èç êëàíà!")
        bot.send_message(target_id, f"? Âû áûëè èñêëþ÷åíû èç êëàíà!")

    except Exception as e:
        print(f"Îøèáêà â handle_clan_kick: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè èñêëþ÷åíèè èãðîêà")

@bot.message_handler(commands=['clan_promote'])
@group_only
def handle_clan_promote(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        if check_ban(user_id, message):
            return

        # Ïðîâåðÿåì, ñîñòîèò ëè ïîëüçîâàòåëü â êëàíå
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "? Âû íå ñîñòîèòå â êëàíå!")
            return

        # Òîëüêî ëèäåð ìîæåò ïîâûøàòü
        if user_balances[user_id]['clan_role'] != 'leader':
            bot.reply_to(message, "? Òîëüêî ëèäåð êëàíà ìîæåò ïîâûøàòü ó÷àñòíèêîâ!")
            return

        # Ïðîâåðÿåì ôîðìàò êîìàíäû
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /clan_promote @username")
            return

        target_username = command_parts[1].lstrip('@')

        # Èùåì ïîëüçîâàòåëÿ
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
            bot.reply_to(message, "? Ïîëüçîâàòåëü íå íàéäåí!")
            return

        # Ïðîâåðÿåì, ñîñòîèò ëè èãðîê â òîì æå êëàíå
        clan_id = user_balances[user_id]['clan']
        if user_balances[target_id].get('clan') != clan_id:
            bot.reply_to(message, "? Ýòîò èãðîê íå ñîñòîèò â âàøåì êëàíå!")
            return

        # Ïðîâåðÿåì òåêóùóþ ðîëü
        if user_balances[target_id]['clan_role'] == 'officer':
            bot.reply_to(message, "? Ýòîò èãðîê óæå ÿâëÿåòñÿ îôèöåðîì!")
            return

        # Ïîâûøàåì äî îôèöåðà
        user_balances[target_id]['clan_role'] = 'officer'
        save_user_data()

        bot.reply_to(message, f"? Èãðîê {target_name} ïîâûøåí äî îôèöåðà!")
        bot.send_message(target_id, "?? Ïîçäðàâëÿåì! Âû ïîâûøåíû äî îôèöåðà êëàíà!")

    except Exception as e:
        print(f"Îøèáêà â handle_clan_promote: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïîâûøåíèè èãðîêà")

@bot.message_handler(commands=['clan_demote'])
@group_only
def handle_clan_demote(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        if check_ban(user_id, message):
            return

        # Ïðîâåðÿåì, ñîñòîèò ëè ïîëüçîâàòåëü â êëàíå
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "? Âû íå ñîñòîèòå â êëàíå!")
            return

        # Òîëüêî ëèäåð ìîæåò ïîíèæàòü
        if user_balances[user_id]['clan_role'] != 'leader':
            bot.reply_to(message, "? Òîëüêî ëèäåð êëàíà ìîæåò ïîíèæàòü îôèöåðîâ!")
            return

        # Ïðîâåðÿåì ôîðìàò êîìàíäû
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /clan_demote @username")
            return

        target_username = command_parts[1].lstrip('@')

        # Èùåì ïîëüçîâàòåëÿ
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
            bot.reply_to(message, "? Ïîëüçîâàòåëü íå íàéäåí!")
            return

        # Ïðîâåðÿåì, ñîñòîèò ëè èãðîê â òîì æå êëàíå
        clan_id = user_balances[user_id]['clan']
        if user_balances[target_id].get('clan') != clan_id:
            bot.reply_to(message, "? Ýòîò èãðîê íå ñîñòîèò â âàøåì êëàíå!")
            return

        # Ïðîâåðÿåì òåêóùóþ ðîëü
        if user_balances[target_id]['clan_role'] != 'officer':
            bot.reply_to(message, "? Ýòîò èãðîê íå ÿâëÿåòñÿ îôèöåðîì!")
            return

        # Ïîíèæàåì äî ó÷àñòíèêà
        user_balances[target_id]['clan_role'] = 'member'
        save_user_data()

        bot.reply_to(message, f"? Èãðîê {target_name} ïîíèæåí äî ó÷àñòíèêà!")
        bot.send_message(target_id, "?? Âû ïîíèæåíû äî îáû÷íîãî ó÷àñòíèêà êëàíà")

    except Exception as e:
        print(f"Îøèáêà â handle_clan_demote: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïîíèæåíèè èãðîêà")

@bot.message_handler(commands=['clan_members'])
@group_only
def handle_clan_members(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        if check_ban(user_id, message):
            return

        # Ïðîâåðÿåì, ñîñòîèò ëè ïîëüçîâàòåëü â êëàíå
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "? Âû íå ñîñòîèòå â êëàíå!")
            return

        clan_id = user_balances[user_id]['clan']
        clan = clans[clan_id]

        # Ñîáèðàåì ñïèñîê ó÷àñòíèêîâ
        members = []
        for uid, data in user_balances.items():
            if data.get('clan') == clan_id:
                role = get_role_name(data['clan_role'])
                try:
                    username = bot.get_chat(uid).first_name
                    members.append((role, username))
                except:
                    continue

        # Ñîðòèðóåì ïî ðîëÿì: ëèäåð -> îôèöåðû -> ó÷àñòíèêè
        role_priority = {'?? Ëèäåð': 0, '?? Îôèöåð': 1, '?? Ó÷àñòíèê': 2}
        members.sort(key=lambda x: role_priority[x[0]])

        response = f"?? Ó÷àñòíèêè êëàíà «{clan['name']}»:\n\n"
        for role, username in members:
            response += f"{role}: {username}\n"

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_clan_members: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïîëó÷åíèè ñïèñêà ó÷àñòíèêîâ")

@bot.message_handler(commands=['clan_leave'])
@group_only
def handle_clan_leave(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        if check_ban(user_id, message):
            return

        # Ïðîâåðÿåì, ñîñòîèò ëè ïîëüçîâàòåëü â êëàíå
        if not user_balances[user_id]['clan']:
            bot.reply_to(message, "? Âû íå ñîñòîèòå â êëàíå!")
            return

        clan_id = user_balances[user_id]['clan']
        clan_name = clans[clan_id]['name']

        # Ïðîâåðÿåì, íå ÿâëÿåòñÿ ëè ïîëüçîâàòåëü ëèäåðîì
        if user_balances[user_id]['clan_role'] == 'leader':
            # Èùåì îôèöåðà äëÿ ïåðåäà÷è ëèäåðñòâà
            new_leader = None
            for uid, data in user_balances.items():
                if data.get('clan') == clan_id and data['clan_role'] == 'officer':
                    new_leader = uid
                    break

            if new_leader:
                # Ïåðåäàåì ëèäåðñòâî îôèöåðó
                user_balances[new_leader]['clan_role'] = 'leader'
                clans[clan_id]['leader'] = new_leader
                save_clans_data()

                try:
                    bot.send_message(new_leader,
                        f"?? Âû ñòàëè íîâûì ëèäåðîì êëàíà «{clan_name}»!")
                except:
                    pass
            else:
                # Åñëè íåò îôèöåðîâ, óäàëÿåì êëàí
                del clans[clan_id]
                save_clans_data()

                # Óáèðàåì êëàí ó âñåõ ó÷àñòíèêîâ
                for uid, data in user_balances.items():
                    if data.get('clan') == clan_id:
                        data['clan'] = None
                        data['clan_role'] = None
                        try:
                            if uid != user_id:
                                bot.send_message(uid,
                                    f"? Êëàí «{clan_name}» áûë ðàñôîðìèðîâàí!")
                        except:
                            continue

                save_user_data()
                bot.reply_to(message,
                    f"? Êëàí «{clan_name}» ðàñôîðìèðîâàí, òàê êàê âû áûëè ïîñëåäíèì îôèöåðîì!")
                return

        # Ïîêèäàåì êëàí
        user_balances[user_id]['clan'] = None
        user_balances[user_id]['clan_role'] = None
        save_user_data()

        bot.reply_to(message, f"? Âû ïîêèíóëè êëàí «{clan_name}»")

    except Exception as e:
        print(f"Îøèáêà â handle_clan_leave: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè âûõîäå èç êëàíà")

@bot.message_handler(commands=['clan_list'])
@group_only
def handle_clan_list(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        if check_ban(user_id, message):
            return

        if not clans:
            bot.reply_to(message, "? Ïîêà íåò íè îäíîãî êëàíà!")
            return

        response = "?? Ñïèñîê êëàíîâ:\n\n"

        for clan_id, clan_data in clans.items():
            # Ñ÷èòàåì êîëè÷åñòâî ó÷àñòíèêîâ
            members_count = sum(1 for data in user_balances.values()
                              if data.get('clan') == clan_id)

            # Ïîëó÷àåì èìÿ ëèäåðà
            leader_name = get_username(clan_data['leader'])

            response += (
                f"?? «{clan_data['name']}»\n"
                f"?? Ëèäåð: {leader_name}\n"
                f"?? Ó÷àñòíèêîâ: {members_count}\n\n"
            )

        response += "×òîáû âñòóïèòü â êëàí, èñïîëüçóéòå:\n/clan_join [íàçâàíèå]"

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_clan_list: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïîëó÷åíèè ñïèñêà êëàíîâ")

@bot.message_handler(commands=['clan_join'])
@group_only
def handle_clan_join(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        if check_ban(user_id, message):
            return

        # Ïðîâåðÿåì, íå ñîñòîèò ëè óæå â êëàíå
        if user_balances[user_id]['clan']:
            bot.reply_to(message, "? Âû óæå ñîñòîèòå â êëàíå!")
            return

        # Ïðîâåðÿåì ôîðìàò êîìàíäû
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) != 2:
            bot.reply_to(message,
                "? Óêàæèòå íàçâàíèå êëàíà!\n"
                "Èñïîëüçîâàíèå: /clan_join [íàçâàíèå]")
            return

        clan_name = command_parts[1].strip()

        # Âûâîäèì îòëàäî÷íóþ èíôîðìàöèþ
        print(f"Ïîèñê êëàíà: {clan_name}")
        print(f"Äîñòóïíûå êëàíû: {clans}")

        # Èùåì êëàí ïî íàçâàíèþ (áåç ó÷åòà ðåãèñòðà)
        clan_found = False
        for clan_id, clan_data in clans.items():
            print(f"Ñðàâíèâàåì ñ: {clan_data['name']}")
            if clan_data['name'].lower() == clan_name.lower():
                clan_found = True
                print(f"Êëàí íàéäåí! ID: {clan_id}")
                # Äîáàâëÿåì ïîëüçîâàòåëÿ â êëàí
                user_balances[user_id]['clan'] = clan_id
                user_balances[user_id]['clan_role'] = 'member'
                save_user_data()

                # Óâåäîìëÿåì ëèäåðà
                try:
                    leader_id = clan_data['leader']
                    bot.send_message(leader_id,
                        f"?? {message.from_user.first_name} ïðèñîåäèíèëñÿ ê êëàíó!")
                except Exception as e:
                    print(f"Îøèáêà ïðè óâåäîìëåíèè ëèäåðà: {e}")

                bot.reply_to(message,
                    f"? Âû óñïåøíî âñòóïèëè â êëàí «{clan_data['name']}»!\n"
                    f"Èñïîëüçóéòå /clan äëÿ ïðîñìîòðà èíôîðìàöèè")
                break

        if not clan_found:
            bot.reply_to(message,
                "? Êëàí ñ òàêèì íàçâàíèåì íå íàéäåí!\n"
                "Èñïîëüçóéòå /clan_list äëÿ ïðîñìîòðà ñïèñêà êëàíîâ")

    except Exception as e:
        print(f"Îøèáêà â handle_clan_join: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè âñòóïëåíèè â êëàí")

# Âñïîìîãàòåëüíûå ôóíêöèè
def get_username(user_id):
    try:
        user = bot.get_chat(user_id)
        return user.first_name
    except:
        return "Íåèçâåñòíûé"

def get_role_name(role):
    return {
        'leader': '?? Ëèäåð',
        'officer': '?? Îôèöåð',
        'member': '?? Ó÷àñòíèê'
    }.get(role, '? Íåèçâåñòíî')

@bot.message_handler(commands=['shop'])
@group_only
def handle_shop(message: Message):
    try:
        user_id = message.from_user.id
        init_user_data(user_id)

        if check_ban(user_id, message):
            return

        response = "?? Ìàãàçèí ïðåäìåòîâ\n\n"

        for item in SHOP_ITEMS.values():
            response += (
                f"{item['name']}\n"
                f"?? {item['description']}\n"
                f"?? Öåíà: {item['price']} Zåòîê\n"
                f"?? Äëÿ ïîêóïêè: /buy {item['id']}\n\n"
            )

        response += (
            f"Ó âàñ: {user_balances[user_id]['leaves']} Zåòîê\n"
            f"Ìàêñèìóì ïðåäìåòîâ: 3\n"
            f"Âàøè ïðåäìåòû: /inventory\n\n"
            f"?? NFT êîëëåêöèÿ\n"
            f"?? Áàçîâàÿ öåíà: {NFT_BASE_PRICE} Zåòîê\n"
            f"?? Ïîñìîòðåòü NFT: /nft_list\n"
            f"?? Êóïèòü NFT: /buy_nft [id]\n\n"


        )


        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_shop: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè îòêðûòèè ìàãàçèíà")

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
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /buy [id_ïðåäìåòà]")
            return

        item_id = command_parts[1].lower()

        if item_id not in SHOP_ITEMS:
            bot.reply_to(message, "? Ïðåäìåò íå íàéäåí!")
            return

        item = SHOP_ITEMS[item_id]

        # Ïðîâåðÿåì êîëè÷åñòâî ïðåäìåòîâ
        if len(user_balances[user_id]['items']) >= 3:
            bot.reply_to(message,
                "? Ó âàñ óæå ìàêñèìàëüíîå êîëè÷åñòâî ïðåäìåòîâ!\n"
                "Èñïîëüçóéòå /inventory äëÿ ïðîñìîòðà è /drop [id_ïðåäìåòà] äëÿ óäàëåíèÿ")
            return

        # Ïðîâåðÿåì, åñòü ëè óæå òàêîé ïðåäìåò
        if item_id in user_balances[user_id]['items']:
            bot.reply_to(message, "? Ó âàñ óæå åñòü ýòîò ïðåäìåò!")
            return

        # Ïðîâåðÿåì íàëè÷èå Zåòîê
        if user_balances[user_id]['leaves'] < item['price']:
            bot.reply_to(message,
                f"? Íåäîñòàòî÷íî Zåòîê!\n"
                f"Íåîáõîäèìî: {item['price']} Zåòîê\n"
                f"Ó âàñ åñòü: {user_balances[user_id]['leaves']} Zåòîê")
            return

        # Ïîêóïàåì ïðåäìåò
        user_balances[user_id]['leaves'] -= item['price']
        user_balances[user_id]['items'].append(item_id)
        save_user_data()

        bot.reply_to(message,
            f"? Âû óñïåøíî ïðèîáðåëè {item['name']}!\n"
            f"Îñòàëîñü òåððèòîðèé: {user_balances[user_id]['leaves']} Zåòîê")

    except Exception as e:
        print(f"Îøèáêà â handle_buy: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè ïîêóïêå ïðåäìåòà")

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
                "?? Âàø èíâåíòàðü ïóñò!\n"
                "Èñïîëüçóéòå /shop äëÿ ïîêóïêè ïðåäìåòîâ")
            return

        response = "?? Âàø èíâåíòàðü:\n\n"

        for item_id in items:
            item = SHOP_ITEMS[item_id]
            response += (
                f"{item['name']}\n"
                f"?? {item['description']}\n"
                f"? Äëÿ óäàëåíèÿ: /drop {item_id}\n\n"
            )

        response += f"Âñåãî ïðåäìåòîâ: {len(items)}/3"

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Îøèáêà â handle_inventory: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè îòêðûòèè èíâåíòàðÿ")

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
                "? Íåâåðíûé ôîðìàò êîìàíäû!\n"
                "Èñïîëüçóéòå: /drop [id_ïðåäìåòà]")
            return

        item_id = command_parts[1].lower()

        if item_id not in SHOP_ITEMS:
            bot.reply_to(message, "? Ïðåäìåò íå íàéäåí!")
            return

        if item_id not in user_balances[user_id]['items']:
            bot.reply_to(message, "? Ó âàñ íåò ýòîãî ïðåäìåòà!")
            return

        # Óäàëÿåì ïðåäìåò
        user_balances[user_id]['items'].remove(item_id)
        save_user_data()

        bot.reply_to(message,
            f"? Âû âûáðîñèëè {SHOP_ITEMS[item_id]['name']}")

    except Exception as e:
        print(f"Îøèáêà â handle_drop: {e}")
        bot.reply_to(message, "? Ïðîèçîøëà îøèáêà ïðè óäàëåíèè ïðåäìåòà")

if __name__ == '__main__':
    print("Áîò çàïóùåí...")
    event_thread = threading.Thread(target=check_event_end, daemon=True)
    event_thread.start()

    bot.infinity_polling()

