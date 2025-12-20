from entropy import WORDS, next_guess, get_feedback_from_user

from collections import Counter

if __name__ == '__main__':

    possible_words = WORDS.copy()
    green = {}
    yellow = {}
    gray = set()
    min_required = {}

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

        if len(possible_words) == 1:
            break