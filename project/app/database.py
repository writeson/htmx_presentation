from pathlib import Path
from typing import AsyncGenerator, List
from contextlib import asynccontextmanager

from sqlmodel import SQLModel
from sqlalchemy import text
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncConnection


DB_PATH = Path(__file__).parent / "db" / "active" / "chinook.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
POOL_SIZE = 5


# create the async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


async def init_db():
    """Initialize the database and create tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        await TextSearchManager.create_virtual_table(conn)
        return "Text search initialized successfully"


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope for the database session."""
    async with AsyncSession(engine) as session:
        try:
            yield session
        finally:
            await session.close()


# Text search functionality
class TextSearchManager:
    @staticmethod
    async def get_text_columns(conn: AsyncConnection) -> List[tuple]:
        result = await conn.execute(
            text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            AND name != 'text_search'
        """)
        )
        tables = result.fetchall()

        text_columns = []
        for (table_name,) in tables:
            result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
            columns = result.fetchall()

            for col in columns:
                col_name = col[1]
                col_type = col[2].upper()
                if any(
                    text_type in col_type
                    for text_type in ["TEXT", "CHAR", "CLOB", "VARCHAR"]
                ):
                    text_columns.append((table_name, col_name, col_type))

        return text_columns

    @staticmethod
    async def create_virtual_table(conn: AsyncConnection):
        # Create FTS5 virtual table
        await conn.execute(text("DROP TABLE IF EXISTS text_search"))
        await conn.execute(
            text("""
            CREATE VIRTUAL TABLE text_search 
            USING fts5(
                table_name,
                column_name,
                content,
                content_rowid UNINDEXED
            )
        """)
        )

        # Get all text columns and populate the virtual table
        text_columns = await TextSearchManager.get_text_columns(conn)

        for table_name, column_name, _ in text_columns:
            await conn.execute(
                text(f"""
                INSERT INTO text_search (table_name, column_name, content, content_rowid)
                SELECT 
                    '{table_name}' AS table_name,
                    '{column_name}' AS column_name,
                    {column_name} AS content,
                    rowid AS content_rowid
                FROM {table_name}
                WHERE {column_name} IS NOT NULL
            """)
            )

            # Create triggers
            await TextSearchManager.create_triggers(conn, table_name, column_name)

        await conn.commit()

    @staticmethod
    async def create_triggers(conn: AsyncConnection, table_name: str, column_name: str):
        # Insert trigger
        await conn.execute(
            text(f"""
            CREATE TRIGGER IF NOT EXISTS text_search_{table_name}_{column_name}_insert 
            AFTER INSERT ON {table_name}
            WHEN NEW.{column_name} IS NOT NULL
            BEGIN
                INSERT INTO text_search (table_name, column_name, content, content_rowid)
                VALUES ('{table_name}', '{column_name}', NEW.{column_name}, NEW.rowid);
            END
        """)
        )

        # Update trigger
        await conn.execute(
            text(f"""
            CREATE TRIGGER IF NOT EXISTS text_search_{table_name}_{column_name}_update 
            AFTER UPDATE ON {table_name}
            WHEN NEW.{column_name} IS NOT NULL
            BEGIN
                UPDATE text_search 
                SET content = NEW.{column_name}
                WHERE table_name = '{table_name}' 
                AND column_name = '{column_name}'
                AND content_rowid = OLD.rowid;
            END
        """)
        )

        # Delete trigger
        await conn.execute(
            text(f"""
            CREATE TRIGGER IF NOT EXISTS text_search_{table_name}_{column_name}_delete 
            AFTER DELETE ON {table_name}
            BEGIN
                DELETE FROM text_search 
                WHERE table_name = '{table_name}' 
                AND column_name = '{column_name}'
                AND content_rowid = OLD.rowid;
            END
        """)
        )
