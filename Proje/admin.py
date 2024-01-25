from tkinter import filedialog, messagebox as ms
import database, user, locale
from datetime import timedelta, datetime
from yaml import safe_dump
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from random import sample

# yeni kullanıcı ekleme
def new_user(username, password, re_password, name, surname, tc_number, address, phone_number, mail, registration_number, job_title, role, holiday1="-", holiday2="-"):
    if not all([username, password, re_password, name, surname, tc_number, address, phone_number, mail, registration_number, job_title, role]):
        ms.showerror("Eksik Bilgi!", "Lütfen tatiller hariç tüm boşlukları doldurun.")
        return
    
    if len(password) <6 or len(tc_number) != 11 or len(phone_number) != 10:
        ms.showerror("Eksik Bilgi!", "Lütfen aşağıdaki kurallara uyarak boşlukları doldurun:\n- Şifre en az 6 haneli olmalı,\n- TC No 11 haneli olmalı,\n- Telefon Numarası 10 haneli olmalı (5314567890).")
        return

    if password != re_password:
        ms.showerror("Şifreler Farklı!", "Girilen şifreler birbiriyle uyuşmuyor.")
        return

    if database.Database().fetch_data(f"SELECT id FROM users WHERE username = '{username}'"):
        ms.showerror("Mevcut Kullanıcı Adı!", "Girilen kullanıcı adı zaten kullanılıyor.")
        return

    if database.Database().fetch_data(f"SELECT id FROM users WHERE registration_number = '{registration_number}'"):
        ms.showerror("Mevcut Sicil Numarası!", "Girilen sicil numarası zaten kullanılıyor.")
        return

    query = f"""
                INSERT INTO users 
                (username, password, name, surname, TC_no, address, phone_number, mail, registration_number, job_title, role, holiday1, holiday2) VALUES
                ("{username}", "{password}", "{name}", "{surname}", "{tc_number}", "{address}", "{phone_number}", "{mail}", "{registration_number}", "{job_title}", "{role}", "{holiday1}", "{holiday2}")
            """

    database.Database().execute_query(query)
    return True

# kullanıcı düzenelme
def edit_user(userID, username, password, name, surname, tc_number, address, phone_number, mail, registration_number, job_title, role, holiday1="-", holiday2="-"):
    database.Database().execute_query(f"""
                                        UPDATE users SET
                                        username = "{username}",
                                        password = "{password}",
                                        name = "{name}",
                                        surname = "{surname}",
                                        TC_no = "{tc_number}",
                                        address = "{address}",
                                        phone_number = "{phone_number}",
                                        mail = "{mail}",
                                        registration_number = "{registration_number}",
                                        job_title = "{job_title}",
                                        role =  "{role}",
                                        holiday1 = "{holiday1}",
                                        holiday2 =  "{holiday2}"
                                        WHERE id = "{userID}"
                                    """)
    return True

# kullanıcı silme
def del_user(userID):
    database.Database().execute_query(f"DELETE FROM users WHERE id='{userID}'")
    return True

# yeni izin
def new_leave(registration_number, start, end):
    if not database.Database().fetch_data(f"SELECT id FROM leaves WHERE start = '{start}' and end = '{end}' and registration_number = '{registration_number}'"):
        database.Database().execute_query(f"""
                                                INSERT INTO leaves 
                                                (registration_number, name, surname, start, end) VALUES
                                                ("{registration_number}",
                                                "{user.User(registration_number=registration_number).get_user()[3]}",
                                                "{user.User(registration_number=registration_number).get_user()[4]}",
                                                "{start}", "{end}")
                                            """)

        now = start
        while now <= end:
            database.Database().execute_query(f"""
                                                    INSERT INTO leavesAlg 
                                                    (registration_number, leave_id, date) VALUES
                                                    ("{registration_number}",
                                                    "{database.Database().fetch_data(f"SELECT id FROM leaves WHERE start = '{start}' and end = '{end}' and registration_number = '{registration_number}'")[0][0]}",
                                                    "{now.strftime('%Y-%m-%d')}")
                                                """)
            now += timedelta(days=1)

        return True
    else:
        ms.showerror("Çakışan Bilgi!", "Aynı kişi için aynı tarihlerde izin var.")


#izin 2
def new_set_shift(registration_number, start, end):
    if not database.Database().fetch_data(f"SELECT id FROM leaves WHERE start = '{start}' and end = '{end}' and registration_number = '{registration_number}'"):
        database.Database().execute_query(f"""
                                                INSERT INTO leaves 
                                                (registration_number, name, surname, start, end) VALUES
                                                ("{registration_number}",
                                                "{user.User(registration_number=registration_number).get_user()[3]}",
                                                "{user.User(registration_number=registration_number).get_user()[4]}",
                                                "{start}", "{end}")
                                            """)

        now = start
        while now <= end:
            database.Database().execute_query(f"""
                                                    INSERT INTO leavesAlg 
                                                    (registration_number, leave_id, date) VALUES
                                                    ("{registration_number}",
                                                    "{database.Database().fetch_data(f"SELECT id FROM leaves WHERE start = '{start}' and end = '{end}' and registration_number = '{registration_number}'")[0][0]}",
                                                    "{now.strftime('%Y-%m-%d')}")
                                                """)
            now += timedelta(days=1)

        return True
    else:
        ms.showerror("Çakışan Bilgi!", "Aynı kişi için aynı tarihlerde izin var.")


# izin silme
def del_leave(registration_number, start, end):
        database.Database().execute_query(f"""
                                                DELETE FROM leaves WHERE
                                                registration_number = "{registration_number}" AND
                                                start = "{start}" AND
                                                end = "{end}"
                                            """)
        return True

# vardiya ekleme
def new_shift(registration_number, date, place, hour, mode=None, old_registration_number=None, old_date=None, old_place=None, old_hour=None):
        if mode: # vardiya düzenlemesi
            if not database.Database().fetch_data(f"""SELECT * FROM algorithm WHERE registration_number='{registration_number}' and day='{date}'"""):
                if database.Database().execute_query(f"""
                                                        UPDATE algorithm 
                                                        SET day = "{date}", 
                                                        shift = "{hour}", 
                                                        place = "{place}" 
                                                        WHERE registration_number = "{old_registration_number}" AND
                                                        day = "{old_date}" AND
                                                        shift = "{old_hour}"
                                                        AND place = "{old_place}"
                                                    """):
                    return True
                else:
                    False
            ms.showerror("", "Seçilen kişinin aynı tarihte vardiyası var!")
            return False

        if not database.Database().fetch_data(f"""SELECT * FROM algorithm WHERE registration_number='{registration_number}' and day='{date}'"""):
            # özel vardiya ekleme
            if database.Database().execute_query(f"""
                                                    INSERT INTO algorithm 
                                                    (registration_number, day, shift, place) VALUES
                                                    ("{registration_number}",
                                                    "{date}",
                                                    "{hour}",
                                                    "{place}")
                                                """):
                return True
            else:
                return False
        else:
            ms.showerror("", "Seçilen kişinin aynı tarihte vardiyası var!")
            return False

# vardiya silme
def del_shift(registration_number, date, place, hour):
        database.Database().execute_query(f"""
                                                DELETE FROM algorithm WHERE
                                                registration_number = "{registration_number}" AND
                                                day = "{date}" AND
                                                shift = "{hour}" AND
                                                place = "{place}"
                                                LIMIT 1                                   
                                            """)
        return True

# veri tabanı ayarlama
def set_db(host, user, password, db):
    if not all([host, user, db]):
        ms.showerror("Eksik Bilgi!", "Lütfen tüm boşlukları doldurun.")
        return
    if not database.is_connected(host, user, password, db):
        ms.showerror("Hatalı Bilgi!", "Veri tabanına bağlanılamadı. lütfen bilgileri kontrol edin..")
        return
    else:
        data = {
            "host": host,
            "user": user,
            "password": password,
            "database": db
        }
        with open("config.yml", "w") as file:
            safe_dump(data, file, default_flow_style=False)

        database.Database().execute_query("""
                                            CREATE TABLE IF NOT EXISTS users (
                                            id INT AUTO_INCREMENT,
                                            username VARCHAR(255) ,
                                            password VARCHAR(255) ,
                                            name VARCHAR(255) ,
                                            surname VARCHAR(255) ,
                                            TC_no VARCHAR(255) ,
                                            address VARCHAR(255) ,
                                            phone_number VARCHAR(255) ,
                                            mail VARCHAR(255) ,
                                            registration_number VARCHAR(255) ,
                                            job_title VARCHAR(255) ,
                                            role VARCHAR(255) ,
                                            holiday1 VARCHAR(255) ,
                                            holiday2 VARCHAR(255) ,
                                            PRIMARY KEY (id)
                                            ) CHARACTER SET utf8 COLLATE utf8_general_ci;
                                        """)
        database.Database().execute_query("""
                                            CREATE TABLE IF NOT EXISTS leaves (
                                            id INT AUTO_INCREMENT,
                                            registration_number VARCHAR(255) ,
                                            name VARCHAR(255) ,
                                            surname VARCHAR(255) ,
                                            start VARCHAR(255) ,
                                            end VARCHAR(255) ,
                                            PRIMARY KEY (id)
                                            ) CHARACTER SET utf8 COLLATE utf8_general_ci;
                                        """)
        database.Database().execute_query("""
                                            CREATE TABLE IF NOT EXISTS leavesAlg (
                                            id INT AUTO_INCREMENT,
                                            registration_number VARCHAR(255) ,
                                            leave_id INT ,
                                            date VARCHAR(255) ,
                                            PRIMARY KEY (id),
                                            FOREIGN KEY (leave_id) REFERENCES leaves(id) ON DELETE CASCADE
                                            ) CHARACTER SET utf8 COLLATE utf8_general_ci;
                                        """)
        database.Database().execute_query("""
                                            CREATE TABLE IF NOT EXISTS algorithm (
                                            id INT AUTO_INCREMENT,
                                            registration_number VARCHAR(255) ,
                                            day VARCHAR(255) ,
                                            shift VARCHAR(255) ,
                                            place VARCHAR(255) ,
                                            PRIMARY KEY (id)
                                            ) CHARACTER SET utf8 COLLATE utf8_general_ci;
                                        """)

        new_user("admin", "admin123", "admin123", "isim", "soyisim", "10101010101", "adres adres adres adres", "5455555555", "mail", "sicilno", "Yönetici", "Yönetici")

        return True

def all_delete_shift(type=("all", "time"), start=None, end=None):
        if type == "all":
            if database.Database().execute_query("""DELETE FROM algorithm"""):
                return True
        else:
            now = start
            while now <= end:
                database.Database().execute_query(f"""DELETE FROM algorithm WHERE day = '{now}'""")
                now += timedelta(days=1)
            return True

# pdf oluşturma
def create_pdf(username="admin", type=("all", "time"), start=None, end=None):
    locale.setlocale(locale.LC_TIME, 'turkish')
    data = [["Tarih", u"İsim", "Saat", "Yer", u"İzinliler"],]
    if type == "all":
        if username == "admin":
            for data_user in user.User().get_all_users(table="algorithm"):
                weekly = user.User().get_all_users(table="users")
                normal = user.User().get_all_users(table="leavesalg")

                gun = datetime.strptime(data_user[2], "%Y-%m-%d").strftime("%A")
                leave = []

                for i in weekly:
                    if i[12] == gun or i[13] == gun:
                        leave.append(i)

                for i in normal:
                    if datetime.strptime(i[3], "%Y-%m-%d").strftime("%A") == gun:
                        if not user.User(registration_number=i[1]).get_user() in leave:
                            leave.append(user.User(registration_number=i[1]).get_user())

                if len(leave) > 3:
                    selected_items = sample(leave, 3)
                else:
                    selected_items = leave

                selected_leave = ""

                for item in selected_items:
                    selected_leave += item[3] + " " + item[4] + ", "
                selected_leave = selected_leave[:-2]

                data.append([f"{data_user[2]} - {gun}", f"{user.User(registration_number=data_user[1]).get_user()[3]} {user.User(registration_number=data_user[1]).get_user()[4]}", data_user[3], data_user[4], selected_leave])
        else:
            for data_user in user.User(registration_number=list(user.User(username=username).get_user())[9]).get_all_users(table="algorithm"):
                data.append([f"{data_user[2]} - {datetime.strptime(data_user[2], "%Y-%m-%d").strftime("%A")}", f"{user.User(registration_number=data_user[1]).get_user()[3]} {user.User(registration_number=data_user[1]).get_user()[4]}", data_user[3], data_user[4]])
    else:
        if username == "admin":
            liste = []
            now = start
            while now <= end:
                liste.append(database.Database().fetch_data(f"SELECT * FROM algorithm WHERE day = '{now}'"))
                now += timedelta(days=1)
            for data_user in liste:
                if data_user:
                    weekly = user.User().get_all_users(table="users")
                    normal = user.User().get_all_users(table="leavesalg")

                    gun = datetime.strptime(data_user[0][2], "%Y-%m-%d").strftime("%A")
                    leave = []

                    for i in weekly:
                        if i[12] == gun or i[13] == gun:
                            leave.append(i)

                    for i in normal:
                        if datetime.strptime(i[3], "%Y-%m-%d").strftime("%A") == gun:
                            if not user.User(registration_number=i[1]).get_user() in leave:
                                leave.append(user.User(registration_number=i[1]).get_user())

                    if len(leave) > 3:
                        selected_items = sample(leave, 3)
                    else:
                        selected_items = leave

                    selected_leave = ""

                    for item in selected_items:
                        selected_leave += item[3] + " " + item[4] + ", "
                    selected_leave = selected_leave[:-2]

                    data.append([f"{data_user[0][2]} - {datetime.strptime(data_user[0][2], "%Y-%m-%d").strftime("%A")}", f"{user.User(registration_number=data_user[0][1]).get_user()[3]} {user.User(registration_number=data_user[0][1]).get_user()[4]}", data_user[0][3], data_user[0][4], selected_leave])
        else:
            liste = []
            now = start
            while now <= end:
                liste.append(database.Database().fetch_data(f"SELECT * FROM algorithm WHERE day = '{now}' and registration_number = '{list(user.User(username=username).get_user())[9]}'"))
                now += timedelta(days=1)
            for data_user in liste:
                data.append([f"{data_user[0][2]} - {datetime.strptime(data_user[0][2], "%Y-%m-%d").strftime("%A")}", f"{user.User(registration_number=data_user[0][1]).get_user()[3]} {user.User(registration_number=data_user[0][1]).get_user()[4]}", data_user[0][3], data_user[0][4]])

    header = data[0]
    other_data = data[1:]
    sorted_data = sorted(other_data, key=lambda x: x[3])

    data_girisi = [item for item in data if item[3] == 'Kampüs Girisi']
    data_ici = [item for item in data if item[3] == 'Kampüs Ici']

    sorted_data_girisi = sorted(data_girisi, key=lambda x: x[0])
    sorted_data_ici = sorted(data_ici, key=lambda x: x[0])

    merged_data = [header] + sorted_data_girisi + sorted_data_ici

    for i in range(len(merged_data)):
        for j in range(len(merged_data[i])):
            merged_data[i][j] = merged_data[i][j].replace("ş", "s")
            merged_data[i][j] = merged_data[i][j].replace("ı", "i")

    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="vardiyalar.pdf")
    if not file_path:
        return
    pdf = SimpleDocTemplate(file_path, pagesize=letter)

    table = Table(merged_data)

    pdfmetrics.registerFont(TTFont('Verdana', 'verdana.ttf'))
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Verdana'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ])

    table.setStyle(style)

    elements = []
    elements.append(table)
    pdf.build(elements)
    return True




