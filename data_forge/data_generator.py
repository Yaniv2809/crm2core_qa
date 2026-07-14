import sqlite3
import random
from datetime import datetime
# Importing your open-source data generation tool
from fixtureforge import FixtureForge 

from config.config_manager import ConfigManager

class TestDataGenerator:
    def __init__(self):
        """
        Initializes the generator with database paths from the configuration manager.
        """
        self.crm_db_path = ConfigManager.get_crm_db_path()
        self.bank_db_path = ConfigManager.get_bank_db_path()
        self.default_rate = ConfigManager.load_config()["business_logic"]["default_ils_rate"]

    def _setup_schemas(self):
        """
        Creates fresh tables for both CRM and Bank Core databases.
        Drops existing tables to ensure a clean state for every test run.
        """
        crm_conn = sqlite3.connect(self.crm_db_path)
        bank_conn = sqlite3.connect(self.bank_db_path)

        # Create CRM Source Table
        crm_conn.execute("DROP TABLE IF EXISTS Source_Requests;")
        crm_conn.execute("""
            CREATE TABLE Source_Requests (
                Request_ID VARCHAR(50) PRIMARY KEY,
                First_Name VARCHAR(50),
                Last_Name VARCHAR(50),
                Loan_Amount_USD DECIMAL(10,2),
                Risk_Level VARCHAR(20),
                Approval_Status VARCHAR(20),
                Creation_Date TIMESTAMP
            );
        """)

        # Create Bank Target Table
        bank_conn.execute("DROP TABLE IF EXISTS Target_Database;")
        bank_conn.execute("""
            CREATE TABLE Target_Database (
                Core_Loan_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CRM_Ref_ID VARCHAR(50),
                Customer_Full_Name VARCHAR(100),
                Loan_Amount_ILS DECIMAL(10,2),
                Bank_Status VARCHAR(20),
                Sync_Date TIMESTAMP
            );
        """)

        crm_conn.commit()
        bank_conn.commit()
        crm_conn.close()
        bank_conn.close()

    def generate_and_inject_data(self, exchange_rate: float, record_count: int = 50):
        """
        Generates base records using FixtureForge, transforms them for the target DB,
        and injects intentional bugs (Data Mutations) to be caught by the tests.
        """
        self._setup_schemas()
        
        # Initialize FixtureForge instance
        forge = FixtureForge()
        
        crm_records = []
        bank_records = []
        
        for i in range(1, record_count + 1):
            req_id = f"CRM-{1000 + i}"
            
            # Use FixtureForge to generate realistic dummy strings/numbers
            # Note: Adjust the method names according to your FixtureForge API
            first_name = forge.generate_string(length=6) 
            last_name = forge.generate_string(length=8)
            amount_usd = round(random.uniform(5000.0, 50000.0), 2)
            
            # Build CRM Record
            crm_records.append((
                req_id, first_name, last_name, amount_usd, 
                "Low", "Approved", datetime.now()
            ))

            # --- Injecting Intentional Bugs for Testing ---
            
            # Bug 1: Missing Record (Skip insertion to Bank DB for CRM-1005)
            if req_id == "CRM-1005":
                continue 
                
            expected_ils = round(amount_usd * exchange_rate, 2)
            
            # Bug 2: Amount Mismatch (Alter the calculated ILS for CRM-1010)
            if req_id == "CRM-1010":
                expected_ils = expected_ils - 100.00 

            full_name = f"{first_name} {last_name}"
            
            # Build Bank Record
            bank_records.append((
                req_id, full_name, expected_ils, "ACTIVE", datetime.now()
            ))

        # Insert records into SQLite databases
        self._insert_records(self.crm_db_path, "Source_Requests", 7, crm_records)
        self._insert_records(self.bank_db_path, "Target_Database", 5, bank_records)

    def _insert_records(self, db_path: str, table_name: str, col_count: int, data: list):
        """
        Generic batch insert helper function.
        """
        conn = sqlite3.connect(db_path)
        placeholders = ",".join(["?"] * col_count)
        
        if table_name == "Source_Requests":
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        else:
            # Skip Core_Loan_ID (AUTOINCREMENT) for Bank DB
            query = f"INSERT INTO {table_name} (CRM_Ref_ID, Customer_Full_Name, Loan_Amount_ILS, Bank_Status, Sync_Date) VALUES ({placeholders})"
            
        conn.executemany(query, data)
        conn.commit()
        conn.close()