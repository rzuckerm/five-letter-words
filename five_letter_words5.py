from typing import List
from functools import reduce
from collections import Counter
from operator import itemgetter
from dataclasses import dataclass, field
from multiprocessing import Queue, Process
import concurrent.futures
import os
import time

WORDS_FILENAME = "words_alpha.txt"
OUTPUT_FILENAME = "result5.txt"
ORD_A = 97
INDEX_LUT = {(2 << index) - 1: index for index in range(26)}


@dataclass
class State:
    codes: List[int] = field(default_factory=list)
    code: int = 0
    max_letter: int = 0
    skipped: bool = False
    stop: bool = False


class FiveLetterWords(Process):
    def __init__(self):
        words = load_words()
        self.codewords = find_unique_words(words)
        self.letter_order, self.letter_indices = self.get_letter_order_and_indices()
        self.queue = Queue()

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

    def find_words_inner(self, solutions, codes, code=0, max_letter=0, skipped=False, force=False):
        num_codes = len(codes)
        if num_codes == 5:
            solutions.append(codes)
            return

        if not force and num_codes == 1:
            self.queue.put(State(code=code, codes=codes, max_letter=max_letter, skipped=skipped))
            return

        for letter_index in range(max_letter, 26):
            if code & (1 << self.letter_order[letter_index]):
                continue

            for code2 in self.letter_indices[letter_index]:
                if code & code2:
                    continue

                self.find_words_inner(
                    solutions,
                    codes + [code2],
                    code | code2,
                    letter_index + 1,
                    skipped,
                )

            if skipped:
                break

            skipped = True

    def find_word_task(self, task_id):
        my_solutions = []
        while True:
            state = self.queue.get()
            if state.stop:
                break

            self.find_words_inner(
                my_solutions,
                state.codes,
                state.code,
                state.max_letter,
                state.skipped,
                force=True,
            )

        print(f"Task {task_id}: Found {len(my_solutions)} solutions")
        return my_solutions

    def find_words(self, solutions):
        num_tasks = os.cpu_count() or 1
        with concurrent.futures.ThreadPoolExecutor(num_tasks) as executor:
            tasks = [executor.submit(self.find_word_task, task_id) for task_id in range(num_tasks)]

            self.find_words_inner(solutions, [])
            for _ in range(num_tasks):
                self.queue.put(State(stop=True))

            for future in concurrent.futures.as_completed(tasks):
                solutions += future.result()


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
    obj.find_words(solutions)

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
