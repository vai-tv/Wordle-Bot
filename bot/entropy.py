# IMPORTS AND ARGPARSE

import argparse
from collections import Counter
import math
import sys
import time

from utils import load_words

from bot.feedback import feedback, filter_words, get_feedback_from_user

parser = argparse.ArgumentParser(description="Entropy-based Word Guessing Bot")
parser.add_argument("-c", "--candidates", type=str, help="Path to the candidate word list file")
parser.add_argument("-g", "--guessables", type=str, help="Path to the guessable word list file")
args, unknown = parser.parse_known_args()

candidate_path = args.candidates or "txt/candidates.txt"
guessable_path = args.guessables or "txt/guessables.txt"

CANDIDATES = load_words(candidate_path)
GUESSABLES = load_words(guessable_path) if args.guessables else CANDIDATES


####################################################################################################
# ENTROPY CALCULATION

def entropy(guess, candidates=CANDIDATES):
    """
    Calculate the entropy of a guess over the current word list.
    Entropy is calculated based on the distribution of feedback patterns
    that would result from this guess against all possible answers.
    """

    # Use a plain dict for counts (a bit faster than Counter here)
    pattern_counts = {}
    for answer in candidates:
        pattern, _, _, _ = feedback(guess, answer)
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

    total_answers = len(candidates)
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

# Strategy constant: only use possible answers when below this threshold
POSSIBLE_ANSWERS_THRESHOLD = 3

# Opening guess - pre-computed to save time on first turn
OPENING_GUESS = "tarse"

def next_guess(candidates=CANDIDATES, guessables=GUESSABLES, green=None, yellow=None, gray=None, min_required=None, show_progress=False):
    """
    Computes the next guess based on the word list and current feedback.

    The function takes the following parameters:
    - candidates: a list of possible words to guess
    - guessables: a list of words that can be guessed (may include non-candidates)
    - green: a dictionary mapping letter positions to letters that are definitely in the correct position
    - yellow: a dictionary mapping letter positions to letters that are probably in the correct position
    - gray: a set of letters that are definitely not in the correct position
    - min_required: a dictionary mapping letters to their minimum required occurrences

    The function returns a tuple containing the next guess, its entropy, and the filtered candidate list.
    """

    if green is None:
        green = {}
    if yellow is None:
        yellow = {}
    if gray is None:
        gray = set()

    filtered_candidates = filter_words(candidates, green, yellow, gray, min_required=min_required)
    total_guessables = len(guessables)

    max_entropy = -1.0
    best_guess = None

    if len(filtered_candidates) == 1:
        return filtered_candidates[0], max_entropy, filtered_candidates
    if len(filtered_candidates) == 0:
        print("No valid words remaining with the given constraints.")
        print("GREEN", green)
        print("YELLOW", yellow)
        print("GRAY", gray)
        exit(1)

    # Use pre-computed opening guess when starting from full word list
    if len(filtered_candidates) == len(CANDIDATES):
        return OPENING_GUESS, entropy(OPENING_GUESS, CANDIDATES), filtered_candidates

    start = time.time()
    
    # Strategy: when few possible answers remain, only consider those for guessing
    # This ensures we don't pick obscure words when the answer pool is small
    if len(filtered_candidates) < POSSIBLE_ANSWERS_THRESHOLD:
        print("Guessing")
        guessables = filter_words(guessables, green, yellow, gray, min_required=min_required)
    else:
        print("Reducing candidate pool")

    # Update at most ~100 times to avoid slowing down the loop with prints
    update_interval = max(1, total_guessables // 100)

    for idx, word in enumerate(guessables, start=1):
        ent = entropy(word, filtered_candidates)
        if ent > max_entropy:
            max_entropy = ent
            best_guess = word

        # Show progress
        if show_progress and (idx % update_interval == 0 or idx == total_guessables):
            elapsed = time.time() - start
            rate = idx / elapsed if elapsed > 0 else 0
            remaining = (total_guessables - idx) / rate if rate > 0 else 0
            pct = idx / total_guessables * 100
            sys.stdout.write(f"\rComputing entropies: {idx}/{total_guessables} ({pct:.1f}%) ETA {remaining:.1f}s")
            sys.stdout.flush()

    if show_progress:
        # clear the progress line
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

    if best_guess is None:
        print("No valid guess found!")
        exit(1)

    return best_guess, max_entropy, filtered_candidates


def update_colours(new_green, new_yellow, new_gray, green, yellow, gray, min_required) -> tuple[dict, dict, set, Counter]:
    """
    Process feedback from each guess separately to build min_required correctly
    We need to extract per-guess feedback from the accumulated lists
    Calculate min_required based on the final constraints, not per-guess counts

    :param new_green: The green letters from the current guess
    :param new_yellow: The yellow letters from the current guess
    :param new_gray: The gray letters from the current guess
    :param green: The accumulated green letters
    :param yellow: The accumulated yellow letters
    :param gray: The accumulated gray letters
    :param min_required: The accumulated minimum required counts
    :return: A tuple containing the updated green, yellow, gray, and min_required
    """

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

    return green, yellow, gray, min_required