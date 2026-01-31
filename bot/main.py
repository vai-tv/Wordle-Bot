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
        
        # Process feedback from each guess separately to build min_required correctly
        # We need to extract per-guess feedback from the accumulated lists
        # Since get_feedback_from_user accumulates across multiple guesses, we need to
        # process them in the order they were entered. Unfortunately, we don't have that
        # order, so we'll use a different approach:
        # Calculate min_required based on the final constraints, not per-guess counts
        
        for letter, pos in new_green:
            green[pos] = letter
        
        for letter, positions in new_yellow:
            if letter not in yellow:
                yellow[letter] = set()
            yellow[letter].add(positions)
        
        for letter, pos in new_gray:
            gray.add(letter)

        # Build min_required from current constraints:
        # A letter needs to appear at least as many times as its green positions
        # OR if it's in yellow/green, at least once
        updated_min_required = Counter()
        
        # Count greens
        for pos, letter in green.items():
            updated_min_required[letter] += 1
        
        # For yellow letters not in green, require them to appear at least once
        for letter in yellow:
            if letter not in updated_min_required:
                updated_min_required[letter] = 1
        
        # Update global min_required: take the maximum for each letter
        for letter, cnt in updated_min_required.items():
            prev = min_required.get(letter, 0)
            if cnt > prev:
                min_required[letter] = cnt

        guess, ent, possible_words = next_guess(possible_words, green, yellow, gray, min_required=min_required, show_progress=True)
        print(f"Next guess: {guess} (Entropy: {ent:.4f}, Possible words left: {len(possible_words)})\n")

        if len(possible_words) == 1:
            break