import json
import random as rnd


with open('messages.json') as f:
    messages = json.load(f)

def load_words(file_path: str) -> list[str]:
    """Load words from a given file and return them as a list."""
    with open(file_path, 'r') as file:
        words = [line.strip() for line in file.readlines()]
    return words

def pattern_to_str(code, n=5):
    """Convert integer base-3 code back to a readable string like 'GYXXG'."""
    mapping = {0: 'X', 1: 'Y', 2: 'G'}
    # extract digits from most-significant to least
    digits = []
    for _ in range(n):
        digits.append(mapping[code % 3])
        code //= 3
    # digits are in reverse (least-significant first)
    return ''.join(reversed(digits))

def str_to_gyx(string: str):
    """Convert a string like 'GYXXG' to a list of greens, yellows, and greys."""
    
    greens = []
    yellows = []
    greys = []
    for i, ch in enumerate(string):
        if ch == 'G':
            greens.append((i))
        elif ch == 'Y':
            yellows.append((i))
        elif ch == 'X':
            greys.append((i))
        else:
            raise ValueError(f"Invalid character in pattern string: {ch}")
    return greens, yellows, greys

def _format_guess_info(*, guess: str, ent: float, candidates: list[str]) -> str:
    """Format the guess information for display.

    Parameters:
    - guess: the suggested next guess word
    - ent: entropy value for the guess
    - candidates: list of candidate words
    """
    
    sample_candidates = rnd.sample(candidates, min(10, len(candidates)))
    return _format_message("guess_info").format(
        guess=guess,
        ent=ent,
        candidates_left=len(candidates),
        sample_candidates=', '.join(sample_candidates)
    )

def _format_message(message_key: str) -> str:
    """Format a message from the messages.json file for display.

    Parameters:
    - message_key: the key in the messages.json file to retrieve the message
    """
    if message_key not in messages:
        raise KeyError(f"Message key '{message_key}' not found in messages.json.")
    
    # Resolve any formatting too
    return "\n".join(messages[message_key])