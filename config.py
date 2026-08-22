"""
config.py
Central place for app configuration. Values are read from environment
variables so real credentials never need to be hard-coded or committed.

Set these in a .env file (see .env.example) or in your shell before running.
"""

import os
from dotenv import load_dotenv

# Loads variables from a .env file in the project root, if present.
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # Individual PostgreSQL connection parameters
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    DB_NAME = os.environ.get("DB_NAME", "employee_db")
    DB_USER = os.environ.get("DB_USER", "employee_roshane")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "employee_roshane_pass")

    @staticmethod
    def db_connection_params():
        return {
            "host": Config.DB_HOST,
            "port": Config.DB_PORT,
            "dbname": Config.DB_NAME,
            "user": Config.DB_USER,
            "password": Config.DB_PASSWORD,
        }