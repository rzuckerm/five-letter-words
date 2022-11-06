from functools import reduce
import time

WORDS_FILENAME = "words_alpha.txt"
OUTPUT_FILENAME = "result.txt"
ORD_A = 97


def encode_word(word):
    return reduce(lambda accum, letter: accum | (1 << (ord(letter) - ORD_A)), word, 0)


def load_words():
    with open(WORDS_FILENAME) as f:
        return [word.strip() for word in f if word.strip()]


def find_unique_words(words):
    return sorted(
        {
            encode_word(word): word for word in words if len(word) == 5 and len(set(word)) == 5
        }.items()
    )


def select_words(codewords, index, code):
    return [
        ((code | code2), (index2, word2))
        for index2, (code2, word2) in enumerate(codewords[index + 1 :], index + 1)
        if code & code2 == 0
    ]


def main():
    start_time = time.time()

    words = load_words()
    print(f"{len(words)} words in total")

    codewords = find_unique_words(words)
    num_words = len(codewords)
    print(f"{num_words} words have a unique set of 5 letters")

    words_found = set()
    for index1, (code1, word1) in enumerate(codewords[:-1]):
        print(
            f"Up to {index1} after {time.time() - start_time:.3f} seconds. "
            f"{len(words_found)} found so far."
        )

        codewords2 = select_words(codewords, index1, code1)
        for code2, (index2, word2) in codewords2:
            codewords3 = select_words(codewords, index2, code2)
            for code3, (index3, word3) in codewords3:
                codewords4 = select_words(codewords, index3, code3)
                for code4, (index4, word4) in codewords4:
                    codewords5 = select_words(codewords, index4, code4)
                    for _, (_, word5) in codewords5:
                        words_found.add(" ".join(sorted((word1, word2, word3, word4, word5))))

    print(f"we had {len(words_found)} successful finds!")
    print(f"That took {time.time() - start_time} seconds")

    print(f"The results are in {OUTPUT_FILENAME}")
    with open(OUTPUT_FILENAME, "w") as f:
        for words in sorted(words_found):
            f.write(f"{words}\n")


if __name__ == "__main__":
    main()