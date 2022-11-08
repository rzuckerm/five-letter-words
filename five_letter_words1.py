from functools import reduce
import time

WORDS_FILENAME = "words_alpha.txt"
OUTPUT_FILENAME = "result1.txt"
ORD_A = 97


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

    return sorted(codewords.items())


def select_words(codewords, index, end_index, code):
    for index2, (code2, word2) in enumerate(codewords[index + 1 : end_index], index + 1):
        if code & code2:
            continue

        yield index2, (code | code2, word2)


def main():
    start_time = time.time()

    words = load_words()
    print(f"{len(words)} words in total")

    codewords = find_unique_words(words)
    num_words = len(codewords)
    print(f"{num_words} words have a unique set of 5 letters")

    words_found = []
    for index1, (code1, word1) in enumerate(codewords[:-4]):
        print(
            f"Up to {index1} after {time.time() - start_time:.3f} seconds. "
            f"{len(words_found)} found so far."
        )

        codewords2 = select_words(codewords, index1, num_words - 3, code1)
        for index2, (code2, word2) in codewords2:
            codewords3 = select_words(codewords, index2, num_words - 2, code2)
            for index3, (code3, word3) in codewords3:
                codewords4 = select_words(codewords, index3, num_words - 1, code3)
                for index4, (code4, word4) in codewords4:
                    codewords5 = select_words(codewords, index4, num_words, code4)
                    for _, (_, word5) in codewords5:
                        words_found.append(" ".join(sorted((word1, word2, word3, word4, word5))))

    print(f"we had {len(words_found)} successful finds!")
    print(f"That took {time.time() - start_time:.3f} seconds")

    print(f"The results are in {OUTPUT_FILENAME}")
    with open(OUTPUT_FILENAME, "w") as f:
        for words in sorted(words_found):
            f.write(f"{words}\n")


if __name__ == "__main__":
    main()
