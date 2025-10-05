# db_config_main.py - Application demonstrating use of DatabaseConfigManager

import sys
import os

from src.database_config_manager import DatabaseConfigManager

CONFIG_FILE = "configs/database_connections.json"


def run_db_config_application(environment: str, application: str):
    """
    Runs logic that requires reading database configuration.
    """
    print("--- Running DB Config Application (db_config_main.py) ---")

    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Configuration file not found at {CONFIG_FILE}. Cannot proceed.")
        return

    manager = DatabaseConfigManager(CONFIG_FILE)

    # Retrieve configuration
    config = manager.get_connection_details(environment, application)

    if config:
        print(f"\n--- Retrieved Configuration for {environment}/{application} ---")
        print(f"Database Type: {config.get('db_type')}")
        print(f"Host: {config.get('host')}")
        print(f"Port: {config.get('port')}")
        print(f"Schema Name: {config.get('schema')}")
        print(f"Username Env Var: {config.get('username_env_var')}")
        print(f"Password Env Var: {config.get('password_env_var')}")
        print(f"Max Connections: {config.get('max_connections')}")

        # Example of dynamic connection string creation (for illustration)
        if config.get("db_type") == "oracle":
            conn_str = f"User={config.get('username_env_var')}/...@{config.get('host')}:{config.get('port')}/{config.get('service_name')}"
        elif config.get("db_type") == "postgresql":
            conn_str = f"Host={config.get('host')};Database={config.get('database')}"
        else:
            conn_str = "Could not determine connection string format."

        print(f"\n[INFO] Simulated Connection String: {conn_str}")
    else:
        print(f"\nFailed to retrieve configuration for {environment}/{application}.")

    print("\nDB config app finished successfully.")


if __name__ == "__main__":
    # Expected command line arguments (due to extra argument from batch file):
    # 0: script_name (db_config_main.py)
    # 1: application_name (Redundant: e.g., db_config_main)
    # 2: environment (e.g., DEV) <-- This is where the ENV key is now
    # 3: application (e.g., DUMMY) <-- This is where the APP key is now

    # We check for at least 4 arguments to ensure ENV and APP keys are present.
    if len(sys.argv) < 4:
        print("Usage: run_app.bat db_config_main <ENVIRONMENT_KEY> <APPLICATION_KEY>")
        print("Example: run_app.bat db_config_main DEV DUMMY")
        sys.exit(1)

    # Read keys from index 2 and 3 to skip the redundant index 1 argument.
    env_key = sys.argv[2].upper()
    app_key = sys.argv[3].upper()

    print(f"Running DB config application for {env_key}/{app_key}")

    run_db_config_application(env_key, app_key)
