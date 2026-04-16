"""
File name: stockfish_bot.py

Author(s): Rachel Newman, Cody Rubendall

Purpose: A module to connect to the external chess engine using WebSocket communication and
requests a move for the AI opponent. 

Note to Cody: I just started this file to connect the API so you can write the code for the bot 
moves! -Rachel (delete when seen please)
"""

import json
import random

from websocket import create_connection
from API.API_config import Config

class StockfishBot():
  """
  Chess bot implementation that communicates with an external chess API.
  """

  def __init__(self):
    """
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

    # Initializing the AI to simulate 500-800 elo
    self.depth = 1
    self.movetime = 100
    self.skill_level = 0
    self.multiPV = 4
  
  def choose_moves(self, board):
    """
    Function to request a move from the Stockfish chess engine.

    Parameters: 
      board: current board representation


    Returns:
      Bot move or None if no move is available.
    """
    try:
      fen = board
      chess_ws = create_connection(self.ws_url, timeout = self.timeout)
      
      payload = { 
        "fen": fen,
        "variants": self.variants,
        "multiPV": self.multiPV  # Ask for top n moves
      }
      
      # leave next 2 lines in case API key gets added to chess-api.com
      if self.api_key:
        payload["api_key"] = self.api_key

      chess_ws.send(json.dumps(payload))
      response = json.loads(chess_ws.recv())
      chess_ws.close()

      # API should return a list of moves if multiPV is used
      top_moves = response.get("moves")  # list of dicts: [{"move": "e2e4"}, ...]
      if not top_moves:
        return None

      # pick 1 move randomly from the top 5
      move_str = random.choice(top_moves[:4])["move"]
      return move_str

    except Exception as e:
      print(f"[Bot Error] Unable to retrieve AI move: {e}")
      return None

  # please write necessary functions for bot moves
  # feel free to make changes to the following code, I just wanted to give a starting point 
  # for using websockets package w the chess API I sent!
