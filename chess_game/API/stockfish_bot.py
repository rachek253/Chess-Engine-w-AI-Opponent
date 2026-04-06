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
from API.config import API_config

class StockfishBot():
  """
  Chess bot implementation that communicates with an external chess API.
  """

def __init__(self):
  """
  Function to initialize the bot and load runtime configuration
  """
  self.config
