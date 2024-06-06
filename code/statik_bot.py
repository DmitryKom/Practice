import wx
import wx.grid as gridlib
import random
import os
import subprocess

class Board:
    def __init__(self):
        self.size = 10
        self.board = [['' for _ in range(10)] for _ in range(10)]
        self.ships = {'Четырёхпалубный': 4, 'Трёхпалубный': 3, 'Двухпалубный': 2, 'Однопалубный': 1}
        self.placing_ship = None
        self.placing_size = 0
        self.placing_orientation = 'V'
        self.board_count = {ship: 0 for ship in self.ships}
        self.ship_counts = {'Четырёхпалубный': 1, 'Трёхпалубный': 2, 'Двухпалубный': 3, 'Однопалубный': 4}
        self.ship_coordinates = {ship: [] for ship in self.ships}  # Координаты всех кораблей

    def place_ship(self, x, y):
        if self.can_place_ship(x, y):
            self.set_ship(x, y, self.placing_size, self.placing_orientation, self.placing_ship)
            self.board_count[self.placing_ship] += 1
            return True
        else:
            return False

    def can_place_ship(self, x, y):
        if self.placing_orientation == 'H' and x + self.placing_size > self.size:
            return False
        elif self.placing_orientation == 'V' and y + self.placing_size > self.size:
            return False

        for i in range(self.placing_size):
            if self.placing_orientation == 'H':
                if self.board[y][x + i] != '':
                    return False
            else:
                if self.board[y + i][x] != '':
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

    def is_sunk(self, ship):
        for coordinates in self.ship_coordinates[ship]:
            if all(self.board[y][x] == 'X' for x, y in coordinates):
                return True
        return False

    def mark_surroundings(self, ship):
        for coordinates in self.ship_coordinates[ship]:
            if all(self.board[y][x] == 'X' for x, y in coordinates):
                for x, y in coordinates:
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.size and 0 <= ny < self.size and self.board[ny][nx] == '':
                                self.board[ny][nx] = 'O'

    def check_win(self):
        for coordinates_list in self.ship_coordinates.values():
            for coordinates in coordinates_list:
                if any(self.board[y][x] != 'X' for x, y in coordinates):
                    return False
        return True

class BattleshipGame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Морской бой", style = (wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.CAPTION))
        ico = wx.Icon('C:\\Users\\Дмитрий\\Downloads\\Telegram Desktop\\statick (2)\\statick\\logo.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.Center()
        self.InitUI()
        self.panel = wx.Panel(self)
        self.player_board = Board()
        self.computer_board = Board()
        self.player_grid = self.create_grid(self.panel, self.player_board)
        self.computer_grid = self.create_grid(self.panel, self.computer_board)

        self.side_panel = wx.Panel(self.panel)
        self.side_sizer = wx.BoxSizer(wx.VERTICAL)
        self.side_panel.SetSizer(self.side_sizer)

        self.ship_choice = wx.Choice(self.side_panel, choices=list(self.player_board.ships.keys()))
        self.orientation_checkbox = wx.CheckBox(self.side_panel, label="Горизонтально")
        self.start_game_button = wx.Button(self.side_panel, label="Начать игру")

        self.side_sizer.Add(self.ship_choice, 0, wx.ALL, 5)
        self.side_sizer.Add(self.orientation_checkbox, 0, wx.ALL, 5)
        self.side_sizer.Add(self.start_game_button, 0, wx.ALL, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.player_grid, 1, wx.EXPAND)
        sizer.Add(self.side_panel, 0, wx.EXPAND)
        sizer.Add(self.computer_grid, 1, wx.EXPAND)

        self.panel.SetSizerAndFit(sizer)
        self.Fit()
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.on_cell_click)
        self.ship_choice.Bind(wx.EVT_CHOICE, self.on_ship_choice)
        self.orientation_checkbox.Bind(wx.EVT_CHECKBOX, self.on_orientation_checkbox)
        self.start_game_button.Bind(wx.EVT_BUTTON, self.on_start_game)
        self.start_game_button.Disable()
        self.computer_grid.Disable()
        self.update_grids()

        self.computer_board.set_ship(0, 0, 4, 'V', 'Четырёхпалубный')
        self.computer_board.set_ship(2, 0, 3, 'H', 'Трёхпалубный')
        self.computer_board.set_ship(2, 2, 3, 'H', 'Трёхпалубный')
        self.computer_board.set_ship(3, 4, 2, 'V', 'Двухпалубный')
        self.computer_board.set_ship(5, 4, 2, 'H', 'Двухпалубный')
        self.computer_board.set_ship(6, 0, 2, 'V', 'Двухпалубный')
        self.computer_board.set_ship(7, 6, 1, 'H', 'Однопалубный')
        self.computer_board.set_ship(0, 7, 1, 'H', 'Однопалубный')
        self.computer_board.set_ship(9, 0, 1, 'H', 'Однопалубный')
        self.computer_board.set_ship(9, 2, 1, 'H', 'Однопалубный')
        self.last_hit = None
        self.game_started = False

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
        aboutDlg = wx.MessageDialog(self, "Морской бой – игра для двух человек (или человека и компьютера), в которой игроки \nпо очереди атакуют корабли, находящиеся на поле противника. "
                                          "\n\nЕсли по указанным координатам у соперника имеется корабль, то корабль или его \nчасть топится, а игрок, сделавший удачный ход, получает "
                                          "право сделать еще один ход. \n\nЦель игры – первым поразить все десять кораблей противника. На левом поле \nрасположены ваши корабли, на правом "
                                          "корабли вашего противника. \n\nКорабли не могут касаться друг друга. Расстояние между кораблями не менее одной \nклетки", "Правила игры", wx.OK)
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

    def create_grid(self, parent, board):
        grid = gridlib.Grid(parent)
        grid.CreateGrid(10, 10)

        for i in range(10):
            grid.SetRowLabelValue(i, str(i + 1))
            grid.SetColLabelValue(i, chr(65 + i))

        grid.AutoSizeColumns(False)
        for col in range(10):
            grid.SetColSize(col, 30)
            grid.SetRowSize(col, 30)
        grid.EnableEditing(False)
        return grid

    def on_cell_click(self, event):
        if not self.game_started:
            row, col = event.GetRow(), event.GetCol()
            if self.player_board.place_ship(col, row):
                self.update_grids()
                if all(self.player_board.board_count[ship] >= self.player_board.ship_counts[ship] for ship in self.player_board.ships):
                    self.start_game_button.Enable()

    def on_cell_click_player(self, event):
        row, col = event.GetRow(), event.GetCol()
        if self.computer_grid.GetCellValue(row, col) != '':
            return
        if self.computer_board.check_hit(col, row):
            self.computer_grid.SetCellValue(row, col, 'X')
            self.update_grids()
            if self.computer_board.check_win():
                wx.MessageBox('Вы выиграли!', 'Поздравляем')
                self.sea_battle_panel(event)
        else:
            self.computer_grid.SetCellValue(row, col, 'O')
            self.computer_move()
            self.update_grids()

    def computer_move(self, event=None):
        while True:
            if self.last_hit is not None:
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                random.shuffle(directions)
                for dx, dy in directions:
                    row, col = self.last_hit[0] + dx, self.last_hit[1] + dy
                    if 0 <= row < 10 and 0 <= col < 10 and self.player_grid.GetCellValue(row, col) == '':
                        break
                else:
                    self.last_hit = None
            if self.last_hit is None:
                row, col = random.randint(0, 9), random.randint(0, 9)
            if self.player_grid.GetCellValue(row, col) != '':
                continue
            if self.player_board.check_hit(col, row):
                self.player_grid.SetCellValue(row, col, 'X')
                self.update_grids()
                self.last_hit = (row, col)
                if self.player_board.check_win():
                    wx.MessageBox('Компьютер выиграл!', 'О нет!')
                    self.update_grids()
                    self.sea_battle_panel(event)
            else:
                self.player_grid.SetCellValue(row, col, 'O')
                self.update_grids()
                break

    def update_grids(self):
        for i in range(10):
            for j in range(10):
                cell_value = self.player_board.board[i][j]
                if cell_value != '':
                    color = wx.BLUE if cell_value not in ('X', 'O') else wx.Colour(169, 169, 169) if cell_value == 'X' else wx.Colour(220, 220, 220)
                    self.player_grid.SetCellBackgroundColour(i, j, color)
                    if cell_value == 'X':
                        self.player_grid.SetCellValue(i, j, 'X')
                    elif cell_value == 'O':
                        self.player_grid.SetCellValue(i, j, 'O')

                cell_value = self.computer_board.board[i][j]
                if cell_value in ('X', 'O'):
                    color = wx.Colour(169, 169, 169) if cell_value == 'X' else wx.Colour(220, 220, 220)
                    self.computer_grid.SetCellBackgroundColour(i, j, color)
                    if cell_value == 'X':
                        self.computer_grid.SetCellValue(i, j, 'X')
                    elif cell_value == 'O':
                        self.computer_grid.SetCellValue(i, j, 'O')
                else:
                    self.computer_grid.SetCellBackgroundColour(i, j, wx.WHITE)
                    self.computer_grid.SetCellValue(i, j, '')
        self.player_grid.Refresh()
        self.computer_grid.Refresh()

    def on_ship_choice(self, event):
        ship_name = self.ship_choice.GetString(self.ship_choice.GetSelection())
        if self.player_board.board_count[ship_name] >= self.player_board.ship_counts[ship_name]:
            wx.MessageBox(f"Вы уже разместили максимальное количество кораблей типа {ship_name}.", "Ошибка", wx.OK | wx.ICON_ERROR)
            return
        self.player_grid.Enable()
        self.player_board.placing_ship = ship_name
        self.player_board.placing_size = self.player_board.ships[ship_name]

    def on_orientation_checkbox(self, event):
        self.player_board.placing_orientation = 'H' if self.orientation_checkbox.IsChecked() else 'V'

    def on_start_game(self, event):
        if all(self.player_board.board_count[ship] >= self.player_board.ship_counts[ship] for ship in self.player_board.ships):
            self.game_started = True
            self.update_grids()
            self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.on_cell_click_player, self.computer_grid)
            self.start_game_button.Disable()
            self.computer_grid.Enable()
            self.orientation_checkbox.Disable()
            self.ship_choice.Disable()

app = wx.App(False)
frame = BattleshipGame(None)
frame.Show(True)
app.MainLoop()
