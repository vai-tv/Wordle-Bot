import random as rnd

from bot.entropy import GUESSABLES, CANDIDATES, feedback, next_guess, filter_words, update_colours
from utils import pattern_to_str, _format_guess_info, _format_message


####################################################################################################


def play(answer: str) -> int:
    """
    Simulates a game of Wordle with the given answer.
    The bot makes guesses until it finds the answer.
    :param answer: The correct answer word.
    :return: The number of guesses taken to find the answer.
    """
    candidates = CANDIDATES.copy()
    green = {}
    yellow = {}
    gray = set()
    # Minimum required occurrences for letters (derived per-guess)
    min_required = {}

    guesses = 0

    while len(candidates) > 1:
        guess, ent, candidates = next_guess(candidates, GUESSABLES, green, yellow, gray, show_progress=True)
        print(_format_guess_info(guess=guess, ent=ent, candidates=candidates))
        
        guesses += 1
        code, new_green, new_yellow, new_gray = feedback(guess, answer)
        print("Feedback:", pattern_to_str(code), "\n")

        if code == 242: # = GGGGG
            return guesses

        green, yellow, gray, min_required = update_colours(new_green, new_yellow, new_gray, green, yellow, gray, min_required)

        if len(candidates) == len(CANDIDATES):
            candidates = filter_words(candidates, green, yellow, gray, min_required=min_required)
    
    return guesses
        

def play_all(n: int) -> None:
    """
    Plays a game for each word in the CANDIDATES list.
    """
    candidates_copy = CANDIDATES.copy()
    rnd.shuffle(candidates_copy)
    results = []

    try:
        for idx, answer in enumerate(candidates_copy[:n], start=1):
            print(f"=== Game {idx}/{n}: Answer is '{answer}' ===\n")
            results.append((play(answer), answer))
            print("========================================\n")
    finally:

        # Print statistics
        guesses, _answers = zip(*results)

        total_games = len(results)
        total_guesses = sum(guesses)
        average_guesses = total_guesses / total_games
        max_guesses = max(guesses)
        min_guesses = min(guesses)

        # Compute guess distribution
        guess_distribution = {}
        for g in guesses:
            guess_distribution[g] = guess_distribution.get(g, 0) + 1
        distr = []
        for k, v in sorted(guess_distribution.items()):
            distr.append(f"{k} guesses: {v} ({v/total_games*100:.0f}%)")
        distr_str = " | ".join(distr)

        print(_format_message("play_all_summary").format(
            total_games=total_games,
            total_guesses=total_guesses,
            average_guesses=average_guesses,
            max_guesses=max_guesses,
            min_guesses=min_guesses,
            guess_distribution=distr_str
        ))


if __name__ == '__main__':

    games = int(input("Enter number of games to play (0 for all): "))
    games = games if games > 0 else len(CANDIDATES)

    play_all(games)