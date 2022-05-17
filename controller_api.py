
import os

with open('status_service.txt') as f:
    status = f.readlines()[0]
    
class Controller:

    def __init__(self):



        self.status = status
        self.status_run = "404"
        self.status_desc = {str(200): "Successful operation.", "202": "Operation in progress.", "404": "Service istance not found."}




    def set_status_run(self, stato):
        self.status_run = stato

    def set_status(self, status):
        self.status = status

    def get_status_run(self):
        return self.status_run

    def get_status(self):
        return self.status





