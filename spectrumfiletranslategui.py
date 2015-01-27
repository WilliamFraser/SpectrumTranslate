# This file is part of the SpectrumTranslate python module.
#
# It's licenced under GPL version 3 (www.gnu.org/licenses/gpl.html) with a few extra stipulations:
# 1) These first lines in this file as far as the line with the date needs to be left in so anyone
# who gets a copy of this file has access to the licence, extra stipulations, and disclaimors.
# 2) If this code is used as part of another project, I'd apreciate a mention in that project's
# documentation.
# 3) If you improve on any of the routines, I'd be most grateful if you would pass them back to
# me so that I can have the option to incorporate them into the origional module with apropriate
# attribution under this licence and stipulations.
#
# A copy of the licence and stipulations is bundled with the source files as licence.txt, or you
# can go to the GNU website for the terms of the GPL licence.
#
# If you try hard enough, I'm sure someone could damage something (software, data, system, hardware)
# useing it. I've put a lot of time and effort into this software, and have removed any obvious
# bugs, but nothing is perfect. If you spot any flaws, please let me know so that I might be able to
# fix them. However I reserve the right not to fix flaws that I don't have the time, or resources
# to fix, or that I feel that fixing would detriment the software overall. By useing this software
# you accept this, and any potential risk to your own hardware, software, data, and/or physical and
# mental health. This software is provided "as is" and any express or implied warranties,
# including, but not limited to, the implied warranties of merchantability and fitness for a
# particular purpose are disclaimed. In no event shall I or any contributors be liable for any
# direct, indirect, incidental, special, exemplary, or consequential damages (including, but not
# limited to, procurement of substitute goods or services; loss of use, data, or profits; or
# business interruption) however caused and on any theory of liability, whether in contract, strict
# liability, or tort (including negligence or otherwise) arising in any way out of the use of this
# software, even if advised of the possibility of such damage.
#
# Author: william.fraser@virgin.net
# Date: 14th January 2015

import sys
import os.path
import os
import spectrumtapblock
import disciplefile
import spectrumtranslate
from PyQt4 import QtGui,QtCore,QtWebKit
from operator import itemgetter

#lambda to make life simpler
setCombo=lambda combo,text: combo.setCurrentIndex(combo.findText(text))

class SpectrumFileTranslateGUI(QtGui.QWidget):

    #nested class
    class StartStopDisplayPanel(QtGui.QWidget):
        def __init__(self,data,start,end,radiobutton,scroll):
            QtGui.QWidget.__init__(self)
            
            self.data=data
            self.selectStart=0 if start==-1 else start
            self.selectEnd=len(self.data) if end==-1 else end+1
            self.selectEnd=max(self.selectEnd,self.selectStart)
            self.radiobutton=radiobutton
            self.scroll=scroll

            self.topleftaddress=-1
            self.columns=-1
            self.rows=-1
            
            #set font and get text dimensions
            self.myfont=QtGui.QFont('monospace',10)
            self.setFont(self.myfont)
            self.cWidth=self.fontMetrics().charWidth('0',0)
            self.cHeight=self.fontMetrics().height()
            self.baseline=self.fontMetrics().ascent()
            
            #hook up scrollbar
            scroll.valueChanged.connect(self.scrollChanged)

        def scrollChanged(self,pos):
            if(self.topleftaddress!=-1):
                self.topleftaddress=pos*self.columns

            #repaint display
            self.update()
            

        def paintEvent(self,event):
            qp=QtGui.QPainter()
            qp.begin(self)
            
            #if topleft not set do so now
            if(self.topleftaddress==-1):
                self.topleftaddress=(self.selectStart/self.columns)*self.columns
                #update scrollbar
                self.resizeEvent(None)
            
            qp.setFont(self.myfont)
            
            #blank canvas
            qp.setBrush(QtGui.QColor(255,255,255))
            qp.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            qp.drawRect(0,0,self.width(),self.height())

            #Are we doing selection?
            #if so, is there selected area in screen? If so then highlight it in grey
            if(self.radiobutton!=None and self.selectStart<self.topleftaddress+self.rows*self.columns and self.selectEnd>self.topleftaddress):
                #selection background to grey
                qp.setBrush(QtGui.QColor(128,128,128))
                
                #work out first full row, and last row to be highlighted
                rstart=(self.selectStart-self.topleftaddress+self.columns-1)/self.columns
                rstart=max(rstart,0)
                    
                rend=(self.selectEnd-self.topleftaddress+self.columns-1)/self.columns
                rend=min(rend,self.rows)
                
                #do whole lines block
                x=(self.cWidth>>1)+(self.cWidth*10)
                qp.drawRect(x,rstart*self.cHeight,((self.columns*3)-1)*self.cWidth,(rend-rstart)*self.cHeight)
                y=x+self.cWidth*(3*self.columns+1)
                qp.drawRect(y,rstart*self.cHeight,self.columns*self.cWidth,(rend-rstart)*self.cHeight)
                
                #do part first line
                i=(self.selectStart-self.topleftaddress)%self.columns
                #if any bytes before whole line, highlight them
                if(i!=0):
                    qp.drawRect(x+(i*3*self.cWidth),(rstart-1)*self.cHeight,(((self.columns-i)*3)-1)*self.cWidth,self.cHeight)
                    qp.drawRect(y+(i*self.cWidth),(rstart-1)*self.cHeight,(self.columns-i)*self.cWidth,self.cHeight)

                #blank any unused blocks on last line if not needed
                i=(self.selectEnd-self.topleftaddress)%self.columns
                if(i!=0 and self.selectEnd<self.topleftaddress+(self.rows*self.columns)):
                    qp.setBrush(QtGui.QColor(255,255,255))
                    qp.drawRect(x+(i*3*self.cWidth),(rend-1)*self.cHeight,(((self.columns-i)*3)-1)*self.cWidth,self.cHeight)
                    qp.drawRect(y+(i*self.cWidth),(rend-1)*self.cHeight,(self.columns-i)*self.cWidth,self.cHeight)

            #now display data in file
            qp.setPen(QtGui.QColor(0,0,0))

            #set y to baseline
            y=self.baseline

            a=self.topleftaddress
            row=0
            #draw each row of values
            while(row<self.rows):
                #start off half a character in
                x=self.cWidth>>1
                
                #print address
                qp.drawText(QtCore.QPointF(x,y),"%08X"%a)
                
                #move past address
                x+=self.cWidth*10
                
                i=0
                txt=""
                #print each value and remember the character representation
                while(i<self.columns and a+i<len(self.data)):
                    #print value at address
                    qp.drawText(QtCore.QPointF(x,y),"%02X"%ord(self.data[a+i]))
                    x+=self.cWidth*3
                    #add character
                    d=ord(self.data[a+i])
                    txt+=chr(d) if (d>=32 and d<=127) else "."
                    i+=1
                    
                x=(self.cWidth>>1)+(self.cWidth*10)
                x+=self.cWidth*(3*self.columns+1)
                qp.drawText(QtCore.QPointF(x,y),spectrumtranslate.get_spectrum_string(txt))

                row+=1
                y+=self.cHeight
                a+=self.columns

            #draw lines between display areas
            qp.setPen(QtGui.QPen(QtCore.Qt.black,1,QtCore.Qt.SolidLine))
            y=self.rows*self.cHeight
            x=(self.cWidth>>1)+(self.cWidth*9)
            qp.drawLine(x,0,x,y)
            x+=self.cWidth*(3*self.columns+1)
            qp.drawLine(x,0,x,y)

            qp.end()

        def resizeEvent(self,event):
            #work out how many columns we can get in
            #allow for 12 chars +4 per column (8 digit address, 2 width for
            #between address & bytes, and between bytes and characters. Also
            #half on left & right of canvas. Minus 1 for after last byte) 4
            #per column is: 2 for byte, 1 for character, and 1 for between bytes
            
            i=self.width()
            #take away space for dividers & address
            i-=self.cWidth*12
            #find out how many characters left
            i/=self.cWidth
            #divide by 4 to see how many columns will fit
            i>>=2
        
            bChanged=(i!=self.columns)
            self.columns=i
        
            i=self.height()/self.cHeight
            bChanged=bChanged or (self.rows!=i)
            self.rows=i

            #if topleft not set do so now
            if(self.topleftaddress==-1):
                self.topleftaddress=(self.selectStart/self.columns)*self.columns

            #if has changed then update ascociated scrollbar
            if(bChanged or event==None or not event):
                self.scroll.setValue(max(self.topleftaddress,0)/self.columns)
                self.scroll.setPageStep(self.rows)
                self.scroll.setRange(0,((len(self.data)+self.columns-1)/self.columns)-self.rows)
        
        def mouseReleaseEvent(self,event):
            #Are we selecting or just displaying. If just Displaying can ignore mouse events
            if(self.radiobutton==None):
                return
                
            row=event.y()/self.cHeight
            #if to below last row of bytes then invalid place to click
            if(row>=self.rows):
                return
            
            x=event.x()-((self.cWidth*10)+(self.cWidth>>1))
            col=-1
            #if to left of bytes then invalid place to click
            if(x<0):
                return
                
            #see if not to right of bytes then should be valid click
            if(x<self.cWidth*(3*self.columns-1)):
                col=(x+(self.cWidth>>1))/self.cWidth
                col/=3

            #move to start of character display
            x-=self.cWidth*(3*self.columns+1)
            if(x>=0 and x<self.columns*self.cWidth):
                col=x/self.cWidth
            
            #if not clicked on valid area, end
            if(col==-1):
                return
                
            #calculate position clicked (end position is position after last selected byte)
            pos=self.topleftaddress+(row*self.columns)+col
            if(not self.radiobutton.isChecked()):
                pos+=1
                
            #if beyond end of data then return
            if(pos>=len(self.data)+(0 if self.radiobutton.isChecked() else 1)):
                return
            
            #now have valid position clicked
            #if start radiobutton selected then set start
            if(self.radiobutton.isChecked()):
                self.selectStart=pos
            #else set select end
            else:
                self.selectEnd=pos
            
            #ensure start not after end, or end before start
            if(self.selectStart>=self.selectEnd):
                if(self.radiobutton.isChecked()):
                    self.selectEnd=self.selectStart+1
                else:
                    self.selectStart=self.selectEnd-1
            
            #repaint display
            self.update()

    #end nested definitions
   
    def __init__(self,defaultFile=None):
        super(SpectrumFileTranslateGUI,self).__init__()
        
        self.diInstructions=[None]
        
        self.ExportSettings={"Filename":"Export    ","AppendOrOver":1,"SaveWithHeadder":1,"Flag":0xFF}
        
        self.initUI(defaultFile)
        
    def initUI(self,defaultFile=None):
        self.setWindowTitle("Spectrum File Translate")

        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif',10))

        bBrowse=QtGui.QPushButton("&Browse",self)
        self.connect(bBrowse,QtCore.SIGNAL("clicked()"),lambda who=bBrowse: self.buttonPressed(who))
        bBrowse.setToolTip("Search for file to extract data from.")
        self.bBrowse=bBrowse
        bBrowseContainer=QtGui.QPushButton("Browse disk image",self)
        bBrowseContainer.setEnabled(False)
        self.bBrowseContainer=bBrowseContainer
        self.connect(bBrowseContainer,QtCore.SIGNAL("clicked()"),lambda who=bBrowseContainer: self.buttonPressed(who))
        bBrowseContainer.setToolTip("Select Spectrum file to translate from container file.")
        bBrowseHex=QtGui.QPushButton("Browse Hex",self)
        bBrowseHex.setEnabled(False)
        self.bBrowseHex=bBrowseHex
        self.connect(bBrowseHex,QtCore.SIGNAL("clicked()"),lambda who=bBrowseHex: self.buttonPressed(who))
        bBrowseHex.setToolTip("Manually select start and last byte of file to translate.")
        bBrowseOut=QtGui.QPushButton("Browse",self)
        self.connect(bBrowseOut,QtCore.SIGNAL("clicked()"),lambda who=bBrowseOut: self.buttonPressed(who))
        bBrowseOut.setToolTip("Select file to save translation in.")
        self.bBrowseOut=bBrowseOut
        bTranslate=QtGui.QPushButton("Translate",self)
        self.connect(bTranslate,QtCore.SIGNAL("clicked()"),lambda who=bTranslate: self.buttonPressed(who))
        bTranslate.setToolTip("Translate selected data.")
        self.bTranslate=bTranslate
        lFileNameIn=QtGui.QLabel("Source File:")
        lDataOffset=QtGui.QLabel("Data Offset:")
        lDataEnd=QtGui.QLabel("Data End:")
        lDataFile=QtGui.QLabel("File Number:")
        lDataType=QtGui.QLabel("Extract As:")
        lNumberFormat=QtGui.QLabel("Number Format:")
        lFileNameOut=QtGui.QLabel("Destination File:")
        leFileNameIn=QtGui.QLineEdit(self)
        self.leFileNameIn=leFileNameIn
        leFileNameIn.textChanged.connect(self.handle_changed_text)
        leFileNameIn.setToolTip("File to extract data from.")
        leDataOffset=QtGui.QLineEdit(self)
        leDataOffset.setToolTip("Offset from start of file to first byte of data to be translated.")
        self.leDataOffset=leDataOffset
        leDataEnd=QtGui.QLineEdit(self)
        leDataEnd.setToolTip("Offset from start of file to last byte of data to be translated.")
        self.leDataEnd=leDataEnd
        leDataFile=QtGui.QLineEdit(self)
        leDataFile.setMaxLength(2)
        leDataFile.setToolTip("File number to extract in selected image file.")
        self.leDataFile=leDataFile
        leFileNameOut=QtGui.QLineEdit(self)
        leFileNameOut.setToolTip("Filename of where to save translation.")
        self.leFileNameOut=leFileNameOut
        cbDataType=QtGui.QComboBox(self)
        cbDataType.addItem("Basic Program",0)
        cbDataType.addItem("Machine Code",1)
        cbDataType.addItem("Variable Array",2)
        cbDataType.addItem("Screen",3)
        cbDataType.addItem("Raw Data",4)
        cbDataType.setToolTip("Specifies what to translate data as.")
        self.cbDataType=cbDataType
        setCombo(cbDataType,"Basic Program")
        cbDataType.activated.connect(self.DataTypeChange)
        cbNumberFormat=QtGui.QComboBox(self)
        cbNumberFormat.addItem("Hexadecimal",0)
        cbNumberFormat.addItem("Decimal",1)
        cbNumberFormat.addItem("Octal",2)
        cbNumberFormat.addItem("Binary",3)
        cbNumberFormat.activated.connect(self.FormatChange)
        cbNumberFormat.setToolTip("Specifies number format for number fields (Data Offset, Data End etc).")
        setCombo(cbNumberFormat,"Hexadecimal")
        self.cbNumberFormat=cbNumberFormat
        self.CurrentNumberFormat=cbNumberFormat.currentIndex()
        self.cbNumberFormat=cbNumberFormat
        cbViewOutput=QtGui.QCheckBox("View Output",self)
        cbViewOutput.toggle()
        cbViewOutput.setToolTip("Select if you want to see translated text after translation.")
        self.cbViewOutput=cbViewOutput
        cbSaveOutput=QtGui.QCheckBox("Save Output",self)
        cbSaveOutput.toggle()
        cbSaveOutput.setToolTip("Select if you want to save translated text after translation.")
        self.cbSaveOutput=cbSaveOutput
        cbExportToContainer=QtGui.QCheckBox("Export file to Container",self)
        cbExportToContainer.toggle()
        cbExportToContainer.setCheckState(False)
        cbExportToContainer.setToolTip("Select if you want to export the selected file to a tap file.")
        self.cbExportToContainer=cbExportToContainer
        cbExportToContainer.stateChanged.connect(self.ExportToContainerChanged)
        bExportSettings=QtGui.QPushButton("Export Settings",self)
        bExportSettings.setToolTip("Edit the Export options.")
        bExportSettings.clicked.connect(self.EditExportSettings)
        bExportSettings.setEnabled(False)
        self.bExportSettings=bExportSettings

        #set out widgets
        grid=QtGui.QGridLayout()
        grid.setSpacing(10)

        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        hbox.addWidget(lFileNameIn)
        leFileNameIn.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        leFileNameIn.sizePolicy().setHorizontalStretch(1)
        hbox.addWidget(leFileNameIn)
        hbox.addWidget(bBrowse)

        grid.addLayout(hbox,0,0,1,3)

        grid.addWidget(bBrowseContainer,0,3)


        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lDataOffset.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        hbox.addWidget(lDataOffset)
        leDataOffset.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        hbox.addWidget(leDataOffset)
        hbox.addStretch(1)
        grid.addLayout(hbox,1,0)
        
        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lDataEnd.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        hbox.addWidget(lDataEnd)
        leDataEnd.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        hbox.addWidget(leDataEnd)
        hbox.addStretch(1)
        grid.addLayout(hbox,1,1)

        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lDataFile.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        hbox.addWidget(lDataFile)
        leDataFile.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        hbox.addWidget(leDataFile)
        hbox.addStretch(1)
        grid.addLayout(hbox,1,2)

        grid.addWidget(bBrowseHex,1,3)

        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lDataType.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        hbox.addWidget(lDataType)
        hbox.addWidget(cbDataType)
        hbox.addStretch(1)

        lNumberFormat.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        hbox.addWidget(lNumberFormat)
        hbox.addWidget(cbNumberFormat)
        
        grid.addLayout(hbox,2,0,1,3)


        stack=QtGui.QStackedWidget()
        
        #panel to hold Basic program variables
        gbBasic=QtGui.QGroupBox("Basic Program",self)

        grid2=QtGui.QGridLayout()
        grid2.setSpacing(10)

        lBasicAutoLine=QtGui.QLabel("Autostart Line:")
        lBasicVariableOffset=QtGui.QLabel("Variable Offset:")
        leBasicAutoLine=QtGui.QLineEdit(self)
        leBasicAutoLine.setToolTip("Specifies line for auto start of BASIC program.")
        self.leBasicAutoLine=leBasicAutoLine
        leBasicVariableOffset=QtGui.QLineEdit(self)
        leBasicVariableOffset.setToolTip("Specifies offset to variables BASIC program. Leave blank if not sure.")
        self.leBasicVariableOffset=leBasicVariableOffset
        cbXMLBasicOutput=QtGui.QCheckBox("XML output")
        cbXMLBasicOutput.setToolTip("Do you want output as text, or as XML.")
        cbXMLBasicOutput.toggle()
        cbXMLBasicOutput.setCheckState(False)
        self.cbXMLBasicOutput=cbXMLBasicOutput
    
        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lBasicAutoLine.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        hbox.addWidget(lBasicAutoLine)
        leBasicAutoLine.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        hbox.addWidget(leBasicAutoLine)
        hbox.addStretch(1)
        grid2.addLayout(hbox,0,0)

        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lBasicVariableOffset.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        hbox.addWidget(lBasicVariableOffset)
        leBasicVariableOffset.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        hbox.addWidget(leBasicVariableOffset)
        hbox.addStretch(1)
        grid2.addLayout(hbox,0,1)

        grid2.addWidget(cbXMLBasicOutput,1,0)

        grid2.setRowStretch(2,1)

        gbBasic.setLayout(grid2)
        
        stack.addWidget(gbBasic)

        #panel to hold machine code variables
        gbCode=QtGui.QGroupBox("Machine Code",self)

        grid2=QtGui.QGridLayout()
        grid2.setSpacing(5)

        lCodeOrigin=QtGui.QLabel("Origin:")
        lCodeFormat=QtGui.QLabel("Output Format:")
        lCodeTimes=QtGui.QLabel("List Timings:")
        lCodeJump=QtGui.QLabel("Gap After Jump/Ret:")
        leCodeOrigin=QtGui.QLineEdit(self)
        leCodeOrigin.setToolTip("The memory address of the first byte of the data.")
        self.leCodeOrigin=leCodeOrigin
        cbCodeFormat=QtGui.QComboBox(self)
        cbCodeFormat.addItem("Hexadecimal",0)
        cbCodeFormat.addItem("Decimal",1)
        cbCodeFormat.addItem("Octal",2)
        cbCodeFormat.addItem("Binary",3)
        setCombo(cbCodeFormat,"Hexadecimal")
        cbCodeFormat.setToolTip("The data format for numbers in the translated code.")
        self.cbCodeFormat=cbCodeFormat
        cbCodeTimes=QtGui.QComboBox(self)
        cbCodeTimes.addItem("None",0)
        cbCodeTimes.addItem("T states",1)
        cbCodeTimes.addItem("Cycles",2)
        cbCodeTimes.addItem("All",3)
        setCombo(cbCodeTimes,"None")
        cbCodeTimes.setToolTip("What instruction timeing details do you want listed?")
        self.cbCodeTimes=cbCodeTimes
        cbCodeJump=QtGui.QComboBox(self)
        cbCodeJump.addItem("None",0)
        cbCodeJump.addItem("After absolute",1)
        cbCodeJump.addItem("All",2)
        setCombo(cbCodeJump,"After absolute")
        cbCodeJump.setToolTip("Do you want a blank line for readability after absolute jumps, none or all.")
        self.cbCodeJump=cbCodeJump
        cbCodeFlags=QtGui.QCheckBox("List Flags")
        cbCodeFlags.setToolTip("List flags affected by machine instructions.")
        cbCodeFlags.toggle()
        cbCodeFlags.setCheckState(False)
        self.cbCodeFlags=cbCodeFlags
        cbCodeUndocumented=QtGui.QCheckBox("Mark Undocumented")
        cbCodeUndocumented.setToolTip("Note undocumented machine instructions.")
        cbCodeUndocumented.toggle()
        cbCodeUndocumented.setCheckState(False)
        self.cbCodeUndocumented=cbCodeUndocumented
        cbXMLOutput=QtGui.QCheckBox("XML output")
        cbXMLOutput.setToolTip("Do you want output as text formatted by spacers, or as XML.")
        cbXMLOutput.toggle()
        cbXMLOutput.setCheckState(False)
        self.cbXMLOutput=cbXMLOutput
        bCustomInstructions=QtGui.QPushButton("Custom Instructions",self)
        bCustomInstructions.setToolTip("Edit Custom Disassemble Instructions.")
        self.connect(bCustomInstructions,QtCore.SIGNAL("clicked()"),lambda who=bCustomInstructions: self.buttonPressed(who))
        self.bCustomInstructions=bCustomInstructions

        grid2.addWidget(lCodeOrigin,0,0)
        grid2.addWidget(leCodeOrigin,0,1)
        lCodeOrigin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        grid2.addWidget(cbCodeFlags,0,3)

        grid2.addWidget(lCodeFormat,1,0)
        grid2.addWidget(cbCodeFormat,1,1)
        lCodeFormat.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        grid2.addWidget(cbCodeUndocumented,1,3)

        grid2.addWidget(lCodeTimes,2,0)
        grid2.addWidget(cbCodeTimes,2,1)
        lCodeTimes.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        grid2.addWidget(cbXMLOutput,2,3)

        grid2.addWidget(lCodeJump,3,0)
        grid2.addWidget(cbCodeJump,3,1)
        lCodeJump.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        grid2.addWidget(bCustomInstructions,3,3)

        hbox=QtGui.QHBoxLayout()
        hbox.addStretch(1)
        grid2.addLayout(hbox,2,0)
        hbox=QtGui.QHBoxLayout()
        hbox.addStretch(1)
        grid2.addLayout(hbox,4,0)
        grid2.setColumnStretch(2,1)
        grid2.setColumnStretch(4,1)
        
        gbCode.setLayout(grid2)
        
        stack.addWidget(gbCode)

        #panel to hold array variables
        gbVars=QtGui.QGroupBox("Variable Array",self)

        grid2=QtGui.QGridLayout()
        grid2.setSpacing(10)

        lArrayVarName=QtGui.QLabel("Variable Name:")
        lArrayVarType=QtGui.QLabel("Variable Type:")
        leArrayVarName=QtGui.QLineEdit(self)
        leArrayVarName.setMaxLength(20)
        leArrayVarName.setToolTip("The letter name of the variable to translate.")
        self.leArrayVarName=leArrayVarName
        cbArrayVarType=QtGui.QComboBox(self)
        cbArrayVarType.addItem("Number Array",0)
        cbArrayVarType.addItem("Character Array",1)
        cbArrayVarType.addItem("String",2)
        cbArrayVarType.setToolTip("The variable type to translate.")
        self.cbArrayVarType=cbArrayVarType
        setCombo(cbArrayVarType,"String")
        cbXMLVarOutput=QtGui.QCheckBox("XML output")
        cbXMLVarOutput.setToolTip("Do you want output as text, or as XML.")
        cbXMLVarOutput.toggle()
        cbXMLVarOutput.setCheckState(False)
        self.cbXMLVarOutput=cbXMLVarOutput

        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lArrayVarName.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        hbox.addWidget(lArrayVarName)
        leArrayVarName.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        hbox.addWidget(leArrayVarName)
        hbox.addStretch(1)
        grid2.addLayout(hbox,0,0)

        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lArrayVarType.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        hbox.addWidget(lArrayVarType)
        hbox.addWidget(cbArrayVarType)
        hbox.addStretch(1)
        grid2.addLayout(hbox,0,1)

        grid2.addWidget(cbXMLVarOutput,1,0)

        grid2.setRowStretch(2,1)

        gbVars.setLayout(grid2)

        stack.addWidget(gbVars)

        #panel to hold image variables
        gbImage=QtGui.QGroupBox("Screen",self)

        grid2=QtGui.QGridLayout()
        grid2.setSpacing(10)

        cbImageFlash=QtGui.QCheckBox("Extract Flashing colours (will need to be saved as animated gif file)")
        cbImageFlash.toggle()
        cbImageFlash.setToolTip("Extract data as an animated GIF file to display flashing colours, or simple GIF file.")
        self.cbImageFlash=cbImageFlash
        lImageDelay=QtGui.QLabel("Flash delay in miliseconds:")
        leImageDelay=QtGui.QLineEdit("320")
        leImageDelay.setToolTip("The time delay between flash states in milliseconds.")
        self.leImageDelay=leImageDelay
    
        grid2.addWidget(cbImageFlash,0,0)

        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        lImageDelay.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        hbox.addWidget(lImageDelay)
        leImageDelay.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        hbox.addWidget(leImageDelay)
        hbox.addStretch(1)
        grid2.addLayout(hbox,1,0)

        grid2.setRowStretch(2,1)

        gbImage.setLayout(grid2)

        stack.addWidget(gbImage)

        #panel to indicate raw data
        gbRaw=QtGui.QGroupBox("Raw Data",self)
        stack.addWidget(gbRaw)


        self.settingsstack=stack

        #layout after processing options
        grid.addWidget(stack,3,0,1,4)
        grid.setRowStretch(3,1)
        

        grid.addWidget(cbViewOutput,4,0)
        grid.addWidget(cbSaveOutput,5,0)

        grid.addWidget(cbExportToContainer,4,1)
        grid.addWidget(bExportSettings,4,2)

        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        hbox.addWidget(lFileNameOut)
        leFileNameOut.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        leFileNameOut.sizePolicy().setHorizontalStretch(1)
        hbox.addWidget(leFileNameOut)
        hbox.addWidget(bBrowseOut)
        grid.addLayout(hbox,5,1,1,3)

        hbox=QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(bTranslate)
        hbox.addStretch(1)
        grid.addLayout(hbox,6,0,1,4)

        self.setLayout(grid) 

        self.setGeometry(0,0,600,300)
        self.adjustSize()
        self.show()

        if(defaultFile!=None):
            leFileNameIn.setText(defaultFile)
            
        self.CheckIfKnownContainerFile()

    def buttonPressed(self,button):
        #browse to find input file
        if(button==self.bBrowse):
            filein=self.leFileNameIn.text()
            #create open file dialog with current file if exists as selected file
            qfd=QtGui.QFileDialog(self,"Select source file",filein if os.path.isfile(filein) else "")
            if(os.path.isfile(filein)):
                qfd.selectFile(filein)
                
            qfd.setFileMode(QtGui.QFileDialog.AnyFile)
            qfd.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
            
            #run dialog and if open is clicked then act on this
            if(qfd.exec_()==QtGui.QDialog.Accepted):
                newfile=qfd.selectedFiles()[0]
                self.leFileNameIn.setText(newfile)
                self.CheckIfKnownContainerFile()
                #set start and finish translate to start & end of file if changed
                if(filein!=newfile and os.path.isfile(newfile)):
                    self.leDataOffset.setText("0")
                    self.leDataEnd.setText(self.FormatNumber(os.path.getsize(newfile)-1))

            return
            
        #browse to find output file
        if(button==self.bBrowseOut):
            fileout=self.leFileNameOut.text()
            #create save file dialog with current file if exists as selected file
            qfd=QtGui.QFileDialog(self,"Select output file",fileout if os.path.isfile(fileout) else "")
            qfd.setFileMode(QtGui.QFileDialog.AnyFile)
            qfd.setAcceptMode(QtGui.QFileDialog.AcceptSave)
            qfd.selectFile(fileout)
            
            #run dialog and if save is clicked then act on this
            if(qfd.exec_()==QtGui.QDialog.Accepted):
                newfile=qfd.selectedFiles()[0]
                self.leFileNameOut.setText(newfile)

            return

        #browse container file
        if(button==self.bBrowseContainer):
            if(self.bBrowseContainer.text()=="Browse TAP"):
                self.BrowseTapFile()
                
            if(self.bBrowseContainer.text()=="Browse disk image"):
                self.BrowseDiscipleImageFile()
                
            return

        #browse container file
        if(button==self.bBrowseHex):
            self.BrowseFileHex()
            return

        #Do Translation
        if(button==self.bTranslate):
            self.Translate()
            return

        #handle machine code Custom Instructions
        if(button==self.bCustomInstructions):
            self.EditCustomDisassembleCommands()
            return

    def EditCustomDisassembleCommands(self):
        #create dialog
        dContainer=QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Disassemble Custom Commands")
        dContainer.setModal(True)
        self.Ddialog=dContainer
        
        grid=QtGui.QGridLayout()
        grid.setSpacing(2)

        bload=QtGui.QPushButton("Load Instructions",self)
        bload.setToolTip("Load a previously saved set of instructions from a file.")
        grid.addWidget(bload,0,0,1,2)
        bload.clicked.connect(self.CustomDisassembleLoad)
        dContainer.bload=bload

        bsave=QtGui.QPushButton("Save Instructions",self)
        bsave.setToolTip("Save instructions currently in editor to a file.")
        grid.addWidget(bsave,1,0,1,2)
        bsave.clicked.connect(self.CustomDisassembleSave)
        dContainer.bsave=bsave

        bdelete=QtGui.QPushButton("Delete Instruction",self)
        bdelete.setToolTip("Delete currently selected instruction.")
        grid.addWidget(bdelete,2,0,1,2)
        bdelete.clicked.connect(self.CustomDisassembleDelete)
        dContainer.bdelete=bdelete

        bnew=QtGui.QPushButton("New Instruction",self)
        bnew.setToolTip("Add new instruction to end of list.")
        grid.addWidget(bnew,3,0,1,2)
        bnew.clicked.connect(self.CustomDisassembleNew)
        dContainer.bnew=bnew

        bup=QtGui.QPushButton("Move Up",self)
        bup.setToolTip("Move curently selected instruction up a line.")
        grid.addWidget(bup,4,0,1,2)
        bup.clicked.connect(self.CustomDisassembleUp)
        dContainer.bup=bup

        bdown=QtGui.QPushButton("Move Down",self)
        bdown.setToolTip("Move curently selected instruction down a line.")
        grid.addWidget(bdown,5,0,1,2)
        bdown.clicked.connect(self.CustomDisassembleDown)
        dContainer.bdown=bdown
        
        cbNumberFormat=QtGui.QComboBox(self)
        cbNumberFormat.addItem("Hexadecimal",0)
        cbNumberFormat.addItem("Decimal",1)
        cbNumberFormat.addItem("Octal",2)
        cbNumberFormat.addItem("Binary",3)
        cbNumberFormat.activated[int].connect(self.DissassembleEditorFormatChange)
        cbNumberFormat.setToolTip("Specifies number format for number fields (Data Offset, Data End etc).")
        setCombo(cbNumberFormat,"Hexadecimal")
        dContainer.cbNumberFormat=cbNumberFormat
        dContainer.Format='{0:X}'
        dContainer.FormatBase=16
        grid.addWidget(cbNumberFormat,6,0,1,2)

        cbDisassembleCommands=QtGui.QComboBox(self)
        for key,value in sorted(spectrumtranslate.DisassembleInstruction.DisassembleCodes.items(),key=itemgetter(1)):
            cbDisassembleCommands.addItem(key,value)
            
        cbDisassembleCommands.setToolTip("Select what you want this instruction to do.")
        cbDisassembleCommands.currentIndexChanged[str].connect(self.ChangeDissassembleCommand)
        dContainer.cbDisassembleCommands=cbDisassembleCommands
        grid.addWidget(cbDisassembleCommands,7,0,1,2)

        lab=QtGui.QLabel("Start:")
        lab.setToolTip("Select the first address you want instruction to apply from.")
        grid.addWidget(lab,8,0,1,1)

        leStart=QtGui.QLineEdit()
        leStart.setMaxLength(16)
        leStart.setToolTip("Select the first address you want instruction to apply from.")
        leStart.textChanged.connect(self.ChangeDissassembleStart)
        leStart.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        leStart.sizePolicy().setHorizontalStretch(1)
        dContainer.leStart=leStart
        grid.addWidget(leStart,8,1,1,1)

        lab=QtGui.QLabel("End:")
        lab.setToolTip("Select the last address you want instruction to apply to.")
        grid.addWidget(lab,9,0,1,1)

        leEnd=QtGui.QLineEdit()
        leEnd.setMaxLength(16)
        leEnd.setToolTip("Select the last address you want instruction to apply to.")
        leEnd.textChanged.connect(self.ChangeDissassembleEnd)
        leEnd.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        leEnd.sizePolicy().setHorizontalStretch(1)
        dContainer.leEnd=leEnd
        grid.addWidget(leEnd,9,1,1,1)

        bedit=QtGui.QPushButton("Edit data",self)
        bedit.setToolTip("Edit aditional data for the instruction.")
        grid.addWidget(bedit,10,0,1,2)
        bedit.clicked.connect(self.CustomDisassembleEdit)
        dContainer.bedit=bedit

        lwInstructions=QtGui.QListWidget(self)
        lwInstructions.setToolTip("List of Disassemble instructions to carry out on the code.")
        #only list instructions if have more than basic format setter
        if(len(self.diInstructions)>1):
            for di in self.diInstructions[1:]:
                item=QtGui.QListWidgetItem("\n")
                lwInstructions.addItem(item)
                lab=QtGui.QLabel()
                lab.setIndent(5)
                lab.setFrameShape(QtGui.QFrame.Box)
                item.label=lab
                item.di=spectrumtranslate.DisassembleInstruction(di)
                self.setLabelText(item)
                lwInstructions.setItemWidget(item,lab)
        
        lwInstructions.clicked.connect(self.SetDisassembleDialogButtons)
        lwInstructions.itemPressed.connect(self.SetDisassembleDialogButtons)
        lwInstructions.currentItemChanged.connect(self.instructionselectionchanged)
        dContainer.lwInstructions=lwInstructions

        grid.addWidget(lwInstructions,0,2,12,1)

        lay=QtGui.QHBoxLayout()
        ok=QtGui.QPushButton("Ok",self)
        lay.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close=QtGui.QPushButton("Cancel",self)
        lay.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay.addStretch(1)
        helpbutton=QtGui.QPushButton("Help",self)
        helpbutton.setToolTip("Displays information about Disassemble Instructions.")
        lay.addWidget(helpbutton)
        helpbutton.clicked.connect(self.DisplayInstructionsHelp)

        grid.addLayout(lay,12,0,2,0)

        grid.setRowStretch(11,1)
        grid.setColumnStretch(2,1)

        dContainer.setLayout(grid)
        
        #set to same size as parent
        dContainer.setGeometry(self.geometry())

        #set button state
        self.SetDisassembleDialogButtons()

        #run dialog, and if ok selected get start & stop points
        if(dContainer.exec_()==QtGui.QDialog.Accepted):
            self.diInstructions=[None]+[lwInstructions.item(i).di for i in range(lwInstructions.count())]

        del self.Ddialog

    def DisplayInstructionsHelp(self):
        #create dialog
        dContainer=QtGui.QDialog(self)
        dContainer.setWindowTitle("Disassemble Instructions Help")
        dContainer.setModal(True)

        lay=QtGui.QVBoxLayout()

        view=QtWebKit.QWebView(self)
        lay.addWidget(view)
        view.setUrl(QtCore.QUrl("DisassembleInstructionHelp.html"))

        lay2=QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok=QtGui.QPushButton("Ok",self)
        lay2.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        back=QtGui.QPushButton("back",self)
        lay2.addWidget(back)
        back.clicked.connect(view.back)
        foreward=QtGui.QPushButton("foreward",self)
        lay2.addWidget(foreward)
        foreward.clicked.connect(view.forward)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)
        
        #set to same size as parent
        dContainer.setGeometry(self.geometry())

        #run dialog
        dContainer.exec_()

    def CustomDisassembleEdit(self):
        lwInstructions=self.Ddialog.lwInstructions
        di=lwInstructions.currentItem().di
        
        if(di.instruction==spectrumtranslate.DisassembleInstruction.DisassembleCodes["Line Number Every X"]):
            self.EditUnreferencedLineNumberFrequency(di)
            
        if(di.instruction==spectrumtranslate.DisassembleInstruction.DisassembleCodes["Custom Format"]):
            self.EditCustomFormatDialog(di)
            #don't need to set label text
            return
            
        if(di.instruction==spectrumtranslate.DisassembleInstruction.DisassembleCodes["Data Block"]):
            self.EditDataBlock(di)
            
        if(di.instruction==spectrumtranslate.DisassembleInstruction.DisassembleCodes["Pattern Data Block"]):
            self.EditPatternDataBlock(di)

        #ensure any data change is represented in list details
        self.setLabelText(lwInstructions.currentItem())

    def EditPatternDataBlock(self,di):
        dContainer=QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Pattern Data Block")
        dContainer.setModal(True)

        lay=QtGui.QVBoxLayout()

        lay2=QtGui.QHBoxLayout()
        lay2.addWidget(QtGui.QLabel("Pattern Data Block function:"))

        cbEditPatternDataBlock=QtGui.QComboBox(self)
        for key in spectrumtranslate.DisassembleInstruction.DisassemblePatternBlockCodeOrderedKeys:
            cbEditPatternDataBlock.addItem(key)

        cbEditPatternDataBlock.setToolTip("Select instructions for Pattern Data block")
        for key in spectrumtranslate.DisassembleInstruction.DisassemblePatternBlockCodeOrderedKeys:
            if(spectrumtranslate.DisassembleInstruction.DisassemblePatternBlockCodes[key]==di.data):
                break
                
        setCombo(cbEditPatternDataBlock,key)
        self.cbEditPatternDataBlock=cbEditPatternDataBlock
        cbEditPatternDataBlock.currentIndexChanged[str].connect(self.ChangeEditPatternDataBlock)

        lay2.addWidget(cbEditPatternDataBlock)
        lay2.addStretch(1)
        
        lay.addLayout(lay2)

        testblock,prepblock,actionblock=spectrumtranslate.GetPartsOfPatternDataBlock(di.data)

        lay.addWidget(QtGui.QLabel("Pattern Data Block search commands:"))
        
        tePatternDataBlockSearch=QtGui.QTextEdit()
        tePatternDataBlockSearch.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        if(testblock):
            tePatternDataBlockSearch.setPlainText(testblock)
        tePatternDataBlockSearch.myfont=QtGui.QFont('monospace',tePatternDataBlockSearch.fontPointSize())
        tePatternDataBlockSearch.setFont(tePatternDataBlockSearch.myfont)
        tePatternDataBlockSearch.setToolTip("Code to find where block ought to be.")
        tePatternDataBlockSearch.textChanged.connect(self.ChangePatternDataBlock)
        self.tePatternDataBlockSearch=tePatternDataBlockSearch
        lay.addWidget(tePatternDataBlockSearch)

        lay.addWidget(QtGui.QLabel("Pattern Data Block address setup commands:"))
        
        tePatternDataBlockSetup=QtGui.QTextEdit()
        tePatternDataBlockSetup.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        if(prepblock):
            tePatternDataBlockSetup.setPlainText(prepblock)
        tePatternDataBlockSetup.myfont=QtGui.QFont('monospace',tePatternDataBlockSetup.fontPointSize())
        tePatternDataBlockSetup.setFont(tePatternDataBlockSetup.myfont)
        tePatternDataBlockSetup.setToolTip("Code to define start & end of Action DataBlock.")
        tePatternDataBlockSetup.textChanged.connect(self.ChangePatternDataBlock)
        self.tePatternDataBlockSetup=tePatternDataBlockSetup
        lay.addWidget(tePatternDataBlockSetup)

        lay.addWidget(QtGui.QLabel("Pattern Data Block Action commands:"))
        
        tePatternDataBlockAction=QtGui.QTextEdit()
        tePatternDataBlockAction.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        if(actionblock):
            tePatternDataBlockAction.setPlainText(actionblock)
        tePatternDataBlockAction.myfont=QtGui.QFont('monospace',tePatternDataBlockAction.fontPointSize())
        tePatternDataBlockAction.setFont(tePatternDataBlockAction.myfont)
        tePatternDataBlockAction.setToolTip("Code to be executed on specified block.")
        tePatternDataBlockAction.textChanged.connect(self.ChangePatternDataBlock)
        self.tePatternDataBlockAction=tePatternDataBlockAction
        lay.addWidget(tePatternDataBlockAction)

        lay2=QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok=QtGui.QPushButton("Ok",self)
        lay2.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close=QtGui.QPushButton("Cancel",self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        #set to same size as parent
        dContainer.setGeometry(self.geometry())

        if(dContainer.exec_()==QtGui.QDialog.Accepted):
            pattern=str(cbEditPatternDataBlock.currentText())
            if(pattern=="Custom"):
                di.data=str(self.tePatternDataBlockSearch.toPlainText()+"\n"+self.tePatternDataBlockSetup.toPlainText()+"\n"+self.tePatternDataBlockAction.toPlainText())
            
            else:
                di.data=spectrumtranslate.DisassembleInstruction.DisassemblePatternBlockCodes[pattern]
        
        del self.cbEditPatternDataBlock
        del self.tePatternDataBlockSearch
        del self.tePatternDataBlockSetup
        del self.tePatternDataBlockAction

    def ChangeEditPatternDataBlock(self,txt):
        blocks=spectrumtranslate.GetPartsOfPatternDataBlock(spectrumtranslate.DisassembleInstruction.DisassemblePatternBlockCodes[str(txt)])
        
        if(blocks[0]!=None and blocks[1]!=None and blocks[2]!=None):
            self.tePatternDataBlockSearch.textChanged.disconnect(self.ChangePatternDataBlock)
            self.tePatternDataBlockSetup.textChanged.disconnect(self.ChangePatternDataBlock)
            self.tePatternDataBlockAction.textChanged.disconnect(self.ChangePatternDataBlock)
            self.tePatternDataBlockSearch.setPlainText(blocks[0])
            self.tePatternDataBlockSetup.setPlainText(blocks[1])
            self.tePatternDataBlockAction.setPlainText(blocks[2])
            self.tePatternDataBlockSearch.textChanged.connect(self.ChangePatternDataBlock)
            self.tePatternDataBlockSetup.textChanged.connect(self.ChangePatternDataBlock)
            self.tePatternDataBlockAction.textChanged.connect(self.ChangePatternDataBlock)


    def ChangePatternDataBlock(self):
        blocks=spectrumtranslate.GetPartsOfPatternDataBlock(str(self.tePatternDataBlockSearch.toPlainText()+self.tePatternDataBlockSetup.toPlainText()+self.tePatternDataBlockAction.toPlainText()))
        if(blocks[0]!=None and blocks[1]!=None and blocks[2]!=None):
            blocks=[block.strip() for block in blocks]

        for key in spectrumtranslate.DisassembleInstruction.DisassemblePatternBlockCodeOrderedKeys:
            testblocks=spectrumtranslate.GetPartsOfPatternDataBlock(spectrumtranslate.DisassembleInstruction.DisassemblePatternBlockCodes[key])
            if(testblocks[0]==None or testblocks[1]==None or testblocks[2]==None):
                continue
                
            testblocks=[block.strip() for block in testblocks]
            if(testblocks==blocks):
                break

        self.cbEditPatternDataBlock.currentIndexChanged[str].disconnect(self.ChangeEditPatternDataBlock)
        setCombo(self.cbEditPatternDataBlock,key)
        self.cbEditPatternDataBlock.currentIndexChanged[str].connect(self.ChangeEditPatternDataBlock)
    
    def EditDataBlock(self,di):
        dContainer=QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Data Block")
        dContainer.setModal(True)

        lay=QtGui.QVBoxLayout()

        lay2=QtGui.QHBoxLayout()
        lay2.addWidget(QtGui.QLabel("Data Block function:"))

        cbEditDataBlock=QtGui.QComboBox(self)
        for key in spectrumtranslate.DisassembleInstruction.DisassembleDataBlockCodeOrderedKeys:
            cbEditDataBlock.addItem(key)

        cbEditDataBlock.setToolTip("Select instructions for Data block")
        for key in spectrumtranslate.DisassembleInstruction.DisassembleDataBlockCodeOrderedKeys:
            if(spectrumtranslate.DisassembleInstruction.DisassembleDataBlockCodes[key]==di.data):
                break
                
        setCombo(cbEditDataBlock,key)
        self.cbEditDataBlock=cbEditDataBlock
        cbEditDataBlock.currentIndexChanged[str].connect(self.ChangeEditDataBlock)

        lay2.addWidget(cbEditDataBlock)
        lay2.addStretch(1)
        
        lay.addLayout(lay2)

        lay.addWidget(QtGui.QLabel("Data Block commands:"))
        
        teDataBlock=QtGui.QTextEdit()
        teDataBlock.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        if(di.data):
            teDataBlock.setPlainText(di.data)
        teDataBlock.myfont=QtGui.QFont('monospace',teDataBlock.fontPointSize())
        teDataBlock.setFont(teDataBlock.myfont)
        teDataBlock.setToolTip("Code to be executed in the Data Block.")
        teDataBlock.textChanged.connect(self.ChangeDataBlock)
        self.teDataBlock=teDataBlock
        lay.addWidget(teDataBlock)

        lay2=QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok=QtGui.QPushButton("Ok",self)
        lay2.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close=QtGui.QPushButton("Cancel",self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        #set to same size as parent
        dContainer.setGeometry(self.geometry())

        if(dContainer.exec_()==QtGui.QDialog.Accepted):
            di.data=str(teDataBlock.toPlainText())
        
        del self.cbEditDataBlock
        del self.teDataBlock

    def ChangeDataBlock(self):
        blockText=self.teDataBlock.toPlainText()
        for key in spectrumtranslate.DisassembleInstruction.DisassembleDataBlockCodeOrderedKeys:
            if(spectrumtranslate.DisassembleInstruction.DisassembleDataBlockCodes[key]==blockText):
                break
                
        self.cbEditDataBlock.currentIndexChanged[str].disconnect(self.ChangeEditDataBlock)
        setCombo(self.cbEditDataBlock,key)
        self.cbEditDataBlock.currentIndexChanged[str].connect(self.ChangeEditDataBlock)

    def ChangeEditDataBlock(self,txt):
        self.teDataBlock.textChanged.disconnect(self.ChangeDataBlock)
        self.teDataBlock.setPlainText(spectrumtranslate.DisassembleInstruction.DisassembleDataBlockCodes[str(txt)])
        self.teDataBlock.textChanged.connect(self.ChangeDataBlock)
    
    def EditUnreferencedLineNumberFrequency(self,instruction):
        #create dialog
        dContainer=QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Line Referenceing")
        dContainer.setModal(True)

        lay=QtGui.QVBoxLayout()

        lay.addWidget(QtGui.QLabel("Have unreferenced line addresses shown at least every how many lines:"))

        leUnreferencedLineNumber=QtGui.QLineEdit()
        leUnreferencedLineNumber.setMaxLength(3)
        leUnreferencedLineNumber.setText(self.Ddialog.Format.format(int(instruction.data,16)))
        leUnreferencedLineNumber.setToolTip("every how many unreferenced lines do you want adresses displayed? Use 0 for none.")
        leUnreferencedLineNumber.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        leUnreferencedLineNumber.sizePolicy().setHorizontalStretch(1)
        leUnreferencedLineNumber.textChanged.connect(self.ChangeUnreferencedLineNumber)
        self.leUnreferencedLineNumber=leUnreferencedLineNumber
        lay.addWidget(leUnreferencedLineNumber)

        lay2=QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok=QtGui.QPushButton("Ok",self)
        lay2.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close=QtGui.QPushButton("Cancel",self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        if(dContainer.exec_()==QtGui.QDialog.Accepted):
            i=self.CheckInstructionAddress(leUnreferencedLineNumber)
            #if invalid number set to 0
            if(i<0 or i>0xFF):
                i=0
            
            instruction.data="%X" % i
        
        del self.leUnreferencedLineNumber

    def ChangeUnreferencedLineNumber(self):        
        i=self.CheckInstructionAddress(self.leUnreferencedLineNumber)
        if(i>0xFF):
            i=-1
            
        self.leUnreferencedLineNumber.setStyleSheet("QLineEdit {background-color:%s}" % "#FF8080" if i==-1 else "white")

    def EditCustomFormatDialog(self,instruction):
        settings=spectrumtranslate.get_custom_format_values(instruction.data)

        #create dialog
        dContainer=QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Custom Format Settings")
        dContainer.setModal(True)

        grid=QtGui.QGridLayout()
        grid.setSpacing(2)

        cbCustomFormatAddressFormat=QtGui.QComboBox(self)
        cbCustomFormatAddressFormat.addItem("Address format Hexadecimal",0)
        cbCustomFormatAddressFormat.addItem("Address format Decimal",1)
        cbCustomFormatAddressFormat.addItem("Address format Octal",2)
        cbCustomFormatAddressFormat.addItem("Address format Binary",3)
        cbCustomFormatAddressFormat.setToolTip("In what format do you want the line adresses displayed?")
        cbCustomFormatAddressFormat.setCurrentIndex(settings["AddressOutput"])
        grid.addWidget(cbCustomFormatAddressFormat,0,0,1,2)

        cbCustomFormatNumberFormat=QtGui.QComboBox(self)
        cbCustomFormatNumberFormat.addItem("Number format Hexadecimal",0)
        cbCustomFormatNumberFormat.addItem("Number format Decimal",1)
        cbCustomFormatNumberFormat.addItem("Number format Octal",2)
        cbCustomFormatNumberFormat.addItem("Number format Binary",3)
        cbCustomFormatNumberFormat.setToolTip("In what format do you want numbers displayed?")
        cbCustomFormatNumberFormat.setCurrentIndex(settings["NumberOutput"])
        grid.addWidget(cbCustomFormatNumberFormat,1,0,1,2)

        cbCustomFormatCommandFormat=QtGui.QComboBox(self)
        cbCustomFormatCommandFormat.addItem("Command format Hexadecimal",0)
        cbCustomFormatCommandFormat.addItem("Command format Decimal",1)
        cbCustomFormatCommandFormat.addItem("Command format Octal",2)
        cbCustomFormatCommandFormat.addItem("Command format Binary",3)
        cbCustomFormatCommandFormat.setToolTip("In what format do you want the bytes of commands displayed?")
        cbCustomFormatCommandFormat.setCurrentIndex(settings["CommandOutput"])
        grid.addWidget(cbCustomFormatCommandFormat,2,0,1,2)

        cbCustomFormatCodeTimes=QtGui.QComboBox(self)
        cbCustomFormatCodeTimes.addItem("No timings",0)
        cbCustomFormatCodeTimes.addItem("List T states",1)
        cbCustomFormatCodeTimes.addItem("List time cycles",2)
        cbCustomFormatCodeTimes.addItem("List all timings",3)
        cbCustomFormatCodeTimes.setToolTip("What instruction timeing details do you want listed?")
        cbCustomFormatCodeTimes.setCurrentIndex(settings["OutputTStates"])
        grid.addWidget(cbCustomFormatCodeTimes,3,0,1,2)

        cbCustomFormatCodeJump=QtGui.QComboBox(self)
        cbCustomFormatCodeJump.addItem("No space after jump",0)
        cbCustomFormatCodeJump.addItem("Space after absolute jump",1)
        cbCustomFormatCodeJump.addItem("Space after all jumps",2)
        cbCustomFormatCodeJump.setToolTip("Blank line for readability after absolute jumps, none or all jumps.")
        cbCustomFormatCodeJump.setCurrentIndex(settings["BreakAfterJumps"])
        grid.addWidget(cbCustomFormatCodeJump,4,0,1,2)

        cbCustomFormatLineFormat=QtGui.QComboBox(self)
        cbCustomFormatLineFormat.addItem("Show every line address",0)
        cbCustomFormatLineFormat.addItem("Show no line addresses",1)
        cbCustomFormatLineFormat.addItem("Show only referenced addresses",2)
        cbCustomFormatLineFormat.setToolTip("Which line adresses do you want displayed?")
        cbCustomFormatLineFormat.setCurrentIndex(settings["LineNumberOutput"])
        grid.addWidget(cbCustomFormatLineFormat,5,0,1,2)

        lab=QtGui.QLabel("Display unreferenced line address:")
        lab.setToolTip("every how many unreferenced lines do you want adresses displayed?")
        grid.addWidget(lab,6,0,1,1)

        leCustomFormatLineFrequency=QtGui.QLineEdit()
        leCustomFormatLineFrequency.setMaxLength(3)
        leCustomFormatLineFrequency.setText(self.Ddialog.Format.format(settings["ListEveryXLines"]))
        leCustomFormatLineFrequency.setToolTip("every how many unreferenced lines do you want adresses displayed?")
        leCustomFormatLineFrequency.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        leCustomFormatLineFrequency.sizePolicy().setHorizontalStretch(1)
        leCustomFormatLineFrequency.textChanged.connect(self.ChangeCustomFormatLineFrequency)
        self.Frequency=leCustomFormatLineFrequency
        grid.addWidget(leCustomFormatLineFrequency,6,1,1,1)

        cbCustomFormatBreakAfterData=QtGui.QCheckBox("Empty line after data")
        cbCustomFormatBreakAfterData.setToolTip("Do you want an empty line after a data block for readability?")
        cbCustomFormatBreakAfterData.toggle()
        if(settings["BreakAfterData"]==1):
            cbCustomFormatBreakAfterData.setCheckState(False)

        grid.addWidget(cbCustomFormatBreakAfterData,7,0,1,2)

        cbCustomFormatReferenceNumbers=QtGui.QCheckBox("Use data numbers as line references")
        cbCustomFormatReferenceNumbers.setToolTip("Do you want to use 16 bit numbers in data to be used as line references?")
        cbCustomFormatReferenceNumbers.toggle()
        if(settings["TreatDataNumbersAsLineReferences"]==1):
            cbCustomFormatReferenceNumbers.setCheckState(False)

        grid.addWidget(cbCustomFormatReferenceNumbers,8,0,1,2)

        cbCustomFormatDisplayCommandBytes=QtGui.QCheckBox("Display byte values of commands")
        cbCustomFormatDisplayCommandBytes.setToolTip("Do you want to display the bytes of a command?")
        cbCustomFormatDisplayCommandBytes.toggle()
        if(settings["DisplayCommandBytes"]==1):
            cbCustomFormatDisplayCommandBytes.setCheckState(False)

        grid.addWidget(cbCustomFormatDisplayCommandBytes,9,0,1,2)

        cbCustomFormatDisplayComments=QtGui.QCheckBox("Display comments")
        cbCustomFormatDisplayComments.setToolTip("Display comments? If not then timing, flags, and undocumented commands won't be displayed.")
        cbCustomFormatDisplayComments.toggle()
        if(settings["DisplayComments"]==1):
            cbCustomFormatDisplayComments.setCheckState(False)
            
        grid.addWidget(cbCustomFormatDisplayComments,10,0,1,2)

        cbCustomFormatSeperatorFormat=QtGui.QComboBox(self)
        cbCustomFormatSeperatorFormat.addItem("Use space as separator",0)
        cbCustomFormatSeperatorFormat.addItem("Use tab as separator",1)
        cbCustomFormatSeperatorFormat.setToolTip("The type of seperator between parts of the output.")
        cbCustomFormatSeperatorFormat.setCurrentIndex(settings["SeperatorMode"])
        grid.addWidget(cbCustomFormatSeperatorFormat,11,0,1,2)

        cbCustomFormatCodeFlags=QtGui.QCheckBox("List Flags")
        cbCustomFormatCodeFlags.setToolTip("List flags affected by machine instructions.")
        cbCustomFormatCodeFlags.toggle()
        if(settings["ShowFlags"]==0):
            cbCustomFormatCodeFlags.setCheckState(False)
        grid.addWidget(cbCustomFormatCodeFlags,12,0,1,2)

        cbCustomFormatCodeUndocumented=QtGui.QCheckBox("Mark undocumented commands")
        cbCustomFormatCodeUndocumented.setToolTip("Note undocumented machine instructions.")
        cbCustomFormatCodeUndocumented.toggle()
        if(settings["MarkUndocumenedCommand"]==0):
            cbCustomFormatCodeUndocumented.setCheckState(False)
        grid.addWidget(cbCustomFormatCodeUndocumented,13,0,1,2)

        cbXML=QtGui.QComboBox(self)
        cbXML.addItem("Non XML Output",0)
        cbXML.addItem("XML Output",1)
        cbXML.setToolTip("Does the disassembler output XML or not.")
        cbXML.setCurrentIndex(settings["XMLOutput"])
        grid.addWidget(cbXML,14,0,1,2)

        lay=QtGui.QHBoxLayout()
        lay.addStretch(1)
        ok=QtGui.QPushButton("Ok",self)
        lay.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close=QtGui.QPushButton("Cancel",self)
        lay.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay.addStretch(1)

        grid.addLayout(lay,15,0,1,2)

        dContainer.setLayout(grid)

        if(dContainer.exec_()==QtGui.QDialog.Accepted):
            i=self.CheckInstructionAddress(leCustomFormatLineFrequency)
            if(i<0 or i>0xFF):
                QtGui.QMessageBox.warning(self,"Error!","Unreferenced line frequency must be between 0 and 255 decimal.")
            
            else:
                instruction.data=spectrumtranslate.get_custom_format_string(
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
                                     cbCustomFormatSeperatorFormat.currentIndex(),
                                     1 if cbCustomFormatCodeFlags.isChecked() else 0,
                                     1 if cbCustomFormatCodeUndocumented.isChecked() else 0,
                                     cbXML.currentIndex())
        
        del self.Frequency
            
    def ChangeCustomFormatLineFrequency(self):        
        i=self.CheckInstructionAddress(self.Frequency)
        if(i>0xFF):
            i=-1
            
        self.Frequency.setStyleSheet("QLineEdit {background-color:%s}" % "#FF8080" if i==-1 else "white")
    
    def CustomDisassembleSave(self):
        qfd=QtGui.QFileDialog(self,"Save Instruction List file")
        qfd.setFileMode(QtGui.QFileDialog.AnyFile)
        qfd.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        
        #run dialog and if save is clicked then act on this
        if(qfd.exec_()==QtGui.QDialog.Accepted):
            lwInstructions=self.Ddialog.lwInstructions
            fOut=qfd.selectedFiles()[0]
            try:
                fo=open(fOut,"wb")
                fo.write("\n".join([str(lwInstructions.item(i).di) for i in range(lwInstructions.count())]))
                fo.close()
            except:
                QtGui.QMessageBox.warning(self,"Error!",'Failed to save data to "%s"' % fOut)
        
    def CustomDisassembleLoad(self):
        qfd=QtGui.QFileDialog(self,"Select Instruction file")
        qfd.setFileMode(QtGui.QFileDialog.AnyFile)
        qfd.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        
        #run dialog and if open is clicked then act on this
        if(qfd.exec_()==QtGui.QDialog.Accepted):
            fIn=qfd.selectedFiles()[0]
            try:
                fo=open(fIn,"rb")
                instructions=[spectrumtranslate.DisassembleInstruction(line.rstrip('\n')) for line in fo]
                fo.close()
            except:
                QtGui.QMessageBox.warning(self,"Error!",'Unable to get data from "%s"' % fIn)
                return
            
            lwInstructions=self.Ddialog.lwInstructions
            lwInstructions.clear()
            for di in instructions:
                item=QtGui.QListWidgetItem("\n")
                lwInstructions.addItem(item)
                lab=QtGui.QLabel()
                lab.setIndent(5)
                lab.setFrameShape(QtGui.QFrame.Box)
                item.label=lab
                item.di=spectrumtranslate.DisassembleInstruction(di)
                self.setLabelText(item)
                lwInstructions.setItemWidget(item,lab)
            
            self.SetDisassembleDialogButtons()

    def CustomDisassembleDown(self):
        lwInstructions=self.Ddialog.lwInstructions
        selectpos=lwInstructions.currentRow()

        #when takeItem is used, it deletes items attached to the listwidgetitem
        #so make a copy of the associated disassemble instruction and create a new label
        di=spectrumtranslate.DisassembleInstruction(lwInstructions.currentItem().di)
        item=lwInstructions.takeItem(selectpos)
        lwInstructions.insertItem(selectpos+1,item)
        lab=QtGui.QLabel()
        lab.setIndent(5)
        lab.setFrameShape(QtGui.QFrame.Box)
        item.label=lab
        item.di=di
        self.setLabelText(item)
        lwInstructions.setItemWidget(item,lab)

        #update focus
        lwInstructions.setCurrentRow(selectpos+1)
        
        self.SetDisassembleDialogButtons()
        
    def CustomDisassembleUp(self):
        lwInstructions=self.Ddialog.lwInstructions
        selectpos=lwInstructions.currentRow()

        #when takeItem is used, it deletes items attached to the listwidgetitem
        #so make a copy of the associated disassemble instruction and create a new label
        di=spectrumtranslate.DisassembleInstruction(lwInstructions.currentItem().di)
        item=lwInstructions.takeItem(selectpos)
        lwInstructions.insertItem(selectpos-1,item)
        lab=QtGui.QLabel()
        lab.setIndent(5)
        lab.setFrameShape(QtGui.QFrame.Box)
        item.label=lab
        item.di=di
        self.setLabelText(item)
        lwInstructions.setItemWidget(item,lab)

        #update focus
        lwInstructions.setCurrentRow(selectpos-1)
        
        self.SetDisassembleDialogButtons()

    def CustomDisassembleDelete(self):
        lwInstructions=self.Ddialog.lwInstructions
        selectpos=lwInstructions.currentRow()
        
        if(selectpos!=-1):
            lwInstructions.takeItem(lwInstructions.currentRow())
            self.SetDisassembleDialogButtons()

    def CustomDisassembleNew(self):
        lwInstructions=self.Ddialog.lwInstructions

        item=QtGui.QListWidgetItem("\n")
        lwInstructions.addItem(item)
        lab=QtGui.QLabel()
        lab.setIndent(5)
        lab.setFrameShape(QtGui.QFrame.Box)
        item.label=lab
        item.di=spectrumtranslate.DisassembleInstruction("Address Output Format Hex")
        self.setLabelText(item)
        lwInstructions.setItemWidget(item,lab)
        

    def DissassembleEditorFormatChange(self,index):
        self.Ddialog.Format=('{0:X}','{0:d}','{0:o}','{0:b}')[index]
        self.Ddialog.FormatBase=(16,10,8,2)[index]
        instructionlist=self.Ddialog.lwInstructions
        for i in range(instructionlist.count()):
            self.setLabelText(instructionlist.item(i))
        
        #change start and end editor lineedits
        self.SetDisassembleDialogButtons()

    def ChangeDissassembleStart(self):
        dialog=self.Ddialog
        instructionlist=dialog.lwInstructions
        di=instructionlist.currentItem().di
        
        i=self.CheckInstructionAddress(dialog.leStart)
        dialog.leStart.setStyleSheet("QLineEdit {background-color:%s}" % "#FF8080" if i==-1 else "white")
        if(i!=-1):
            di.start=i
            self.setLabelText(instructionlist.currentItem())
        
    def ChangeDissassembleEnd(self):
        dialog=self.Ddialog
        instructionlist=dialog.lwInstructions
        di=instructionlist.currentItem().di
        
        i=self.CheckInstructionAddress(dialog.leEnd)
        dialog.leEnd.setStyleSheet("QLineEdit {background-color:%s}" % "#FF8080" if i==-1 else "white")
        if(i!=-1):
            di.end=i
            self.setLabelText(instructionlist.currentItem())

    def CheckInstructionAddress(self,le):
        try:
            l=int(str(le.text()),self.Ddialog.FormatBase)
            if(l<0 or l>0x10000):
                l=-1
            return l
        except:
            return -1

    def instructionselectionchanged(self,f,t):
        self.SetDisassembleDialogButtons()
        
    def ChangeDissassembleCommand(self,txt):
        dialog=self.Ddialog
        instructionlist=dialog.lwInstructions
        selectpos=instructionlist.currentRow()
        
        if(selectpos!=-1):
            di=instructionlist.currentItem().di
            txt=str(txt)
            newinstruction=spectrumtranslate.DisassembleInstruction.DisassembleCodes[txt]
            instructionchanged=(newinstruction!=di.instruction)
            di.instruction=newinstruction

            #handle change of format that needs data change            
            if(instructionchanged and txt=="Custom Format"):
                di.data="100"
                
            elif(instructionchanged and txt=="Line Number Every X"):
                di.data="8"

            elif(instructionchanged and txt=="Data Block"):
                di.data=spectrumtranslate.DisassembleInstruction.DisassembleDataBlockCodes["Define Byte Hex"]

            elif(instructionchanged and txt=="Pattern Data Block"):
                di.data=spectrumtranslate.DisassembleInstruction.DisassemblePatternBlockCodes["RST#08 (Error)"]
            
            elif(instructionchanged):
                di.data=None

            self.setLabelText(instructionlist.currentItem())

        self.SetDisassembleDialogButtons()

    def SetDisassembleDialogButtons(self):
        dialog=self.Ddialog
        instructionlist=dialog.lwInstructions
        
        number=instructionlist.count()
        selectpos=instructionlist.currentRow()
        
        di=None if selectpos==-1 else instructionlist.currentItem().di
        
        if(di!=None):
            for key,value in spectrumtranslate.DisassembleInstruction.DisassembleCodes.iteritems():
                if(value==di.instruction):
                    setCombo(dialog.cbDisassembleCommands,key)
                    break

            #could have used the textEdited signal to avoid disconnecting and reconnecting.
            #This way will allow highlighting of all abnormal value inputs
            dialog.leStart.textChanged.disconnect(self.ChangeDissassembleStart)
            dialog.leEnd.textChanged.disconnect(self.ChangeDissassembleEnd)
            dialog.leStart.setText(dialog.Format.format(di.start))
            dialog.leEnd.setText(dialog.Format.format(di.end))
            dialog.leStart.textChanged.connect(self.ChangeDissassembleStart)
            dialog.leEnd.textChanged.connect(self.ChangeDissassembleEnd)
        
        dialog.bsave.setEnabled(number>0)
        dialog.bdelete.setEnabled(di!=None)
        dialog.bup.setEnabled(selectpos>0)
        dialog.bdown.setEnabled(selectpos<number-1 and di!=None)
        dialog.bedit.setEnabled(di!=None and (di.instruction==spectrumtranslate.DisassembleInstruction.DisassembleCodes["Custom Format"] or
                                              di.instruction==spectrumtranslate.DisassembleInstruction.DisassembleCodes["Line Number Every X"] or
                                              di.instruction==spectrumtranslate.DisassembleInstruction.DisassembleCodes["Data Block"] or
                                              di.instruction==spectrumtranslate.DisassembleInstruction.DisassembleCodes["Pattern Data Block"]))
        dialog.cbDisassembleCommands.setEnabled(di!=None)
        dialog.leStart.setEnabled(di!=None)
        dialog.leEnd.setEnabled(di!=None)

    def setLabelText(self,lwInstruction):
        #find code name
        for key,value in spectrumtranslate.DisassembleInstruction.DisassembleCodes.iteritems():
            if(value==lwInstruction.di.instruction):
                break
        
        s=("<strong>%s</strong><br/>"+self.Ddialog.Format.format(lwInstruction.di.start)+"->"+self.Ddialog.Format.format(lwInstruction.di.end))% (key)

        if(lwInstruction.di.instruction==spectrumtranslate.DisassembleInstruction.DisassembleCodes["Line Number Every X"]):
            s+=" address every "+self.Ddialog.Format.format(int(lwInstruction.di.data,16))+" lines."
            
        elif(lwInstruction.di.instruction==spectrumtranslate.DisassembleInstruction.DisassembleCodes["Data Block"]):
            for key in spectrumtranslate.DisassembleInstruction.DisassembleDataBlockCodeOrderedKeys:
                if(spectrumtranslate.DisassembleInstruction.DisassembleDataBlockCodes[key]==lwInstruction.di.data):
                    break
                    
            s+=" - "+key
        
        elif(lwInstruction.di.instruction==spectrumtranslate.DisassembleInstruction.DisassembleCodes["Pattern Data Block"]):
            for key in spectrumtranslate.DisassembleInstruction.DisassemblePatternBlockCodeOrderedKeys:
                if(spectrumtranslate.DisassembleInstruction.DisassemblePatternBlockCodes[key]==lwInstruction.di.data):
                    break

            s+=" - "+key
        
        lwInstruction.label.setText(s)

    def EditExportSettings(self):
        #create dialog
        dContainer=QtGui.QDialog(self)
        dContainer.setWindowTitle("Edit Export Settings")
        dContainer.setModal(True)

        vbox=QtGui.QVBoxLayout()

        cbOverOrAppend=QtGui.QComboBox(self)
        cbOverOrAppend.addItem("Overwrite existing file",0)
        cbOverOrAppend.addItem("Append to Existing file",1)
        cbOverOrAppend.setToolTip("Do you want to append or overwrite an existing file?")
        cbOverOrAppend.setCurrentIndex(self.ExportSettings["AppendOrOver"])
        vbox.addWidget(cbOverOrAppend)

        cbSaveWithHeadder=QtGui.QComboBox(self)
        cbSaveWithHeadder.addItem("Save as headderless block",0)
        cbSaveWithHeadder.addItem("Save with headder",1)
        cbSaveWithHeadder.setToolTip("Do you want to save as headderless block or file with headder?")
        cbSaveWithHeadder.setCurrentIndex(self.ExportSettings["SaveWithHeadder"])
        vbox.addWidget(cbSaveWithHeadder)

        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        hbox.addWidget(QtGui.QLabel("File Name:"))
        leFileName=QtGui.QLineEdit(self)
        leFileName.setToolTip("Filename to export as.")
        leFileName.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        leFileName.sizePolicy().setHorizontalStretch(1)
        leFileName.setText(self.ExportSettings["Filename"])
        hbox.addWidget(leFileName)
        vbox.addLayout(hbox)

        hbox=QtGui.QHBoxLayout()
        hbox.setSpacing(2)
        hbox.addWidget(QtGui.QLabel("Block Flag:"))
        leFlag=QtGui.QLineEdit(self)
        leFlag.setToolTip("Flag value for the data block.\nIgnored if saveing with headder.")
        leFlag.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        leFlag.sizePolicy().setHorizontalStretch(1)
        leFlag.setText(str(self.ExportSettings["Flag"]))
        hbox.addWidget(leFlag)
        vbox.addLayout(hbox)

        hbox=QtGui.QHBoxLayout()
        hbox.addStretch(1)
        ok=QtGui.QPushButton("Ok",self)
        hbox.addWidget(ok)
        ok.clicked.connect(self.CheckValidFileName)
        close=QtGui.QPushButton("Cancel",self)
        hbox.addWidget(close)
        close.clicked.connect(dContainer.reject)
        hbox.addStretch(1)

        vbox.addLayout(hbox)

        dContainer.setLayout(vbox)

        dContainer.leFileName=leFileName
        dContainer.leFlag=leFlag
        self.Ddialog=dContainer

        if(dContainer.exec_()==QtGui.QDialog.Accepted):
            self.ExportSettings["Flag"]=int(str(leFlag.text()))
            self.ExportSettings["Filename"]=str(leFileName.text())
            self.ExportSettings["AppendOrOver"]=cbOverOrAppend.currentIndex()
            self.ExportSettings["SaveWithHeadder"]=cbSaveWithHeadder.currentIndex()

        del self.Ddialog
    
    def CheckValidFileName(self):
        if(len(self.Ddialog.leFileName.text())>10):
            QtGui.QMessageBox.warning(self,"Error!","Specrum file names have to be 10 characters or less.")
            return
        
        try:
            f=int(self.Ddialog.leFlag.text())
            if(f<0 or f>0xFF):
                QtGui.QMessageBox.warning(self,"Error!","Flag must be from 0 to 255 inclusive.")
                return
        
        except:
            QtGui.QMessageBox.warning(self,"Error!","Flag must be a number from 0 to 255 inclusive.")
            return
            
        self.Ddialog.accept()

    def ExportToContainerChanged(self,state):
        self.SetTranslateButtonText()


    def Translate(self):
        #get data and exit if error
        data=self.GetSelectedData()
        if(data==None):
            return

        outputformat=self.cbDataType.currentText()

        #do exporting
        if(self.cbExportToContainer.isChecked()):
            #check if file is greater than 0xFFFF: won't fit in tap file if is.
            if(len(data)>0xFFFF):
                QtGui.QMessageBox.warning(self,"Error!","Data is bigger than 65535 bytes and can't be saved in a .TAP file.")
                return None

            output=''
            if(self.ExportSettings["SaveWithHeadder"]==1):
                filename=self.ExportSettings["Filename"]
                if(outputformat=="Basic Program"):
                    auto=self.getNumber(self.leBasicAutoLine)
                    variableoffset=self.getNumber(self.leBasicVariableOffset)
                    output=spectrumtapblock.CreateProgramHeadder(filename,variableoffset,len(data),auto).getPackagedForFile()
                    
                elif(outputformat=="Machine Code"):
                    origin=self.getNumber(self.leCodeOrigin)
                    if(origin<0 or origin>0xFFFF):
                        QtGui.QMessageBox.warning(self,"Error!","Code Origin must be between 0 and 65535 (0000 and FFFF hexadecimal).")
                        return None
                        
                    output=spectrumtapblock.CreateCodeHeadder(filename,origin,len(data)).getPackagedForFile()
                    
                elif(outputformat=="Variable Array"):
                    idescriptor=self.cbArrayVarType.currentIndex()
                    idescriptor+=2
                    idescriptor-=(idescriptor>>2)*3
                    idescriptor*=64
                    
                    sVarName=str(self.leArrayVarName.text()).lower()
                    if(len(sVarName)!=1 or ord(sVarName)<97 or ord(sVarName)>122):
                        QtGui.QMessageBox.warning(self,"Error!","Variable Name must be single letter.")
                        return None

                    output=spectrumtapblock.CreateArrayHeadder(filename,idescriptor|(ord(sVarName)&0x3F),len(data)).getPackagedForFile()
                    
                elif(outputformat=="Screen"):
                    output=spectrumtapblock.CreateScreenHeadder(filename).getPackagedForFile()

            output+=spectrumtapblock.CreateDataBlock(data,0xFF if self.ExportSettings["SaveWithHeadder"]==1 else self.ExportSettings["Flag"]).getPackagedForFile()
            
            fileout=self.leFileNameOut.text()
            if(not fileout or fileout==""):
                QtGui.QMessageBox.warning(self,"Error!",'No output file selected.')
                return
            
            try:
                fo=open(fileout,"ab" if self.ExportSettings["AppendOrOver"]==1 else "wb")
                fo.write(output)
                fo.close()
            except:
                QtGui.QMessageBox.warning(self,"Error!",'Failed to save data to "%s"' % fileout)
            
            return

            
        #handle images
        if(outputformat=="Screen"):
            #get image as gif
            delay=self.getNumber(self.leImageDelay)
            if(not self.cbImageFlash.isChecked()):
                delay=-1
            
            #display waiting cursor while do translation
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            data=spectrumtranslate.get_GIF_from_screen(data,delay)
            QtGui.QApplication.restoreOverrideCursor()

            #was there a problem?
            if(data==None):
                QtGui.QMessageBox.warning(self,"Error!",'Unable to extract screen from "%s"' % self.leFileNameIn.text())
                return
            
            #preview image if needed
            if(self.cbViewOutput.isChecked()):
                #create dialog to display image
                dContainer=QtGui.QDialog(self)
                dContainer.setWindowTitle("Translation results")
                dContainer.setModal(True)
                
                #create label to hold gif (which might be animated)
                pic=QtGui.QLabel()
                buf=QtCore.QBuffer()
                buf.open(QtCore.QIODevice.ReadWrite)
                buf.write(data)
                buf.seek(0)
                movie=QtGui.QMovie(buf,QtCore.QByteArray())
                pic.setMovie(movie)
                movie.start()
                
                #set out dialog
                pic.setAlignment(QtCore.Qt.AlignCenter)
                
                lay=QtGui.QVBoxLayout()
                
                lay.addWidget(pic)
                
                hbox=QtGui.QHBoxLayout()
                hbox.addStretch(1)
                ok=QtGui.QPushButton("Ok",self)
                ok.clicked.connect(dContainer.accept)
                hbox.addWidget(ok)
                hbox.addStretch(1)
                lay.addLayout(hbox)
                
                dContainer.setLayout(lay)
                
                dContainer.exec_()

            #save image if required
            if(self.cbSaveOutput.isChecked()):
                self.PutFileData(data)
            
            return
            
        #handle raw data
        if(outputformat=="Raw Data"):
            #create dialog
            dContainer=QtGui.QDialog(self)
            dContainer.setWindowTitle("View Raw Data")
            dContainer.setModal(True)
            
            lay=QtGui.QVBoxLayout()
            
            lay2=QtGui.QHBoxLayout()
            lay2.addStretch(1)
            ok=QtGui.QPushButton("Ok",self)
            lay2.addWidget(ok)
            ok.clicked.connect(dContainer.accept)
            lay2.addStretch(1)
            
            lay3=QtGui.QHBoxLayout()
            scroll=QtGui.QScrollBar(QtCore.Qt.Vertical)
            hexview=SpectrumFileTranslateGUI.StartStopDisplayPanel(data,0,len(data),None,scroll)
            lay3.addWidget(hexview)
            hexview.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
            hexview.sizePolicy().setHorizontalStretch(1)
            lay3.addWidget(scroll)
            
            lay.addLayout(lay3)
            lay.addLayout(lay2)
            
            dContainer.setLayout(lay)
            
            #set to same size as parent
            dContainer.setGeometry(self.geometry())
            
            #run dialog
            dContainer.exec_()
            
            #save data if required
            if(self.cbSaveOutput.isChecked()):
                self.PutFileData(data)

            return

        #otherwise translate into text
        s=self.DoTextTranslation(data,outputformat)
        if(s==None):
            return
            
        if(self.cbViewOutput.isChecked()):
            self.DisplayTranslation(s)
            
        if(self.cbSaveOutput.isChecked()):
            self.PutFileData(s)

    def DoTextTranslation(self,data,datatype):
        if(datatype=="Basic Program"):
            #get program variables
            auto=self.getNumber(self.leBasicAutoLine)
            variable=self.getNumber(self.leBasicVariableOffset)
            length=len(data)
            if(variable<0 or variable>length):
                variable=length

            try:
                #handle XML
                if(self.cbXMLBasicOutput.isChecked()==True):
                    return spectrumtranslate.convert_program_to_XML(data,auto,variable)
                
                #default to simple text
                return spectrumtranslate.convert_program_to_text(data,auto,variable)
            except SpectrumTranslateException, ste:
                QtGui.QMessageBox.warning(self,"Error!",ste.value)
                return None

        elif(datatype=="Machine Code"):
            origin=self.getNumber(self.leCodeOrigin)
            if(origin<0 or origin>0xFFFF):
                QtGui.QMessageBox.warning(self,"Error!","Code Origin must be between 0 and 65535 (0000 and FFFF hexadecimal).")
                return None

            #get format instructions
            iFormat=self.cbCodeFormat.currentIndex()
            iOutputTimes=self.cbCodeTimes.currentIndex()
            iOutputJumpGap=self.cbCodeJump.currentIndex()
            bListFlags=self.cbCodeFlags.isChecked()
            bListUndocumented=self.cbCodeUndocumented.isChecked()
            bXMLOutput=self.cbXMLOutput.isChecked()
            
            self.diInstructions[0]=spectrumtranslate.DisassembleInstruction(spectrumtranslate.DisassembleInstruction.DisassembleCodes["Custom Format"],
                0,
                0xFFFF,
                spectrumtranslate.get_custom_format_string(iFormat,
                    iFormat,
                    iFormat,
                    iOutputTimes,
                    iOutputJumpGap,
                    spectrumtranslate.DisassembleInstruction.DisassembleCodes["Line Numbers Referenced"],
                    16,
                    spectrumtranslate.DisassembleInstruction.DisassembleCodes["Empty Line After Data On"],
                    spectrumtranslate.DisassembleInstruction.DisassembleCodes["Reference Data Numbers On"],
                    spectrumtranslate.DisassembleInstruction.DisassembleCodes["List Command Bytes On"],
                    spectrumtranslate.DisassembleInstruction.DisassembleCodes["Comments Off"],
                    spectrumtranslate.DisassembleInstruction.DisassembleCodes["Seperators Space"],
                    spectrumtranslate.DisassembleInstruction.DisassembleCodes["Display Flags On" if bListFlags else "Display Flags Off"],
                    spectrumtranslate.DisassembleInstruction.DisassembleCodes["Mark Undocumented Command On" if bListUndocumented else "Mark Undocumented Command Off"],
                    spectrumtranslate.DisassembleInstruction.DisassembleCodes["XML Output On" if bXMLOutput else "XML Output Off"]))

            try:
                return spectrumtranslate.disassemble(data,0,origin,len(data),self.diInstructions)
            except spectrumtranslate.SpectrumTranslateException, ste:
                QtGui.QMessageBox.warning(self,"Error!",ste.value)
                return None
            
        elif(datatype=="Variable Array"):
            idescriptor=self.cbArrayVarType.currentIndex()
            idescriptor+=2
            idescriptor-=(idescriptor>>2)*3
            idescriptor*=64
            
            sVarName=str(self.leArrayVarName.text()).lower()
            if(len(sVarName)!=1 or ord(sVarName)<97 or ord(sVarName)>122):
                QtGui.QMessageBox.warning(self,"Error!","Variable Name must be single letter.")
                return None
            
            #handle XML
            if(self.cbXMLVarOutput.isChecked()==True):
                if(idescriptor&192==64):
                    vartype='string'
                elif(idescriptor&192==128):
                    vartype='numberarray'
                elif(idescriptor&192==192):
                    vartype='characterarray'
                
                soutput='<?xml version="1.0" encoding="UTF-8" ?>\n'
                soutput+='<variable>\n  <name>'+sVarName
                if(idescriptor&64==64):
                    soutput+='$'
                    
                soutput+='</name>\n  <type>'+vartype+'</type>\n'
                soutput+='  <value>\n'
                soutput+='\n'.join(['    '+x for x in spectrumtranslate.convert_array_to_XML(data,idescriptor).splitlines()])
                soutput+='\n  </value>\n</variable>\n'
                
                return soutput
            
            #default to simple text
            return sVarName+("" if idescriptor==128 else "$")+("" if idescriptor==64 else "[]")+"=\n"+spectrumtranslate.convert_array_to_text(data,idescriptor)

        else:
            return "Error!"

    def DisplayTranslation(self,txt):
        #create dialog to display image
        dContainer=QtGui.QDialog(self)
        dContainer.setWindowTitle("Translation results")
        dContainer.setModal(True)
        
        #create label to hold gif (which might be animated)
        textdisplay=QtGui.QTextEdit()
        textdisplay.setPlainText(txt)
        textdisplay.setReadOnly(True)
        textdisplay.myfont=QtGui.QFont('monospace',textdisplay.fontPointSize())
        textdisplay.setFont(textdisplay.myfont)
        
        lay=QtGui.QVBoxLayout()
        lay.addWidget(textdisplay)
        
        hbox=QtGui.QHBoxLayout()
        hbox.addStretch(1)
        ok=QtGui.QPushButton("Ok",self)
        ok.clicked.connect(dContainer.accept)
        hbox.addWidget(ok)
        hbox.addStretch(1)
        lay.addLayout(hbox)
        
        dContainer.setLayout(lay)
        
        dContainer.setGeometry(self.geometry())

        dContainer.exec_()

    def PutFileData(self,data):
        fileout=self.leFileNameOut.text()
        if(not fileout or fileout==""):
            QtGui.QMessageBox.warning(self,"Error!",'No output file selected.')
            return

        try:
            fo=open(fileout,"wb")
            fo.write(data)
            fo.close()
        except:
            QtGui.QMessageBox.warning(self,"Error!",'Failed to save data to "%s"' % fileout)

    def GetSelectedData(self):
        #first check if is +d/disciple file as go by file number rather than start & stop
        if(self.bBrowseContainer.text()=="Browse disk image"):
            i=self.getNumber(self.leDataFile)
            
            if(i<1 or i>80):
                QtGui.QMessageBox.warning(self,"Error!",'Valid file numbers are 1 to 80 inclusive.')
                return None
            
            try:
                #get disciple file object
                di=disciplefile.DiscipleImage(self.leFileNameIn.text())
                df=disciplefile.DiscipleFile(di,i)
                #return it's data
                return df.GetFileData()
            except:
                QtGui.QMessageBox.warning(self,"Error!",'Failed to extract file %d from "%s".' % (i,self.leFileNameIn.text()))
                return None

        offset=self.getNumber(self.leDataOffset)
        end=self.getNumber(self.leDataEnd)+1
        length=end-offset

        #sanity check for inputs
        if(offset<0 or end<0 or offset>end or length>65535):
            QtGui.QMessageBox.warning(self,"Error!",'invalid data offset or data end parameters')
            return None

        filein=self.leFileNameIn.text()
        if(not os.path.isfile(filein)):
            QtGui.QMessageBox.warning(self,"Error!",'"%s" does not exist.' % filein)
            return None

        #get contents of file
        try:
            fo=open(filein,"rb")
            fo.seek(offset)
            data=fo.read(length)
            fo.close()
        except:
            QtGui.QMessageBox.warning(self,"Error!",'Unable to get data from "%s"' % filein)
            return None
        
        if(len(data)!=length):
            QtGui.QMessageBox.warning(self,"Error!",'Unable to get data from "%s"' % filein)
            return None
        
        return data
        
    def DataTypeChange(self,datatype):
        self.settingsstack.setCurrentIndex(datatype)
        self.SetTranslateButtonText()

    def SetTranslateButtonText(self):
        if(self.cbExportToContainer.isChecked()):
            self.bTranslate.setText("Export")
            self.bExportSettings.setEnabled(True)
        else:
            self.bTranslate.setText(("Translate","Translate","Translate","Translate","Extract")[self.cbDataType.currentIndex()])
            self.bExportSettings.setEnabled(False)

    def FormatChange(self,newformat):
        #we're done if no change
        if(self.CurrentNumberFormat==newformat):
            return
            
        #go through all the boxes changing text formats
        self.SetNewNumberFormat(self.leDataOffset)
        self.SetNewNumberFormat(self.leDataEnd)
        self.SetNewNumberFormat(self.leDataFile)
        self.SetNewNumberFormat(self.leBasicAutoLine)
        self.SetNewNumberFormat(self.leBasicVariableOffset)
        self.SetNewNumberFormat(self.leCodeOrigin)
        
        #update current format
        self.CurrentNumberFormat=newformat

    def SetNewNumberFormat(self,le):
        val=self.getNumber(le)

        le.setText("" if val<0 else self.FormatNumber(val))

    def getNumber(self,le):
        try:
            #get old value adjusting for number format
            return int(str(le.text()),[16,10,8,2][self.CurrentNumberFormat])
            
        except:
            #if there's any error (or blank: not ment to have a number), return -1
            return -1

    #browse files in disciple image file
    def BrowseDiscipleImageFile(self):
        dContainer=QtGui.QDialog(self)
        dContainer.setWindowTitle("Select what to translate")
        dContainer.setModal(True)
        
        Dview=QtGui.QListView()
        Dview.myfont=QtGui.QFont('monospace',10)
        Dview.setFont(Dview.myfont)
        maxwidth=0

        Dmodel=QtGui.QStandardItemModel()
        
        di=disciplefile.DiscipleImage(self.leFileNameIn.text())
        
        for df in di.IterateDiscipleFiles():
            #do we have a valid entry?
            if(not df.IsEmpty()):
                txt='%(filenumber)2d "%(filename)s"%(sectors)4d %(filetypeshort)s %(catextradata)s' % df.GetFileDetails()
                maxwidth=max(Dview.fontMetrics().width(txt),maxwidth)
                line=QtGui.QStandardItem(txt)
                line.Ddata=df
                line.setEditable(False)
                Dmodel.appendRow(line)
       
        Dview.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        Dview.setModel(Dmodel)
        
        lay=QtGui.QVBoxLayout()
        
        lay.addWidget(Dview)

        lay2=QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok=QtGui.QPushButton("Ok",self)
        lay2.addWidget(ok)
        ok.clicked.connect(self.DiscipleEntrySelected)
        lay2.addStretch(1)
        close=QtGui.QPushButton("Cancel",self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)
        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        Dview.doubleClicked.connect(self.DiscipleEntrySelected)

        #ensure first item is always selected
        Dview.selectionModel().select(Dmodel.createIndex(0,0),QtGui.QItemSelectionModel.Select)

        #remember Dview and dialog
        self.Ddialog=dContainer
        self.Dview=Dview
        
        dContainer.show()
        Dview.setMinimumWidth(maxwidth+Dview.verticalScrollBar().width()+15)
        
        #run dialog, but forget Dview and dialog references if cancel pressed
        if(dContainer.exec_()==QtGui.QDialog.Rejected):
            del self.Ddialog
            del self.Dview

    def DiscipleEntrySelected(self,x):
        #retrieve references to what we need
        Dview=self.Dview
        Ddialog=self.Ddialog
        #tidy up self
        del self.Ddialog
        del self.Dview
        
        #close dialog
        Ddialog.accept()
        
        #if nothing selected then exit
        if(len(Dview.selectedIndexes())<1):
            return
        
        #retrieve Ddata
        index=Dview.selectedIndexes()[0]
        df=index.model().itemFromIndex(index).Ddata

        headder=df.GetHeadder()
        
        self.SetSourceLimits(-1,-1,df.filenumber)

        #save off filename incase want to export it
        self.ExportSettings["Filename"]=df.GetRawFileName()

        t=df.GetFileType(headder)
        if(t==1):
            #basic program
            self.SetBasicDetails(df.GetAutostartLine(headder),df.GetVariableOffset(headder))

        elif(t==2 or t==3):
            #number or character array
            self.SetVariableArrayDetails(df.GetVariableLetter(headder),df.GetArrayDescriptor(headder))

        elif(t==4):
            #bytes: can be screen or data/machine code
            if(df.GetFileLength(headder)==6912):
                  self.SetScreenDetails(df.GetCodeStart(headder))
                  
            else:
                  self.SetCodeDetails(df.GetCodeStart(headder))

        elif(t==7):
            #SCREEN$
            self.SetScreenDetails(df.GetCodeStart(headder))
            
        elif(t==7):
            #Execute
            self.SetCodeDetails(df.GetCodeStart(headder))

        else:
            #todo
            """            
            t==5: //48K snapshot
            t==9: //128K Snapshop
            t==6: //microdrive
            t==8: //Special
            t==10: //Opentype
            """
            #treat as raw data extract for now
            self.SetRawData()
        
    #browse files in TAP file
    def BrowseTapFile(self):
        dContainer=QtGui.QDialog(self)
        dContainer.setWindowTitle("Select what to translate")
        dContainer.setModal(True)
        
        tapmodel=QtGui.QStandardItemModel()
        tapmodel.setHorizontalHeaderLabels(['Tap Entries'])
        
        tbs=spectrumtapblock.get_TapBlocks(self.leFileNameIn.text())
        i=0
        while(i<len(tbs)):
            #do we have a headder that matches the following code block?
            if(i<len(tbs)-1 and tbs[i].is_headder() and tbs[i+1].flag==255 and len(tbs[i+1].data)==tbs[i].get_headder_described_data_length()):
                block=QtGui.QStandardItem(tbs[i].get_file_details_string())
                block.tapdata=tbs[i:i+2]
                line=QtGui.QStandardItem(str(tbs[i]))
                line.tapdata=tbs[i:i+1]
                line.setEditable(False)
                block.appendRow(line)
                line=QtGui.QStandardItem(str(tbs[i+1]))
                line.tapdata=tbs[i+1:i+2]
                line.setEditable(False)
                block.appendRow(line)
                block.setEditable(False)
                i+=2
                tapmodel.appendRow(block)
            #if not treat it as simple block of data
            else:
                line=QtGui.QStandardItem(str(tbs[i]))
                line.tapdata=tbs[i:i+1]
                line.setEditable(False)
                tapmodel.appendRow(line)
                i+=1
       
        tapview=QtGui.QTreeView()
        tapview.myfont=QtGui.QFont('monospace',10)
        tapview.setFont(tapview.myfont)
        tapview.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        tapview.setModel(tapmodel)
        tapview.setUniformRowHeights(True)
        
        lay=QtGui.QVBoxLayout()
        
        lay.addWidget(tapview)

        lay2=QtGui.QHBoxLayout()
        lay2.addStretch(1)
        ok=QtGui.QPushButton("Ok",self)
        lay2.addWidget(ok)
        ok.clicked.connect(self.TapEntrySelected)
        lay2.addStretch(1)
        close=QtGui.QPushButton("Cancel",self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)
        lay.addLayout(lay2)

        dContainer.setLayout(lay)

        tapview.doubleClicked.connect(self.TapEntrySelected)
        tapview.setExpandsOnDoubleClick(False)

        #ensure first item is always selected
        tapview.selectionModel().select(tapmodel.createIndex(0,0),QtGui.QItemSelectionModel.Select)

        #remember tapview and dialog
        self.tapdialog=dContainer
        self.tapview=tapview

        #run dialog, but forget tapview and dialog references if cancel pressed
        if(dContainer.exec_()==QtGui.QDialog.Rejected):
            del self.tapdialog
            del self.tapview

    def BrowseFileHex(self):

        if(not os.path.isfile(self.leFileNameIn.text())):
            return

        #get contents of file
        try:
            fo=open(self.leFileNameIn.text(),"rb")
            data=fo.read()
            fo.close()
        except:
            QtGui.QMessageBox.warning(self,"Error",'Unable to read file:\n"%s"' % self.leFileNameIn.text())
            return

        #create dialog
        dContainer=QtGui.QDialog(self)
        dContainer.setWindowTitle("Select start & end")
        dContainer.setModal(True)
        
        lay=QtGui.QVBoxLayout()
        
        lay2=QtGui.QHBoxLayout()
        lay2.addStretch(1)

        select_group=QtGui.QButtonGroup(dContainer)
        rb0=QtGui.QRadioButton("Select start")
        rb0.setChecked(True)
        lay2.addWidget(rb0)
        select_group.addButton(rb0)
        rb1=QtGui.QRadioButton("Select end")
        lay2.addWidget(rb1)
        select_group.addButton(rb1)
        
        ok=QtGui.QPushButton("Ok",self)
        lay2.addWidget(ok)
        ok.clicked.connect(dContainer.accept)
        close=QtGui.QPushButton("Cancel",self)
        lay2.addWidget(close)
        close.clicked.connect(dContainer.reject)
        lay2.addStretch(1)

        lay3=QtGui.QHBoxLayout()
        scroll=QtGui.QScrollBar(QtCore.Qt.Vertical)
        hexview=SpectrumFileTranslateGUI.StartStopDisplayPanel(data,self.getNumber(self.leDataOffset),self.getNumber(self.leDataEnd),rb0,scroll)
        lay3.addWidget(hexview)
        hexview.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        hexview.sizePolicy().setHorizontalStretch(1)
        lay3.addWidget(scroll)

        lay.addLayout(lay3)
        lay.addLayout(lay2)

        dContainer.setLayout(lay)
        
        #set to same size as parent
        dContainer.setGeometry(self.geometry())

        #run dialog, and if ok selected get start & stop points
        if(dContainer.exec_()==QtGui.QDialog.Accepted):
            self.SetSourceLimits(hexview.selectStart,hexview.selectEnd-hexview.selectStart)

        
    def TapEntrySelected(self,x):
        #retrieve references to what we need
        tapview=self.tapview
        tapdialog=self.tapdialog
        #tidy up self
        del self.tapdialog
        del self.tapview
        
        #close dialog
        tapdialog.accept()
        
        #if nothing selected then exit
        if(len(tapview.selectedIndexes())<1):
            return
        
        #retrieve tapdata
        index=tapview.selectedIndexes()[0]
        tapdata=index.model().itemFromIndex(index).tapdata
        
        #if only 1 tap block then is individual tapblock. treat as code
        if(len(tapdata)==1):
            #set values
            self.SetSourceLimits(tapdata[0].get_data_start_offset(),len(tapdata[0].data))
            self.SetCodeDetails(0)
        
            return
        
        #if not then should contain 2 TapBlocks: headder & data block.
        self.SetSourceLimits(tapdata[1].get_data_start_offset(),len(tapdata[1].data),-1)
        
        #save off filename incase want to export it
        self.ExportSettings["Filename"]=tapdata[0].get_raw_file_name()
        
        if(ord(tapdata[0].data[0])==0):
            #basic program
            self.SetBasicDetails(tapdata[0].get_headder_autostart_line(),tapdata[0].get_headder_variable_offset())
            
        elif(ord(tapdata[0].data[0])==1 or ord(tapdata[0].data[0])==2):
            #number or character array
            self.SetVariableArrayDetails(tapdata[0].get_headder_variable_letter(),tapdata[0].get_headder_array_descriptor())

        elif(ord(tapdata[0].data[0])==3):
            #bytes: can be screen or data/machine code
            if(len(tapdata[1].data)==6912):
                  self.SetScreenDetails(tapdata[0].get_headder_code_start())
                  
            else:
                  self.SetCodeDetails(tapdata[0].get_headder_code_start())

        else:
            #default to code block
            self.SetCodeDetails(0)

    def SetSourceLimits(self,datastartoffset,datalength,filenumber=-1):
        self.leDataOffset.setText(self.FormatNumber(datastartoffset))
        self.leDataEnd.setText("" if datalength==-1 else self.FormatNumber(datastartoffset+datalength-1))
        self.leDataFile.setText(self.FormatNumber(filenumber))

    def SetCodeDetails(self,origin):
        self.leBasicAutoLine.setText("")
        self.leBasicVariableOffset.setText("")
        self.leArrayVarName.setText("")
        self.leCodeOrigin.setText(self.FormatNumber(origin))
        setCombo(self.cbDataType,"Machine Code")
        self.SetTranslateButtonText()
        self.settingsstack.setCurrentIndex(1)

    def SetScreenDetails(self,origin):
        self.leBasicAutoLine.setText("")
        self.leBasicVariableOffset.setText("")
        self.leArrayVarName.setText("")
        self.leCodeOrigin.setText(self.FormatNumber(origin))
        setCombo(self.cbDataType,"Screen")
        self.SetTranslateButtonText()
        self.settingsstack.setCurrentIndex(3)

    def SetVariableArrayDetails(self,variableletter,arraydescriptor):
        self.leBasicAutoLine.setText("")
        self.leBasicVariableOffset.setText("")
        self.leArrayVarName.setText(spectrumtranslate.get_spectrum_char(variableletter))
        i=arraydescriptor
        i/=64
        i+=1
        i%=3
        self.cbArrayVarType.setCurrentIndex(i)
        self.leCodeOrigin.setText(self.FormatNumber(0))
        setCombo(self.cbDataType,"Variable Array")
        self.SetTranslateButtonText()
        self.settingsstack.setCurrentIndex(2)

    def  SetBasicDetails(self,autoline,variableoffset):
        self.leBasicAutoLine.setText("" if (autoline<0) else self.FormatNumber(autoline))
        self.leBasicVariableOffset.setText(self.FormatNumber(variableoffset))
        self.leArrayVarName.setText("")
        self.leCodeOrigin.setText(self.FormatNumber(0))
        setCombo(self.cbDataType,"Basic Program")
        self.SetTranslateButtonText()
        self.settingsstack.setCurrentIndex(0)

    def SetRawData(self):
        self.leBasicAutoLine.setText("")
        self.leBasicVariableOffset.setText("")
        self.leArrayVarName.setText("")
        self.leCodeOrigin.setText(self.FormatNumber(0))
        setCombo(self.cbDataType,"Raw Data")
        self.SetTranslateButtonText()
        self.settingsstack.setCurrentIndex(4)
        
    def FormatNumber(self,n):
        if(n==-1):
            return ""
            
        #format provided number to current number format
        form=('{0:X}','{0:d}','{0:o}','{0:b}')[self.cbNumberFormat.currentIndex()]
        
        return form.format(n)

    def handle_changed_text(self,txt):
        if(self.leFileNameIn.hasFocus()):
            self.CheckIfKnownContainerFile()
            #QtGui.QMessageBox.information(self,"Test","txt="+txt)

    def CheckIfKnownContainerFile(self):
        if(os.path.isfile(self.leFileNameIn.text())):

            self.bBrowseHex.setEnabled(True)
            
            #try extracting from tap file
            try:
                tbs=spectrumtapblock.get_TapBlocks(self.leFileNameIn.text())
                if(len(tbs)>0):
                    self.bBrowseContainer.setText("Browse TAP")
                    self.bBrowseContainer.setEnabled(True)
                    return
            except:
                tbs=[]
            
            #try from disciple/+D image file
            try:
                di=disciplefile.DiscipleImage(self.leFileNameIn.text())
                
                if(di.CheckImageIsValid(True)):
                    self.bBrowseContainer.setText("Browse disk image")
                    self.bBrowseContainer.setEnabled(True)
                    return
                    
            except:
                #ignore errors, and fall through into further browsing options
                pass

        else:
            self.bBrowseHex.setEnabled(False)

        self.bBrowseContainer.setText("Browse contents")
        self.bBrowseContainer.setEnabled(False)
        
def main(fileToOpen=None):
    
    app=QtGui.QApplication(sys.argv)
    
    sftGUI=SpectrumFileTranslateGUI(fileToOpen)

    #todo remove once debugging complete
    #sftGUI=SpectrumFileTranslateGUI('/home/william/RR.tap/REBRAID1.TAP')
    #sftGUI=SpectrumFileTranslateGUI("/home/william/java/tap reader/01.img")
    
    #move screen to right for debugging
    screen=QtGui.QDesktopWidget().screenGeometry()
    mysize=sftGUI.geometry()
    hpos=screen.width()-mysize.width()
    sftGUI.move(hpos,0)
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv)>1 else None)
