from entropy import WORDS, is_guess_valid, next_guess, get_feedback_from_user

from collections import Counter

if __name__ == '__main__':

    # Example usage
    possible_words = WORDS.copy()
    green = {}
    yellow = {}
    gray = set()
    min_required = {}

    # Sanity check for DOLLY-like case: X G Y X G -> single 'L' required
    test_green = {1: 'O', 4: 'Y'}
    test_yellow = {'L': {2}}
    test_gray = {'L'}
    assert is_guess_valid('LOABY', test_green, test_yellow, test_gray) is True
    assert is_guess_valid('LLABY', test_green, test_yellow, test_gray) is False

    while True:

        new_green, new_yellow, new_gray = get_feedback_from_user()
        for letter, pos in new_green:
            green[pos] = letter
        # per-guess non-gray counts
        per_guess = Counter()
        for letter, _ in new_green:
            per_guess[letter] += 1
        for letter, positions in new_yellow:
            if letter not in yellow:
                yellow[letter] = set()
            yellow[letter].add(positions)
            per_guess[letter] += 1
        for letter, pos in new_gray:
            gray.add(letter)

        # update global min_required
        for letter, cnt in per_guess.items():
            prev = min_required.get(letter, 0)
            if cnt > prev:
                min_required[letter] = cnt

        guess, ent, possible_words = next_guess(possible_words, green, yellow, gray, min_required=min_required, show_progress=True)
        print(f"Next guess: {guess} (Entropy: {ent:.4f}, Possible words left: {len(possible_words)})\n")