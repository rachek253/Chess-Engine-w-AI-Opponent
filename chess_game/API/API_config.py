"""
File Name: API_config.py

Author(s): Rachel Newman

Purpose: This file contains the configuration module
for the chess application designed in SE 300 in Spring 2026.

This configuration module is responsible for:
1. Loading environment variables from the API.env file
2. Providing centralized access to runtime configuration
3. Keeping sensitive or changeable settings out of source code
"""

import os
from dotenv import load_dotenv, find_dotenv

class Config:
    """
    Central configuration class for the chess application.

    This class loads environment variables from the API.env 
    file and provides methods for accessing configuration values. 
    """

    def __init__(self):
        """
        [[SDD_LLD_API_02]]
        Function to load environment variables when the configuration 
        object is created.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(base_dir, "API.env")
        load_dotenv(env_path)

    def get_engine_mode(self):
        """
        Function to return the engine mode selected for the application. 
        """
        return os.getenv("ENGINE_MODE")
    
    def get_chess_url(self):
        """
        Returns the WebSocket URL used to connect to the external chess
        engine. Used for the Bot module to send board positions and 
        receive move suggestions for the AI.
        """
        return os.getenv("CHESS_WS_URL")
    
    def get_api_key(self): 
        """
        [[SDD_LLD_API_03]]
        Function to access API key if one is defined in the environment file.
        """
        return os.getenv("CHESS_API_KEY")
    
    def get_bot_variants(self):
        """
        Returns the number of move variants the Bot should request from the 
        external engine. 
        """
        value = os.getenv("BOT_VARIANTS")
        return int(value) if value else 1
    
    def get_bot_timeout(self):
        """
        Function to return the timeout value for external chess engine 
        communication, as the system should not wait indefinitely for a
        response from the API.
        """
        value = os.getenv("BOT_TIMEOUT")
        return int(value) if value else 10
    
    def validate(self): 
        """
        [[SDD_LLD_API_05]]
        Function to validate required environment settings for chess
        application. 

        Returns a list of missing configuration fields.
        """
        missing = []
        
        if not self.get_engine_mode():
            missing.append("ENGINE_MODE")
        elif not self.get_chess_url():
            missing.append("CHESS_WS_URL")

        return missing
