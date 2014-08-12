
import sublime
import sublime_plugin


SUBLIME_MAJOR = int(sublime.version()[0])

if SUBLIME_MAJOR == 3:
    from .base import Game
    from .touch import LiveEventListener, add_event_handler, remove_event_handlers
    from .utils import UtilsEditViewCommand
elif SUBLIME_MAJOR == 2:
    from base import Game
    from touch import LiveEventListener, add_event_handler, remove_event_handlers
    from utils import UtilsEditViewCommand
else:
    raise Exception('We only support sublime 2 or 3')


STATUS_PLAYING = 0
STATUS_WINNER = 1
STATUS_DRAW = 2
IN_A_ROW_INSTANCES = {}
PLAYER_COLORS = (
    ('yellow', '#ffec38'),
    ('red', '#ff3a2f'),
    ('orange', '#ff7f00'),
    ('blue', '#385eff'),
    ('green', '#30ec34'),
    ('magenta', '#dd5eff')
)


class Cell:
    def __init__(self, index):
        self.index = index
        self.color = 'white'


class InARowGame(Game):
    def __init__(self, view=None, rows=6, cols=7, target=4, players=2):
        super(InARowGame, self).__init__(view, settings={'name': 'In A Row'})
        self.colors = [
            {
                'name': 'white', 'scope': 'white', 'background': '#ffffff',
                'foreground': '#ffffff', 'caret': '#ffffff'
            },
            {
                'name': 'yellow', 'scope': 'yellow', 'background': '#ffec38',
                'foreground': '#000000', 'caret': '#ffec38'
            },
            {
                'name': 'red', 'scope': 'red', 'background': '#ff3a2f',
                'foreground': '#000000', 'caret': '#ff3a2f'
            },
            {
                'name': 'orange', 'scope': 'orange', 'background': '#ff7f00',
                'foreground': '#000000', 'caret': '#ff7f00'
            },
            {
                'name': 'blue', 'scope': 'blue', 'background': '#385eff',
                'foreground': '#000000', 'caret': '#385eff'
            },
            {
                'name': 'green', 'scope': 'green', 'background': '#30ec34',
                'foreground': '#000000', 'caret': '#30ec34'
            },
            {
                'name': 'magenta', 'scope': 'magenta', 'background': '#dd5eff',
                'foreground': '#000000', 'caret': '#dd5eff'
            },
        ]
        if players > len(PLAYER_COLORS):
            sublime.message_dialog('Max %d players.' % len(PLAYER_COLORS))
            return

        self.row_count = rows
        self.col_count = cols
        self.target = target
        self.players = players
        self.player_colors = PLAYER_COLORS[:players]
        self.winner = self.cells = self.cols = self.game_over = self.whos_move = None
        self.reset_game()

    def draw_board(self):
        regions_to_add = {'white': []}
        regions_to_add.update(dict((x[0], []) for x in self.player_colors))
        remove_event_handlers(self.view)
        for color in regions_to_add.keys():
            self.view.erase_regions(color)
        title = 'GAME OVER' if self.game_over else 'Player %s' % (self.whos_move + 1)
        data = self.centered_text(title, (3 * self.col_count + 1))
        if not self.game_over or self.winner is not None:
            region = sublime.Region(0, len(data))
            regions_to_add[self.player_colors[self.whos_move][0]].append(region)
        data += '\n'
        for row in range(self.row_count):
            for col in range(self.col_count):
                data += '+--'
                if not self.game_over:
                    region = sublime.Region(len(data) - 2, len(data))
                    region.cell = self.cells[row * self.col_count + col]
                    add_event_handler(
                        self.view, region, lambda w, x, y, z: self.click_handler(y.cell), None)
            data += '+\n'
            for col in range(self.col_count):
                data += '|  '
                region = sublime.Region(len(data) - 2, len(data))
                regions_to_add[self.cells[row * self.col_count + col].color].append(region)
                if not self.game_over:
                    region = sublime.Region(len(data) - 2, len(data))
                    region.cell = self.cells[row * self.col_count + col]
                    add_event_handler(
                        self.view, region, lambda w, x, y, z: self.click_handler(y.cell), None)
            data += '|\n'
        for col in range(self.col_count):
            data += '+--'
        data += '+\n'

        pre_length = len(data)
        data += self.centered_text('%s Players' % self.players, (3 * self.col_count + 1))
        if not self.game_over or self.winner is not None:
            region = sublime.Region(pre_length, len(data))
            regions_to_add[self.player_colors[self.whos_move][0]].append(region)
        data += '\n'

        pre_length = len(data)
        data += self.centered_text('- | +', (3 * self.col_count + 1))
        if not self.game_over or self.winner is not None:
            region = sublime.Region(pre_length, pre_length + int((len(data) - pre_length) / 2))
            add_event_handler(self.view, region, lambda w, x, y, z: self.zoom(-10, True), None)
            region = sublime.Region(pre_length + int((len(data) - pre_length) / 2), len(data))
            add_event_handler(self.view, region, lambda w, x, y, z: self.zoom(+10, True), None)
        data += '\n'

        self.view.run_command(
            'utils_edit_view', {'data': data, 'start': 0, 'end': self.view.size()}
        )
        for color, regions in regions_to_add.items():
            self.view.add_regions(color, regions, color, '', 0)
        if self.game_over:
            region = sublime.Region(0, self.view.size())
            add_event_handler(self.view, region, lambda w, x, y, z: self.reset_game(), None)

    def click_handler(self, cell):
        for cell in reversed(self.cols[cell.index % self.col_count]):
            if cell.color == 'white':
                cell.color = self.player_colors[self.whos_move][0]
                self.whos_move += 1
                break
        status = self.is_game_over()
        if not status == STATUS_PLAYING:
            self.whos_move -= 1
            self.set_color_scheme(background='#cccccc')
            self.game_over = True
            if status == STATUS_WINNER:
                self.winner = self.whos_move
        if self.whos_move == self.players:
            self.whos_move = 0
        sel = self.view.sel()
        sel.clear()
        sel.add(sublime.Region(0, 0))
        self.draw_board()

    def is_game_over(self):
        no_white_seen = True
        for cell in self.cells:
            if cell.color == 'white':
                no_white_seen = False
                continue
            for direction in [
                'up', 'down', 'left', 'right',
                'up_left', 'up_right', 'down_left', 'down_right'
            ]:
                next_cell = cell
                for i in range(1, self.target):
                    next_cell = self.get_next_cell(next_cell, direction)
                    if next_cell is None or not next_cell.color == cell.color:
                        break
                else:
                    return STATUS_WINNER
        return STATUS_DRAW if no_white_seen else STATUS_PLAYING

    def get_next_cell(self, cell, direction):
        cell_index = {
            'up': lambda cell: cell.index - self.col_count if
            cell.index >= self.col_count else None,
            'down': lambda cell: cell.index + self.col_count if
            cell.index <= self.col_count * (self.row_count - self.col_count) else None,
            'left': lambda cell: cell.index - 1 if cell.index % self.col_count else None,
            'right': lambda cell: cell.index + 1 if
            cell.index % self.col_count < self.col_count - 1 else None,
            'up_left': lambda cell: cell.index - (self.col_count + 1) if
            self.get_next_cell(cell, 'up') and self.get_next_cell(cell, 'left') else None,
            'up_right': lambda cell: cell.index - (self.col_count - 1) if
            self.get_next_cell(cell, 'up') and self.get_next_cell(cell, 'right') else None,
            'down_left': lambda cell: cell.index + (self.col_count - 1) if
            self.get_next_cell(cell, 'down') and self.get_next_cell(cell, 'left') else None,
            'down_right': lambda cell: cell.index + (self.col_count + 1) if
            self.get_next_cell(cell, 'down') and self.get_next_cell(cell, 'right') else None,
        }[direction](cell)
        if cell_index is not None:
            return self.cells[cell_index]

    def reset_game(self):
        self.set_color_scheme()
        self.cells = []
        self.cols = [[] for x in range(self.col_count)]
        self.game_over = False
        self.whos_move = 0
        self.winner = None
        for row in range(self.row_count):
            for col in range(self.col_count):
                cell = Cell(row * self.col_count + col)
                self.cells.append(cell)
                self.cols[col].append(cell)
        self.draw_board()


class InARowStartCommand(sublime_plugin.WindowCommand):
    def run(self, rows=6, cols=7, target=4, players=2, view_id=None):
        window = sublime.active_window()
        view = None
        if view_id is not None:
            views = [x for x in window.views() if x.id() == view_id]
            if views:
                view = views[0]
        if view is None:
            view = window.new_file()

        if view.id() in IN_A_ROW_INSTANCES:
            in_a_row = IN_A_ROW_INSTANCES[view.id()]
            in_a_row.__init__(view, rows, cols, target, players)
        else:
            in_a_row = InARowGame(view, rows, cols, target, players)
            IN_A_ROW_INSTANCES[view.id()] = in_a_row


class InARowPromptCommand(sublime_plugin.WindowCommand):
    def run(self, rows=6, cols=7, target=4, players=2, view_id=None):
        self.view_id = view_id
        initial = '%s-%s-%s-%s' % (rows, cols, target, players)
        self.window.show_input_panel(
            'rows-cols[-target[-players]]', initial, self.on_done, None, None
        )

    def on_done(self, text):
        for separator in ['-', ' ', ',', '\t', ':']:
            bits = text.split(separator)
            if len(bits) == 2:
                bits.append(4)
            if len(bits) == 3:
                bits.append(2)
            if len(bits) == 4 and len([x for x in bits if x.isdigit()]) == 4:
                rows, cols, target, players = [int(x) for x in bits]
                self.window.run_command(
                    'in_aRow_start',
                    {
                        'rows': rows, 'cols': cols, 'target': target,
                        'players': players, 'view_id': self.view_id
                    }
                )
                break


class InARowListener(sublime_plugin.EventListener):
    def on_close(self, view):
        if view.id() in IN_A_ROW_INSTANCES:
            IN_A_ROW_INSTANCES[view.id()].view = None
            del IN_A_ROW_INSTANCES[view.id()]
