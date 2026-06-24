from skilltest import play
from entropy import CANDIDATES

if __name__ == '__main__':
    test_word = input("Enter the test word: ").strip().lower()
    if test_word not in CANDIDATES:
        print(f"Word '{test_word}' is not in the candidates list.")
    else:
        guesses = play(test_word)
        print(f"Solved the word '{test_word}' in {guesses} guesses.")