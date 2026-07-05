from bot.entropy import CANDIDATES, GUESSABLES, next_guess, get_feedback_from_user, update_colours
from utils import _format_message, _format_suggestion

from tests import skilltest_main, testword_main

def main():

    print(_format_message("main.py_introduction"))
    
    candidates = CANDIDATES.copy()
    green = {}
    yellow = {}
    gray = set()
    min_required = {}

    num_guesses = 0

    while True:

        num_guesses += 1

        new_green, new_yellow, new_gray = get_feedback_from_user()
        
        green, yellow, gray, min_required = update_colours(new_green, new_yellow, new_gray, green, yellow, gray, min_required)

        guess, ent, candidates = next_guess(candidates, GUESSABLES, green, yellow, gray, min_required=min_required, show_progress=True)

        if len(candidates) == 1:
            print(_format_message("found_answer").format(answer=candidates[0], guesses=num_guesses))
            return

        print(_format_suggestion(guess=guess, ent=ent, candidates=candidates))
        

FILE_OPTIONS = {
    "skilltest": skilltest_main,
    "testword": testword_main,
    "main": main
}

if __name__ == '__main__':
    print("hello! please select a file to run by typing it below, here are your options")
    print(", ".join(list(FILE_OPTIONS.keys())))
    FILE_OPTIONS[input().strip().lower()]()