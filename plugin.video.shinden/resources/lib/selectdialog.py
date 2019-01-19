# -*- coding: utf-8 -*-

'''
    Masterani Redux Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import sys

import pyxbmct.addonwindow as pyxbmct
import xbmcaddon
import xbmcgui

reload(sys)
sys.setdefaultencoding('UTF8')

_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo("path")
_check_icon = os.path.join(_path, "resources", "check.png")  # Don't decode _path to utf-8!!!

_white = "FFFFFFFF"
_yellow = "FFEB9E17"


class SelectDialog(pyxbmct.AddonDialogWindow):
    def __init__(self, title="", stype=None, sort=None, status=None, genre=None, genre_opt=None, callback=None):
        super(SelectDialog, self).__init__(title)
        self.setGeometry(900, 500, 15, 6)
        self.selected = []
        self.column_items = []
        self.set_controls()
        self.callback = callback
        self.typeids = stype
        self.type = [k for k, v in stype.iteritems()]
        # self.type = sorted(self.type)

        self.sortids = sort
        self.sort = [k for k, v in sort.iteritems()]
        self.sort = sorted(self.sort)

        self.genre_opt_ids = genre_opt
        self.genre_opt = [k for k, v in genre_opt.iteritems()]
        self.genre_opt = sorted(self.genre_opt)

        self.statusids = status
        self.status = [k for k, v in status.iteritems()]

        # self.genreids = {v: k for k, v in genre.iteritems()}
        self.genreids = dict((v, k) for k, v in genre.iteritems())

        self.genre = [v for k, v in genre.iteritems()]
        self.genre = sorted(self.genre)

        self.column_items.append([])
        self.set_column(0, 0, "Typ:", self.type or [])
        self.set_column(0, 8, "Sortowanie:", self.sort or [])

        self.cur_row = 0
        self.cur_col = 0

        self.column_items.append([])
        self.set_column(1, 0, "Status:", self.status or [])
        self.set_column(1, 6, "Opcje gatunkow:", self.genre_opt or [])
        # self.statuslisting.addItems(status or [])

        self.column_items.append([])
        self.set_column(2, 0, "Gatunek:", self.genre[0:(len(self.genre) / 3) - 1] or [])

        self.column_items.append([])
        self.set_column(3, 0, "", self.genre[(len(self.genre) / 3) - 1: ((len(self.genre) / 3) * 2) - 2] or [])

        self.column_items.append([])
        self.set_column(4, 0, "", self.genre[((len(self.genre) / 3) * 2) - 2: ((len(self.genre) / 3) * 3) - 3] or [])

        self.column_items.append([])
        self.set_column(5, 0, "", self.genre[((len(self.genre) / 3) * 3) - 3: len(self.genre)] or [])

        self.column_items[2].append(self.ok_button)
        self.column_items[3].append(self.cancel_button)

        self.check_uncheck(self.column_items[0][0])  # All
        self.check_uncheck(self.column_items[0][7])  # Score +
        self.check_uncheck(self.column_items[1][5])  # Score +
        self.check_uncheck(self.column_items[1][0])  # All
        self.cur_col = 2
        self.setFocus(self.column_items[self.cur_col][self.cur_row])

    def set_column(self, column=0, row_offset=0, header="", items=[]):
        if header is not "":
            typelabel = pyxbmct.Label(header, alignment=4)
            self.placeControl(typelabel, row_offset, column, rowspan=1, columnspan=1, pad_x=1, pad_y=1)
        # print items
        for i in range(0, len(items)):
            # btn = pyxbmct.Button(items[i], focusTexture="button-focus.png", noFocusTexture="button-nofocus.png")
            btn = pyxbmct.Button(items[i])
            self.placeControl(btn, i + 1 + row_offset, column, rowspan=1, columnspan=1, pad_x=1, pad_y=1)
            self.column_items[column].append(btn)

    def set_controls(self):
        # self.ok_button = pyxbmct.Button("OK", focusTexture="button-focus.png", noFocusTexture="button-nofocus.png")
        self.ok_button = pyxbmct.Button("Filtruj")
        self.placeControl(self.ok_button, 14, 2, columnspan=1, pad_x=1, pad_y=1)
        # self.cancel_button = pyxbmct.Button("Cancel", focusTexture="button-focus.png", noFocusTexture="button-nofocus.png")
        self.cancel_button = pyxbmct.Button("Anuluj")
        self.placeControl(self.cancel_button, 14, 3, columnspan=1, pad_x=1, pad_y=1)

    def check_uncheck(self, btn):
        # button = self.column_items[col][row]
        button = btn
        if button.getLabel() in self.ok_button.getLabel():
            self.ok()
            return
        if button.getLabel() in self.cancel_button.getLabel():
            self.close()
            return

        if button.getLabel() in self.sort:
            for i in range(7, 11):
                label = self.column_items[0][i].getLabel()
                self.column_items[0][i].setLabel(label, font="fontContextMenu", textColor=_white, focusedColor=_white)
                try:
                    self.selected.remove(label)
                except:
                    pass

        if button.getLabel() in self.genre_opt:
            for i in range(5, 7):
                label = self.column_items[1][i].getLabel()
                self.column_items[1][i].setLabel(label, font="fontContextMenu", textColor=_white,
                                                 focusedColor=_white)
                try:
                    self.selected.remove(label)
                except:
                    pass

            button.setLabel(button.getLabel(), font="fontContextMenu", textColor=_yellow, focusedColor=_yellow)
            self.selected.append(button.getLabel())
            return

        if button.getLabel() in self.status:
            for i in range(0, 5):
                label = self.column_items[1][i].getLabel()
                self.column_items[1][i].setLabel(label, font="fontContextMenu", textColor=_white, focusedColor=_white)
                try:
                    self.selected.remove(label)
                except:
                    pass

            button.setLabel(button.getLabel(), font="fontContextMenu", textColor=_yellow, focusedColor=_yellow)
            self.selected.append(button.getLabel())
            print self.selected
            return

        if button.getLabel() in self.type:
            for i in range(0, 5):
                label = self.column_items[0][i].getLabel()
                self.column_items[0][i].setLabel(label, font="fontContextMenu", textColor=_white, focusedColor=_white)
                try:
                    self.selected.remove(label)
                except:
                    pass

            button.setLabel(button.getLabel(), font="fontContextMenu", textColor=_yellow, focusedColor=_yellow)
            self.selected.append(button.getLabel())
            return

        if button.getLabel() in self.selected:
            button.setLabel(button.getLabel(), font="fontContextMenu", textColor=_white, focusedColor=_white)
            self.selected.remove(button.getLabel())
        else:
            button.setLabel(button.getLabel(), font="fontContextMenu", textColor=_yellow, focusedColor=_yellow)
            self.selected.append(button.getLabel())

    def ok(self):
        seltype = 0
        selsort = 0
        selstatus = ''
        selgenre = []
        selgenre_opt = []
        for item in self.selected:
            try:
                if item in self.type:
                    seltype = self.typeids[item]
                if item in self.sort:
                    selsort = self.sortids[item]
                if item in self.status:
                    selstatus = self.statusids[item]
                if item in self.genre:
                    selgenre.append(self.genreids[item])
                if item in self.genre_opt:
                    selgenre_opt.append(self.genre_opt_ids[item])
            except Exception as e:
                print(str(e))

        super(SelectDialog, self).close()
        self.callback(seltype, selsort, selstatus, selgenre, selgenre_opt)

    def close(self):
        self.selected = []
        super(SelectDialog, self).close()
        self.callback(0, 0, 0, 0, 0, 1)

    #
    def onAction(self, action):
        print action
        try:
            self.getFocus()
        except:
            self.setFocus(self.column_items[0][0])
        if action == xbmcgui.ACTION_PREVIOUS_MENU:
            self.close()
        if action == xbmcgui.ACTION_NAV_BACK:
            print "bobobob"
            self.close()
        if action == xbmcgui.ACTION_MOUSE_LEFT_CLICK:
            self.check_uncheck(self.getFocus())

        if action == xbmcgui.ACTION_SELECT_ITEM:
            self.check_uncheck(self.getFocus())

        if action == xbmcgui.ACTION_MOVE_LEFT:
            self.cur_col -= 1
            if self.cur_col < 0:
                self.cur_col = self.getColumns() - 1
            if self.cur_row >= len(self.column_items[self.cur_col]):
                self.cur_row = len(self.column_items[self.cur_col]) - 1
            self.setFocus(self.column_items[self.cur_col][self.cur_row])

        if action == xbmcgui.ACTION_MOVE_RIGHT:
            self.cur_col += 1
            if self.cur_col == self.getColumns():
                self.cur_col = 0
            if self.cur_row >= len(self.column_items[self.cur_col]):
                self.cur_row = len(self.column_items[self.cur_col]) - 1
            self.setFocus(self.column_items[self.cur_col][self.cur_row])

        if action == xbmcgui.ACTION_MOVE_DOWN:
            self.cur_row += 1
            if self.cur_row >= len(self.column_items[self.cur_col]):
                self.cur_row = 0
            self.setFocus(self.column_items[self.cur_col][self.cur_row])

        if action == xbmcgui.ACTION_MOVE_UP:
            self.cur_row -= 1
            if self.cur_row < 0:
                self.cur_row = len(self.column_items[self.cur_col]) - 1
            self.setFocus(self.column_items[self.cur_col][self.cur_row])
