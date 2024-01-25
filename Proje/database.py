import mysql.connector
from tkinter import messagebox as ms
from yaml import safe_load

# veri tabanı bilgileri doğru mu kontrolü
def is_connected(host, user, password, database):
    try:
        config = {
                'host': host,
                'user': user,
                'password': password,
                'database': database
            }
        connection2 = mysql.connector.connect(**config)

        if connection2.is_connected():
            return True
        else:
            ms.showerror("Veri Tabanı Hatası", f"Veri tabanına bağlanılamadı. Lütfen bağlantı ayarlarını ve interneti kontrol edin.\n{error}")
            return False

    except mysql.connector.Error as error:
        ms.showerror("Veri Tabanı Hatası", f"Veri tabanına bağlanılamadı. Lütfen bağlantı ayarlarını ve interneti kontrol edin.\n{error}")
        return False

class Database:
    def __init__(self):
        try:
            with open("config.yml", 'r') as file: # veri tabanı bağlantısı
                data = safe_load(file)
            self.connection = mysql.connector.connect(
                host=data["host"],
                user=data["user"],
                password=data["password"],
                database=data["database"]
            )
            self.cursor = self.connection.cursor()
        except:
            ms.showerror("Veri Tabanı Hatası", "Veri tabanına bağlanılamadı. Lütfen bağlantı ayarlarını ve interneti kontrol edin.")
            self.close_connection()

    def execute_query(self, query): # execute işlemi
        try:
            self.cursor.execute(query)
            self.connection.commit()
            return True
        except mysql.connector.Error as e:
            ms.showinfo("Veri Tabanı Hatası!", f"Veri kaydedilirken bir hata oluştu: \n{e}")
            self.connection.rollback()
            return None
        finally:
            self.close_connection()

    def fetch_data(self, query): # veri çekme
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as e:
            ms.showinfo("Veri Tabanı Hatası!", f"Veri alınırken hata oluştu: \n{e}")
            return None
        finally:
            self.close_connection()

    def close_connection(self): # bağlantı kapatma
        self.connection.close()
