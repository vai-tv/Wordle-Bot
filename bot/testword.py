from skilltest import play
from entropy import WORDS

if __name__ == '__main__':
    test_word = input("Enter the test word: ").strip().lower()
    if test_word not in WORDS:
        print(f"Word '{test_word}' is not in the valid words list.")
    else:
        guesses = play(test_word)
        print(f"Solved the word '{test_word}' in {guesses} guesses.")