
import os


class Controller:

    def __init__(self):



        self._resume_txt = ""
        self.ln = ""




    def set_filename(self, filename):
        self._resume_txt = filename

    def set_language(self, language):
        self.ln = language

    def get_filenam(self):
        return self._resume_txt

    def get_languag(self):
        return self.ln





