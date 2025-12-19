import random as rnd

from entropy import WORDS, feedback, next_guess, filter_words
from utils import pattern_to_str


####################################################################################################


def play(answer: str) -> int:
    """
    Simulates a game of Wordle with the given answer.
    The bot makes guesses until it finds the answer.
    :param answer: The correct answer word.
    :return: The number of guesses taken to find the answer.
    """
    possible_words = WORDS.copy()
    green = {}
    yellow = {}
    gray = set()
    # Minimum required occurrences for letters (derived per-guess)
    min_required = {}

    guesses = 0

    while len(possible_words) > 1:
        if len(possible_words) == len(WORDS):
            guess = "raise"
            print(f"First guess: {guess}\n")
        else:
            guess, ent, possible_words = next_guess(possible_words, green, yellow, gray, show_progress=True)
            print(f"Next guess: {guess} (Entropy: {ent:.4f}, Possible words left: {len(possible_words)})")

        guesses += 1
        code, new_green, new_yellow, new_gray = feedback(guess, answer)
        print("Feedback:", pattern_to_str(code), "\n")

        for letter, pos in new_green:
            green[pos] = letter
            # each green increases the per-guess non-gray count
        # compute per-guess non-gray counts (greens + yellows for this guess)
        from collections import Counter
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

        # Update global min_required with maxima over per-guess counts
        for letter, cnt in per_guess.items():
            prev = min_required.get(letter, 0)
            if cnt > prev:
                min_required[letter] = cnt

        if len(possible_words) == len(WORDS):
            possible_words = filter_words(possible_words, green, yellow, gray, min_required=min_required)
    
    return guesses
        

def play_all(n: int) -> None:
    """
    Plays a game for each word in the WORDS list.
    """
    words_copy = WORDS.copy()
    rnd.shuffle(words_copy)
    results = []

    for idx, answer in enumerate(words_copy[:n], start=1):
        print(f"=== Game {idx}/{len(WORDS)}: Answer is '{answer}' ===\n")
        results.append((play(answer), answer))
        print("========================================\n")

    # Print statistics
    guesses, answers = zip(*results)

    total_games = len(results)
    total_guesses = sum(guesses)
    average_guesses = total_guesses / total_games
    max_guesses = max(guesses)
    min_guesses = min(guesses)

    print(f"""
    Played {total_games} games.
    Average guesses: {average_guesses:.2f}
    Max guesses: {max_guesses} (Answer: {results[results.index(max(results))][1]})
    Min guesses: {min_guesses} (Answer: {results[results.index(min(results))][1]})
""")


if __name__ == '__main__':

    games = int(input("Enter number of games to play (0 for all): "))
    games = games if games > 0 else len(WORDS)

    play_all(games)