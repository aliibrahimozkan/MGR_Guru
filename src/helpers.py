
from dataclasses import dataclass
import string
@dataclass
class BM25Parameters:
    k1: float = 1.2
    b: float = 0.75


def remove_punctuation(text:string):
    """
    Removing punctuation from the text
    :param text: string
    :return: updated text
    """
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)