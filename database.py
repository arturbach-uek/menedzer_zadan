def create_table(conn):
    create_query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            minutes INTEGER NOT NULL,
            priority INTEGER NOT NULL,
            is_done INTEGER NOT NULL DEFAULT 0
        )
    """
    with conn:
        conn.execute(create_query)