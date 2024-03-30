# Copyright 2024 by AisleSolutions. All Rights Reserved. 
# 
# Source code is explicitly for meeting requirements requested by University
# of Calgary Entrepreneurial Capstone Design Project 2024. 
#
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying source code is explicitly forbidden. 

from difflib import SequenceMatcher
import numpy as np
import enchant 


class CategorizeText:
    """
    Categorizes the text detected and places these texts by indices
    into their categories.

    Parameters
    ----------
        texts: list
            These are the detected texts in the scene.

        boxes: np.ndarray
            These are the bounding boxes of each texts.
    """
    def __init__(self, texts: list, boxes: np.ndarray) -> None:
        self.texts = texts
        self.boxes = boxes
        self.categories = dict()

        # This object contains words in the English dictionary for correct spelling.
        self.dictionary = enchant.Dict("en_US")

    def categorize_by_longest_match(self): #NOSONAR
        """
        If the word does not exist in the dictionary, suggest words.
        Choose suggested words with lengths > 2, remove any spaces, lower case all letters.
        Store the categories if it does not exist.
        """
        for text in self.texts:
            # Check if the word exists.    
            if (self.dictionary.check(text)):
                if (len(text) > 2 and 
                    (text not in self.categories.keys()) and not text.isdigit()):
                    self.categories[text] = []
            else:
                options = self.dictionary.suggest(text)
                if len(options) > 0:
                    category = options[0].lower().replace(" ", "")
                    if len(category) > 2 and (category not in self.categories.keys()):
                        self.categories[category] = []

    def categorize_by_common_text(self):
        """
        Categorizes the text based on uniqueness. A unique text is its own
        category, repeated texts have their indices placed on a particular
        category.
        """
        for i, text in enumerate(self.texts):
            text = text.lower().replace(" ", "")
            if text not in self.categories.keys():
                self.categories[text] = [i]
            else:
                self.categories[text].append(i)
                
    def classify(self):
        """
        This method is requried for `categorize_by_longest_match` which places
        the text indices on the category that had a longest match.
        """
        for i, text in enumerate(self.texts):
            text = text.lower().replace(" ", "")
            largest_size = 0
            matched_key = None
            for key in self.categories.keys():
                match = SequenceMatcher(None, text, key).find_longest_match() #NOSONAR
                if match.size > largest_size:
                    largest_size = match.size
                    matched_key = key

            if matched_key is not None:
                self.categories[matched_key].append(i)        
  