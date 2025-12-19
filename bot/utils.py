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