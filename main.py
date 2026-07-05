from bot.entropy import CANDIDATES, GUESSABLES, next_guess, get_feedback_from_user, update_colours
from utils import _format_guess_info

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
        print(_format_guess_info(guess=guess, ent=ent, candidates=candidates))
        if len(candidates) == 1:
            break