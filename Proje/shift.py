import mysql.connector, calendar, datetime as dt
from tkinter import messagebox as ms
from yaml import safe_load

# Otomatik vardiya algoritması

class Main:
    def __init__(self, start, end):
        try:
            with open("config.yml", 'r') as file:
                db_data = safe_load(file)
            self.start_date = start
            self.end_date = end
            self.db = mysql.connector.connect(
                host=db_data["host"],
                user=db_data["user"],
                password=db_data["password"],
                database=db_data["database"]
            )
            self.cursor = self.db.cursor()

            kampus = ["08:00-17:00", "08:00-17:00", "08:00-17:00"]
            kampus2 = ["12:00-00:00", "00:00-12:00"]
            days_between = (self.end_date - self.start_date).days
            sicil_list = self.get_sicil_list()
            for i in range(days_between):
                current_date = self.start_date + dt.timedelta(days=i)
                if sicil_list:
                    for sicil in sicil_list:
                        if self.izinsorgulama(sicil, current_date):
                            sql = "SELECT COUNT(*) FROM algorithm WHERE place = %s AND day = %s"
                            self.cursor.execute(sql, ("Kampus İçi", current_date))
                            kampus_ici = self.cursor.fetchone()[0]
                            self.cursor.execute(sql, ("Kampüs Girisi", current_date))
                            kampus_disi = self.cursor.fetchone()[0]
                            sql2 = "SELECT COUNT(*) FROM algorithm WHERE place = %s AND day = %s AND shift = %s"
                            sql3 = "INSERT INTO algorithm (registration_number, day, shift, place) VALUES (%s, %s, %s, %s)"
                            saat = ""
                            if (kampus_ici / 3) < (kampus_disi / 3):
                                bölge = "Kampüs Ici"
                                self.cursor.execute(sql2, (bölge, current_date, kampus[0]))
                                vardiyaA = self.cursor.fetchone()[0]
                                self.cursor.execute(sql2, (bölge, current_date, kampus[1]))
                                vardiyaB = self.cursor.fetchone()[0]
                                self.cursor.execute(sql2, (bölge, current_date, kampus[2]))
                                vardiyaC = self.cursor.fetchone()[0]
                                aVardiye = int(vardiyaA)
                                bVardiye = int(vardiyaB)
                                cVardiye = int(vardiyaC)
                                enKucukVardiye = min(aVardiye, bVardiye, cVardiye)
                                if enKucukVardiye == aVardiye:
                                    saat = kampus[0]
                                elif enKucukVardiye == bVardiye:
                                    saat = kampus[1]
                                elif enKucukVardiye == cVardiye:
                                    saat = kampus[2]
                                self.cursor.execute(sql3, (sicil, current_date, saat, bölge))
                                self.db.commit()
                            else:
                                bölge = "Kampüs Girisi"
                                self.cursor.execute(sql2, (bölge, current_date, kampus2[0]))
                                vardiyaA = self.cursor.fetchone()[0]
                                self.cursor.execute(sql2, (bölge, current_date, kampus2[1]))
                                vardiyaB = self.cursor.fetchone()[0]
                                aVardiye = int(vardiyaA)
                                bVardiye = int(vardiyaB)
                                if aVardiye < bVardiye:
                                    saat = kampus2[0]
                                else:
                                    saat = kampus2[1]
                                self.cursor.execute(sql3, (sicil, current_date, saat, bölge))
                                self.db.commit()
            ms.showinfo("Kayıt Başarılı!", "Otomatik vardiya başarıyla kaydedildi.")
        except Exception as e:
            ms.showerror("Beklenmedik Hata!", f"Beklenmedik hatayla karşılaşıldı:\n {e}")
        finally:
            self.db.rollback()
            self.db.close()

    def get_sicil_list(self):
        sql = "SELECT registration_number FROM users"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return [row[0] for row in result]

    def izinsorgulama(self, sicil_no, tarih):
        sql = "SELECT COUNT(*) FROM leaves WHERE registration_number = %s AND start = %s"
        self.cursor.execute(sql, (sicil_no, tarih))
        count = self.cursor.fetchone()[0]
        if count == 0:
            sql2 = "SELECT COUNT(*) FROM algorithm WHERE registration_number = %s AND day = %s"
            self.cursor.execute(sql2, (sicil_no, tarih))
            count2 = self.cursor.fetchone()[0]
            if count2 == 0:
                english_days = list(calendar.day_name)
                turkish_days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
                bugunun_gunu = english_days[tarih.weekday()]
                turkce_gun = turkish_days[english_days.index(bugunun_gunu)]

                self.cursor.execute(f"""SELECT holiday1 FROM users WHERE registration_number = '{sicil_no}'""")
                data = self.cursor.fetchall()
                self.cursor.execute(f"""SELECT holiday2 FROM users WHERE registration_number = '{sicil_no}'""")
                data2 = self.cursor.fetchall()
                if data[0][0] == turkce_gun or data2[0][0] == turkce_gun:
                    return False
                return True
        return False
