from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
import pickle
import os


class SymmetricDeleteSpellingCorrection(object):
    def __init__(self, longest_edit_distance: int, word_dictionary: dict):
        self.longest_edit_distance = longest_edit_distance
        # self.word_dictionary = {"apple": 1, "pear": 2, "peach": 3, "beach": 4, "preach": 5 }
        self.word_dictionary = word_dictionary
        self.edit_distance_dictionary = dict()
        self.key_to_word_dictionary = {y: x for x, y in self.word_dictionary.items()}
        if not os.path.exists(r"D:\Jay\Personal_C\PycharmProjects\spell_checker\edit_distance_dictionary.pickle"):
            print("Building...")
            self.build_edit_distance_dictionary()
            print("Finished Building...")
            print("Pickling Data...")
            self.pickle_edit_distance_dictionary()
            print("Finished Pickling")
        else:
            print("Loading edit_distance_dictionary...")
            self.load_edit_distance_dictionary()
            print("Loaded")

    def build_edit_distance_dictionary(self):
        for edit_distance in range(1, self.longest_edit_distance + 1):
            ind = 1
            for word in self.word_dictionary:
                print(f"Finished Processing {ind}")
                # Creating the reverse key <-> word mapping
                key = self.word_dictionary[word]
                # self.key_to_word_dictionary[key] = word
                self.possible_edits_after_deletion(word=word, key=key, edit_distance=edit_distance,
                                                   storage_dictionary=self.edit_distance_dictionary)
                ind += 1

    def pickle_edit_distance_dictionary(self):
        with open('edit_distance_dictionary.pickle', 'wb') as handle:
            pickle.dump(self.edit_distance_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # with open('key_to_word_dictionary.pickle', 'wb') as handle:
        #     pickle.dump(self.edit_distance_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_edit_distance_dictionary(self):
        with open('edit_distance_dictionary.pickle', 'rb') as handle:
            self.edit_distance_dictionary = pickle.load(handle)

    def possible_edits_after_deletion(self, word: str, edit_distance: int, storage_dictionary: dict, key: int):
        """
        Generate all possible words after deleting 'distance' characters from the original word.

        :param word: The original word from which to generate deletions.
        :param key: key corresponding to the word.
        :param storage_dictionary: the dictionary to store the symmetric deletion data to.
        :param edit_distance: The number of characters to delete.
        """
        if edit_distance == 0 | edit_distance > len(word):
            return

        for i in range(len(word)):
            # Delete one character from the current position
            new_word = word[:i] + word[i + 1:]
            if edit_distance == 1:
                # print(storage_dictionary)
                if storage_dictionary.get(new_word, None) and new_word.strip() != "":
                    storage_dictionary[new_word].add(key)
                else:
                    storage_dictionary[new_word] = {key}
            else:
                # Recursively delete more characters
                self.possible_edits_after_deletion(word=new_word, key=key, edit_distance=edit_distance - 1,
                                                   storage_dictionary=storage_dictionary)

    def generate_input_deletions(self, input_string: str, max_edit_distance: int) -> dict:
        input_edit_distance_dictionary = {input_string: -1}

        for edit_distance in range(1, max_edit_distance + 1):
            self.possible_edits_after_deletion(word=input_string, key=-2, edit_distance=edit_distance,
                                               storage_dictionary=input_edit_distance_dictionary)
        return input_edit_distance_dictionary

    def parallel_generate_input_deletions(self, input_string: str, max_edit_distance: int) -> dict:
        input_edit_distance_dictionary = {input_string: -3}
        with ThreadPoolExecutor(max_workers=1000000000) as executor:  # Adjust max_workers as needed
            futures = []
            for edit_distance in range(1, max_edit_distance + 1):
                ind = -4
                future = executor.submit(self.possible_edits_after_deletion, word=input_string, key=-5,
                                         edit_distance=edit_distance,
                                         storage_dictionary=input_edit_distance_dictionary)
                # futures.append(future)
                # ind += 1

            # Optionally, wait for all futures to complete and handle results or exceptions
            # for future in as_completed(futures):
            #     try:
            #         result = future.result()  # You can use the result or just ensure the task is completed
            #     except Exception as exc:
            #         print(f'Generated an exception: {exc}')
        return input_edit_distance_dictionary

    def correct_spell(self, input_string: str, max_edit_distance: int) -> List[List[str]]:
        # Generating all combinations of edit distances
        # input_edit_distance_dictionary = self.generate_input_deletions(input_string=input_string,
        #                                                                max_edit_distance=max_edit_distance)
        input_edit_distance_dictionary = self.generate_input_deletions(input_string=input_string,
                                                                       max_edit_distance=max_edit_distance)

        # If match is found in original word list, then no spell correction needed
        og_match = self.word_dictionary.get(input_string)
        if og_match is not None:
            return [[self.key_to_word_dictionary[og_match]]]

        # Otherwise
        valid_matches = set()
        # print(self.edit_distance_dictionary, input_edit_distance_dictionary)
        for edits in input_edit_distance_dictionary:
            match = self.edit_distance_dictionary.get(edits, None)
            og_match = self.word_dictionary.get(edits, None)
            # print(edits, match, og_match)
            if match:
                # print("MATCH", match, edits)
                valid_matches.update(match)
            if og_match:
                # print("OG_MATCH", og_match, edits)

                valid_matches.update([og_match])
        # print(valid_matches)
        rankings = [[] for _ in range(max_edit_distance)]
        for matches in valid_matches:
            # print(matches)
            # print(self.key_to_word_dictionary)
            rank = SymmetricDeleteSpellingCorrection.edit_distance(self.key_to_word_dictionary[matches], input_string)
            # print(self.key_to_word_dictionary[matches], input_string, rank)
            if rank - 1 < max_edit_distance:
                rankings[rank - 1].append(self.key_to_word_dictionary[matches])
        return rankings

    @staticmethod
    def edit_distance(word1, word2):
        """
            Calculate the Levenshtein distance between two words, which is the minimum number of single-character edits
            (insertions, deletions, or substitutions) required to change one word into the other.

            :param word1: First word.
            :param word2: Second word.
            :return: Integer representing the edit distance between word1 and word2.
            """
        m, n = len(word1), len(word2)
        # Initialize DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # Base cases: edit distance for an empty word1 or word2
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        # Compute edit distance
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]  # No operation needed
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j],  # Deletion
                                       dp[i][j - 1],  # Insertion
                                       dp[i - 1][j - 1])  # Substitution

        return dp[m][n]

    def __repr__(self):
        return f"Initial Word Dict: {self.word_dictionary}\nSymmetric Deletion Dictionary: {self.edit_distance_dictionary}"
