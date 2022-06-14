
import os


class Controller:

    def __init__(self):


       
        self._resume_txt = ""
        self.ln = ""
        self.list_of_contents = {}
        self.list_file_skiss= {}
        self.folder = None
        self.run = None
        self.filenameresult=''



    def set_filenameresult(self, filename):
           self.filenameresult = filename
    def get_filenameresult(self):
            return self.filenameresult
    def set_filename(self, filename):
        self._resume_txt = filename
    def set_list_file_skiss(self, list_file_skiss):
        self.list_file_skiss = list_file_skiss
        
    def set_contents(self, contents):
     
        self.list_of_contents =contents

    def set_language(self, language):
        self.ln = language

    def get_filenam(self):
        return self._resume_txt

    def get_languag(self):
        return self.ln
    def get_contents(self):
        return self.list_of_contents
    
    def get_list_file_skisss(self):
        return self.list_file_skiss






