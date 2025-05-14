from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser
import requests
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from threading import Thread
import sqlite3
from PIL import Image, ImageTk
import io
from playwright.sync_api import sync_playwright
import time
import logging
from datetime import datetime, timedelta
from babel.dates import format_date
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
import traceback
import sys
import random

logging.basicConfig(
    filename = 'Match_Center_App.log',
    filemode = 'w',
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S'
)


class Match_Center_App:
    def __init__(self):
        self.window = Tk()
        self.window.title("Матч-центр")
        self.window.geometry('600x825')
        self.window.resizable(False, False)
        self.image_width, self.image_height = 200, 200
        self.array = []
        self.del_text_title = None
        self.check = 0
        self.scheduled_update_id = None
        self.scheduled_update_id_stat = None
        self.scheduled_update_id_dyn = None
        self.url = None
        self.wnd_3 = None
        self.gr_1 = None
        self.gr_2 = None
        self.title_gr_1 = None
        self.title_gr_2 = None
        self.background_text = None
        self.check_auto = 0
        self.setup_ui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def on_closing(self):
        plt.close('all')  # Закрыть все графики
        self.window.destroy()
        sys.exit(0)

    def setup_ui(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Custom.TEntry", fieldbackground = "cornsilk2")
        self.style.configure("Primary.TButton", background = "cornsilk2", font = ('Calibri', 12), padding = (0, 0))
        self.style.configure("Secondary.TButton", background = "cornsilk2", font = ('Calibri', 10), padding = (0, 0))
        """Настраивает элементы интерфейса"""
        bg_image = Image.open("ball.png")
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_image_1 = Image.open("ball2.png")
        bg_photo_1 = ImageTk.PhotoImage(bg_image_1)
        self.canvas = Canvas(self.window, width = 600, height = 200, background = 'cornsilk', bd = 0, highlightthickness = 0)
        self.canvas.pack()
        self.canvas_main = Canvas(self.window, width = 600, height = 500, background = 'cornsilk',  bd = 0, highlightthickness = 0)
        self.canvas_main.pack()
        self.canvas_bottom = Canvas(self.window, width = 600, height = 125, background = 'cornsilk',  bd = 0, highlightthickness = 0)
        self.canvas_bottom.pack()
        self.canvas.create_image(450, -50, image = bg_photo, anchor = "nw")
        self.canvas_bottom.create_image(-100, 0, image = bg_photo_1, anchor = "nw")
        self.canvas.create_text(49, 35, anchor = 'nw', text = 'Введите дату в формате ГГГГ-ММ-ЧЧ:', font = ('Calibri', 13))
        self.entry = ttk.Entry(width = 27, font = ('Arial', 13), style = "Custom.TEntry")
        self.entry.focus()
        self.canvas.image = bg_photo
        self.canvas_bottom.image = bg_photo_1

        self.button_enter = ttk.Button(text = 'Enter', command = self.new, style = "Primary.TButton")
        self.button_show_stat = ttk.Button(text = 'Показать статистику', command = self.show, state = DISABLED, style = "Primary.TButton")

        self.button_today = ttk.Button(text = 'Сегодня', command = self.today, style = "Secondary.TButton")
        self.button_tomorrow = ttk.Button(text = 'Завтра', command = self.tomorrow, style = "Secondary.TButton")
        self.button_yesterday = ttk.Button(text = 'Вчера', command = self.yesterday, style = "Secondary.TButton")
        self.button_show_stat.place(x = 425, y = 71, height = 28)
        self.entry.place(x = 50, y = 71, height = 28)
        self.button_enter.place(x = 305, y = 71, height = 28, width = 60)
        self.button_yesterday.place(x = 50, y = 105, width = 55)
        self.button_today.place(x = 115, y = 105, width = 55)
        self.button_tomorrow.place(x = 180, y = 105, width = 55)

    def today(self):
        self.check_auto = 1
        self.url = datetime.now().strftime('%Y-%m-%d')
        self.new()

    def tomorrow(self):
        self.check_auto = 1
        yesterday = datetime.now() + timedelta(days = 1)
        self.url = yesterday.strftime("%Y-%m-%d")
        self.new()

    def yesterday(self):
        self.check_auto = 1
        yesterday = datetime.now() - timedelta(days = 1)
        self.url = yesterday.strftime("%Y-%m-%d")
        self.new()

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
        button_2 = ttk.Button(self.select_window, text = 'Enter', command = self.get_stat, style = "Primary.TButton")
        button_2.place(x = 290, y = 29, height = 28, width = 60)

    def new(self, is_scheduled = False):
        self.check_arg = is_scheduled
        self.cancel_scheduled_update_list()
        if not is_scheduled:
            for data in self.array:
                self.canvas_main.delete(data)
            self.canvas.delete(self.del_text_title)
            self.array = []
            self.button_enter.configure(state = DISABLED)
            self.button_show_stat.configure(state = DISABLED)
            self.button_today.configure(state = DISABLED)
            self.button_yesterday.configure(state = DISABLED)
            self.button_tomorrow.configure(state = DISABLED)
            self.canvas_main.configure(scrollregion = (0, 0, 0, 0))
            self.del_text = self.canvas_main.create_text(220, 200, anchor = 'nw', text = 'Пожалуйста, подождите...', font = ('Arial', 11))
        t1 = Thread(target = self.get_matches, daemon = True)
        t1.start()

    def cancel_scheduled_update_list(self):
        if self.scheduled_update_id is not None:
            self.window.after_cancel(self.scheduled_update_id)
            self.scheduled_update_id = None

    def get_matches(self, attempt = 1, max_attempts = 3):
        self.cancel_scheduled_update_list()
        try:
            start = time.time()
            if self.check_auto == 0:
                if not self.check_arg:
                    self.url = self.entry.get()
                    try:
                        datetime.strptime(self.url, "%Y-%m-%d")
                    except ValueError:
                        logging.error("invalid date format")
                        messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте ГГГГ-ММ-ЧЧ")
                        self.canvas_main.delete(self.del_text)
                        self.button_enter.configure(state = NORMAL)
                        self.button_show_stat.configure(state = NORMAL)
                        self.entry.focus()  # возвращаем фокус в поле ввода
                        return
            else:
                if not self.check_arg:
                    self.check_auto = 0

            url_1 = 'https://www.sports.ru/football/match/'
            url_2 = url_1 + self.url + '/'
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
            logging.info("successful output of the list of matches")

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

            self.scheduled_update_id = self.window.after(0, self.update_matches)
            elapsed = time.time() - start
            delay = max(60 - elapsed, 0) * 1000
            self.scheduled_update_id = self.window.after(int(delay), lambda: self.new(is_scheduled = True))
        except Exception as e:
            if attempt < max_attempts:
                logging.warning(f"retrying parsing to get list of matches... attempt {attempt}/{max_attempts}")
                delay = (2 ** attempt) * 10
                self.scheduled_update_id = self.window.after(delay * 1000, lambda: self.get_matches(attempt + 1, max_attempts))
            else:
                error_line = traceback.extract_tb(e.__traceback__)[-1].lineno
                logging.error(f"error parsing to get list of matches, строка {error_line}: {e}")
                messagebox.showerror("Ошибка", "Не удалось получить список матчей")
                self.canvas_main.delete(self.del_text)
                self.button_enter.configure(state = NORMAL)
                self.button_show_stat.configure(state = NORMAL)
                self.entry.focus()
                for data in self.array:
                    self.canvas_main.delete(data)
                self.array = []
                return

    def update_matches(self):
        self.canvas_main.delete(self.del_text)
        if self.check == 0:
            self.button_enter.configure(state = NORMAL)
            self.button_show_stat.configure(state = NORMAL)
            self.button_today.configure(state = NORMAL)
            self.button_yesterday.configure(state = NORMAL)
            self.button_tomorrow.configure(state = NORMAL)
        for data in self.array:
            self.canvas_main.delete(data)
        self.canvas.delete(self.del_text_title)
        self.array = []
        ll = 0
        font1 = font.Font(family = "Calibri", size = 16, slant = font.ITALIC)
        font2 = font.Font(family = "Calibri", size = 13, slant = font.ITALIC)
        url_new = datetime.strptime(self.url, "%Y-%m-%d")
        url_new = format_date(url_new, "d MMMM Y", locale = 'ru')
        self.del_text_title = self.canvas.create_text(50, 150, text = f"Матчи {url_new}", anchor = 'nw', font = ("Calibri Italic", 20), fill = 'black')
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
                ll += 23
                n.append(int(j / 2))
                k = k + 1
                numbers = numbers + 1
                if self.status[j + 1].text == 'Не начался':
                    ar = self.canvas_main.create_text(50, ll, text = str(numbers) + ') ' + self.status[j].text + ' ' + self.status[j + 1].text + ' ' + self.a[j] + '  - : -  ' + ' ' + self.a[j + 1], anchor = 'nw', font = font2, fill = 'dark slate gray')
                    self.array.append(ar)

                elif self.status[j + 1].text == 'Перенесен' or self.status[j + 1].text == 'Отменен':
                    ar = self.canvas_main.create_text(50, ll, text = str(numbers) + ') ' + self.status[j].text + ' ' + self.status[j + 1].text + ' ' + self.a[j] + '  - : -  ' + ' ' + self.a[j + 1], anchor = 'nw', font = font2, fill = 'red')
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

        self.canvas_main.update()
        bbox = self.canvas_main.bbox("all")
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

    def cancel_scheduled_update_stat(self):
        if self.scheduled_update_id_stat is not None:
            self.window.after_cancel(self.scheduled_update_id_stat)
            self.scheduled_update_id_stat = None

    def func_1(self, attempt = 1, max_attempts = 3):
        self.cancel_scheduled_update_stat()
        try:
            if self.wnd_2.winfo_exists():
                page = requests.get(self.url_3)
                self.soup_9 = BeautifulSoup(page.text, "lxml")
                self.tournament_info = self.soup_9.find_all(class_=['top__tournament-name', 'top__tournament-round'])
                for i in range(len(self.tournament_info)):
                    self.tournament_info[i] = self.tournament_info[i].text
                self.tournament_info = "\n ".join(self.tournament_info)
                goal_scorer = self.soup_9.find_all(class_='match-summary__score-info')
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
                score = self.soup_9.find_all('span', class_='matchboard__card-game')
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
                xG = self.soup_9.find_all('span', class_='xg-display__value')
                x = 62 * ' '

                name_stats = self.soup_9.find_all('span', class_= "statistics-info-bar__title")
                stats = self.soup_9.find_all('span', class_= 'statistics-info-bar__stat')
                self.links_last_five = self.soup_9.find_all('a', class_= 'last-five__result')
                for i in range(len(self.links_last_five)):
                    self.links_last_five[i] = self.links_last_five[i].get("href")
                k = 0

                text_stats = Text(self.wnd_2, state = DISABLED, borderwidth = 0, background = 'cornsilk')
                text_stats.config(state = NORMAL)
                font3 = font.Font(self.wnd_2, family = "Calibri", size = 13, slant = font.ITALIC)
                text_stats.tag_add("stats", END)
                text_stats.tag_configure("stats", justify = CENTER, font = font3, foreground = 'black')
                texts = [self.text_time, text_op_1, text_op_2, text_goal_scorer_left, text_goal_scorer_right, text_stats]
                # Отключаем возможность выделить текст
                for text in texts:
                    text.bind('<Button-1>', lambda e: 'break')
                    text.bind('<B1-Motion>', lambda e: 'break')
                    text.bind('<ButtonRelease-1>', lambda e: 'break')
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
                lbl_6.place(y = 315, x = 150)
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
                check_button_add = 0
                if check_button_add == 0:
                    if len(self.links_last_five) == 20:
                        self.button_add_stat = ttk.Button(self.wnd_2, command = self.get_last_five, text = "Доп. статистика", style = "Primary.TButton")
                    else:
                        self.button_add_stat = ttk.Button(self.wnd_2, command = self.get_last_five, text = "Доп. статистика", style = "Primary.TButton", state = DISABLED)
                    self.button_add_stat.place(x = 370, y = 320)
                    check_button_add = 1
                logging.info("successful output of match statistics")
                self.scheduled_update_id_stat = self.window.after(60000, self.func_1)

        except Exception as e:
            if attempt < max_attempts:
                logging.warning(f"retrying parsing to get statistics... attempt {attempt}/{max_attempts}")
                time.sleep(2 ** attempt)
                self.func_1(attempt + 1, max_attempts)
            else:
                logging.error(f"error parsing to get statistics: {e}")
                messagebox.showerror("Ошибка", "Не удалось получить статистику")
                return

    def get_last_five(self):
        self.button_add_stat.configure(state = DISABLED)
        self.last_five_links = []
        for i in range(10):
            if i < 5:
                self.last_five_links.append(self.links_last_five[4 - i])
            else:
                self.last_five_links.append(self.links_last_five[14 - i])
        self.wnd_3 = Toplevel(self.window)
        self.status_add_button()
        title = f'Доп. статистика матча {self.only_teams[2*self.num - 2]} - {self.only_teams[2*self.num - 1]}'
        self.wnd_3.title(title)
        self.wnd_3.geometry('500x800')
        self.wnd_3.resizable(False, False)
        label_full = ttk.Label(self.wnd_3, background = "cornsilk")
        label_full.place(width = 500, height = 800)
        self.text = Text(self.wnd_3, state = DISABLED, borderwidth = 0, background = 'cornsilk')
        # Отключаем возможность выделить текст
        self.text.bind('<Button-1>', lambda e: 'break')
        self.text.bind('<B1-Motion>', lambda e: 'break')
        self.text.bind('<ButtonRelease-1>', lambda e: 'break')
        self.font_title = font.Font(self.wnd_3, family = "Calibri", size = 17, slant = font.ITALIC, weight = font.BOLD)
        self.text.place(width = 500, height = 800, y = 50)
        self.lbl_wait = ttk.Label(self.wnd_3, text = 'Пожалуйста, подождите...', font = ('Arial', 11), background = 'cornsilk', foreground = 'black')
        self.lbl_wait.pack(pady = 300)
        self.font7 = font.Font(family = "Calibri", size = 16, slant = font.ITALIC)
        font8 = font.Font(family = "Calibri", size = 13, slant = font.ITALIC)
        self.text.tag_add("draw", END)
        self.text.tag_add("win", END)
        self.text.tag_add("lose", END)
        self.text.tag_add('noname', END)
        self.text.tag_add("title", END)
        self.text.tag_add('name', END)
        self.text.tag_add('add_1', END)
        self.text.tag_add('add_2', END)
        self.text.tag_configure("draw", justify = CENTER, font = self.font7, foreground = 'black')
        self.text.tag_configure("win", justify = CENTER, font = self.font7, foreground = 'forest green')
        self.text.tag_configure("lose", justify = CENTER, font = self.font7, foreground = 'red')
        self.text.tag_configure("noname", justify = CENTER, font = self.font7, foreground = 'dark slate gray')
        self.text.tag_configure("title", justify = CENTER, font = font8, foreground = 'black')
        self.text.tag_configure("name", justify = CENTER, font = self.font_title, foreground = 'blue4')
        self.text.tag_configure("add_1", font = ('Calibri', 7))
        self.text.tag_configure("add_2", font = ('Calibri', 4))
        self.loaded_matches = 0
        self.total_matches = len(self.last_five_links)
        self.match_data = {}
        for i, link in enumerate(self.last_five_links):
            Thread(target = self.process_match, args = (link, i), daemon = True).start()

    def process_match(self, link, match_index):
        try:
            # Загружаем данные матча
            data = self.fetch_match_data(link)
            data['index'] = match_index
            self.wnd_3.after(0, self.store_and_update, data)

        except Exception as e:
            error_line = traceback.extract_tb(e.__traceback__)[-1].lineno
            logging.error(f"Ошибка обработки матча, строка {error_line}: {e}")
            self.wnd_3.after(0, lambda: messagebox.showerror("Ошибка", str(e)))

    def store_and_update(self, data):
        # Сохраняем данные по индексу
        self.match_data[data['index']] = data
        self.loaded_matches += 1
        # Если все матчи загружены, обновляем интерфейс
        if self.loaded_matches == self.total_matches:
            self.update_interface()


    def get_random_headers(self):
        user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0']

        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1'
        }



    def fetch_match_data(self, link):
        try:
            conn = sqlite3.connect('logos.db')
            cur = conn.cursor()

            html_content = requests.get(f'https://www.sports.ru{link}', headers = self.get_random_headers(), timeout = 20).text
            tree = HTMLParser(html_content)
            soup = BeautifulSoup(html_content, 'lxml')

            teams = [t.text.replace("Унион Берлин", "Унион")
                    for t in soup.find_all('span', class_=['match-summary__team-name match-summary__team-name--home',
                                                        'match-summary__team-name match-summary__team-name--away'])]
            times = soup.find('time', class_='match-summary__state-time').text
            status = soup.find('span', class_='match-summary__state-status').text
            score = ' : '.join([s.text for s in soup.find_all('span', class_='matchboard__card-game')])
            xG_last_five = [t.text for t in soup.find_all('span', class_='xg-display__value')]

            for _ in range(10):
                html_content = requests.get(f'https://www.sports.ru{link}', headers = self.get_random_headers(), timeout = 10).text
                tree = HTMLParser(html_content)
                self.name_stats_last_five = [node.text() for node in tree.css('span.statistics-info-bar__title')]
                stats_last_five = [node.text() for node in tree.css('span.statistics-info-bar__stat')]
                if len(stats_last_five) == 20 and len(self.name_stats_last_five) == 10:
                    break

            logos = []
            for team in teams:
                cur.execute("SELECT Logos FROM Logos WHERE Name_logo=?", (team,))
                result = cur.fetchone()
                if result and result[0]:
                    img = Image.open(io.BytesIO(result[0]))
                    img.thumbnail((50, 30))
                    logos.append(ImageTk.PhotoImage(img))
                else:
                    logos.append(None)

            return {
                'logos': logos,
                'teams': teams,
                'time': times,
                'status': status,
                'score': score,
                'xG': xG_last_five,
                'stats': stats_last_five
            }
        finally:
            cur.close()
            conn.close()

    def update_interface(self):
        try:
            self.text.configure(state = NORMAL)
            number_of_matches = 0
            for i in range(self.total_matches):
                if i in self.match_data:
                    data = self.match_data[i]
                    # Вставляем текст
                    self.lbl_wait.destroy()

                    if number_of_matches == 0:
                        self.label_op_1 = ttk.Label(self.wnd_3, text = f"Форма команды {self.opponents[0].upper()}", font = self.font_title, background = 'cornsilk', foreground = 'blue4')
                        self.label_op_1.pack(pady = 10)

                    if number_of_matches < 5:
                        add = 0
                    else:
                        add = 24
                    if number_of_matches < 5 and data['teams'].index(self.opponents[0]) == 0 or number_of_matches >= 5 and data['teams'].index(self.opponents[1]) == 0:
                        if int(data['score'][0]) > int(data['score'][data['score'].index(':') + 1:]):
                            style = 'win'
                        elif int(data['score'][0]) < int(data['score'][data['score'].index(':') + 1:]):
                            self.text.tag_configure("info", foreground = 'red')
                            style = 'lose'
                        else:
                            style = 'draw'
                    if number_of_matches < 5 and data['teams'].index(self.opponents[0]) == 1 or number_of_matches >= 5 and data['teams'].index(self.opponents[1]) == 1:
                        if int(data['score'][0]) < int(data['score'][data['score'].index(':') + 1:]):
                            style = 'win'
                        elif int(data['score'][0]) > int(data['score'][data['score'].index(':') + 1:]):
                            style = 'lose'
                        else:
                            style = 'draw'

                    self.text.insert(END, f"{data['time']}, {data['status']}\n", 'title')
                    if number_of_matches != 4:
                        self.text.insert(END, f"{data['teams'][0]} {data['score']} {data['teams'][1]}\n\n", style)
                    else:
                        self.text.insert(END, f"{data['teams'][0]} {data['score']} {data['teams'][1]}\n", style)
                        self.text.insert(END,'\n', 'add_1')
                        self.text.insert(END, f"Форма команды {self.opponents[1].upper()}\n", 'name')
                        self.text.insert(END,'\n\n', 'add_2')

                    # Добавляем изображения
                    if data['logos'][0]:
                        lbl = ttk.Label(self.wnd_3, image = data['logos'][0], background = 'cornsilk')
                        lbl.image = data['logos'][0]
                        lbl.place(x = (500 - (self.font7.measure(data['teams'][0]) + self.font7.measure(data['teams'][1]) +
                                            self.font7.measure(7*' ')))/2 - 15 - data['logos'][0].width(), y = 70 + 73 * number_of_matches + add)

                    if data['logos'][1]:
                        lbl = ttk.Label(self.wnd_3, image = data['logos'][1], background = 'cornsilk')
                        lbl.image = data['logos'][1]
                        lbl.place(x = (500 - (self.font7.measure(data['teams'][0]) + self.font7.measure(data['teams'][1]) +
                                                    self.font7.measure(7*' ')))/2 + self.font7.measure(data['teams'][0]) + self.font7.measure(data['teams'][1]) +
                                                    self.font7.measure(7*' ') + 10, y = 70 + 73 * number_of_matches + add)
                number_of_matches += 1
            self.text.configure(state = DISABLED)
            menu_bar = Menu(self.wnd_3)
            self.wnd_3.configure(menu = menu_bar)
            stats_menu = Menu(menu_bar, tearoff = 0)
            menu_bar.add_command(label = "Форма команд", command = self.show_last_five)
            menu_bar.add_cascade(label = "Инфографика", menu = stats_menu)
            self.background_text = None
            for stat in self.name_stats_last_five:
                stats_menu.add_command(label = stat, command = lambda s = stat: self.show_graphics(s))
        except Exception as e:
            error_line = traceback.extract_tb(e.__traceback__)[-1].lineno
            logging.error(f"GUI error, строка {error_line}: {e}")

    def get_infographics(self, stat):
        op_1_possession = []
        op_1_op_logo = []
        for i in range(5):
            if i in self.match_data:
                data = self.match_data[i]
                if data['teams'].index(self.opponents[0]) == 0:
                    op_1_possession.append(data['stats'][2*self.name_stats_last_five.index(stat)])
                    op_1_op_logo.append(data['logos'][1])
                else:
                    op_1_possession.append(data['stats'][2*self.name_stats_last_five.index(stat) + 1])
                    op_1_op_logo.append(data['logos'][0])
        for i in range(len(op_1_possession)):
            op_1_possession[i] = int(op_1_possession[i].replace('%', ''))

        x = [i for i in range(1, 6)]
        y_pos = op_1_possession

        fig = Figure(figsize = (3, 2), dpi = 100)
        plot = fig.add_subplot(111)

        plot.spines['top'].set_visible(False)
        plot.spines['left'].set_visible(False)
        plot.spines['bottom'].set_visible(False)
        plot.spines['right'].set_visible(False)

        plot.plot(x, y_pos, marker = 'o', linestyle = '-', color = 'blue')
        fig.set_facecolor('cornsilk')
        plot.patch.set_facecolor('cornsilk')

        if stat == 'Владение мячом':
            plot.set_ylim(-24, 100)
        elif stat == 'Удары по воротам':
            plot.set_ylim(-10.8, 45)
        elif stat == 'Удары в створ':
            plot.set_ylim(-6, 25)
        elif stat == 'Удары мимо':
            plot.set_ylim(-4.8, 20)
        elif stat == 'Заблокированные удары':
            plot.set_ylim(-4.8, 20)
        elif stat == 'Фолы':
            plot.set_ylim(-8.4, 35)
        elif stat == 'Желтые карточки':
            plot.set_ylim(-2.4, 10)
        elif stat == 'Красные карточки':
            plot.set_ylim(-1.2, 5)
        elif stat == 'Угловые удары':
            plot.set_ylim(-4.8, 20)
        else:
            plot.set_ylim(-7.2, 30)

        for xi, yi in zip(x, y_pos):
            if stat == 'Владение мячом':
                plot.text(xi, yi + 5/100*plot.get_ylim()[1], str(yi) + '%', ha = 'center', va = 'bottom', fontsize = 10)
            else:
                plot.text(xi, yi + 5/100*plot.get_ylim()[1], str(yi), ha = 'center', va = 'bottom', fontsize = 10)

        for xi, yi, photo in zip(x, y_pos, op_1_op_logo):
            if photo != None:
                # Конвертируем PhotoImage в numpy array
                img_data = self.photoimage_to_array(photo)

                imagebox = OffsetImage(img_data)
                ab = AnnotationBbox(imagebox, (xi, yi - 15/100*plot.get_ylim()[1]),
                                frameon = False,
                                boxcoords = "data",
                                pad = 0)
                plot.add_artist(ab)

        plot.set_yticks([])
        plot.set_xticks([])
        plot.grid(False)
        fig.subplots_adjust(top = 1, bottom = 0, right = 0.97, left = 0.03, hspace = 0, wspace = 0)
        canvas_1 = FigureCanvasTkAgg(fig, master = self.wnd_3)
        canvas_1.draw()
        self.gr_1 = canvas_1.get_tk_widget()
        self.gr_1.place(y = 60, width = 500, height = 330)
        self.gr_1.config(highlightthickness = 0, borderwidth = 0)


        op_2_possession = []
        op_2_op_logo = []
        for i in range(5, 10):
            if i in self.match_data:
                data = self.match_data[i]
                if data['teams'].index(self.opponents[1]) == 0:
                    op_2_possession.append(data['stats'][2*self.name_stats_last_five.index(stat)])
                    op_2_op_logo.append(data['logos'][1])
                else:
                    op_2_possession.append(data['stats'][2*self.name_stats_last_five.index(stat) + 1])
                    op_2_op_logo.append(data['logos'][0])
        for i in range(len(op_2_possession)):
            op_2_possession[i] = int(op_2_possession[i].replace('%', ''))

        x = [i for i in range(1, 6)]
        y_pos = op_2_possession

        fig = Figure(figsize = (3, 2), dpi = 100)
        plot = fig.add_subplot(111)

        plot.spines['top'].set_visible(False)
        plot.spines['left'].set_visible(False)
        plot.spines['bottom'].set_visible(False)
        plot.spines['right'].set_visible(False)

        plot.plot(x, y_pos, marker = 'o', linestyle = '-', color = 'blue')
        fig.set_facecolor('cornsilk')
        plot.patch.set_facecolor('cornsilk')

        if stat == 'Владение мячом':
            plot.set_ylim(-24, 100)
        elif stat == 'Удары по воротам':
            plot.set_ylim(-10.8, 45)
        elif stat == 'Удары в створ':
            plot.set_ylim(-6, 25)
        elif stat == 'Удары мимо':
            plot.set_ylim(-4.8, 20)
        elif stat == 'Заблокированные удары':
            plot.set_ylim(-4.8, 20)
        elif stat == 'Фолы':
            plot.set_ylim(-8.4, 35)
        elif stat == 'Желтые карточки':
            plot.set_ylim(-2.4, 10)
        elif stat == 'Красные карточки':
            plot.set_ylim(-1.2, 5)
        elif stat == 'Угловые удары':
            plot.set_ylim(-4.8, 20)
        else:
            plot.set_ylim(-7.2, 30)

        for xi, yi in zip(x, y_pos):
            if stat == 'Владение мячом':
                plot.text(xi, yi + 5/100*plot.get_ylim()[1], str(yi) + '%', ha = 'center', va = 'bottom', fontsize = 10)
            else:
                plot.text(xi, yi + 5/100*plot.get_ylim()[1], str(yi), ha = 'center', va = 'bottom', fontsize = 10)

        for xi, yi, photo in zip(x, y_pos, op_2_op_logo):
            if photo != None:
                # Конвертируем PhotoImage в numpy array
                img_data = self.photoimage_to_array(photo)

                imagebox = OffsetImage(img_data)
                ab = AnnotationBbox(imagebox, (xi, yi - 15/100*plot.get_ylim()[1]),
                                frameon = False,
                                boxcoords = "data",
                                pad = 0)
                plot.add_artist(ab)

        plot.set_yticks([])
        plot.set_xticks([])
        plot.grid(False)
        fig.subplots_adjust(top = 1, bottom = 0, right = 0.97, left = 0.03, hspace = 0, wspace = 0)
        canvas_2 = FigureCanvasTkAgg(fig, master = self.wnd_3)
        canvas_2.draw()
        self.gr_2 = canvas_2.get_tk_widget()
        self.gr_2.place(y = 460, width = 500, height = 330)
        self.gr_2.config(highlightthickness = 0, borderwidth = 0)

    def photoimage_to_array(self, photo):
        pil_img = ImageTk.getimage(photo)
        return np.array(pil_img)

    def destroy_widget(self, widget):
        if widget != None:
            widget.destroy()


    def show_graphics(self, stat):
        self.destroy_widget(self.gr_1)
        self.destroy_widget(self.gr_2)
        self.destroy_widget(self.title_gr_1)
        self.destroy_widget(self.title_gr_2)
        self.destroy_widget(self.background_text)
        self.label_op_1.pack_forget()
        self.image_1.thumbnail((1000, 45))
        photo_1 = ImageTk.PhotoImage(self.image_1)
        self.image_2.thumbnail((1000, 45))
        photo_2 = ImageTk.PhotoImage(self.image_2)
        self.background_text = ttk.Label(self.wnd_3, background = 'cornsilk')
        self.background_text.place(width = 500, height = 800)
        self.title_gr_1 = ttk.Label(self.wnd_3, background = 'cornsilk', text = f'{stat}: {self.opponents[0].upper()}', image = photo_1, compound = 'right',
                                    font = self.font_title, foreground = 'blue4')
        self.title_gr_1.image = photo_1
        self.title_gr_1.place(x = (500 - self.font_title.measure(f'{stat}: {self.opponents[0].upper()}'))/2, y = 13)
        self.title_gr_2 = ttk.Label(self.wnd_3, background = 'cornsilk', text = f'{stat}: {self.opponents[1].upper()}', image = photo_2, compound = 'right',
                                    font = self.font_title, foreground = 'blue4')
        self.title_gr_2.image = photo_2
        self.title_gr_2.place(x = (500 - self.font_title.measure(f'{stat}: {self.opponents[1].upper()}'))/2, y = 410)
        self.text.place_forget()

        self.get_infographics(stat)

    def show_last_five(self):
        self.gr_1.destroy()
        self.gr_2.destroy()
        self.title_gr_1.destroy()
        self.title_gr_2.destroy()
        self.background_text.place_forget()
        self.label_op_1.pack(pady = 10)
        self.text.place(width = 500, height = 800, y = 50)

    def status_button(self):
        if self.wnd_2.winfo_exists():
            self.check = 1
            self.button_show_stat.configure(state = DISABLED)
            self.button_enter.configure(state = DISABLED)
            self.button_today.configure(state = DISABLED)
            self.button_yesterday.configure(state = DISABLED)
            self.button_tomorrow.configure(state = DISABLED)
        else:
            if self.wnd_3 != None:
                self.wnd_3.destroy()
            self.check = 0
            self.button_show_stat.configure(state = NORMAL)
            self.button_enter.configure(state = NORMAL)
            self.button_today.configure(state = NORMAL)
            self.button_yesterday.configure(state = NORMAL)
            self.button_tomorrow.configure(state = NORMAL)
            return
        self.window.after(500, self.status_button)

    def status_add_button(self):
        if self.wnd_2.winfo_exists():
            if self.wnd_3.winfo_exists():
                self.button_add_stat.configure(state = DISABLED)
            else:
                self.button_add_stat.configure(state = NORMAL)
                return
        else:
            return
        self.window.after(500, self.status_add_button)

    def f(self):
        t = Thread(target = self.get_text_threading, daemon = True)
        t.start()

    def get_image(self, attempt = 1, max_attempts = 3):
        try:
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
                self.image_1 = Image.open(io.BytesIO(blob_data_1))
                self.image_1.thumbnail((1000, 80))
                self.photo_1 = ImageTk.PhotoImage(self.image_1)
                logo_label_1 = ttk.Label(self.wnd_2, image = self.photo_1, background = 'cornsilk')
                logo_label_1.place(x = 10, y = 5)
                logo_label_1.image = self.photo_1
            if result_2:
                blob_data_2 = result_2[0]
            else:
                blob_data_2 = None
            if blob_data_2:
                self.image_2 = Image.open(io.BytesIO(blob_data_2))
                self.image_2.thumbnail((1000, 80))
                self.photo_2 = ImageTk.PhotoImage(self.image_2)
                logo_label_2 = ttk.Label(self.wnd_2, image = self.photo_2, background = 'cornsilk')
                logo_label_2.place(x = 585 - self.photo_2.width(), y = 5)
                logo_label_2.image = self.photo_2
            cur.close()
            conn.commit()
            conn.close()
            logging.info("successful connection to the database")
        except Exception as e:
            if attempt < max_attempts:
                logging.warning(f"retrying connecting to database... attempt {attempt}/{max_attempts}")
                time.sleep(2 ** attempt)
                self.get_image(attempt + 1, max_attempts)
            else:
                logging.error(f"error connecting to database: {e}")
                messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
                return

    def cancel_scheduled_update_dyn(self):
        if self.scheduled_update_id_dyn is not None:
            self.window.after_cancel(self.scheduled_update_id_dyn)
            self.scheduled_update_id_dyn = None

    def get_text_threading(self, attempt = 1, max_attempts = 3):
        self.cancel_scheduled_update_dyn()
        try:
            while self.wnd_2.winfo_exists():
                start = time.time()
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless = True)
                    page = browser.new_page()
                    page.goto(self.url_3)
                    page.wait_for_selector("div.match-summary__state-info")
                    text_content = page.inner_text('div.match-summary__state-info')
                    self.scheduled_update_id_dyn = self.window.after(0, self.update_text, text_content)
                logging.info("successful parsing of dynamic data")
                elapsed = time.time() - start
                time.sleep(max(60 - elapsed, 0))

        except Exception as e:
            if attempt < max_attempts:
                logging.warning(f"retrying parsing dynamic data... attempt {attempt}/{max_attempts}")
                time.sleep(2 ** attempt) 
                self.get_text_threading(attempt + 1, max_attempts)
            else:
                logging.error(f"error parsing dynamic data: {e}")
                messagebox.showerror("Ошибка", "Не удалось получить динамические данные")
                return

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
