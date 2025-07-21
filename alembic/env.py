from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context
from shared.db.models import Base

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    from sqlalchemy.ext.asyncio import create_async_engine
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )
    async def do_run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True
        )
        async with context.begin_transaction():
            await context.run_migrations()
    import asyncio
    asyncio.run(do_run_migrations(connectable.connect()))

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
