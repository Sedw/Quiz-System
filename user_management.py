
from dataclasses import dataclass
import joblib
import os


@dataclass
class Userr:
    username: str
    email: str
    password: str
    login: bool
    role: str

class UserManagement(object):
    def __init__(self) -> None:
        
        self._db_filename = os.path.join(os.path.dirname(__file__), 'db', 'users.joblib')
        
        self.current_user = None

        if os.path.exists(self._db_filename):
            self.users = joblib.load(self._db_filename)
        else:
            self.users = [
                Userr("Mojtaba", "mojtabajafary@gmail.com", "12345678", False, "admin")
            ]

    def add_user(self, user: Userr):
        self.users.append(user)

    def save(self):
        joblib.dump(self.users, self._db_filename)


    def change_login_state(self, username, password, state=True):
        for user in self.users:
                if user.username == username and user.password == password:
                    user.login = state
                    break

    def set_current_user(self, username, password):
        self.current_user = self.get_user(username, password)


    def is_user_exist(self, username, password) -> bool:
        for user in self.users:
            if user.username == username and user.password == password:
                return True
            
        return False


    def get_user(self, username, password):
        
        for user in self.users:
            if user.username == username and user.password == password:
                return user
            
        return
    
    def change_current_user_state(self, state=False):
        self.current_user.login = state


user_manager = UserManagement()