from fastapi import APIRouter, Request
from sys import stderr

import asyncio

router = APIRouter()

def pos_notation_to_dict(pos):
  return {
    'column': 'abcdefgh'.index(pos[0]),
    'row': int(pos[1]) - 1
  }

timeout = 5.0

JIS_PATH = './bin/jazzinsea'

async def ask_jazz(process, command):
  process.stdin.write(command)
  process.stdin.flush()

  return asyncio.wait_for(process.stdout.readline(), timeout)

@router.post("/calculate")
async def calculate(request: Request):
  data = await request.json()

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

  try:
    process = await asyncio.create_subprocess_exec(
      JIS_PATH,
      '-d%',
      stdin=asyncio.subprocess.PIPE,
      stdout=asyncio.subprocess.PIPE,
      stderr=stderr)

    process.stdin.write(f'aitime {aitime}\n'.encode())
    process.stdin.write(f'aidepth {aidepth}\n'.encode())
    process.stdin.write(f'loadfen "{fen}"\n'.encode())

    process.stdin.write(f'status -i\n'.encode())
    # process.stdin.flush()
    status = (await asyncio.wait_for(process.stdout.readline(), timeout)).decode()

    if status != '0':
      return None

    process.stdin.write(f'evaluate -r\n'.encode())
    # process.stdin.flush()
    move_str = (await asyncio.wait_for(process.stdout.readline(), timeout)).decode()

    process.stdin.write(f'descmove {move_str}\n'.encode())
    # process.stdin.flush()
    describe_str = (await asyncio.wait_for(process.stdout.readline(), timeout)).decode()

    from_pos, to_pos, capture_pos = describe_str.split()

    move = {
      'from_': pos_notation_to_dict(from_pos),
      'to': pos_notation_to_dict(to_pos),
      'capture': None
    }

    if capture_pos != '-':
      move["capture"] = pos_notation_to_dict(capture_pos)

    return move

  finally:
    process.kill()
