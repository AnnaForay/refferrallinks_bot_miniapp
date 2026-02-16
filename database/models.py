from .connection import db


# ============== USERS ==============

async def add_user(user_id: int, username: str, first_name: str, role: str = 'user'):
    """Добавить или обновить пользователя"""
    query = """
    INSERT INTO users (user_id, username, first_name, role)
    VALUES ($1, $2, $3, $4)
    ON CONFLICT (user_id)
    DO UPDATE SET username = $2, first_name = $3
    """
    async with db.pool.acquire() as conn:
        await conn.execute(query, user_id, username, first_name, role)


# ============== CATEGORIES ==============

async def add_category(name: str, emoji: str = '📁', position: int = 0):
    """Добавить категорию"""
    query = """
    INSERT INTO categories (name, emoji, position)
    VALUES ($1, $2, $3)
    RETURNING id
    """
    async with db.pool.acquire() as conn:
        return await conn.fetchval(query, name, emoji, position)


async def get_all_categories(only_active: bool = True):
    """Получить все категории"""
    query = """
    SELECT id, name, emoji, position, is_active,
    (SELECT COUNT(*) FROM links WHERE category_id = categories.id AND status = 'approved') as links_count
    FROM categories
    WHERE ($1 = FALSE OR is_active = TRUE)
    ORDER BY position, id
    """
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, only_active)
        return [dict(row) for row in rows]


async def get_category_by_id(category_id: int):
    """Получить категорию по ID"""
    query = "SELECT * FROM categories WHERE id = $1"
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(query, category_id)
        return dict(row) if row else None


async def update_category(category_id: int, name: str = None, emoji: str = None):
    """Обновить категорию"""
    fields = []
    values = []
    param_num = 1
    
    if name is not None:
        fields.append(f"name = ${param_num}")
        values.append(name)
        param_num += 1
    
    if emoji is not None:
        fields.append(f"emoji = ${param_num}")
        values.append(emoji)
        param_num += 1
    
    if not fields:
        return
    
    values.append(category_id)
    query = f"UPDATE categories SET {', '.join(fields)} WHERE id = ${param_num}"
    
    async with db.pool.acquire() as conn:
        await conn.execute(query, *values)


async def delete_category(category_id: int):
    """Удалить категорию"""
    query = "DELETE FROM categories WHERE id = $1"
    async with db.pool.acquire() as conn:
        await conn.execute(query, category_id)


async def toggle_category_status(category_id: int):
    """Переключить статус категории (активна/неактивна)"""
    query = "UPDATE categories SET is_active = NOT is_active WHERE id = $1"
    async with db.pool.acquire() as conn:
        await conn.execute(query, category_id)


# ============== LINKS ==============

async def add_link(category_id: int, name: str, url: str, description: str = None,
                  user_id: int = None, status: str = 'approved'):
    """Добавить ссылку"""
    query = """
    INSERT INTO links (category_id, user_id, name, url, description, status)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING id
    """
    async with db.pool.acquire() as conn:
        return await conn.fetchval(query, category_id, user_id, name, url, description, status)


async def get_links_by_category(category_id: int, status: str = 'approved'):
    """Получить ссылки категории"""
    query = """
    SELECT
        l.*,
        c.name as category_name,
        c.emoji as category_emoji,
        (SELECT COUNT(*) FROM reactions WHERE link_id = l.id) as reactions_count,
        COALESCE(SUM(CASE WHEN r.reaction = '👍' THEN 1 ELSE 0 END), 0) as thumbs_up,
        COALESCE(SUM(CASE WHEN r.reaction = '👎' THEN 1 ELSE 0 END), 0) as thumbs_down,
        COALESCE(SUM(CASE WHEN r.reaction = '🔥' THEN 1 ELSE 0 END), 0) as fire,
        COALESCE(SUM(CASE WHEN r.reaction = '❤️' THEN 1 ELSE 0 END), 0) as heart
    FROM links l
    LEFT JOIN categories c ON l.category_id = c.id
    LEFT JOIN reactions r ON l.id = r.link_id
    WHERE l.category_id = $1 AND l.status = $2
    GROUP BY l.id, c.name, c.emoji
    ORDER BY l.created_at DESC
    """
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, category_id, status)
        return [dict(row) for row in rows]


async def get_all_links(status: str = None):
    """Получить все ссылки"""
    if status:
        query = """
        SELECT l.*, c.name as category_name, c.emoji as category_emoji
        FROM links l
        LEFT JOIN categories c ON l.category_id = c.id
        WHERE l.status = $1
        ORDER BY l.created_at DESC
        """
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(query, status)
    else:
        query = """
        SELECT l.*, c.name as category_name, c.emoji as category_emoji
        FROM links l
        LEFT JOIN categories c ON l.category_id = c.id
        ORDER BY l.created_at DESC
        """
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(query)
    
    return [dict(row) for row in rows]


async def get_link_by_id(link_id: int):
    """Получить ссылку по ID"""
    query = """
    SELECT
        l.*,
        c.name as category_name,
        c.emoji as category_emoji,
        c.id as category_id,
        u.username as author_username,
        u.first_name as author_name,
        (SELECT COUNT(*) FROM reactions WHERE link_id = l.id) as reactions_count,
        COALESCE(SUM(CASE WHEN r.reaction = '👍' THEN 1 ELSE 0 END), 0) as thumbs_up,
        COALESCE(SUM(CASE WHEN r.reaction = '👎' THEN 1 ELSE 0 END), 0) as thumbs_down,
        COALESCE(SUM(CASE WHEN r.reaction = '🔥' THEN 1 ELSE 0 END), 0) as fire,
        COALESCE(SUM(CASE WHEN r.reaction = '❤️' THEN 1 ELSE 0 END), 0) as heart
    FROM links l
    LEFT JOIN categories c ON l.category_id = c.id
    LEFT JOIN users u ON l.user_id = u.user_id
    LEFT JOIN reactions r ON l.id = r.link_id
    WHERE l.id = $1
    GROUP BY l.id, c.name, c.emoji, c.id, u.username, u.first_name
    """
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(query, link_id)
        return dict(row) if row else None


async def get_user_links(user_id: int):
    """Получить все ссылки пользователя"""
    query = """
    SELECT 
        l.id,
        l.name,
        l.url,
        l.description,
        l.status,
        l.rejection_reason,
        l.clicks_count,
        c.name as category_name,
        c.emoji as category_emoji,
        c.id as category_id,
        (SELECT COUNT(*) FROM reactions WHERE link_id = l.id) as reactions_count
    FROM links l
    LEFT JOIN categories c ON l.category_id = c.id
    WHERE l.user_id = $1
    ORDER BY l.created_at DESC
    """
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, user_id)
        return [dict(row) for row in rows]


async def get_pending_links():
    """Получить все ссылки на модерации"""
    query = """
    SELECT l.*, c.name as category_name, c.emoji as category_emoji,
           u.username as author_username, u.first_name as author_name
    FROM links l
    LEFT JOIN categories c ON l.category_id = c.id
    LEFT JOIN users u ON l.user_id = u.user_id
    WHERE l.status = 'pending'
    ORDER BY l.created_at ASC
    """
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]


async def update_link(link_id: int, name: str = None, url: str = None, 
                     description: str = None, category_id: int = None):
    """Обновить ссылку"""
    fields = []
    values = []
    param_num = 1
    
    if name is not None:
        fields.append(f"name = ${param_num}")
        values.append(name)
        param_num += 1
    
    if url is not None:
        fields.append(f"url = ${param_num}")
        values.append(url)
        param_num += 1
    
    if description is not None:
        fields.append(f"description = ${param_num}")
        values.append(description)
        param_num += 1
    
    if category_id is not None:
        fields.append(f"category_id = ${param_num}")
        values.append(category_id)
        param_num += 1
    
    if not fields:
        return
    
    values.append(link_id)
    query = f"UPDATE links SET {', '.join(fields)} WHERE id = ${param_num}"
    
    async with db.pool.acquire() as conn:
        await conn.execute(query, *values)


async def update_link_status(link_id: int, status: str, rejection_reason: str = None):
    """Обновить статус ссылки"""
    query = """
    UPDATE links 
    SET status = $1, rejection_reason = $2, moderated_at = NOW()
    WHERE id = $3
    """
    async with db.pool.acquire() as conn:
        await conn.execute(query, status, rejection_reason, link_id)


async def delete_link(link_id: int):
    """Удалить ссылку"""
    query = "DELETE FROM links WHERE id = $1"
    async with db.pool.acquire() as conn:
        await conn.execute(query, link_id)


# ============== CLICKS & REACTIONS ==============

async def increment_link_clicks(link_id: int, user_id: int):
    """Увеличить счётчик кликов по ссылке"""
    query_click = """
        INSERT INTO clicks (link_id, user_id) 
        VALUES ($1, $2)
    """
    
    query_update = """
        UPDATE links 
        SET clicks_count = clicks_count + 1 
        WHERE id = $1
    """
    
    async with db.pool.acquire() as conn:
        await conn.execute(query_click, link_id, user_id)
        await conn.execute(query_update, link_id)


async def add_reaction(link_id: int, user_id: int, reaction: str):
    """Добавить или обновить реакцию пользователя"""
    query = """
        INSERT INTO reactions (link_id, user_id, reaction) 
        VALUES ($1, $2, $3)
        ON CONFLICT (link_id, user_id) 
        DO UPDATE SET reaction = $3, created_at = NOW()
    """
    
    async with db.pool.acquire() as conn:
        await conn.execute(query, link_id, user_id, reaction)


async def get_user_reaction(link_id: int, user_id: int):
    """Получить реакцию пользователя на ссылку"""
    query = "SELECT reaction FROM reactions WHERE link_id = $1 AND user_id = $2"
    async with db.pool.acquire() as conn:
        return await conn.fetchval(query, link_id, user_id)


# ============== STATISTICS ==============

async def get_global_stats():
    """Получить глобальную статистику"""
    query = """
    SELECT
        (SELECT COUNT(*) FROM users) as total_users,
        (SELECT COUNT(*) FROM categories WHERE is_active = TRUE) as total_categories,
        (SELECT COUNT(*) FROM links WHERE status = 'approved') as total_links,
        (SELECT COUNT(*) FROM links WHERE status = 'pending') as pending_links,
        (SELECT COUNT(*) FROM clicks) as total_clicks,
        (SELECT COUNT(*) FROM reactions) as total_reactions
    """
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(query)
        return dict(row)


async def get_top_links(limit: int = 10):
    """Получить топ ссылок по просмотрам"""
    query = """
    SELECT l.name, l.url, l.clicks_count, c.name as category_name, c.emoji
    FROM links l
    LEFT JOIN categories c ON l.category_id = c.id
    WHERE l.status = 'approved'
    ORDER BY l.clicks_count DESC
    LIMIT $1
    """
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, limit)
        return [dict(row) for row in rows]
