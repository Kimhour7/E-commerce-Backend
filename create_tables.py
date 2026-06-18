import os
import sys
import importlib
from core.db import Base, engine
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from core.custom_id import PrefixId

def import_models(base_path: str, sub_path: str = "api"):
    """
    Dynamically import all models.py files from the api modules.
    """
    sys.path.insert(0, base_path)
    for root, _, files in os.walk(os.path.join(base_path, sub_path)):
        for file in files:
            if file == "models.py":
                module_path = os.path.relpath(root, base_path).replace(os.path.sep, ".")
                module_name = f"{module_path}.models"
                try:
                    importlib.import_module(module_name)
                    print(f"Imported: {module_name}")
                except ImportError as e:
                    print(f"Error importing {module_name}: {e}")

def create_tables():
    """
    Create all tables defined in the models.
    """
    # Import all models relative to this script's directory
    base_path = os.path.abspath(os.path.dirname(__file__))
    import_models(base_path)

    # Ensure branch models are explicitly imported if dynamic import misses them
    try:
        importlib.import_module('api.website.branch.models')
        print('Explicitly imported api.website.branch.models')
    except ImportError as e:
        print(f'Error explicitly importing branch model: {e}')
    
    # Verify the connection to the database
    try:
        with engine.connect() as connection:
            print("Database connection successful.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return
    
    # Debugging: Print the tables before creating them
    print(f"Base.metadata.tables before creation: {Base.metadata.tables}")
    
    # Check if tables are loaded
    if not Base.metadata.tables:
        print("No tables found to create.")
    else:
        print(f"Tables to be created: {Base.metadata.tables.keys()}")

    print(f"tbl_branch loaded in metadata: {'tbl_branch' in Base.metadata.tables}")
    
    # Check if tables exist in the public schema
    inspector = inspect(engine)
    tables_in_public = inspector.get_table_names(schema='public')
    print(f"Tables in the public schema before creation: {tables_in_public}")
    
    try:
        # Attempt to create all tables
        Base.metadata.create_all(bind=engine)
        print("All tables have been created successfully.")
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")
    
    # Initialize ID counters
    initialize_counters()
    
    # Verify tables after creation
    tables_in_public_after = inspector.get_table_names(schema='public')
    print(f"Tables in the public schema after creation: {tables_in_public_after}")

def initialize_counters():
    """
    Initialize ID counter table with prefixes if not already present.
    """
    from sqlalchemy.orm import sessionmaker
    from api.master_data.id_config.models import TBL_ID_COUNTER
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        prefixes = ["PRO", "CAT", "CART", "ITEM", "PRO-TAG", "SUB-CAT", PrefixId.Country, PrefixId.Province, PrefixId.Company, PrefixId.Branch, PrefixId.User]  # Add Prefixes ID
        
        for prefix in prefixes:
            # Check if this prefix already exists
            existing = session.query(TBL_ID_COUNTER).filter_by(prefix=prefix).first()
            if not existing:
                counter = TBL_ID_COUNTER(prefix=prefix, sequence=0)
                session.add(counter)
                print(f"Initialized counter for prefix: {prefix}")
        
        session.commit()
        print("ID counters initialized successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error initializing counters: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_tables()