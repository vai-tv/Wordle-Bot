from entropy import CANDIDATES, GUESSABLES, next_guess, get_feedback_from_user, update_colours

if __name__ == '__main__':

    candidates = CANDIDATES.copy()
    green = {}
    yellow = {}
    gray = set()
    min_required = {}

    while True:

        new_green, new_yellow, new_gray = get_feedback_from_user()
        
        green, yellow, gray, min_required = update_colours(new_green, new_yellow, new_gray, green, yellow, gray, min_required)

        guess, ent, candidates = next_guess(candidates, GUESSABLES, green, yellow, gray, min_required=min_required, show_progress=True)
        print(f"Next guess: {guess} (Entropy: {ent:.4f}, | Candidates left: {len(candidates)})\n")

        if len(candidates) == 1:
            break