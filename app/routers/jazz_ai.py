from fastapi import APIRouter, Request
from subprocess import Popen, PIPE
from sys import stderr
from app.cez_ai.libs.move_lib import Move

router = APIRouter()

def pos_notation_to_dict(pos):
  return {
    'column': 'abcdefgh'.index(pos[0]),
    'row': int(pos[1]) - 1
  }

@router.post("/calculate")
async def calculate(request: Request):
  data = await request.json()

  print(data)
  fen = data["fen"]

  # difficulty is one of 1, 2 or 3
  difficulty = 1
  if "difficulty" in data:
    difficulty = min(max(int(data["difficulty"]), 1), 3)

  aitime = 0
  if difficulty == 1:
    aitime = 500
  elif difficulty == 2:
    aitime = 1000
  elif difficulty == 3:
    aitime = 2000

  aidepth = 256

  with Popen(
      ('jazzinsea', '-d%'),
      stdin=PIPE,
      stdout=PIPE,
      stderr=stderr,
      text=True) as process:

    process.stdin.write(f'aitime {aitime}\n')
    process.stdin.write(f'aidepth {aidepth}\n')
    process.stdin.write(f'loadfen "{fen}"\n')
    process.stdin.write(f'evaluate -r\n')
    process.stdin.flush()
    move_str = process.stdout.readline()[:-1]

    process.stdin.write(f'descmove {move_str}\n')
    process.stdin.flush()
    describe_str = process.stdout.readline()[:-1]
    from_pos, to_pos, capture_pos = describe_str.split()

    move = {
      'from_': pos_notation_to_dict(from_pos),
      'to': pos_notation_to_dict(to_pos),
      'capture': None
    }

    if capture_pos != '-':
      move["capture"] = pos_notation_to_dict(capture_pos)

    return move
