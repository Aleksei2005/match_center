from bs4 import BeautifulSoup
import requests
from tkinter import *
from tkinter import ttk
from tkinter import font
from threading import Thread
import sqlite3
from PIL import Image, ImageTk
import io
from playwright.sync_api import sync_playwright
import time

class Match_Center_App:
    def __init__(self):
        self.window = Tk()
        self.window.title("Матч-центр")
        self.window.geometry('600x825')
        self.window.resizable(False, False)
        self.db_name = 'logos.db'
        self.image_width, self.image_height = 200, 200
        self.array = []
        self.check = 0
        self.setup_ui()
        #self.load_and_display_logo()
        self.window.mainloop()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.TEntry", fieldbackground = "cornsilk2")
        style.configure("Custom.TButton", background = "cornsilk2", font = ('Calibri', 12), padding=(0, 0))

        """Настраивает элементы интерфейса"""
        bg_image = Image.open("ball.png").convert("RGBA")
        alpha = bg_image.split()[3]
        alpha = alpha.point(lambda p: p * 1.0)
        bg_image.putalpha(alpha)  # Применяем новый альфа-канал
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_image_1 = Image.open("ball2.png").convert("RGBA")
        alpha_1 = bg_image_1.split()[3]
        alpha_1 = alpha_1.point(lambda p: p * 1.0)
        bg_image_1.putalpha(alpha_1)  # Применяем новый альфа-канал
        bg_photo_1 = ImageTk.PhotoImage(bg_image_1)
        self.canvas = Canvas(self.window, width = 600, height = 150, background = 'cornsilk', bd = 0, highlightthickness = 0)
        self.canvas.pack()
        self.canvas_main = Canvas(self.window, width = 600, height = 550, background = 'cornsilk',  bd = 0, highlightthickness = 0)
        self.canvas_main.pack()
        self.canvas_bottom = Canvas(self.window, width = 600, height = 125, background = 'cornsilk',  bd = 0, highlightthickness = 0)
        self.canvas_bottom.pack()
        self.canvas.create_image(450, -50, image = bg_photo, anchor="nw")
        self.canvas_bottom.create_image(-100, 0, image = bg_photo_1, anchor="nw")
        self.canvas.create_text(49, 35, anchor = 'nw', text = 'Введите дату в формате ГГГГ-ММ-ЧЧ:', font = ('Calibri', 13))
        self.entry = ttk.Entry(width = 27, font = ('Arial', 13), style = "Custom.TEntry")
        self.entry.focus()
        self.canvas.image = bg_photo
        self.canvas_bottom.image = bg_photo_1
        self.button_enter = ttk.Button(text = 'Enter', command = self.new, style = "Custom.TButton")
        self.button_show_stat = ttk.Button(text = 'Показать статистику', command = self.show, state = DISABLED, style = "Custom.TButton")
        self.button_show_stat.place(x = 425, y = 71, height = 28)
        self.entry.place(x = 50, y = 71, height = 28)
        self.button_enter.place(x = 305, y = 71, height = 28, width = 60)

    def match_selection(self):
        self.select_window = Toplevel(self.window)
        self.select_window.title('Выбор матча')
        self.select_window.geometry('400x100')
        self.select_window.resizable(False, False)

    def show(self):
        self.match_selection()
        lbl_4 = ttk.Label(self.select_window, background = 'cornsilk')
        lbl_4.place(height = 100, width = 400)
        lbl_3 = ttk.Label(self.select_window, text = 'Выберите номер матча:', background = 'cornsilk', font = ('Calibri', 13))
        lbl_3.place(x = 50, y = 30)
        self.entry_1 = ttk.Entry(self.select_window, width = 30, font = ('Arial', 13), style = "Custom.TEntry")
        self.entry_1.focus()
        self.entry_1.place(x = 240, y = 29, height = 28, width = 40)
        button_2 = ttk.Button(self.select_window, text = 'Enter', command = self.get_stat, style = "Custom.TButton")
        button_2.place(x = 290, y = 29, height = 28, width = 60)

    def new(self):
        for data in self.array:
                self.canvas_main.delete(data)
        self.array = []
        self.button_enter.configure(state = DISABLED)
        self.button_show_stat.configure(state = DISABLED)
        self.del_text = self.canvas_main.create_text(220, 200, anchor = 'nw', text = 'Пожалуйста, подождите...', font = ('Arial', 11))
        t1 = Thread(target = self.get_matches, daemon = True)
        t1.start()

    def get_matches(self):
        while True:
            url = self.entry.get()
            url_1 = 'https://www.sports.ru/football/match/'
            url_2 = url_1 + url + '/'
            page = requests.get(url_2)
            self.soup_1 = BeautifulSoup(page.text, "lxml")
            self.score = []
            self.titles = self.soup_1.find_all(class_= ['light-gray-title corners-3px', 'light-gray-title drawn-title corners-3px'])
            self.left_score = self.soup_1.find_all('span', class_='s-left')
            self.right_score = self.soup_1.find_all('span', class_='s-right')
            self.status = self.soup_1.find_all('td', class_='alLeft gray-text')
            self.teams = self.soup_1.find_all(class_= ['light-gray-title corners-3px', 'light-gray-title drawn-title corners-3px', 'rel'])
            self.a = self.soup_1.find_all(class_= 'rel')
            self.links = self.soup_1.find_all('a', class_='score')

            for i in range(len(self.titles)):
                self.titles[i] = (self.titles[i].text).replace('\n', '')
                if '(' in self.titles[i]:
                    q = self.titles[i].index('(')
                    self.titles[i] = self.titles[i][:q - 1]

            for i in range(len(self.left_score)):
                self.score.append(self.left_score[i])
                self.score.append(self.right_score[i])

            url_2 = 'https://www.sports.ru/football/tournament/bundesliga/table/'
            page_2 = requests.get(url_2)
            soup_2 = BeautifulSoup(page_2.text, "lxml")

            teams_bundesliga = soup_2.find_all('a', class_='name')
            for i in range(len(teams_bundesliga)):
                teams_bundesliga[i] = teams_bundesliga[i].text
                if teams_bundesliga[i] == 'Унион Берлин':
                    teams_bundesliga[i] = 'Унион'
            del soup_2
            url_3 = 'https://www.sports.ru/football/tournament/premier-league/table/'
            page_3 = requests.get(url_3)
            soup_3 = BeautifulSoup(page_3.text, "lxml")

            teams_premier_league = soup_3.find_all('a', class_='name')
            for i in range(len(teams_premier_league)):
                teams_premier_league[i] = teams_premier_league[i].text
            del soup_3

            url_4 = 'https://www.sports.ru/football/tournament/la-liga/table/'
            page_4 = requests.get(url_4)
            soup_4 = BeautifulSoup(page_4.text, "lxml")

            teams_la_liga = soup_4.find_all('a', class_='name')
            for i in range(len(teams_la_liga)):
                teams_la_liga[i] = teams_la_liga[i].text
            del soup_4

            url_5 = 'https://www.sports.ru/football/tournament/ligue-1/table/'
            page_5 = requests.get(url_5)
            soup_5 = BeautifulSoup(page_5.text, "lxml")

            teams_liga_1 = soup_5.find_all('a', class_='name')
            for i in range(len(teams_liga_1)):
                teams_liga_1[i] = teams_liga_1[i].text
            del soup_5

            url_6 = 'https://www.sports.ru/football/tournament/seria-a/table/'
            page_6 = requests.get(url_6)
            soup_6 = BeautifulSoup(page_6.text, "lxml")

            teams_seria_a = soup_6.find_all('a', class_='name')
            for i in range(len(teams_seria_a)):
                teams_seria_a[i] = teams_seria_a[i].text
            del soup_6

            url_7 = 'https://www.sports.ru/football/tournament/rfpl/table/'
            page_7 = requests.get(url_7)
            soup_7 = BeautifulSoup(page_7.text, "lxml")

            teams_RPL = soup_7.find_all('a', class_='name')
            for i in range(len(teams_RPL)):
                teams_RPL[i] = teams_RPL[i].text
            del soup_7

            url_8 = 'https://news.sportbox.ru/Vidy_sporta/Futbol/stats/reiting_259'
            page_8 = requests.get(url_8)
            soup_8 = BeautifulSoup(page_8.text, "lxml")
            new_teams_fifa = []
            teams_fifa = soup_8.find_all('td', class_='table-link')
            for i in range(len(teams_fifa)):
                teams_fifa[i] = teams_fifa[i].text
                teams_fifa[i] = teams_fifa[i][15:-8]
                if i < 78:
                    new_teams_fifa.append(teams_fifa[i])
            del soup_8

            self.top_tournaments = teams_bundesliga + teams_premier_league + teams_la_liga + teams_liga_1 + teams_seria_a + teams_RPL + new_teams_fifa
            for i in range(len(self.teams)):
                self.teams[i] = (self.teams[i].text).replace('\n', '')
                if '(' in self.teams[i]:
                    q = self.teams[i].index('(')
                    self.teams[i] = self.teams[i][:q - 1]

            for data in self.teams:
                if data == 'Эвертон' and self.teams.index(data) > 100 or data == 'Матч дня':
                    del self.teams[self.teams.index(data)]
                if data == 'Катар' and self.teams.index(data) > 150:
                    del self.teams[self.teams.index(data)]
            for i in range(len(self.a)):
                self.a[i] = (self.a[i].text).replace('\n', '')

            for data in self.a:
                if data == 'Эвертон' and self.a.index(data) > 100:
                    del self.a[self.a.index(data)]
                if data == 'Катар' and self.a.index(data) > 150:
                    del self.a[self.a.index(data)]
            self.b = []

            for data in self.titles:
                if data == 'Матч дня':
                    del self.titles[0]
            teams_1 = []
            for i in range(len(self.teams) - 1):
                if self.teams[i] in self.titles:
                    teams_1.append(self.teams[i])
                else:
                    if (self.a.index(self.teams[i])) % 2 == 0 and (self.teams[i] in self.top_tournaments or self.teams[i + 1] in self.top_tournaments):
                        teams_1.append(self.teams[i])
                    if (self.a.index(self.teams[i])) % 2 != 0 and (self.teams[i] in self.top_tournaments or self.teams[i - 1] in self.top_tournaments):
                        teams_1.append(self.teams[i])
            if self.teams[-1] in self.top_tournaments or self.teams[-2] in self.top_tournaments:
                teams_1.append(self.teams[-1])
            self.new_teams = []
            for i in range(len(teams_1) - 1):
                if (teams_1[i] in self.titles and teams_1[i + 1] in self.titles) == 0:
                    self.new_teams.append(teams_1[i])
            if teams_1[-1] not in self.titles:
                self.new_teams.append(teams_1[-1])
            for i in range(len(self.new_teams)):
                if self.new_teams[i] in self.titles:
                    self.b.append(i)

            self.window.after(0, self.update_matches)
            time.sleep(60)

    def update_matches(self):
        self.canvas_main.delete(self.del_text)
        if self.check == 0:
            self.button_enter.configure(state = NORMAL)
            self.button_show_stat.configure(state = NORMAL)
        for data in self.array:
                self.canvas_main.delete(data)
        self.array = []
        ll = 0
        font1 = font.Font(family = "Calibri", size = 16, slant = font.ITALIC)
        font2 = font.Font(family = "Calibri", size = 13, slant = font.ITALIC)
        ar = self.canvas_main.create_text(50, ll, text = self.new_teams[0], anchor = 'nw', font = font1, fill = 'blue4')
        self.array.append(ar)
        l = 0
        s = 0
        k = 0
        numbers = 0
        n = []
        for j in range(0, len(self.a) - 1, 2):
            e = 0
            for x in range(1, j, 2):
                if self.status[x].text == 'Не начался' or self.status[x].text == 'Перенесен' or self.status[x].text == 'Отменен':
                    e = e + 1
                if self.status[x].text == 'Отменен' and self.score[x - 2*e].text in '0123456789':
                    e = e - 1
            if (l < len(self.b) - 1) and (self.b[l + 1] - self.b[l] - 1)/2 == k:
                l = l + 1
                ll +=35
                ar = self.canvas_main.create_text(50, ll, text = self.new_teams[self.b[l]], anchor = 'nw', font = font1, fill = 'blue4')
                self.array.append(ar)

                k = 0
            if self.a[j] in self.top_tournaments or self.a[j + 1] in self.top_tournaments:
                ll+=23
                n.append(int(j / 2))
                k = k + 1
                numbers = numbers + 1
                if self.status[j + 1].text == 'Не начался':
                    ar = self.canvas_main.create_text(50, ll, text = str(numbers) + ') ' + self.status[j].text + ' ' + self.status[j + 1].text + ' ' + self.a[j] + ' _ : _ ' + ' ' + self.a[j + 1], anchor = 'nw', font = font2, fill = 'dark slate gray')
                    self.array.append(ar)

                elif self.status[j + 1].text == 'Перенесен' or self.status[j + 1].text == 'Отменен':
                    ar = self.canvas_main.create_text(50, ll, text = str(numbers) + ') ' + self.status[j].text + ' ' + self.status[j + 1].text + ' ' + self.a[j] + ' _ : _ ' + ' ' + self.a[j + 1], anchor = 'nw', font = font2, fill = 'red')
                    self.array.append(ar)
                elif self.status[j + 1].text == 'Приостановлен':
                    s = 2*e
                    ar = self.canvas_main.create_text(50, ll, text = str(numbers) + ') ' + self.status[j].text + ' ' + self.status[j + 1].text + ' ' + self.a[j] + ' ' + self.score[j - s].text + ' : ' + self.score[j + 1 - s].text + ' ' + self.a[j + 1], anchor = 'nw', font = font2, fill = 'red')
                    self.array.append(ar)
                else:
                    s = 2*e
                    if self.status[j + 1].text == 'Завершен':
                        ar = self.canvas_main.create_text(50, ll, text = str(numbers) + ') ' + self.status[j].text + ' ' + self.status[j + 1].text + ' ' + self.a[j] + ' ' + self.score[j - s].text + ' : ' + self.score[j + 1 - s].text + ' ' + self.a[j + 1], anchor = 'nw', font = font2, fill = 'black')
                        self.array.append(ar)
                    else:
                        ar = self.canvas_main.create_text(50, ll, text = str(numbers) + ') ' + self.status[j].text + ' ' + self.status[j + 1].text + ' ' + self.a[j] + ' ' + self.score[j - s].text + ' : ' + self.score[j + 1 - s].text + ' ' + self.a[j + 1], anchor = 'nw', font = font2, fill = 'green4')
                        self.array.append(ar)

        self.summary_links = []

        for i in range(len(self.links)):
            self.links[i] = self.links[i].get('href')
            if i in n:
                self.summary_links.append(self.links[i])

        self.canvas_main.update()  # Обновляем Canvas для корректного расчета bbox
        bbox = self.canvas_main.bbox("all")  # Получаем (x1, y1, x2, y2) всех элементов
        self.canvas_main.configure(scrollregion = bbox)
        self.canvas_main.bind("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        current_pos = self.canvas_main.yview()
        if event.delta < 0 and current_pos[1] >= 0.999:
            return
        # Если пытаемся скроллить вверх, но уже вверху — блокируем
        elif event.delta > 0 and current_pos[0] <= 0.001:
            return
        self.canvas_main.yview_scroll(-1 * (event.delta // 120), "units")

    def get_stat(self):
        self.only_teams = []
        for data in self.new_teams:
            if data not in self.titles:
                self.only_teams.append(data)
        self.num = int(self.entry_1.get())
        self.select_window.destroy()
        self.wnd_2 = Toplevel(self.window)
        title_2 = self.only_teams[2*self.num - 2] + ' - ' + self.only_teams[2*self.num - 1]
        self.wnd_2.title(title_2)
        self.wnd_2.geometry('600x825')
        self.wnd_2.resizable(False, False)
        lbl_5 = ttk.Label(self.wnd_2, background = 'cornsilk')
        lbl_5.place(height = 800, width = 600)
        self.text_time = Text(self.wnd_2, state = DISABLED, borderwidth = 0, background = 'cornsilk')
        self.text_time.place(y = 90, x = 185, height = 165, width = 230)
        self.text_time.config(state = NORMAL)

        self.text_time.tag_add("timer_download", END)
        self.text_time.tag_configure("timer_download", justify = CENTER, font = ('Calibri Italic', 12), foreground = 'black')

        self.text_time.insert(END, "Загрузка данных...", 'timer_download')
        self.text_time.config(state = DISABLED)
        self.f()

        self.url_3 = ''
        if 'https://www.sports.ru' not in self.summary_links[self.num - 1]:
            self.url_3 = 'https://www.sports.ru' + self.summary_links[self.num - 1]
        else:
            self.url_3 = self.summary_links[self.num - 1]

        self.status_button()
        self.func_1()

    def func_1(self):
        if self.wnd_2.winfo_exists():
            page = requests.get(self.url_3)
            soup_9 = BeautifulSoup(page.text, "lxml")
            self.tournament_info = soup_9.find_all(class_=['top__tournament-name', 'top__tournament-round'])
            for i in range(len(self.tournament_info)):
                self.tournament_info[i] = self.tournament_info[i].text
            self.tournament_info = "\n ".join(self.tournament_info)
            goal_scorer = soup_9.find_all(class_='match-summary__score-info')
            for i in range(len(goal_scorer)):
                goal_scorer[i] = goal_scorer[i].text
            for i in range(len(goal_scorer)):
                if 'автогол' in goal_scorer[i]:
                    ind = goal_scorer[i].index('автогол')
                    goal_scorer[i] = goal_scorer[i][:ind] + ' (а)'
                if 'пенальти' in goal_scorer[i]:
                    ind = goal_scorer[i].index('пенальти')
                    goal_scorer[i] = goal_scorer[i][:ind] + '(п)'
            lbl_score = ttk.Label(self.wnd_2, background = 'cornsilk', font = ('Calibri ITALIC', 55))
            score = soup_9.find_all('span', class_='matchboard__card-game')
            text_op_1 = Text(self.wnd_2, state = DISABLED, borderwidth = 0, background = 'cornsilk')
            text_op_2 = Text(self.wnd_2, state = DISABLED, borderwidth = 0, background = 'cornsilk')

            text_goal_scorer_left = Text(self.wnd_2, state = DISABLED, borderwidth = 0, background = 'cornsilk')
            text_goal_scorer_right = Text(self.wnd_2, state = DISABLED, borderwidth = 0, background = 'cornsilk')

            font_score = font.Font(self.wnd_2, family = "Calibri", size = 11, slant = font.ITALIC)
            text_goal_scorer_left.tag_add("left", END)
            text_goal_scorer_left.tag_configure("left", justify = LEFT, font = font_score, foreground = 'black')
            text_goal_scorer_right.tag_add("right", END)
            text_goal_scorer_right.tag_configure("right", justify = RIGHT, font = font_score, foreground = 'black')
            counter = 0
            v = 0
            if len(score) != 0:
                for data in '0123456789':
                    if score[0].text == data:
                        v = v + 1
                if v != 0:
                    text_goal_scorer_left.config(state = NORMAL)
                    text_goal_scorer_right.config(state = NORMAL)
                    for i in range(int(len(goal_scorer)/2)):
                        if int(score[0].text) > counter:
                            if int(score[0].text) - counter == 1:
                                text_goal_scorer_left.insert(END, goal_scorer[i], 'left')
                            else:
                                text_goal_scorer_left.insert(END, goal_scorer[i] + '\n', 'left')
                            counter += 1
                        else:
                            if i == int(len(goal_scorer)/2) - 1:
                                text_goal_scorer_right.insert(END, goal_scorer[i], 'right')
                            else:
                                text_goal_scorer_right.insert(END, goal_scorer[i] + '\n', 'right')
            text_goal_scorer_right.delete(END)
            text_goal_scorer_left.config(state = DISABLED)
            text_goal_scorer_right.config(state = DISABLED)

            self.opponents = []
            self.opponents.append(self.only_teams[2*self.num - 2])
            self.opponents.append(self.only_teams[2*self.num - 1])
            xG = soup_9.find_all('span', class_='xg-display__value')
            x = 62 * ' '

            name_stats = soup_9.find_all('span', class_= "statistics-info-bar__title")
            stats = soup_9.find_all('span', class_= 'statistics-info-bar__stat')
            k = 0
            del soup_9

            text_stats = Text(self.wnd_2, state = DISABLED, borderwidth = 0, background = 'cornsilk')
            text_stats.config(state = NORMAL)
            font3 = font.Font(self.wnd_2, family = "Calibri", size = 13, slant = font.ITALIC)
            text_stats.tag_add("stats", END)
            text_stats.tag_configure("stats", justify = CENTER, font = font3, foreground = 'black')

            if len(xG) != 0:
                xG_full = xG[0].text + x + 'xG' + x + xG[1].text
                text_stats.insert(END, xG_full + '\n\n', 'stats')
            else:
                xG_full = '-' + x + 'xG' + x + '-'
                text_stats.insert(END, xG_full + '\n\n', 'stats')
            for i in range(len(name_stats)):
                x = int((134 - len(name_stats[i].text) - len(stats[i + k].text) - len(stats[i + 1 + k].text)) / 2) - int(0.5*len(name_stats[i].text)) + 1
                if name_stats[i].text == 'Владение мячом':
                    x = x - 3
                if name_stats[i].text == 'Штрафные удары':
                    x = x - 2
                text_stats.insert(END, stats[i + k].text + x * ' ' + name_stats[i].text + x * ' ' + stats[i + 1 + k].text + '\n\n', 'stats')
                k = k + 1
            h = 0
            if len(score) != 0:
                for data in '0123456789':
                    if score[0].text == data:
                        h = h + 1
                if h != 0:
                    full_score = score[0].text + ' : ' + score[1].text
                else:
                    full_score = ' - : -'
            else:
                full_score = ' - : -'

            left_1 = ttk.Label(self.wnd_2, background = 'IndianRed1', font = ('Calibri', 2))
            left_2 = ttk.Label(self.wnd_2, background = 'IndianRed1', font = ('Calibri', 2))
            left_3 = ttk.Label(self.wnd_2, background = 'IndianRed1', font = ('Calibri', 2))
            left_4 = ttk.Label(self.wnd_2, background = 'IndianRed1', font = ('Calibri', 2))
            left_5 = ttk.Label(self.wnd_2, background = 'IndianRed1', font = ('Calibri', 2))
            left_6 = ttk.Label(self.wnd_2, background = 'IndianRed1', font = ('Calibri', 2))
            left_7 = ttk.Label(self.wnd_2, background = 'IndianRed1', font = ('Calibri', 2))
            left_8 = ttk.Label(self.wnd_2, background = 'IndianRed1', font = ('Calibri', 2))
            left_9 = ttk.Label(self.wnd_2, background = 'IndianRed1', font = ('Calibri', 2))
            left_10 = ttk.Label(self.wnd_2, background = 'IndianRed1', font = ('Calibri', 2))
            left_11 = ttk.Label(self.wnd_2, background = 'IndianRed1', font = ('Calibri', 2))

            right_1 = ttk.Label(self.wnd_2, background = 'purple1', font = ('Calibri', 2))
            right_2 = ttk.Label(self.wnd_2, background = 'purple1', font = ('Calibri', 2))
            right_3 = ttk.Label(self.wnd_2, background = 'purple1', font = ('Calibri', 2))
            right_4 = ttk.Label(self.wnd_2, background = 'purple1', font = ('Calibri', 2))
            right_5 = ttk.Label(self.wnd_2, background = 'purple1', font = ('Calibri', 2))
            right_6 = ttk.Label(self.wnd_2, background = 'purple1', font = ('Calibri', 2))
            right_7 = ttk.Label(self.wnd_2, background = 'purple1', font = ('Calibri', 2))
            right_8 = ttk.Label(self.wnd_2, background = 'purple1', font = ('Calibri', 2))
            right_9 = ttk.Label(self.wnd_2, background = 'purple1', font = ('Calibri', 2))
            right_10 = ttk.Label(self.wnd_2, background = 'purple1', font = ('Calibri', 2))
            right_11 = ttk.Label(self.wnd_2, background = 'purple1', font = ('Calibri', 2))

            text_stats.config(state = DISABLED)
            font4 = font.Font(self.wnd_2, family = "Calibri", size = 17, slant = font.ITALIC, weight = font.BOLD)
            lbl_score.configure(text = full_score)

            lbl_6 = ttk.Label(self.wnd_2, text = 'Статистика матча', background = 'cornsilk', font = font4)
            lbl_score.place(x = 235, y = 0, width = 190, height = 80)
            text_op_1.place(x = 10, y = 107, width = 200, height = 25)
            text_op_2.place(x = 395, y = 107, width = 195, height = 25)
            text_op_1.config(state = NORMAL)
            text_op_2.config(state = NORMAL)
            font5 = font.Font(self.wnd_2, family = "Calibri", size = 13, slant = font.ITALIC, weight = font.BOLD)
            text_op_1.insert(END, self.opponents[0].upper(), 'opponent')
            text_op_2.insert(END, self.opponents[1].upper(), 'opponent')
            text_op_1.tag_add("opponent", END)
            text_op_2.tag_add("opponent", END)
            text_op_1.tag_configure("opponent", justify = LEFT, font = font5, foreground = 'black')
            text_op_2.tag_configure("opponent", justify = RIGHT, font = font5, foreground = 'black')
            text_op_1.config(state = DISABLED)
            text_op_2.config(state = DISABLED)
            lbl_6.place(y = 315, x = 190)
            text_goal_scorer_left.place(y = 130, x = 10, width = 170, height = 225)
            text_goal_scorer_right.place(y = 130, x = 420, width = 170, height = 225)
            text_stats.place(height = 485, width = 588, y = 350, x = 5)

            self.get_image()

            length = []
            for i in range(0, len(stats), 2):
                if '%' in stats[i].text:
                    stats[i] = (stats[i].text)[:-1]
                    stats[i + 1] = (stats[i + 1].text)[:-1]
                    if int(stats[i]) + int(stats[i + 1]) != 0:
                        s = int(588 * int(stats[i]) / (int(stats[i]) + int(stats[i + 1])))
                        length.append(s)
                    else:
                        s = 294
                        length.append(s)
                else:
                    if int(stats[i].text) + int(stats[i + 1].text) != 0:
                        s = int(588 * int(stats[i].text) / (int(stats[i].text) + int(stats[i + 1].text)))
                        length.append(s)
                    else:
                        s = 294
                        length.append(s)
            if len(xG) != 0:
                if '.' in xG[0].text and float(xG[0].text) + float(xG[1].text) != 0:
                    length_xG = int(588 * float(xG[0].text) / (float(xG[0].text) + float(xG[1].text)))
                else:
                    length_xG = 294
            else:
                length_xG = 294

            left_1.place(y = 375, x = 5, width = length_xG)
            left_2.place(y = 417, x = 5, width = length[0])
            left_3.place(y = 459, x = 5, width = length[1])
            left_4.place(y = 501, x = 5, width = length[2])
            left_5.place(y = 543, x = 5, width = length[3])
            left_6.place(y = 585, x = 5, width = length[4])
            left_7.place(y = 627, x = 5, width = length[5])
            left_8.place(y = 669, x = 5, width = length[6])
            left_9.place(y = 711, x = 5, width = length[7])
            left_10.place(y = 753, x = 5, width = length[8])
            left_11.place(y = 795, x = 5, width = length[9])

            right_1.place(y = 375, x = 5 + length_xG, width = 588 - length_xG)
            right_2.place(y = 417, x = 5 + length[0], width = 588 - length[0])
            right_3.place(y = 459, x = 5 + length[1], width = 588 - length[1])
            right_4.place(y = 501, x = 5 + length[2], width = 588 - length[2])
            right_5.place(y = 543, x = 5 + length[3], width = 588 - length[3])
            right_6.place(y = 585, x = 5 + length[4], width = 588 - length[4])
            right_7.place(y = 627, x = 5 + length[5], width = 588 - length[5])
            right_8.place(y = 669, x = 5 + length[6], width = 588 - length[6])
            right_9.place(y = 711, x = 5 + length[7], width = 588 - length[7])
            right_10.place(y = 753, x = 5 + length[8], width = 588 - length[8])
            right_11.place(y = 795, x = 5 + length[9], width = 588 - length[9])

            self.window.after(60000, self.func_1)

    def status_button(self):
        if self.wnd_2.winfo_exists():
            self.check = 1
            self.button_show_stat.configure(state = DISABLED)
            self.button_enter.configure(state = DISABLED)
        else:
            self.check = 0
            self.button_show_stat.configure(state = NORMAL)
            self.button_enter.configure(state = NORMAL)
            return
        self.window.after(500, self.status_button)

    def f(self):
        t = Thread(target = self.get_text_threading, daemon = True)
        t.start()

    def get_image(self):
        # подключаемся к базе данных
        conn = sqlite3.connect('logos.db')
        cur = conn.cursor()
        cur.execute("SELECT Logos FROM Logos WHERE Name_logo =?", (self.opponents[0], ))
        result_1 = cur.fetchone()
        cur.execute("SELECT Logos FROM Logos WHERE Name_logo =?", (self.opponents[1], ))
        result_2 = cur.fetchone()
        if result_1:
            blob_data_1 = result_1[0]
        else:
            blob_data_1 = None
        if blob_data_1:
            image_1 = Image.open(io.BytesIO(blob_data_1))
            image_1.thumbnail((1000, 80))
            photo_1 = ImageTk.PhotoImage(image_1)
            logo_label_1 = ttk.Label(self.wnd_2, image = photo_1, background = 'cornsilk')
            logo_label_1.place(x = 10, y = 5)
            logo_label_1.image = photo_1
        if result_2:
            blob_data_2 = result_2[0]
        else:
            blob_data_2 = None
        if blob_data_2:
            image_2 = Image.open(io.BytesIO(blob_data_2))
            image_2.thumbnail((1000, 80))
            photo_2 = ImageTk.PhotoImage(image_2)
            logo_label_2 = ttk.Label(self.wnd_2, image = photo_2, background = 'cornsilk')
            logo_label_2.place(x = 585 - photo_2.width(), y = 5)
            logo_label_2.image = photo_2
        cur.close()
        conn.commit()
        conn.close()

    def get_text_threading(self):
        while self.wnd_2.winfo_exists():
            with sync_playwright() as p:
                browser = p.chromium.launch(headless = True)
                page = browser.new_page()
                page.goto(self.url_3, timeout = 60000)
                page.wait_for_selector("div.match-summary__state-info", timeout = 60000)
                text_content = page.inner_text('div.match-summary__state-info')
                self.window.after(0, self.update_text, text_content)

            time.sleep(60)

    def update_text(self, text):
        if self.wnd_2.winfo_exists():
            font6 = font.Font(self.wnd_2, family = "Calibri", size = 14, slant = font.ITALIC, weight = font.BOLD)
            font7 = font.Font(self.wnd_2, family = "Calibri", size = 13, slant = font.ITALIC, weight = font.BOLD)
            self.text_time.config(state = NORMAL)
            self.text_time.lift()
            self.text_time.delete("1.0", END)
            self.text_time.tag_add("info_tournament", END)
            self.text_time.tag_configure("info_tournament", justify = CENTER, font = font7, foreground = 'black')
            self.text_time.tag_add("timer", END)
            self.text_time.tag_configure("timer", justify = CENTER, font = font6, foreground = 'black')
            self.text_time.insert(END, self.tournament_info + '\n\n', 'info_tournament')
            self.text_time.insert(END, text, 'timer')
            self.text_time.config(state = DISABLED)

if __name__ == "__main__":
    Match_Center_App()

