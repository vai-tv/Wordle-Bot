# IMPORTS AND ARGPARSE

import argparse
from collections import Counter
import math
import sys
import time

from utils import load_words

parser = argparse.ArgumentParser(description="Entropy-based Word Guessing Bot")
parser.add_argument("-w", "--wordlist", type=str, required=True, help="Path to the word list file")
args = parser.parse_args()


WORDS = load_words(args.wordlist)

####################################################################################################
# FEEDBACK 

def feedback(guess, answer):
    """
        Provides feedback on a guess compared to the answer.
        Returns a tuple (code, greens, yellows):
        - code: integer encoding of the pattern in base-3 (MSB at pos 0), where
            2=green, 1=yellow, 0=gray
        - greens: list of (letter, index) for letters that are green
        - yellows: list of (letter, index) for letters that are yellow
        - greys: list of (letter, index) for letters that are gray
    """

    assert len(guess) == len(answer), "guess and answer must be same length"
    n = len(guess)

    # First pass: mark greens and count non-green letters in answer
    green = [False] * n
    answer_counts = Counter()
    for i in range(n):
        g = guess[i]
        a = answer[i]
        if g == a:
            green[i] = True
        else:
            answer_counts[a] += 1

    # Second pass: compute code in base-3 (most-significant at pos 0)
    code = 0
    for i in range(n):
        code *= 3
        if green[i]:
            val = 2
        else:
            g = guess[i]
            if answer_counts.get(g, 0) > 0:
                val = 1
                answer_counts[g] -= 1
            else:
                val = 0
        code += val

    # Build lists of (letter, index)
    greens = []
    yellows = []
    greys = []
    # Recompute pass to collect positions (we already determined green[] and
    # decreased answer_counts while computing code above, so recompute in the
    # same loop to avoid extra passes)
    # To do this efficiently, walk positions again and determine val as above.
    # We need a fresh copy of answer_counts (counts of non-green letters in
    # answer) to correctly identify yellow positions.
    answer_counts = Counter()
    for i in range(n):
        if not green[i]:
            answer_counts[answer[i]] += 1

    for i in range(n):
        if green[i]:
            greens.append((guess[i], i))
        else:
            g = guess[i]
            if answer_counts.get(g, 0) > 0:
                yellows.append((g, i))
                answer_counts[g] -= 1

            else:
                greys.append((g, i))

    return code, greens, yellows, greys

def is_guess_valid(guess, green, yellow, gray, min_required=None):
    """
    Check if a guess is valid given the constraints from previous feedback.
    - green: dict of position -> letter (correct letters in correct positions)
    - yellow: dict of letter -> set of positions (correct letters in wrong positions)
    - gray: set of letters (incorrect letters)
    """

    n = len(guess)

    # Check green constraints (position must match)
    for pos, letter in green.items():
        if guess[pos] != letter:
            return False

    # Build minimal required counts from greens (definite positions)
    # and optional external information in min_required parameter.
    # The `min_required` parameter should be a mapping letter->min_count
    # derived from per-guess non-gray counts (max per-guess count), which
    # avoids over-counting occurrences across multiple guesses.
    if min_required is None:
        # Fallback: conservative requirement = number of greens for letter +
        # 1 if letter has any yellow seen (ensures presence but avoids summing yellows)
        inferred = Counter()
        for _, letter in green.items():
            inferred[letter] += 1
        for letter, positions in yellow.items():
            if letter not in inferred:
                inferred[letter] = 1
        min_required = inferred

    # Count letters in the candidate guess
    guess_counts = Counter(guess)

    # Each letter with a min requirement must appear at least that many times
    for letter, req in min_required.items():
        if guess_counts.get(letter, 0) < req:
            return False

    # Check yellow position constraints (letter must not be at any forbidden pos)
    for letter, positions in yellow.items():
        for pos in positions:
            if guess[pos] == letter:
                return False

    # Check gray constraints:
    # - If a gray letter has no required occurrences (not in min_required), it must not appear at all
    # - If a gray letter *does* have required occurrences (because of earlier green/yellow),
    #   then the candidate must not contain more instances than required (no extra copies)
    for letter in gray:
        req = min_required.get(letter, 0)
        cnt = guess_counts.get(letter, 0)
        # If a letter is gray and we have no required occurrences for it,
        # it must not appear at all. If we do have a required count, the
        # candidate must not contain more instances than required.
        if req == 0 and cnt > 0:
            return False
        if req > 0 and cnt > req:
            return False

    return True

def filter_words(possible_words, green, yellow, gray, min_required=None):
    """
    Filter the list of possible words based on the feedback constraints.
    - green: dict of position -> letter (correct letters in correct positions)
    - yellow: dict of letter -> set of positions (correct letters in wrong positions)
    - gray: set of letters (incorrect letters)
    """

    filtered = []
    for word in possible_words:
        if is_guess_valid(word, green, yellow, gray, min_required=min_required):
            filtered.append(word)
    return filtered


def get_feedback_from_user() -> tuple[list[tuple[str, int]], list[tuple[str, int]], list[tuple[str, int]]]:

    greens = []
    yellows = []
    greys = []

    while True:

        while True:
            user_guess = input("Enter a word you tried (5-letter word, DONE to finish): ")
            if user_guess.upper() == "DONE":
                return greens, yellows, greys
            
            if len(user_guess) != 5:
                print("Invalid guess. Please enter a 5-letter word.")
                continue

            break

        while True:
            user_input = input("Enter feedback (g for green, y for yellow, x for gray, e.g. 'ggyxx'): ")
            if len(user_input) != 5 or any(c not in 'gyx' for c in user_input):
                print("Invalid input. Please enter a 5-character string using 'g', 'y', and 'x'.")
                continue

            for i, c in enumerate(user_input):
                if c == 'g':
                    greens.append((user_guess[i], i))
                elif c == 'y':
                    yellows.append((user_guess[i], i))
                elif c == 'x':
                    greys.append((user_guess[i], i))
            
            break


####################################################################################################
# ENTROPY CALCULATION

def entropy(guess, possible_answers=WORDS):
    """
    Calculate the entropy of a guess over the current word list.
    Entropy is calculated based on the distribution of feedback patterns
    that would result from this guess against all possible answers.
    """

    # Use a plain dict for counts (a bit faster than Counter here)
    pattern_counts = {}
    for answer in possible_answers:
        pattern, _, _, _ = feedback(guess, answer)
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

    total_answers = len(possible_answers)
    ent = 0.0
    for count in pattern_counts.values():
        p = count / total_answers
        ent -= p * math.log2(p)

    return ent


####################################################################################################
# GUESS LOOP
# - Calculate entropy for each word in the word list
# - Pick the word with the highest entropy as the next guess
# - Receive feedback and filter the word list accordingly


def next_guess(possible_words=WORDS, green=None, yellow=None, gray=None, min_required=None, show_progress=False):
    """
    Determine the next guess based on maximum entropy.
    - possible_words: current list of possible words
    - green: dict of position -> letter (correct letters in correct positions)
    - yellow: dict of letter -> set of positions (correct letters in wrong positions)
    - gray: set of letters (incorrect letters)
    """

    if green is None:
        green = {}
    if yellow is None:
        yellow = {}
    if gray is None:
        gray = set()

    filtered_words = filter_words(possible_words, green, yellow, gray, min_required=min_required)

    total = len(WORDS)
    max_entropy = -1.0
    best_guess = None

    if len(filtered_words) == 1:
        print("\n!! ANSWER FOUND !!")
        return filtered_words[0], max_entropy, filtered_words
    if len(filtered_words) == 0:
        print("No valid words remaining with the given constraints.")
        print("GREEN", green)
        print("YELLOW", yellow)
        print("GRAY", gray)
        exit(1)

    start = time.time()
    # Update at most ~100 times to avoid slowing down the loop with prints
    update_interval = max(1, total // 100)

    for idx, word in enumerate(WORDS, start=1):
        ent = entropy(word, filtered_words)
        if ent > max_entropy:
            max_entropy = ent
            best_guess = word

        if show_progress and (idx % update_interval == 0 or idx == total):
            elapsed = time.time() - start
            rate = idx / elapsed if elapsed > 0 else 0
            remaining = (total - idx) / rate if rate > 0 else 0
            pct = idx / total * 100
            sys.stdout.write(f"\rComputing entropies: {idx}/{total} ({pct:.1f}%) ETA {remaining:.1f}s")
            sys.stdout.flush()

    if show_progress:
        # clear the progress line
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

    return best_guess, max_entropy, filtered_words