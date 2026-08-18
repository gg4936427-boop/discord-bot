"""
طبقة قاعدة البيانات — SQLite عن طريق aiosqlite
تخزن: روم الترحيب، نظام اقتصاد، متجر، مخزون، وتذاكر الدعم
"""

import aiosqlite

DB_PATH = "bot_data.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                welcome_channel_id INTEGER DEFAULT NULL,
                ticket_category_id INTEGER DEFAULT NULL,
                ticket_log_channel_id INTEGER DEFAULT NULL,
                ticket_support_role_id INTEGER DEFAULT NULL
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS economy (
                user_id INTEGER,
                guild_id INTEGER,
                balance INTEGER DEFAULT 0,
                last_daily TEXT DEFAULT NULL,
                PRIMARY KEY (user_id, guild_id)
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS shop_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                name TEXT,
                price INTEGER,
                description TEXT DEFAULT ''
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                user_id INTEGER,
                guild_id INTEGER,
                item_name TEXT,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, guild_id, item_name)
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                channel_id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                user_id INTEGER,
                status TEXT DEFAULT 'open'
            )
            """
        )
        await db.commit()


# ---------------- إعدادات السيرفر ----------------

async def set_welcome_channel(guild_id: int, channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO guild_settings (guild_id, welcome_channel_id) VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET welcome_channel_id = excluded.welcome_channel_id
            """,
            (guild_id, channel_id),
        )
        await db.commit()


async def get_welcome_channel(guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT welcome_channel_id FROM guild_settings WHERE guild_id = ?", (guild_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def set_ticket_settings(guild_id: int, category_id: int = None, log_channel_id: int = None, support_role_id: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO guild_settings (guild_id) VALUES (?) ON CONFLICT(guild_id) DO NOTHING",
            (guild_id,),
        )
        if category_id is not None:
            await db.execute(
                "UPDATE guild_settings SET ticket_category_id = ? WHERE guild_id = ?",
                (category_id, guild_id),
            )
        if log_channel_id is not None:
            await db.execute(
                "UPDATE guild_settings SET ticket_log_channel_id = ? WHERE guild_id = ?",
                (log_channel_id, guild_id),
            )
        if support_role_id is not None:
            await db.execute(
                "UPDATE guild_settings SET ticket_support_role_id = ? WHERE guild_id = ?",
                (support_role_id, guild_id),
            )
        await db.commit()


async def get_ticket_settings(guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT ticket_category_id, ticket_log_channel_id, ticket_support_role_id FROM guild_settings WHERE guild_id = ?",
            (guild_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None, None, None
        return row


# ---------------- نظام الاقتصاد ----------------

async def get_balance(user_id: int, guild_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT balance FROM economy WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id),
        )
        row = await cursor.fetchone()
        return row[0] if row else 0


async def update_balance(user_id: int, guild_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO economy (user_id, guild_id, balance) VALUES (?, ?, ?)
            ON CONFLICT(user_id, guild_id) DO UPDATE SET balance = balance + excluded.balance
            """,
            (user_id, guild_id, amount),
        )
        await db.commit()


async def get_last_daily(user_id: int, guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT last_daily FROM economy WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id),
        )
        row = await cursor.fetchone()
        return row[0] if row and row[0] else None


async def set_last_daily(user_id: int, guild_id: int, timestamp: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO economy (user_id, guild_id, last_daily) VALUES (?, ?, ?)
            ON CONFLICT(user_id, guild_id) DO UPDATE SET last_daily = excluded.last_daily
            """,
            (user_id, guild_id, timestamp),
        )
        await db.commit()


async def get_leaderboard(guild_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT user_id, balance FROM economy
            WHERE guild_id = ? ORDER BY balance DESC LIMIT ?
            """,
            (guild_id, limit),
        )
        return await cursor.fetchall()


# ---------------- المتجر ----------------

async def add_shop_item(guild_id: int, name: str, price: int, description: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO shop_items (guild_id, name, price, description) VALUES (?, ?, ?, ?)",
            (guild_id, name, price, description),
        )
        await db.commit()


async def remove_shop_item(guild_id: int, name: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM shop_items WHERE guild_id = ? AND name = ?", (guild_id, name)
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_shop_items(guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT name, price, description FROM shop_items WHERE guild_id = ? ORDER BY price ASC",
            (guild_id,),
        )
        return await cursor.fetchall()


async def get_shop_item(guild_id: int, name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT name, price, description FROM shop_items WHERE guild_id = ? AND name = ?",
            (guild_id, name),
        )
        return await cursor.fetchone()


# ---------------- المخزون ----------------

async def add_inventory_item(user_id: int, guild_id: int, item_name: str, quantity: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO inventory (user_id, guild_id, item_name, quantity) VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, guild_id, item_name) DO UPDATE SET quantity = quantity + excluded.quantity
            """,
            (user_id, guild_id, item_name, quantity),
        )
        await db.commit()


async def remove_inventory_item(user_id: int, guild_id: int, item_name: str, quantity: int = 1) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT quantity FROM inventory WHERE user_id = ? AND guild_id = ? AND item_name = ?",
            (user_id, guild_id, item_name),
        )
        row = await cursor.fetchone()
        if not row or row[0] < quantity:
            return False
        new_qty = row[0] - quantity
        if new_qty <= 0:
            await db.execute(
                "DELETE FROM inventory WHERE user_id = ? AND guild_id = ? AND item_name = ?",
                (user_id, guild_id, item_name),
            )
        else:
            await db.execute(
                "UPDATE inventory SET quantity = ? WHERE user_id = ? AND guild_id = ? AND item_name = ?",
                (new_qty, user_id, guild_id, item_name),
            )
        await db.commit()
        return True


async def get_inventory(user_id: int, guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT item_name, quantity FROM inventory WHERE user_id = ? AND guild_id = ? ORDER BY item_name ASC",
            (user_id, guild_id),
        )
        return await cursor.fetchall()


# ---------------- التذاكر ----------------

async def create_ticket(channel_id: int, guild_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO tickets (channel_id, guild_id, user_id, status) VALUES (?, ?, ?, 'open')",
            (channel_id, guild_id, user_id),
        )
        await db.commit()


async def close_ticket(channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE tickets SET status = 'closed' WHERE channel_id = ?", (channel_id,)
        )
        await db.commit()


async def get_open_ticket_for_user(user_id: int, guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT channel_id FROM tickets WHERE user_id = ? AND guild_id = ? AND status = 'open'",
            (user_id, guild_id),
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def get_ticket(channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT guild_id, user_id, status FROM tickets WHERE channel_id = ?", (channel_id,)
        )
        return await cursor.fetchone()
