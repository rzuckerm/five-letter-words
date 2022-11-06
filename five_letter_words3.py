from functools import reduce
from collections import Counter
from operator import itemgetter
import time

WORDS_FILENAME = "words_alpha.txt"
OUTPUT_FILENAME = "result3.txt"
ORD_A = 97
INDEX_LUT = {(2 << index) - 1: index for index in range(26)}


class FiveLetterWords:
    def __init__(self):
        words = load_words()
        self.codewords = find_unique_words(words)
        self.letter_order, self.letter_indices = self.get_letter_order_and_indices()

    def get_letter_order_and_indices(self):
        # Get letter frequency
        index_freq = Counter(ord(ch) - ORD_A for word in self.codewords.values() for ch in word)

        # Rearrange letter order based on lettter frequency (least used letter gets lowest index)
        index_freq = sorted([(freq, index) for index, freq in index_freq.items()])
        letter_order = [index for _, index in index_freq]
        reverse_letter_order = [0] * 26
        for index, letter_order_index in enumerate(letter_order):
            reverse_letter_order[letter_order_index] = index

        # Build index based on least used letter
        letter_indices = [[] for _ in range(26)]
        for code in self.codewords:
            temp_code = code
            index = INDEX_LUT[temp_code ^ (temp_code - 1)]
            min_index = reverse_letter_order[index]
            temp_code &= temp_code - 1
            while temp_code:
                index = INDEX_LUT[temp_code ^ (temp_code - 1)]
                min_index = min(min_index, reverse_letter_order[index])
                temp_code &= temp_code - 1

            letter_indices[min_index].append(code)

        return letter_order, letter_indices

    def find_words(self, solutions, codes, code=0, max_letter=0, skipped=False):
        if len(codes) == 5:
            solutions.append(codes)
            return

        for letter_index in range(max_letter, 26):
            if code & (1 << self.letter_order[letter_index]):
                continue

            for code2 in self.letter_indices[letter_index]:
                if code & code2:
                    continue

                self.find_words(
                    solutions,
                    codes + [code2],
                    code | code2,
                    letter_index + 1,
                    skipped,
                )

            if skipped:
                break

            skipped = True


def encode_word(word):
    return reduce(lambda accum, letter: accum | (1 << (ord(letter) - ORD_A)), word, 0)


def load_words():
    with open(WORDS_FILENAME) as f:
        return [word.strip() for word in f if word.strip()]


def find_unique_words(words):
    codewords = {}
    unique_words = [word for word in words if len(word) == 5 and len(set(word)) == 5]
    for word in unique_words:
        code = encode_word(word)
        if code not in codewords:
            codewords[code] = word

    return codewords


def main():
    start = time.time()

    words = load_words()
    print(f"{len(words)} words in total")

    start_algo = time.time()
    obj = FiveLetterWords()
    num_words = len(obj.codewords)
    print(f"{num_words} words have a unique set of 5 letters")
    print("Letter order: " + "".join(chr(index + ORD_A) for index in obj.letter_order))

    solutions = []
    obj.find_words(solutions, [])

    start_output = time.time()
    words_found = sorted(
        " ".join(sorted(obj.codewords[code] for code in solution)) for solution in solutions
    )
    print(f"{len(words_found)} solutions written to {OUTPUT_FILENAME}\n")
    with open(OUTPUT_FILENAME, "w") as f:
        for words in words_found:
            f.write(f"{words}\n")

    end = time.time()
    print(f"Total Time: {end - start:8.3f} s")
    print(f"Read:       {start_algo - start:8.3f} s")
    print(f"Process:    {start_output - start_algo:8.3f} s")
    print(f"Write:      {end - start_output:8.3f} s")


if __name__ == "__main__":
    main()
