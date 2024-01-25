from tkinter.ttk import Entry, Label, Frame, Button, Combobox, Treeview, LabelFrame, Checkbutton
from tkinter import Tk, Toplevel, StringVar, BooleanVar, messagebox as ms
from user import User
import admin, os.path, shift
from tkcalendar import DateEntry
from datetime import datetime

# treeview sıralaması
def sort_treeview_column(tree, col, reverse=False):
    data = [(tree.set(item, col), item) for item in tree.get_children('')]
    data.sort(reverse=reverse)
    for index, (val, item) in enumerate(data):
        tree.move(item, '', index)
    tree.heading(col, command=lambda: sort_treeview_column(tree, col, not reverse))

# pencereleri ortalamak için kullanılır
def center_window(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

# veri tabanı düzenleme
def set_db(mode=None):
    if mode == "new":
        set_db = Tk()
    else:
        set_db = Toplevel()
        set_db.grab_set()
    set_db.geometry("330x240")
    set_db.resizable(0,0)
    set_db.iconbitmap("icon.ico")
    set_db.title("Veri Tabanı Ayarları")
    center_window(set_db)

    Label(set_db, text=("Veri Tabanı Adı:")).grid(column=0, row=0, padx=10, pady=10)
    db = Entry(set_db)
    db.grid(column=1, row=0, padx=10, pady=10)

    Label(set_db, text="Host:").grid(column=0, row=1, padx=10, pady=10)
    host = Entry(set_db)
    host.grid(column=1, row=1, padx=10, pady=10)

    Label(set_db, text=("Kullanıcı Adı: ")).grid(column=0, row=2, padx=10, pady=10)
    user = Entry(set_db)
    user.grid(column=1, row=2, padx=10, pady=10)

    Label(set_db, text=("Şifre:")).grid(column=0, row=3, padx=10, pady=10)
    password = Entry(set_db, show="*")
    password.grid(column=1, row=3, padx=10, pady=10)

    def save():
        if not os.path.exists("config.yml"):
            if admin.set_db(host.get(), user.get(), password.get(), db.get()):
                set_db.destroy()
                Interface()

    saveButton = Button(set_db, text="Kaydet", command=save) 
    saveButton.grid(column=0, row=4, padx=10, pady=10, columnspan=2)

    set_db.mainloop()

# giriş yapma arayüzü
class Interface:
    def __init__(self):
        self.root = Tk()
        self.root.resizable(0,0)
        self.root.iconbitmap("icon.ico")
        self.root.title("Giriş Yap")
        self.root.geometry("300x130")
        center_window(self.root)

        self.login_frame = Frame(self.root)
        self.login_frame.pack()

        self.username_label = Label(self.login_frame, text="Kullanıcı Adı:")
        self.login_username_entry = Entry(self.login_frame)
        self.password_label = Label(self.login_frame, text="Şifre:")
        self.password_entry = Entry(self.login_frame, show="*")
        self.login_button = Button(self.login_frame, text="Giriş", command=self.login)

        self.username_label.grid(row=0, column=0, padx=10, pady=10)
        self.login_username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        self.login_button.grid(row=2, column=0, columnspan=3)

    def login(self):
        if User(self.login_username_entry.get(), self.password_entry.get()).login():
            global login_username
            login_username = self.login_username_entry.get()
            if User(self.login_username_entry.get()).get_role() == "Yönetici":
                self.root.destroy()
                AdminInterface()
            else:
                self.root.destroy()
                StaffInterface()
        else:
            ms.showerror("Hatalı Giriş!", "Hatalı kullanıcı adı veya şifre.")

    def logout(self):
        self.root.destroy()
        Interface()

# admin arayüzü
class AdminInterface(Interface):
    def __init__(self):
        super().__init__()
        self.root.title("Yönetici Arayüzü") 
        self.login_frame.destroy()
        self.root.geometry("600x330")
        center_window(self.root)

        self.admin_frame = Frame(self.root)
        self.admin_frame.pack()

        self.new_user_button = Button(self.admin_frame, text="Yeni Kullanıcı", command=lambda: self.set_user("new"))
        self.new_user_button.grid(row=0, column=0, pady=10)

        self.new_leave_button = Button(self.admin_frame, text="İzinler", command=self.set_leave)
        self.new_leave_button.grid(row=0, column=1, pady=10)

        self.shift_button = Button(self.admin_frame, text="Vardiyalar", command=self.set_shift)
        self.shift_button.grid(row=0, column=2, pady=10)

        self.users_tree = Treeview(self.admin_frame, columns=("Sicil Numarası", "İsim Soyisim", "Telefon", "Rol"), show="headings", selectmode="browse")
        self.users_tree.heading("#1", text="Sicil Numarası")
        self.users_tree.heading("#2", text="İsim Soyisim")
        self.users_tree.heading("#3", text="Telefon")
        self.users_tree.heading("#4", text="Rol")
        self.users_tree.column("#1", width=120)
        self.users_tree.column("#2", width=150)
        self.users_tree.column("#3", width=100)
        self.users_tree.column("#4", width=80)
        self.users_tree.grid(row=1, column=0, columnspan=3, padx=10)

        self.settings_button = Button(self.admin_frame, text="Veri Tabanı Ayarları", command=set_db)
        self.settings_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.logout_button = Button(self.admin_frame, text="Çıkış Yap", command=self.logout)
        self.logout_button.grid(row=2, column=2, columnspan=2, pady=10)

        for self.user in User().get_all_users():
            self.users_tree.insert("", "end", values=(self.user[9], (self.user[3], self.user[4]), self.user[7], self.user[11]))

        def double_click(event):
            if self.users_tree.item(self.users_tree.selection())["values"]:
                self.set_user(type="set")

        self.users_tree.bind("<Double-1>", double_click)

    def top_close(self, top):
        self.root.deiconify()
        top.destroy()

# kullanıcı ekleme - düzenleme - silme
    def set_user(self, type=("new", "set")):
        self.set_top = Toplevel()
        self.set_top.geometry("650x430")
        self.set_top.iconbitmap("icon.ico")
        self.set_top.grab_set()
        center_window(self.set_top)
        self.root.withdraw()
        self.set_top.protocol("WM_DELETE_WINDOW", lambda: self.top_close(self.set_top))

        self.username_label = Label(self.set_top, text="Kullanıcı Adı:")
        self.username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.username_entry = Entry(self.set_top)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.password_label = Label(self.set_top, text="Şifre:")
        self.password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = Entry(self.set_top, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.name_label = Label(self.set_top, text="İsim:")
        self.name_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.name_entry = Entry(self.set_top)
        self.name_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.surname_label = Label(self.set_top, text="Soyisim:")
        self.surname_label.grid(row=2, column=2, padx=10, pady=10, sticky="e")
        self.surname_entry = Entry(self.set_top)
        self.surname_entry.grid(row=2, column=3, padx=10, pady=10, sticky="w")

        self.tc_label = Label(self.set_top, text="TC. Numarası:")
        self.tc_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.tc_entry = Entry(self.set_top)
        self.tc_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.address_label = Label(self.set_top, text="Adres:")
        self.address_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.address_entry = Entry(self.set_top)
        self.address_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        self.mail_label = Label(self.set_top, text="Mail:")
        self.mail_label.grid(row=4, column=2, padx=10, pady=10, sticky="e")
        self.mail_entry = Entry(self.set_top)
        self.mail_entry.grid(row=4, column=3, padx=10, pady=10, sticky="w")

        self.phone_number_label = Label(self.set_top, text="Telefon:")
        self.phone_number_label.grid(row=5, column=0, padx=10, pady=10, sticky="e")
        self.phone_number_entry = Entry(self.set_top)
        self.phone_number_entry.grid(row=5, column=1, padx=10, pady=10, sticky="w")

        self.first_holiday_label = Label(self.set_top, text="1. Tatil Günü:")
        self.first_holiday_label.grid(row=5, column=2, padx=10, pady=10, sticky="e")
        self.first_holiday_combo = Combobox(self.set_top, state="readonly", values=("-", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"))
        self.first_holiday_combo.grid(row=5, column=3, padx=10, pady=10, sticky="w")

        self.registration_number_label = Label(self.set_top, text="Sicil Numarası:")
        self.registration_number_label.grid(row=6, column=0, padx=10, pady=10, sticky="e")
        self.registration_number_entry = Entry(self.set_top)
        self.registration_number_entry.grid(row=6, column=1, padx=10, pady=10, sticky="w")

        self.second_holiday_label = Label(self.set_top, text="2. Tatil Günü:")
        self.second_holiday_label.grid(row=6, column=2, padx=10, pady=10, sticky="e")
        self.second_holiday_combo = Combobox(self.set_top, state="readonly", values=("-", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"))
        self.second_holiday_combo.grid(row=6, column=3, padx=10, pady=10, sticky="w")

        self.job_title_label = Label(self.set_top, text="Görev:")
        self.job_title_label.grid(row=7, column=0, padx=10, pady=10, sticky="e")
        self.job_title_var = StringVar()
        self.job_title_values = ("-","Bekçi", "Temizlikçi", "Hizmetli", "Güvenlik Görevlisi")
        self.job_title_combo = Combobox(self.set_top, state="readonly", values=self.job_title_values, textvariable=self.job_title_var)
        self.job_title_combo.grid(row=7, column=1, padx=10, pady=10, sticky="w")

        self.role_label = Label(self.set_top, text="Rol:")
        self.role_label.grid(row=7, column=2, padx=10, pady=10, sticky="e")
        self.role_var = StringVar()
        self.role_values = ("Yönetici", "Memur", "İşçi")
        self.role_combo = Combobox(self.set_top, state="readonly", values=self.role_values, textvariable=self.role_var)
        self.role_combo.grid(row=7, column=3, padx=10, pady=10, sticky="w")

        self.save_button = Button(self.set_top, text="Kaydet")

        if type == "new":
            self.set_top.title("Yeni Kullanıcı Ekle")
            self.re_password_label = Label(self.set_top, text="Şifre Onayla:")
            self.re_password_label.grid(row=1, column=2, padx=10, pady=10, sticky="e")
            self.re_password_entry = Entry(self.set_top, show="*")
            self.re_password_entry.grid(row=1, column=3, padx=10, pady=10, sticky="w")
            self.job_title_combo.current(0)
            self.role_combo.current(0)
            self.first_holiday_combo.current(0)
            self.second_holiday_combo.current(0)

            def confirm_save():
                if admin.new_user(self.username_entry.get(),
                                    self.password_entry.get(),
                                    self.re_password_entry.get(),
                                    self.name_entry.get(),
                                    self.surname_entry.get(),
                                    self.tc_entry.get(),
                                    self.address_entry.get(),
                                    self.phone_number_entry.get(),
                                    self.mail_entry.get(),
                                    self.registration_number_entry.get(),
                                    self.job_title_combo.get(),
                                    self.role_combo.get(),
                                    self.first_holiday_combo.get(),
                                    self.second_holiday_combo.get()):
                    self.top_close(self.set_top)
                    ms.showinfo("Kullanıcı Kaydedildi!", "Kullanıcı başarıyla kaydedildi.")
                    self.users_tree.delete(*self.users_tree.get_children())
                    for self.user in User().get_all_users():
                        self.users_tree.insert("", "end", values=(self.user[9], (self.user[3], self.user[4]), self.user[7], self.user[11]))

            self.save_button.grid(row=8, column=0, columnspan=5, pady=10)
            self.save_button["command"] = confirm_save

        else:
            self.user = list(User(registration_number=self.users_tree.item(self.users_tree.selection())["values"][0]).get_user())
            self.set_top.title("Kullanıcı Düzenle")
            for i in range(1, 12):
                if self.user[i] is None:
                    self.user[i] = " "
            self.username_entry.insert(0, self.user[1])
            self.password_entry.insert(0, self.user[2])
            self.name_entry.insert(0, self.user[3])
            self.surname_entry.insert(0, self.user[4])
            self.tc_entry.insert(0, self.user[5])
            self.address_entry.insert(0, self.user[6])
            self.phone_number_entry.insert(0, self.user[7])
            self.mail_entry.insert(0, self.user[8])
            self.registration_number_entry.insert(0, self.user[9])
            self.job_title_var.set(self.user[10])
            self.role_var.set(self.user[11])
            self.first_holiday_combo.set(self.user[12])
            self.second_holiday_combo.set(self.user[13])

            def confirm_delete():
                if ms.askyesno("Kullanıcı Sil!", "Kullanıcı kaydını silmek istediğine emin misin?"):
                    if admin.del_user(userID=self.user[0]):
                        self.top_close(self.set_top)
                        ms.showinfo("Kullanıcı Silindi!", "Kullanıcı başarıyla silindi.")
                        self.users_tree.delete(*self.users_tree.get_children())
                        for self.user in User().get_all_users():
                            self.users_tree.insert("", "end", values=(self.user[9], (self.user[3], self.user[4]), self.user[7], self.user[11]))

            def confirm_edit():
                if admin.edit_user(self.user[0],
                                    self.username_entry.get(),
                                    self.password_entry.get(),
                                    self.name_entry.get(),
                                    self.surname_entry.get(),
                                    self.tc_entry.get(),
                                    self.address_entry.get(),
                                    self.phone_number_entry.get(),
                                    self.mail_entry.get(),
                                    self.registration_number_entry.get(),
                                    self.job_title_combo.get(),
                                    self.role_combo.get(),
                                    self.first_holiday_combo.get(),
                                    self.second_holiday_combo.get()):
                    self.top_close(self.set_top)
                    self.set_top.destroy()
                    ms.showinfo("Kullanıcı Bilgileri Düzenlendi!", "Kullanıcı başarıyla düzenlendi.")
                    self.users_tree.delete(*self.users_tree.get_children())
                    for self.user in User().get_all_users():
                        self.users_tree.insert("", "end", values=(self.user[9], (self.user[3], self.user[4]), self.user[7], self.user[11]))


            self.del_button = Button(self.set_top, text="Sil", command=confirm_delete)
            self.del_button.grid(row=8, column=2, columnspan=7, pady=10)
            self.save_button["command"] = confirm_edit
            self.save_button.grid(row=8, column=0, columnspan=3, pady=10)

# izin ekleme - silme
    def set_leave(self):
        self.set_leave = Toplevel()
        self.set_leave.geometry("950x300")
        self.set_leave.resizable(0,0)
        self.set_leave.iconbitmap("icon.ico")
        self.set_leave.title("İzinler")
        self.set_leave.grab_set()
        center_window(self.set_leave)
        self.root.withdraw()
        self.set_leave.protocol("WM_DELETE_WINDOW", lambda: self.top_close(self.set_leave))

        self.enter_frame = LabelFrame(self.set_leave, text="Yeni İzin")
        self.enter_frame.grid(column=0, row=0, padx=10, pady=10)

        self.registration_label = Label(self.enter_frame, text="Sicil Numarası:")
        self.registration_label.grid(column=0, row=0, padx=10, pady=10)
        self.registration_values = []
        for self.registration_number in User().get_all_users():
            self.registration_values.append(f"{self.registration_number[9]} ({self.registration_number[3]} {self.registration_number[4]})")
        self.registration_combo = Combobox(self.enter_frame, values=self.registration_values, state="readonly", width=25)
        self.registration_combo.grid(column=1, row=0, padx=10, pady=10)

        self.start_date_label = Label(self.enter_frame, text="İzin Başlangıç Tarihi:")
        self.start_date_label.grid(column=0, row=1, padx=10, pady=10)
        self.start_day_select = DateEntry(self.enter_frame)
        self.start_day_select.grid(column=1, row=1, padx=10, pady=10)

        self.end_date_label = Label(self.enter_frame, text="İzin Bitiş Tarihi:")
        self.end_date_label.grid(column=0, row=2, padx=10, pady=10)
        self.end_day_select = DateEntry(self.enter_frame)
        self.end_day_select.grid(column=1, row=2, padx=10, pady=10)

        def new_leave():
            if all([(self.registration_combo.get().split(" ")[0]), self.start_day_select.get(), self.end_day_select.get_date()]):
                if admin.new_leave((self.registration_combo.get().split(" ")[0]), self.start_day_select.get_date(), self.end_day_select.get_date()):
                    ms.showinfo("İzin Kaydedildi!", "İzin başarıyla kaydedildi.")
                    insert_leaves_tree()
            else:
                ms.showerror("Eksik Bilgi!", "Lütfen tüm boşlukları doldurun.")

        self.new_button  = Button(self.enter_frame, text="Ekle", command=new_leave)
        self.new_button.grid(column=0, row=3, padx=10, pady=10, columnspan=3)

        self.data_frame = LabelFrame(self.set_leave, text="İzin Listesi")
        self.data_frame.grid(column=1, row=0, padx=10, pady=10)

        def insert_leaves_tree():
            self.leaves_tree.delete(*self.leaves_tree.get_children())
            for self.user in User().get_all_users(table="leaves"):
                self.leaves_tree.insert("", "end", values=(self.user[1], (self.user[2], self.user[3]), self.user[4], self.user[5]))

        def double_click(event):
            if self.leaves_tree.item(self.leaves_tree.selection())["values"]:
                if ms.askyesno("İzin Sil!", "İzini silmek istediğinize emin misin?"):
                    if admin.del_leave(User(registration_number=(self.leaves_tree.item(self.leaves_tree.selection())["values"][0])).get_user()[9], self.start_day_select.get_date(), self.end_day_select.get_date()):
                        ms.showinfo("İzin Silindi!", "İzin kaydı başarıyla silindi.")
                        insert_leaves_tree()

        self.leaves_tree = Treeview(self.data_frame, columns=("Sicil Numarası", "İsim Soyisim", "Başlangıç", "Bitiş"), show="headings", selectmode="browse")
        self.leaves_tree.heading("#1", text="Sicil Numarası")
        self.leaves_tree.heading("#2", text="İsim Soyisim")
        self.leaves_tree.heading("#3", text="Başlangıç")
        self.leaves_tree.heading("#4", text="Bitiş")
        self.leaves_tree.column("#1", width=110)
        self.leaves_tree.column("#2", width=140)
        self.leaves_tree.column("#3", width=100)
        self.leaves_tree.column("#4", width=100)
        self.leaves_tree.grid(column=0, row=0, columnspan=3, padx=10, pady=10)
        self.leaves_tree.bind("<Double-1>", double_click)
        insert_leaves_tree()
    
# vardiya ekleme - silme - düzenleme
    def set_shift(self):
        self.set_shift = Toplevel()
        self.set_shift.geometry("1050x330")
        self.set_shift.resizable(0,0)
        self.set_shift.iconbitmap("icon.ico")
        self.set_shift.title("Vardiyalar")
        self.set_shift.grab_set()
        center_window(self.set_shift)
        self.root.withdraw()
        self.set_shift.protocol("WM_DELETE_WINDOW", lambda: self.top_close(self.set_shift))

        self.enter_frame = LabelFrame(self.set_shift, text="Yeni Vardiya")
        self.enter_frame.grid(column=0, row=0, padx=10, pady=10)

        self.registration_label = Label(self.enter_frame, text="Sicil Numarası:")
        self.registration_label.grid(column=0, row=0, padx=10, pady=10)
        self.registration_values = []
        for self.registration_number in User().get_all_users():
            if self.registration_number[11] != "Yönetici":
                self.registration_values.append(f"{self.registration_number[9]} ({self.registration_number[3]} {self.registration_number[4]})")
        self.registration_combo = Combobox(self.enter_frame, values=self.registration_values, state="readonly", width=25)
        self.registration_combo.grid(column=1, row=0, padx=10, pady=10)

        self.shift_date_label = Label(self.enter_frame, text="Vardiya Tarihi:")
        self.shift_date_label.grid(column=0, row=1, padx=10, pady=10)
        self.shift_date_select = DateEntry(self.enter_frame)
        self.shift_date_select.grid(column=1, row=1, padx=10, pady=10)

        def set_shift_hours_values(event):
            if self.shift_place_select.get() == "Kampüs Içi":
                self.shift_hour_select["values"] = ("08:00-17:00")
            else:
                self.shift_hour_select["values"] = ("12:00-00:00", "00:00-12:00")
            self.shift_hour_select["state"] = "readonly"

        self.shift_place_label = Label(self.enter_frame, text="Vardiya Yeri:")
        self.shift_place_label.grid(column=0, row=2, padx=10, pady=10)
        self.shift_place_select = Combobox(self.enter_frame, state="readonly", values=("Kampüs Girisi", "Kampüs Içi"))
        self.shift_place_select.grid(column=1, row=2, padx=10, pady=10)
        self.shift_place_select.bind("<<ComboboxSelected>>", set_shift_hours_values)

        self.shift_hour_label = Label(self.enter_frame, text="Vardiya Saati:")
        self.shift_hour_label.grid(column=0, row=3, padx=10, pady=10)
        self.shift_hour_select = Combobox(self.enter_frame, state="disabled")
        self.shift_hour_select.grid(column=1, row=3, padx=10, pady=10)

        def new_shift():
            if all([(self.registration_combo.get().split(" ")[0]), self.shift_date_select.get_date(), self.shift_place_select.get(), self.shift_hour_select.get()]):
                self.leaves = User().get_all_users(table="leaves")
                count = 0
                for self.leave in self.leaves:
                    if self.leave[1] == (self.registration_combo.get().split(" ")[0]):
                        count += 1
                        if datetime.strptime(self.leave[4], "%Y-%m-%d").date() <= self.shift_date_select.get_date() <= datetime.strptime(self.leave[5], "%Y-%m-%d").date():
                            ms.showerror("Personel İzinli!", "Personel belirtilen tarihte izinli.")
                        else:
                            if admin.new_shift((self.registration_combo.get().split(" ")[0]), self.shift_date_select.get_date(), self.shift_place_select.get(), self.shift_hour_select.get()):
                                ms.showinfo("Kayıt Başarılı", "Vardiya başarıyla kaydedildi.")
                                insert_shift_tree()
                                return
                if count == 0:
                    if admin.new_shift((self.registration_combo.get().split(" ")[0]), self.shift_date_select.get_date(), self.shift_place_select.get(), self.shift_hour_select.get()):
                        ms.showinfo("Kayıt Başarılı", "Vardiya başarıyla kaydedildi.")
                        insert_shift_tree()
                        return
            else:
                ms.showerror("Eksik Bilgi!", "Lütfen tüm boşlukları doldurun.")

        self.new_button  = Button(self.enter_frame, text="Ekle", command=new_shift)
        self.new_button.grid(column=0, row=4, padx=10, pady=10)

        def auto_shift():
            self.auto_shift_top = Toplevel()
            self.auto_shift_top.geometry("330x200")
            self.auto_shift_top.resizable(0,0)
            self.auto_shift_top.iconbitmap("icon.ico")
            self.auto_shift_top.title("Otomatik Vardiya Ekleme")
            self.auto_shift_top.grab_set()
            center_window(self.auto_shift_top)

            self.start_date_label = Label(self.auto_shift_top, text="Vardiya Başlangıç Tarihi:")
            self.start_date_label.grid(column=0, row=1, padx=10, pady=10)
            self.start_day_select = DateEntry(self.auto_shift_top)
            self.start_day_select.grid(column=1, row=1, padx=10, pady=10)

            self.end_date_label = Label(self.auto_shift_top, text="Vardiya Bitiş Tarihi:")
            self.end_date_label.grid(column=0, row=2, padx=10, pady=10)
            self.end_day_select = DateEntry(self.auto_shift_top)
            self.end_day_select.grid(column=1, row=2, padx=10, pady=10)

            def save_auto():
                if all([self.start_day_select.get_date(), self.end_day_select.get_date()]):
                    shift.Main(start=self.start_day_select.get_date(), end=self.end_day_select.get_date())
                    insert_shift_tree()
                    self.auto_shift_top.destroy()
                else:
                    ms.showerror("Eksik Bilgi", "Lütfen tarihleri tam girin.")

            self.auto_save_button  = Button(self.auto_shift_top, text="Otomatik Ekle", command=save_auto)
            self.auto_save_button.grid(column=0, row=4, padx=10, pady=10, columnspan=3)

        self.auto_button  = Button(self.enter_frame, text="Otomatik Ekle", command=auto_shift)
        self.auto_button.grid(column=1, row=4, padx=10, pady=10)

        def export_pdf():
            self.export_top = Toplevel(self.set_shift)
            self.export_top.geometry("330x200")
            self.export_top.resizable(0,0)
            self.export_top.iconbitmap("icon.ico")
            self.export_top.title("Toplu Vardiya Silme")
            self.export_top.grab_set()
            center_window(self.export_top)

            self.start_date_label = Label(self.export_top, text="Başlangıç Tarihi:")
            self.start_date_label.grid(column=0, row=0, padx=10, pady=10)
            self.start_day_select = DateEntry(self.export_top)
            self.start_day_select.grid(column=1, row=0, padx=10, pady=10)

            self.end_date_label = Label(self.export_top, text="Bitiş Tarihi:")
            self.end_date_label.grid(column=0, row=1, padx=10, pady=10)
            self.end_day_select = DateEntry(self.export_top)
            self.end_day_select.grid(column=1, row=1, padx=10, pady=10)

            def checkbutton_check():
                if self.check_var.get():
                    self.start_day_select["state"] = "disabled"
                    self.end_day_select["state"] = "disabled"
                else: 
                    self.start_day_select["state"] = "normal"
                    self.end_day_select["state"] = "normal"

            self.check_var = BooleanVar()
            self.all_checkbutton = Checkbutton(self.export_top, text="Hepsini Çıkar", variable=self.check_var, command=checkbutton_check)
            self.all_checkbutton.grid(column=0, row=2, padx=10, pady=10)

            def export():
                if self.check_var.get():
                    if admin.create_pdf(type="all"):
                        ms.showinfo("Liste çıkartıldı!", "Liste başarıyla çıkartıldı.")
                        self.export_top.destroy()
                else:
                    if admin.create_pdf(type="time", start=self.start_day_select.get_date(), end=self.end_day_select.get_date()):
                        ms.showinfo("Liste çıkartıldı!", "Liste başarıyla çıkartıldı.")
                        self.export_top.destroy()

            self.export_button  = Button(self.export_top, text="Çıkart", command=export)
            self.export_button.grid(column=0, row=3, columnspan=2, padx=10, pady=10)

        self.export_button  = Button(self.enter_frame, text="Liste Çıkar", command=export_pdf)
        self.export_button.grid(column=0, row=5, padx=10, pady=10)

        def all_delete():
            self.all_del_top = Toplevel(self.set_shift)
            self.all_del_top.geometry("330x200")
            self.all_del_top.resizable(0,0)
            self.all_del_top.iconbitmap("icon.ico")
            self.all_del_top.title("Toplu Vardiya Silme")
            self.all_del_top.grab_set()
            center_window(self.all_del_top)

            self.start_date_label = Label(self.all_del_top, text="Başlangıç Tarihi:")
            self.start_date_label.grid(column=0, row=0, padx=10, pady=10)
            self.start_day_select = DateEntry(self.all_del_top)
            self.start_day_select.grid(column=1, row=0, padx=10, pady=10)

            self.end_date_label = Label(self.all_del_top, text="Bitiş Tarihi:")
            self.end_date_label.grid(column=0, row=1, padx=10, pady=10)
            self.end_day_select = DateEntry(self.all_del_top)
            self.end_day_select.grid(column=1, row=1, padx=10, pady=10)

            def checkbutton_check():
                if self.check_var.get():
                    self.start_day_select["state"] = "disabled"
                    self.end_day_select["state"] = "disabled"
                else: 
                    self.start_day_select["state"] = "normal"
                    self.end_day_select["state"] = "normal"

            self.check_var = BooleanVar()
            self.all_checkbutton = Checkbutton(self.all_del_top, text="Hepsini Sil", variable=self.check_var, command=checkbutton_check)
            self.all_checkbutton.grid(column=0, row=2, padx=10, pady=10)

            def delete():
                if self.check_var.get():
                    if admin.all_delete_shift(type="all"):
                        ms.showinfo("Vardiya Silindi!", "Vardiyalar başarıyla silindi.")
                        insert_shift_tree()
                        self.all_del_top.destroy()
                else:
                    if admin.all_delete_shift("time", self.start_day_select.get_date(), self.end_day_select.get_date()):
                        ms.showinfo("Vardiya Silindi!", "Vardiyalar başarıyla silindi.")
                        insert_shift_tree()
                        self.all_del_top.destroy()

            self.delete_button  = Button(self.all_del_top, text="Sil", command=delete)
            self.delete_button.grid(column=0, row=3, columnspan=2, padx=10, pady=10)

        self.all_delete_button  = Button(self.enter_frame, text="Toplu Sil", command=all_delete)
        self.all_delete_button.grid(column=1, row=5, padx=10, pady=10)

        self.data_frame = LabelFrame(self.set_shift, text="İzin Listesi")
        self.data_frame.grid(column=1, row=0, padx=10, pady=10)

        def insert_shift_tree():
            self.shifts_tree.delete(*self.shifts_tree.get_children())
            for self.user in User().get_all_users(table="algorithm"):
                self.name = User(registration_number=self.user[1]).get_user()[3] + " " + User(registration_number=self.user[1]).get_user()[4]
                self.shifts_tree.insert("", "end", values=(self.user[1], self.name, self.user[2], self.user[3], self.user[4]))

        def double_click(event):
            if self.shifts_tree.item(self.shifts_tree.selection())["values"]:
                self.edit_shift = Toplevel(self.set_shift)
                self.edit_shift.geometry("330x270")
                self.edit_shift.resizable(0,0)
                self.edit_shift.iconbitmap("icon.ico")
                self.edit_shift.title("Vardiya Düzenle")
                self.edit_shift.grab_set()
                center_window(self.edit_shift)

                self.registration_label_edit = Label(self.edit_shift, text="Sicil Numarası:")
                self.registration_label_edit.grid(column=0, row=0, padx=10, pady=10)
                self.registration_combo_edit = Combobox(self.edit_shift, state="readonly")
                self.registration_combo_edit.set((self.shifts_tree.item(self.shifts_tree.selection())["values"][0]))
                self.registration_combo_edit.grid(column=1, row=0, padx=10, pady=10)

                self.shift_date_label_edit = Label(self.edit_shift, text="Vardiya Tarihi:")
                self.shift_date_label_edit.grid(column=0, row=1, padx=10, pady=10)
                self.shift_date_select_edit = DateEntry(self.edit_shift)
                self.shift_date_select_edit.grid(column=1, row=1, padx=10, pady=10)

                def set_shift_hours_values_edit(event):
                    if self.shift_place_select_edit.get() == "Kampüs Içi":
                        self.shift_hour_select_edit["values"] = ("08:00-17:00", "08:00-17:00", "08:00-17:00")
                    else:
                        self.shift_hour_select_edit["values"] = ("12:00-00:00", "00:00-12:00")
                    self.shift_hour_select_edit["state"] = "readonly"

                self.shift_place_label_edit = Label(self.edit_shift, text="Vardiya Yeri:")
                self.shift_place_label_edit.grid(column=0, row=2, padx=10, pady=10)
                self.shift_place_select_edit = Combobox(self.edit_shift, state="readonly", values=("Kampüs Girisi", "Kampüs Içi"))
                self.shift_place_select_edit.grid(column=1, row=2, padx=10, pady=10)
                self.shift_place_select_edit.bind("<<ComboboxSelected>>", set_shift_hours_values_edit)
                self.shift_place_select_edit.set(((self.shifts_tree.item(self.shifts_tree.selection())["values"])[4]))

                self.shift_hour_label_edit = Label(self.edit_shift, text="Vardiya Saati:")
                self.shift_hour_label_edit.grid(column=0, row=3, padx=10, pady=10)
                self.shift_hour_select_edit = Combobox(self.edit_shift, state="readonly")
                self.shift_hour_select_edit.grid(column=1, row=3, padx=10, pady=10)

                def edit_shift():
                    if all([self.shift_date_select_edit.get_date(), self.shift_place_select_edit.get(), self.shift_hour_select_edit.get()]):
                        self.leaves_edit = User().get_all_users(table="leaves")
                        count_edit = 0
                        for self.leave_edit in self.leaves_edit:
                            if self.leave_edit[1] == (self.registration_combo_edit.get().split(" ")[0]):
                                count_edit += 1
                                if datetime.strptime(self.leave_edit[4], "%Y-%m-%d").date() <= self.shift_date_select_edit.get_date() <= datetime.strptime(self.leave_edit[5], "%Y-%m-%d").date():
                                    ms.showerror("Personel İzinli!", "Personel belirtilen tarihte izinli.")
                                else:
                                    if admin.new_shift((self.registration_combo_edit.get().split(" ")[0]), self.shift_date_select_edit.get_date(), self.shift_place_select_edit.get(), self.shift_hour_select_edit.get(), mode="edit", old_registration_number=(self.shifts_tree.item(self.shifts_tree.selection())["values"][0]), old_date=self.shifts_tree.item(self.shifts_tree.selection())["values"][2], old_place=self.shifts_tree.item(self.shifts_tree.selection())["values"][4], old_hour=self.shifts_tree.item(self.shifts_tree.selection())["values"][3]):
                                        ms.showinfo("Kayıt Başarılı", "Vardiya başarıyla kaydedildi.")
                                        self.edit_shift.destroy()
                                        insert_shift_tree()
                                        return
                        if count_edit == 0:
                            if admin.new_shift((self.registration_combo_edit.get().split(" ")[0]), self.shift_date_select_edit.get_date(), self.shift_place_select_edit.get(), self.shift_hour_select_edit.get(), mode="edit", old_registration_number=(self.shifts_tree.item(self.shifts_tree.selection())["values"][0]), old_date=self.shifts_tree.item(self.shifts_tree.selection())["values"][2], old_place=self.shifts_tree.item(self.shifts_tree.selection())["values"][4], old_hour=self.shifts_tree.item(self.shifts_tree.selection())["values"][3]):
                                ms.showinfo("Kayıt Başarılı", "Vardiya başarıyla kaydedildi.")
                                self.edit_shift.destroy()
                                insert_shift_tree()
                                return
                    else:
                        ms.showerror("Eksik Bilgi!", "Lütfen tüm boşlukları doldurun.")

                self.save_button_edit = Button(self.edit_shift, text="Kaydet", command=edit_shift)
                self.save_button_edit.grid(column=0, row=4, padx=10, pady=10)

                self.cancel_button_edit = Button(self.edit_shift, text="İptal", command=lambda: self.edit_shift.destroy())
                self.cancel_button_edit.grid(column=1, row=4, padx=10, pady=10)

                def del_shift():
                    if ms.askyesno("Vardiya Sil!", "Vardiyayı silmek istediğinize emin misin?"):
                        if admin.del_shift(self.shifts_tree.item(self.shifts_tree.selection())["values"][0], self.shifts_tree.item(self.shifts_tree.selection())["values"][2], self.shifts_tree.item(self.shifts_tree.selection())["values"][4], self.shifts_tree.item(self.shifts_tree.selection())["values"][3]):
                            ms.showinfo("Vardiya Silindi!", "Vardiya kaydı başarıyla silindi.")
                            self.edit_shift.destroy()
                            insert_shift_tree()

                self.del_button_edit = Button(self.edit_shift, text="Sil", command=del_shift)
                self.del_button_edit.grid(column=0, row=5, padx=10, pady=10, columnspan=2)

        self.shifts_tree = Treeview(self.data_frame, columns=("Sicil No", "İsim", "Tarih", "Saat", "Yer"), show="headings", selectmode="browse")
        self.shifts_tree.heading("#1", text="Sicil No")
        self.shifts_tree.heading("#2", text="İsim", command=lambda: sort_treeview_column(self.shifts_tree, "İsim", False))
        self.shifts_tree.heading("#3", text="Tarih", command=lambda: sort_treeview_column(self.shifts_tree, "Tarih", False))
        self.shifts_tree.heading("#4", text="Saat", command=lambda: sort_treeview_column(self.shifts_tree, "Saat", False))
        self.shifts_tree.heading("#5", text="Yer", command=lambda: sort_treeview_column(self.shifts_tree, "Yer", False))
        self.shifts_tree.column("#1", width=110)
        self.shifts_tree.column("#2", width=150)
        self.shifts_tree.column("#3", width=120)
        self.shifts_tree.column("#4", width=120)
        self.shifts_tree.column("#5", width=120)
        self.shifts_tree.grid(column=0, row=0, columnspan=3, padx=10, pady=10)
        self.shifts_tree.bind("<Double-1>", double_click)
        insert_shift_tree()

# kullanıcı arayüzü
class StaffInterface(Interface):
    def __init__(self):
        super().__init__()
        self.root.title("Personel Arayüzü")
        self.root.geometry("770x320")
        self.root.resizable(0,0)
        self.login_frame.destroy()
        center_window(self.root)

        self.info_frame = LabelFrame(self.root, text="Bilgilerim")
        self.info_frame.grid(column=0, row=0, padx=10, pady=10)

        self.user = list(User(username=login_username).get_user())

        self.info_label = Label(self.info_frame, text=
                                f"Kullanıcı Adı    : {self.user[1]}\n"
                                f"İsim Soyisim     : {self.user[3]} {self.user[4]}\n"
                                f"TC Numarası    : {self.user[5]}\n"
                                f"Adres                : {self.user[6]}\n"
                                f"Telefon             : {self.user[7]}\n"
                                f"Mail Adresi       : {self.user[8]}\n"
                                f"Sicil Numarası  : {self.user[9]}\n"
                                f"Görev                : {self.user[10]}\n"
                                f"Rol                    : {self.user[11]}")
        self.info_label.grid(column=0, row=0, padx=10, pady=10)

        self.logout_button = Button(self.info_frame, text="Çıkış Yap", command=self.logout)
        self.logout_button.grid(column=0, row=1, padx=10, pady=10)

        self.data_frame = LabelFrame(self.root, text="Vardiya Listesi")
        self.data_frame.grid(column=1, row=0, padx=10, pady=10)

        def insert_shift_tree():
            self.shifts_tree.delete(*self.shifts_tree.get_children())
            for self.user_shift in User(registration_number=self.user[9]).get_all_users(table="algorithm"):
                self.shifts_tree.insert("", "end", values=(self.user_shift[1], self.user_shift[2], self.user_shift[3], self.user_shift[4]))

        self.shifts_tree = Treeview(self.data_frame, columns=("Sicil Numarası", "Tarih", "Saat", "Yer"), show="headings", selectmode="browse")
        self.shifts_tree.heading("#1", text="Sicil Numarası")
        self.shifts_tree.heading("#2", text="Tarih")
        self.shifts_tree.heading("#3", text="Saat")
        self.shifts_tree.heading("#4", text="Yer")
        self.shifts_tree.column("#1", width=110)
        self.shifts_tree.column("#2", width=120)
        self.shifts_tree.column("#3", width=120)
        self.shifts_tree.column("#4", width=120)
        self.shifts_tree.grid(column=0, row=0, columnspan=3, padx=10, pady=5)
        insert_shift_tree()

        def export_pdf():
            self.export_top = Toplevel()
            self.export_top.geometry("330x200")
            self.export_top.resizable(0,0)
            self.export_top.iconbitmap("icon.ico")
            self.export_top.title("Toplu Vardiya Silme")
            self.export_top.grab_set()
            center_window(self.export_top)

            self.start_date_label = Label(self.export_top, text="Başlangıç Tarihi:")
            self.start_date_label.grid(column=0, row=0, padx=10, pady=10)
            self.start_day_select = DateEntry(self.export_top)
            self.start_day_select.grid(column=1, row=0, padx=10, pady=10)

            self.end_date_label = Label(self.export_top, text="Bitiş Tarihi:")
            self.end_date_label.grid(column=0, row=1, padx=10, pady=10)
            self.end_day_select = DateEntry(self.export_top)
            self.end_day_select.grid(column=1, row=1, padx=10, pady=10)

            def checkbutton_check():
                if self.check_var.get():
                    self.start_day_select["state"] = "disabled"
                    self.end_day_select["state"] = "disabled"
                else: 
                    self.start_day_select["state"] = "normal"
                    self.end_day_select["state"] = "normal"

            self.check_var = BooleanVar()
            self.all_checkbutton = Checkbutton(self.export_top, text="Hepsini Çıkar", variable=self.check_var, command=checkbutton_check)
            self.all_checkbutton.grid(column=0, row=2, padx=10, pady=10)

            def export():
                if self.check_var.get():
                    if admin.create_pdf(username=login_username, type="all"):
                        ms.showinfo("Liste çıkartıldı!", "Liste başarıyla çıkartıldı.")
                        self.export_top.destroy()
                else:
                    if admin.create_pdf(username=login_username, type="time", start=self.start_day_select.get_date(), end=self.end_day_select.get_date()):
                        ms.showinfo("Liste çıkartıldı!", "Liste başarıyla çıkartıldı.")
                        self.export_top.destroy()

            self.export_button  = Button(self.export_top, text="Çıkart", command=export)
            self.export_button.grid(column=0, row=3, columnspan=2, padx=10, pady=10)

        self.print_button = Button(self.data_frame, text="Çıktı Al", command=export_pdf)
        self.print_button.grid(column=0, row=1, columnspan=3, padx=10, pady=5)