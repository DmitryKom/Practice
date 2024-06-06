import wx
import wx.grid as gridlib
import os
import subprocess

# Класс Board отвечает за логику игровой доски
class Board:
    def __init__(self, size, num_ships):
        self.size = size
        self.board = [['' for _ in range(size)] for _ in range(size)]  # Создание пустой доски
        self.num_ships = num_ships
        self.ships = {'Четырёхпалубный': 4, 'Трёхпалубный': 3, 'Двухпалубный': 2, 'Однопалубный': 1}
        self.remaining_ships = self.num_ships
        self.placing_ship = None
        self.placing_size = 0
        self.placing_orientation = None
        self.visible = True
        self.board_count = {ship: 0 for ship in self.ships}
        self.ship_counts = {'Четырёхпалубный': 1, 'Трёхпалубный': 2, 'Двухпалубный': 3, 'Однопалубный': 4}
        self.ship_coordinates = {ship: [] for ship in self.ships}

    # Метод для размещения корабля
    def place_ship(self, x, y):
        if self.can_place_ship(x, y):
            self.set_ship(x, y, self.placing_size, self.placing_orientation, self.placing_ship)
            self.board_count[self.placing_ship] += 1
            return True
        else:
            return False

    # Метод для проверки возможности размещения корабля
    def can_place_ship(self, x, y):
        if self.placing_orientation == 'H' and x + self.placing_size > self.size:
            return False
        elif self.placing_orientation == 'V' and y + self.placing_size > self.size:
            return False

        for i in range(self.placing_size):
            if self.placing_orientation == 'H':
                if x + i >= self.size or self.board[y][x + i] != '':
                    return False
            else:
                if y + i >= self.size or self.board[y + i][x] != '':
                    return False

        for i in range(-1, self.placing_size + 1):
            for j in range(-1, 2):
                if self.placing_orientation == 'H':
                    if 0 <= y + j < self.size and 0 <= x + i < self.size and self.board[y + j][x + i] != '':
                        return False
                else:
                    if 0 <= y + i < self.size and 0 <= x + j < self.size and self.board[y + i][x + j] != '':
                        return False

        if self.placing_ship is not None:
            if self.board_count[self.placing_ship] >= self.ship_counts[self.placing_ship]:
                return False

        return True

    # Метод для установки корабля на доске
    def set_ship(self, x, y, size, orientation, ship):
        coordinates = []
        for i in range(size):
            if orientation == 'H':
                self.board[y][x + i] = ship
                coordinates.append((x + i, y))
            else:
                self.board[y + i][x] = ship
                coordinates.append((x, y + i))
        self.ship_coordinates[ship].append(coordinates)

    # Метод для проверки попадания по кораблю
    def check_hit(self, x, y):
        if self.board[y][x] != '' and self.board[y][x] != 'X' and self.board[y][x] != 'O':
            hit_ship = self.board[y][x]
            self.board[y][x] = 'X'
            if self.is_sunk(hit_ship):
                self.mark_surroundings(hit_ship)
            return True
        elif self.board[y][x] == '':
            self.board[y][x] = 'O'
        return False

    # Метод для проверки, потоплен ли корабль
    def is_sunk(self, ship):
        for coordinates in self.ship_coordinates[ship]:
            if all(self.board[y][x] == 'X' for x, y in coordinates):
                return True
        return False

    # Метод для пометки окружающих клеток после потопления корабля
    def mark_surroundings(self, ship):
        for coordinates in self.ship_coordinates[ship]:
            if all(self.board[y][x] == 'X' for x, y in coordinates):
                for x, y in coordinates:
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.size and 0 <= ny < self.size and self.board[ny][nx] == '':
                                self.board[ny][nx] = 'O'

    # Метод для проверки победы
    def check_win(self):
        for coordinates_list in self.ship_coordinates.values():
            for coordinates in coordinates_list:
                if any(self.board[y][x] != 'X' for x, y in coordinates):
                    return False
        return True

# Класс BattleshipGame отвечает за логику игры и интерфейс
class BattleshipGame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Морской бой", style = (wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.CAPTION))
        ico = wx.Icon('C:\\Users\\Дмитрий\\Downloads\\Telegram Desktop\\statick (2)\\statick\\logo.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.Center()
        self.InitUI()
        self.panel = wx.Panel(self)
        self.player1_board = Board(10, 10)
        self.player2_board = Board(10, 10)
        self.player1_grid = self.create_grid(self.panel, self.player1_board)
        self.player2_grid = self.create_grid(self.panel, self.player2_board)
        self.current_player = 1

        self.player1_text = wx.StaticText(self.panel, label="Игрок 1")
        self.player2_text = wx.StaticText(self.panel, label="Игрок 2")

        # Панели управления для игрока 1
        self.player1_controls_panel = wx.Panel(self.panel)
        self.player1_controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.player1_controls_panel.SetSizer(self.player1_controls_sizer)

        self.player1_ship_choice = wx.Choice(self.player1_controls_panel, choices=list(self.player1_board.ships.keys()))
        self.player1_orientation_checkbox = wx.CheckBox(self.player1_controls_panel, label="Горизонтально")
        self.player1_finish_placement_button = wx.Button(self.player1_controls_panel, label="Завершить размещение")
        self.player1_finish_placement_button.Disable()

        self.player1_controls_sizer.Add(self.player1_ship_choice, 0, wx.ALL, 5)
        self.player1_controls_sizer.Add(self.player1_orientation_checkbox, 0, wx.ALL, 5)
        self.player1_controls_sizer.Add(self.player1_finish_placement_button, 0, wx.ALL, 5)

        # Панели управления для игрока 2
        self.player2_controls_panel = wx.Panel(self.panel)
        self.player2_controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.player2_controls_panel.SetSizer(self.player2_controls_sizer)

        self.player2_ship_choice = wx.Choice(self.player2_controls_panel, choices=list(self.player2_board.ships.keys()))
        self.player2_orientation_checkbox = wx.CheckBox(self.player2_controls_panel, label="Горизонтально")
        self.player2_finish_placement_button = wx.Button(self.player2_controls_panel, label="Завершить размещение")
        self.player2_ship_choice.Disable()
        self.player2_finish_placement_button.Disable()
        self.player2_orientation_checkbox.Disable()
        self.start_game_button = wx.Button(self.panel, label="Начать игру")
        self.start_game_button.Disable()

        self.player2_controls_sizer.Add(self.player2_ship_choice, 0, wx.ALL, 5)
        self.player2_controls_sizer.Add(self.player2_orientation_checkbox, 0, wx.ALL, 5)
        self.player2_controls_sizer.Add(self.player2_finish_placement_button, 0, wx.ALL, 5)

        # Основной горизонтальный
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Максимальный размер кнопки "Начать игру"
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.Add(self.start_game_button, 1, wx.EXPAND)

        # Игрок 1 (управление + сетка)
        player1_sizer = wx.BoxSizer(wx.VERTICAL)
        player1_sizer.Add(self.player1_text, 0, wx.EXPAND)
        player1_sizer.Add(self.player1_controls_panel, 0, wx.EXPAND)
        player1_sizer.Add(self.player1_grid, 1, wx.EXPAND)

        # Игрок 2 (управление + сетка)
        player2_sizer = wx.BoxSizer(wx.VERTICAL)
        player2_sizer.Add(self.player2_text, 0, wx.EXPAND)
        player2_sizer.Add(self.player2_controls_panel, 0, wx.EXPAND)
        player2_sizer.Add(self.player2_grid, 1, wx.EXPAND)

        boards_sizer = wx.BoxSizer(wx.HORIZONTAL)
        boards_sizer.Add(player1_sizer, 1, wx.EXPAND)
        boards_sizer.Add(player2_sizer, 1, wx.EXPAND)

        sizer.Add(top_sizer, 0, wx.EXPAND)
        sizer.Add(boards_sizer, 1, wx.EXPAND)

        self.status_bar = self.CreateStatusBar()
        self.panel.SetSizerAndFit(sizer)
        self.Fit()
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.on_cell_click)
        self.player1_finish_placement_button.Bind(wx.EVT_BUTTON, self.on_finish_placement)
        self.player2_finish_placement_button.Bind(wx.EVT_BUTTON, self.on_finish_placement)
        self.start_game_button.Bind(wx.EVT_BUTTON, self.on_start_game)
        self.player1_ship_choice.Bind(wx.EVT_CHOICE, self.on_ship_choice)
        self.player2_ship_choice.Bind(wx.EVT_CHOICE, self.on_ship_choice)
        self.player1_orientation_checkbox.Bind(wx.EVT_CHECKBOX, self.on_orientation_checkbox)
        self.player2_orientation_checkbox.Bind(wx.EVT_CHECKBOX, self.on_orientation_checkbox)
        self.game_started = False
        self.update_grids()

    def InitUI(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        aboutMenu = wx.Menu()
        inMenu = fileMenu.Append(wx.ID_ANY, 'В меню')
        fileMenu.Append(wx.ID_EXIT, 'Выйти')
        menubar.Append(fileMenu, 'Menu')
        menubar.Append(aboutMenu, 'About')
        Aboutcreator = aboutMenu.Append(wx.ID_ANY, "О разработчике", "Информация о разработчике")
        Aboutgame = aboutMenu.Append(wx.ID_ANY, "Правила игры", "Правила игры")

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
        aboutDlg = wx.MessageDialog(self, "Морской бой – игра для двух человек (или человека и компьютера), в которой игроки \nпо очереди атакуют корабли, находящиеся на поле противника. "
                                          "\n\nЕсли по указанным координатам у соперника имеется корабль, то корабль или его \nчасть топится, а игрок, сделавший удачный ход, получает "
                                          "право сделать еще один ход. \n\nЦель игры – первым поразить все десять кораблей противника. На левом поле \nрасположены ваши корабли, на правом "
                                          "корабли вашего противника. \n\nКорабли не могут касаться друг друга. Расстояние между кораблями не менее одной \nклетки", "Правила игры", wx.OK)
        aboutDlg.ShowModal()

    def sea_battle_panel(self, event):
        self.Close()
        module_path = 'C:\\Users\\Дмитрий\\Downloads\\Telegram Desktop\\statick (2)\\statick\\sea_battle_panel.py'
        if os.path.exists(module_path):
            subprocess.Popen(['python', module_path])
        else:
            print(f"Модуль {module_path} не найден.")

    def create_grid(self, parent, board):
        grid = gridlib.Grid(parent)
        grid.CreateGrid(board.size, board.size)

        for i in range(board.size):
            grid.SetRowLabelValue(i, str(i + 1))
            grid.SetColLabelValue(i, chr(65 + i))

        grid.AutoSizeColumns(False)
        for col in range(board.size):
            grid.SetColSize(col, 30)
            grid.SetRowSize(col, 30)

        grid.EnableEditing(False)
        return grid

    def on_orientation_checkbox(self, event):
        current_board = self.player1_board if self.current_player == 1 else self.player2_board
        current_board.placing_orientation = 'H' if event.GetEventObject().GetValue() else 'V'

    def on_cell_click(self, event):
        if not self.game_started:
            row, col = event.GetRow(), event.GetCol()
            current_board = self.player1_board if self.current_player == 1 else self.player2_board
            if current_board.place_ship(col, row):
                self.update_grids()
                finish_button = self.player1_finish_placement_button if self.current_player == 1 else self.player2_finish_placement_button
                if all(current_board.board_count[ship] >= current_board.ship_counts[ship] for ship in current_board.ships):
                    finish_button.Enable()
                self.update_grids()

    def on_finish_placement(self, event):
        if self.current_player == 1:
            self.player1_board.visible = False
            self.current_player = 2
            self.player1_finish_placement_button.Disable()
            self.player1_ship_choice.SetSelection(wx.NOT_FOUND)
            self.player1_grid.Disable()
            wx.MessageBox('Игрок 1 закончил расставлять корабли. Теперь очередь игрока 2.', 'Оповещение')
            self.update_grids()
            self.player2_orientation_checkbox.Enable()
            self.player1_orientation_checkbox.Disable()
            self.player2_ship_choice.Enable()
            self.player1_ship_choice.Disable()
        elif self.current_player == 2:
            self.player2_board.visible = False
            self.player2_finish_placement_button.Disable()
            self.start_game_button.Enable()
            self.player2_grid.Disable()
            wx.MessageBox('Игрок 2 закончил расставлять корабли. Вы можете начать игру прямо сейчас.', 'Оповещение')
            self.player2_orientation_checkbox.Disable()
            self.player2_ship_choice.Disable()
            self.update_grids()
            self.player2_grid.Disable()

    def on_start_game(self, event):
        self.game_started = True
        self.player1_board.visible = False
        self.player2_board.visible = False
        self.player1_finish_placement_button.Disable()
        self.player2_finish_placement_button.Disable()
        self.start_game_button.Disable()
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.on_cell_click_game)
        self.update_grids()

    def on_ship_choice(self, event):
        ship_name = event.GetEventObject().GetStringSelection()
        current_board = self.player1_board if self.current_player == 1 else self.player2_board
        if current_board.board_count[ship_name] >= current_board.ship_counts[ship_name]:
            wx.MessageBox(f"Максимальное количество кораблей типа: {ship_name}", "Предупреждение", wx.OK | wx.ICON_ERROR)
            return
        current_board.placing_ship = ship_name
        current_board.placing_size = current_board.ships[ship_name]

    def on_cell_click_game(self, event):
        if self.game_started:
            row, col = event.GetRow(), event.GetCol()
            if self.current_player == 1:
                if self.player2_grid.GetCellValue(row, col) != '':
                    return
                if self.player2_board.check_hit(col, row):
                    self.player2_grid.SetCellValue(row, col, 'X')
                    if self.player2_board.check_win():
                        self.update_grids()
                        wx.MessageBox('Игрок 1 победил!', 'Поздравления')
                        self.sea_battle_panel(event)
                else:
                    self.player2_grid.SetCellValue(row, col, 'O')
                    self.current_player = 2
            elif self.current_player == 2:
                if self.player1_grid.GetCellValue(row, col) != '':
                    return
                if self.player1_board.check_hit(col, row):
                    self.player1_grid.SetCellValue(row, col, 'X')
                    if self.player1_board.check_win():
                        self.update_grids()
                        wx.MessageBox('Игрок 2 победил!', 'Поздравления')
                        self.sea_battle_panel(event)
                else:
                    self.player1_grid.SetCellValue(row, col, 'O')
                    self.current_player = 1
            self.update_grids()

    def update_status_bar(self, message):
        self.status_bar.SetStatusText(message)

    def update_grids(self):
        for i in range(10):
            for j in range(10):
                cell_value = self.player1_board.board[i][j]
                if cell_value != '' and cell_value not in ('X', 'O'):
                    color = wx.BLUE if self.player1_board.visible else wx.WHITE
                    self.player1_grid.SetCellBackgroundColour(i, j, color)
                elif cell_value in ('X', 'O'):
                    color = wx.Colour(169, 169, 169) if cell_value == 'X' else wx.Colour(220, 220, 220)
                    self.player1_grid.SetCellBackgroundColour(i, j, color)
                    self.player1_grid.SetCellValue(i, j, cell_value)

                cell_value = self.player2_board.board[i][j]
                if cell_value != '' and cell_value not in ('X', 'O'):
                    color = wx.BLUE if self.player2_board.visible else wx.WHITE
                    self.player2_grid.SetCellBackgroundColour(i, j, color)
                elif cell_value in ('X', 'O'):
                    color = wx.Colour(169, 169, 169) if cell_value == 'X' else wx.Colour(220, 220, 220)
                    self.player2_grid.SetCellBackgroundColour(i, j, color)
                    self.player2_grid.SetCellValue(i, j, cell_value)

        if self.current_player == 1:
            self.player1_grid.Enable()
            self.player2_grid.Disable()
            self.update_status_bar("Игрок 1 размещает корабли")
        else:
            self.player1_grid.Disable()
            self.player2_grid.Enable()
            self.update_status_bar("Игрок 2 размещает корабли")

        if self.game_started:
            if self.current_player == 1:
                self.player1_grid.Disable()
                self.player2_grid.Enable()
                self.update_status_bar("Ход игрока 1")
            else:
                self.player1_grid.Enable()
                self.player2_grid.Disable()
                self.update_status_bar("Ход игрока 2")

        self.player1_grid.Refresh()
        self.player2_grid.Refresh()

app = wx.App(False)
frame = BattleshipGame(None)
frame.Show(True)
app.MainLoop()
