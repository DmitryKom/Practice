import wx
import wx.grid as gridlib
import random
import os
import subprocess

class Board:
    def __init__(self, size):
        self.size = size
        self.board = [['' for _ in range(size)] for _ in range(size)]
        self.ships = {}
        self.remaining_ships = 0
        self.placing_ship = None
        self.placing_size = 0
        self.placing_orientation = None
        self.visible = True
        self.mines = []
        self.board_count = {}
        self.ship_coordinates = {}

    def place_mines(self, num_mines):
        for _ in range(num_mines):
            while True:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                if self.board[y][x] == '':  # Проверка, что мина помещена на пустую ячейку
                    self.mines.append((x, y))
                    break

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
            if self.board_count[self.placing_ship] >= self.ships[self.placing_ship]:
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
        elif (x, y) in self.mines:
            return self.trigger_mine(x, y)
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

    def trigger_mine(self, x, y):
        mine_impact = [(x, y), (x - 1, y), (x, y - 1)]
        hit_ship = False
        for (ix, iy) in mine_impact:
            if 0 <= ix < self.size and 0 <= iy < self.size:
                if self.board[iy][ix] not in ('X', 'O', ''):
                    self.board[iy][ix] = 'X'
                    hit_ship = True
                else:
                    if self.board[iy][ix] != 'X':
                        self.board[iy][ix] = 'O'
        self.board[y][x] = 'O' if not hit_ship else 'X'
        return hit_ship

class BattleshipGame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Морской бой", style = (wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.CAPTION))
        self.InitUI()
        ico = wx.Icon('C:\\Users\\Дмитрий\\Downloads\\Telegram Desktop\\statick (2)\\statick\\logo.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.Center()
        self.panel = wx.Panel(self)
        self.board_size = self.get_board_size_dialog()
        if self.board_size is None:
            self.Close()
            return

        self.num_mines = self.get_mines_count_dialog()
        self.ships_count = self.get_ships_count_dialog()

        if not self.validate_ships_count(self.board_size, self.ships_count):
            wx.MessageBox('Слишком много кораблей для данного размера поля.', 'Ошибка', wx.OK | wx.ICON_ERROR)
            self.Close()
            return

        self.player1_board = Board(self.board_size)
        self.player2_board = Board(self.board_size)
        self.initialize_board(self.player1_board)
        self.initialize_board(self.player2_board)
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
        main_sizer = wx.BoxSizer(wx.VERTICAL)

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

        main_sizer.Add(top_sizer, 0, wx.EXPAND)
        main_sizer.Add(boards_sizer, 1, wx.EXPAND)

        self.status_bar = self.CreateStatusBar()
        self.panel.SetSizerAndFit(main_sizer)
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

    def initialize_board(self, board):
        board.ships = self.ships_count
        board.board_count = {ship: 0 for ship in board.ships}
        board.ship_coordinates = {ship: [] for ship in board.ships}

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
                if all(current_board.board_count[ship] >= current_board.ships[ship] for ship in current_board.ships):
                    finish_button.Enable()

    def on_finish_placement(self, event):
        if self.current_player == 1:
            self.player1_board.visible = False
            self.current_player = 2
            self.player1_finish_placement_button.Disable()
            self.player1_ship_choice.SetSelection(wx.NOT_FOUND)
            self.player1_grid.Disable()
            wx.MessageBox('Игрок 1 завершил размещение кораблей. Теперь очередь игрока 2.', 'Информация')
            self.update_grids()
            self.player2_orientation_checkbox.Enable()
            self.player1_orientation_checkbox.Disable()
            self.player2_ship_choice.Enable()
            self.player1_ship_choice.Disable()
        elif self.current_player == 2:
            self.player1_board.place_mines(self.num_mines)
            self.player2_board.place_mines(self.num_mines)
            self.player2_board.visible = False
            self.player2_finish_placement_button.Disable()
            self.start_game_button.Enable()
            self.player2_grid.Disable()
            wx.MessageBox('Игрок 2 завершил размещение кораблей. Теперь можно начать игру.', 'Информация')
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
        if current_board.board_count[ship_name] >= current_board.ships[ship_name]:
            wx.MessageBox(f"Максимальное количество {ship_name} размещено.", "Ошибка", wx.OK | wx.ICON_ERROR)
            return
        current_board.placing_ship = ship_name
        current_board.placing_size = {'Четырёхпалубный': 4, 'Трёхпалубный': 3, 'Двухпалубный': 2, 'Однопалубный': 1}[ship_name]

    def on_cell_click_game(self, event):
        if self.game_started:
            row, col = event.GetRow(), event.GetCol()
            if self.current_player == 1:
                if self.player2_grid.GetCellValue(row, col) != '':
                    return
                hit_result = self.player2_board.check_hit(col, row)
                if hit_result:
                    if (col, row) in self.player2_board.mines:
                        hit_ship = self.player2_board.trigger_mine(col, row)
                        self.update_grids()  # Обновление цвета сетки сразу после запуска мины
                    else:
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
                hit_result = self.player1_board.check_hit(col, row)
                if hit_result:
                    if (col, row) in self.player1_board.mines:
                        hit_ship = self.player1_board.trigger_mine(col, row)
                        self.update_grids()  # Обновление цвета сетки сразу после запуска мины
                    else:
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
        for i in range(self.board_size):
            for j in range(self.board_size):
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

    def get_ships_count_dialog(self, event=None):
        ship_types = ['Четырёхпалубный', 'Трёхпалубный', 'Двухпалубный', 'Однопалубный']
        ships_count = {}
        total_ships = 0
        for ship in ship_types:
            dlg = wx.TextEntryDialog(self.panel, f'Введите количество типа: {ship} (Осталось {self.board_size - total_ships}):', 'Количество кораблей', '1')
            if dlg.ShowModal() == wx.ID_OK:
                count = dlg.GetValue()
                try:
                    count = int(count)
                    if count < 0 or total_ships + count > self.board_size:
                        wx.MessageBox(f'Общее количество кораблей не должно быть меньше 0 и не должно превышать {self.board_size}.', 'Ошибка', wx.OK | wx.ICON_ERROR)
                        return self.get_ships_count_dialog()
                    ships_count[ship] = count
                    total_ships += count
                except ValueError:
                    wx.MessageBox('Некорректное количество кораблей.', 'Ошибка', wx.OK | wx.ICON_ERROR)
                    return self.get_ships_count_dialog()
            else:
                self.sea_battle_panel(event)
                self.Close()
                return
        if total_ships == 0:
            wx.MessageBox(f'Количество всех кораблей равно 0, сделайте хотя бы один корабль', 'Ошибка', wx.OK | wx.ICON_ERROR)
            return self.get_ships_count_dialog()
        return ships_count

    def validate_ships_count(self, board_size, ships_count):
        total_ships = sum(ships_count.values())
        return total_ships <= board_size  # Обеспечение достаточного пространства с учетом пробелов

    def get_mines_count_dialog(self, event=None):
            dlg = wx.TextEntryDialog(self.panel, f'Введите количество мин для двух полей (натуральное четное число). Доступно {self.board_size * self.board_size}:', 'Количество мин', '10')
            if dlg.ShowModal() == wx.ID_OK:
                mines_text = dlg.GetValue()
                try:
                    mines = int(mines_text)
                    if mines % 2 == 0 and mines >= 0 and mines <= self.board_size * self.board_size:
                        return mines
                    else:
                        wx.MessageBox(f'Количество мин должно быть четным и в пределах от 0 до {self.board_size * self.board_size}.', 'Ошибка', wx.OK | wx.ICON_ERROR)
                        return self.get_mines_count_dialog()
                except ValueError:
                    wx.MessageBox('Некорректное количество мин.', 'Ошибка', wx.OK | wx.ICON_ERROR)
                    return self.get_mines_count_dialog()
            else:
                self.sea_battle_panel(event)
                breakpoint()

    def get_board_size_dialog(self, event=None):
        dlg = wx.TextEntryDialog(self.panel, 'Введите размер поля (от 10 до 26):', 'Размер поля', '10')
        if dlg.ShowModal() == wx.ID_OK:
            size_text = dlg.GetValue()
            try:
                size = int(size_text)
                if 10 <= size <= 26:
                    return size
                else:
                    wx.MessageBox('Некорректный размер поля. Введите число от 10 до 26.', 'Ошибка', wx.OK | wx.ICON_ERROR)
                    return self.get_board_size_dialog()
            except ValueError:
                wx.MessageBox('Некорректный размер поля. Введите число от 10 до 26.', 'Ошибка', wx.OK | wx.ICON_ERROR)
                return self.get_board_size_dialog()
        else:
            self.sea_battle_panel(event)
        return None

app = wx.App(False)
frame = BattleshipGame(None)
frame.Show(True)
app.MainLoop()
