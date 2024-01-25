from gui import Interface, set_db
import os.path
import os
def main():
    if not os.path.exists("config.yml"): # config.yml dosyası yoksa ilk açılış algılar tabloları ve yönetici kullanıcısını oluşturur.
        set_db(mode="new")
    else:
        app = Interface()
        app.root.mainloop()

if __name__ == "__main__":
    main()