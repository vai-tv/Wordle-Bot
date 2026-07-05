from tests.skilltest import play
from bot.entropy import CANDIDATES

def main():
    test_word = input("Enter the test word: ").strip().lower()
    if test_word not in CANDIDATES:
        print(f"Word '{test_word}' is not in the candidates list.")
    else:
        play(test_word)