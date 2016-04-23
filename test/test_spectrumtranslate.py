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

"""
Unit Test for SpectrumTranslate file
"""

import unittest
import subprocess
import re
import sys
import os
from PIL import Image
from sys import hexversion as _PYTHON_VERSION_HEX
from codecs import unicode_escape_decode as _UED
from io import BytesIO
from os import remove as os_remove
# import modules from parent directory
pathtemp = sys.path
sys.path += [os.path.dirname(os.getcwd())]
import spectrumtranslate
import spectrumnumber
# restore system path
sys.path = pathtemp

if(_PYTHON_VERSION_HEX > 0x03000000):
    from io import StringIO

    def _u(x):
        return x

    def _getfile(name):
        with open(name, 'r') as f:
            return f.read()

else:
    # 2to3 will complain but won't cause problems in real life
    from StringIO import StringIO

    def _u(x):
        return _UED(x)[0]

    def _getfile(name):
        with open(name, 'r') as f:
            return f.read().decode('utf8')


def _getfileasbytearray(name):
    with open(name, 'rb') as infile:
        return bytearray(infile.read())


class Testbasicconversion(unittest.TestCase):
    def test_basictotext(self):
        data = _getfileasbytearray("basictest.dat")
        self.assertEqual(spectrumtranslate.basictotext(data), _u("""\
10 REM ^16^00^00\u259C^11^05\u2597^11^03hello123^11^01^10^05^11^06
15 PRINT ^10^00^11^07"80"
20 DATA 1(number without value),2(1024),3,4: LIST : NEW \n\


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

        self.assertEqual(spectrumtranslate.basictotext(data,
                                                       hexfornonascii=True),
                         """\
10 REM ^16^00^00^87^11^05^84^11^03hello123^11^01^10^05^11^06
15 PRINT ^10^00^11^07"80"
20 DATA 1(number without value),2(1024),3,4: LIST : NEW \n\


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
""")

    def test_basictoxml(self):
        data = _getfileasbytearray("basictest.dat")
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

        self.assertEqual(spectrumtranslate.basictoxml(data,
                                                      hexfornonascii=True),
                         _u("""\
<?xml version="1.0" encoding="UTF-8" ?>
<basiclisting>
  <line>
    <linenumber>10</linenumber>
    <instruction>
      <keyword>REM</keyword>
      <argument>^16^00^00^87^11^05^84^11^03hello123^11^01^10^05^11^06</argument>
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
        data = _getfileasbytearray("arraytest_number.dat")
        self.assertEqual(spectrumtranslate.getarraydepth(data, 0x98), 2)
        data = _getfileasbytearray("arraytest_char.dat")
        self.assertEqual(spectrumtranslate.getarraydepth(data, 0xD3), 3)

    def test_extractarray(self):
        data = _getfileasbytearray("arraytest_number.dat")
        data = spectrumtranslate.extractarray(data, 0x98)
        correctvalues = [[round(x * y * 0.1, 2) for y in range(1, 11)] for x
                         in range(1, 21)]

        # convert spectrumnumbers to floats
        data = [[float(x) for x in row] for row in data]
        # now compare
        self.assertEqual(data, correctvalues)

        data = _getfileasbytearray("arraytest_char.dat")
        self.assertEqual(spectrumtranslate.extractarray(data, 0xD3),
                         [['test', 'mum ', 'good'], ['one ', 'two ', 'thre']])

    def test_arraytotext(self):
        data = _getfileasbytearray("arraytest_number.dat")
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

        data = _getfileasbytearray("arraytest_char.dat")
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

        data = [2, 2, 0, 1, 0, 0xFF, 0x7F]
        self.assertEqual(spectrumtranslate.arraytotext(data, 0xD3), _u("""{
  "COPY ",
  "\u00A9"
}"""))

        self.assertEqual(spectrumtranslate.arraytotext(data, 0xD3, True),
                         _u("""{
  "^FF",
  "^7F"
}"""))

    def test_arraytoxml(self):
        data = _getfileasbytearray("arraytest_number.dat")
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

        data = _getfileasbytearray("arraytest_char.dat")
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

        data = [2, 2, 0, 1, 0, 0xFF, 0x7F]
        self.assertEqual(spectrumtranslate.arraytoxml(data, 0xD3), _u("""\
<dimension>
  <string>COPY </string>
  <string>\u00A9</string>
</dimension>"""))

        self.assertEqual(spectrumtranslate.arraytoxml(data, 0xD3, True),
                         _u("""\
<dimension>
  <string>^FF</string>
  <string>^7F</string>
</dimension>"""))


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
        self.assertEqual(error.value, 'Data Format error processing \
"<code here>" after character 6 on line 0, starting at address 4000\nTest')


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
    spectrumchars2 = ("^00", "^01", "^02", "^03", "^04", "^05", "^06", "^07",
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
                      "X", "Y", "Z", "[", "\\", "]", "^5E", "_",
                      "^60", "a", "b", "c", "d", "e", "f", "g",
                      "h", "i", "j", "k", "l", "m", "n", "o",
                      "p", "q", "r", "s", "t", "u", "v", "w",
                      "x", "y", "z", "{", "|", "}", "~", "^7F",
                      '^80', '^81', '^82', '^83', '^84', '^85', '^86', '^87',
                      "^88", "^89", "^8A", "^8B", "^8C", "^8D", "^8E", "^8F",
                      "^90", "^91", "^92", "^93", "^94", "^95", "^96", "^97",
                      "^98", "^99", "^9A", "^9B", "^9C", "^9D", "^9E", "^9F",
                      "^A0", "^A1", "^A2", "^A3", "^A4", "^A5", "^A6", "^A7",
                      "^A8", "^A9", "^AA", "^AB", "^AC", "^AD", "^AE", "^AF",
                      "^B0", "^B1", "^B2", "^B3", "^B4", "^B5", "^B6", "^B7",
                      "^B8", "^B9", "^BA", "^BB", "^BC", "^BD", "^BE", "^BF",
                      "^C0", "^C1", "^C2", "^C3", "^C4", "^C5", "^C6", "^C7",
                      "^C8", "^C9", "^CA", "^CB", "^CC", "^CD", "^CE", "^CF",
                      "^D0", "^D1", "^D2", "^D3", "^D4", "^D5", "^D6", "^D7",
                      "^D8", "^D9", "^DA", "^DB", "^DC", "^DD", "^DE", "^DF",
                      "^E0", "^E1", "^E2", "^E3", "^E4", "^E5", "^E6", "^E7",
                      "^E8", "^E9", "^EA", "^EB", "^EC", "^ED", "^EE", "^EF",
                      "^F0", "^F1", "^F2", "^F3", "^F4", "^F5", "^F6", "^F7",
                      "^F8", "^F9", "^FA", "^FB", "^FC", "^FD", "^FE", "^FF")

    def test_getspectrumchar(self):
        for code, character in enumerate(self.spectrumchars):
            self.assertEqual(spectrumtranslate.getspectrumchar(code),
                             character)

        for code, character in enumerate(self.spectrumchars2):
            self.assertEqual(spectrumtranslate.getspectrumchar(code, True),
                             character)

    def test_getspectrumstring(self):
        self.assertEqual(
            spectrumtranslate.getspectrumstring([x for x in range(256)]),
            ''.join(self.spectrumchars))

        self.assertEqual(
            spectrumtranslate.getspectrumstring([x for x in range(256)], True),
            ''.join(self.spectrumchars2))

    def test_chartospectrum(self):
        for code, character in enumerate(self.spectrumchars):
            self.assertEqual(spectrumtranslate.chartospectrum(character),
                             chr(code))

    def test_stringtospectrum(self):
        self.assertEqual(
            spectrumtranslate.stringtospectrum(''.join(self.spectrumchars)),
            ''.join([chr(x) for x in range(256)]))


class TestImageConvert(unittest.TestCase):
    def imageto32bitlist(self, im):
        return [(xy[0] << 16) + (xy[1] << 8) + xy[2] for xy in
                im.convert("RGB").getdata()]

    def test_getgiffromscreen(self):
        # get reference images
        irReference = Image.open("screentest.gif")
        refimage1 = self.imageto32bitlist(irReference)
        irReference.seek(1)
        refimage2 = self.imageto32bitlist(irReference)

        # get image created by spectrumtranslate
        gifscreen = spectrumtranslate.getgiffromscreen(
            _getfileasbytearray("screentest.dat"))
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

        # test getting individual images
        # get image created by spectrumtranslate
        gifscreen = spectrumtranslate.getgiffromscreen(
            _getfileasbytearray("screentest.dat"), -1)
        # should have valid gif now
        gifimage = Image.open(BytesIO(gifscreen))
        # compare images now
        self.assertEqual(refimage1, self.imageto32bitlist(gifimage))

        # test flash image
        gifscreen = spectrumtranslate.getgiffromscreen(
            _getfileasbytearray("screentest.dat"), -2)
        # should have valid gif now
        gifimage = Image.open(BytesIO(gifscreen))
        # compare images now
        self.assertEqual(refimage2, self.imageto32bitlist(gifimage))

    def test_getrgbfromscreen(self):
        # get reference images
        irReference = Image.open("screentest.gif")
        refimage1 = self.imageto32bitlist(irReference)
        irReference.seek(1)
        refimage2 = self.imageto32bitlist(irReference)

        gifscreen = spectrumtranslate.getrgbfromscreen(
            _getfileasbytearray("screentest.dat"), alphamask=0)
        # should have valid list of RGB values
        # should be 2 images
        self.assertEqual(type(gifscreen), list)
        self.assertEqual(len(gifscreen), 2)
        self.assertEqual(type(gifscreen[0]), list)
        self.assertEqual(len(gifscreen[0]), 256 * 192)
        self.assertEqual(type(gifscreen[1]), list)
        self.assertEqual(len(gifscreen[1]), 256 * 192)
        # compare images now
        self.assertEqual(refimage1, gifscreen[0])
        self.assertEqual(refimage2, gifscreen[1])

        # test ignore RBG list
        gifscreen = spectrumtranslate.getrgbfromscreen(
            _getfileasbytearray("screentest.dat"), imageformat=1)
        # should be 2 images
        self.assertEqual(type(gifscreen), list)
        self.assertEqual(len(gifscreen), 2)
        self.assertEqual(type(gifscreen[0]), list)
        self.assertEqual(len(gifscreen[0]), 256 * 192)
        self.assertEqual(type(gifscreen[0][0]), list)
        self.assertEqual(len(gifscreen[0][0]), 4)
        self.assertEqual(type(gifscreen[1]), list)
        self.assertEqual(len(gifscreen[1]), 256 * 192)
        self.assertEqual(type(gifscreen[1][0]), list)
        self.assertEqual(len(gifscreen[1][0]), 4)
        # compare images now
        irReference.seek(0)
        refimage1 = [list(x) for x in irReference.convert("RGBA").getdata()]
        irReference.seek(1)
        refimage2 = [list(x) for x in irReference.convert("RGBA").getdata()]
        self.assertEqual(refimage1, gifscreen[0])
        self.assertEqual(refimage2, gifscreen[1])

        # test ignore RBG list without alpha
        gifscreen = spectrumtranslate.getrgbfromscreen(
            _getfileasbytearray("screentest.dat"), imageformat=1, alphamask=-1)
        # should be 2 images
        self.assertEqual(type(gifscreen), list)
        self.assertEqual(len(gifscreen), 2)
        self.assertEqual(type(gifscreen[0]), list)
        self.assertEqual(len(gifscreen[0]), 256 * 192)
        self.assertEqual(type(gifscreen[0][0]), list)
        self.assertEqual(len(gifscreen[0][0]), 3)
        self.assertEqual(type(gifscreen[1]), list)
        self.assertEqual(len(gifscreen[1]), 256 * 192)
        self.assertEqual(type(gifscreen[1][0]), list)
        self.assertEqual(len(gifscreen[1][0]), 3)
        # compare images now
        irReference.seek(0)
        refimage1 = [list(x) for x in irReference.convert("RGB").getdata()]
        irReference.seek(1)
        refimage2 = [list(x) for x in irReference.convert("RGB").getdata()]
        self.assertEqual(refimage1, gifscreen[0])
        self.assertEqual(refimage2, gifscreen[1])


class TestSnapConvert(unittest.TestCase):
    # todo : test snap files once I have snap files to test
    def test_snaptosna(self):
        pass

    def test_snaptoz80(self):
        pass


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
                    "XMLOutput": 0,
                    "HexForNonASCII": 0}

        data = (65, 66, 67, 127, 22, 0, 0, 49, 50)

        position, text = di.disassembledatablock(Settings, data)

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
                    "XMLOutput": 0,
                    "HexForNonASCII": 0}
        Vars = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x4000, 0, 0, 0x4000, 0x4001]

        # check tests
        instructions = "%( %?EQ%V00%V00 %?BO %?NE%V00%V00 Hello %)"
        self.assertEqual(spectrumtranslate._processcommandblock(instructions,
                                                                Vars,
                                                                Settings,
                                                                None,
                                                                False,
                                                                True),
                         (1, ''))

        instructions = "%( %?EQ%V00%V00 %?BA %?NE%V00%V00 Hello %)"
        Settings["DATASTRINGPOS"] = 0
        self.assertEqual(spectrumtranslate._processcommandblock(instructions,
                                                                Vars,
                                                                Settings,
                                                                None,
                                                                False,
                                                                True),
                         (0, 'Hello'))

        instructions = "%( %?EQ%V00%V00 %?BX %?NE%V00%V00 Hello %)"
        Settings["DATASTRINGPOS"] = 0
        self.assertEqual(spectrumtranslate._processcommandblock(instructions,
                                                                Vars,
                                                                Settings,
                                                                None,
                                                                False,
                                                                True),
                         (1, 'Hello'))

        # test ReferencedLineNumbers
        instructions = "%W80"
        Settings["DATASTRINGPOS"] = 0
        Settings["ReferencedLineNumbers"] = []
        self.assertEqual(spectrumtranslate._processcommandblock(instructions,
                         Vars, Settings, None, False, True), (0, '0000'))
        self.assertEqual(len(Settings["ReferencedLineNumbers"]), 1)
        self.assertEqual(Settings["ReferencedLineNumbers"][0], 0)

        # test break and continue
        instructions = "%Y Hello"
        Settings["DATASTRINGPOS"] = 0
        self.assertEqual(spectrumtranslate._processcommandblock(instructions,
                                                                Vars,
                                                                Settings,
                                                                None,
                                                                False,
                                                                True),
                         (2, ''))
        self.assertEqual(Settings["DATASTRINGPOS"], 2)

        instructions = "%Z Hello"
        Settings["DATASTRINGPOS"] = 0
        self.assertEqual(spectrumtranslate._processcommandblock(instructions,
                                                                Vars,
                                                                Settings,
                                                                None,
                                                                False,
                                                                True),
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
                "XML Output On"],
            spectrumtranslate.DisassembleInstruction.DISASSEMBLE_CODES[
                "Hex instead of non-ASCII On"]),
            'FA078E4~')

    def test_get_custom_format_values(self):
        self.assertEqual(
            spectrumtranslate.get_custom_format_values('FA078E4~', True),
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
             'HexForNonASCII': spectrumtranslate.DisassembleInstruction.
             DISASSEMBLE_CODES["Hex instead of non-ASCII On"],
             'ListEveryXLines': 7})

        self.assertEqual(
            spectrumtranslate.get_custom_format_values('FA078E4~'),
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
             'HexForNonASCII': 1,
             'ListEveryXLines': 7})

    def test_get_comment_reference_string(self):
        self.assertEqual(spectrumtranslate.get_comment_reference_string(
            0x1234, 0x0F, "Test"), "1234FTest")

    def test_get_comment_reference_values(self):
        self.assertEqual(spectrumtranslate.get_comment_reference_values(
            "1234FTest"), (0x1234, 0x0F, "Test"))

    def test_get_comment_displacement_string(self):
        self.assertEqual(spectrumtranslate.get_comment_displacement_string(
            0x12, 0x03, "Test"), "123Test")

    def test_get_comment_displacement_values(self):
        self.assertEqual(spectrumtranslate.get_comment_displacement_values(
            "123Test"), (0x12, 0x03, "Test"))

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

  %X0200%V0F0003     %#var0 is position of code to check + length of command
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

4000  DD,CB,01,01  LD C,RLC (IX+#01)
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

4000  DD           \n\
4001  00           NOP
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

4000  7E           LD A,(HL)
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

4000  CB,47        BIT 0,A
4002  87           ADD A,A
4003  A7           AND A
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

4000  C3,00,00     JP #0000
4003  C2,00,00     JP NZ,#0000
4006  00           NOP
""",
              """ORG #4000

4000  C3,00,00     JP #0000

4003  C2,00,00     JP NZ,#0000
4006  00           NOP
""",
              """ORG #4000

4000  C3,00,00     JP #0000

4003  C2,00,00     JP NZ,#0000

4006  00           NOP
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

4000               041,377,177           LD HL,32767
16387              00100001,11111111,01111111                     LD HL,o077777
o040006            21,FF,7F     LD HL,b0111111111111111
b0100000000001001  33,255,127            LD HL,#7FFF
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
             ["""ORG #4000\n\n4000  21,FF,7F     LD HL,#7FFF\n""",
              """ORG #4000\n\n4000    LD HL,#7FFF\n"""]],
            # comments on/off
            [[0x10, 0xFE],
             [["Comments On", "Display Flags On"],
              ["Comments Off", "Display Flags On"]],
             ["""ORG #4000\n\n4000  10,FE        DJNZ #4000           \
;S- Z- H- PV- N- C-\n""",
              """ORG #4000\n\n4000  10,FE        DJNZ #4000\n"""]],
            # separators
            [[0x10, 0xFE],
             [["Seperators Space"], ["Seperators Tab"], ["0E02#4000#4002##~"]],
             ["""ORG #4000\n\n4000  10,FE        DJNZ #4000\n""",
              """ORG #4000\n\n4000\t10,FE\tDJNZ #4000\n""",
              """ORG #4000\n\n4000~10,FE~DJNZ #4000\n"""]],
            # line numbering
            [[0xC3, 0x04, 0x40, 0x00, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00],
             [["Line After Jump None", "Line Numbers All"],
              ["Line After Jump None", "Line Numbers None"],
              ["Line After Jump None", "Line Numbers Referenced"],
              ["Line After Jump None", "Line Numbers None",
               "900#4000#400A##3"]],
             ["""ORG #4000

4000  C3,04,40     JP #4004
4003  00           NOP
4004  18,00        JR #4006
4006  00           NOP
4007  00           NOP
4008  00           NOP
4009  00           NOP
""",
              """ORG #4000

      C3,04,40     JP #4004
      00           NOP
      18,00        JR #4006
      00           NOP
      00           NOP
      00           NOP
      00           NOP
""",
              """ORG #4000

4000  C3,04,40     JP #4004
      00           NOP
4004  18,00        JR #4006
4006  00           NOP
      00           NOP
      00           NOP
      00           NOP
""",
              """ORG #4000

4000  C3,04,40     JP #4004
      00           NOP
      18,00        JR #4006
4006  00           NOP
      00           NOP
      00           NOP
4009  00           NOP
"""]],
            # reference data
            [[0x21, 0x03, 0x40, 0xC3, 0x06, 0x40, 0x00],
             [["Line Numbers Referenced", "Reference Data Numbers On"],
              ["Line Numbers Referenced", "Reference Data Numbers Off"]],
             ["""ORG #4000

4000  21,03,40     LD HL,#4003
4003  C3,06,40     JP #4006

4006  00           NOP
""",
              """ORG #4000

4000  21,03,40     LD HL,#4003
      C3,06,40     JP #4006

4006  00           NOP
"""]],
            # comment
            [[0x00, 0x00, 0x00],
             [["30000#4001#4002##End of Line"],
              ["30000#4001#4002##End of Line", "30000#4001#4002##Another End"],
              ["30000#4001#4002##End of Line\nEnd of Line2"],
              ["30001#4001#4002##Before Line"],
              ["30001#4001#4002##Before 1", "30001#4001#4002##Before 2"],
              ["30001#4001#4002##Before Line\nBefore Line2"],
              ["30002#4001#4002##After Line"],
              ["30002#4001#4002##After Line", "30002#4001#4002##After again"],
              ["30002#4001#4002##After Line\nAfter Line2"],
              ["XML Output On", "30000#4001#4002##End of Line"],
              ["XML Output On", "30000#4001#4002##End of Line\nEnd of Line2"],
              ["XML Output On", "30001#4001#4002##Before Line"],
              ["XML Output On", "30001#4001#4002##Before Line\nBefore Line2"],
              ["XML Output On", "30002#4001#4002##After Line"],
              ["XML Output On", "30002#4001#4002##After Line\nAfter Line2"]],
             ["""\
ORG #4000

4000  00           NOP
4001  00           NOP                  ;End of Line
4002  00           NOP
""",
              """\
ORG #4000

4000  00           NOP
4001  00           NOP                  ;End of Line. Another End
4002  00           NOP
""",
              """\
ORG #4000

4000  00           NOP
4001  00           NOP                  ;End of Line
      ;End of Line2
4002  00           NOP
""",
              """\
ORG #4000

4000  00           NOP
      ;Before Line
4001  00           NOP
4002  00           NOP
""",
              """\
ORG #4000

4000  00           NOP
      ;Before 1
      ;Before 2
4001  00           NOP
4002  00           NOP
""",
              """\
ORG #4000

4000  00           NOP
      ;Before Line
      ;Before Line2
4001  00           NOP
4002  00           NOP
""",
              """\
ORG #4000

4000  00           NOP
4001  00           NOP
      ;After Line
4002  00           NOP
""",
              """\
ORG #4000

4000  00           NOP
4001  00           NOP
      ;After Line
      ;After again
4002  00           NOP
""",
              """\
ORG #4000

4000  00           NOP
4001  00           NOP
      ;After Line
      ;After Line2
4002  00           NOP
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
            # comment in data
            [[0x01, 0x23, 0x45],
             [["30000#4001#4002##End of Line",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["30000#4001#4002##End of Line", "30000#4001#4002##Another End",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["30000#4001#4002##End of Line\nEnd of Line2",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["30001#4001#4002##Before Line",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["30001#4001#4002##Before 1", "30001#4001#4002##Before 2",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["30001#4001#4002##Before Line\nBefore Line2",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["30002#4001#4002##After Line",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["30002#4001#4002##After Line", "30002#4001#4002##After again",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["30002#4001#4002##After Line\nAfter Line2",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["XML Output On", "30000#4001#4002##End of Line",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["XML Output On", "30000#4001#4002##End of Line\nEnd of Line2",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["XML Output On", "30001#4001#4002##Before Line",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["XML Output On", "30001#4001#4002##Before Line\nBefore Line2",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["XML Output On", "30002#4001#4002##After Line",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""],
              ["XML Output On", "30002#4001#4002##After Line\nAfter Line2",
               """10000#4000#4006##%$A%F0004%ACA%$-A%S%S%$IDB%$-I%S%$D%F0000\
%F0100#%B0F%$-D"""]],
             ["""\
ORG #4000

4000    DB  #01
4001    DB  #23  ;End of Line
4002    DB  #45

""",
              """\
ORG #4000

4000    DB  #01
4001    DB  #23  ;End of Line. Another End
4002    DB  #45

""",
              """\
ORG #4000

4000    DB  #01
4001    DB  #23  ;End of Line
  ;End of Line2
4002    DB  #45

""",
              """\
ORG #4000

4000    DB  #01
  ;Before Line
4001    DB  #23
4002    DB  #45

""",
              """\
ORG #4000

4000    DB  #01
  ;Before 1
  ;Before 2
4001    DB  #23
4002    DB  #45

""",
              """\
ORG #4000

4000    DB  #01
  ;Before Line
  ;Before Line2
4001    DB  #23
4002    DB  #45

""",
              """\
ORG #4000

4000    DB  #01
4001    DB  #23
  ;After Line
4002    DB  #45

""",
              """\
ORG #4000

4000    DB  #01
4001    DB  #23
  ;After Line
  ;After again
4002    DB  #45

""",
              """\
ORG #4000

4000    DB  #01
4001    DB  #23
  ;After Line
  ;After Line2
4002    DB  #45

""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DB</instruction><data>#01</data>\
</line>
  <line><address>4001</address><instruction>DB</instruction><data>#23</data>\
<comment>End of Line</comment></line>
  <line><address>4002</address><instruction>DB</instruction><data>#45</data>\
</line>

</z80code>""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DB</instruction><data>#01</data>\
</line>
  <line><address>4001</address><instruction>DB</instruction><data>#23</data>\
<comment>End of Line\nEnd of Line2</comment></line>
  <line><address>4002</address><instruction>DB</instruction><data>#45</data>\
</line>

</z80code>""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DB</instruction><data>#01</data>\
</line>
  <line><comment>Before Line</comment></line>
  <line><address>4001</address><instruction>DB</instruction><data>#23</data>\
</line>
  <line><address>4002</address><instruction>DB</instruction><data>#45</data>\
</line>

</z80code>""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DB</instruction><data>#01</data>\
</line>
  <line><comment>Before Line\nBefore Line2</comment></line>
  <line><address>4001</address><instruction>DB</instruction><data>#23</data>\
</line>
  <line><address>4002</address><instruction>DB</instruction><data>#45</data>\
</line>

</z80code>""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DB</instruction><data>#01</data>\
</line>
  <line><address>4001</address><instruction>DB</instruction><data>#23</data>\
</line>
  <line><comment>After Line</comment></line>
  <line><address>4002</address><instruction>DB</instruction><data>#45</data>\
</line>

</z80code>""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DB</instruction><data>#01</data>\
</line>
  <line><address>4001</address><instruction>DB</instruction><data>#23</data>\
</line>
  <line><comment>After Line\nAfter Line2</comment></line>
  <line><address>4002</address><instruction>DB</instruction><data>#45</data>\
</line>

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

4000  21,03,40     LD HL,#4003
4003  CD,C2,04     CALL #04C2           ;Save IX,DE bytes
4006  00           NOP
"""]],
            # Hex instead of non-ASCII On/Off
            [[0xFF, 0x41, 0x7F],
             [["Hex instead of non-ASCII Off",
               """10000#4000#4002##%F0004%ACA%S%SDM%S%X01000000%L%(%?LE%V\
0F%V0E%)%(%I%(%(%?EQ%V000001%?BA%(%?LT%MV0F0020%?BO%(%?MT%MV0F007F%?BA%?LT%MV0\
F00A3%)%)%)%?BO%(%?EQ%V000000%?BA%(%?MT%MV0F00A2%?BO%(%?MT%MV0F001F%?BA%?LT%MV\
0F0080%)%)%)%)%("%X03000001%V00%)%C0F%)%I%(%?EQ%V000001%)%("%)"""],
              ["Hex instead of non-ASCII On",
               """10000#4000#4002##%F0004%ACA%S%SDM%S%X01000000%L%(%?LE%V\
0F%V0E%)%(%I%(%(%?EQ%V000001%?BA%(%?LT%MV0F0020%?BO%(%?MT%MV0F007F%?BA%?LT%MV0\
F00A3%)%)%)%?BO%(%?EQ%V000000%?BA%(%?MT%MV0F00A2%?BO%(%?MT%MV0F001F%?BA%?LT%MV\
0F0080%)%)%)%)%("%X03000001%V00%)%C0F%)%I%(%?EQ%V000001%)%("%)"""]],
             [_u("""ORG #4000

4000    DM  "COPY A\u00A9"

"""),
              """ORG #4000

4000    DM  "^FFA^7F"

"""]],
            # test comment reference
            [[0x21, 0x00, 0x40, 0xCD, 0x00, 0x40, 0xC2, 0x00, 0x40, 0x3A, 0x00,
              0x40],
             [[spectrumtranslate.DisassembleInstruction(
                 "Comment Reference", 0x4000, 0x400B,
                 spectrumtranslate.get_comment_reference_string(
                     0x4000, 0x0F, "Test"))],
              [spectrumtranslate.DisassembleInstruction(
                 "Comment Reference", 0x4000, 0x400B,
                 spectrumtranslate.get_comment_reference_string(
                     0x4000, 0x01, "Test"))],
              [spectrumtranslate.DisassembleInstruction(
                 "Comment Reference", 0x4000, 0x400B,
                 spectrumtranslate.get_comment_reference_string(
                     0x4000, 0x02, "Test"))],
              [spectrumtranslate.DisassembleInstruction(
                 "Comment Reference", 0x4000, 0x400B,
                 spectrumtranslate.get_comment_reference_string(
                     0x4000, 0x04, "Test"))],
              [spectrumtranslate.DisassembleInstruction(
                 "Comment Reference", 0x4000, 0x400B,
                 spectrumtranslate.get_comment_reference_string(
                     0x4000, 0x08, "Test"))],
              [spectrumtranslate.DisassembleInstruction(
                 "Comment Reference", 0x4000, 0x4005,
                 spectrumtranslate.get_comment_reference_string(
                     0x4000, 0x0F, "Test"))],
              [spectrumtranslate.DisassembleInstruction(
                 "Comment Reference Before", 0x4000, 0x400B,
                 spectrumtranslate.get_comment_reference_string(
                     0x4000, 0x0F, "Test"))],
              [spectrumtranslate.DisassembleInstruction(
                 "Comment Reference After", 0x4000, 0x400B,
                 spectrumtranslate.get_comment_reference_string(
                     0x4000, 0x0F, "Test"))]],
             ["""ORG #4000

4000  21,00,40     LD HL,#4000          ;Test
4003  CD,00,40     CALL #4000           ;Test
4006  C2,00,40     JP NZ,#4000          ;Test
4009  3A,00,40     LD A,(#4000)         ;Test
""",
              """ORG #4000

4000  21,00,40     LD HL,#4000
4003  CD,00,40     CALL #4000
4006  C2,00,40     JP NZ,#4000
4009  3A,00,40     LD A,(#4000)         ;Test
""",
              """ORG #4000

4000  21,00,40     LD HL,#4000          ;Test
4003  CD,00,40     CALL #4000
4006  C2,00,40     JP NZ,#4000
4009  3A,00,40     LD A,(#4000)
""",
              """ORG #4000

4000  21,00,40     LD HL,#4000
4003  CD,00,40     CALL #4000           ;Test
4006  C2,00,40     JP NZ,#4000
4009  3A,00,40     LD A,(#4000)
""",
              """ORG #4000

4000  21,00,40     LD HL,#4000
4003  CD,00,40     CALL #4000
4006  C2,00,40     JP NZ,#4000          ;Test
4009  3A,00,40     LD A,(#4000)
""",
              """ORG #4000

4000  21,00,40     LD HL,#4000          ;Test
4003  CD,00,40     CALL #4000           ;Test
4006  C2,00,40     JP NZ,#4000
4009  3A,00,40     LD A,(#4000)
""",
              """ORG #4000

      ;Test
4000  21,00,40     LD HL,#4000
      ;Test
4003  CD,00,40     CALL #4000
      ;Test
4006  C2,00,40     JP NZ,#4000
      ;Test
4009  3A,00,40     LD A,(#4000)
""",
              """ORG #4000

4000  21,00,40     LD HL,#4000
      ;Test
4003  CD,00,40     CALL #4000
      ;Test
4006  C2,00,40     JP NZ,#4000
      ;Test
4009  3A,00,40     LD A,(#4000)
      ;Test
"""]],
            # test comment Displacement
            [[0xDD, 0x7E, 0x04, 0xFD, 0x77, 0x04, 0xDD, 0x77, 0x00],
             [[spectrumtranslate.DisassembleInstruction(
                 "Comment Displacement", 0x4000, 0x4008,
                 spectrumtranslate.get_comment_displacement_string(
                     0x04, 3, "Test"))],
              [spectrumtranslate.DisassembleInstruction(
                 "Comment Displacement", 0x4000, 0x4008,
                 spectrumtranslate.get_comment_displacement_string(
                     0x04, 1, "Test"))],
              [spectrumtranslate.DisassembleInstruction(
                 "Comment Displacement", 0x4000, 0x4008,
                 spectrumtranslate.get_comment_displacement_string(
                     0x04, 2, "Test"))],
              [spectrumtranslate.DisassembleInstruction(
                 "Comment Displacement", 0x4000, 0x4002,
                 spectrumtranslate.get_comment_displacement_string(
                     0x04, 3, "Test"))],
              [spectrumtranslate.DisassembleInstruction(
                 "Comment Displacement Before", 0x4000, 0x4008,
                 spectrumtranslate.get_comment_displacement_string(
                     0x04, 3, "Test"))],
              [spectrumtranslate.DisassembleInstruction(
                 "Comment Displacement After", 0x4000, 0x4008,
                 spectrumtranslate.get_comment_displacement_string(
                     0x04, 3, "Test"))]],
             ["""ORG #4000

4000  DD,7E,04     LD A,(IX+#04)        ;Test
4003  FD,77,04     LD (IY+#04),A        ;Test
4006  DD,77,00     LD (IX+#00),A
""",
              """ORG #4000

4000  DD,7E,04     LD A,(IX+#04)        ;Test
4003  FD,77,04     LD (IY+#04),A
4006  DD,77,00     LD (IX+#00),A
""",
              """ORG #4000

4000  DD,7E,04     LD A,(IX+#04)
4003  FD,77,04     LD (IY+#04),A        ;Test
4006  DD,77,00     LD (IX+#00),A
""",
              """ORG #4000

4000  DD,7E,04     LD A,(IX+#04)        ;Test
4003  FD,77,04     LD (IY+#04),A
4006  DD,77,00     LD (IX+#00),A
""",
              """ORG #4000

      ;Test
4000  DD,7E,04     LD A,(IX+#04)
      ;Test
4003  FD,77,04     LD (IY+#04),A
4006  DD,77,00     LD (IX+#00),A
""",
              """ORG #4000

4000  DD,7E,04     LD A,(IX+#04)
      ;Test
4003  FD,77,04     LD (IY+#04),A
      ;Test
4006  DD,77,00     LD (IX+#00),A
"""]],
            # test comment Displacement part 2
            [[0xDD, 0x7E, 0x04, 0xFD, 0x77, 0x04, 0xDD, 0x77, 0x04],
             [["30200#4000#4008##043A", "30200#4003#4005##043B"]],
             ["""ORG #4000

4000  DD,7E,04     LD A,(IX+#04)        ;A
4003  FD,77,04     LD (IY+#04),A        ;B
4006  DD,77,04     LD (IX+#04),A        ;A
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
        # force line after off with formatting
        di[0].data = "%F0502" + di[0].data
        self.assertEqual(spectrumtranslate.disassemble(data, 0, 0x4000,
                         len(data), di), """ORG #4000

4000    DM0  "ABC",#00
4004    DM0  "012",#00
""")
        # default no line after
        di[0].data = spectrumtranslate.DisassembleInstruction.\
            DISASSEMBLE_DATABLOCK_CODES["Define Message zero terminated"]
        di[1] = spectrumtranslate.DisassembleInstruction(
            "Empty Line After Data Off")
        self.assertEqual(spectrumtranslate.disassemble(data, 0, 0x4000,
                         len(data), di), """ORG #4000

4000    DM0  "ABC",#00
4004    DM0  "012",#00
""")
        # force line after with formatting
        di[0].data = "%F0501" + di[0].data
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

4000  7F           LD A,A
4001  EF           RST 28H
    DEFB  #00
    DEFB  #00
    DEFB  #38

4005  C9           RET

""")

    def test_predefined(self):
        def testfunction(data, Settings, Vars, txt=None, val=None, mode=0):
            if(mode == 1):
                if(Vars[0] == 4):
                    return 2
                return 0
            if(mode == 2):
                if(Vars[0] == 4):
                    return 4
                return 0
            if(val and not txt):
                return val
            if(txt and not val):
                return txt
            return val, txt

        spectrumtranslate.DisassembleInstruction.PredefinedFunctions["Test"] =\
            testfunction

        tests = [
            # define bytes
            [[0, 1, 2, 3, 4, 5, 6, 7, 8, 0xDD, 0x0A, 0x7F],
             [["10000#4000#4009##%PDefineByte()",
               "30000#4001#4002##End",
               "30001#4001#4002##Before",
               "30002#4001#4002##After"],
              ["10000#4000#4009##%PDefineByte()", "XML Output On",
               "30000#4001#4002##End",
               "30001#4001#4002##Before",
               "30002#4001#4002##After"],
              ["10000#4000#400B##%PDefineByte(Signed=True, Format=1)"],
              ["10000#4000#400B##%PDefineByte(Format=2, MaxPerLine=3)"],
              ["10000#4000#400D##%PDefineByte(Format=3, MaxPerLine = 5)"],
              ["10000#4000#400B##%PDefineByte(GapFrequency=2, Gap=' ', \
MaxPerLine=6,FormatIdentifyer=False)"]],
             ["""ORG #4000

4000    DB  #00
      ;Before
4001    DB  #01  ;End
      ;After
4002    DB  #02
4003    DB  #03
4004    DB  #04
4005    DB  #05
4006    DB  #06
4007    DB  #07
4008    DB  #08
4009    DB  #DD

400A  0A           LD A,(BC)
400B  7F           LD A,A
""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DB</instruction><data>#00</data>\
</line>
  <line><comment>Before</comment></line>
  <line><address>4001</address><instruction>DB</instruction><data>#01</data>\
<comment>End</comment></line>
  <line><comment>After</comment></line>
  <line><address>4002</address><instruction>DB</instruction><data>#02</data>\
</line>
  <line><address>4003</address><instruction>DB</instruction><data>#03</data>\
</line>
  <line><address>4004</address><instruction>DB</instruction><data>#04</data>\
</line>
  <line><address>4005</address><instruction>DB</instruction><data>#05</data>\
</line>
  <line><address>4006</address><instruction>DB</instruction><data>#06</data>\
</line>
  <line><address>4007</address><instruction>DB</instruction><data>#07</data>\
</line>
  <line><address>4008</address><instruction>DB</instruction><data>#08</data>\
</line>
  <line><address>4009</address><instruction>DB</instruction><data>#DD</data>\
</line>

  <line><address>400A</address><bytes>0A</bytes><instruction>LD A,(BC)\
</instruction><flags>S- Z- H- PV- N- C-</flags><timeing><cycles>7</cycles>\
<tstates>4,3</tstates></timeing></line>
  <line><address>400B</address><bytes>7F</bytes><instruction>LD A,A\
</instruction><flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles>\
<tstates>4</tstates></timeing></line>\n</z80code>""",
              """ORG #4000

4000    SB  0
4001    SB  1
4002    SB  2
4003    SB  3
4004    SB  4
4005    SB  5
4006    SB  6
4007    SB  7
4008    SB  8
4009    SB  -35
400A    SB  10
400B    SB  127

""",
              """ORG #4000

4000    DB  o000,o001,o002
4003    DB  o003,o004,o005
4006    DB  o006,o007,o010
4009    DB  o335,o012,o177

""",
              """ORG #4000

4000    DB  b00000000,b00000001,b00000010,b00000011,b00000100
4005    DB  b00000101,b00000110,b00000111,b00001000,b11011101
400A    DB  b00001010,b01111111

""",
              """ORG #4000

4000    DB  0001 0203 0405
4006    DB  0607 08DD 0A7F

"""]],
            # define word
            [[0, 1, 2, 3, 4, 5, 6, 7, 8, 0xDD, 0x0A, 0x7F],
             [["10000#4000#4008##%PDefineWord()",
               "30000#4001#4002##End",
               "30001#4001#4002##Before",
               "30002#4001#4002##After"],
              ["10000#4000#4009##%PDefineWord()", "XML Output On",
               "30000#4001#4002##End",
               "30001#4001#4002##Before",
               "30002#4001#4002##After"],
              ["10000#4000#400B##%PDefineWord(Signed=True, Format=1)"],
              ["10000#4000#400B##%PDefineWord(Format=2, MaxPerLine=5)"],
              ["10000#4000#400D##%PDefineWord(Format=3, MaxPerLine = 3)"],
              ["10000#4000#400B##%PDefineWord(GapFrequency=2, Gap=' ', \
MaxPerLine=6,FormatIdentifyer=False, LittleEndian=False)"]],
             ["""ORG #4000

4000    DW  #0100
      ;Before
4002    DW  #0302  ;End
      ;After
4004    DW  #0504
4006    DW  #0706
4008    DW  #DD08

400A  0A           LD A,(BC)
400B  7F           LD A,A
""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DW</instruction><data>#0100</data>\
</line>
  <line><comment>Before</comment></line>
  <line><address>4002</address><instruction>DW</instruction><data>#0302</data>\
<comment>End</comment></line>
  <line><comment>After</comment></line>
  <line><address>4004</address><instruction>DW</instruction><data>#0504</data>\
</line>
  <line><address>4006</address><instruction>DW</instruction><data>#0706</data>\
</line>
  <line><address>4008</address><instruction>DW</instruction><data>#DD08</data>\
</line>

  <line><address>400A</address><bytes>0A</bytes><instruction>LD A,(BC)\
</instruction><flags>S- Z- H- PV- N- C-</flags><timeing><cycles>7</cycles>\
<tstates>4,3</tstates></timeing></line>
  <line><address>400B</address><bytes>7F</bytes><instruction>LD A,A\
</instruction><flags>S- Z- H- PV- N- C-</flags><timeing><cycles>4</cycles>\
<tstates>4</tstates></timeing></line>
</z80code>""",
              """ORG #4000

4000    SW  256
4002    SW  770
4004    SW  1284
4006    SW  1798
4008    SW  -8952
400A    SW  32522

""",
              """ORG #4000

4000    DW  o000400,o001402,o002404,o003406,o156410
400A    DW  o077412

""",
              """ORG #4000

4000    DW  b0000000100000000,b0000001100000010,b0000010100000100
4006    DW  b0000011100000110,b1101110100001000,b0111111100001010

""",
              """ORG #4000

4000    DWBE  00010203 04050607 08DD0A7F

"""]],
            # define message
            [[200, 16, 65] + [ord(x) for x in "BC\nLine 2"] + [0],
             [["10000#4000#400B##%PDefineMessage()"],
              ["10000#4000#400D##%PDefineMessage()", "XML Output On"],
              ["10000#4000#400B##%PDefineMessage(Noncharoutofquotes=True)"],
              ["Hex instead of non-ASCII On",
               "10000#4000#400B##%PDefineMessage(Noncharoutofquotes=True)"]],
             ["""ORG #4000

4000    DM  ">= ^10^41BC^0ALine 2"

400C  00           NOP
""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DM</instruction><data>\
">= ^10^41BC^0ALine 2^00"</data></line>

</z80code>""",
              """ORG #4000

4000    DM  ">= ",0x10,0x41,"BC",0x0A,"Line 2"

400C  00           NOP
""",
              """ORG #4000

4000    DM  0xC8,0x10,0x41,"BC",0x0A,"Line 2"

400C  00           NOP
"""]],
            # define message zero terminated
            [[200] + [ord(x) for x in "Test\nLine2"] + [0, 16, 0, 65, 0, 0, 1],
             [["10000#4000#4011##%PDefineMessage(DataType='DM0')"],
              ["10000#4000#4012##%PDefineMessage(DataType='0')",
               "XML Output On"],
              ["10000#4000#400D##%PDefineMessage(Noncharoutofquotes=True,\
DataType='DM0')"]],
             ["""ORG #4000

4000    DM0  ">= Test^0ALine2^00"
400C    DM0  "^10^00A^00"
4010    DM0  "^00"
4011    DM0  "^01"

""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DM0</instruction><data>\
">= Test^0ALine2^00"</data></line>
  <line><address>400C</address><instruction>DM0</instruction><data>\
"^10^00A^00"</data></line>
  <line><address>4010</address><instruction>DM0</instruction><data>\
"^00"</data></line>
  <line><address>4011</address><instruction>DM0</instruction><data>\
"^01"</data></line>

</z80code>""",
              """ORG #4000

4000    DM0  ">= Test",0x0A,"Line2",0x00
400C    DM0  0x10,0x00,"A",0x00

4010  00           NOP
4011    DB  #01

"""]],
            # define message bit7 terminated
            [[ord(x) for x in "Test\nLine2"] + [128, 16, 128, 65, 128, 128, 1],
             [["10000#4000#4010##%PDefineMessage(DataType='DM7')"],
              ["10000#4000#4012##%PDefineMessage(DataType='7')",
               "XML Output On"],
              ["10000#4000#400D##%PDefineMessage(Noncharoutofquotes=True,\
DataType='DM7')"]],
             ["""ORG #4000

4000    DM7  "Test^0ALine2^80"
400B    DM7  "^10^80A^80"
400F    DM7  "^80"
4010    DM7  "^01"

""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DM7</instruction><data>\
"Test^0ALine2^80"</data></line>
  <line><address>400B</address><instruction>DM7</instruction><data>\
"^10^80A^80"</data></line>
  <line><address>400F</address><instruction>DM7</instruction><data>"^80"\
</data></line>
  <line><address>4010</address><instruction>DM7</instruction><data>"^01"\
</data></line>

</z80code>""",
              """ORG #4000

4000    DM7  "Test",0x0A,"Line2",0x80
400B    DM7  0x10,0x80,"A",0x80

400F  80           ADD A,B
4010    DB  #01

"""]],
            # define message length byte
            [[10] + [ord(x) for x in "Test\nLine2"] + [3, 16, 65, 65],
             [["10000#4000#400C##%PDefineMessage(DataType='DMLB')"],
              ["10000#4000#400F##%PDefineMessage(DataType='LB')",
               "XML Output On"],
              ["10000#4000#4004##%PDefineMessage(Noncharoutofquotes=True,\
DataType='LB')"]],
             ["""ORG #4000

4000    DMLB  "Test^0ALine2"
400B    DMLB  "^10^41A"

""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DMLB</instruction><data>\
"Test^0ALine2"</data></line>
  <line><address>400B</address><instruction>DMLB</instruction><data>\
"^10^41A"</data></line>

</z80code>""",
              """ORG #4000

4000    DMLB  "Test",0x0A,"Line2"

400B  03           INC BC
400C  10,41        DJNZ #404F
400E  41           LD B,C
"""]],
            # define message length word
            [[10, 0] + [ord(x) for x in "Test\nLine2"] + [3, 0, 16, 65, 65],
             [["10000#4000#400C##%PDefineMessage(DataType='DMLW')"],
              ["10000#4000#400F##%PDefineMessage(DataType='LW')",
               "XML Output On"],
              ["10000#4000#4004##%PDefineMessage(Noncharoutofquotes=True,\
DataType='LW')"]],
             ["""ORG #4000

4000    DMLW  "Test^0ALine2"
400C    DMLW  "^10^41A"

""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DMLW</instruction><data>\
"Test^0ALine2"</data></line>
  <line><address>400C</address><instruction>DMLW</instruction><data>\
"^10^41A"</data></line>

</z80code>""",
              """ORG #4000

4000    DMLW  "Test",0x0A,"Line2"

400C  03           INC BC
400D  00           NOP
400E  10,41        DJNZ #4051
4010  41           LD B,C
"""]],
            # define message length word big endian
            [[0, 10] + [ord(x) for x in "Test\nLine2"] + [0, 3, 16, 65, 65],
             [["10000#4000#400C##%PDefineMessage(DataType='DMLWBE')"],
              ["10000#4000#400F##%PDefineMessage(DataType='LWBE')",
               "XML Output On"],
              ["10000#4000#4004##%PDefineMessage(Noncharoutofquotes=True,\
DataType='BE')"]],
             ["""ORG #4000

4000    DMLWBE  "Test^0ALine2"
400C    DMLWBE  "^10^41A"

""",
              """<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#4000</org>
  <line><address>4000</address><instruction>DMLWBE</instruction><data>\
"Test^0ALine2"</data></line>
  <line><address>400C</address><instruction>DMLWBE</instruction><data>\
"^10^41A"</data></line>

</z80code>""",
              """ORG #4000

4000    DMLWBE  "Test",0x0A,"Line2"

400C  00           NOP
400D  03           INC BC
400E  10,41        DJNZ #4051
4010  41           LD B,C
"""]],
            # predefied find & start end
            [[0x21, 0x44, 0x80, 0xCD, 0x44, 0x80, 0xC2, 0x44, 0x80],
             [["20000#4000#4008#0,3,1F,2A,2D,66,69,70,85#%(  %!FindPattern\
(0x44, 0x80)%) %#hello%(  %!StartandEndbyOffset(startoffset = -1,\
 endoffset = 1)%)%F0502From:%WCA% To:%WCE%Q"]],
             ["""ORG #4000

From:4000 To:4002
4000  21,44,80     LD HL,#8044
From:4003 To:4005
4003  CD,44,80     CALL #8044
From:4006 To:4008
4006  C2,44,80     JP NZ,#8044
"""]],
            # predefined functions
            [[0],
             [["10000#4000#4000#0,20,23,2A,2D,30,33,3B,3E,41#%I%(%PTest(val=0,\
txt='Hello')%)%(  TRUE%)%J%(  FALSE%)%Q"],
              ["10000#4000#4000#0,20,23,2A,2D,30,33,3B,3E,41#%I%(%PTest(val=1,\
txt='Hello')%)%(  TRUE%)%J%(  FALSE%)%Q"],
              ["10000#4000#4000#0,20,23,2A,2D,30,33,3B,3E,41#%I%(%PTest(val=\
False, txt='A')%)%(  TRUE%)%J%(  FALSE%)%Q"],
              ["10000#4000#4000#0,20,23,2A,2D,30,33,3B,3E,41#%I%(%PTest(val=\
True, txt='B')%)%(  TRUE%)%J%(  FALSE%)%Q"],
              ["10000#4000#4000#0,B,1E,21,32,43,4E,51,54#%X01000000%L%(\
%?LT%V000005%)%(  %X0200%V000001  %PTest(mode=1)  LOOP%BC0%)%Q"],
              ["10000#4000#4000#0,B,1E,21,32,43,4E,51,54#%X01000000%L%(\
%?LT%V000005%)%(  %X0200%V000001  %PTest(mode=2)  LOOP%BC0%)%Q"]],
             ["""ORG #4000

HelloFALSE

4000  00           NOP
""",
              """ORG #4000

HelloTRUE

4000  00           NOP
""",
              """ORG #4000

AFALSE

4000  00           NOP
""",
              """ORG #4000

BTRUE

4000  00           NOP
""",
              """ORG #4000

LOOP01LOOP02LOOP03

4000  00           NOP
""",
              """ORG #4000

LOOP01LOOP02LOOP03LOOP05

4000  00           NOP
"""]]]
        for data, instructions, outputs in tests:
            for instruction, output in zip(instructions, outputs):
                si = [spectrumtranslate.DisassembleInstruction(i) for i in
                      instruction]
                self.assertEqual(spectrumtranslate.disassemble(data, 0, 0x4000,
                                 len(data), si), output)


class TestSpectrumTranslateError(unittest.TestCase):
    def test_SpectrumTranslateError(self):
        # test create
        e = spectrumtranslate.SpectrumTranslateError("Test")
        self.assertEqual("Test", e.value)


class Testformating(unittest.TestCase):
    def runpep8(self, py_file, errignore, stdoutignore):
        p = subprocess.Popen(["python",
                              "/usr/local/lib/python2.6/dist-packages/pep8.py",
                              "--repeat", py_file],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()

        output = output.splitlines()
        if(len(output) > 0 and isinstance(output[0], bytes)):
            output = [x.decode("utf-8") for x in output]
        if(stdoutignore):
            output = [x for x in output if x not in stdoutignore]

        error = error.splitlines()
        if(len(error) > 0 and isinstance(error[0], bytes)):
            error = [x.decode("utf-8") for x in error]
        if(errignore):
            error = [x for x in error if x not in errignore]

        return "\n".join(output), "\n".join(error)

    def test_pep8(self):
        output, error = self.runpep8("../spectrumtranslate.py", [], [])
        self.assertEqual(output, "", "../spectrumtranslate.py pep8 formatting \
errors:\n" + output)
        self.assertEqual(error, "", "../spectrumtranslate.py pep8 format \
check had errors:\n" + error)

        output, error = self.runpep8("test_spectrumtranslate.py", [], [
            "test_spectrumtranslate.py:62:1: E402 module level import not at \
top of file",
            "test_spectrumtranslate.py:63:1: E402 module level import not at \
top of file"])
        self.assertEqual(output, "", "test_spectrumtranslate.py pep8 \
formatting errors:\n" + output)
        self.assertEqual(error, "", "test_spectrumtranslate.py pep8 format \
check had errors:\n" + error)


class Test2_3compatibility(unittest.TestCase):
    def run2to3(self, py_file, errignore, stdoutignore):
        p = subprocess.Popen(["/usr/bin/2to3", py_file],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()

        # remove refactoring info
        output = output.splitlines()
        if(len(output) > 0 and isinstance(output[0], bytes)):
            output = [x.decode("utf-8") for x in output]
        refactorignore = ["--- " + py_file + " (original)",
                          "+++ " + py_file + " (refactored)"]
        output = "\n".join([x for x in output if x not in refactorignore])
        # split into diffs
        chunks = re.compile(
            "^(@@\s[\-\+0-9]*,[0-9]*\s[\+\-0-9]+,[0-9]+\s@@$\n)",
            re.MULTILINE).split(output)
        chunks = [x for x in chunks if len(x) > 0]
        # prepare matcher if is problem commented to ignore
        commentmatcher = re.compile("^([^\-\+].*?\n)*(\s*# 2to3 will complain \
but.*?\n)([\-\+].*?\n)*([^\-\+].*?\n?)*$")
        # filter out stuff want to ignore
        output = []
        for x in range(0, len(chunks), 2):
            if(commentmatcher.match(chunks[x + 1])):
                continue
            if(chunks[x + 1] not in stdoutignore):
                output += [chunks[x], chunks[x + 1]]

        error = error.splitlines()
        if(len(error) > 0 and isinstance(error[0], bytes)):
            error = [x.decode("utf-8") for x in error]
        if(not errignore):
            errignore = []
        errignore += [
            "AssertionError: {0} 2to3 check had errors:".format(py_file),
            "RefactoringTool: Skipping implicit fixer: buffer",
            "RefactoringTool: Skipping implicit fixer: idioms",
            "RefactoringTool: Skipping implicit fixer: set_literal",
            "RefactoringTool: Skipping implicit fixer: ws_comma",
            "RefactoringTool: Refactored {0}".format(py_file),
            "RefactoringTool: Files that need to be modified:",
            "RefactoringTool: {0}".format(py_file),
            "RefactoringTool: No changes to {0}".format(py_file)]

        error = [x for x in error if x not in errignore]

        return output, "".join(error)

    def test_2to3(self):
        output, error = self.run2to3("../spectrumtranslate.py", [], [])
        self.assertEqual(output, [], "../spectrumtranslate.py 2to3 errors:\n" +
                         "".join(output))
        self.assertEqual(error, "", "../spectrumtranslate.py 2to3 check had \
errors:\n" + error)

        output, error = self.run2to3("test_spectrumtranslate.py", [], [])
        self.assertEqual(output, [], "test_spectrumtranslate.py 2to3 errors\
:\n" + "".join(output))
        self.assertEqual(error, "", "test_spectrumtranslate.py 2to3 check had \
errors:\n" + error)


class Testcommandline(unittest.TestCase):
    class Mystdout(StringIO):
        # a class to mimic the buffer behaviour of stdout
        class bufferemulator:
            def __init__(self):
                self.bytedata = bytearray()

            def write(self, data):
                self.bytedata += data

        def __init__(self):
            StringIO.__init__(self)
            self.buffer = Testcommandline.Mystdout.bufferemulator()

    class Mystdin(StringIO):
        # a class to mimic the buffer behaviour of stdout
        class bufferemulator:
            def __init__(self):
                self.bytedata = bytearray()

            def read(self):
                return self.bytedata

        def __init__(self, data, avoidbuffer):
            StringIO.__init__(self)
            self.buffer = Testcommandline.Mystdin.bufferemulator()
            if(sys.hexversion > 0x03000000):
                if(isinstance(data, bytearray)):
                    self.buffer.bytedata = data
                elif(avoidbuffer):
                    self.write(data)
                    self.seek(0)
                else:
                    self.buffer.bytedata = bytearray([ord(x) for x in data])
            else:
                self.write(data)
                self.seek(0)

    def runtest(self, command, stdindata, wantbytearrayreturned=False,
                avoidbuffer=False):
        saved_output = sys.stdout
        saved_input = sys.stdin
        sys.stdin = Testcommandline.Mystdin(stdindata, avoidbuffer)
        output = Testcommandline.Mystdout()
        sys.stdout = output
        try:
            spectrumtranslate._commandline(["x.py"] + command.split())

        finally:
            sys.stdout = saved_output
            sys.stdin = saved_input

        out = output.getvalue()
        if(sys.hexversion < 0x03000000 and not wantbytearrayreturned):
            out = out.decode('utf8')
        if(len(out) == 0 and len(output.buffer.bytedata) > 0):
            out = output.buffer.bytedata
        output.close()
        return out

    def setUp(self):
        # tidy up
        try:
            os_remove("temp.txt")
        except:
            pass

        try:
            os_remove("temp.gif")
        except:
            pass

        try:
            os_remove("temp.bin")
        except:
            pass

    def test_help(self):
        self.assertEqual(self.runtest("", ""), spectrumtranslate.usage())
        self.assertEqual(self.runtest("help", ""), spectrumtranslate.usage())

    def test_basic(self):
        self.assertEqual(self.runtest("basic basictest.dat temp.txt", ""), "")
        self.assertEqual(_getfile("temp.txt"), _u("""\
10 REM ^16^00^00\u259c^11^05\u2597^11^03hello123^11^01^10^05^11^06
15 PRINT ^10^00^11^07"80"
20 DATA 1(number without value),2(1024),3,4: LIST : NEW \n\


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
        self.assertEqual(self.runtest("basic -o -a basictest.dat", ""), _u("""\
10 REM ^16^00^00^87^11^05^84^11^03hello123^11^01^10^05^11^06
15 PRINT ^10^00^11^07"80"
20 DATA 1(number without value),2(1024),3,4: LIST : NEW \n\


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
        self.assertEqual(self.runtest("basic -o -s 10 basictest.dat", ""),
                         _u("""\
Autostart at line:10
10 REM ^16^00^00\u259c^11^05\u2597^11^03hello123^11^01^10^05^11^06
15 PRINT ^10^00^11^07"80"
20 DATA 1(number without value),2(1024),3,4: LIST : NEW \n\


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
        self.assertEqual(self.runtest("basic -o --xml basictest.dat", ""),
                         _u("""\
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
        self.assertEqual(self.runtest("basic -o --xml -s 10 basictest.dat",
                                      ""), _u("""\
<?xml version="1.0" encoding="UTF-8" ?>
<basiclisting>
  <autostart>10</autostart>
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

        # tidy up
        os_remove("temp.txt")

    def test_text(self):
        def _listtostring(b):
            return bytearray(b).decode('latin-1')

        self.assertEqual(self.runtest("text -i -o",
                                      '\x7F\x60\x5E\x01\x41\x80\xFF'),
                         _u('\xA9\xA3\u2191^01A\u2003COPY '))
        self.assertEqual(self.runtest("text -i temp.txt", _listtostring(
            [0x7F, 0x60, 0x5E, 0x01, 0x41, 0x80, 0xFF])), "")
        self.assertEqual(_getfile("temp.txt"),
                         _u('\xA9\xA3\u2191^01A\u2003COPY '))
        self.assertEqual(self.runtest("text -i -o -a", _listtostring(
            [0x7F, 0x60, 0x5E, 0x01, 0x41, 0x80, 0xFF])),
                         _u('^7F^60^5E^01A^80^FF'))
        self.assertEqual(self.runtest("text -o -a -k 0x1F -l 4 \
arraytest_char.tap", ""), 'test')

        # tidy up
        os_remove("temp.txt")

    def test_array(self):
        self.assertEqual(self.runtest("array -t 0x98 arraytest_number.dat \
temp.txt", ""), "")
        self.assertEqual(_getfile("temp.txt"), spectrumtranslate.arraytotext(
            _getfileasbytearray("arraytest_number.dat"), 0x98))

        self.assertEqual(self.runtest("array -t 0x98 -xml \
arraytest_number.dat temp.txt", ""), "")
        self.assertEqual(_getfile("temp.txt"), spectrumtranslate.arraytoxml(
            _getfileasbytearray("arraytest_number.dat"), 0x98))

        self.assertEqual(self.runtest("array -t 0x98 -d -o \
arraytest_number.dat ", ""), "2")

        self.assertEqual(self.runtest("array -t 0xC0 -i -o",
                                      "\x02\x02\x00\x01\x00\xFF\x7F"),
                         _u("""{
  "COPY ",
  "\u00A9"
}"""))

        self.assertEqual(self.runtest("array -t 0xC0 -i -o -a",
                                      "\x02\x02\x00\x01\x00\xFF\x7F"),
                         _u("""{
  "^FF",
  "^7F"
}"""))

        self.assertEqual(self.runtest("array -t 0xC0 -i -x temp.txt",
                                      "\x02\x02\x00\x01\x00\xFF\x7F"), "")
        self.assertEqual(_getfile("temp.txt"), _u("""\
<dimension>
  <string>COPY </string>
  <string>\u00A9</string>
</dimension>"""))

        self.assertEqual(self.runtest("array -t 0xC0 -i -o -a -x",
                                      "\x02\x02\x00\x01\x00\xFF\x7F"),
                         """\
<dimension>
  <string>^FF</string>
  <string>^7F</string>
</dimension>""")

        # tidy up
        os_remove("temp.txt")

    def test_screen(self):
        def imageto32bitlist(im):
            return [(xy[0] << 16) + (xy[1] << 8) + xy[2] for xy in
                    im.convert("RGB").getdata()]

        def imagetobytearray(im):
            return bytearray([x[i] for x in im.convert("RGB").getdata() for i
                              in (0, 1, 2)])

        self.assertEqual(self.runtest("screen -g -o screentest.dat", "", True),
                         _getfileasbytearray("screentest.gif"),
                         "Screen test Failed 1.")

        self.assertEqual(self.runtest("screen -g -f -1 screentest.dat \
temp.gif", ""), "")
        irReference = Image.open("screentest.gif")
        refimage = imageto32bitlist(irReference)
        irTemp = Image.open("temp.gif")
        tempimg = imageto32bitlist(irTemp)
        self.assertEqual(refimage, tempimg, "Screen test Failed 2.")
        # ensure only 1 image
        self.assertRaises(EOFError, irTemp.seek, 2)

        irReference.seek(1)
        self.assertEqual(self.runtest("screen -g -f -2 screentest.dat \
temp.gif", ""), "")
        refimage1 = imageto32bitlist(irReference)
        irTemp = Image.open("temp.gif")
        tempimg = imageto32bitlist(irTemp)
        self.assertEqual(refimage1, tempimg, "Screen test Failed 3.")
        # ensure only 1 image
        self.assertRaises(EOFError, irTemp.seek, 2)

        irReference.seek(0)
        self.assertEqual(self.runtest("screen -o -f -1 screentest.dat", "",
                                      True), imagetobytearray(irReference),
                         "Screen test Failed 4.")

        self.assertEqual(self.runtest("screen -f -2 screentest.dat temp.bin",
                                      ""), "")
        irReference.seek(1)
        refimage = imagetobytearray(irReference)
        self.assertEqual(refimage, _getfileasbytearray("temp.bin"),
                         "Screen test Failed 5.")

        # tidy up
        os_remove("temp.gif")
        os_remove("temp.bin")

    def test_code(self):
        self.assertEqual(self.runtest("code -i -o",
                                      "\x21\x12\x34"),
                         """ORG #0000

0000  21,12,34     LD HL,#3412
""")

        self.assertEqual(self.runtest("code -i -o -base 0x4000",
                                      "\x21\x12\x34"),
                         """ORG #4000

4000  21,12,34     LD HL,#3412
""")

        self.assertEqual(self.runtest("code -i -o -b 32768",
                                      "\x21\x12\x34"),
                         """ORG #8000

8000  21,12,34     LD HL,#3412
""")

        self.assertEqual(self.runtest("code -i -o --xml",
                                      "\x21\x12\x34"),
                         """\
<?xml version="1.0" encoding="UTF-8" ?>
<z80code>
  <org>#0000</org>
  <line><address>0000</address><bytes>21,12,34</bytes><instruction>LD HL,#3412\
</instruction><flags>S- Z- H- PV- N- C-</flags><timeing><cycles>10</cycles>\
<tstates>4,3,3</tstates></timeing></line>
</z80code>""")

        self.assertEqual(self.runtest("code -b 16384 -c f instructions.txt \
code.dat temp.txt", ""), "")
        self.assertEqual(_getfile("temp.txt"), """ORG #4000

4000  21,03,40     LD HL,16387
4003  C3,06,40     JP #4006
4006  00           NOP
""")

        # tidy up
        os_remove("temp.txt")

    def test_instruction(self):
        self.assertEqual(self.runtest("instruction -i -o", "0100#0000#FFFF##",
                                      avoidbuffer=True), "100#0#FFFF#")
        self.assertEqual(self.runtest("instruction -i -o -mo",
                                      "0100#0000#FFFF##", avoidbuffer=True),
                         "100\n0\nFFFF\n")
        self.assertEqual(self.runtest("instruction -i -o -n",
                                      "0100#0000#FFFF##", avoidbuffer=True),
                         "100#0#FFFF#")
        self.assertEqual(self.runtest("instruction -i -o -mo -n",
                                      "0100#0000#FFFF##", avoidbuffer=True),
                         "Address Output Format Hex\n0\nFFFF\n")
        self.assertEqual(self.runtest("instruction -i -o -mi",
                                      "Address Output Format Hex\n0\n0xFFFF",
                                      avoidbuffer=True), "100#0#FFFF#")
        self.assertEqual(self.runtest("instruction -i -o -mi",
                                      "256\n0\n65535", avoidbuffer=True),
                         "100#0#FFFF#")
        self.assertEqual(self.runtest("instruction -i -o -m",
                                      "Address Output Format Hex\n0\n0xFFFF",
                                      avoidbuffer=True), "100\n0\nFFFF\n")
        self.assertEqual(self.runtest("instruction -i -o -mi",
                                      "512\n0\n65535\nHello\nTest",
                                      avoidbuffer=True),
                         "200#0#FFFF#5#HelloTest")
        self.assertEqual(self.runtest("instruction -i -o -mo",
                                      "200#0#FFFF#5#HelloTest",
                                      avoidbuffer=True),
                         "200\n0\nFFFF\nHello\nTest")

    def checkinvalidcommand(self, command, message):
        try:
            spectrumtranslate._commandline(["x.py"] + command.split())
            self.fail("No SpectrumTranslateError raised")
        except spectrumtranslate.SpectrumTranslateError as se:
            if(se.value == message):
                return
            self.fail("Wrong exception message. Got:\n{0}\nExpected:\n{1}".
                      format(se.value, message))

    def test_invalidcommands(self):
        # incorrect command
        self.checkinvalidcommand("hello in out", 'No translateing mode \
(basic, code, screen, array, text, or instruction) specified.')
        # multiple actions
        self.checkinvalidcommand("basic array in out", "Can't have multiple \
formats to convert into.")
        # no input or output files
        self.checkinvalidcommand("basic", 'No input file specified.')
        self.checkinvalidcommand("basic in", 'No output file specified.')
        # unknown argument
        self.checkinvalidcommand("code hello in out",
                                 '"hello" is unrecognised argument.')
        # invalid start
        self.checkinvalidcommand("basic -s x",
                                 "Missing or invalid autostart line number.")
        # invalid variable offset
        self.checkinvalidcommand("basic -v x",
                                 "Missing or invalid offset to variables.")
        # check array specifyer
        self.checkinvalidcommand("array -t x",
                                 "Missing or invalid array description.")
        self.checkinvalidcommand("array -t 1", "Invalid array description. \
Must have integer with bits 6 and 7 as 64, 128, or 192, or be number, \
character, or string.")
        self.checkinvalidcommand("array in out", "Missing array type.")
        # flash rate check
        self.checkinvalidcommand("screen -f x",
                                 "Missing or invalid image flash rate.")
        # code origin check
        self.checkinvalidcommand("code -b x",
                                 "Missing or invalid base code address.")
        # instructions check
        self.checkinvalidcommand("code -c x", "Missing or invalid input \
source descriptor for special instructions.")
        self.checkinvalidcommand("code -c f",
                                 "Missing or invalid commands information.")
        self.checkinvalidcommand("code -i -o -c f x.txt",
                                 'Failed to read instructions from "x.txt".')
        # skip check
        self.checkinvalidcommand("code -k x",
                                 "Missing or invalid number of bytes to skip.")
        self.checkinvalidcommand("code -k 200 -o code.dat",
                                 'Invalid skip value.')
        # len check
        self.checkinvalidcommand("code --len x",
                                 "Missing or invalid bytes length number.")
        self.checkinvalidcommand("code -l 200 -o code.dat",
                                 'Invalid length value.')


if __name__ == "__main__":
    unittest.main()
