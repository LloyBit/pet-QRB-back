from pydantic_settings import BaseSettings 

class Settings(BaseSettings):

    # Database settings
    db_name: str
    db_url: str 
    admin_db_url: str  
    redis_url: str
    
    # Blockchain settings
    admin_wallet_address: str 
    network_rpc_url: str
    blockchain_confirmations: int = 3
    
    # Logging settings
    debug: bool = False
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_log_level: str = "WARNING"  # Уровень для консоли
    file_log_level: str = "DEBUG"       # Уровень для файла
    
    class Config:
        env_file = ".env"
        
settings = Settings()

