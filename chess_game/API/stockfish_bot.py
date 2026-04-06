"""
File name: stockfish_bot.py

Author(s): Rachel Newman, Cody Rubendall

Purpose: A module to connect to the external chess engine using WebSocket communication and
requests a move for the AI opponent. 

Note to Cody: I just started this file to connect the API so you can write the code for the bot 
moves! -Rachel (delete when seen please)
"""
import ayncio # may be necessary for websockets (from what I read)
import json
import random

from websockets import create_connection
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
        f"Missing required configuration values in API.env: {', ' .join(missing)}"
      )

    self.engine_mode = self.config.get_engine_mode()
    self.ws_url = self.config.get_chess_url()
    self.api_key = self.config.get_api_key()
    self.variants = self.config.get_bot_variants()
    self.timeout = self.config.get_bot_timeout()

  def choose_moves(self, board, color):
    """
    Function to request a move from the Stockfish chess engine.

    Parameters: 
      board: current board representation
      color: side to move ('white' or 'black')

    Returns:
      Bot move or None if no move is available.
    """
    try:
      fen = # insert code here
      chess_ws = create_connection(self.ws_url, timeout = self.timeout)
      
      payload = { 
        "fen": fen,
        "variants": self.variants}
      
      # leave next 2 lines in case API key gets added to chess-api.com
      if self.api_key:
        payload["api_key"] = self.api_key

      chess_ws.send(json.dumps(payload))
      response = json.loads(chess_ws.recv())
      chess_ws.close()

      move_str = response.get("move")
      if not move_str:
        return None

  except Exception as e:
    print(f"[Bot Error] Unable to retrieve AI move: {e}")

  # please write necessary functions for bot moves
  # feel free to make changes to the following code, I just wanted to give a starting point 
  # for using websockets package w the chess API I sent!
