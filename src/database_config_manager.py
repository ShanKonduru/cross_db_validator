import json
import os
from typing import Dict, Any, Optional

class DatabaseConfigManager:
    """
    Manages reading, writing, and querying data from the database connection
    configuration JSON file.

    It assumes the config file follows the structure:
    {"environments": {"ENV_KEY": {"applications": {"APP_KEY": {settings}}}}
    """

    def __init__(self, file_path: str):
        """
        Initializes the manager and attempts to load the configuration file.

        Args:
            file_path: The full path to the configuration JSON file.
        """
        self.file_path = file_path
        self.config_data: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> bool:
        """
        Loads the configuration data from the JSON file into memory.

        Returns:
            True if the configuration was loaded successfully, False otherwise.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            print(f"Configuration loaded successfully from: {self.file_path}")
            return True
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {self.file_path}")
            return False
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from {self.file_path}. Check file format.")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during loading: {e}")
            return False

    def save_config(self) -> bool:
        """
        Writes the current in-memory configuration data back to the JSON file.

        Returns:
            True if the configuration was saved successfully, False otherwise.
        """
        try:
            # Ensure the directory exists before saving
            dir_name = os.path.dirname(self.file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)

            with open(self.file_path, 'w', encoding='utf-8') as f:
                # Use indent=2 for human-readable formatting
                json.dump(self.config_data, f, indent=2)
            print(f"Configuration saved successfully to: {self.file_path}")
            return True
        except Exception as e:
            print(f"Error saving configuration to {self.file_path}: {e}")
            return False

    def get_connection_details(self, environment_key: str, application_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the connection details for a specific environment and application.

        Args:
            environment_key: The uppercase key of the environment (e.g., "DEV", "QA").
            application_key: The uppercase key of the application (e.g., "RED", "TPS").

        Returns:
            A dictionary of connection settings, or None if not found.
        """
        try:
            # Accesses environments -> ENV_KEY -> applications -> APP_KEY
            return self.config_data['environments'][environment_key]['applications'][application_key]
        except KeyError:
            print(f"Error: Configuration for Environment '{environment_key}' or Application '{application_key}' not found.")
            return None
        except TypeError:
            print("Error: Configuration data structure is invalid.")
            return None

    def update_config_value(self, environment_key: str, application_key: str, key: str, value: Any) -> bool:
        """
        Updates a single key-value pair for a specific connection entry in memory.

        The change must be explicitly saved using save_config() to persist it.

        Args:
            environment_key: The uppercase key of the environment (e.g., "DEV").
            application_key: The uppercase key of the application (e.g., "RED").
            key: The setting key to update (e.g., "host", "max_connections").
            value: The new value for the setting.

        Returns:
            True if the update was successful, False otherwise.
        """
        details = self.get_connection_details(environment_key, application_key)
        if details is not None:
            details[key] = value
            print(f"Updated: [{environment_key}][{application_key}][{key}] set to '{value}' (in memory)")
            return True
        return False