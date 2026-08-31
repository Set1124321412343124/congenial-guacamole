import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_conn():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    conn.autocommit = True
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (user_id BIGINT PRIMARY KEY, data JSONB NOT NULL DEFAULT '{}')''')
    cur.execute('''CREATE TABLE IF NOT EXISTS clans (clan_name TEXT PRIMARY KEY, data JSONB NOT NULL DEFAULT '{}')''')
    cur.execute('''CREATE TABLE IF NOT EXISTS promos (promo_name TEXT PRIMARY KEY, data JSONB NOT NULL DEFAULT '{}')''')
    cur.execute('''CREATE TABLE IF NOT EXISTS nfts (nft_id INTEGER PRIMARY KEY, data JSONB NOT NULL DEFAULT '{}')''')
    cur.execute('''CREATE TABLE IF NOT EXISTS market (listing_id INTEGER PRIMARY KEY, data JSONB NOT NULL DEFAULT '{}')''')
    cur.close()
    conn.close()

init_db()

def load_all_users():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT user_id, data FROM users')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {row['user_id']: row['data'] for row in rows}

def save_user(user_id, data):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO users (user_id, data) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET data = %s',
        (user_id, json.dumps(data, ensure_ascii=False), json.dumps(data, ensure_ascii=False))
    )
    cur.close()
    conn.close()

def save_all_users(user_balances):
    conn = get_conn()
    cur = conn.cursor()
    for user_id, data in user_balances.items():
        cur.execute(
            'INSERT INTO users (user_id, data) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET data = %s',
            (int(user_id), json.dumps(data, ensure_ascii=False), json.dumps(data, ensure_ascii=False))
        )
    cur.close()
    conn.close()

def load_all_clans():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT clan_name, data FROM clans')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {row['clan_name']: row['data'] for row in rows}

def save_all_clans(clans):
    conn = get_conn()
    cur = conn.cursor()
    for clan_name, data in clans.items():
        cur.execute(
            'INSERT INTO clans (clan_name, data) VALUES (%s, %s) ON CONFLICT (clan_name) DO UPDATE SET data = %s',
            (clan_name, json.dumps(data, ensure_ascii=False), json.dumps(data, ensure_ascii=False))
        )
    cur.close()
    conn.close()

def load_all_promos():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT promo_name, data FROM promos')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {row['promo_name']: row['data'] for row in rows}

def save_all_promos(promos):
    conn = get_conn()
    cur = conn.cursor()
    for promo_name, data in promos.items():
        cur.execute(
            'INSERT INTO promos (promo_name, data) VALUES (%s, %s) ON CONFLICT (promo_name) DO UPDATE SET data = %s',
            (promo_name, json.dumps(data, ensure_ascii=False), json.dumps(data, ensure_ascii=False))
        )
    cur.close()
    conn.close()

def load_all_nfts():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT nft_id, data FROM nfts')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {row['nft_id']: row['data'] for row in rows}

def save_all_nfts(nfts):
    conn = get_conn()
    cur = conn.cursor()
    for nft_id, data in nfts.items():
        cur.execute(
            'INSERT INTO nfts (nft_id, data) VALUES (%s, %s) ON CONFLICT (nft_id) DO UPDATE SET data = %s',
            (int(nft_id), json.dumps(data, ensure_ascii=False), json.dumps(data, ensure_ascii=False))
        )
    cur.close()
    conn.close()

def load_all_market():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT listing_id, data FROM market')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {row['listing_id']: row['data'] for row in rows}

def save_all_market(market):
    conn = get_conn()
    cur = conn.cursor()
    for listing_id, data in market.items():
        cur.execute(
            'INSERT INTO market (listing_id, data) VALUES (%s, %s) ON CONFLICT (listing_id) DO UPDATE SET data = %s',
            (int(listing_id), json.dumps(data, ensure_ascii=False), json.dumps(data, ensure_ascii=False))
        )
    cur.close()
    conn.close()
