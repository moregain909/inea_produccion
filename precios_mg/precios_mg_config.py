from dotenv import load_dotenv
import os

load_dotenv()

# Database producción server INEA
PRODUCCION_MYSQL_USER = os.getenv('INEA_DB_MYSQL_USER')
PRODUCCION_MYSQL_PASS = os.getenv('INEA_DB_MYSQL_PASS')
PRODUCCION_MYSQL_HOST = os.getenv('INEA_DB_MYSQL_HOST')
PRODUCCION_MYSQL_PORT = os.getenv('INEA_DB_MYSQL_PORT')
PRODUCCION_DB = os.getenv('INEA_DB_DATABASE')

# Database de prueba local@local
TEST_MYSQL_USER = os.getenv('INEA_TEST_DB_MYSQL_USER')
TEST_MYSQL_PASS = os.getenv('INEA_TEST_DB_MYSQL_PASS')
TEST_MYSQL_HOST = os.getenv('INEA_TEST_DB_MYSQL_HOST')
TEST_MYSQL_PORT = os.getenv('INEA_TEST_DB_MYSQL_PORT')
TEST_DB = os.getenv('INEA_TEST_DB_DATABASE')

if __name__ == '__main__':
    
    
    
    pass