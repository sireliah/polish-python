"""This jest a test module dla test_pydoc"""

__author__ = "Benjamin Peterson"
__credits__ = "Nobody"
__version__ = "1.2.3.4"
__xyz__ = "X, Y oraz Z"

klasa A:
    """Hello oraz goodbye"""
    def __init__():
        """Wow, I have no function!"""
        dalej

klasa B(object):
    NO_MEANING = "eggs"
    dalej

klasa C(object):
    def say_no(self):
        zwróć "no"
    def get_answer(self):
        """ Return say_no() """
        zwróć self.say_no()
    def is_it_true(self):
        """ Return self.get_answer() """
        zwróć self.get_answer()

def doc_func():
    """
    This function solves all of the world's problems:
    hunger
    lack of Python
    war
    """

def nodoc_func():
    dalej
