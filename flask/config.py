import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    # Configurações principais
    SECRET_KEY = os.getenv('SECRET_KEY')  # Chave secreta para JWT
    MONGO_URI = os.getenv('MONGO_URI')    # URI do MongoDB

    # Configurações relacionadas a segurança (exemplo)
    SESSION_COOKIE_HTTPONLY = True

config = Config()