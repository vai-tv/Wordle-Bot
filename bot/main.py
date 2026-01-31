from entropy import WORDS, next_guess, get_feedback_from_user, update_colours

if __name__ == '__main__':

    possible_words = WORDS.copy()
    green = {}
    yellow = {}
    gray = set()
    min_required = {}

    while True:

        new_green, new_yellow, new_gray = get_feedback_from_user()
        
        green, yellow, gray, min_required = update_colours(new_green, new_yellow, new_gray, green, yellow, gray, min_required)

        print(green, yellow, gray, min_required)

        guess, ent, possible_words = next_guess(possible_words, green, yellow, gray, min_required=min_required, show_progress=True)
        print(f"Next guess: {guess} (Entropy: {ent:.4f}, Possible words left: {len(possible_words)})\n")

        if len(possible_words) == 1:
            break