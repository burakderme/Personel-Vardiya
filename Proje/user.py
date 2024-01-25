import database
from datetime import timedelta

class User:
    def __init__(self, username=None, password=None, registration_number=None):
        self.username = username
        self.password = password
        self.registration_number = registration_number

    # giriş yapma
    def login(self):
        self.correct_password = database.Database().fetch_data(f"SELECT password FROM users WHERE username = '{self.username}'")

        if self.correct_password:
            return self.correct_password[0][0] == self.password
        return

    # bir kullanıcının rolünü çekme
    def get_role(self):
        self.role = database.Database().fetch_data(f"SELECT role FROM users WHERE username = '{self.username}'")
        return self.role[0][0]

    # bir tablodaki tüm veriyi çekme
    def get_all_users(self, table="users", start_date=None, end_date=None):
        if not start_date:
            if not self.registration_number:
                return database.Database().fetch_data(f"SELECT * FROM {table}")
            else:
                return database.Database().fetch_data(f"SELECT * FROM {table} WHERE registration_number = '{self.registration_number}'")

    # bir kullanıcının bilgilerini çekme
    def get_user(self):
        if self.registration_number:
            return database.Database().fetch_data(f"SELECT * FROM users WHERE registration_number = '{self.registration_number}'")[0]
        elif self.username:
            try: return database.Database().fetch_data(f"SELECT * FROM users WHERE username = '{self.username}'")[0]
            except: return False
        else:
            return False