import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration Variables
# These can be set in a .env file for production use
DB_TYPE = os.getenv("HOSPITAL_DB_TYPE", "sqlite") # Options: sqlite, postgresql, mssql, mysql
DB_USER = os.getenv("HOSPITAL_DB_USER", "")
DB_PASSWORD = os.getenv("HOSPITAL_DB_PASSWORD", "")
DB_HOST = os.getenv("HOSPITAL_DB_HOST", "localhost")
DB_NAME = os.getenv("HOSPITAL_DB_NAME", "healthcare.db")
DB_PORT = os.getenv("HOSPITAL_DB_PORT", "5432")

def get_engine():
    """
    Creates a SQLAlchemy engine based on the environment configuration.
    Defaults to local SQLite for local development and testing.
    """
    try:
        if DB_TYPE == "sqlite":
            # Local Development SQLite
            print(f"Using Local SQLite: {DB_NAME}")
            return create_engine(f"sqlite:///{DB_NAME}")
        
        elif DB_TYPE == "postgresql":
            # Production PostgreSQL
            # Requires 'psycopg2' driver
            print(f"Connecting to Production PostgreSQL at {DB_HOST}...")
            return create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        elif DB_TYPE == "mssql":
            # Production MS SQL Server
            # Requires 'pyodbc' driver
            print(f"Connecting to Production MS SQL Server at {DB_HOST}...")
            return create_engine(f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server")
        
        elif DB_TYPE == "mysql":
            # Production MySQL
            # Requires 'pymysql' or 'mysqlclient' driver
            print(f"Connecting to Production MySQL at {DB_HOST}...")
            return create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
            
        else:
            # Default fallback to sqlite
            print(f"Unknown DB_TYPE '{DB_TYPE}'. Falling back to local SQLite.")
            return create_engine(f"sqlite:///healthcare.db")
            
    except Exception as e:
        print(f"Database Connection Error: {e}")
        # Final safety fallback
        return create_engine("sqlite:///healthcare.db")

# Global engine instance for the application
engine = get_engine()
