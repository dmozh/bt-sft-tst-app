from pydantic import BaseSettings


class Settings(BaseSettings):
    DEBUG = "false"

    server_host: str = '0.0.0.0'
    server_port: int = 9000

    database_host: str = ""
    database_name = ""
    database_user = ""
    database_pwd = ""
    database_port = ""

    redis_host = "localhost"
    redis_port = 6379

    rabbit_user = "guest"
    rabbit_pwd = "guest"
    rabbit_host = "localhost"


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8'
)
