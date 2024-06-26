#!/usr/bin/python
#
# This file is part of the SpectrumTranslate python module.
#
# It's licenced under GPL version 3 (www.gnu.org/licenses/gpl.html) with
# a few extra stipulations:
# 1) These first lines in this file as far as the line with the date
# needs to be left in so anyone who gets a copy of this file has access
# to the licence, extra stipulations, and disclaimors.
# 2) If this code is used as part of another project, I'd apreciate a
# mention in that project's documentation.
# 3) If you improve on any of the routines, I'd be most grateful if you
# would pass them back to me so that I can have the option to
# incorporate them into the origional module with apropriate attribution
# under this licence and stipulations.
#
# A copy of the licence and stipulations is bundled with the source
# files as licence.txt, or you can go to the GNU website for the terms
# of the GPL licence.
#
# If you try hard enough, I'm sure someone could damage something
# (software, data, system, hardware) useing it.  I've put a lot of time
# and effort into this software, and have removed any obvious bugs, but
# nothing is perfect.  If you spot any flaws, please let me know so that
# I might be able to fix them.  However I reserve the right not to fix
# flaws that I don't have the time, or resources to fix, or that I feel
# that fixing would detriment the software overall.  By useing this
# software you accept this, and any potential risk to your own hardware,
# software, data, and/or physical and mental health.  This software is
# provided "as is" and any express or implied warranties, including, but
# not limited to, the implied warranties of merchantability and fitness
# for a particular purpose are disclaimed.  In no event shall I or any
# contributors be liable for any direct, indirect, incidental, special,
# exemplary, or consequential damages (including, but not limited to,
# procurement of substitute goods or services; loss of use, data, or
# profits; or business interruption) however caused and on any theory of
# liability, whether in contract, strict liability, or tort (including
# negligence or otherwise) arising in any way out of the use of this
# software, even if advised of the possibility of such damage.  By using
# this software you agree to these terms.
#
# Author: william.fraser@virgin.net
# Date: 14th January 2015

import sys
import re
import os.path
import spectrumtape
import disciplefile
import spectrumtranslate
# Manage moveing of functions and renameing modules from PyQt4 to PyQt5
try:
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView
    except:
        from PyQt5.QtWebKitWidgets import QWebView
    from PyQt5 import QtCore
    from PyQt5.QtGui import (QColor, QStandardItemModel, QStandardItem,
                             QPainter, QFont, QPen, QCursor, QMovie)
    from PyQt5.QtCore import QItemSelectionModel
    import PyQt5.QtWidgets as QtGui
except ImportError:
    from PyQt4.QtWebKit import QWebView
    from PyQt4 import QtGui, QtCore
    from PyQt4.QtGui import (QColor, QStandardItemModel, QStandardItem,
                             QPainter, QFont, QPen, QItemSelectionModel,
                             QCursor, QMovie)
from operator import itemgetter, attrgetter


def _validbytestointlist(x):
    # function to convert any valid source to a list of ints
    if isinstance(x, (bytes, bytearray)):
        return [b for b in x]

    return x[:]

# open file modes
MODE_WB = 'wb'
MODE_RB = 'rb'
MODE_AB = 'ab'
MODE_WT = 'w'
MODE_RT = 'r'
MODE_AT = 'a'


def _setcombo(combo, text):
    combo.setCurrentIndex(combo.findText(text))


class SpectrumFileTranslateGUI(QtGui.QWidget):

    # nested class
    class StartStopDisplayPanel(QtGui.QWidget):
        def __init__(self, data, start, end, radiobutton, scroll):
            QtGui.QWidget.__init__(self)

            self.data = data
            self.selectStart = 0 if start == -1 else start
            self.selectEnd = len(self.data) if end == -1 else end + 1
            self.selectEnd = max(self.selectEnd, self.selectStart)
            self.radiobutton = radiobutton
            self.scroll = scroll

            self.topleftaddress = -1
            self.columns = -1
            self.rows = -1

            # set font and get text dimensions
            self.myfont = QFont('monospace', 10)
            self.setFont(self.myfont)
            self.cWidth = self.fontMetrics().width('0')
            self.cHeight = self.fontMetrics().height()
            self.baseline = self.fontMetrics().ascent()

            # hook up scrollbar
            scroll.valueChanged.connect(self.scrollChanged)

        def scrollChanged(self, pos):
            if self.topleftaddress != -1:
                self.topleftaddress = pos * self.columns

            # repaint display
            self.update()

        def paintEvent(self, event):
            qp = QPainter()
            qp.begin(self)

            # if topleft not set do so now
            if self.topleftaddress == -1:
                self.topleftaddress = (self.selectStart // self.columns) *\
                                        self.columns
                # update scrollbar
                self.resizeEvent(None)

            qp.setFont(self.myfont)

            # blank canvas
            qp.setBrush(QColor(255, 255, 255))
            qp.setPen(QPen(QtCore.Qt.NoPen))
            qp.drawRect(0, 0, self.width(), self.height())

            # Are we doing selection?
            # if so, is there selected area in screen? If so then
            # highlight it in grey
            if (self.radiobutton is not None and
                self.selectStart < self.topleftaddress + self.rows *
                self.columns and self.selectEnd > self.topleftaddress):
                # selection background to grey
                qp.setBrush(QColor(128, 128, 128))

                # work out first full row, and last row to be
                # highlighted
                rstart = (self.selectStart - self.topleftaddress +
                          self.columns - 1) // self.columns
                rstart = max(rstart, 0)

                rend = (self.selectEnd - self.topleftaddress + self.columns -
                        1) // self.columns
                rend = min(rend, self.rows)

                # do whole lines block
                x = (self.cWidth >> 1) + (self.cWidth * 10)
                qp.drawRect(x, rstart * self.cHeight,
                            ((self.columns * 3) - 1) * self.cWidth,
                            (rend - rstart) * self.cHeight)
                y = x + self.cWidth * (3 * self.columns + 1)
                qp.drawRect(y, rstart * self.cHeight,
                            self.columns * self.cWidth,
                            (rend - rstart) * self.cHeight)

                # do part first line
                i = (self.selectStart - self.topleftaddress) % self.columns
                # if any bytes before whole line, highlight them
                if i != 0:
                    qp.drawRect(x + (i * 3 * self.cWidth),
                                (rstart - 1) * self.cHeight,
                                (((self.columns - i) * 3) - 1) * self.cWidth,
                                self.cHeight)
                    qp.drawRect(y + (i * self.cWidth),
                                (rstart - 1) * self.cHeight,
                                (self.columns - i) * self.cWidth,
                                self.cHeight)

                # blank any unused blocks on last line if not needed
                i = (self.selectEnd - self.topleftaddress) % self.columns
                if (i != 0 and self.selectEnd < self.topleftaddress +
                   (self.rows * self.columns)):
                    qp.setBrush(QColor(255, 255, 255))
                    qp.drawRect(x + (((i * 3) - 1) * self.cWidth),
                                (rend - 1) * self.cHeight,
                                ((self.columns - i) * 3) * self.cWidth,
                                self.cHeight)
                    qp.drawRect(y + (i * self.cWidth),
                                (rend - 1) * self.cHeight,
                                (self.columns - i) * self.cWidth,
                                self.cHeight)

            # now display data in file
            qp.setPen(QColor(0, 0, 0))

            # set y to baseline
            y = self.baseline

            a = self.topleftaddress
            row = 0
            # draw each row of values
            while row < self.rows:
                # start off half a character in
                x = self.cWidth >> 1

                # print address
                qp.drawText(QtCore.QPointF(x, y), "{:08X}".format(a))

                # move past address
                x += self.cWidth * 10

                i = 0
                txt = ""
                # print each value and remember the character
                # representation
                while i < self.columns and a + i < len(self.data):
                    # print value at address
                    qp.drawText(QtCore.QPointF(x, y),
                                "{:02X}".format(self.data[a + i]))
                    x += self.cWidth * 3
                    # add character
                    d = self.data[a + i]
                    txt += chr(d) if (d >= 32 and d <= 127) else "."
                    i += 1

                x = (self.cWidth >> 1) + (self.cWidth * 10)
                x += self.cWidth * (3 * self.columns + 1)
                qp.drawText(QtCore.QPointF(x, y),
                            spectrumtranslate.getspectrumstring(txt))

                row += 1
                y += self.cHeight
                a += self.columns

            # draw lines between display areas
            qp.setPen(QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine))
            y = self.rows * self.cHeight
            x = (self.cWidth >> 1) + (self.cWidth * 9)
            qp.drawLine(x, 0, x, y)
            x += self.cWidth * (3 * self.columns + 1)
            qp.drawLine(x, 0, x, y)

            qp.end()

        def resizeEvent(self, event):
            # work out how many columns we can get in.  allow for 12
            # chars +4 per column (8 digit address, 2 width for between
            # address & bytes, and between bytes and characters. Also
            # half on left & right of canvas. Minus 1 for after last
            # byte) 4 per column is: 2 for byte, 1 for character, and 1
            # for between bytes

            i = self.width()
            # take away space for dividers & address
            i -= self.cWidth * 12
            # find out how many characters left
            i //= self.cWidth
            # divide by 4 to see how many columns will fit
            i >>= 2

            bChanged = (i != self.columns)
            self.columns = i

            i = self.height() // self.cHeight
            bChanged = bChanged or (self.rows != i)
            self.rows = i

            # if topleft not set do so now
            if self.topleftaddress == -1:
                self.topleftaddress = (self.selectStart // self.columns) * \
                                      self.columns

            # if has changed then update ascociated scrollbar
            if bChanged or event is None or not event:
                self.scroll.setValue(max(self.topleftaddress,
                                         0) // self.columns)
                self.scroll.setPageStep(self.rows)
                self.scroll.setRange(0, ((len(self.data) + self.columns -
                                         1) // self.columns) - self.rows)

        def mouseReleaseEvent(self, event):
            # Are we selecting or just displaying. If just Displaying
            # can ignore mouse events
            if self.radiobutton is None:
                return

            row = event.y() // self.cHeight
            # if to below last row of bytes then invalid place to click
            if row >= self.rows:
                return

            x = event.x() - ((self.cWidth * 10) + (self.cWidth >> 1))
            col = -1
            # if to left of bytes then invalid place to click
            if x < 0:
                return

            # see if not to right of bytes then should be valid click
            if x < self.cWidth * (3 * self.columns - 1):
                col = (x + (self.cWidth >> 1)) // self.cWidth
                col //= 3

            # move to start of character display
            x -= self.cWidth * (3 * self.columns + 1)
            if x >= 0 and x < self.columns * self.cWidth:
                col = x // self.cWidth

            # if not clicked on valid area, end
            if col == -1:
                return

            # calculate position clicked (end position is position after
            # last selected byte)
            pos = self.topleftaddress + (row * self.columns) + col
            if not self.radiobutton.isChecked():
                pos += 1

            # if beyond end of data then return
            if pos >= len(self.data) + (0 if self.radiobutton.isChecked() else
                                        1):
                return

            # now have valid position clicked
            # if start radiobutton selected then set start
            if self.radiobutton.isChecked():
                self.selectStart = pos
            # else set select end
            else:
                self.selectEnd = pos

            # ensure start not after end, or end before start
            if self.selectStart >= self.selectEnd:
                if self.radiobutton.isChecked():
                    self.selectEnd = self.selectStart + 1
                else:
                    self.selectStart = self.selectEnd - 1

            # repaint display
            self.update()

    class DisassemblerThread(QtCore.QThread):
        sFinished = QtCore.pyqtSignal()
        sStatus = QtCore.pyqtSignal()
        sAbort = QtCore.pyqtSignal()

        def __init__(self, main, data, origin):
            QtCore.QThread.__init__(self)
            self.sFinished.connect(main.DisassembleFinished)
            self.sStatus.connect(main.StatusUpdate)
            self.sAbort.connect(main.AbortDisassembly)
            self.main = main
            self.data = data
            self.origin = origin
            self.dContainer = main.progressdialog
            self.start()

        def run(self):
            # dissasemble the code
            try:
                self.dContainer.result = spectrumtranslate.disassemble(
                    self.data, 0, self.origin, len(self.data),
                    self.main.diInstructions, self.StatusUpdate)
                self.dContainer.error = None

            except spectrumtranslate.SpectrumTranslateError as ste:
                self.dContainer.error = ste.value
                self.dContainer.result = None

            self.sFinished.emit()

        def StatusUpdate(self, text, a1, a2, b1, b2):
            # pass on status update to main program
            self.dContainer.update = (text, a1, a2, b1, b2)
            self.sStatus.emit()

        def Stop(self):
            self.dContainer.result = None
            self.terminate()
            self.sAbort.emit()

    # end nested definitions

    def __init__(self, defaultFile=None):
        super(SpectrumFileTranslateGUI, self).__init__()

        self.diInstructions = [None]

        self.ExportSettings = {"Filename": "Export",
                               "AppendOrOver": 1,
                               "SaveWithHeader": 1,
                               "Flag": 0xFF,
                               "+DPos": 1,
                               "FilePosition": 0,
                               "ContainerType": 3,
                               "MakeTZXHeader": True}

        self.ImageFormatFallback = "Unknown"

        self.initUI(defaultFile)

    def initUI(self, defaultFile=None):
        self.setWindowTitle("Spectrum File Translate")

        QtGui.QToolTip.setFont(QFont('SansSerif', 10))

        bBrowse = QtGui.QPushButton("&Browse", self)
        bBrowse.clicked.connect(self.buttonPressed)
        bBrowse.setToolTip("Search for file to extract data from.")
        self.bBrowse = bBrowse
        bBrowseContainer = QtGui.QPushButton("Browse disk image", self)
        bBrowseContainer.setEnabled(False)
        self.bBrowseContainer = bBrowseContainer
        bBrowseContainer.clicked.connect(self.buttonPressed)
        bBrowseContainer.setToolTip(
            "Select Spectrum file to translate from container file.")
        bBrowseHex = QtGui.QPushButton("Browse Hex", self)
        bBrowseHex.setEnabled(False)
        self.bBrowseHex = bBrowseHex
        bBrowseHex.clicked.connect(self.buttonPressed)
        bBrowseHex.setToolTip(
            "Manually select start and last byte of file to translate.")
        bBrowseOut = QtGui.QPushButton("Browse", self)
        bBrowseOut.clicked.connect(self.buttonPressed)
        bBrowseOut.setToolTip("Select file to save translation in.")
        self.bBrowseOut = bBrowseOut
        bTranslate = QtGui.QPushButton("Translate", self)
        bTranslate.clicked.connect(self.buttonPressed)
        bTranslate.setToolTip("Translate selected data.")
        self.bTranslate = bTranslate
        lFileNameIn = QtGui.QLabel("Source File:")
        lDataOffset = QtGui.QLabel("Data Offset:")
        lDataEnd = QtGui.QLabel("Data End:")
        lDataFile = QtGui.QLabel("+D File Number:")
        lDataFileOffset = QtGui.QLabel("Offset in image file:")
        lDataType = QtGui.QLabel("Extract As:")
        lNumberFormat = QtGui.QLabel("Number Format:")
        lFileNameOut = QtGui.QLabel("Destination File:")
        leFileNameIn = QtGui.QLineEdit(self)
        self.leFileNameIn = leFileNameIn
        leFileNameIn.textChanged.connect(self.handle_changed_text)
        leFileNameIn.setToolTip("File to extract data from.")
        leDataOffset = QtGui.QLineEdit(self)
        leDataOffset.setToolTip(
            "Offset from file start to first byte of data to be translated.")
        self.leDataOffset = leDataOffset
        leDataEnd = QtGui.QLineEdit(self)
        leDataEnd.setToolTip(
            "Offset from file start to last byte of data to be translated.")
        self.leDataEnd = leDataEnd
        leDataFile = QtGui.QLineEdit(self)
        leDataFile.setMaxLength(2)
        leDataFile.setToolTip(
            "File number to extract in selected +D image file.")
        self.leDataFile = leDataFile
        leDataFileOffset = QtGui.QLineEdit(self)
        leDataFileOffset.setMaxLength(2)
        leDataFileOffset.setToolTip("Offset from start of selected +D image \
file from where to extract data.")
        self.leDataFileOffset = leDataFileOffset
        leFileNameOut = QtGui.QLineEdit(self)
        leFileNameOut.setToolTip("Filename of where to save translation.")
        self.leFileNameOut = leFileNameOut
        cbDataType = QtGui.QComboBox(self)
        cbDataType.addItem("Basic Program", 0)
        cbDataType.addItem("Machine Code", 1)
        cbDataType.addItem("Variable Array", 2)
        cbDataType.addItem("Screen", 3)
        cbDataType.addItem("Raw Data", 4)
        cbDataType.addItem("Snapshot", 5)
        # disable Snapshot option for now until snapshot is selected
        cbDataType.model().item(5).setEnabled(False)
        cbDataType.setToolTip("Specifies what to translate data as.")
        self.cbDataType = cbDataType
        _setcombo(cbDataType, "Basic Program")
        cbDataType.activated.connect(self.DataTypeChange)
        cbNumberFormat = QtGui.QComboBox(self)
        cbNumberFormat.addItem("Hexadecimal", 0)
        cbNumberFormat.addItem("Decimal", 1)
        cbNumberFormat.addItem("Octal", 2)
        cbNumberFormat.addItem("Binary", 3)
        cbNumberFormat.activated.connect(self.FormatChange)
        cbNumberFormat.setToolTip("Specifies number format for number fields \
(Data Offset,  Data End etc).")
        _setcombo(cbNumberFormat, "Hexadecimal")
        self.cbNumberFormat = cbNumberFormat
        self.CurrentNumberFormat = cbNumberFormat.currentIndex()
        self.cbNumberFormat = cbNumberFormat
        cbViewOutput = QtGui.QCheckBox("View Output", self)
        cbViewOutput.toggle()
        cbViewOutput.setToolTip(
            "Select if you want to see translated text after translation.")
        self.cbViewOutput = cbViewOutput
        cbSaveOutput = QtGui.QCheckBox("Save Output", self)
        cbSaveOutput.toggle()
        cbSaveOutput.setToolTip(
            "Select if you want to save translated text after translation.")
        self.cbSaveOutput = cbSaveOutput
        cbExportToContainer = QtGui.QCheckBox("Export file to Container", self)
        cbExportToContainer.toggle()
        cbExportToContainer.setCheckState(False)
        cbExportToContainer.setToolTip(
            "Select if you want to export the selected file to a tap file.")
        self.cbExportToContainer = cbExportToContainer
        cbExportToContainer.stateChanged.connect(self.ExportToContainerChanged)
        bExportSettings = QtGui.QPushButton("Export Settings", self)
        bExportSettings.setToolTip("Edit the Export options.")
        bExportSettings.clicked.connect(self.EditExportSettings)
        bExportSettings.setEnabled(False)
        self.bExportSettings = bExportSettings

        # set out widgets
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        hbox.addWidget(lFileNameIn)
        leFileNameIn.sizePolicy().setHorizontalPolicy(
            QtGui.QSizePolicy.Expanding)
        leFileNameIn.sizePolicy().setHorizontalStretch(1)
        hbox.addWidget(leFileNameIn)
        hbox.addWidget(bBrowse)

        grid.addLayout(hbox, 0, 0, 1, 3)

        grid.addWidget(bBrowseContainer, 0, 3)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lDataOffset.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(lDataOffset)
        leDataOffset.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        hbox.addWidget(leDataOffset)
        hbox.addStretch(1)
        grid.addLayout(hbox, 1, 0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lDataEnd.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(lDataEnd)
        leDataEnd.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        hbox.addWidget(leDataEnd)
        hbox.addStretch(1)
        grid.addLayout(hbox, 1, 1)

        grid.addWidget(bBrowseHex, 1, 3)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lDataFile.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(lDataFile)
        leDataFile.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        hbox.addWidget(leDataFile)
        hbox.addStretch(1)
        grid.addLayout(hbox, 2, 0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lDataFile.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(lDataFileOffset)
        leDataFile.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        hbox.addWidget(leDataFileOffset)
        hbox.addStretch(1)
        grid.addLayout(hbox, 2, 1)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lDataType.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(lDataType)
        hbox.addWidget(cbDataType)
        hbox.addStretch(1)

        lNumberFormat.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(lNumberFormat)
        hbox.addWidget(cbNumberFormat)

        grid.addLayout(hbox, 3, 0, 1, 3)

        stack = QtGui.QStackedWidget()

        # panel to hold Basic program variables
        gbBasic = QtGui.QGroupBox("Basic Program", self)
        gbBasic.setStyleSheet("""QGroupBox { border: 1px solid gray; \
                                             border-radius: 3px; \
                                             margin-top: 0.5em; \
                                             font-weight: bold; }
                                 QGroupBox::title { subcontrol-origin: margin;\
                                                    left: 10px; \
                                                    padding: 0 3px 0 3px; }""")
        grid2 = QtGui.QGridLayout()
        grid2.setSpacing(10)

        lBasicAutoLine = QtGui.QLabel("Autostart Line:")
        lBasicVariableOffset = QtGui.QLabel("Variable Offset:")
        leBasicAutoLine = QtGui.QLineEdit(self)
        leBasicAutoLine.setToolTip(
            "Specifies line for auto start of BASIC program.")
        self.leBasicAutoLine = leBasicAutoLine
        leBasicVariableOffset = QtGui.QLineEdit(self)
        leBasicVariableOffset.setToolTip("Specifies offset to variables BASIC \
program. Leave blank if not sure.")
        self.leBasicVariableOffset = leBasicVariableOffset
        cbXMLBasicOutput = QtGui.QCheckBox("XML output")
        cbXMLBasicOutput.setToolTip("Do you want output as text, or as XML.")
        cbXMLBasicOutput.toggle()
        cbXMLBasicOutput.setCheckState(False)
        self.cbXMLBasicOutput = cbXMLBasicOutput

        cbASCIIBasicOutput = QtGui.QCheckBox("ASCII only output")
        cbASCIIBasicOutput.setToolTip("Some spectrum characters like the \
copyright symbol aren't ASCII compliant.\nUse this option to output such \
characters as a '^' followed by it's 2 digit hexadecimal value.")
        cbASCIIBasicOutput.toggle()
        cbASCIIBasicOutput.setCheckState(False)
        self.cbASCIIBasicOutput = cbASCIIBasicOutput

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lBasicAutoLine.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(lBasicAutoLine)
        leBasicAutoLine.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        hbox.addWidget(leBasicAutoLine)
        hbox.addStretch(1)
        grid2.addLayout(hbox, 0, 0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lBasicVariableOffset.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(lBasicVariableOffset)
        leBasicVariableOffset.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        hbox.addWidget(leBasicVariableOffset)
        hbox.addStretch(1)
        grid2.addLayout(hbox, 0, 1)

        grid2.addWidget(cbXMLBasicOutput, 1, 0)
        grid2.addWidget(cbASCIIBasicOutput, 1, 1)

        grid2.setRowStretch(2, 1)

        gbBasic.setLayout(grid2)

        stack.addWidget(gbBasic)

        # panel to hold machine code variables
        gbCode = QtGui.QGroupBox("Machine Code", self)
        gbCode.setStyleSheet("""QGroupBox { border: 1px solid gray; \
                                            border-radius: 3px; \
                                            margin-top: 0.5em; \
                                            font-weight: bold; }
                                QGroupBox::title { subcontrol-origin: margin;\
                                                   left: 10px; \
                                                   padding: 0 3px 0 3px; }""")

        grid2 = QtGui.QGridLayout()
        grid2.setSpacing(5)

        lCodeOrigin = QtGui.QLabel("Origin:")
        lCodeFormat = QtGui.QLabel("Output Format:")
        lCodeTimes = QtGui.QLabel("List Timings:")
        lCodeJump = QtGui.QLabel("Gap After Jump/Ret:")
        leCodeOrigin = QtGui.QLineEdit(self)
        leCodeOrigin.setToolTip(
            "The memory address of the first byte of the data.")
        self.leCodeOrigin = leCodeOrigin
        cbCodeFormat = QtGui.QComboBox(self)
        cbCodeFormat.addItem("Hexadecimal", 0)
        cbCodeFormat.addItem("Decimal", 1)
        cbCodeFormat.addItem("Octal", 2)
        cbCodeFormat.addItem("Binary", 3)
        _setcombo(cbCodeFormat, "Hexadecimal")
        cbCodeFormat.setToolTip(
            "The data format for numbers in the translated code.")
        self.cbCodeFormat = cbCodeFormat
        cbCodeTimes = QtGui.QComboBox(self)
        cbCodeTimes.addItem("None", 0)
        cbCodeTimes.addItem("T states", 1)
        cbCodeTimes.addItem("Cycles", 2)
        cbCodeTimes.addItem("All", 3)
        _setcombo(cbCodeTimes, "None")
        cbCodeTimes.setToolTip(
            "What instruction timeing details do you want listed?")
        self.cbCodeTimes = cbCodeTimes
        cbCodeJump = QtGui.QComboBox(self)
        cbCodeJump.addItem("None", 0)
        cbCodeJump.addItem("After absolute", 1)
        cbCodeJump.addItem("All", 2)
        _setcombo(cbCodeJump, "After absolute")
        cbCodeJump.setToolTip("Do you want a blank line for readability after \
absolute jumps, none or all.")
        self.cbCodeJump = cbCodeJump
        cbCodeFlags = QtGui.QCheckBox("List Flags")
        cbCodeFlags.setToolTip("List flags affected by machine instructions.")
        cbCodeFlags.toggle()
        cbCodeFlags.setCheckState(False)
        self.cbCodeFlags = cbCodeFlags
        cbCodeUndocumented = QtGui.QCheckBox("Mark Undocumented")
        cbCodeUndocumented.setToolTip(
            "Note undocumented machine instructions.")
        cbCodeUndocumented.toggle()
        cbCodeUndocumented.setCheckState(False)
        self.cbCodeUndocumented = cbCodeUndocumented
        cbXMLOutput = QtGui.QCheckBox("XML output")
        cbXMLOutput.setToolTip(
            "Do you want output as text formatted by spacers, or as XML.")
        cbXMLOutput.toggle()
        cbXMLOutput.setCheckState(False)
        self.cbXMLOutput = cbXMLOutput
        bCustomInstructions = QtGui.QPushButton("Custom Instructions", self)
        bCustomInstructions.setToolTip("Edit Custom Disassemble Instructions.")
        bCustomInstructions.clicked.connect(self.buttonPressed)
        self.bCustomInstructions = bCustomInstructions

        grid2.addWidget(lCodeOrigin, 0, 0)
        grid2.addWidget(leCodeOrigin, 0, 1)
        lCodeOrigin.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid2.addWidget(cbCodeFlags, 0, 3)

        grid2.addWidget(lCodeFormat, 1, 0)
        grid2.addWidget(cbCodeFormat, 1, 1)
        lCodeFormat.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid2.addWidget(cbCodeUndocumented, 1, 3)

        grid2.addWidget(lCodeTimes, 2, 0)
        grid2.addWidget(cbCodeTimes, 2, 1)
        lCodeTimes.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid2.addWidget(cbXMLOutput, 2, 3)

        grid2.addWidget(lCodeJump, 3, 0)
        grid2.addWidget(cbCodeJump, 3, 1)
        lCodeJump.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid2.addWidget(bCustomInstructions, 3, 3)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        grid2.addLayout(hbox, 2, 0)
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        grid2.addLayout(hbox, 4, 0)
        grid2.setColumnStretch(2, 1)
        grid2.setColumnStretch(4, 1)

        gbCode.setLayout(grid2)

        stack.addWidget(gbCode)

        # panel to hold array variables
        gbVars = QtGui.QGroupBox("Variable Array", self)
        gbVars.setStyleSheet("""QGroupBox { border: 1px solid gray; \
                                            border-radius: 3px; \
                                            margin-top: 0.5em; \
                                            font-weight: bold; }
                                QGroupBox::title { subcontrol-origin: margin;\
                                                   left: 10px; \
                                                   padding: 0 3px 0 3px; }""")

        grid2 = QtGui.QGridLayout()
        grid2.setSpacing(10)

        lArrayVarName = QtGui.QLabel("Variable Name:")
        lArrayVarType = QtGui.QLabel("Variable Type:")
        leArrayVarName = QtGui.QLineEdit(self)
        leArrayVarName.setMaxLength(20)
        leArrayVarName.setToolTip(
            "The letter name of the variable to translate.")
        self.leArrayVarName = leArrayVarName
        cbArrayVarType = QtGui.QComboBox(self)
        cbArrayVarType.addItem("Number Array", 0)
        cbArrayVarType.addItem("Character Array", 1)
        cbArrayVarType.addItem("String", 2)
        cbArrayVarType.setToolTip("The variable type to translate.")
        self.cbArrayVarType = cbArrayVarType
        _setcombo(cbArrayVarType, "String")
        cbXMLVarOutput = QtGui.QCheckBox("XML output")
        cbXMLVarOutput.setToolTip("Do you want output as text, or as XML.")
        cbXMLVarOutput.toggle()
        cbXMLVarOutput.setCheckState(False)
        self.cbXMLVarOutput = cbXMLVarOutput
        cbASCIIVarOutput = QtGui.QCheckBox("ASCII only output")
        cbASCIIVarOutput.setToolTip("Some spectrum characters like the \
copyright symbol aren't ASCII compliant.\nUse this option to output such \
characters as a '^' followed by it's 2 digit hexadecimal value.")
        cbASCIIVarOutput.toggle()
        cbASCIIVarOutput.setCheckState(False)
        self.cbASCIIVarOutput = cbASCIIVarOutput

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lArrayVarName.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(lArrayVarName)
        leArrayVarName.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        hbox.addWidget(leArrayVarName)
        hbox.addStretch(1)
        grid2.addLayout(hbox, 0, 0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lArrayVarType.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(lArrayVarType)
        hbox.addWidget(cbArrayVarType)
        hbox.addStretch(1)
        grid2.addLayout(hbox, 0, 1)

        grid2.addWidget(cbXMLVarOutput, 1, 0)
        grid2.addWidget(cbASCIIVarOutput, 1, 1)

        grid2.setRowStretch(2, 1)

        gbVars.setLayout(grid2)

        stack.addWidget(gbVars)

        # panel to hold image variables
        gbImage = QtGui.QGroupBox("Screen", self)
        gbImage.setStyleSheet("""QGroupBox { border: 1px solid gray; \
                                             border-radius: 3px; \
                                             margin-top: 0.5em; \
                                             font-weight: bold; }
                                 QGroupBox::title { subcontrol-origin: margin;\
                                                    left: 10px; \
                                                    padding: 0 3px 0 3px; }""")

        grid2 = QtGui.QGridLayout()
        grid2.setSpacing(10)

        cbImageFlash = QtGui.QCheckBox("Extract Flashing colours (will need \
to be saved as animated gif file)")
        cbImageFlash.toggle()
        cbImageFlash.setToolTip("Extract data as an animated GIF file to \
display flashing colours, or simple GIF file.")
        self.cbImageFlash = cbImageFlash
        lImageDelay = QtGui.QLabel("Flash delay in miliseconds:")
        leImageDelay = QtGui.QLineEdit("320")
        leImageDelay.setToolTip(
            "The time delay between flash states in milliseconds.")
        self.leImageDelay = leImageDelay

        grid2.addWidget(cbImageFlash, 0, 0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lImageDelay.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(lImageDelay)
        leImageDelay.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        hbox.addWidget(leImageDelay)
        hbox.addStretch(1)
        grid2.addLayout(hbox, 1, 0)

        grid2.setRowStretch(2, 1)

        gbImage.setLayout(grid2)

        stack.addWidget(gbImage)

        # panel to indicate raw data
        gbRaw = QtGui.QGroupBox("Raw Data", self)
        gbRaw.setStyleSheet("""QGroupBox { border: 1px solid gray; \
                                           border-radius: 3px; \
                                           margin-top: 0.5em; \
                                           font-weight: bold; }
                               QGroupBox::title { subcontrol-origin: margin; \
                                                  left: 10px; \
                                                  padding: 0 3px 0 3px; }""")
        stack.addWidget(gbRaw)

        # panel to hold snapshot variables
        gbSnap = QtGui.QGroupBox("Snapshot", self)
        gbSnap.setStyleSheet("""QGroupBox { border: 1px solid gray; \
                                            border-radius: 3px; \
                                            margin-top: 0.5em; \
                                            font-weight: bold; }
                                QGroupBox::title { subcontrol-origin: margin; \
                                                   left: 10px; \
                                                   padding: 0 3px 0 3px; }""")
        self.gbSnap = gbSnap

        grid2 = QtGui.QGridLayout()
        grid2.setSpacing(10)

        lSnapshotOutput = QtGui.QLabel("Convert to what format:")

        cbSnapshotOutput = QtGui.QComboBox(self)
        cbSnapshotOutput.addItem(".SNA", 0)
        cbSnapshotOutput.addItem(".Z80 (version 1)", 1)
        cbSnapshotOutput.addItem(".Z80 (version 2)", 2)
        cbSnapshotOutput.addItem(".Z80 (version 3)", 3)
        cbSnapshotOutput.setToolTip(
            "What type of snapshot would you like to save as.")
        self.cbSnapshotOutput = cbSnapshotOutput

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lSnapshotOutput.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(lSnapshotOutput)
        hbox.addWidget(cbSnapshotOutput)
        hbox.addStretch(1)
        grid2.addLayout(hbox, 0, 0)

        grid2.setRowStretch(1, 1)

        gbSnap.setLayout(grid2)

        stack.addWidget(gbSnap)

        self.settingsstack = stack

        # layout after processing options
        grid.addWidget(stack, 4, 0, 1, 4)
        grid.setRowStretch(3, 1)

        grid.addWidget(cbViewOutput, 5, 0)
        grid.addWidget(cbSaveOutput, 6, 0)

        grid.addWidget(cbExportToContainer, 5, 1)
        grid.addWidget(bExportSettings, 5, 2)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        hbox.addWidget(lFileNameOut)
        leFileNameOut.sizePolicy().setHorizontalPolicy(
            QtGui.QSizePolicy.Expanding)
        leFileNameOut.sizePolicy().setHorizontalStretch(1)
        hbox.addWidget(leFileNameOut)
        hbox.addWidget(bBrowseOut)
        grid.addLayout(hbox, 6, 1, 1, 3)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(bTranslate)
        hbox.addStretch(1)
        grid.addLayout(hbox, 7, 0, 1, 4)

        self.setLayout(grid)

        self.setGeometry(0, 0, 600, 300)
        self.adjustSize()
        self.show()

        if defaultFile is not None:
            leFileNameIn.setText(defaultFile)

        self.CheckIfKnownContainerFile()

    def buttonPressed(self):
        button = self.sender()
        # browse to find input file
        if button == self.bBrowse:
            filein = self.leFileNameIn.text()
            # create open file dialog with current file if exists as
            # selected file
            qfd = QtGui.QFileDialog(self, "Select source file",
                                    filein if os.path.isfile(filein) else "")
            if os.path.isfile(filein):
                qfd.selectFile(filein)

            qfd.setFileMode(QtGui.QFileDialog.AnyFile)
            qfd.setAcceptMode(QtGui.QFileDialog.AcceptOpen)

            # run dialog and if open is clicked then act on this
            if qfd.exec_() == QtGui.QDialog.Accepted:
                newfile = qfd.selectedFiles()[0]
                self.leFileNameIn.setText(newfile)
                self.CheckIfKnownContainerFile()
                # set start and finish translate to start & end of file
                # if changed
                if filein != newfile:
                    self.leDataOffset.setText("")
                    self.leDataEnd.setText("")
                    self.leDataFile.setText("")
                    self.leDataFileOffset.setText("")
                    if os.path.isfile(newfile):
                        self.leDataOffset.setText("0")
                        self.leDataEnd.setText(
                            self.FormatNumber(os.path.getsize(newfile) - 1))

            return

        # browse to find output file
        if button == self.bBrowseOut:
            fileout = self.leFileNameOut.text()
            # create save file dialog with current file if exists as
            # selected file
            qfd = QtGui.QFileDialog(self, "Select output file",
                                    fileout if os.path.isfile(fileout) else "")
            qfd.setFileMode(QtGui.QFileDialog.AnyFile)
            qfd.setAcceptMode(QtGui.QFileDialog.AcceptSave)
            qfd.selectFile(fileout)

            # run dialog and if save is clicked then act on this
            if qfd.exec_() == QtGui.QDialog.Accepted:
                newfile = qfd.selectedFiles()[0]
                self.leFileNameOut.setText(newfile)

            return

        # browse container file
        if button == self.bBrowseContainer:
            if self.bBrowseContainer.text() in ["Browse TAP", "Browse TZX"]:
                self.BrowseTapeFile()

            if self.bBrowseContainer.text() == "Browse disk image":
                self.BrowseDiscipleImageFile()

            return

        # browse container file
        if button == self.bBrowseHex:
            self.BrowseFileHex()
            return

        # Do Translation
        if button == self.bTranslate:
            self.Translate()
            return

        # handle machine code Custom Instructions
        if button == self.bCustomInstructions:
            self.EditCustomDisassembleCommands()
            return

    def EditCustomDisassembleCommands(self):
        # create dialog
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Disassemble Custom Commands")
        dContainer.setModal(True)
        self.Ddialog = dContainer

        grid = QtGui.QGridLayout()
        grid.setSpacing(2)

        bload = QtGui.QPushButton("Load Instructions", self)
        bload.setToolTip(
            "Load a previously saved set of instructions from a file.")
        grid.addWidget(bload, 0, 0, 1, 2)
        bload.clicked.connect(self.CustomDisassembleLoad)
        dContainer.bload = bload

        bsave = QtGui.QPushButton("Save Instructions", self)
        bsave.setToolTip("Save instructions currently in editor to a file.")
        grid.addWidget(bsave, 1, 0, 1, 2)
        bsave.clicked.connect(self.CustomDisassembleSave)
        dContainer.bsave = bsave

        bdelete = QtGui.QPushButton("Delete Instruction", self)
        bdelete.setToolTip("Delete currently selected instruction.")
        grid.addWidget(bdelete, 2, 0, 1, 2)
        bdelete.clicked.connect(self.CustomDisassembleDelete)
        dContainer.bdelete = bdelete

        bnew = QtGui.QPushButton("New Instruction", self)
        bnew.setToolTip("Add new instruction to end of list.")
        grid.addWidget(bnew, 3, 0, 1, 2)
        bnew.clicked.connect(self.CustomDisassembleNew)
        dContainer.bnew = bnew

        lay = QtGui.QHBoxLayout()
        bup = QtGui.QPushButton("Move Up", self)
        bup.setToolTip("Move curently selected instruction up a line.")
        lay.addWidget(bup)
        bup.clicked.connect(self.CustomDisassembleUp)
        dContainer.bup = bup

        bdown = QtGui.QPushButton("Move Down", self)
        bdown.setToolTip("Move curently selected instruction down a line.")
        lay.addWidget(bdown)
        bdown.clicked.connect(self.CustomDisassembleDown)
        dContainer.bdown = bdown
        grid.addLayout(lay, 4, 0, 1, 2)

        bsort = QtGui.QPushButton("Sort Instructions", self)
        bsort.setToolTip("Sorts instructions to the order in which they will \
be processed.")
        grid.addWidget(bsort, 5, 0, 1, 2)
        bsort.clicked.connect(self.CustomDisassembleSort)
        dContainer.bsort = bsort

        cbNumberFormat = QtGui.QComboBox(self)
        cbNumberFormat.addItem("Hexadecimal", 0)
        cbNumberFormat.addItem("Decimal", 1)
        cbNumberFormat.addItem("Octal", 2)
        cbNumberFormat.addItem("Binary", 3)
        cbNumberFormat.activated[int].connect(
            self.DissassembleEditorFormatChange)
        cbNumberFormat.setToolTip("Specifies number format for number fields \
(Data Offset, Data End etc).")
        _setcombo(cbNumberFormat, "Hexadecimal")
        dContainer.cbNumberFormat = cbNumberFormat
        dContainer.Format = '{:X}'
        dContainer.FormatBase = 16
        grid.addWidget(cbNumberFormat, 6, 0, 1, 2)

        cbDisassembleCommands = QtGui.QComboBox(self)
        for key, value in sorted(list(spectrumtranslate.DisassembleInstruction.
                                 DISASSEMBLE_CODES.items()),
                                 key=itemgetter(1)):
            cbDisassembleCommands.addItem(key, value)

        cbDisassembleCommands.setToolTip(
            "Select what you want this instruction to do.")
        cbDisassembleCommands.currentIndexChanged[str].connect(
            self.ChangeDissassembleCommand)
        dContainer.cbDisassembleCommands = cbDisassembleCommands
        grid.addWidget(cbDisassembleCommands, 7, 0, 1, 2)

        lab = QtGui.QLabel("Start:")
        lab.setToolTip(
            "Select the first address you want instruction to apply from.")
        grid.addWidget(lab, 8, 0, 1, 1)

        leStart = QtGui.QLineEdit()
        leStart.setMaxLength(16)
        leStart.setToolTip(
            "Select the first address you want instruction to apply from.")
        leStart.textChanged.connect(self.ChangeDissassembleStart)
        leStart.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        leStart.sizePolicy().setHorizontalStretch(1)
        dContainer.leStart = leStart
        grid.addWidget(leStart, 8, 1, 1, 1)

        lab = QtGui.QLabel("End:")
        lab.setToolTip(
            "Select the last address you want instruction to apply to.")
        grid.addWidget(lab, 9, 0, 1, 1)

        leEnd = QtGui.QLineEdit()
        leEnd.setMaxLength(16)
        leEnd.setToolTip(
            "Select the last address you want instruction to apply to.")
        leEnd.textChanged.connect(self.ChangeDissassembleEnd)
        leEnd.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        leEnd.sizePolicy().setHorizontalStretch(1)
        dContainer.leEnd = leEnd
        grid.addWidget(leEnd, 9, 1, 1, 1)

        bedit = QtGui.QPushButton("Edit data", self)
        bedit.setToolTip("Edit aditional data for the instruction.")
        grid.addWidget(bedit, 10, 0, 1, 2)
        bedit.clicked.connect(self.CustomDisassembleEdit)
        dContainer.bedit = bedit

        lwInstructions = QtGui.QListWidget(self)
        lwInstructions.setToolTip(
            "List of Disassemble instructions to carry out on the code.")
        # only list instructions if have more than basic format setter
        if len(self.diInstructions) > 1:
            for di in self.diInstructions[1:]:
                item = QtGui.QListWidgetItem("\n")
                lwInstructions.addItem(item)
                lab = QtGui.QLabel()
                lab.setIndent(5)
                lab.setFrameShape(QtGui.QFrame.Box)
                item.label = lab
                item.di = spectrumtranslate.DisassembleInstruction(di)
                self.setLabelText(item)
                lwInstructions.setItemWidget(item, lab)

        lwInstructions.clicked.connect(self.SetDisassembleDialogButtons)
        lwInstructions.itemPressed.connect(self.SetDisassembleDialogButtons)
        lwInstructions.currentItemChanged.connect(
            self.instructionselectionchanged)
        dContainer.lwInstructions = lwInstructions
        if len(self.diInstructions) > 1:
            lwInstructions.setCurrentRow(0)
            self.SetDisassembleDialogButtons()

        grid.addWidget(lwInstructions, 0, 2, 12, 1)

        lay = QtGui.QHBoxLayout()
        ok = QtGui.QPushButton("Ok", self)
        lay.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close = QtGui.QPushButton("Cancel", self)
        lay.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay.addStretch(1)
        helpbutton = QtGui.QPushButton("Help", self)
        helpbutton.setToolTip(
            "Displays information about Disassemble Instructions.")
        lay.addWidget(helpbutton)
        helpbutton.clicked.connect(self.DisplayInstructionsHelp)

        grid.addLayout(lay, 12, 0, 2, 0)

        grid.setRowStretch(11, 1)
        grid.setColumnStretch(2, 1)

        dContainer.setLayout(grid)

        # set to same size as parent
        dContainer.setGeometry(self.geometry())

        # set button state
        self.SetDisassembleDialogButtons()

        # run dialog, and if ok selected get start & stop points
        if dContainer.exec_() == QtGui.QDialog.Accepted:
            self.diInstructions = [None] + [lwInstructions.item(i).di for i in
                                            range(lwInstructions.count())]

        del self.Ddialog

    def CustomDisassembleSort(self):
        lwInstructions = self.Ddialog.lwInstructions
        # can't sort if no instructions
        if lwInstructions.count() == 0:
            return

        # get current instructions
        diInstructions = [lwInstructions.item(i).di for i in
                          range(lwInstructions.count())]

        # make note of which one was selected in way that will survive
        # sorting
        for i in range(len(diInstructions)):
            diInstructions[i].Selected = False

        diInstructions[lwInstructions.currentRow()].Selected = True

        # now sort them
        diInstructions = sorted(diInstructions, key=attrgetter('start', 'end'))

        # find selected index
        for i in range(len(diInstructions)):
            if diInstructions[i].Selected:
                selected = i

        # clear listwidget
        lwInstructions.clear()
        # put them back in listwidget
        for di in diInstructions:
            item = QtGui.QListWidgetItem("\n")
            lwInstructions.addItem(item)
            lab = QtGui.QLabel()
            lab.setIndent(5)
            lab.setFrameShape(QtGui.QFrame.Box)
            item.label = lab
            item.di = spectrumtranslate.DisassembleInstruction(di)
            self.setLabelText(item)
            lwInstructions.setItemWidget(item, lab)

        lwInstructions.setCurrentRow(selected)
        self.SetDisassembleDialogButtons()

    def DisplayInstructionsHelp(self):
        # create dialog
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Disassemble Instructions Help")
        dContainer.setModal(True)

        lay = QtGui.QVBoxLayout()

        view = QWebView(self)
        lay.addWidget(view)
        with open("DisassembleInstructionHelp.html", MODE_RT) as fi:
            html = fi.read()
        view.setHtml(html)

        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        lay2.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        back = QtGui.QPushButton("back", self)
        lay2.addWidget(back)
        back.clicked.connect(view.back)
        foreward = QtGui.QPushButton("foreward", self)
        lay2.addWidget(foreward)
        foreward.clicked.connect(view.forward)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        # set to same size as parent
        dContainer.setGeometry(self.geometry())

        # run dialog
        dContainer.exec_()

    def CustomDisassembleEdit(self):
        lwInstructions = self.Ddialog.lwInstructions
        di = lwInstructions.currentItem().di

        if di.instruction == spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Line Number Every X"]:
            self.EditUnreferencedLineNumberFrequency(di)

        if di.instruction == spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Custom Format"]:
            self.EditCustomFormatDialog(di)
            # don't need to set label text
            return

        if di.instruction == spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Data Block"]:
            self.EditDataBlock(di)

        if di.instruction == spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Pattern Data Block"]:
            self.EditPatternDataBlock(di)

        if di.instruction in [spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Comment"],
           spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Comment Before"],
           spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Comment After"]]:
            self.EditComment(di)

        if di.instruction & 0xFFFF00 == spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Comment Reference"]:
            self.EditCommentReference(di)

        if di.instruction & 0xFFFF00 == spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Comment Displacement"]:
            self.EditCommentDisplacement(di)

        if di.instruction == spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Comment Pattern"]:
            self.EditCommentPattern(di)

        # ensure any data change is represented in list details
        self.setLabelText(lwInstructions.currentItem())

    def EditComment(self, di):
        # create dialog
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Comment")
        dContainer.setModal(True)

        lay = QtGui.QVBoxLayout()

        lay.addWidget(QtGui.QLabel("Comment Text:"))

        leCommentText = QtGui.QLineEdit()
        if di.data:
            leCommentText.setText(di.data)
        leCommentText.setToolTip("The text to be added as the comment.")
        leCommentText.sizePolicy().setHorizontalPolicy(
            QtGui.QSizePolicy.Expanding)
        leCommentText.sizePolicy().setHorizontalStretch(1)
        lay.addWidget(leCommentText)

        cbPosition = QtGui.QComboBox(self)
        cbPosition.addItem("Comment End of line",
                           spectrumtranslate.DisassembleInstruction.
                           DISASSEMBLE_CODES["Comment"])
        cbPosition.addItem("Comment Before line",
                           spectrumtranslate.DisassembleInstruction.
                           DISASSEMBLE_CODES["Comment Before"])
        cbPosition.addItem("Comment After line",
                           spectrumtranslate.DisassembleInstruction.
                           DISASSEMBLE_CODES["Comment After"])
        cbPosition.setToolTip("Where the comment is placed.")
        cbPosition.setCurrentIndex(cbPosition.findData(di.instruction))
        lay.addWidget(cbPosition)

        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        lay2.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close = QtGui.QPushButton("Cancel", self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        if dContainer.exec_() == QtGui.QDialog.Accepted:
            di.data = str(leCommentText.text())
            di.instruction = int(cbPosition.itemData(
                                 cbPosition.currentIndex()).toInt()[0])
            self.Ddialog.cbDisassembleCommands.setCurrentIndex(
                self.Ddialog.cbDisassembleCommands.findData(di.instruction))

    def EditCommentDisplacement(self, di):
        # get components
        d, f, c = spectrumtranslate.get_comment_displacement_values(di.data)
        # create dialog
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Comment Displacement")
        dContainer.setModal(True)

        lay = QtGui.QVBoxLayout()

        lay.addWidget(QtGui.QLabel("Comment Text:"))

        leCommentText = QtGui.QLineEdit()
        if c:
            leCommentText.setText(c)
        leCommentText.setToolTip("The text to be added as the comment.")
        leCommentText.sizePolicy().setHorizontalPolicy(
            QtGui.QSizePolicy.Expanding)
        leCommentText.sizePolicy().setHorizontalStretch(1)
        lay.addWidget(leCommentText)
        dContainer.leCommentText = leCommentText

        cbPosition = QtGui.QComboBox(self)
        cbPosition.addItem("Comment End of line",
                           spectrumtranslate.DisassembleInstruction.
                           DISASSEMBLE_CODES["Comment Displacement"])
        cbPosition.addItem("Comment on line before",
                           spectrumtranslate.DisassembleInstruction.
                           DISASSEMBLE_CODES["Comment Displacement Before"])
        cbPosition.addItem("Comment on line after",
                           spectrumtranslate.DisassembleInstruction.
                           DISASSEMBLE_CODES["Comment Displacement After"])
        cbPosition.setToolTip("Where the comment is placed.")
        cbPosition.setCurrentIndex(cbPosition.findData(di.instruction))
        lay.addWidget(cbPosition)

        lay.addWidget(QtGui.QLabel("index to be referenced:"))

        leAddress = QtGui.QLineEdit()
        leAddress.setText(self.Ddialog.Format.format(0 if d is None else d))
        leAddress.setToolTip("The index to be searched for and commented on \
when found.\nShould be {}.".format(
            self.Ddialog.cbNumberFormat.currentText()))
        lay.addWidget(leAddress)
        dContainer.leAddress = leAddress

        cbRegister = QtGui.QComboBox(self)
        cbRegister.addItem("IX register", 1)
        cbRegister.addItem("IY register", 2)
        cbRegister.addItem("IX and IY registers", 3)
        cbRegister.setToolTip("Displacements on which registers do you want \
commented.")
        cbRegister.setCurrentIndex(cbRegister.findData(1 if f is None else f))
        lay.addWidget(cbRegister)

        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        lay2.addWidget(ok)
        ok.clicked.connect(self.CommentDisplacementOk)
        close = QtGui.QPushButton("Cancel", self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        self.Ddialog.dCommentDisplacement = dContainer

        if dContainer.exec_() == QtGui.QDialog.Accepted:
            d = self.CheckInstructionAddress(leAddress)
            f = int(cbRegister.itemData(cbRegister.currentIndex()).toInt()[0])
            di.data = spectrumtranslate.get_comment_displacement_string(
                d, f, str(leCommentText.text()))
            di.instruction = int(cbPosition.itemData(
                                 cbPosition.currentIndex()).toInt()[0])
            self.Ddialog.cbDisassembleCommands.setCurrentIndex(
                self.Ddialog.cbDisassembleCommands.findData(di.instruction))

        del self.Ddialog.dCommentDisplacement

    def CommentDisplacementOk(self):
        d = self.Ddialog.dCommentDisplacement
        if self.CheckInstructionAddress(d.leAddress) == -1:
            message = "Displacement must be between 0 and " + self.Ddialog.Format +\
                " {1}."
            QtGui.QMessageBox.warning(self, "Error!", message.format(
                255, self.Ddialog.cbNumberFormat.currentText()))
        elif d.leCommentText.text() == "":
            QtGui.QMessageBox.warning(self, "Error!", "No comment")
        else:
            d.accept()

    def EditCommentReference(self, di):
        # get data
        ref, flag, comment = spectrumtranslate.get_comment_reference_values(
            di.data)
        # create dialog
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Comment Reference")
        dContainer.setModal(True)

        lay = QtGui.QVBoxLayout()

        lay.addWidget(QtGui.QLabel("Comment Text:"))

        leCommentText = QtGui.QLineEdit()
        if comment:
            leCommentText.setText(comment)
        leCommentText.setToolTip("The text to be added as the comment.")
        leCommentText.sizePolicy().setHorizontalPolicy(
            QtGui.QSizePolicy.Expanding)
        leCommentText.sizePolicy().setHorizontalStretch(1)
        lay.addWidget(leCommentText)
        dContainer.leCommentText = leCommentText

        cbPosition = QtGui.QComboBox(self)
        cbPosition.addItem("Comment End of line",
                           spectrumtranslate.DisassembleInstruction.
                           DISASSEMBLE_CODES["Comment Reference"])
        cbPosition.addItem("Comment on line before",
                           spectrumtranslate.DisassembleInstruction.
                           DISASSEMBLE_CODES["Comment Reference Before"])
        cbPosition.addItem("Comment on line after",
                           spectrumtranslate.DisassembleInstruction.
                           DISASSEMBLE_CODES["Comment Reference After"])
        cbPosition.setToolTip("Where the comment is placed.")
        cbPosition.setCurrentIndex(cbPosition.findData(di.instruction))
        lay.addWidget(cbPosition)

        lay.addWidget(QtGui.QLabel("address/value to be referenced:"))

        leAddress = QtGui.QLineEdit()
        leAddress.setText(self.Ddialog.Format.format(ref if ref else 0))
        leAddress.setToolTip("The address/value to be searched for and \
commented on when found.\nShould be {}.".format(
            self.Ddialog.cbNumberFormat.currentText()))
        lay.addWidget(leAddress)
        dContainer.leAddress = leAddress

        flag = 0 if flag is None else flag
        cb1 = QtGui.QCheckBox("contents of address accessed")
        cb1.setToolTip("Comment the address if it's used to access the memory \
contents: LD A,(0x8000), or LD (0x4000),HL.")
        cb1.toggle()
        if (flag & 1) == 0:
            cb1.setCheckState(False)
        lay.addWidget(cb1)

        cb2 = QtGui.QCheckBox("address/value loaded into a register")
        cb2.setToolTip("Comment the address/value if it's loaded into a \
register: LD BC,0x9000.")
        cb2.toggle()
        if (flag & 2) == 0:
            cb2.setCheckState(False)
        lay.addWidget(cb2)

        cb3 = QtGui.QCheckBox("Call to this address")
        cb3.setToolTip("Comment the address if it's called: CALL NZ,0x8000.")
        cb3.toggle()
        if (flag & 4) == 0:
            cb3.setCheckState(False)
        lay.addWidget(cb3)

        cb4 = QtGui.QCheckBox("Jump absolute to this address")
        cb4.setToolTip("Comment the address if it's jumped absolutly to: JP 0x8000.")
        cb4.toggle()
        if (flag & 8) == 0:
            cb4.setCheckState(False)
        lay.addWidget(cb4)

        cb5 = QtGui.QCheckBox("Jump relative to this address")
        cb5.setToolTip("Comment the address if it's jumped relative to: JR 0x8000.")
        cb5.toggle()
        if (flag & 16) == 0:
            cb5.setCheckState(False)
        lay.addWidget(cb5)

        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        lay2.addWidget(ok)
        ok.clicked.connect(self.CommentReferenceOk)
        close = QtGui.QPushButton("Cancel", self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        self.Ddialog.dCommentReference = dContainer

        if dContainer.exec_() == QtGui.QDialog.Accepted:
            a = self.CheckInstructionAddress(leAddress)
            f = (1 if cb1.isChecked() else 0) + \
                (2 if cb2.isChecked() else 0) + \
                (4 if cb3.isChecked() else 0) + \
                (8 if cb4.isChecked() else 0) + \
                (16 if cb5.isChecked() else 0)
            di.data = spectrumtranslate.get_comment_reference_string(
                a, f, str(leCommentText.text()))
            di.instruction = int(cbPosition.itemData(
                                 cbPosition.currentIndex()).toInt()[0])
            self.Ddialog.cbDisassembleCommands.setCurrentIndex(
                self.Ddialog.cbDisassembleCommands.findData(di.instruction))

        del self.Ddialog.dCommentReference

    def CommentReferenceOk(self):
        d = self.Ddialog.dCommentReference
        if self.CheckInstructionAddress(d.leAddress) == -1:
            message = "Address must be between 0 and " + self.Ddialog.Format +\
                " {1}."
            QtGui.QMessageBox.warning(self, "Error!", message.format(
                65535, self.Ddialog.cbNumberFormat.currentText()))
        elif d.leCommentText.text() == "":
            QtGui.QMessageBox.warning(self, "Error!", "No comment")
        else:
            d.accept()

    def EditCommentPattern(self, di):
        # get instruction parts
        parts = spectrumtranslate.detailsfromfindandcomment(di.data)
        # create dialog
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Comment Pattern")
        dContainer.setModal(True)

        lay = QtGui.QVBoxLayout()

        lay.addWidget(QtGui.QLabel("Comment Text:"))

        leCommentText = QtGui.QTextEdit()
        leCommentText.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        if parts and parts[0]:
            leCommentText.setPlainText(
                spectrumtranslate.instructiontexttostring(parts[1]))
        leCommentText.myfont = QFont(
            'monospace', int(round(leCommentText.fontPointSize())))
        leCommentText.setFont(leCommentText.myfont)
        leCommentText.setToolTip("The text to be added as the comment.")
        lay.addWidget(leCommentText)

        cbPosition = QtGui.QComboBox(self)
        cbPosition.addItem("Comment End of line",
                           spectrumtranslate.DisassembleInstruction.
                           DISASSEMBLE_CODES["Comment"])
        cbPosition.addItem("Comment Before line",
                           spectrumtranslate.DisassembleInstruction.
                           DISASSEMBLE_CODES["Comment Before"])
        cbPosition.addItem("Comment After line",
                           spectrumtranslate.DisassembleInstruction.
                           DISASSEMBLE_CODES["Comment After"])
        cbPosition.setToolTip("Where the comment is placed.")
        cbPosition.setCurrentIndex(parts[3] if (parts and parts[3]) else 0)
        lay.addWidget(cbPosition)

        createPredefined = QtGui.QPushButton(
            "Create search command for CALL/JP", self)
        createPredefined.setToolTip("Create Comment Pattern search command \
for a CALL or JP command.\nN.B. it will be more efficient to use a Comment \
Reference command unless you want to do anything non-standard.")
        lay.addWidget(createPredefined)
        createPredefined.clicked.connect(
            self.CreateCommentPatternSearchCommand)

        lay.addWidget(QtGui.QLabel("Comment Pattern search commands:"))

        teCommentPatternSearch = QtGui.QTextEdit()
        teCommentPatternSearch.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        if parts and parts[0]:
            teCommentPatternSearch.setPlainText(parts[0])
        teCommentPatternSearch.myfont = QFont(
            'monospace', int(round(teCommentPatternSearch.fontPointSize())))
        teCommentPatternSearch.setFont(teCommentPatternSearch.myfont)
        teCommentPatternSearch.setToolTip(
            "Code to find where if this line should be commented.")
        lay.addWidget(teCommentPatternSearch)

        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        lay2.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close = QtGui.QPushButton("Cancel", self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        self.Ddialog.teCommentPatternSearch = teCommentPatternSearch

        if dContainer.exec_() == QtGui.QDialog.Accepted:
            di.data = spectrumtranslate.createfindandcomment(
                str(teCommentPatternSearch.toPlainText()),
                spectrumtranslate.stringtoinstructiontext(
                    leCommentText.toPlainText()),
                1,
                cbPosition.currentIndex())

        del self.Ddialog.teCommentPatternSearch

    def CreateCommentPatternSearchCommand(self):
        # create dialog
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Create Comment Pattern Search Command")
        dContainer.setModal(True)

        lay = QtGui.QVBoxLayout()

        cbCommand = QtGui.QComboBox(self)
        cbCommand.addItem("CALL")
        cbCommand.addItem("JP")
        cbCommand.addItem("CALL or JP")
        cbCommand.setToolTip("The command to be looked for.")
        lay.addWidget(cbCommand)

        lay.addWidget(QtGui.QLabel("address to be called/jumped to:"))

        leAddress = QtGui.QLineEdit()
        leAddress.setToolTip("The address which the call/jump to is being \
searched for.\nShould be {}.".format(
            self.Ddialog.cbNumberFormat.currentText()))
        lay.addWidget(leAddress)
        dContainer.leAddress = leAddress

        cbConditional = QtGui.QCheckBox("Include conditional CALL/JP")
        cbConditional.setToolTip(
            "Do you want to look for conditional calls and/or jumps.")
        cbConditional.toggle()
        cbConditional.setCheckState(False)
        lay.addWidget(cbConditional)

        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok = QtGui.QPushButton("Set Commands", self)
        lay2.addWidget(ok)
        ok.clicked.connect(self.CreateCommentPatternSearchCommandAddress)
        close = QtGui.QPushButton("Cancel", self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        self.Ddialog.CommentPatternSearchDialog = dContainer

        if dContainer.exec_() == QtGui.QDialog.Accepted:
            i = cbCommand.currentIndex() + 1
            a = self.CheckInstructionAddress(leAddress)
            c = cbConditional.isChecked()
            d1 = "  " if i == 3 else ""
            d2 = "" if i == 3 else "  "

            searchcommand = "%(                     %#start test block\n"
            if i == 3:
                searchcommand += "  %(\n"
            if c:
                searchcommand += "{}  %X0700%MV0F00C7    {}%#filter out \
variable bits for conditional {}{}{}\n".format(d1, d2,
                                               "Call" if i & 1 == 1 else "",
                                               "/" if i == 3 else "",
                                               "Jump" if i & 2 == 2 else "")
            if (i & 1) == 1:
                searchcommand += "{{}}  %?EQ0000C4         {{}}%#do the bits\
 C7 at current address==0xC4 (CALL)\n" if c else "{{}}  %?EQ%MV0F00CD      {{}}\
%#does the byte at current address==0xCD (CALL)\n"
            if i == 3:
                searchcommand += "    %?BO               %#or\n"
            if (i & 2) == 2:
                searchcommand += "{{}}  %?EQ0000C2         {{}}%#do the bits\
 C7 at current address==0xC2 (JP)\n" if c else "{{}}  %?EQ%MV0F00C3      \
{{}}%#does the byte at current address==0xC3 (JP)\n"
            if i == 3:
                searchcommand += "  %)\n"
            searchcommand += """  %X0200%V0F0001       %#var0=current address+1
  %?BA                 %#and mode
  %?EQ%MWV00{:04X}       %#is address right?
%)                     %#end of test block""".format(a)
            self.Ddialog.teCommentPatternSearch.setPlainText(
                searchcommand.format().format(d1, d2))

        del self.Ddialog.CommentPatternSearchDialog

    def CreateCommentPatternSearchCommandAddress(self):
        i = self.Ddialog.CommentPatternSearchDialog.leAddress
        if self.CheckInstructionAddress(i) == -1:
            message = "Address must be between 0 and " + self.Ddialog.Format +\
                " {1}."
            QtGui.QMessageBox.warning(self, "Error!", message.format(
                65535, self.Ddialog.cbNumberFormat.currentText()))
        else:
            self.Ddialog.CommentPatternSearchDialog.accept()

    def EditPatternDataBlock(self, di):
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Pattern Data Block")
        dContainer.setModal(True)

        lay = QtGui.QVBoxLayout()

        lay2 = QtGui.QHBoxLayout()
        lay2.addWidget(QtGui.QLabel("Pattern Data Block function:"))

        cbEditPatternDataBlock = QtGui.QComboBox(self)
        for key in spectrumtranslate.DisassembleInstruction.\
                DISASSEMBLE_PATTERNBLOCK_CODES_ORDERED:
            cbEditPatternDataBlock.addItem(key)

        cbEditPatternDataBlock.setToolTip(
            "Select instructions for Pattern Data block")
        for key in spectrumtranslate.DisassembleInstruction.\
                DISASSEMBLE_PATTERNBLOCK_CODES_ORDERED:
            if spectrumtranslate.DisassembleInstruction.DISASSEMBLE_PATTERNBLOCK_CODES[key] == di.data:
                break

        _setcombo(cbEditPatternDataBlock, key)
        self.cbEditPatternDataBlock = cbEditPatternDataBlock
        cbEditPatternDataBlock.currentIndexChanged[str].connect(
            self.ChangeEditPatternDataBlock)

        lay2.addWidget(cbEditPatternDataBlock)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        testblock, prepblock, actionblock = spectrumtranslate.\
            getpartsofpatterndatablock(di.data)

        lay.addWidget(QtGui.QLabel("Pattern Data Block search commands:"))

        tePatternDataBlockSearch = QtGui.QTextEdit()
        tePatternDataBlockSearch.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        if testblock:
            tePatternDataBlockSearch.setPlainText(testblock)
        tePatternDataBlockSearch.myfont = QFont(
            'monospace', int(round(tePatternDataBlockSearch.fontPointSize())))
        tePatternDataBlockSearch.setFont(tePatternDataBlockSearch.myfont)
        tePatternDataBlockSearch.setToolTip(
            "Code to find where block ought to be.")
        tePatternDataBlockSearch.textChanged.connect(
            self.ChangePatternDataBlock)
        self.tePatternDataBlockSearch = tePatternDataBlockSearch
        lay.addWidget(tePatternDataBlockSearch)

        lay.addWidget(QtGui.QLabel(
            "Pattern Data Block address setup commands:"))

        tePatternDataBlockSetup = QtGui.QTextEdit()
        tePatternDataBlockSetup.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        if prepblock:
            tePatternDataBlockSetup.setPlainText(prepblock)
        tePatternDataBlockSetup.myfont = QFont(
            'monospace', int(round(tePatternDataBlockSetup.fontPointSize())))
        tePatternDataBlockSetup.setFont(tePatternDataBlockSetup.myfont)
        tePatternDataBlockSetup.setToolTip(
            "Code to define start & end of Action DataBlock.")
        tePatternDataBlockSetup.textChanged.connect(
            self.ChangePatternDataBlock)
        self.tePatternDataBlockSetup = tePatternDataBlockSetup
        lay.addWidget(tePatternDataBlockSetup)

        lay.addWidget(QtGui.QLabel("Pattern Data Block Action commands:"))

        tePatternDataBlockAction = QtGui.QTextEdit()
        tePatternDataBlockAction.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        if actionblock:
            tePatternDataBlockAction.setPlainText(actionblock)
        tePatternDataBlockAction.myfont = QFont(
            'monospace', int(round(tePatternDataBlockAction.fontPointSize())))
        tePatternDataBlockAction.setFont(tePatternDataBlockAction.myfont)
        tePatternDataBlockAction.setToolTip(
            "Code to be executed on specified block.")
        tePatternDataBlockAction.textChanged.connect(
            self.ChangePatternDataBlock)
        self.tePatternDataBlockAction = tePatternDataBlockAction
        lay.addWidget(tePatternDataBlockAction)

        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        lay2.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close = QtGui.QPushButton("Cancel", self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        # set to same size as parent
        dContainer.setGeometry(self.geometry())

        if dContainer.exec_() == QtGui.QDialog.Accepted:
            pattern = str(cbEditPatternDataBlock.currentText())
            if pattern == "Custom":
                di.data = str(self.tePatternDataBlockSearch.toPlainText() +
                              "\n" +
                              self.tePatternDataBlockSetup.toPlainText() +
                              "\n" +
                              self.tePatternDataBlockAction.toPlainText())

            else:
                di.data = spectrumtranslate.DisassembleInstruction.\
                    DISASSEMBLE_PATTERNBLOCK_CODES[pattern]

        del self.cbEditPatternDataBlock
        del self.tePatternDataBlockSearch
        del self.tePatternDataBlockSetup
        del self.tePatternDataBlockAction

    def ChangeEditPatternDataBlock(self, txt):
        blocks = spectrumtranslate.getpartsofpatterndatablock(
            spectrumtranslate.DisassembleInstruction.
            DISASSEMBLE_PATTERNBLOCK_CODES[str(txt)])

        if all(blocks[0] is not None, blocks[1] is not None, blocks[2] is not None):
            self.tePatternDataBlockSearch.textChanged.disconnect(
                self.ChangePatternDataBlock)
            self.tePatternDataBlockSetup.textChanged.disconnect(
                self.ChangePatternDataBlock)
            self.tePatternDataBlockAction.textChanged.disconnect(
                self.ChangePatternDataBlock)
            self.tePatternDataBlockSearch.setPlainText(blocks[0])
            self.tePatternDataBlockSetup.setPlainText(blocks[1])
            self.tePatternDataBlockAction.setPlainText(blocks[2])
            self.tePatternDataBlockSearch.textChanged.connect(
                self.ChangePatternDataBlock)
            self.tePatternDataBlockSetup.textChanged.connect(
                self.ChangePatternDataBlock)
            self.tePatternDataBlockAction.textChanged.connect(
                self.ChangePatternDataBlock)

    def ChangePatternDataBlock(self):
        blocks = spectrumtranslate.getpartsofpatterndatablock(
            str(self.tePatternDataBlockSearch.toPlainText() +
                self.tePatternDataBlockSetup.toPlainText() +
                self.tePatternDataBlockAction.toPlainText()))
        if all(blocks[0] is not None, blocks[1] is not None, blocks[2] is not None):
            blocks = [block.strip() for block in blocks]

        for key in spectrumtranslate.DisassembleInstruction.\
                DISASSEMBLE_PATTERNBLOCK_CODES_ORDERED:
            testblocks = spectrumtranslate.getpartsofpatterndatablock(
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_PATTERNBLOCK_CODES[key])
            if any(testblocks[0] is None, testblocks[1] is None, testblocks[2] is None):
                continue

            testblocks = [block.strip() for block in testblocks]
            if testblocks == blocks:
                break

        self.cbEditPatternDataBlock.currentIndexChanged[str].disconnect(
            self.ChangeEditPatternDataBlock)
        _setcombo(self.cbEditPatternDataBlock, key)
        self.cbEditPatternDataBlock.currentIndexChanged[str].connect(
            self.ChangeEditPatternDataBlock)

    def EditDataBlock(self, di):
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Data Block")
        dContainer.setModal(True)

        lay = QtGui.QVBoxLayout()

        lay2 = QtGui.QHBoxLayout()
        lay2.addWidget(QtGui.QLabel("Data Block function:"))

        cbEditDataBlock = QtGui.QComboBox(self)
        for key in spectrumtranslate.DisassembleInstruction.\
                PredefinedFunctions.keys():
            cbEditDataBlock.addItem("PredefinedFunction: " + key)
        for key in spectrumtranslate.DisassembleInstruction.\
                PredefinedRoutines.keys():
            cbEditDataBlock.addItem("PredefinedRoutine: " + key)
        for key in spectrumtranslate.DisassembleInstruction.\
                DISASSEMBLE_DATABLOCK_CODES_ORDERED:
            cbEditDataBlock.addItem(key)

        cbEditDataBlock.setToolTip("Select instructions for Data block")
        for key in spectrumtranslate.DisassembleInstruction.DISASSEMBLE_DATABLOCK_CODES_ORDERED:
            if spectrumtranslate.DisassembleInstruction.DISASSEMBLE_DATABLOCK_CODES[key] == di.data:
                break
        match = re.match(r"^\s*%!([a-zA-Z_][a-zA-Z_0-9]*)[(].*[)]\s*$", di.data,
                         re.DOTALL)
        if match and match.groups()[0] in spectrumtranslate.DisassembleInstruction.PredefinedRoutines.keys():
            key = "PredefinedRoutine: " + match.groups()[0]
        match = re.match(r"^\s*%P([a-zA-Z_][a-zA-Z_0-9]*)[(].*[)]\s*$", di.data,
                         re.DOTALL)
        if match and match.groups()[0] in spectrumtranslate.DisassembleInstruction.PredefinedFunctions.keys():
            key = "PredefinedFunction: " + match.groups()[0]

        _setcombo(cbEditDataBlock, key)
        self.cbEditDataBlock = cbEditDataBlock
        cbEditDataBlock.currentIndexChanged[str].connect(
            self.ChangeEditDataBlock)

        lay2.addWidget(cbEditDataBlock)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        lay.addWidget(QtGui.QLabel("Data Block commands:"))

        teDataBlock = QtGui.QTextEdit()
        teDataBlock.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        if di.data:
            teDataBlock.setPlainText(di.data)
        teDataBlock.myfont = QFont('monospace',
                                   int(round(teDataBlock.fontPointSize())))
        teDataBlock.setFont(teDataBlock.myfont)
        teDataBlock.setToolTip("Code to be executed in the Data Block.")
        teDataBlock.textChanged.connect(self.ChangeDataBlock)
        self.teDataBlock = teDataBlock
        lay.addWidget(teDataBlock)

        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        lay2.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close = QtGui.QPushButton("Cancel", self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        # set to same size as parent
        dContainer.setGeometry(self.geometry())

        if dContainer.exec_() == QtGui.QDialog.Accepted:
            di.data = str(teDataBlock.toPlainText())

        del self.cbEditDataBlock
        del self.teDataBlock

    def ChangeDataBlock(self):
        blockText = self.teDataBlock.toPlainText()
        for key in spectrumtranslate.DisassembleInstruction.\
                DISASSEMBLE_DATABLOCK_CODES_ORDERED:
            if spectrumtranslate.DisassembleInstruction.DISASSEMBLE_DATABLOCK_CODES[key] == blockText:
                break
        match = re.match(r"^\s*%!([a-zA-Z_][a-zA-Z_0-9]*)[(].*[)]\s*$",
                         blockText, re.DOTALL)
        if match and match.groups()[0] in spectrumtranslate.DisassembleInstruction.\
               PredefinedRoutines.keys():
            key = "PredefinedRoutine: " + match.groups()[0]
        match = re.match(r"^\s*%P([a-zA-Z_][a-zA-Z_0-9]*)[(].*[)]\s*$",
                         blockText, re.DOTALL)
        if match and match.groups()[0] in spectrumtranslate.DisassembleInstruction.\
               PredefinedFunctions.keys():
            key = "PredefinedFunction: " + match.groups()[0]

        self.cbEditDataBlock.currentIndexChanged[str].disconnect(
            self.ChangeEditDataBlock)
        _setcombo(self.cbEditDataBlock, key)
        self.cbEditDataBlock.currentIndexChanged[str].connect(
            self.ChangeEditDataBlock)

    def ChangeEditDataBlock(self, txt):
        self.teDataBlock.textChanged.disconnect(self.ChangeDataBlock)
        txt = str(txt)
        if txt == "PredefinedFunction: DefineByte":
            txt = "%PDefineByte(Signed=False, Format=0, FormatIdentifyer=True, GapFrequency=1, Gap=',', MaxPerLine=1)"
        elif txt == "PredefinedFunction: DefineWord":
            txt = "%PDefineWord(Signed=False, Format=0, FormatIdentifyer=True, GapFrequency=1, Gap=',', MaxPerLine=1, LittleEndian=True)"
        elif txt == "PredefinedFunction: DefineMessage":
            txt = "%PDefineMessage(DataType='DM', Noncharoutofquotes=False)"
        elif txt == "PredefinedRoutine: DefineByte":
            txt = "%!DefineByte(Signed=False, Format=0, FormatIdentifyer=True, GapFrequency=1, Gap=',', MaxPerLine=1)"
        elif txt == "PredefinedRoutine: DefineWord":
            txt = "%!DefineWord(Signed=False, Format=0, FormatIdentifyer=True, GapFrequency=1, Gap=',', MaxPerLine=1, LittleEndian=True)"
        elif txt == "PredefinedRoutine: DefineMessage":
            txt = "%!DefineMessage(DataType='DM', Noncharoutofquotes=False)"
        elif txt == "PredefinedRoutine: FindPattern":
            txt = "%!FindPattern(0,1,2,3,4)"
        elif txt == "PredefinedRoutine: StartandEndbyOffset":
            txt = "%!StartandEndbyOffset(startoffset=0, endoffset=0)"
        else:
            txt = spectrumtranslate.DisassembleInstruction.\
                DISASSEMBLE_DATABLOCK_CODES[txt]

        self.teDataBlock.setPlainText(txt)
        self.teDataBlock.textChanged.connect(self.ChangeDataBlock)

    def EditUnreferencedLineNumberFrequency(self, instruction):
        # create dialog
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Line Referenceing")
        dContainer.setModal(True)

        lay = QtGui.QVBoxLayout()

        lay.addWidget(QtGui.QLabel("Have unreferenced line addresses shown at \
least every how many lines:"))

        leUnreferencedLineNumber = QtGui.QLineEdit()
        leUnreferencedLineNumber.setMaxLength(3)
        leUnreferencedLineNumber.setText(self.Ddialog.Format.format(
            int(instruction.data, 16)))
        leUnreferencedLineNumber.setToolTip("every how many unreferenced \
lines do you want adresses displayed? Use 0 for none.")
        leUnreferencedLineNumber.sizePolicy().setHorizontalPolicy(
            QtGui.QSizePolicy.Expanding)
        leUnreferencedLineNumber.sizePolicy().setHorizontalStretch(1)
        leUnreferencedLineNumber.textChanged.connect(
            self.ChangeUnreferencedLineNumber)
        self.leUnreferencedLineNumber = leUnreferencedLineNumber
        lay.addWidget(leUnreferencedLineNumber)

        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        lay2.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close = QtGui.QPushButton("Cancel", self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        if dContainer.exec_() == QtGui.QDialog.Accepted:
            i = self.CheckInstructionAddress(leUnreferencedLineNumber)
            # if invalid number set to 0
            if i < 0 or i > 0xFF:
                i = 0

            instruction.data = "{:X}".format(i)

        del self.leUnreferencedLineNumber

    def ChangeUnreferencedLineNumber(self):
        i = self.CheckInstructionAddress(self.leUnreferencedLineNumber)
        colour = "#FF8080" if i > 0xFF or i < 0 else "white"

        self.leUnreferencedLineNumber.setStyleSheet(
            "QLineEdit {background-color:" + colour + "}")

    def EditCustomFormatDialog(self, instruction):
        settings = spectrumtranslate.get_custom_format_values(instruction.data)

        # create dialog
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Custom Format Settings")
        dContainer.setModal(True)

        grid = QtGui.QGridLayout()
        grid.setSpacing(2)

        cbCustomFormatAddressFormat = QtGui.QComboBox(self)
        cbCustomFormatAddressFormat.addItem("Address format Hexadecimal", 0)
        cbCustomFormatAddressFormat.addItem("Address format Decimal", 1)
        cbCustomFormatAddressFormat.addItem("Address format Octal", 2)
        cbCustomFormatAddressFormat.addItem("Address format Binary", 3)
        cbCustomFormatAddressFormat.setToolTip(
            "In what format do you want the line adresses displayed?")
        cbCustomFormatAddressFormat.setCurrentIndex(settings["AddressOutput"])
        grid.addWidget(cbCustomFormatAddressFormat, 0, 0, 1, 2)

        cbCustomFormatNumberFormat = QtGui.QComboBox(self)
        cbCustomFormatNumberFormat.addItem("Number format Hexadecimal", 0)
        cbCustomFormatNumberFormat.addItem("Number format Decimal", 1)
        cbCustomFormatNumberFormat.addItem("Number format Octal", 2)
        cbCustomFormatNumberFormat.addItem("Number format Binary", 3)
        cbCustomFormatNumberFormat.setToolTip(
            "In what format do you want numbers displayed?")
        cbCustomFormatNumberFormat.setCurrentIndex(settings["NumberOutput"])
        grid.addWidget(cbCustomFormatNumberFormat, 1, 0, 1, 2)

        cbCustomFormatCommandFormat = QtGui.QComboBox(self)
        cbCustomFormatCommandFormat.addItem("Command format Hexadecimal", 0)
        cbCustomFormatCommandFormat.addItem("Command format Decimal", 1)
        cbCustomFormatCommandFormat.addItem("Command format Octal", 2)
        cbCustomFormatCommandFormat.addItem("Command format Binary", 3)
        cbCustomFormatCommandFormat.setToolTip(
            "In what format do you want the bytes of commands displayed?")
        cbCustomFormatCommandFormat.setCurrentIndex(settings["CommandOutput"])
        grid.addWidget(cbCustomFormatCommandFormat, 2, 0, 1, 2)

        cbCustomFormatCodeTimes = QtGui.QComboBox(self)
        cbCustomFormatCodeTimes.addItem("No timings", 0)
        cbCustomFormatCodeTimes.addItem("List T states", 1)
        cbCustomFormatCodeTimes.addItem("List time cycles", 2)
        cbCustomFormatCodeTimes.addItem("List all timings", 3)
        cbCustomFormatCodeTimes.setToolTip(
            "What instruction timeing details do you want listed?")
        cbCustomFormatCodeTimes.setCurrentIndex(settings["OutputTStates"])
        grid.addWidget(cbCustomFormatCodeTimes, 3, 0, 1, 2)

        cbCustomFormatCodeJump = QtGui.QComboBox(self)
        cbCustomFormatCodeJump.addItem("No space after jump", 0)
        cbCustomFormatCodeJump.addItem("Space after absolute jump", 1)
        cbCustomFormatCodeJump.addItem("Space after all jumps", 2)
        cbCustomFormatCodeJump.setToolTip("Blank line for readability after \
absolute jumps, none or all jumps.")
        cbCustomFormatCodeJump.setCurrentIndex(settings["BreakAfterJumps"])
        grid.addWidget(cbCustomFormatCodeJump, 4, 0, 1, 2)

        cbCustomFormatLineFormat = QtGui.QComboBox(self)
        cbCustomFormatLineFormat.addItem("Show every line address", 0)
        cbCustomFormatLineFormat.addItem("Show no line addresses", 1)
        cbCustomFormatLineFormat.addItem("Show only referenced addresses", 2)
        cbCustomFormatLineFormat.setToolTip(
            "Which line adresses do you want displayed?")
        cbCustomFormatLineFormat.setCurrentIndex(settings["LineNumberOutput"])
        grid.addWidget(cbCustomFormatLineFormat, 5, 0, 1, 2)

        lab = QtGui.QLabel("Display unreferenced line address:")
        lab.setToolTip("every how many unreferenced lines do you want \
adresses displayed?")
        grid.addWidget(lab, 6, 0, 1, 1)

        leCustomFormatLineFrequency = QtGui.QLineEdit()
        leCustomFormatLineFrequency.setMaxLength(3)
        leCustomFormatLineFrequency.setText(self.Ddialog.Format.format(
            settings["ListEveryXLines"]))
        leCustomFormatLineFrequency.setToolTip("every how many unreferenced \
lines do you want adresses displayed?")
        leCustomFormatLineFrequency.sizePolicy().setHorizontalPolicy(
            QtGui.QSizePolicy.Expanding)
        leCustomFormatLineFrequency.sizePolicy().setHorizontalStretch(1)
        leCustomFormatLineFrequency.textChanged.connect(
            self.ChangeCustomFormatLineFrequency)
        self.Frequency = leCustomFormatLineFrequency
        grid.addWidget(leCustomFormatLineFrequency, 6, 1, 1, 1)

        cbCustomFormatBreakAfterData = QtGui.QCheckBox("Empty line after data")
        cbCustomFormatBreakAfterData.setToolTip(
            "Do you want an empty line after a data block for readability?")
        cbCustomFormatBreakAfterData.toggle()
        if settings["BreakAfterData"] == 1:
            cbCustomFormatBreakAfterData.setCheckState(False)

        grid.addWidget(cbCustomFormatBreakAfterData, 7, 0, 1, 2)

        cbCustomFormatReferenceNumbers = QtGui.QCheckBox(
            "Use data numbers as line references")
        cbCustomFormatReferenceNumbers.setToolTip("Do you want to use 16 bit \
numbers in data to be used as line references?")
        cbCustomFormatReferenceNumbers.toggle()
        if settings["TreatDataNumbersAsLineReferences"] == 1:
            cbCustomFormatReferenceNumbers.setCheckState(False)

        grid.addWidget(cbCustomFormatReferenceNumbers, 8, 0, 1, 2)

        cbCustomFormatDisplayCommandBytes = QtGui.QCheckBox(
            "Display byte values of commands")
        cbCustomFormatDisplayCommandBytes.setToolTip(
            "Do you want to display the bytes of a command?")
        cbCustomFormatDisplayCommandBytes.toggle()
        if settings["DisplayCommandBytes"] == 1:
            cbCustomFormatDisplayCommandBytes.setCheckState(False)

        grid.addWidget(cbCustomFormatDisplayCommandBytes, 9, 0, 1, 2)

        cbCustomFormatDisplayComments = QtGui.QCheckBox("Display comments")
        cbCustomFormatDisplayComments.setToolTip("Display comments? If not \
then timing, flags, and undocumented commands won't be displayed.")
        cbCustomFormatDisplayComments.toggle()
        if settings["DisplayComments"] == 1:
            cbCustomFormatDisplayComments.setCheckState(False)

        grid.addWidget(cbCustomFormatDisplayComments, 10, 0, 1, 2)

        cbCustomFormatSeperatorFormat = QtGui.QComboBox(self)
        cbCustomFormatSeperatorFormat.addItem("Use double space as separator",
                                              0)
        cbCustomFormatSeperatorFormat.addItem("Use tab as separator", 1)
        cbCustomFormatSeperatorFormat.addItem("Custom separator", 2)
        cbCustomFormatSeperatorFormat.setToolTip(
            "The type of seperator between parts of the output.")

        if settings["Seperator"] == "  ":
            sep = 0
        elif settings["Seperator"] == "\t":
            sep = 1
        else:
            sep = 2

        cbCustomFormatSeperatorFormat.setCurrentIndex(sep)
        cbCustomFormatSeperatorFormat.activated.connect(self.SeparatorChange)
        grid.addWidget(cbCustomFormatSeperatorFormat, 11, 0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lab = QtGui.QLabel("custom seperator:")
        lab.setToolTip("what characters do you want as a seperator?")
        self.lCustomSeperator = lab
        hbox.addWidget(lab)
        leCustomSeperator = QtGui.QLineEdit()
        leCustomSeperator.setText(settings["Seperator"])
        leCustomSeperator.setToolTip(
            "what characters do you want as a seperator?")
        leCustomSeperator.sizePolicy().setHorizontalPolicy(
            QtGui.QSizePolicy.Expanding)
        leCustomSeperator.sizePolicy().setHorizontalStretch(1)
        self.leCustomSeperator = leCustomSeperator
        hbox.addWidget(leCustomSeperator)
        grid.addLayout(hbox, 11, 1)

        self.lCustomSeperator.setEnabled(sep == 2)
        self.leCustomSeperator.setEnabled(sep == 2)

        cbCustomFormatCodeFlags = QtGui.QCheckBox("List Flags")
        cbCustomFormatCodeFlags.setToolTip(
            "List flags affected by machine instructions.")
        cbCustomFormatCodeFlags.toggle()
        if settings["ShowFlags"] == 0:
            cbCustomFormatCodeFlags.setCheckState(False)
        grid.addWidget(cbCustomFormatCodeFlags, 12, 0, 1, 2)

        cbCustomFormatCodeUndocumented = QtGui.QCheckBox(
            "Mark undocumented commands")
        cbCustomFormatCodeUndocumented.setToolTip(
            "Note undocumented machine instructions.")
        cbCustomFormatCodeUndocumented.toggle()
        if settings["MarkUndocumenedCommand"] == 0:
            cbCustomFormatCodeUndocumented.setCheckState(False)
        grid.addWidget(cbCustomFormatCodeUndocumented, 13, 0, 1, 2)

        cbXML = QtGui.QComboBox(self)
        cbXML.addItem("Non XML Output", 0)
        cbXML.addItem("XML Output", 1)
        cbXML.setToolTip("Does the disassembler output XML or not.")
        cbXML.setCurrentIndex(settings["XMLOutput"])
        grid.addWidget(cbXML, 14, 0, 1, 2)

        lay = QtGui.QHBoxLayout()
        lay.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        lay.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close = QtGui.QPushButton("Cancel", self)
        lay.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay.addStretch(1)

        grid.addLayout(lay, 15, 0, 1, 2)

        dContainer.setLayout(grid)

        if dContainer.exec_() == QtGui.QDialog.Accepted:
            i = self.CheckInstructionAddress(leCustomFormatLineFrequency)
            sep = cbCustomFormatSeperatorFormat.currentIndex()
            if sep == 0:
                septext = "  "
            elif sep == 1:
                septext = "\t"
            else:
                septext = str(leCustomSeperator.text())

            if i < 0 or i > 0xFF:
                QtGui.QMessageBox.warning(self, "Error!", "Unreferenced line \
frequency must be between 0 and 255 decimal.")

            elif len(septext) == 0:
                QtGui.QMessageBox.warning(self, "Error!",
                                          "Invalid custom seperator.")

            else:
                instruction.data = spectrumtranslate.get_custom_format_string(
                    cbCustomFormatAddressFormat.currentIndex(),
                    cbCustomFormatNumberFormat.currentIndex(),
                    cbCustomFormatCommandFormat.currentIndex(),
                    cbCustomFormatCodeTimes.currentIndex(),
                    cbCustomFormatCodeJump.currentIndex(),
                    cbCustomFormatLineFormat.currentIndex(),
                    i,
                    0 if cbCustomFormatBreakAfterData.isChecked() else 1,
                    0 if cbCustomFormatReferenceNumbers.isChecked() else 1,
                    0 if cbCustomFormatDisplayCommandBytes.isChecked() else 1,
                    0 if cbCustomFormatDisplayComments.isChecked() else 1,
                    septext,
                    1 if cbCustomFormatCodeFlags.isChecked() else 0,
                    1 if cbCustomFormatCodeUndocumented.isChecked() else 0,
                    cbXML.currentIndex())

        del self.Frequency
        del self.lCustomSeperator
        del self.leCustomSeperator

    def SeparatorChange(self, newindex):
        self.lCustomSeperator.setEnabled(newindex == 2)
        self.leCustomSeperator.setEnabled(newindex == 2)

    def ChangeCustomFormatLineFrequency(self):
        i = self.CheckInstructionAddress(self.Frequency)

        colour = "#FF8080" if i == -1 or i > 0xFF else "white"

        self.Frequency.setStyleSheet("QLineEdit {background-color:" + colour +
                                     "}")

    def CustomDisassembleSave(self):
        qfd = QtGui.QFileDialog(self, "Save Instruction List file")
        qfd.setFileMode(QtGui.QFileDialog.AnyFile)
        qfd.setAcceptMode(QtGui.QFileDialog.AcceptSave)

        # run dialog and if save is clicked then act on this
        if qfd.exec_() == QtGui.QDialog.Accepted:
            lwInstructions = self.Ddialog.lwInstructions
            fOut = qfd.selectedFiles()[0]
            try:
                with open(fOut, MODE_WT) as fo:
                    fo.write("\n".join([str(lwInstructions.item(i).di) for i in
                                        range(lwInstructions.count())]))
            except:
                QtGui.QMessageBox.warning(
                    self, "Error!",
                    'Failed to save data to "{}"'.format(fOut))

    def CustomDisassembleLoad(self):
        qfd = QtGui.QFileDialog(self, "Select Instruction file")
        qfd.setFileMode(QtGui.QFileDialog.AnyFile)
        qfd.setAcceptMode(QtGui.QFileDialog.AcceptOpen)

        # run dialog and if open is clicked then act on this
        if qfd.exec_() == QtGui.QDialog.Accepted:
            fIn = qfd.selectedFiles()[0]
            try:
                with open(fIn, MODE_RT) as fo:
                    instructions = [spectrumtranslate.DisassembleInstruction(
                        line.rstrip('\n')) for line in fo]
            except:
                QtGui.QMessageBox.warning(
                    self, "Error!",
                    'Unable to get data from "{}"'.format(fIn))
                return

            lwInstructions = self.Ddialog.lwInstructions
            lwInstructions.clear()
            for di in instructions:
                item = QtGui.QListWidgetItem("\n")
                lwInstructions.addItem(item)
                lab = QtGui.QLabel()
                lab.setIndent(5)
                lab.setFrameShape(QtGui.QFrame.Box)
                item.label = lab
                item.di = spectrumtranslate.DisassembleInstruction(di)
                self.setLabelText(item)
                lwInstructions.setItemWidget(item, lab)

            if len(instructions) > 0:
                lwInstructions.setCurrentRow(0)
            self.SetDisassembleDialogButtons()

    def CustomDisassembleDown(self):
        lwInstructions = self.Ddialog.lwInstructions
        selectpos = lwInstructions.currentRow()

        # when takeItem is used, it deletes items attached to the
        # listwidgetitem, so make a copy of the associated disassemble
        # instruction and create a new label
        di = spectrumtranslate.DisassembleInstruction(
            lwInstructions.currentItem().di)
        item = lwInstructions.takeItem(selectpos)
        lwInstructions.insertItem(selectpos + 1, item)
        lab = QtGui.QLabel()
        lab.setIndent(5)
        lab.setFrameShape(QtGui.QFrame.Box)
        item.label = lab
        item.di = di
        self.setLabelText(item)
        lwInstructions.setItemWidget(item, lab)

        # update focus
        lwInstructions.setCurrentRow(selectpos + 1)

        self.SetDisassembleDialogButtons()

    def CustomDisassembleUp(self):
        lwInstructions = self.Ddialog.lwInstructions
        selectpos = lwInstructions.currentRow()

        # when takeItem is used, it deletes items attached to the
        # listwidgetitem, so make a copy of the associated disassemble
        # instruction and create a new label
        di = spectrumtranslate.DisassembleInstruction(
            lwInstructions.currentItem().di)
        item = lwInstructions.takeItem(selectpos)
        lwInstructions.insertItem(selectpos - 1, item)
        lab = QtGui.QLabel()
        lab.setIndent(5)
        lab.setFrameShape(QtGui.QFrame.Box)
        item.label = lab
        item.di = di
        self.setLabelText(item)
        lwInstructions.setItemWidget(item, lab)

        # update focus
        lwInstructions.setCurrentRow(selectpos - 1)

        self.SetDisassembleDialogButtons()

    def CustomDisassembleDelete(self):
        lwInstructions = self.Ddialog.lwInstructions
        selectpos = lwInstructions.currentRow()

        if selectpos != -1:
            lwInstructions.takeItem(lwInstructions.currentRow())
            self.SetDisassembleDialogButtons()

    def CustomDisassembleNew(self):
        lwInstructions = self.Ddialog.lwInstructions

        item = QtGui.QListWidgetItem("\n")
        lwInstructions.addItem(item)
        lab = QtGui.QLabel()
        lab.setIndent(5)
        lab.setFrameShape(QtGui.QFrame.Box)
        item.label = lab
        item.di = spectrumtranslate.DisassembleInstruction(
            "Address Output Format Hex")
        self.setLabelText(item)
        lwInstructions.setItemWidget(item, lab)

        # set focus if new item added
        if len(self.diInstructions) == 1:
            lwInstructions.setCurrentRow(0)
            self.SetDisassembleDialogButtons()

    def DissassembleEditorFormatChange(self, index):
        self.Ddialog.Format = ('{0:X}', '{0:d}', '{0:o}', '{0:b}')[index]
        self.Ddialog.FormatBase = (16, 10, 8, 2)[index]
        instructionlist = self.Ddialog.lwInstructions
        for i in range(instructionlist.count()):
            self.setLabelText(instructionlist.item(i))

        # change start and end editor lineedits
        self.SetDisassembleDialogButtons()

    def ChangeDissassembleStart(self):
        dialog = self.Ddialog
        instructionlist = dialog.lwInstructions
        di = instructionlist.currentItem().di

        i = self.CheckInstructionAddress(dialog.leStart)
        dialog.leStart.setStyleSheet("QLineEdit {{\nbackground-color: {}\n}}".
                                     format("#FF8080" if i == -1 else "white"))
        if i != -1:
            di.start = i
            self.setLabelText(instructionlist.currentItem())

    def ChangeDissassembleEnd(self):
        dialog = self.Ddialog
        instructionlist = dialog.lwInstructions
        di = instructionlist.currentItem().di

        i = self.CheckInstructionAddress(dialog.leEnd)
        dialog.leEnd.setStyleSheet("QLineEdit {{\nbackground-color: {}\n}}".
                                   format("#FF8080" if i == -1 else "white"))
        if i != -1:
            di.end = i
            self.setLabelText(instructionlist.currentItem())

    def CheckInstructionAddress(self, le):
        try:
            l = int(str(le.text()), self.Ddialog.FormatBase)
            if l < 0 or l > 0x10000:
                l = -1
            return l
        except:
            return -1

    def instructionselectionchanged(self, f, t):
        self.SetDisassembleDialogButtons()

    def ChangeDissassembleCommand(self, txt):
        dialog = self.Ddialog
        instructionlist = dialog.lwInstructions
        selectpos = instructionlist.currentRow()

        if selectpos != -1:
            di = instructionlist.currentItem().di
            txt = str(txt)
            newinstruction = spectrumtranslate.DisassembleInstruction.\
                DISASSEMBLE_CODES[txt]
            instructionchanged = (newinstruction != di.instruction)
            di.instruction = newinstruction

            # handle change of format that needs data change
            if instructionchanged and txt == "Custom Format":
                di.data = "0000100  "

            elif instructionchanged and txt == "Line Number Every X":
                di.data = "8"

            elif instructionchanged and txt == "Data Block":
                di.data = spectrumtranslate.DisassembleInstruction.\
                    DISASSEMBLE_DATABLOCK_CODES["Define Byte Hex"]

            elif instructionchanged and txt == "Pattern Data Block":
                di.data = spectrumtranslate.DisassembleInstruction.\
                    DISASSEMBLE_PATTERNBLOCK_CODES["RST#08 (Error)"]

            elif instructionchanged and txt.startswith("Comment Reference"):
                di.data = spectrumtranslate.get_comment_reference_string(
                    0, 0x1F, "Comment")

            elif instructionchanged and txt.startswith("Comment Displacement"):
                di.data = spectrumtranslate.get_comment_displacement_string(
                    0, 3, "Comment")

            elif instructionchanged:
                di.data = None

            self.setLabelText(instructionlist.currentItem())

        self.SetDisassembleDialogButtons()

    def SetDisassembleDialogButtons(self):
        dialog = self.Ddialog
        instructionlist = dialog.lwInstructions

        number = instructionlist.count()
        selectpos = instructionlist.currentRow()

        di = None if selectpos == -1 else instructionlist.currentItem().di

        if di is not None:
            key = spectrumtranslate.get_disassemblecodename_from_value(
                di.instruction)
            if key is not None:
                _setcombo(dialog.cbDisassembleCommands, key)

            # could have used the textEdited signal to avoid
            # disconnecting and reconnecting.  This way will allow
            # highlighting of all abnormal value inputs
            dialog.leStart.textChanged.disconnect(self.ChangeDissassembleStart)
            dialog.leEnd.textChanged.disconnect(self.ChangeDissassembleEnd)
            dialog.leStart.setText(dialog.Format.format(di.start))
            dialog.leEnd.setText(dialog.Format.format(di.end))
            dialog.leStart.textChanged.connect(self.ChangeDissassembleStart)
            dialog.leEnd.textChanged.connect(self.ChangeDissassembleEnd)

        dialog.bsave.setEnabled(number > 0)
        dialog.bdelete.setEnabled(di is not None)
        dialog.bup.setEnabled(selectpos > 0)
        dialog.bdown.setEnabled(selectpos < number - 1 and di is not None)
        dialog.bedit.setEnabled(
            di is not None and
            (di.instruction in [spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Custom Format"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Line Number Every X"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Data Block"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Pattern Data Block"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Comment"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Comment Before"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Comment After"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Comment Reference"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Comment Reference Before"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Comment Reference After"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Comment Displacement"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Comment Displacement Before"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Comment Displacement After"],
                spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Comment Pattern"]]))
        dialog.cbDisassembleCommands.setEnabled(di is not None)
        dialog.leStart.setEnabled(di is not None)
        dialog.leEnd.setEnabled(di is not None)

    def setLabelText(self, lwInstruction):
        # find code name
        key = spectrumtranslate.get_disassemblecodename_from_value(
            lwInstruction.di.instruction)

        s = "<strong>{}</strong><br/>".format(key) + \
            self.Ddialog.Format.format(lwInstruction.di.start) + "->" + \
            self.Ddialog.Format.format(lwInstruction.di.end)

        if lwInstruction.di.instruction == spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Line Number Every X"]:
            s += " address every " + self.Ddialog.Format.format(
                int(lwInstruction.di.data, 16)) + " lines."

        elif lwInstruction.di.instruction == spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Data Block"]:
            for key in spectrumtranslate.DisassembleInstruction.\
                    DISASSEMBLE_DATABLOCK_CODES_ORDERED:
                if spectrumtranslate.DisassembleInstruction.DISASSEMBLE_DATABLOCK_CODES[key] == lwInstruction.di.data:
                    break

            match = re.match(r"^\s*%!([a-zA-Z_][a-zA-Z_0-9]*)[(].*[)]\s*$",
                             lwInstruction.di.data, re.DOTALL)
            if match and match.groups()[0] in spectrumtranslate.DisassembleInstruction.\
                    PredefinedRoutines.keys():
                key = "PredefinedRoutine: " + match.groups()[0]
            match = re.match(r"^\s*%P([a-zA-Z_][a-zA-Z_0-9]*)[(].*[)]\s*$",
                             lwInstruction.di.data, re.DOTALL)
            if match and match.groups()[0] in spectrumtranslate.DisassembleInstruction.\
                   PredefinedFunctions.keys():
                key = "PredefinedFunction: " + match.groups()[0]

            s += " - " + key

        elif lwInstruction.di.instruction == spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Pattern Data Block"]:
            for key in spectrumtranslate.DisassembleInstruction.DISASSEMBLE_PATTERNBLOCK_CODES_ORDERED:
                if spectrumtranslate.DisassembleInstruction.DISASSEMBLE_PATTERNBLOCK_CODES[key] == lwInstruction.di.data:
                    break

            s += " - " + key

        elif lwInstruction.di.instruction in [spectrumtranslate.
             DisassembleInstruction.DISASSEMBLE_CODES["Comment"].
             spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Comment Before"],
             spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Comment After"]]:
            s += ' comment: "{}"'.format("" if not lwInstruction.di.data else
                                          lwInstruction.di.data)

        elif lwInstruction.di.instruction in [spectrumtranslate.
             DisassembleInstruction.DISASSEMBLE_CODES["Comment Reference"],
             spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Comment Reference Before"],
             spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Comment Reference After"]]:
            a, f, c = spectrumtranslate.get_comment_reference_values(
                lwInstruction.di.data)
            s += ' address: {:04X} comment: "{}"'.format(a, c)

        elif lwInstruction.di.instruction in [spectrumtranslate.
             DisassembleInstruction.DISASSEMBLE_CODES[
             "Comment Displacement"],
             spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
             "Comment Displacement Before"],
             spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
             "Comment Displacement After"]]:
            d, f, c = spectrumtranslate.get_comment_displacement_values(
                lwInstruction.di.data)
            s += ' displacement: {:02X} comment: "{}"'.format(d, c)

        elif lwInstruction.di.instruction == spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES["Comment Pattern"]:
            parts = spectrumtranslate.detailsfromfindandcomment(
                lwInstruction.di.data)
            s += ' comment: "{}"'.format("" if not parts else
                spectrumtranslate.instructiontexttostring(parts[1]))

        lwInstruction.label.setText(s)

    def EditExportSettings(self):
        # create dialog
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Export Settings")
        dContainer.setModal(True)

        box = QtGui.QVBoxLayout()
        cbContainerType = QtGui.QComboBox(self)
        cbContainerType.addItem("Tzx file container", 0)
        cbContainerType.addItem("Tap file container", 1)
        cbContainerType.addItem("+D/Disciple file container", 2)
        cbContainerType.addItem("container format from destination file", 3)
        cbContainerType.setToolTip(
            "Select the type of containter file to export to.")
        cbContainerType.setCurrentIndex(self.ExportSettings["ContainerType"])
        box.addWidget(cbContainerType)

        tab = QtGui.QTabWidget()

        vbox = QtGui.QVBoxLayout()

        cbOverOrAppend = QtGui.QComboBox(self)
        cbOverOrAppend.addItem("Overwrite if file exists", 0)
        cbOverOrAppend.addItem("Append if file exists", 1)
        cbOverOrAppend.setToolTip(
            "Do you want to append or overwrite an existing file?")
        cbOverOrAppend.setCurrentIndex(self.ExportSettings["AppendOrOver"])
        vbox.addWidget(cbOverOrAppend)

        cbSaveWithHeader = QtGui.QComboBox(self)
        cbSaveWithHeader.addItem("Save as headerless block", 0)
        cbSaveWithHeader.addItem("Save with header", 1)
        cbSaveWithHeader.setToolTip(
            "Do you want to save as headerless block or file with header?")
        cbSaveWithHeader.setCurrentIndex(
            self.ExportSettings["SaveWithHeader"])
        cbSaveWithHeader.activated.connect(self.ExportSettingsControlUpdate)
        vbox.addWidget(cbSaveWithHeader)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lFileName = QtGui.QLabel("File Name:")
        hbox.addWidget(lFileName)
        leFileName = QtGui.QLineEdit(self)
        leFileName.setToolTip("Filename to export as.")
        leFileName.sizePolicy().setHorizontalPolicy(
            QtGui.QSizePolicy.Expanding)
        leFileName.sizePolicy().setHorizontalStretch(1)
        leFileName.setText(str(self.ExportSettings["Filename"]))
        leFileName.textEdited.connect(self.setleFileNameD)
        hbox.addWidget(leFileName)
        vbox.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lFlag = QtGui.QLabel("Block Flag:")
        hbox.addWidget(lFlag)
        leFlag = QtGui.QLineEdit(self)
        leFlag.setToolTip(
            "Flag value for the data block.\nIgnored if saveing with header.")
        leFlag.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        leFlag.sizePolicy().setHorizontalStretch(1)
        leFlag.setText(str(self.ExportSettings["Flag"]))
        hbox.addWidget(leFlag)
        vbox.addLayout(hbox)

        cbMakeTxzHeaderIfNeeded = QtGui.QCheckBox("Make TZX Header Block if needed", self)
        cbMakeTxzHeaderIfNeeded.toggle()
        cbMakeTxzHeaderIfNeeded.setChecked(self.ExportSettings["MakeTZXHeader"])
        cbMakeTxzHeaderIfNeeded.setToolTip(
            "Select if you need to add a header block to the TZX file you're exporing to. This is not the header info for the data you're exporting, but an id block at the beginning of a TZX file. Leave it checked if you're not sure")
        vbox.addWidget(cbMakeTxzHeaderIfNeeded)

        w = QtGui.QWidget()
        w.setLayout(vbox)
        tab.addTab(w, "Tape options")

        vbox = QtGui.QVBoxLayout()

        cbFilePosition = QtGui.QComboBox(self)
        cbFilePosition.addItem("Overwrite if file exists or first empty", 0)
        cbFilePosition.addItem("Save at specified position", 1)
        cbFilePosition.addItem("Save in first empty slot", 2)
        cbFilePosition.setToolTip(
            "Which Directory slot do you want to save into?")
        cbFilePosition.setCurrentIndex(self.ExportSettings["FilePosition"])
        cbFilePosition.activated.connect(self.ExportSettingsControlUpdate)
        vbox.addWidget(cbFilePosition)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        hbox.addWidget(QtGui.QLabel("File Name:"))
        leFileNameD = QtGui.QLineEdit(self)
        leFileNameD.setToolTip("Filename to export as.")
        leFileNameD.sizePolicy().setHorizontalPolicy(
            QtGui.QSizePolicy.Expanding)
        leFileNameD.sizePolicy().setHorizontalStretch(1)
        leFileNameD.setText(self.ExportSettings["Filename"])
        leFileNameD.textEdited.connect(self.setleFileName)
        hbox.addWidget(leFileNameD)
        vbox.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lSlot = QtGui.QLabel("Target Slot:")
        hbox.addWidget(lSlot)
        leSlot = QtGui.QLineEdit(self)
        leSlot.setToolTip("Which header slot do you want this file saved \
into.\nValid options are 1 to 80 inclusive.")
        leSlot.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        leSlot.sizePolicy().setHorizontalStretch(1)
        leSlot.setText(str(self.ExportSettings["+DPos"]))
        hbox.addWidget(leSlot)
        vbox.addLayout(hbox)

        w = QtGui.QWidget()
        w.setLayout(vbox)
        tab.addTab(w, "+D/Disciple options")

        box.addWidget(tab)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        hbox.addWidget(ok)
        ok.clicked.connect(self.CheckValidFileName)
        close = QtGui.QPushButton("Cancel", self)
        hbox.addWidget(close)
        close.clicked.connect(dContainer.reject)
        hbox.addStretch(1)

        box.addLayout(hbox)

        dContainer.setLayout(box)

        dContainer.cbSaveWithHeader = cbSaveWithHeader
        dContainer.lFileName = lFileName
        dContainer.leFileName = leFileName
        dContainer.lFlag = lFlag
        dContainer.leFlag = leFlag
        dContainer.cbFilePosition = cbFilePosition
        dContainer.lSlot = lSlot
        dContainer.leSlot = leSlot
        dContainer.leFileNameD = leFileNameD
        self.Ddialog = dContainer

        self.ExportSettingsControlUpdate()

        if dContainer.exec_() == QtGui.QDialog.Accepted:
            self.ExportSettings["ContainerType"] = cbContainerType.\
                currentIndex()
            self.ExportSettings["Flag"] = int(str(leFlag.text()))
            self.ExportSettings["Filename"] = str(leFileName.text())
            self.ExportSettings["AppendOrOver"] = cbOverOrAppend.currentIndex()
            self.ExportSettings["SaveWithHeader"] = cbSaveWithHeader.\
                currentIndex()
            self.ExportSettings["+DPos"] = int(str(leSlot.text()))
            self.ExportSettings["FilePosition"] = cbFilePosition.currentIndex()
            self.ExportSettings["MakeTZXHeader"] = cbMakeTxzHeaderIfNeeded.isChecked()

        del self.Ddialog

    def setleFileNameD(self, text):
        self.Ddialog.leFileNameD.setText(text)

    def setleFileName(self, text):
        self.Ddialog.leFileName.setText(text)

    def ExportSettingsControlUpdate(self):
        i = self.Ddialog.cbSaveWithHeader.currentIndex()
        self.Ddialog.lFileName.setEnabled(i == 1)
        self.Ddialog.leFileName.setEnabled(i == 1)
        self.Ddialog.lFlag.setEnabled(i == 0)
        self.Ddialog.leFlag.setEnabled(i == 0)

        i = self.Ddialog.cbFilePosition.currentIndex()
        self.Ddialog.lSlot.setEnabled(i == 1)
        self.Ddialog.leSlot.setEnabled(i == 1)

    def CheckValidFileName(self):
        try:
            s = spectrumtranslate.getspectrumstring(
                str(self.Ddialog.leFileName.text()))
            if len(s) > 10:
                QtGui.QMessageBox.warning(
                    self, "Error!",
                    "Specrum file names have to be 10 characters or less.")
                return

        except:
            QtGui.QMessageBox.warning(self, "Error!",
                                      "Not valid spectrum string.")
            return

        try:
            f = int(str(self.Ddialog.leFlag.text()))
            if f < 0 or f > 0xFF:
                QtGui.QMessageBox.warning(
                    self, "Error!", "Flag must be from 0 to 255 inclusive.")
                return

        except:
            QtGui.QMessageBox.warning(
                self, "Error!",
                "Flag must be a number from 0 to 255 inclusive.")
            return

        try:
            p = int(str(self.Ddialog.leSlot.text()))
            if p < 1 or p > 80:
                QtGui.QMessageBox.warning(
                    self, "Error!", "Save position must be 1 to 80 inclusive.")
                return

        except:
            QtGui.QMessageBox.warning(
                self, "Error!", "Save position must be 1 to 80 inclusive.")
            return

        self.Ddialog.accept()

    def ExportToContainerChanged(self, state):
        self.SetTranslateButtonText()

    def Translate(self):
        # get data and exit if error
        data = self.GetSelectedData()
        if data is None:
            return

        outputformat = self.cbDataType.currentText()

        # do exporting
        if self.cbExportToContainer.isChecked():
            self.DoExport(data, outputformat)
            return

        # handle images
        if outputformat == "Screen":
            # get image as gif
            delay = self.getNumber(self.leImageDelay)
            if not self.cbImageFlash.isChecked():
                delay = -1

            # display waiting cursor while do translation
            QtGui.QApplication.setOverrideCursor(
                QCursor(QtCore.Qt.WaitCursor))
            data = spectrumtranslate.getgiffromscreen(data, delay)
            QtGui.QApplication.restoreOverrideCursor()

            # was there a problem?
            if data is None:
                QtGui.QMessageBox.warning(
                    self, "Error!",
                    'Unable to extract screen from "{}"'.format(
                        self.leFileNameIn.text()))
                return

            # preview image if needed
            if self.cbViewOutput.isChecked():
                self.DisplayImageDialog("Translation results", data)

            # save image if required
            if self.cbSaveOutput.isChecked():
                self.PutFileData(data, True)

            return

        # handle raw data
        if outputformat == "Raw Data":
            # display raw data if required
            if self.cbViewOutput.isChecked():
                # create dialog
                dContainer = QtGui.QDialog(self)
                dContainer.setWindowTitle("View Raw Data")
                dContainer.setModal(True)

                lay = QtGui.QVBoxLayout()

                lay2 = QtGui.QHBoxLayout()
                lay2.addStretch(1)
                ok = QtGui.QPushButton("Ok", self)
                lay2.addWidget(ok)
                ok.clicked.connect(dContainer.accept)
                lay2.addStretch(1)

                lay3 = QtGui.QHBoxLayout()
                scroll = QtGui.QScrollBar(QtCore.Qt.Vertical)
                hexview = SpectrumFileTranslateGUI.StartStopDisplayPanel(
                    data, 0, len(data), None, scroll)
                lay3.addWidget(hexview)
                hexview.sizePolicy().setHorizontalPolicy(
                    QtGui.QSizePolicy.Expanding)
                hexview.sizePolicy().setHorizontalStretch(1)
                lay3.addWidget(scroll)

                lay.addLayout(lay3)
                lay.addLayout(lay2)

                dContainer.setLayout(lay)

                # set to same size as parent
                dContainer.setGeometry(self.geometry())

                # run dialog
                dContainer.exec_()

            # save data if required
            if self.cbSaveOutput.isChecked():
                self.PutFileData(data, True)

            return

        # handle snapshot
        if outputformat == "Snapshot":
            if len(data) != 131073 and len(data) != 49152:
                QtGui.QMessageBox.warning(
                    self, "Error!",
                    'Snapshot data wrong size for 48K or 128K snapshots.')
                return

            # get requested format
            snapformat = self.cbSnapshotOutput.currentIndex()

            if snapformat == 1 and len(data) == 131073:
                QtGui.QMessageBox.warning(
                    self, "Error!",
                    'Z80 version 1 can only handle 48K snapshots.')
                return

            # if 128K get rid of page byte
            if len(data) == 131073:
                data = data[1:]

            # get registers etc
            di = disciplefile.DiscipleImage(self.leFileNameIn.text())
            di.guessimageformat()
            if di.ImageFormat == "Unknown":
                di.ImageFormat = self.ImageFormatFallback
            df = disciplefile.DiscipleFile(di, self.getNumber(self.leDataFile))
            registers = df.getsnapshotregisters()

            # display waiting cursor while do translation
            QtGui.QApplication.setOverrideCursor(
                QCursor(QtCore.Qt.WaitCursor))
            # get image that's being displayed in snapshot
            # work out where in data image is
            if len(data) == 49152:
                picoffset = 0
            elif registers["Screen"] == 0:
                picoffset = 5 * 0x4000
            else:
                picoffset = 7 * 0x4000

            picdata = spectrumtranslate.getgiffromscreen(
                data[picoffset:picoffset + 6912], 320)
            # convert snapshot to requested format
            try:
                if snapformat == 0:
                    data = spectrumtranslate.snaptosna(data, registers)

                else:
                    data = spectrumtranslate.snaptoz80(data, registers,
                                                       version=snapformat)

            # was there a problem?
            except spectrumtranslate.SpectrumTranslateError as ste:
                QtGui.QMessageBox.warning(self, "Error!", 'Unable to convert \
snapshot. Error:\n{}'.format(ste.value))
                return

            # restore cursor
            QtGui.QApplication.restoreOverrideCursor()

            # preview image from snapshotif needed
            if self.cbViewOutput.isChecked():
                self.DisplayImageDialog("Translation results", picdata)

            # save snapshot if required
            if self.cbSaveOutput.isChecked():
                self.PutFileData(data, True)

            return

        # otherwise translate into text
        s = self.DoTextTranslation(data, outputformat)
        if s is None:
            return

        if self.cbViewOutput.isChecked():
            self.DisplayTranslation(s)

        if self.cbSaveOutput.isChecked():
            self.PutFileData(s)

    def DoExport(self, data, outputformat):
        # check we have output filename
        fileout = self.leFileNameOut.text()
        if not fileout or fileout == "":
            QtGui.QMessageBox.warning(self, "Error!",
                                      'No output file selected.')
            return

        # work out what container format to use
        containertype = self.ExportSettings["ContainerType"]
        # handle working out container type
        if containertype == 3:
            if os.path.isfile(fileout):
                # try to see if is disciple/+D image file
                try:
                    di = disciplefile.DiscipleImage(fileout)
                    di.guessimageformat()

                    # if it's a valid +D file then use this format
                    if di.isimagevalid(True)[0]:
                        containertype = 2

                except:
                    # ignore errors, and fall through into tap check
                    pass

                # try to see if is tap file
                try:
                    if containertype == 3:
                        with open(fileout, 'rb') as f:
                            tbs = [*spectrumtape.gettapblocks(f)]
                            if len(tbs) > 0:
                                containertype = 1
                except:
                    # ignore errors, and fall through into next part of
                    # routine
                    pass

                # try to see if is tzx file
                try:
                    if containertype == 3:
                        with open(fileout, 'rb') as f:
                            tbs = [*spectrumtape.gettzxblocks(f)]
                            if len(tbs) > 0:
                                containertype = 0
                except:
                    # ignore errors, and fall through into next part of
                    # routine
                    pass

                # see if we've not worked out the format and handle this
                if containertype == 2:
                    QtGui.QMessageBox.warning(self, "Error!", '"{}" is not a \
.tap file, .tzx file, or a disciple/+D disk image.'.format(fileout))
                    return

            # what to do if no container file existing to guess format
            else:
                QtGui.QMessageBox.warning(self, "Error!", '"{}" is not a \
file, so cannot guess container format.'.format(fileout))
                return

        # get spectrum file filename
        filename = spectrumtranslate.stringtospectrum(
            self.ExportSettings["Filename"])

        # todo remove when have support for snap files, opentype files
        # etc that are bigger than 64K
        # check if file is greater than 0xFFFF: won't fit in file if is.
        if len(data) > 0xFFFF:
            QtGui.QMessageBox.warning(
                self, "Error!",
                "Data is bigger than 65535 bytes and can't be saved.")
            return None

        # handle tape file
        if containertype in [0, 1]:
            fileformat = 'Tap' if containertype == 1 else 'Tzx'
            output = ''
            if self.ExportSettings["SaveWithHeader"] == 1:
                if outputformat == "Basic Program":
                    auto = self.getNumber(self.leBasicAutoLine)
                    variableoffset = self.getNumber(self.leBasicVariableOffset)
                    headerblock = spectrumtape.createbasicheader(
                        filename, variableoffset, len(data), auto)

                elif outputformat == "Machine Code":
                    origin = self.getNumber(self.leCodeOrigin)
                    if origin < 0 or origin > 0xFFFF:
                        QtGui.QMessageBox.warning(self, "Error!", "Code \
Origin must be between 0 and 65535 (0000 and FFFF hexadecimal).")
                        return None

                    headerblock = spectrumtape.createcodeheader(
                        filename, origin, len(data))

                elif outputformat == "Variable Array":
                    idescriptor = self.cbArrayVarType.currentIndex()
                    idescriptor += 2
                    idescriptor -= (idescriptor >> 2) * 3
                    idescriptor *= 64

                    sVarName = str(self.leArrayVarName.text()).lower()
                    if len(sVarName) != 1 or ord(sVarName) < 97 or ord(sVarName) > 122:
                        QtGui.QMessageBox.warning(
                            self, "Error!",
                            "Variable Name must be single letter.")
                        return None

                    headerblock = spectrumtape.createarrayheader(
                        filename, idescriptor | (ord(sVarName) & 0x3F),
                        len(data))

                elif outputformat == "Screen":
                    headerblock = spectrumtape.createscreenheader(filename)

                output = spectrumtape.convertblockformat(
                    headerblock, fileformat).getpackagedforfile()

            output += spectrumtape.convertblockformat(
                spectrumtape.createdatablock(
                data,
                0xFF if self.ExportSettings["SaveWithHeader"] == 1 else
                self.ExportSettings["Flag"]), fileformat).getpackagedforfile()

            # if tzx file ensure have header if new file
            if containertype == 0 and (self.ExportSettings["AppendOrOver"] == 0 or (not os.path.isfile(fileout) or os.path.getsize(fileout) == 0)) and self.ExportSettings["MakeTZXHeader"]:
                output = spectrumtape.SpectrumTZXHeaderBlock(1, 20).getpackagedforfile() + output

            # prepare data for output
            output = bytes(output)

            try:
                with open(
                    fileout,
                    MODE_AB if self.ExportSettings["AppendOrOver"] == 1 else
                    MODE_WB) as fo:
                    fo.write(output)
            except:
                QtGui.QMessageBox.warning(
                    self, "Error!",
                    'Failed to save data to "{}"'.format(fileout))

            return

        # otherwise handle +D/disciple

        # create output image to copy into
        diout = disciplefile.DiscipleImage()
        # if we're writing to an existing file then load it into image
        if os.path.isfile(fileout):
            try:
                with open(fileout, MODE_RB) as outfile:
                    diout.setbytes(outfile.read())
            except:
                QtGui.QMessageBox.warning(
                    self, "Error!",
                    'Failed to save data to "{}"'.format(fileout))
        # otherwise create blank image
        elif containertype == 2:
            diout.setbytes([0] * 819200)

        # get where to save directory entry and whether to overwrite
        copyposition = self.ExportSettings["+DPos"] if self.ExportSettings[
            "FilePosition"] == 1 else -1
        overwritename = self.ExportSettings["FilePosition"] == 0

        if outputformat == "Basic Program":
            auto = self.getNumber(self.leBasicAutoLine)
            variableoffset = self.getNumber(self.leBasicVariableOffset)
            diout.writebasicfile(data, filename, position=copyposition,
                                 autostartline=auto,
                                 varposition=variableoffset,
                                 overwritename=overwritename)

        elif outputformat == "Machine Code":
            origin = self.getNumber(self.leCodeOrigin)
            if origin < 0 or origin > 0xFFFF:
                QtGui.QMessageBox.warning(self, "Error!", "Code Origin must \
be between 0 and 65535 (0000 and FFFF hexadecimal).")
                return None

            diout.writecodefile(data, filename, position=copyposition,
                                codestartaddress=origin,
                                overwritename=overwritename)

        elif outputformat == "Variable Array":
            idescriptor = self.cbArrayVarType.currentIndex()
            idescriptor += 2
            idescriptor -= (idescriptor >> 2) * 3
            idescriptor *= 64

            sVarName = str(self.leArrayVarName.text()).lower()
            if len(sVarName) != 1 or ord(sVarName) < 97 or ord(sVarName) > 122:
                QtGui.QMessageBox.warning(
                    self, "Error!", "Variable Name must be single letter.")
                return None

            diout.writearrayfile(data, filename,
                                 idescriptor | (ord(sVarName) & 0x3F),
                                 position=copyposition,
                                 overwritename=overwritename)

        elif outputformat == "Screen":
            diout.writescreenfile(data, filename, position=copyposition,
                                  overwritename=overwritename)

        # not standard file so treat as code
        else:
            diout.writecodefile(data, filename, position=copyposition,
                                codestartaddress=0,
                                overwritename=overwritename)

        # prepare data for output
        output = bytes(diout.bytedata)

        # output data
        try:
            with open(fileout, MODE_WB) as fo:
                fo.write(output)
        except:
            QtGui.QMessageBox.warning(
                self, "Error!",
                'Failed to save data to "{}"'.format(fileout))

    def DisplayImageDialog(self, title, imagedata):
        # create dialog to display image
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Translation results")
        dContainer.setModal(True)

        # create label to hold gif (which might be animated)
        pic = QtGui.QLabel()
        buf = QtCore.QBuffer()
        buf.open(QtCore.QIODevice.ReadWrite)

        buf.write(bytes(imagedata))

        buf.seek(0)
        movie = QMovie(buf, QtCore.QByteArray())
        pic.setMovie(movie)
        movie.start()

        # set out dialog
        pic.setAlignment(QtCore.Qt.AlignCenter)

        lay = QtGui.QVBoxLayout()

        lay.addWidget(pic)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        ok.clicked.connect(dContainer.accept)
        hbox.addWidget(ok)
        hbox.addStretch(1)
        lay.addLayout(hbox)

        dContainer.setLayout(lay)

        dContainer.exec_()

    def DoTextTranslation(self, data, datatype):
        if datatype == "Basic Program":
            # get program variables
            auto = self.getNumber(self.leBasicAutoLine)
            variable = self.getNumber(self.leBasicVariableOffset)
            length = len(data)
            if variable < 0 or variable > length:
                variable = length

            try:
                forceascii = self.cbASCIIBasicOutput.isChecked()
                # handle XML
                if self.cbXMLBasicOutput.isChecked() == True:
                    return spectrumtranslate.basictoxml(data, auto, variable,
                                                        forceascii)

                # default to simple text
                return spectrumtranslate.basictotext(data, auto, variable,
                                                     forceascii)
            except spectrumtranslate.SpectrumTranslateError as ste:
                QtGui.QMessageBox.warning(self, "Error!", ste.value)
                return None

        elif datatype == "Machine Code":
            origin = self.getNumber(self.leCodeOrigin)
            if origin < 0 or origin > 0xFFFF:
                QtGui.QMessageBox.warning(self, "Error!", "Code Origin must \
be between 0 and 65535 (0000 and FFFF hexadecimal).")
                return None

            # get format instructions
            iFormat = self.cbCodeFormat.currentIndex()
            iOutputTimes = self.cbCodeTimes.currentIndex()
            iOutputJumpGap = self.cbCodeJump.currentIndex()
            bListFlags = self.cbCodeFlags.isChecked()
            bListUndocumented = self.cbCodeUndocumented.isChecked()
            bXMLOutput = self.cbXMLOutput.isChecked()

            self.diInstructions[0] = spectrumtranslate.\
                DisassembleInstruction(
                    spectrumtranslate.DisassembleInstruction.
                    DISASSEMBLE_CODES["Custom Format"],
                    0,
                    0xFFFF,
                    spectrumtranslate.get_custom_format_string(
                        iFormat,
                        iFormat,
                        iFormat,
                        iOutputTimes,
                        iOutputJumpGap,
                        spectrumtranslate.DisassembleInstruction.
                        DISASSEMBLE_CODES["Line Numbers Referenced"],
                        16,
                        spectrumtranslate.DisassembleInstruction.
                        DISASSEMBLE_CODES["Empty Line After Data On"],
                        spectrumtranslate.DisassembleInstruction.
                        DISASSEMBLE_CODES["Reference Data Numbers On"],
                        spectrumtranslate.DisassembleInstruction.
                        DISASSEMBLE_CODES["List Command Bytes On"],
                        spectrumtranslate.DisassembleInstruction.
                        DISASSEMBLE_CODES["Comments On"],
                        spectrumtranslate.DisassembleInstruction.
                        DISASSEMBLE_CODES["Seperators Space"],
                        spectrumtranslate.DisassembleInstruction.
                        DISASSEMBLE_CODES[
                            "Display Flags On" if bListFlags else
                            "Display Flags Off"],
                        spectrumtranslate.DisassembleInstruction.
                        DISASSEMBLE_CODES[
                            "Mark Undocumented Command On" if
                            bListUndocumented else
                            "Mark Undocumented Command Off"],
                        spectrumtranslate.DisassembleInstruction.
                        DISASSEMBLE_CODES[
                            "XML Output On" if bXMLOutput else
                            "XML Output Off"],
                        spectrumtranslate.DisassembleInstruction.
                        DISASSEMBLE_CODES["Hex instead of non-ASCII Off"]))

            return self.DisassembleDialog(data, origin)

        elif datatype == "Variable Array":
            idescriptor = self.cbArrayVarType.currentIndex()
            idescriptor += 2
            idescriptor -= (idescriptor >> 2) * 3
            idescriptor *= 64

            sVarName = str(self.leArrayVarName.text()).lower()
            if len(sVarName) != 1 or ord(sVarName) < 97 or ord(sVarName) > 122:
                QtGui.QMessageBox.warning(
                    self, "Error!", "Variable Name must be single letter.")
                return None

            forceascii = self.cbASCIIVarOutput.isChecked()
            # handle XML
            if self.cbXMLVarOutput.isChecked() == True:
                if idescriptor & 192 == 64:
                    vartype = 'string'
                elif idescriptor & 192 == 128:
                    vartype = 'numberarray'
                elif idescriptor & 192 == 192:
                    vartype = 'characterarray'

                soutput = '<?xml version="1.0" encoding="UTF-8" ?>\n'
                soutput += '<variable>\n  <name>' + sVarName
                if idescriptor & 64 == 64:
                    soutput += '$'

                soutput += '</name>\n  <type>' + vartype + '</type>\n'
                soutput += '  <value>\n'
                soutput += '\n'.join(['    ' + x for x in
                                      spectrumtranslate.arraytoxml(
                                          data, idescriptor,
                                          forceascii).splitlines()])
                soutput += '\n  </value>\n</variable>\n'

                return soutput

            # default to simple text
            return sVarName + ("" if idescriptor == 128 else "$") + \
                ("" if idescriptor == 64 else "[]") + \
                "=\n" + spectrumtranslate.arraytotext(data, idescriptor,
                                                      forceascii)

        else:
            return "Error!"

    def DisassembleDialog(self, data, origin):
        # create dialog
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Disassembling")
        dContainer.setModal(True)

        lay = QtGui.QVBoxLayout()

        lWhatDoing = QtGui.QLabel("Waiting to start.")
        lay.addWidget(lWhatDoing)
        dContainer.lWhatDoing = lWhatDoing

        pbCurrentJob = QtGui.QProgressBar()
        pbCurrentJob.setMinimum(0)
        pbCurrentJob.setMaximum(100)
        lay.addWidget(pbCurrentJob)
        dContainer.pbCurrentJob = pbCurrentJob

        lay.addWidget(QtGui.QLabel("Total complete:"))

        pbTotal = QtGui.QProgressBar()
        pbTotal.setMinimum(0)
        pbTotal.setMaximum(100)
        lay.addWidget(pbTotal)
        dContainer.pbTotal = pbTotal

        # todo:
        # There's a problem with Abort button not responding.
        # Haven't been able to figure it out just yet, but otherwise it
        # works so comment out for now.

        # bStop = QtGui.QPushButton("Abort", self)
        # bStop.clicked.connect(self.AbortDisassembly)
        # lay.addWidget(bStop)

        dContainer.setLayout(lay)

        self.progressdialog = dContainer

        dContainer.result = None

        # start disassembly thread
        dContainer.t = SpectrumFileTranslateGUI.DisassemblerThread(self, data,
                                                                   origin)

        # start dialog
        dContainer.exec_()

        del self.progressdialog

        return dContainer.result

    def AbortDisassembly(self):
        dContainer = self.progressdialog
        dContainer.t.Stop()
        dContainer.reject()

    def DisassembleFinished(self):
        if self.progressdialog.error:
            QtGui.QMessageBox.warning(self, "Error!",
                                      self.progressdialog.error)

        # close dialog
        self.progressdialog.reject()

    def StatusUpdate(self):
        dContainer = self.progressdialog
        dContainer.lWhatDoing.setText(dContainer.update[0])

        dContainer.pbCurrentJob.setValue(dContainer.update[1])
        dContainer.pbCurrentJob.setMaximum(dContainer.update[2])

        dContainer.pbTotal.setValue(dContainer.update[3])
        dContainer.pbTotal.setMaximum(dContainer.update[4])

    def DisplayTranslation(self, txt):
        # create dialog to display image
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Translation results")
        dContainer.setModal(True)

        # create label to hold gif (which might be animated)
        textdisplay = QtGui.QTextEdit()
        textdisplay.setPlainText(txt)
        textdisplay.setReadOnly(True)
        textdisplay.myfont = QFont('monospace',
                                   int(round(textdisplay.fontPointSize())))
        textdisplay.setFont(textdisplay.myfont)

        lay = QtGui.QVBoxLayout()
        lay.addWidget(textdisplay)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        ok.clicked.connect(dContainer.accept)
        hbox.addWidget(ok)
        hbox.addStretch(1)
        lay.addLayout(hbox)

        dContainer.setLayout(lay)

        dContainer.setGeometry(self.geometry())

        dContainer.exec_()

    def PutFileData(self, data, isbinary=False):
        fileout = self.leFileNameOut.text()
        if not fileout or fileout == "":
            QtGui.QMessageBox.warning(self, "Error!",
                                      'No output file selected.')
            return

        # prepare data for output
        if isinstance(data, str):
            data = bytes([ord(b) for b in data])
        elif isinstance(data, (list, tuple)):
            data = bytes(data)

        try:
            with open(fileout, MODE_WB) as fo:
                if isbinary:
                    fo.write(data)
                else:
                    fo.write(data.encode('utf-8'))
        except:
            QtGui.QMessageBox.warning(
                self, "Error!", 'Failed to save data to "{}"'.format(fileout))

    def GetSelectedData(self):
        # first check if is +d/disciple file as go by file number rather
        # than start & stop
        if self.bBrowseContainer.text() == "Browse disk image":
            i = self.getNumber(self.leDataFile)
            o = self.getNumber(self.leDataFileOffset)

            if i < 1 or i > 80:
                QtGui.QMessageBox.warning(
                    self, "Error!",
                    'Valid file numbers are 1 to 80 inclusive.')
                return None

            if o < 0:
                QtGui.QMessageBox.warning(self, "Error!",
                                          'Valid offsets are 0 and above.')
                return None

            try:
                # get disciple file object
                di = disciplefile.DiscipleImage(self.leFileNameIn.text())
                di.guessimageformat()
                if di.ImageFormat == "Unknown":
                    di.ImageFormat = self.ImageFormatFallback
                df = disciplefile.DiscipleFile(di, i)
                # return it's data, ignoreing any offset
                return (df.getfiledata(True))[o:]
            except:
                QtGui.QMessageBox.warning(self, "Error!", 'Failed to extract \
file {} from "{}".'.format(i, self.leFileNameIn.text()))
                return None

        offset = self.getNumber(self.leDataOffset)
        end = self.getNumber(self.leDataEnd) + 1
        length = end - offset

        # sanity check for inputs
        if offset < 0 or end < 0 or offset > end or length > 65535:
            QtGui.QMessageBox.warning(
                self, "Error!", 'invalid data offset or data end parameters')
            return None

        filein = self.leFileNameIn.text()
        if not os.path.isfile(filein):
            QtGui.QMessageBox.warning(self, "Error!",
                                      '"{}" does not exist.'.format(filein))
            return None

        # get contents of file
        try:
            with open(filein, MODE_RB) as fo:
                fo.seek(offset)
                data = fo.read(length)
        except:
            QtGui.QMessageBox.warning(
                self, "Error!", 'Unable to get data from "{}"'.format(filein))
            return None

        # ensure data is converted to valid format
        data = _validbytestointlist(data)

        if len(data) != length:
            QtGui.QMessageBox.warning(
                self, "Error!", 'Unable to get data from "{}"'.format(filein))
            return None

        return data

    def DataTypeChange(self, datatype):
        self.settingsstack.setCurrentIndex(datatype)
        self.SetTranslateButtonText()

    def SetTranslateButtonText(self):
        if self.cbExportToContainer.isChecked():
            self.bTranslate.setText("Export")
            self.bExportSettings.setEnabled(True)
        else:
            self.bTranslate.setText(("Translate", "Translate", "Translate",
                                     "Translate", "Extract", "Convert"
                                     )[self.cbDataType.currentIndex()])
            self.bExportSettings.setEnabled(False)

    def FormatChange(self, newformat):
        # we're done if no change
        if self.CurrentNumberFormat == newformat:
            return

        # go through all the boxes changing text formats
        self.SetNewNumberFormat(self.leDataOffset)
        self.SetNewNumberFormat(self.leDataEnd)
        self.SetNewNumberFormat(self.leDataFile)
        self.SetNewNumberFormat(self.leDataFileOffset)
        self.SetNewNumberFormat(self.leBasicAutoLine)
        self.SetNewNumberFormat(self.leBasicVariableOffset)
        self.SetNewNumberFormat(self.leCodeOrigin)

        # update current format
        self.CurrentNumberFormat = newformat

    def SetNewNumberFormat(self, le):
        val = self.getNumber(le)

        le.setText("" if val < 0 else self.FormatNumber(val))

    def getNumber(self, le):
        try:
            # get old value adjusting for number format
            return int(str(le.text()),
                       [16, 10, 8, 2][self.CurrentNumberFormat])

        except:
            # if there's any error (or blank: not ment to have a
            # number), return -1
            return -1

    # browse files in disciple image file
    def BrowseDiscipleImageFile(self):
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Select what to translate")
        dContainer.setModal(True)

        Dview = QtGui.QListView()
        Dview.myfont = QFont('monospace', 10)
        Dview.setFont(Dview.myfont)
        maxwidth = 0

        Dmodel = QStandardItemModel()

        di = disciplefile.DiscipleImage(self.leFileNameIn.text())
        di.guessimageformat()
        if di.ImageFormat == "Unknown":
            di.ImageFormat = self.ImageFormatFallback

        for df in di.iteratedisciplefiles():
            # do we have a valid entry?
            if not df.isempty():
                txt = '{filenumber:2} "{filename:s}"{sectors:4} \
{filetypeshort} {catextradata}'.format(**df.getfiledetails())
                maxwidth = max(Dview.fontMetrics().width(txt), maxwidth)
                line = QStandardItem(txt)
                line.Ddata = df
                line.setEditable(False)
                faults = df.checkforfaults()
                if faults:
                    line.setBackground(QColor(255,128,128))
                    line.setToolTip("\n".join(faults))
                Dmodel.appendRow(line)

        Dview.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        Dview.setModel(Dmodel)

        lay = QtGui.QVBoxLayout()

        lay.addWidget(Dview)

        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        lay2.addWidget(ok)
        ok.clicked.connect(self.DiscipleEntrySelected)
        lay2.addStretch(1)
        close = QtGui.QPushButton("Cancel", self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)
        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        Dview.doubleClicked.connect(self.DiscipleEntrySelected)

        # ensure first item is always selected
        Dview.selectionModel().select(Dmodel.createIndex(0, 0),
                                      QItemSelectionModel.Select)

        # remember Dview and dialog
        self.Ddialog = dContainer
        self.Dview = Dview

        dContainer.show()
        Dview.setMinimumWidth(maxwidth + Dview.verticalScrollBar().width() +
                              15)

        # run dialog, but forget Dview and dialog references if cancel
        # pressed
        if dContainer.exec_() == QtGui.QDialog.Rejected:
            del self.Ddialog
            del self.Dview

    def DiscipleEntrySelected(self, x):
        # retrieve references to what we need
        Dview = self.Dview
        Ddialog = self.Ddialog

        # check to see if faulty entry selected
        if len(Dview.selectedIndexes()) > 0:
            # retrieve Ddata
            index = Dview.selectedIndexes()[0]
            df = index.model().itemFromIndex(index).Ddata
            # check
            if df.checkforfaults():
                QtGui.QMessageBox.warning(self, "Error",
                    "Selected file is faulty and can't be extracted")
                return

        # tidy up self
        del self.Ddialog
        del self.Dview

        # close dialog
        Ddialog.accept()

        # if nothing selected then exit
        if len(Dview.selectedIndexes()) < 1:
            return

        header = df.getheader()
        t = df.getfiletype(header)

        # set filenumber and offset (remmbering that basic, code, screen
        # number and character array
        # have a 9 byte header at the start of the file
        self.SetSourceLimits(-1, -1, df.filenumber,
                             9 if ((t > 0 and t < 5) or t == 7) else 0)

        # save off filename incase want to export it
        self.ExportSettings["Filename"] = ''.join(
            [chr(x) for x in df.getrawfilename()])

        if t == 1:
            # basic program
            self.SetBasicDetails(df.getautostartline(header),
                                 df.getvariableoffset(header))

        elif t in [2, 3]:
            # number or character array
            self.SetVariableArrayDetails(df.getvariableletter(header),
                                         df.getarraydescriptor(header))

        elif t == 4:
            # bytes: can be screen or data/machine code
            if df.getfilelength(header) == 6912:
                self.SetScreenDetails(df.getcodestart(header))

            else:
                self.SetCodeDetails(df.getcodestart(header))

        elif t == 5:
            # 48K Snapshot
            self.SetSnapshotDetails(False)

        elif t == 7:
            # SCREEN$
            self.SetScreenDetails(df.getcodestart(header))

        elif t == 7:
            # Execute
            self.SetCodeDetails(df.getcodestart(header))

        elif t == 9:
            # 128K Snapshot
            self.SetSnapshotDetails(True)

        else:
            # microdrive(6), special(8), and opentype(10) all default to
            # raw data
            # treat as raw data extract for now
            self.SetRawData()

    # browse files in TAP file
    def BrowseTapeFile(self):
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Select what to translate")
        dContainer.setModal(True)

        tapmodel = QStandardItemModel()
        tapmodel.setHorizontalHeaderLabels(['Tape Entries'])

        with open(self.leFileNameIn.text(), 'rb') as f:
            if self.bBrowseContainer.text() == "Browse TAP":
                tbs = [*spectrumtape.nexttapblock(f)]
            else:
                tbs = [*spectrumtape.nexttzxblock(f)]
        i = 0
        while i < len(tbs):
            # do we have a header that matches the next code block?
            if (i < len(tbs) - 1 and tbs[i].isheader() and
               tbs[i + 1].isdatablock() and tbs[i + 1].flag == 255 and
               tbs[i + 1].getpayloadlength() == tbs[i].getheaderdescribeddatalength()):
                block = QStandardItem(tbs[i].getblockinfo())
                block.tapdata = tbs[i:i + 2]
                line = QStandardItem(str(tbs[i]))
                line.tapdata = tbs[i:i + 1]
                line.setEditable(False)
                block.appendRow(line)
                line = QStandardItem(str(tbs[i + 1]))
                line.tapdata = tbs[i + 1:i + 2]
                line.setEditable(False)
                block.appendRow(line)
                block.setEditable(False)
                i += 2
                tapmodel.appendRow(block)
            # if not treat it as simple block of data
            else:
                line = QStandardItem(str(tbs[i]))
                line.tapdata = tbs[i:i + 1]
                line.setEditable(False)
                tapmodel.appendRow(line)
                i += 1

        tapview = QtGui.QTreeView()
        tapview.myfont = QFont('monospace', 10)
        tapview.setFont(tapview.myfont)
        tapview.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        tapview.setModel(tapmodel)
        tapview.setUniformRowHeights(True)

        lay = QtGui.QVBoxLayout()

        lay.addWidget(tapview)

        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok = QtGui.QPushButton("Ok", self)
        lay2.addWidget(ok)
        ok.clicked.connect(self.TapeEntrySelected)
        lay2.addStretch(1)
        close = QtGui.QPushButton("Cancel", self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)
        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        tapview.doubleClicked.connect(self.TapeEntrySelected)
        tapview.setExpandsOnDoubleClick(False)

        # ensure first item is always selected
        tapview.selectionModel().select(tapmodel.createIndex(0, 0),
                                        QItemSelectionModel.Select)

        # remember tapview and dialog
        self.tapdialog = dContainer
        self.tapview = tapview

        # run dialog, but forget tapview and dialog references if cancel
        # pressed
        if dContainer.exec_() == QtGui.QDialog.Rejected:
            del self.tapdialog
            del self.tapview

    def BrowseFileHex(self):

        if not os.path.isfile(self.leFileNameIn.text()):
            return

        # get contents of file
        try:
            with open(self.leFileNameIn.text(), MODE_RB) as fo:
                data = _validbytestointlist(fo.read())
        except:
            QtGui.QMessageBox.warning(
                self, "Error",
                'Unable to read file:\n"{}"'.format(self.leFileNameIn.text()))
            return

        # create dialog
        dContainer = QtGui.QDialog(self)
        dContainer.setWindowTitle("Select start & end")
        dContainer.setModal(True)

        lay = QtGui.QVBoxLayout()

        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch(1)

        select_group = QtGui.QButtonGroup(dContainer)
        rb0 = QtGui.QRadioButton("Select start")
        rb0.setChecked(True)
        lay2.addWidget(rb0)
        select_group.addButton(rb0)
        rb1 = QtGui.QRadioButton("Select end")
        lay2.addWidget(rb1)
        select_group.addButton(rb1)

        ok = QtGui.QPushButton("Ok", self)
        lay2.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close = QtGui.QPushButton("Cancel", self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay3 = QtGui.QHBoxLayout()
        scroll = QtGui.QScrollBar(QtCore.Qt.Vertical)
        hexview = SpectrumFileTranslateGUI.StartStopDisplayPanel(
            data, self.getNumber(self.leDataOffset),
            self.getNumber(self.leDataEnd), rb0, scroll)
        lay3.addWidget(hexview)
        hexview.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        hexview.sizePolicy().setHorizontalStretch(1)
        lay3.addWidget(scroll)

        lay.addLayout(lay3)
        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        # set to same size as parent
        dContainer.setGeometry(self.geometry())

        # run dialog, and if ok selected get start & stop points
        if dContainer.exec_() == QtGui.QDialog.Accepted:
            self.SetSourceLimits(hexview.selectStart,
                                 hexview.selectEnd - hexview.selectStart)

    def TapeEntrySelected(self, x):
        # retrieve references to what we need
        tapview = self.tapview
        tapdialog = self.tapdialog
        # tidy up self
        del self.tapdialog
        del self.tapview

        # close dialog
        tapdialog.accept()

        # if nothing selected then exit
        if len(tapview.selectedIndexes()) < 1:
            return

        # retrieve tapdata
        index = tapview.selectedIndexes()[0]
        tapdata = index.model().itemFromIndex(index).tapdata

        # if only 1 tap block then is individual tapblock. treat as code
        if len(tapdata) == 1:
            # set values
            self.SetSourceLimits(tapdata[0].getpayloadstartoffset(),
                                 tapdata[0].getpayloadlength())
            self.SetCodeDetails(0)

            return

        # if not then should contain 2 TapBlocks: header & data block.
        self.SetSourceLimits(tapdata[1].getpayloadstartoffset(),
                             tapdata[1].getpayloadlength(), -1)

        # save off filename incase want to export it
        self.ExportSettings["Filename"] = ''.join(
            [chr(x) for x in tapdata[0].getrawfilename()])

        if tapdata[0].getpayload()[0] == 0:
            # basic program
            self.SetBasicDetails(tapdata[0].getheaderautostartline(),
                                 tapdata[0].getheadervariableoffset())

        elif tapdata[0].getpayload()[0] in [1, 2]:
            # number or character array
            self.SetVariableArrayDetails(tapdata[0].getheadervariableletter(),
                                         tapdata[0].getheaderarraydescriptor()
                                         )

        elif tapdata[0].getpayload()[0] == 3:
            # bytes: can be screen or data/machine code
            if tapdata[1].getpayloadlength() == 6912:
                self.SetScreenDetails(tapdata[0].getheadercodestart())

            else:
                self.SetCodeDetails(tapdata[0].getheadercodestart())

        else:
            # default to code block
            self.SetCodeDetails(0)

    def SetSourceLimits(self, datastartoffset, datalength, filenumber=-1,
                        fileoffset=0):
        self.leDataOffset.setText(self.FormatNumber(datastartoffset))
        self.leDataEnd.setText("" if datalength == -1 else
                               self.FormatNumber(datastartoffset + datalength -
                                                 1))
        self.leDataFile.setText(self.FormatNumber(filenumber))
        self.leDataFileOffset.setText("" if filenumber == -1 else
                                      self.FormatNumber(fileoffset))

    def SetSnapshotDetails(self, is128):
        self.leBasicAutoLine.setText("")
        self.leBasicVariableOffset.setText("")
        self.leArrayVarName.setText("")
        self.leCodeOrigin.setText(self.FormatNumber(0))
        self.cbDataType.removeItem(5)
        self.cbDataType.addItem("Snapshot", 5)
        _setcombo(self.cbDataType, "Snapshot")
        self.gbSnap.setTitle("128K Snapshot" if is128 else "48K Snapshot")
        self.SetTranslateButtonText()
        self.settingsstack.setCurrentIndex(5)

    def SetCodeDetails(self, origin):
        self.leBasicAutoLine.setText("")
        self.leBasicVariableOffset.setText("")
        self.leArrayVarName.setText("")
        self.leCodeOrigin.setText(self.FormatNumber(origin))
        _setcombo(self.cbDataType, "Machine Code")
        self.SetTranslateButtonText()
        self.settingsstack.setCurrentIndex(1)
        self.cbDataType.model().item(5).setEnabled(False)

    def SetScreenDetails(self, origin):
        self.leBasicAutoLine.setText("")
        self.leBasicVariableOffset.setText("")
        self.leArrayVarName.setText("")
        self.leCodeOrigin.setText(self.FormatNumber(origin))
        _setcombo(self.cbDataType, "Screen")
        self.SetTranslateButtonText()
        self.settingsstack.setCurrentIndex(3)
        self.cbDataType.model().item(5).setEnabled(False)

    def SetVariableArrayDetails(self, variableletter, arraydescriptor):
        self.leBasicAutoLine.setText("")
        self.leBasicVariableOffset.setText("")
        self.leArrayVarName.setText(
            spectrumtranslate.getspectrumchar(variableletter))
        i = arraydescriptor
        i //= 64
        i += 1
        i %= 3
        self.cbArrayVarType.setCurrentIndex(i)
        self.leCodeOrigin.setText(self.FormatNumber(0))
        _setcombo(self.cbDataType, "Variable Array")
        self.SetTranslateButtonText()
        self.settingsstack.setCurrentIndex(2)
        self.cbDataType.model().item(5).setEnabled(False)

    def SetBasicDetails(self, autoline, variableoffset):
        self.leBasicAutoLine.setText("" if (autoline < 0) else
                                     self.FormatNumber(autoline))
        self.leBasicVariableOffset.setText(self.FormatNumber(variableoffset))
        self.leArrayVarName.setText("")
        self.leCodeOrigin.setText(self.FormatNumber(0))
        _setcombo(self.cbDataType, "Basic Program")
        self.SetTranslateButtonText()
        self.settingsstack.setCurrentIndex(0)
        self.cbDataType.model().item(5).setEnabled(False)

    def SetRawData(self):
        self.leBasicAutoLine.setText("")
        self.leBasicVariableOffset.setText("")
        self.leArrayVarName.setText("")
        self.leCodeOrigin.setText(self.FormatNumber(0))
        _setcombo(self.cbDataType, "Raw Data")
        self.SetTranslateButtonText()
        self.settingsstack.setCurrentIndex(4)
        self.cbDataType.model().item(5).setEnabled(False)

    def FormatNumber(self, n):
        if n == -1:
            return ""

        # format provided number to current number format
        form = ('{0:X}', '{0:d}', '{0:o}', '{0:b}')[self.cbNumberFormat.
                                                    currentIndex()]

        return form.format(n)

    def handle_changed_text(self, txt):
        if self.leFileNameIn.hasFocus():
            self.CheckIfKnownContainerFile()

    def CheckIfKnownContainerFile(self):
        if os.path.isfile(self.leFileNameIn.text()):

            self.bBrowseHex.setEnabled(True)

            # try extracting from tzx file
            try:
                with open(self.leFileNameIn.text(), 'rb') as f:
                    tbs = [*spectrumtape.nexttzxblock(f)]
                    if len(tbs) > 0:
                        self.bBrowseContainer.setText("Browse TZX")
                        self.bBrowseContainer.setEnabled(True)
                        return
            except IOError:
                pass

            # try extracting from tap file
            try:
                with open(self.leFileNameIn.text(), 'rb') as f:
                    tbs = [*spectrumtape.nexttapblock(f)]
                    if len(tbs) > 0:
                        self.bBrowseContainer.setText("Browse TAP")
                        self.bBrowseContainer.setEnabled(True)
                        return
            except IOError:
                tbs = []

            # display waiting cursor while do translation
            QtGui.QApplication.setOverrideCursor(
                QCursor(QtCore.Qt.WaitCursor))

            # try from disciple/+D image file
            try:
                di = disciplefile.DiscipleImage(self.leFileNameIn.text())
                di.guessimageformat()
                self.ImageFormatFallback = di.ImageFormat

                # handle definately valid disciple/+D image
                if di.isimagevalid(True)[0]:
                    QtGui.QApplication.restoreOverrideCursor()
                    self.bBrowseContainer.setText("Browse disk image")
                    self.bBrowseContainer.setEnabled(True)
                    return

                # check if could possibly be image file
                if di.couldbeimage:
                    di.ImageFormat = "MGT"
                    mgtErrors = di.isimagevalid(True)[1]
                    di.ImageFormat = "IMG"
                    imgErrors = di.isimagevalid(True)[1]
                    QtGui.QApplication.restoreOverrideCursor()

                    qb = QtGui.QMessageBox()
                    qb.setIcon(QtGui.QMessageBox.Question)
                    qb.setText("Cannot determine +D/Disciple image format")
                    qb.setInformativeText("There are errors with each format.\
<br>Please choose image format or HEX to view raw file:")
                    qb.setWindowTitle("Indeterminate image file")
                    mgtbutton = qb.addButton('MGT',
                                             QtGui.QMessageBox.AcceptRole)
                    imgbutton = qb.addButton('IMG', QtGui.QMessageBox.NoRole)
                    qb.addButton('HEX', QtGui.QMessageBox.RejectRole)
                    if imgErrors.count('\n') > mgtErrors.count('\n'):
                        qb.setDefaultButton(mgtbutton)
                        qb.setDetailedText("""In MGT format, the errors were:
""" + mgtErrors + "\n\nIn IMG format, the errors were:\n" + imgErrors)
                    else:
                        qb.setDefaultButton(imgbutton)
                        qb.setDetailedText("""In IMG format, the errors were:
""" + imgErrors + "\n\nIn MGT format, the errors were:\n" + mgtErrors)
    	
                    i = qb.exec_()
                    if i == QtGui.QMessageBox.AcceptRole:
                        self.ImageFormatFallback = "MGT"
                        self.bBrowseContainer.setText("Browse disk image")
                        self.bBrowseContainer.setEnabled(True)
                        return
                    if i == QtGui.QMessageBox.RejectRole:
                        self.ImageFormatFallback = "IMG"
                        self.bBrowseContainer.setText("Browse disk image")
                        self.bBrowseContainer.setEnabled(True)
                        return
                else:
                    QtGui.QApplication.restoreOverrideCursor()

            except:
                # ignore errors, and fall through into further browsing
                # options
                QtGui.QApplication.restoreOverrideCursor()

        else:
            self.bBrowseHex.setEnabled(False)

        self.bBrowseContainer.setText("Browse contents")
        self.bBrowseContainer.setEnabled(False)


def main(fileToOpen=None):

    app = QtGui.QApplication(sys.argv)

    sftGUI = SpectrumFileTranslateGUI(fileToOpen)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
