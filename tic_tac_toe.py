
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
TIC_TAC_TOE_INSTANCES = {}


class Cell:
    def __init__(self, index):
        self.index = index
        self.value = ' '


class TicTacToeGame(Game):
    def __init__(self, view=None):
        super(TicTacToeGame, self).__init__(view, settings={'name': 'Tic Tac Toe'})
        self.loaded = self.whos_move = None
        self.reset_game()

    def draw_board(self):
        self.loaded = False
        remove_event_handlers(self.view)
        if not self.game_over:
            data = '     %s\n\n' % self.whos_move
        else:
            data = ' Game Over \n\n'
        for row in range(3):
            for col in range(3):
                pre_length = len(data)
                data += ' ' + self.cells[row * 3 + col].value + ' '
                if not col == 2:
                    data += '|'
                else:
                    data += '\n'
                region = sublime.Region(pre_length, pre_length + 3)
                region.cell = self.cells[row * 3 + col]
                add_event_handler(self.view, region, lambda w, x, y, z: self.click_handler(y.cell))
            if row != 2:
                data += '---+---+---\n'

        pre_length = len(data)
        data += '\n   - | +   '
        if not self.game_over or self.winner is not None:
            region = sublime.Region(pre_length, pre_length + int((len(data) - pre_length) / 2))
            add_event_handler(self.view, region, lambda w, x, y, z: self.zoom(-10, True), None)
            region = sublime.Region(pre_length + int((len(data) - pre_length) / 2), len(data))
            add_event_handler(self.view, region, lambda w, x, y, z: self.zoom(+10, True), None)

        self.view.run_command(
            'utils_edit_view', {'data': data, 'start': 0, 'end': self.view.size()}
        )

        if self.game_over:
            region = sublime.Region(0, self.view.size())
            add_event_handler(self.view, region, lambda w, x, y, z: self.reset_game())
        self.loaded = True

    def click_handler(self, cell):
        if cell.value == ' ':
            cell.value = self.whos_move
        status = self.is_game_over()
        self.whos_move = 'X' if self.whos_move == 'O' else 'O'
        if not status == STATUS_PLAYING:
            self.whos_move = 'X' if self.whos_move == 'O' else 'O'
            self.set_color_scheme(background='#cccccc')
            self.game_over = True
            if status == STATUS_WINNER:
                self.winner = self.whos_move
        self.clear_selection()
        self.draw_board()

    def is_game_over(self):
        saw_white = False
        for direction, cell_indexes in [
            ['down', [0, 1, 2]],
            ['right', [0, 3, 6]],
            ['down_right', [0]],
            ['down_left', [2]]
        ]:
            for cell_index in cell_indexes:
                cell = self.cells[cell_index]
                if cell.value == ' ':
                    saw_white = True
                    continue
                if cell.value != self.whos_move:
                    continue
                while 1:
                    cell = self.get_next_cell(cell, direction)
                    if cell is None:
                        return STATUS_WINNER
                    if cell.value == ' ':
                        saw_white = True
                        break
                    if cell.value != self.whos_move:
                        break
        return STATUS_DRAW if saw_white is False else STATUS_PLAYING

    def get_next_cell(self, cell, direction):
        cell_index = {
            'down': lambda cell: cell.index + 3 if cell.index <= 5 else None,
            'left': lambda cell: cell.index - 1 if cell.index % 3 else None,
            'right': lambda cell: cell.index + 1 if cell.index % 3 < 2 else None,
            'down_left': lambda cell: cell.index + 2 if self.get_next_cell(cell, 'down') and
            self.get_next_cell(cell, 'left') else None,
            'down_right': lambda cell: cell.index + 4 if self.get_next_cell(cell, 'down') and
            self.get_next_cell(cell, 'right') else None,
        }[direction](cell)
        if cell_index is not None:
            return self.cells[cell_index]

    def reset_game(self):
        self.set_color_scheme()
        self.cells = [Cell(x) for x in range(9)]
        self.game_over = False
        self.whos_move = 'X'
        self.winner = None
        self.draw_board()


class TicTacToeStartCommand(sublime_plugin.WindowCommand):
    def run(self, view_id=None):
        window = sublime.active_window()
        view = None
        if view_id is not None:
            views = [x for x in window.views() if x.id() == view_id]
            if views:
                view = views[0]
        if view is None:
            view = window.new_file()

        if view.id() in TIC_TAC_TOE_INSTANCES:
            tic_tac_toe = TIC_TAC_TOE_INSTANCES[view.id()]
            tic_tac_toe.__init__(view)
        else:
            tic_tac_toe = TicTacToeGame(view)
            TIC_TAC_TOE_INSTANCES[view.id()] = tic_tac_toe


class TicTacToeListener(sublime_plugin.EventListener):
    def on_close(self, view):
        if view.id() in TIC_TAC_TOE_INSTANCES:
            TIC_TAC_TOE_INSTANCES[view.id()].view = None
            del TIC_TAC_TOE_INSTANCES[view.id()]
