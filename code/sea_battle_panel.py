import wx
import os
import subprocess

class SeaBattlePanel(wx.Panel):
    def __init__(self, parent):
        super(SeaBattlePanel, self).__init__(parent)

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.mode_buttons = []
        modes = [
            "Статичный бот",
            "Бот с генерацией",
            "Игра с другом",
            "Расширенный режим"
        ]

        for mode in modes:
            font = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            btn = wx.Button(self, label=mode, size=(-1, 30))
            btn.SetFont(font)
            self.vbox.Add(btn, flag=wx.EXPAND | wx.ALL, border=5)
            btn.Bind(wx.EVT_BUTTON, self.OnModeButtonClick)
            btn.Hide()
            self.mode_buttons.append(btn)

        self.mode_button = wx.Button(self, label='Выбор режима')
        self.mode_button.Bind(wx.EVT_BUTTON, self.OnModeButtonClick)
        self.vbox.Add(self.mode_button, flag=wx.EXPAND | wx.ALL, border=10)
        font = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.mode_button.SetFont(font)

        self.exit_button = wx.Button(self, label='Выйти', pos=(125, 80))
        self.exit_button.Bind(wx.EVT_BUTTON, self.OnExitButtonClick)
        self.vbox.Add(self.exit_button, flag=wx.EXPAND | wx.ALL, border=10)
        self.exit_button.SetFont(font)
        self.SetSizer(self.vbox)

    def OnModeButtonClick(self, event):
        if event.GetEventObject().GetLabel() == "Статичный бот": # Извлекает объект, вызвавший событие (кнопка режима). Получает метку (текст) нажатой кнопки.
            self.statik_bot() # Отобразить сетку игры статичной карты
        elif event.GetEventObject().GetLabel() == "Бот с генерацией":
            self.random_bot() # Отобразить сетку игры случайной карты
        elif event.GetEventObject().GetLabel() == "Игра с другом":
            self.one_x_one() # Отобразить сетку игры 1 на 1
        elif event.GetEventObject().GetLabel() == "Расширенный режим":
            self.more_game() # Отобразить сетку игры расширенного режима
        else:
            self.mode_button.Hide()
            for btn in self.mode_buttons:
                btn.Show()
            self.Layout() # Обеспечивает правильное расположение кнопок на панели

    def OnExitButtonClick(self, event):
        self.GetParent().Close()
    def more_game(self):
    # Очистить панель перед отображением сетки игры
        self.GetParent().Close()
        # Путь к модулю
        module_path = 'C:\\Users\\Дмитрий\\Downloads\\Telegram Desktop\\statick (2)\\statick\\more_game.py'
        print(module_path)
        # Проверяем, существует ли файл
        if os.path.exists(module_path):
            # Запускаем модуль с помощью subprocess
            subprocess.Popen(['python', module_path])
        else:
            print(f"Модуль {module_path} не найден.")
    def one_x_one(self):
        # Очистить панель перед отображением сетки игры
        self.GetParent().Close()

        # Путь к модулю
        module_path = 'C:\\Users\\Дмитрий\\Downloads\\Telegram Desktop\\statick (2)\\statick\\1x1.py'
        print(module_path)
        # Проверяем, существует ли файл
        if os.path.exists(module_path):
            # Запускаем модуль с помощью subprocess
            subprocess.Popen(['python', module_path])
        else:
            print(f"Модуль {module_path} не найден.")

    def random_bot(self):
    # Очистить панель перед отображением сетки игры
        self.GetParent().Close()

        # Путь к модулю
        module_path = 'C:\\Users\\Дмитрий\\Downloads\\Telegram Desktop\\statick (2)\\statick\\random_bot.py'
        print(module_path)
        # Проверяем, существует ли файл
        if os.path.exists(module_path):
            # Запускаем модуль с помощью subprocess
            subprocess.Popen(['python', module_path])
        else:
            print(f"Модуль {module_path} не найден.")

    def statik_bot(self):
    # Очистить панель перед отображением сетки игры
        self.GetParent().Close()

        # Путь к модулю
        module_path = 'C:\\Users\\Дмитрий\\Downloads\\Telegram Desktop\\statick (2)\\statick\\statik_bot.py'
        print(module_path)
        # Проверяем, существует ли файл
        if os.path.exists(module_path):
            # Запускаем модуль с помощью subprocess
            subprocess.Popen(['python', module_path])
        else:
            print(f"Модуль {module_path} не найден.")

class SeaBattleFrame(wx.Frame):
    def __init__(self, parent, title):
        super(SeaBattleFrame, self).__init__(parent, title=title, size=(500, 500), style = (wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.CAPTION))
        ico = wx.Icon('C:\\Users\\Дмитрий\\Downloads\\Telegram Desktop\\statick (2)\\statick\\logo.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.InitUI()
        self.Centre()

        self.panel = SeaBattlePanel(self)

        # Загрузка фонового изображения
        self.background_image = wx.Image('C:\\Users\\Дмитрий\\Downloads\\Telegram Desktop\\statick (2)\\statick\\1.jpg', wx.BITMAP_TYPE_ANY)

        # Привязка событий рисования и изменения размера к панели
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_resize)

    def InitUI(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        aboutMenu = wx.Menu()
        inMenu = fileMenu.Append(wx.ID_ANY, 'В меню')
        #fileMenu.Append(wx.ID_ANY, 'Выбор режима', 'Выбор режима')
        fileMenu.Append(wx.ID_EXIT, 'Выйти')
        menubar.Append(fileMenu, 'Menu')
        menubar.Append(aboutMenu, 'About')
        Aboutcreator = aboutMenu.Append(wx.ID_ANY, "О разработчике", "Информация о разработчике")
        Aboutgame = aboutMenu.Append(wx.ID_ANY, "Правила игры", "Правила игры")

        # Обработчики событий
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.OnAboutcreator, Aboutcreator)
        self.Bind(wx.EVT_MENU, self.HelpGame, Aboutgame)
        self.Bind(wx.EVT_MENU, self.sea_battle_panel, inMenu)
        self.Bind(wx.EVT_MENU, self.onQuit, id=wx.ID_EXIT)

    def onQuit(self, event):
        self.Close()

    def OnAboutcreator(self, event):
        aboutDlg = wx.MessageDialog(self, "Данную игру разработал студент 2 курса группы 5.205-2\nКомягин Дмитрий Алексеевич", "О разработчике", wx.OK)
        aboutDlg.ShowModal()

    def HelpGame(self, event):
        aboutDlg = wx.MessageDialog(self, "Игра для двух участников, в которой игроки по очереди делают 'выстрелы'. \nЕсли у врага с этими координатами имеется корабль, то корабль или его палуба (дека)\n убивается, попавший делает еще один ход. Цель игрока: первым убить все игровые\n корабли врага партии.", "Правила игры", wx.OK)
        aboutDlg.ShowModal()

    def sea_battle_panel(self, event):
    # Очистить панель перед отображением сетки игры
        self.Close()

        # Путь к модулю
        module_path = 'C:\\Users\\Дмитрий\\Downloads\\Telegram Desktop\\statick (2)\\statick\\sea_battle_panel.py'

        # Проверяем, существует ли файл
        if os.path.exists(module_path):
            # Запускаем модуль с помощью subprocess
            subprocess.Popen(['python', module_path])
        else:
            print(f"Модуль {module_path} не найден.")

    def on_paint(self, event):
        # Создаем объект контекста устройства (DC) для рисования
        dc = wx.PaintDC(self.panel)

        # Рисуем bitmap на панели
        if hasattr(self, 'resized_bitmap'):
            dc.DrawBitmap(self.resized_bitmap, 0, 0)

    def on_resize(self, event):
        # Получаем новые размеры окна
        size = self.GetSize() # Возвращаем кортеж, содержащий ширину и высоту окна.
        width, height = size[0], size[1] # Присваиваем ширину и высоту переменным

        # Масштабируем изображение до новых размеров окна
        if width > 0 and height > 0:
            scaled_image = self.background_image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)

            # Преобразуем масштабированное изображение в bitmap
            self.resized_bitmap = wx.Bitmap(scaled_image)

        # Перерисовываем панель
        self.panel.Refresh()

        # Передаем событие дальше
        event.Skip()

app = wx.App(False)
frame = SeaBattleFrame(None, title="Морской бой")
frame.Show()
app.MainLoop()
