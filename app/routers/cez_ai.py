from fastapi import APIRouter, HTTPException, Request
from typing import List

from app.cez_ai.libs import game_lib, board_lib, ai_lib

import random

router = APIRouter()

@router.post("/calculate")
async def calculate(request: Request):
  data = await request.json()
  
  print(data)
  fen = data["fen"]

  # difficulty is one of 1, 2 or 3
  difficulty = 1
  if "difficulty" in data:
    difficulty = min(max(int(data["difficulty"]), 1), 3)

  game = game_lib.Game()

  try:
    game.board.load_fen(fen)
  except board_lib.FENError as e:
    print(f"could not load fen")
    return

  aidepth = difficulty + 3

  ai = ai_lib.AI(aidepth)
  
  print(f"Calculating with depth {aidepth}...")

  best_lines, best_score = ai.calculate_best_move(game.board)
  move = random.choice(best_lines)[-1]
  length = len(best_lines[0])

  print("All found alternatives:")
  for line in best_lines:
      print(*line[::-1], sep=", ")

  if best_score is None:
      print("Score is not calculated")

  else:
      print(f"Score: {-best_score}")

  print(f"Length: {length}")

  print(f"Gonna play {move}")
  
  return move

