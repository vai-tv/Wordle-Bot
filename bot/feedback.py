from collections import Counter

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

def get_feedback_from_user() -> tuple[list[tuple[str, int]], list[tuple[str, int]], list[tuple[str, int]], int]:

    greens = []
    yellows = []
    greys = []
    guesses = 0

    while True:

        while True:
            user_guess = input("Enter a word you tried (5-letter word, DONE to finish): ")
            if user_guess.upper() == "DONE":
                return greens, yellows, greys, guesses

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
            guesses += 1
            break
