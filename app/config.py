import json
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

def load_abi():
    abi_path = Path(__file__).parent / "abi.json"
    with open(abi_path, "r") as f:
        return json.load(f)
    
class Settings(BaseSettings):

    # Postgres settings
    db_name: str
    db_url: str 
    admin_db_url: str 
    
    # Redis settings
    redis_url_main: str
    encoding: str ="utf-8"
    decode_responses: bool = True
    max_connections: int = 10
    retry_on_timeout: bool = True
    socket_keepalive: bool = True
    
    # Blockchain settings 
    contract_address: str
    network_http_rpc_url: str
    network_ws_rpc_url: str
    blockchain_confirmations: int 
    chain_id: int
    contract_abi: list = Field(default_factory=load_abi)
    
    # Logging settings
    debug: bool = False
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_log_level: str = "WARNING"  # Уровень для консоли
    file_log_level: str = "DEBUG"       # Уровень для файла
    
    class Config:
        env_file = ".env"
        extra = "ignore"  

#TODO: Избавиться от глобального инстанса
settings = Settings()
