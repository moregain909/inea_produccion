from dotenv import load_dotenv
import os

load_dotenv()

# Database server INEA
MYSQL_USER = os.getenv('INEA_DB_MYSQL_USER')
MYSQL_PASS = os.getenv('INEA_DB_MYSQL_PASS')
MYSQL_HOST = os.getenv('INEA_DB_MYSQL_HOST')
MYSQL_PORT = os.getenv('INEA_DB_MYSQL_PORT')
DB = os.getenv('INEA_DB_DATABASE')

# Database de prueba local
LOCAL_MYSQL_USER = os.getenv('INEA_LOCAL_DB_MYSQL_USER')
LOCAL_MYSQL_PASS = os.getenv('INEA_LOCAL_DB_MYSQL_PASS')
LOCAL_MYSQL_HOST = os.getenv('INEA_LOCAL_DB_MYSQL_HOST')
LOCAL_MYSQL_PORT = os.getenv('INEA_LOCAL_DB_MYSQL_PORT')
LOCAL_DB = os.getenv('INEA_LOCAL_DB_DATABASE')

if __name__ == '__main__':
    
    
    
    pass