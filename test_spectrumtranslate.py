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
# software, even if advised of the possibility of such damage.
#
# Author: william.fraser@virgin.net
# Date: 14th January 2015

"""
Unit Test for SpectrumTranslate file
"""

import spectrumtranslate
import spectrumnumber
import unittest
from PIL import Image
from sys import hexversion as _PYTHON_VERSION_HEX
from codecs import unicode_escape_decode as _UED
from io import BytesIO

_TEST_DIRECTORY = "test/"

if(_PYTHON_VERSION_HEX > 0x03000000):
    def _u(x):
        return x

    def _getfileaslist(name):
        with open(_TEST_DIRECTORY + name, 'rb') as infile:
            return [b for b in infile.read()]

else:
    def _u(x):
        return _UED(x)[0]

    def _getfileaslist(name):
        with open(_TEST_DIRECTORY + name, 'rb') as infile:
            return [ord(b) for b in infile.read()]


class Testbasicconversion(unittest.TestCase):
    def test_basictotext(self):
        data = _getfileaslist("basictest.dat")
        self.assertEqual(spectrumtranslate.basictotext(data), _u("""\
10 REM ^16^00^00\u259C^11^05\u2597^11^03hello123^11^01^10^05^11^06
15 PRINT ^10^00^11^07"80"
20 DATA 1(number without value),2(1024),3,4: LIST : NEW 


Variables:
a=-2.2
test=65537
b[10]={
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10
}
d$[2][2]={
  "AB",
  "  "
}
FOR...NEXT, c Value=11 Limit=10 Step=1 Loop back to line=65534, statement=6
z$="testing"
"""))

    def test_basictoxml(self):
        data = _getfileaslist("basictest.dat")
        self.assertEqual(spectrumtranslate.basictoxml(data), _u("""\
<?xml version="1.0" encoding="UTF-8" ?>
<basiclisting>
  <line>
    <linenumber>10</linenumber>
    <instruction>
      <keyword>REM</keyword>
      <argument>^16^00^00\u259C^11^05\u2597^11^03hello123^11^01^10^05^11^06</argument>
    </instruction>
  </line>
  <line>
    <linenumber>15</linenumber>
    <instruction>
      <keyword>PRINT</keyword>
      <argument><format>INK 0</format><format>PAPER 7</format>"80"</argument>
    </instruction>
  </line>
  <line>
    <linenumber>20</linenumber>
    <instruction>
      <keyword>DATA</keyword>
      <argument><number>1<realvalue>number without value</realvalue></number>,\
<number>2<realvalue>1024</realvalue></number>,<number>3</number>,<number>4\
</number></argument>
    </instruction>
    <instructionseperator>:</instructionseperator>
    <instruction>
      <keyword>LIST</keyword>
    </instruction>
    <instructionseperator>:</instructionseperator>
    <instruction>
      <keyword>NEW</keyword>
    </instruction>
  </line>
  <variables>
    <variable>
      <name>a</name>
      <type>number</type>
      <value>-2.2</value>
    </variable>
    <variable>
      <name>test</name>
      <type>number</type>
      <value>65537</value>
    </variable>
    <variable>
      <name>b</name>
      <type>numberarray</type>
      <value>
        <dimension>
          <number>1</number>
          <number>2</number>
          <number>3</number>
          <number>4</number>
          <number>5</number>
          <number>6</number>
          <number>7</number>
          <number>8</number>
          <number>9</number>
          <number>10</number>
        </dimension>
      </value>
    </variable>
    <variable>
      <name>d$</name>
      <type>characterarray</type>
      <value>
        <dimension>
          <string>AB</string>
          <string>  </string>
        </dimension>
      </value>
    </variable>
    <variable>
      <name>c</name>
      <type>fornext</type>
      <value>11</value>
      <limit>10</limit>
      <step>1</step>
      <loopbackto>
        <line>65534</line>
        <statement>6</statement>
      </loopback>
    </variable>
    <variable>
      <name>z$</name>
      <type>string</type>
      <value>testing</value>
    </variable>
  </variables>
</basiclisting>
"""))


class TestArrayConversion(unittest.TestCase):
    def test_getarraydepth(self):
        data = _getfileaslist("arraytest_number.dat")
        self.assertEqual(spectrumtranslate.getarraydepth(data, 0x98), 2)
        data = _getfileaslist("arraytest_char.dat")
        self.assertEqual(spectrumtranslate.getarraydepth(data, 0xD3), 3)

    def test_extractarray(self):
        data = _getfileaslist("arraytest_number.dat")
        data = spectrumtranslate.extractarray(data, 0x98)
        correctvalues = [[round(x * y * 0.1, 2) for y in range(1, 11)] for x
                         in range(1, 21)]

        # convert spectrumnumbers to floats
        data = [[float(x) for x in row] for row in data]
        # now compare
        self.assertEqual(data, correctvalues)

        data = _getfileaslist("arraytest_char.dat")
        self.assertEqual(spectrumtranslate.extractarray(data, 0xD3),
                         [['test', 'mum ', 'good'], ['one ', 'two ', 'thre']])

    def test_arraytotext(self):
        data = _getfileaslist("arraytest_number.dat")
        self.assertEqual(spectrumtranslate.arraytotext(data, 0x98), """{
  {
    0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1
  },
  {
    0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2
  },
  {
    0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3
  },
  {
    0.4, 0.8, 1.2, 1.6, 2, 2.4, 2.8, 3.2, 3.6, 4
  },
  {
    0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5
  },
  {
    0.6, 1.2, 1.8, 2.4, 3, 3.6, 4.2, 4.8, 5.4, 6
  },
  {
    0.7, 1.4, 2.1, 2.8, 3.5, 4.2, 4.9, 5.6, 6.3, 7
  },
  {
    0.8, 1.6, 2.4, 3.2, 4, 4.8, 5.6, 6.4, 7.2, 8
  },
  {
    0.9, 1.8, 2.7, 3.6, 4.5, 5.4, 6.3, 7.2, 8.1, 9
  },
  {
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10
  },
  {
    1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 11
  },
  {
    1.2, 2.4, 3.6, 4.8, 6, 7.2, 8.4, 9.6, 10.8, 12
  },
  {
    1.3, 2.6, 3.9, 5.2, 6.5, 7.8, 9.1, 10.4, 11.7, 13
  },
  {
    1.4, 2.8, 4.2, 5.6, 7, 8.4, 9.8, 11.2, 12.6, 14
  },
  {
    1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12, 13.5, 15
  },
  {
    1.6, 3.2, 4.8, 6.4, 8, 9.6, 11.2, 12.8, 14.4, 16
  },
  {
    1.7, 3.4, 5.1, 6.8, 8.5, 10.2, 11.9, 13.6, 15.3, 17
  },
  {
    1.8, 3.6, 5.4, 7.2, 9, 10.8, 12.6, 14.4, 16.2, 18
  },
  {
    1.9, 3.8, 5.7, 7.6, 9.5, 11.4, 13.3, 15.2, 17.1, 19
  },
  {
    2, 4, 6, 8, 10, 12, 14, 16, 18, 20
  }
}""")

        data = _getfileaslist("arraytest_char.dat")
        self.assertEqual(spectrumtranslate.arraytotext(data, 0xD3), """{
  {
    "test",
    "mum ",
    "good"
  },
  {
    "one ",
    "two ",
    "thre"
  }
}""")

    def test_arraytoxml(self):
        data = _getfileaslist("arraytest_number.dat")
        self.assertEqual(spectrumtranslate.arraytoxml(data, 0x98), """\
<dimension>
  <dimension>
    <number>0.1</number>
    <number>0.2</number>
    <number>0.3</number>
    <number>0.4</number>
    <number>0.5</number>
    <number>0.6</number>
    <number>0.7</number>
    <number>0.8</number>
    <number>0.9</number>
    <number>1</number>
  </dimension>
  <dimension>
    <number>0.2</number>
    <number>0.4</number>
    <number>0.6</number>
    <number>0.8</number>
    <number>1</number>
    <number>1.2</number>
    <number>1.4</number>
    <number>1.6</number>
    <number>1.8</number>
    <number>2</number>
  </dimension>
  <dimension>
    <number>0.3</number>
    <number>0.6</number>
    <number>0.9</number>
    <number>1.2</number>
    <number>1.5</number>
    <number>1.8</number>
    <number>2.1</number>
    <number>2.4</number>
    <number>2.7</number>
    <number>3</number>
  </dimension>
  <dimension>
    <number>0.4</number>
    <number>0.8</number>
    <number>1.2</number>
    <number>1.6</number>
    <number>2</number>
    <number>2.4</number>
    <number>2.8</number>
    <number>3.2</number>
    <number>3.6</number>
    <number>4</number>
  </dimension>
  <dimension>
    <number>0.5</number>
    <number>1</number>
    <number>1.5</number>
    <number>2</number>
    <number>2.5</number>
    <number>3</number>
    <number>3.5</number>
    <number>4</number>
    <number>4.5</number>
    <number>5</number>
  </dimension>
  <dimension>
    <number>0.6</number>
    <number>1.2</number>
    <number>1.8</number>
    <number>2.4</number>
    <number>3</number>
    <number>3.6</number>
    <number>4.2</number>
    <number>4.8</number>
    <number>5.4</number>
    <number>6</number>
  </dimension>
  <dimension>
    <number>0.7</number>
    <number>1.4</number>
    <number>2.1</number>
    <number>2.8</number>
    <number>3.5</number>
    <number>4.2</number>
    <number>4.9</number>
    <number>5.6</number>
    <number>6.3</number>
    <number>7</number>
  </dimension>
  <dimension>
    <number>0.8</number>
    <number>1.6</number>
    <number>2.4</number>
    <number>3.2</number>
    <number>4</number>
    <number>4.8</number>
    <number>5.6</number>
    <number>6.4</number>
    <number>7.2</number>
    <number>8</number>
  </dimension>
  <dimension>
    <number>0.9</number>
    <number>1.8</number>
    <number>2.7</number>
    <number>3.6</number>
    <number>4.5</number>
    <number>5.4</number>
    <number>6.3</number>
    <number>7.2</number>
    <number>8.1</number>
    <number>9</number>
  </dimension>
  <dimension>
    <number>1</number>
    <number>2</number>
    <number>3</number>
    <number>4</number>
    <number>5</number>
    <number>6</number>
    <number>7</number>
    <number>8</number>
    <number>9</number>
    <number>10</number>
  </dimension>
  <dimension>
    <number>1.1</number>
    <number>2.2</number>
    <number>3.3</number>
    <number>4.4</number>
    <number>5.5</number>
    <number>6.6</number>
    <number>7.7</number>
    <number>8.8</number>
    <number>9.9</number>
    <number>11</number>
  </dimension>
  <dimension>
    <number>1.2</number>
    <number>2.4</number>
    <number>3.6</number>
    <number>4.8</number>
    <number>6</number>
    <number>7.2</number>
    <number>8.4</number>
    <number>9.6</number>
    <number>10.8</number>
    <number>12</number>
  </dimension>
  <dimension>
    <number>1.3</number>
    <number>2.6</number>
    <number>3.9</number>
    <number>5.2</number>
    <number>6.5</number>
    <number>7.8</number>
    <number>9.1</number>
    <number>10.4</number>
    <number>11.7</number>
    <number>13</number>
  </dimension>
  <dimension>
    <number>1.4</number>
    <number>2.8</number>
    <number>4.2</number>
    <number>5.6</number>
    <number>7</number>
    <number>8.4</number>
    <number>9.8</number>
    <number>11.2</number>
    <number>12.6</number>
    <number>14</number>
  </dimension>
  <dimension>
    <number>1.5</number>
    <number>3</number>
    <number>4.5</number>
    <number>6</number>
    <number>7.5</number>
    <number>9</number>
    <number>10.5</number>
    <number>12</number>
    <number>13.5</number>
    <number>15</number>
  </dimension>
  <dimension>
    <number>1.6</number>
    <number>3.2</number>
    <number>4.8</number>
    <number>6.4</number>
    <number>8</number>
    <number>9.6</number>
    <number>11.2</number>
    <number>12.8</number>
    <number>14.4</number>
    <number>16</number>
  </dimension>
  <dimension>
    <number>1.7</number>
    <number>3.4</number>
    <number>5.1</number>
    <number>6.8</number>
    <number>8.5</number>
    <number>10.2</number>
    <number>11.9</number>
    <number>13.6</number>
    <number>15.3</number>
    <number>17</number>
  </dimension>
  <dimension>
    <number>1.8</number>
    <number>3.6</number>
    <number>5.4</number>
    <number>7.2</number>
    <number>9</number>
    <number>10.8</number>
    <number>12.6</number>
    <number>14.4</number>
    <number>16.2</number>
    <number>18</number>
  </dimension>
  <dimension>
    <number>1.9</number>
    <number>3.8</number>
    <number>5.7</number>
    <number>7.6</number>
    <number>9.5</number>
    <number>11.4</number>
    <number>13.3</number>
    <number>15.2</number>
    <number>17.1</number>
    <number>19</number>
  </dimension>
  <dimension>
    <number>2</number>
    <number>4</number>
    <number>6</number>
    <number>8</number>
    <number>10</number>
    <number>12</number>
    <number>14</number>
    <number>16</number>
    <number>18</number>
    <number>20</number>
  </dimension>
</dimension>""")

        data = _getfileaslist("arraytest_char.dat")
        self.assertEqual(spectrumtranslate.arraytoxml(data, 0xD3), """\
<dimension>
  <dimension>
    <string>test</string>
    <string>mum </string>
    <string>good</string>
  </dimension>
  <dimension>
    <string>one </string>
    <string>two </string>
    <string>thre</string>
  </dimension>
</dimension>""")


class TestUtilityFunctions(unittest.TestCase):
    def test_sn_to_string(self):
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumtranslate._sn_to_string, ([]))
        self.assertEqual(spectrumtranslate._sn_to_string([0, 0, 1, 1, 0]),
                         "257")
        self.assertEqual(spectrumtranslate._sn_to_string("", message="Test"),
                         "Test")

    def test_numbertostring(self):
        self.assertEqual(spectrumtranslate._numbertostring(0x501, 16, 0),
                         "#0501")
        self.assertEqual(spectrumtranslate._numbertostring(0x501, 8, 0),
                         "#501")
        self.assertEqual(spectrumtranslate._numbertostring(0x501, 16, 0,
                         False), "0501")
        self.assertEqual(spectrumtranslate._numbertostring(1, 8, 0), "#01")
        self.assertEqual(spectrumtranslate._numbertostring(17, 8, 0), "#11")
        self.assertEqual(spectrumtranslate._numbertostring(65535, 16, 0),
                         "#FFFF")

        self.assertEqual(spectrumtranslate._numbertostring(655, 16, 1), "655")
        self.assertEqual(spectrumtranslate._numbertostring(655, 8, 1, False),
                         "655")

        self.assertEqual(spectrumtranslate._numbertostring(80, 8, 2), "o120")
        self.assertEqual(spectrumtranslate._numbertostring(81, 16, 2, False),
                         "000121")

        self.assertEqual(spectrumtranslate._numbertostring(127, 8, 3),
                         "b01111111")
        self.assertEqual(spectrumtranslate._numbertostring(257, 8, 3, False),
                         "100000001")

        self.assertEqual(spectrumtranslate._numbertostring(20, 6, 10), "")

    def test_newSpectrumTranslateError(self):
        error = spectrumtranslate._newSpectrumTranslateError(16384, 6,
                                                             "<code here>",
                                                             "Test")
        self.assertEqual(error.value, 'Data Format error processing "<code \
here>" near character number 6 on line starting at 4000\nTest')


class TestTextConvert(unittest.TestCase):
    spectrumchars = ("^00", "^01", "^02", "^03", "^04", "^05", "^06", "^07",
                     "^08", "^09", "^0A", "^0B", "^0C", "^0D", "^0E", "^0F",
                     "^10", "^11", "^12", "^13", "^14", "^15", "^16", "^17",
                     "^18", "^19", "^1A", "^1B", "^1C", "^1D", "^1E", "^1F",
                     " ", "!", '"', "#", "$", "%", "&", "'",
                     "(", ")", "*", "+", ",", "-", ".", "/",
                     "0", "1", "2", "3", "4", "5", "6", "7",
                     "8", "9", ":", ";", "<", "=", ">", "?",
                     "@", "A", "B", "C", "D", "E", "F", "G",
                     "H", "I", "J", "K", "L", "M", "N", "O",
                     "P", "Q", "R", "S", "T", "U", "V", "W",
                     "X", "Y", "Z", "[", "\\", "]", _u("\u2191"), "_",
                     _u("\u00A3"), "a", "b", "c", "d", "e", "f", "g",
                     "h", "i", "j", "k", "l", "m", "n", "o",
                     "p", "q", "r", "s", "t", "u", "v", "w",
                     "x", "y", "z", "{", "|", "}", "~", _u("\u00A9"),
                     _u('\u2003'), _u('\u259D'), _u('\u2598'), _u('\u2580'),
                     _u('\u2597'), _u('\u2590'), _u('\u259A'), _u('\u259C'),
                     _u('\u2596'), _u('\u259E'), _u('\u258C'), _u('\u259B'),
                     _u('\u2584'), _u('\u259F'), _u('\u2599'), _u('\u2588'),
                     "^90", "^91", "^92", "^93", "^94", "^95", "^96", "^97",
                     "^98", "^99", "^9A", "^9B", "^9C", "^9D", "^9E", "^9F",
                     "^A0", "^A1", "^A2", "SPECTRUM ",
                     "PLAY ", "RND ", "INKEY$ ", "PI ",
                     "FN ", "POINT ", "SCREEN$ ", "ATTR ",
                     "AT ", "TAB ", "VAL$ ", "CODE ",
                     "VAL ", "LEN ", "SIN ", "COS ",
                     "TAN ", "ASN ", "ACS ", "ATN ",
                     "LN ", "EXP ", "INT ", "SQR ",
                     "SGN ", "ABS ", "PEEK ", "IN ",
                     "USR ", "STR$ ", "CHR$ ", "NOT ",
                     "BIN ", "OR ", "AND ", "<= ",
                     ">= ", "<> ", "LINE ", "THEN ",
                     "TO ", "STEP ", "DEF FN ", "CAT ",
                     "FORMAT ", "MOVE ", "ERASE ", "OPEN # ",
                     "CLOSE # ", "MERGE ", "VERIFY ", "BEEP ",
                     "CIRCLE ", "INK ", "PAPER ", "FLASH ",
                     "BRIGHT ", "INVERSE ", "OVER ", "OUT ",
                     "LPRINT ", "LLIST ", "STOP ", "READ ",
                     "DATA ", "RESTORE ", "NEW ", "BORDER ",
                     "CONTINUE ", "DIM ", "REM ", "FOR ",
                     "GO TO ", "GO SUB ", "INPUT ", "LOAD ",
                     "LIST ", "LET ", "PAUSE ", "NEXT ",
                     "POKE ", "PRINT ", "PLOT ", "RUN ",
                     "SAVE ", "RANDOMIZE ", "IF ", "CLS ",
                     "DRAW ", "CLEAR ", "RETURN ", "COPY ")

    def test_getspectrumchar(self):
        for code, character in enumerate(self.spectrumchars):
            self.assertEqual(spectrumtranslate.getspectrumchar(code),
                             character)

    def test_getspectrumstring(self):
        self.assertEqual(
            spectrumtranslate.getspectrumstring([x for x in range(256)]),
            ''.join(self.spectrumchars))

    def test_chartospectrum(self):
        for code, character in enumerate(self.spectrumchars):
            self.assertEqual(spectrumtranslate.chartospectrum(character),
                             chr(code))

    def test_stringtospectrum(self):
        self.assertEqual(
            spectrumtranslate.stringtospectrum(''.join(self.spectrumchars)),
            ''.join([chr(x) for x in range(256)]))

"""
class TestImageConvert(unittest.TestCase):
    def imageto32bitlist(self, im):
        return [(xy[0] << 16) + (xy[1] << 8) + xy[2] for xy in
                im.convert("RGB").getdata()]

    def test_getgiffromscreen(self):
        # get reference images
        irReference = Image.open(_TEST_DIRECTORY + "screentest.gif")
        refimage1 = self.imageto32bitlist(irReference)
        irReference.seek(1)
        refimage2 = self.imageto32bitlist(irReference)

        # get image created by spectrumtranslate
        gifscreen = spectrumtranslate.getgiffromscreen(
            _getfileaslist("screentest.dat"))
        # should have valid gif now
        gifimage = Image.open(BytesIO(gifscreen))
        # should be 2 images
        gifimage1 = self.imageto32bitlist(gifimage)
        self.assertEqual(gifimage.info["duration"], 320)
        gifimage.seek(1)
        gifimage2 = self.imageto32bitlist(gifimage)
        self.assertEqual(gifimage.info["duration"], 320)
        # ensure only 2 images
        self.assertRaises(EOFError, gifimage.seek, 2)

        # compare images now
        self.assertEqual(refimage1, gifimage1)
        self.assertEqual(refimage2, gifimage2)

    def test_getrgbfromscreen(self):
        # get reference images
        irReference = Image.open(_TEST_DIRECTORY + "screentest.gif")
        refimage1 = self.imageto32bitlist(irReference)
        irReference.seek(1)
        refimage2 = self.imageto32bitlist(irReference)

        gifscreen = spectrumtranslate.getrgbfromscreen(
            _getfileaslist("screentest.dat"), alphamask=0)
        # should have valid list of RGB values

        # should be 2 images
        self.assertEqual(type(gifscreen), list)
        self.assertEqual(len(gifscreen), 2)
        self.assertEqual(type(gifscreen[0]), list)
        self.assertEqual(type(gifscreen[1]), list)

        # compare images now
        self.assertEqual(refimage1, gifscreen[0])
        self.assertEqual(refimage2, gifscreen[1])


class TestSnapConvert(unittest.TestCase):
    # todo : test snap files once I have snap files to test
    def test_snaptosna(self):
        pass

    def test_snaptoz80(self):
        pass
"""


class TestDisassembleInstruction(unittest.TestCase):
    def test_create(self):
        di = spectrumtranslate.DisassembleInstruction(0x0100)
        self.assertEqual(di.instruction, 0x0100)
        self.assertEqual(di.start, 0)
        self.assertEqual(di.end, 65536)
        self.assertEqual(di.data, None)

        di = spectrumtranslate.DisassembleInstruction("Custom Format")
        self.assertEqual(di.instruction, 0x0700)
        self.assertEqual(di.start, 0)
        self.assertEqual(di.end, 65536)
        self.assertEqual(di.data, None)

        di = spectrumtranslate.DisassembleInstruction(0x0101, start=16384,
                                                      end=30000,
                                                      data="hello")
        self.assertEqual(di.instruction, 0x0101)
        self.assertEqual(di.start, 0x4000)
        self.assertEqual(di.end, 30000)
        self.assertEqual(di.data, "hello")

        di2 = spectrumtranslate.DisassembleInstruction(di)
        self.assertEqual(di2.instruction, 0x0101)
        self.assertEqual(di2.start, 0x4000)
        self.assertEqual(di2.end, 30000)
        self.assertEqual(di2.data, "hello")

        di = spectrumtranslate.DisassembleInstruction("200#4000#FFFF#")
        self.assertEqual(di.instruction, 0x0200)
        self.assertEqual(di.start, 16384)
        self.assertEqual(di.end, 65535)
        self.assertEqual(di.data, None)

        di = spectrumtranslate.DisassembleInstruction(
            "D00#0100#4000#4,7,C#Thisistestdata")
        self.assertEqual(di.instruction, 0x0D00)
        self.assertEqual(di.start, 256)
        self.assertEqual(di.end, 16384)
        self.assertEqual(di.data, "This\nis\ntest\ndata")

    def test_isformatinstruction(self):
        self.assertTrue(spectrumtranslate.DisassembleInstruction(0x0800).
                        isformatinstruction())
        self.assertFalse(spectrumtranslate.DisassembleInstruction(0x010000).
                         isformatinstruction())

    def test_tostring(self):
        di = spectrumtranslate.DisassembleInstruction(0x0200)
        di.start = 16384
        di.end = 65535
        self.assertEqual(str(di), "200#4000#FFFF#")

        di = spectrumtranslate.DisassembleInstruction(0x0D00)
        di.start = 256
        di.end = 16384
        di.data = """\
This
is
test
data"""
        self.assertEqual(str(di), "D00#100#4000#4,7,C#Thisistestdata")

    def test_cmp(self):
        di1 = spectrumtranslate.DisassembleInstruction(0x0100, start=0x4000)
        di2 = spectrumtranslate.DisassembleInstruction(0x0100, start=0x8000)
        self.assertTrue(di1 < di2)
        self.assertFalse(di1 > di2)
        self.assertFalse(di1 == di2)

    def test_disassembledatablock(self):
        di = spectrumtranslate.DisassembleInstruction(
            "Data Block", 0x4000, 0x4008,
            spectrumtranslate.DisassembleInstruction.
            DISASSEMBLE_DATABLOCK_CODES["Define Message"])

        Settings = {"DATASTRINGPOS": 0,
                    "NUMBERFORMAT": 0,
                    "NUMBERSIGNED": 0,
                    "NUMBERWORDORDER": 0,
                    "DISPLAYEVERYXLINES": 1,
                    "ORIGIONALSEPERATOR": "  ",
                    "SEPERATOR": "  ",
                    "ORIGIN": 0x4000,
                    "ADDRESSOUTPUT": 0,
                    "NUMBEROUTPUT": 0,
                    "COMMANDOUTPUT": 0,
                    "XMLOutput": 0}

        data = (65, 66, 67, 127, 22, 0, 0, 49, 50)

        position, text = di.disassembledatablock(Settings, data, None)

        # check where position counter got to
        self.assertEqual(position, 0x4008)
        # check number formatting code (0 for marker, 4 for hex, display every
        # 1 line
        self.assertEqual([ord(x) for x in text[:3]], [0, 4, 1])
        # check text
        self.assertEqual(text[3:],
                         _u('4000    DM  "ABC\u00A9"^16^00^00"12"\n'))

    def test_numbertostring(self):
        self.assertEqual(spectrumtranslate._numbertostring(256, 16, 0, False),
                         "0100")
        self.assertEqual(spectrumtranslate._numbertostring(512, 8, 0, True),
                         "#200")

        self.assertEqual(spectrumtranslate._numbertostring(256, 16, 1, False),
                         "256")
        self.assertEqual(spectrumtranslate._numbertostring(512, 8, 1, True),
                         "512")

        self.assertEqual(spectrumtranslate._numbertostring(256, 16, 2, False),
                         "000400")
        self.assertEqual(spectrumtranslate._numbertostring(512, 8, 2, True),
                         "o1000")

        self.assertEqual(spectrumtranslate._numbertostring(256, 16, 3, False),
                         "0000000100000000")
        self.assertEqual(spectrumtranslate._numbertostring(512, 8, 3, True),
                         "b1000000000")

    def test_getnextcharacters(self):
        Settings = {"DATASTRINGPOS": 0}
        instruction = """
        %# this is a test to ignore
        \t%H %%%# more to avoid
        Hello"""
        self.assertEqual(spectrumtranslate._getnextcharacters(instruction,
                                                              Settings, 2),
                         "%H")
        self.assertEqual(spectrumtranslate._getnextcharacters(instruction,
                                                              Settings, 4),
                         "%%He")

    def test_movetoblockend(self):
        # instructions, Vars, Settings, commandstart
        Settings = {"DATASTRINGPOS": 11}
        Vars = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        instruction = """
        %(
          internal block
          %(
            Test
          %)
          Test block
          %# %)
        %)End
"""
        spectrumtranslate._movetoblockend(instruction, Vars, Settings, 11)
        self.assertEqual(Settings["DATASTRINGPOS"], 127)
        self.assertEqual(instruction[Settings["DATASTRINGPOS"]:], "End\n")

        Settings = {"DATASTRINGPOS": 0}
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtranslate._movetoblockend,
                          instruction, Vars, Settings, 0)

        Settings = {"DATASTRINGPOS": 49}
        spectrumtranslate._movetoblockend(instruction, Vars, Settings, 49)
        self.assertEqual(Settings["DATASTRINGPOS"], 79)
        self.assertEqual(instruction[Settings["DATASTRINGPOS"]:], """
          Test block
          %# %)
        %)End
""")

    def test_processcommandblock(self):
        Settings = {"DATASTRINGPOS": 0,
                    "NUMBERFORMAT": 0,
                    "NUMBERSIGNED": 0,
                    "NUMBERWORDORDER": 0,
                    "DISPLAYEVERYXLINES": 1,
                    "ORIGIONALSEPERATOR": "  ",
                    "SEPERATOR": "  ",
                    "ORIGIN": 0x4000,
                    "ADDRESSOUTPUT": 0,
                    "NUMBEROUTPUT": 0,
                    "COMMANDOUTPUT": 0,
                    "XMLOutput": 0}
        Vars = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x4000, 0, 0, 0x4000, 0x4001]

        # check tests
        instructions = "%( %?EQ%V00%V00 %?BO %?NE%V00%V00 Hello %)"
        self.assertEqual(spectrumtranslate._processcommandblock(instructions,
                                                                Vars,
                                                                Settings,
                                                                None,
                                                                False,
                                                                True,
                                                                None),
                         (1, ''))

        instructions = "%( %?EQ%V00%V00 %?BA %?NE%V00%V00 Hello %)"
        Settings["DATASTRINGPOS"] = 0
        self.assertEqual(spectrumtranslate._processcommandblock(instructions,
                                                                Vars,
                                                                Settings,
                                                                None,
                                                                False,
                                                                True,
                                                                None),
                         (0, 'Hello'))

        instructions = "%( %?EQ%V00%V00 %?BX %?NE%V00%V00 Hello %)"
        Settings["DATASTRINGPOS"] = 0
        self.assertEqual(spectrumtranslate._processcommandblock(instructions,
                                                                Vars,
                                                                Settings,
                                                                None,
                                                                False,
                                                                True,
                                                                None),
                         (1, 'Hello'))

        # test ReferencedLineNumbers
        instructions = "%W80"
        Settings["DATASTRINGPOS"] = 0
        ReferencedLineNumbers = []
        self.assertEqual(spectrumtranslate._processcommandblock(instructions,
                         Vars, Settings, None, False, True,
                         ReferencedLineNumbers), (0, '0000'))
        self.assertEqual(len(ReferencedLineNumbers), 1)
        self.assertEqual(ReferencedLineNumbers[0], 0)

        # test break and continue
        instructions = "%Y Hello"
        Settings["DATASTRINGPOS"] = 0
        self.assertEqual(spectrumtranslate._processcommandblock(instructions,
                                                                Vars,
                                                                Settings,
                                                                None,
                                                                False,
                                                                True,
                                                                None),
                         (2, ''))
        self.assertEqual(Settings["DATASTRINGPOS"], 2)

        instructions = "%Z Hello"
        Settings["DATASTRINGPOS"] = 0
        self.assertEqual(spectrumtranslate._processcommandblock(instructions,
                                                                Vars,
                                                                Settings,
                                                                None,
                                                                False,
                                                                True,
                                                                None),
                         (4, ''))
        self.assertEqual(Settings["DATASTRINGPOS"], 2)

    def test_get_custom_format_string(self):
        self.assertEqual(spectrumtranslate.get_custom_format_string(
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "Address Output Format Hex"],
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "Number Output Format Decimal"],
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "Command Output Format Octal"],
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "Output T States Format List All"],
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "Line After Jump None"],
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "Line Numbers Referenced"],
            7,
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "Empty Line After Data On"],
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "Reference Data Numbers Off"],
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "List Command Bytes On"],
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "Comments Off"],
            '~',
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "Display Flags On"],
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "Mark Undocumented Command On"],
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "XML Output On"]),
            '7A078E4~')

    def test_get_custom_format_values(self):
        self.assertEqual(
            spectrumtranslate.get_custom_format_values('7A078E4~', True),
            {'NumberOutput': spectrumtranslate.DisassembleInstruction.
                DISASSEMBLE_CODES["Number Output Format Decimal"],
             'TreatDataNumbersAsLineReferences': spectrumtranslate.
             DisassembleInstruction.DISASSEMBLE_CODES[
                 "Reference Data Numbers Off"],
             'OutputTStates': spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Output T States Format List All"],
             'DisplayComments': spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Comments Off"],
             'ShowFlags': spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Display Flags On"],
             'BreakAfterJumps': spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Line After Jump None"],
             'BreakAfterData': spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Empty Line After Data On"],
             'LineNumberOutput': spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Line Numbers Referenced"],
             'AddressOutput': spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Address Output Format Hex"],
             'MarkUndocumenedCommand': spectrumtranslate.
             DisassembleInstruction.DISASSEMBLE_CODES[
                 "Mark Undocumented Command On"],
             'DisplayCommandBytes': spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["List Command Bytes On"],
             'CommandOutput': spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Command Output Format Octal"],
             'Seperator': '~',
             'XMLOutput': spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["XML Output On"],
             'ListEveryXLines': 7})

        self.assertEqual(
            spectrumtranslate.get_custom_format_values('7A078E4~'),
            {'NumberOutput': 1,
             'TreatDataNumbersAsLineReferences': 1,
             'OutputTStates': 3,
             'DisplayComments': 1,
             'ShowFlags': 1,
             'BreakAfterJumps': 0,
             'BreakAfterData': 0,
             'LineNumberOutput': 2,
             'AddressOutput': 0,
             'MarkUndocumenedCommand': 1,
             'DisplayCommandBytes': 0,
             'CommandOutput': 2,
             'Seperator': '~',
             'XMLOutput': 1,
             'ListEveryXLines': 7})

    def test_getpartsofpatterndatablock(self):
        parts = spectrumtranslate.getpartsofpatterndatablock(
            spectrumtranslate.DisassembleInstruction.
            DISASSEMBLE_PATTERNBLOCK_CODES["RST#08 (Error)"])

        self.assertEqual(parts[0], """\
%(               %#start test block
  %?EQ%MV0F00CF  %#does the first byte equal 0xCF (code for RST #08)
%)               %#end test block""")
        self.assertEqual(parts[1], """\
%(               %#block to define first & last address of data block
  %X0200%V0F0001 %#start position (var0) is position of RST #08 command +1
  %X0101%V00     %#end position (var1) is start position (only 1 byte affter
                 %#                                       error restart)
%)               %#end variable setup block""")
        self.assertEqual(parts[2], """
                 %#start of data handling block
%S%S
%$I              %#start instruction xml tag
DEFB             %#output instuction (DEFB or Define Byte)
%$-I             %#close instruction xml tag
%S
%$D              %#start data tag
%F0000           %#set hex mode
%F0100           %#set unsigned
#%B0F            %#output contents of current address as byte and increment
                 %#current address\n%$-D             %#close data tag""")

    def test_createfindandcomment(self):
        self.assertEqual(spectrumtranslate.createfindandcomment("Hello\nTest",
                                                                "Comment", 4,
                                                                1),
                         """\
%(                   %#start test block
  %(                 %#start test code
Hello
Test
  %)                 %#end test code

  %?BA
  %?EQ00000000       %#test to ensure that false test fails now

  %X0200%V0F0004     %#var0 is position of code to check + length of command
                     %#start comment text
Comment
                     %#end comment text
  %;%V0F%V0010       %#Create comment instruction

  %?BA
  %?EQ00000001       %#Force fail test otherwise will be processed as pattern
%)                   %#end test block

%(
%)
""")

    def test_detailsfromfindandcomment(self):
        self.assertEqual(spectrumtranslate.detailsfromfindandcomment("Hello"),
                         None)
        self.assertEqual(spectrumtranslate.detailsfromfindandcomment(
                         spectrumtranslate.createfindandcomment("Hello\nTest",
                                                                "Comment",
                                                                4, 1)),
                         ["Hello\nTest", "Comment", 4, 1])

    def test_instructiontexttostring(self):
        self.assertEqual(spectrumtranslate.instructiontexttostring("""  Hello
% Mum%%%T%N."""),
                         "Hello Mum%\t\n.")

    def test_stringtoinstructiontext(self):
        self.assertEqual(spectrumtranslate.stringtoinstructiontext(
            "Hello Mum%\t\n."), "Hello% Mum%%%T%N.")

    def test_isfindandcomment(self):
        self.assertFalse(spectrumtranslate.isfindandcomment(spectrumtranslate.
                         DisassembleInstruction.
                         DISASSEMBLE_PATTERNBLOCK_CODES["RST#08 (Error)"]))

    def test_get_disassemblecodename_from_value(self):
        for name in spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES:
            self.assertEqual(spectrumtranslate.
                             get_disassemblecodename_from_value(
                                 spectrumtranslate.DisassembleInstruction.
                                 DISASSEMBLE_CODES[name]), name)

        self.assertEqual(spectrumtranslate.get_disassemblecodename_from_value(
            "invalid code name"), None)

    def test_get_disassembleblockname_from_value(self):
        for name in spectrumtranslate.DisassembleInstruction.\
                DISASSEMBLE_DATABLOCK_CODES_ORDERED:
            self.assertEqual(spectrumtranslate.
                             get_disassembleblockname_from_value(
                                 spectrumtranslate.DisassembleInstruction.
                                 DISASSEMBLE_DATABLOCK_CODES[name]), name)

        for name in spectrumtranslate.DisassembleInstruction.\
                DISASSEMBLE_PATTERNBLOCK_CODES_ORDERED:
            self.assertEqual(spectrumtranslate.
                             get_disassembleblockname_from_value(
                                 spectrumtranslate.DisassembleInstruction.
                                 DISASSEMBLE_PATTERNBLOCK_CODES[name]), name)

        self.assertEqual(spectrumtranslate.get_disassembleblockname_from_value(
            "invalid block name"), None)


class TestDisassembleCode(unittest.TestCase):
    def test_disassemble(self):
        tests = [
            # undocumented commands
            [[0xDD, 0xCB, 0x01, 0x01],
             [["Mark Undocumented Command Off"],
              ["Mark Undocumented Command On"], ["XML Output On"]],
             ["""ORG #4000

4000  DD,CB,01,01  LD C,RLC (IX+#01)    ;
""",
              """ORG #4000

4000  DD,CB,01,01  LD C,RLC (IX+#01)    ;Undocumented Command
""",
             """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>DD,CB,01,01</bytes><instruction>\
LD C,RLC (IX+#01)</instruction><flags>S+ Z+ H0 PVP N0 C+</flags><timeing>\
<cycles>unknown</cycles></timeing><undocumented/></line>
</z80code>"""]],
            # non-op codes DD00
            [[0xDD, 0x00],
             [["Address Output Format Hex"], ["XML Output On"]],
             ["""ORG #4000

4000  DD                                ;
4001  00           NOP                  ;
""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>DD</bytes><instruction></instruction>\
<timeing><cycles>unknown</cycles></timeing></line>
  <line><address>4001</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
</z80code>"""]],
            # time listings part 1
            [[0x7E],
             [["Output T States Format List All"],
              ["Output T States Format None"],
              ["Output T States Format Total"],
              ["Output T States Format List States"],
              ["XML Output On"]],
             ["""ORG #4000

4000  7E           LD A,(HL)            ;T=7(4,3)
""",
              """ORG #4000

4000  7E           LD A,(HL)            ;
""",
              """ORG #4000

4000  7E           LD A,(HL)            ;T=7
""",
              """ORG #4000

4000  7E           LD A,(HL)            ;T=(4,3)
""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>7E</bytes><instruction>LD A,(HL)\
</instruction><flags>S- Z- H- PV- N- C-</flags><timeing><cycles>7</cycles>\
<tstates>4,3</tstates></timeing></line>
</z80code>"""]],
            # time listings part 2
            [[0xDD, 00, 0x10, 0xFE, 0xC9],
             [["Output T States Format List All"], ["XML Output On"]],
             ["""ORG #4000

4000  DD                                ;T=unknown
4001  00           NOP                  ;T=4(4)
4002  10,FE        DJNZ #4002           ;T=13(5,3,5)/8(5,3)
4004  C9           RET                  ;T=10(4,3,3)

""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>DD</bytes><instruction></instruction>\
<timeing><cycles>unknown</cycles></timeing></line>
  <line><address>4001</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
  <line><address>4002</address><bytes>10,FE</bytes><instruction>DJNZ #4002\
</instruction><flags>S- Z- H- PV- N- C-</flags><timeing><cycles>13</cycles>\
<tstates>5,3,5</tstates></timeing><timeing alternate="true"><cycles>8</cycles>\
<tstates>5,3</tstates></timeing></line>
  <line><address>4004</address><bytes>C9</bytes><instruction>RET</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>10</cycles><tstates>4,3,3\
</tstates></timeing></line>
</z80code>"""]],
            # flags,
            [[0xCB, 0x47, 0x87, 0xA7],
             [["Display Flags Off"], ["Display Flags On"], ["XML Output On"]],
             ["""ORG #4000

4000  CB,47        BIT 0,A              ;
4002  87           ADD A,A              ;
4003  A7           AND A                ;
""",
              """ORG #4000

4000  CB,47        BIT 0,A              ;S? Z+ H1 PV? N0 C-
4002  87           ADD A,A              ;S+ Z+ H+ PVV N0 C+
4003  A7           AND A                ;S+ Z+ H1 PVP N0 C0
""",
             """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>CB,47</bytes><instruction>BIT 0,A\
</instruction><flags>S? Z+ H1 PV? N0 C-</flags><timeing><cycles>8</cycles>\
<tstates>4,4</tstates></timeing></line>
  <line><address>4002</address><bytes>87</bytes><instruction>ADD A,A\
</instruction><flags>S+ Z+ H+ PVV N0 C+</flags><timeing><cycles>4</cycles>\
<tstates>4</tstates></timeing></line>
  <line><address>4003</address><bytes>A7</bytes><instruction>AND A\
</instruction><flags>S+ Z+ H1 PVP N0 C0</flags><timeing><cycles>4</cycles>\
<tstates>4</tstates></timeing></line>
</z80code>"""]],
            # line after jump
            [[0xC3, 0x00, 0x00, 0xC2, 0x00, 0x00, 0x00],
             [["Line After Jump None"], ["Line After Jump After Absolute"],
              ["Line After Jump After All"], ["XML Output On"]],
             ["""ORG #4000

4000  C3,00,00     JP #0000             ;
4003  C2,00,00     JP NZ,#0000          ;
4006  00           NOP                  ;
""",
              """ORG #4000

4000  C3,00,00     JP #0000             ;

4003  C2,00,00     JP NZ,#0000          ;
4006  00           NOP                  ;
""",
              """ORG #4000

4000  C3,00,00     JP #0000             ;

4003  C2,00,00     JP NZ,#0000          ;

4006  00           NOP                  ;
""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>C3,00,00</bytes><instruction>JP #0000\
</instruction><flags>S- Z- H- PV- N- C-</flags><timeing><cycles>10</cycles>\
<tstates>4,3,3</tstates></timeing></line>
  <line><address>4003</address><bytes>C2,00,00</bytes><instruction>JP NZ,#0000\
</instruction><flags>S- Z- H- PV- N- C-</flags><timeing><cycles>10</cycles>\
<tstates>4,3,3</tstates></timeing></line>
  <line><address>4006</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
</z80code>"""]],
            # formats for numbers, address, etc
            [[0x21, 0xFF, 0x7F, 0x21, 0xFF, 0x7F, 0x21, 0xFF, 0x7F, 0x21, 0xFF,
              0x7F],
             [["Address Output Format Hex", "Number Output Format Decimal",
               "Command Output Format Octal", "101#4003#4006#",
               "202#4003#4006#", "303#4003#4006#", "102#4006#4009#",
               "203#4006#4009#", "300#4006#4009#", "103#4009#400B#",
               "200#4009#400B#", "301#4009#400B#"],
              ["XML Output On", "Address Output Format Hex",
               "Number Output Format Decimal", "Command Output Format Octal",
               "101#4003#4006#", "202#4003#4006#", "303#4003#4006#",
               "102#4006#4009#", "203#4006#4009#", "300#4006#4009#",
               "103#4009#400B#", "200#4009#400B#", "301#4009#400B#"]],
             ["""ORG #4000

4000               041,377,177           LD HL,32767           ;
16387              00100001,11111111,01111111                     \
LD HL,o077777          ;
o040006            21,FF,7F     LD HL,b0111111111111111      ;
b0100000000001001  33,255,127            LD HL,#7FFF\
                             ;
""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>041,377,177</bytes><instruction>\
LD HL,32767</instruction><flags>S- Z- H- PV- N- C-</flags><timeing><cycles>10\
</cycles><tstates>4,3,3</tstates></timeing></line>
  <line><address>16387</address><bytes>00100001,11111111,01111111</bytes>\
<instruction>LD HL,o077777</instruction><flags>S- Z- H- PV- N- C-</flags>\
<timeing><cycles>10</cycles><tstates>4,3,3</tstates></timeing></line>
  <line><address>o040006</address><bytes>21,FF,7F</bytes><instruction>\
LD HL,b0111111111111111</instruction><flags>S- Z- H- PV- N- C-</flags>\
<timeing><cycles>10</cycles><tstates>4,3,3</tstates></timeing></line>
  <line><address>b0100000000001001</address><bytes>33,255,127</bytes>\
<instruction>LD HL,#7FFF</instruction><flags>S- Z- H- PV- N- C-</flags>\
<timeing><cycles>10</cycles><tstates>4,3,3</tstates></timeing></line>
</z80code>"""]],
            # command bytes
            [[0x21, 0xFF, 0x7F],
             [["List Command Bytes On"], ["List Command Bytes Off"]],
             ["""ORG #4000\n\n4000  21,FF,7F     LD HL,#7FFF          ;\n""",
              """ORG #4000\n\n4000    LD HL,#7FFF          ;\n"""]],
            # comments on/off
            [[0x10, 0xFE],
             [["Comments On"], ["Comments Off"]],
             ["""ORG #4000\n\n4000  10,FE        DJNZ #4000           ;\n""",
              """ORG #4000\n\n4000  10,FE        DJNZ #4000         \n"""]],
            # separators
            [[0x10, 0xFE],
             [["Seperators Space"], ["Seperators Tab"], ["0E02#4000#4002##~"]],
             ["""ORG #4000\n\n4000  10,FE        DJNZ #4000           ;\n""",
              """ORG #4000\n\n4000\t10,FE\tDJNZ #4000\t;\n""",
              """ORG #4000\n\n4000~10,FE~DJNZ #4000~;\n"""]],
            # line numbering
            [[0xC3, 0x04, 0x40, 0x00, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00],
             [["Line After Jump None", "Line Numbers All"],
              ["Line After Jump None", "Line Numbers None"],
              ["Line After Jump None", "Line Numbers Referenced"],
              ["Line After Jump None", "Line Numbers None",
               "900#4000#400A##3"]],
             ["""ORG #4000

4000  C3,04,40     JP #4004             ;
4003  00           NOP                  ;
4004  18,00        JR #4006             ;
4006  00           NOP                  ;
4007  00           NOP                  ;
4008  00           NOP                  ;
4009  00           NOP                  ;
""",
              """ORG #4000

      C3,04,40     JP #4004             ;
      00           NOP                  ;
      18,00        JR #4006             ;
      00           NOP                  ;
      00           NOP                  ;
      00           NOP                  ;
      00           NOP                  ;
""",
              """ORG #4000

4000  C3,04,40     JP #4004             ;
      00           NOP                  ;
4004  18,00        JR #4006             ;
4006  00           NOP                  ;
      00           NOP                  ;
      00           NOP                  ;
      00           NOP                  ;
""",
              """ORG #4000

4000  C3,04,40     JP #4004             ;
      00           NOP                  ;
      18,00        JR #4006             ;
4006  00           NOP                  ;
      00           NOP                  ;
      00           NOP                  ;
4009  00           NOP                  ;
"""]],
            # reference data
            [[0x21, 0x03, 0x40, 0xC3, 0x06, 0x40, 0x00],
             [["Line Numbers Referenced", "Reference Data Numbers On"],
              ["Line Numbers Referenced", "Reference Data Numbers Off"]],
             ["""ORG #4000

4000  21,03,40     LD HL,#4003          ;
4003  C3,06,40     JP #4006             ;

4006  00           NOP                  ;
""",
              """ORG #4000

4000  21,03,40     LD HL,#4003          ;
      C3,06,40     JP #4006             ;

4006  00           NOP                  ;
"""]],
            # comment
            [[0x00, 0x00, 0x00],
             [["30000#4001#4002##End of Line"],
              ["30000#4001#4002##End of Line\nEnd of Line2"],
              ["30001#4001#4002##Before Line"],
              ["30001#4001#4002##Before Line\nBefore Line2"],
              ["30002#4001#4002##After Line"],
              ["30002#4001#4002##After Line\nAfter Line2"],
              ["XML Output On", "30000#4001#4002##End of Line"],
              ["XML Output On", "30000#4001#4002##End of Line\nEnd of Line2"],
              ["XML Output On", "30001#4001#4002##Before Line"],
              ["XML Output On", "30001#4001#4002##Before Line\nBefore Line2"],
              ["XML Output On", "30002#4001#4002##After Line"],
              ["XML Output On", "30002#4001#4002##After Line\nAfter Line2"]],
             ["""\
ORG #4000

4000  00           NOP                  ;
4001  00           NOP                  ;End of Line
4002  00           NOP                  ;
""",
              """\
ORG #4000

4000  00           NOP                  ;
4001  00           NOP                  ;End of Line
    ;End of Line2
4002  00           NOP                  ;
""",
              """\
ORG #4000

4000  00           NOP                  ;
    ;Before Line
4001  00           NOP                  ;
4002  00           NOP                  ;
""",
              """\
ORG #4000

4000  00           NOP                  ;
    ;Before Line
    ;Before Line2
4001  00           NOP                  ;
4002  00           NOP                  ;
""",
              """\
ORG #4000

4000  00           NOP                  ;
4001  00           NOP                  ;
    ;After Line
4002  00           NOP                  ;
""",
              """\
ORG #4000

4000  00           NOP                  ;
4001  00           NOP                  ;
    ;After Line
    ;After Line2
4002  00           NOP                  ;
""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
  <line><address>4001</address><bytes>00</bytes><instruction>NOP</instruction>\
<comment>End of Line</comment><flags>S- Z- H- PV- N- C-</flags><timeing>\
<cycles>4</cycles><tstates>4</tstates></timeing></line>
  <line><address>4002</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
</z80code>""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
  <line><address>4001</address><bytes>00</bytes><instruction>NOP</instruction>\
<comment>End of Line
End of Line2</comment><flags>S- Z- H- PV- N- C-</flags><timeing>\
<cycles>4</cycles><tstates>4</tstates></timeing></line>
  <line><address>4002</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
</z80code>""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
  <line><comment>Before Line</comment></line>
  <line><address>4001</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
  <line><address>4002</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
</z80code>""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
  <line><comment>Before Line
Before Line2</comment></line>
  <line><address>4001</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
  <line><address>4002</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
</z80code>""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
  <line><address>4001</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
  <line><comment>After Line</comment></line>
  <line><address>4002</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
</z80code>""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
  <line><address>4001</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
  <line><comment>After Line
After Line2</comment></line>
  <line><address>4002</address><bytes>00</bytes><instruction>NOP</instruction>\
<flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles><tstates>4\
</tstates></timeing></line>
</z80code>"""]],
            # find and comment
            [[0x21, 0x03, 0x40, 0xCD, 0xC2, 0x04, 0x00],
             [[spectrumtranslate.DisassembleInstruction(
                 "Comment Pattern", 0x4000, 0x4004,
                 spectrumtranslate.createfindandcomment("""\
  %X0200%V0F0001     %#var0 is position of code to check +1
  %?EQ%MWV0004C2     %#do the second two bytes point to save routine?
  %?BA               %#and
  %(                 %#now ensure first byte is a call command
    %?EQ%MV0F00CD    %#does the first byte equal 0xCD (code for call)
    %?BO             %#or
    %(               %#check if is conditional call command
      %X0700%V0F00C7 %#var0 is code to check and 0xC7 (mask bits that change)
      %?EQ%V0000C0   %#masked value should be 0xC0 for a conditional call
    %)
  %)""", spectrumtranslate.stringtoinstructiontext("Save IX,DE bytes"), 3, 0))
               ]],
             ["""ORG #4000

4000  21,03,40     LD HL,#4003          ;
4003  CD,C2,04     CALL #04C2           ;Save IX,DE bytes
4006  00           NOP                  ;
"""]]
        ]

        for data, instructions, outputs in tests:
            for instruction, output in zip(instructions, outputs):
                si = [spectrumtranslate.DisassembleInstruction(i) for i in
                      instruction]
                self.assertEqual(spectrumtranslate.disassemble(data, 0, 0x4000,
                                 len(data), si), output)

        # data block
        data = [0x41, 0x42, 0x43, 0x00, 0x30, 0x31, 0x32, 0x00]
        di = [spectrumtranslate.DisassembleInstruction("Data Block")]
        di[0].data = spectrumtranslate.DisassembleInstruction.\
            DISASSEMBLE_DATABLOCK_CODES["Define Message zero terminated"]
        self.assertEqual(spectrumtranslate.disassemble(data, 0, 0x4000,
                         len(data), di), """ORG #4000

4000    DM0  "ABC",#00
4004    DM0  "012",#00

""")
        # line after data
        di += [spectrumtranslate.DisassembleInstruction(
            "Empty Line After Data On")]
        self.assertEqual(spectrumtranslate.disassemble(data, 0, 0x4000,
                         len(data), di), """ORG #4000

4000    DM0  "ABC",#00
4004    DM0  "012",#00

""")
        di[1] = spectrumtranslate.DisassembleInstruction(
            "Empty Line After Data Off")
        self.assertEqual(spectrumtranslate.disassemble(data, 0, 0x4000,
                         len(data), di), """ORG #4000

4000    DM0  "ABC",#00
4004    DM0  "012",#00
""")
        # pattern block
        data = [0x7F, 0xEF, 0x00, 0x00, 0x38, 0xC9]
        di = [spectrumtranslate.DisassembleInstruction("Pattern Data Block")]
        di[0].data = spectrumtranslate.DisassembleInstruction.\
            DISASSEMBLE_PATTERNBLOCK_CODES["RST#28 (Calculator)"]
        self.assertEqual(spectrumtranslate.disassemble(data, 0, 0x4000,
                         len(data), di), """ORG #4000

4000  7F           LD A,A               ;
4001  EF           RST 28H              ;
    DEFB  #00
    DEFB  #00
    DEFB  #38

4005  C9           RET                  ;

""")


class TestSpectrumTranslateError(unittest.TestCase):
    def test_SpectrumTranslateError(self):
        # test create
        e = spectrumtranslate.SpectrumTranslateError("Test")
        self.assertEqual("Test", e.value)

# todo test command line

if __name__ == "__main__":
    unittest.main()
