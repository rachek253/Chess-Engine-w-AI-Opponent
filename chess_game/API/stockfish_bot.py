"""
File name: stockfish_bot.py

Author(s): Rachel Newman, Cody Rubendall

Purpose: A module to connect to the external chess engine using WebSocket communication and
requests a move for the AI opponent. 

"""

import requests
from websocket import create_connection
from API.API_config import Config

class StockfishBot():
  """
  Chess bot implementation that communicates with an external chess API.
  """

  def __init__(self):
    """
    [[SDD_LLD_API_05]]
    Function to initialize the bot and load runtime configuration
    """
    self.config = Config()

    missing = self.config.validate()
    if missing:
      raise ValueError(
        f"Missing required configuration values in API.env: {', '.join(missing)}"
      )

    self.engine_mode = self.config.get_engine_mode()
    self.ws_url = self.config.get_chess_url()
    self.api_key = self.config.get_api_key()
    self.variants = self.config.get_bot_variants()
    self.timeout = self.config.get_bot_timeout()

  def is_online(self): 
    """
    Checks if the chess engine API is reachable. 
    Returns a bool value, true if success, false else 
    """
    
    try: 
      ws = create_connection(self.ws_url, timeout=self.timeout) 
      ws.close() 
      return True
    except Exception: 
      return False
  
  def choose_moves(self, board_fen):
        try:
            print("\n[BOT] Requesting moves...")

            response = requests.get(
                "https://stockfish.online/api/s/v2.php",
                params={
                    "fen": board_fen,
                    "depth": 5
                },
                timeout=self.timeout
            )

            data = response.json()
            bestmove = data.get("bestmove", "")

            print("[BOT RAW]", data)

            if not bestmove:
                print("[BOT WARNING] No move returned")
                return None

            parts = bestmove.split()

            # Checks for e2e4 format
            if len(parts) >= 2:
                move = parts[1]
            else:
                move = parts[0]
            return move

        except Exception as e:
            print("[BOT ERROR]", repr(e))
            return None

  # please write necessary functions for bot moves
  # feel free to make changes to the following code, I just wanted to give a starting point 
  # for using websockets package w the chess API I sent!
