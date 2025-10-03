HELP_TEXT = """calc: A simple command-line calculator

Features:
  ?           Previous result
  1,000       Thousands separators
  #           Comments
  exit        Exit calculator

Operators:
  +  -  *  /  %  **  (aliases: ＋  － x X ×  ÷  ^)

Functions:
  abs avg ceil cos exp floor log max min round sin sqrt sum tan

Constants: pi e

Time:
  HH:MM:SS    1h 30m    1 hour 30 minutes    1時間 30分

Examples:
  1,000 x 3      → 3,000 (comma separators, alias)
  ? ÷ 2         → 1,500 (previous result, alias)
  1h 30m + 45s   → 01:30:45 (time)
  10個 + 20個    → 30 (units ignored)

More: https://github.com/shakiyam/calc"""


def get_help() -> str:
    """Get help text"""
    return HELP_TEXT
