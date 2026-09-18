from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 1440
    algorithm: str = "HS256"

    payhere_merchant_id: str
    payhere_merchant_secret: str
    payhere_sandbox: bool = True

    booking_hold_minutes: int = 10

    class Config:
        env_file = ".env"


settings = Settings()