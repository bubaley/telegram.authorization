# https://github.com/bubaley/production-fastapi-docker-template
# version: 0.0.0 | Increase the version after changes from the template, this will make

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = True

    # database settings
    sql_engine: str = 'asyncpg'
    sql_database: str = 'postgres'
    sql_user: str = 'postgres'
    sql_password: str = 'postgres'
    sql_host: str = 'localhost'
    sql_port: int = 5432

    # encryption settings
    secret_key: str
    encryption_key: str

    # bot settings
    base_url: str | None = None
    debug_bot_id: str | None = None

    @property
    def database_url(self) -> str:
        return f'{self.sql_engine}://{self.sql_user}:{self.sql_password}@{self.sql_host}:{self.sql_port}/{self.sql_database}'

    class Config:
        pass
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()  # type: ignore
