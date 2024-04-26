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
# Date: 15th April 2024

"""
Unit Test for spectrumtape file
"""

import subprocess
import unittest
import sys
import os
import pycodestyle
from io import StringIO
# import modules from parent directory
import addparentmodules
import spectrumtape
import spectrumtranslate


# change to current directory in case being run from elsewhere
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def _getfile(name):
    with open(name, 'r') as f:
        return f.read()


def _getfileasbytes(name):
    with open(name, 'rb') as infile:
        return bytearray(infile.read())


class Testutilityfunctions(unittest.TestCase):
    def test_bytesarevalid(self):
        self.assertTrue(spectrumtape._bytesarevalid(bytes(b"Test")))
        self.assertTrue(spectrumtape._bytesarevalid(bytearray(b"Test")))
        self.assertTrue(spectrumtape._bytesarevalid([1, 2]))
        self.assertTrue(spectrumtape._bytesarevalid((1, 2)))

        self.assertFalse(spectrumtape._bytesarevalid("Wrong"))
        self.assertFalse(spectrumtape._bytesarevalid([1, 'X']))
        self.assertFalse(spectrumtape._bytesarevalid((1, 'X')))

    def test_sourceisvalid(self):
        self.assertTrue(spectrumtape._sourceisvalid(bytes(b"Test")))
        self.assertTrue(spectrumtape._sourceisvalid(bytearray(b"Test")))
        self.assertTrue(spectrumtape._sourceisvalid([1, 2]))
        self.assertTrue(spectrumtape._sourceisvalid((1, 2)))
        with open("basictest.tap", 'rb') as f:
            self.assertTrue(spectrumtape._sourceisvalid(f))

    def test_validateandpreparebytes_validate(self):
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtape._validateandpreparebytes,
                          "Wrong", "test")

        self.assertTrue(spectrumtape._validateandpreparebytes(bytes(b"Test")))
        self.assertTrue(spectrumtape._validateandpreparebytes(
            bytearray(b"Test")))
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtape._validateandpreparebytes, 1, "X")
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtape._validateandpreparebytes,
                          ["Wrong", "input"], "X")
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtape._validateandpreparebytes,
                          [0.1, 0.2], "X")
        self.assertTrue(spectrumtape._validateandpreparebytes([1, 2]))

    def test_validateandpreparebytes_prepare(self):
        self.assertEqual(spectrumtape._validateandpreparebytes([1, 2]),
                         bytearray([1, 2]))
        self.assertEqual(spectrumtape._validateandpreparebytes(bytearray(
                         b"Test")), bytearray([84, 101, 115, 116]))
        self.assertEqual(spectrumtape._validateandpreparebytes(bytes(
                         b"Test")), bytearray([84, 101, 115, 116]))

    def test_get_word(self):
        self.assertEqual(spectrumtape._get_word([1, 2, 3]), 0x030201)

    def test_validateandconvertfilename(self):
        self.assertEqual(spectrumtape._validateandconvertfilename(
                         [65, 66, 67]), bytearray(b'ABC       '))
        self.assertEqual(spectrumtape._validateandconvertfilename(
                         "ABC"), bytearray(b'ABC       '))
        self.assertEqual(spectrumtape._validateandconvertfilename(
                         ["A", "B", "C"]), bytearray(b'ABC       '))
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtape._validateandconvertfilename,
                          [0.1, 0.2])
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtape._validateandconvertfilename,
                          0.1)


class TestSpectrumTapBlock(unittest.TestCase):
    def test_create(self):
        stb = spectrumtape.SpectrumTapBlock()
        self.assertEqual(stb.data, bytearray([]))
        self.assertEqual(stb.flag, 0)
        self.assertEqual(stb.filePosition, 0)

        stb = spectrumtape.SpectrumTapBlock(flag=255, data=[1, 2])
        self.assertEqual(stb.data, bytearray([1, 2]))
        self.assertEqual(stb.flag, 255)
        self.assertEqual(stb.filePosition, 0)

        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtape.SpectrumTapBlock,
                          flag="hello")

    def test_isheader(self):
        stb = spectrumtape.SpectrumTapBlock(data=[0]*17)
        self.assertTrue(stb.isheader())
        stb.flag = 255
        self.assertFalse(stb.isheader())
        stb.flag = 0
        stb.data = bytearray([1])
        self.assertFalse(stb.isheader())

    def test_getfilename(self):
        stb = spectrumtape.SpectrumTapBlock()
        self.assertEqual(stb.getfilename(), None)
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getfilename(), "BASIC     ")
        stb.data = bytearray([0, 254, 65, 127, 96, 32, 32, 32, 32, 32, 32, 0,
                              0, 0, 0, 0, 0])
        self.assertEqual(stb.getfilename(), 'RETURN A\xa9\xa3      ')

    def test_getrawfilename(self):
        stb = spectrumtape.SpectrumTapBlock()
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getrawfilename(), bytearray([66, 65, 83, 73, 67,
                                                          32, 32, 32, 32, 32]))
        stb.data = bytearray([0, 254, 65, 127, 96, 32, 32, 32, 32, 32, 32, 0,
                              0, 0, 0, 0, 0])
        self.assertEqual(stb.getrawfilename(), bytearray([254, 65, 127, 96, 32,
                                                          32, 32, 32, 32, 32]))

    def test_getfiletypestring(self):
        stb = spectrumtape.SpectrumTapBlock()
        self.assertEqual(stb.getfiletypestring(), None)
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getfiletypestring(), "Program")
        stb.data[0] = 1
        self.assertEqual(stb.getfiletypestring(), "Number array")
        stb.data[0] = 2
        self.assertEqual(stb.getfiletypestring(), "Character array")
        stb.data[0] = 3
        self.assertEqual(stb.getfiletypestring(), "Bytes")
        stb.data[0] = 4
        self.assertEqual(stb.getfiletypestring(), "Unknown")

    def test_getblockinfo(self):
        stb = spectrumtape.SpectrumTapBlock()
        self.assertEqual(stb.getblockinfo(), "")
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getblockinfo(), '"BASIC     " Program')
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getblockinfo(),
                         '"SCREENTEST" Bytes 16384,6912')
        stb.data = _getfileasbytes("arraytest_number.tap")[3:20]
        self.assertEqual(stb.getblockinfo(),
                         '"x         " Number array X')
        stb.data = _getfileasbytes("arraytest_char.tap")[3:20]
        self.assertEqual(stb.getblockinfo(),
                         '"c         " Character array S$')

    def test_getheaderautostartline(self):
        stb = spectrumtape.SpectrumTapBlock()
        self.assertEqual(stb.getheaderautostartline(), None)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheaderautostartline(), None)
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getheaderautostartline(), None)
        stb.data[13] = 10
        stb.data[14] = 0
        self.assertEqual(stb.getheaderautostartline(), 10)

    def test_getheadervariableoffset(self):
        stb = spectrumtape.SpectrumTapBlock()
        self.assertEqual(stb.getheadervariableoffset(), None)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheadervariableoffset(), None)
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getheadervariableoffset(), 78)

    def test_getheadercodestart(self):
        stb = spectrumtape.SpectrumTapBlock()
        self.assertEqual(stb.getheadercodestart(), None)
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getheadercodestart(), None)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheadercodestart(), 16384)

    def test_getheaderdescribeddatalength(self):
        stb = spectrumtape.SpectrumTapBlock()
        self.assertEqual(stb.getheaderdescribeddatalength(), None)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheaderdescribeddatalength(), 6912)

    def test_getheadervariableletter(self):
        stb = spectrumtape.SpectrumTapBlock()
        self.assertEqual(stb.getheadervariableletter(), None)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheadervariableletter(), None)
        stb.data = _getfileasbytes("arraytest_number.tap")[3:20]
        self.assertEqual(stb.getheadervariableletter(), "X")
        stb.data = _getfileasbytes("arraytest_char.tap")[3:20]
        self.assertEqual(stb.getheadervariableletter(), "S")

    def test_getheadervariablename(self):
        stb = spectrumtape.SpectrumTapBlock()
        self.assertEqual(stb.getheadervariablename(), None)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheadervariablename(), None)
        stb.data = _getfileasbytes("arraytest_number.tap")[3:20]
        self.assertEqual(stb.getheadervariablename(), "X")
        stb.data = _getfileasbytes("arraytest_char.tap")[3:20]
        self.assertEqual(stb.getheadervariablename(), "S$")

    def test_getheaderarraydescriptor(self):
        stb = spectrumtape.SpectrumTapBlock()
        self.assertEqual(stb.getheaderarraydescriptor(), None)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheaderarraydescriptor(), None)
        stb.data = _getfileasbytes("arraytest_number.tap")[3:20]
        self.assertEqual(stb.getheaderarraydescriptor() & 192, 128)
        stb.data = _getfileasbytes("arraytest_char.tap")[3:20]
        self.assertEqual(stb.getheaderarraydescriptor() & 192, 192)

    def test_getpayloadstartoffset(self):
        stb = spectrumtape.SpectrumTapBlock()
        self.assertEqual(stb.getpayloadstartoffset(), 3)

    def test__str__(self):
        stb = spectrumtape.SpectrumTapBlock(flag=255, data=[1, 2, 3])
        self.assertEqual(str(stb), "Tap file block. Flag:255, block length:3")

    def test_getpackagedforfile(self):
        stb = spectrumtape.SpectrumTapBlock(flag=255, data=[1, 2, 3])
        self.assertEqual(stb.getpackagedforfile(),
                         b'\x05\x00\xff\x01\x02\x03\xff')


class Testmetafunctions(unittest.TestCase):
    def test_nexttapblock(self):
        # test from file
        with open("arraytest_char.tap", "rb") as f:
            generator = spectrumtape.nexttapblock(f)
            tb = next(generator)
            self.assertEqual(tb.data, bytearray([2, 99, 32, 32, 32, 32, 32, 32,
                                                 32, 32, 32, 31, 0, 93, 211, 0,
                                                 128]))
            self.assertEqual(tb.flag, 0)
            self.assertEqual(tb.filePosition, 0)

            tb = next(generator)
            self.assertEqual(tb.data, bytearray([3, 2, 0, 3, 0, 4, 0, 116, 101,
                                                 115, 116, 109, 117, 109, 32,
                                                 103, 111, 111, 100, 111, 110,
                                                 101, 32, 116, 119, 111, 32,
                                                 116, 104, 114, 101]))
            self.assertEqual(tb.flag, 255)
            self.assertEqual(tb.filePosition, 21)

            with self.assertRaises(StopIteration):
                next(generator)

        # test from bytearray
        generator = spectrumtape.nexttapblock([5, 0, 255, 1, 2, 3, 255, 5, 0,
                                               255, 4, 5, 6, 248])
        tb = next(generator)
        self.assertEqual(tb.flag, 255)
        self.assertEqual(tb.filePosition, 0)

        # test array
        tbs = [*spectrumtape.nexttapblock([5, 0, 255, 1, 2, 3, 255, 5, 0, 255,
                                           4, 5, 6, 248])]
        self.assertEqual(len(tbs), 2)

    def test_createbasicheader(self):
        tb = spectrumtape.createbasicheader("Hello", 20, 30)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([0, 72, 101, 108, 108, 111, 32, 32,
                                             32, 32, 32, 30, 0, 0, 128, 20, 0]
                                            ))

    def test_createcodeheader(self):
        tb = spectrumtape.createcodeheader("Code", 16384, 6912)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([3, 67, 111, 100, 101, 32, 32, 32,
                                             32, 32, 32, 0, 27, 0, 64, 0, 0]))

    def test_createarrayheader(self):
        tb = spectrumtape.createarrayheader("Number", 129, 10)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([1, 78, 117, 109, 98, 101, 114, 32,
                                             32, 32, 32, 10, 0, 0, 129, 0, 0]))
        tb = spectrumtape.createarrayheader("Char", 194, 10)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([2, 67, 104, 97, 114, 32, 32, 32,
                                             32, 32, 32, 10, 0, 0, 194, 0, 0]))
        tb = spectrumtape.createarrayheader("String", 194, 10)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([2, 83, 116, 114, 105, 110, 103,
                                             32, 32, 32, 32, 10, 0, 0, 194, 0,
                                             0]))

    def test_createscreenheader(self):
        tb = spectrumtape.createscreenheader("Screen")
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([3, 83, 99, 114, 101, 101, 110, 32,
                                             32, 32, 32, 0, 27, 0, 64, 0, 0]))

    def test_createdatablock(self):
        tb = spectrumtape.createdatablock([1, 2, 3], 1)
        self.assertEqual(tb.flag, 1)
        self.assertEqual(tb.data, bytearray([1, 2, 3]))

    def test_convertblockformat(self):
        tb = spectrumtape.createscreenheader("Screen")
        tb = spectrumtape.convertblockformat(tb, "Tzx")
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.getpayload(), bytearray([3, 83, 99, 114, 101, 101,
                                                     110, 32, 32, 32, 32, 0,
                                                     27, 0, 64, 0, 0]))
        tb = spectrumtape.convertblockformat(tb, "Tap")
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([3, 83, 99, 114, 101, 101, 110, 32,
                                             32, 32, 32, 0, 27, 0, 64, 0, 0]))


class Testformating(unittest.TestCase):
    class Mystdout(StringIO):
        # a class to mimic the buffer behaviour of stdout
        class bufferemulator:
            def __init__(self):
                self.bytedata = bytearray()

            def write(self, data):
                self.bytedata += data

        def __init__(self):
            StringIO.__init__(self)
            self.buffer = Testformating.Mystdout.bufferemulator()

    def runpycodestyle(self, py_file, stdoutignore):
        saved_output = sys.stdout
        output = Testformating.Mystdout()
        sys.stdout = output
        try:
            style = pycodestyle.StyleGuide()
            result = style.check_files([py_file])

        finally:
            sys.stdout = saved_output

        output = output.getvalue()

        output = output.splitlines()
        if len(output) > 0 and isinstance(output[0], bytes):
            output = [x.decode("utf-8") for x in output]
        if stdoutignore:
            output = [x for x in output if x not in stdoutignore]

        return "\n".join(output)

    def test_pep8(self):
        output = self.runpycodestyle("../spectrumtape.py", [])
        self.assertEqual(output, "", "../spectrumtape.py pep8 formatting \
errors:\n" + output)

        output = self.runpycodestyle("test_spectrumtape.py", [])
        self.assertEqual(output, "", "test_spectrumtape.py pep8 \
formatting errors:\n" + output)


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

        def __init__(self, data):
            StringIO.__init__(self)
            self.buffer = Testcommandline.Mystdin.bufferemulator()
            if isinstance(data, bytearray):
                self.buffer.bytedata = data
            else:
                self.buffer.bytedata = bytearray([ord(x) for x in data])

    def runtest(self, command, stdindata="", wantbytearrayreturned=False):
        saved_output = sys.stdout
        saved_input = sys.stdin
        sys.stdin = Testcommandline.Mystdin(stdindata)
        output = Testcommandline.Mystdout()
        sys.stdout = output
        try:
            spectrumtape._commandline(["x.py"] + command.split())

        finally:
            sys.stdout = saved_output
            sys.stdin = saved_input

        out = output.getvalue()
        if not wantbytearrayreturned:
            out = bytearray(out, 'utf-8')
        if len(out) == 0 and len(output.buffer.bytedata) > 0:
            out = output.buffer.bytedata
        output.close()
        return out

    def setUp(self):
        # tidy up
        try:
            os.remove("temp.tap")
        except FileNotFoundError:
            pass

        try:
            os.remove("temp.txt")
        except FileNotFoundError:
            pass

        try:
            os.remove("temp.bin")
        except FileNotFoundError:
            pass

    def test_help(self):
        self.assertEqual(self.runtest(""), bytes(spectrumtape.usage(),
                                                 'utf-8'))
        self.assertEqual(self.runtest("help"), bytes(spectrumtape.usage(),
                                                     'utf-8'))

    def test_list(self):
        self.assertEqual(self.runtest("list -o basictest.tap"),
                         b"""block type                content information
   0  TAP Block            Header "BASIC     " Program
   1  TAP Block            Data   Flag:255, block length:190
""")

        self.assertEqual(self.runtest("list --details basictest.tap temp.txt"),
                         b"")
        self.assertEqual(_getfile("temp.txt"), """\
0\tTAP Block\tHeader\tBASIC     \tProgram\t190\t\t78
1\tTAP Block\tData\tFlag:255\tLength:190
""")

        self.assertEqual(self.runtest("list -od basictest.tap"), b"""\
0\tTAP Block\tHeader\tBASIC     \tProgram\t190\t\t78
1\tTAP Block\tData\tFlag:255\tLength:190
""")

        self.assertEqual(self.runtest("list -o test.tzx"), b'\
block type                content information\n\
   0  TZX Header                  \n\
   1  TZX Standard Speed   Header "SCREENTEST" Bytes 16384,6912 pause after:\
1000ms\n\
   2  TZX Turbo Speed      Data   Flag:255, block length:6912 pause after:\
1000ms\n\
   3  TZX Pure Tone               \n\
   4  TZX Pulse Sequence          \n\
   5  TZX Pure Data        Header "JPSP      " Bytes 16384,6912\n\
   6  TZX Direct Recording         pause after:500ms\n\
   7  TZX CSW Recording            pause after:2000ms\n\
   8  TZX Generalized Data         pause after:1000ms\n\
   9  TZX Pause or Stop            Pause 32ms\n\
  10  TZX Group Start              Group Name:Group Test\n\
  11  TZX Group End               \n\
  12  TZX Jump To                  Jump To block:10\n\
  13  TZX Loop Start               Repetitions:65534\n\
  14  TZX Loop End                \n\
  15  TZX Call Sequence            Calls to:[17, 14]\n\
  16  TZX Return from Sequ        \n\
  17  TZX Select Block             Options: "BACK" to block 16, "NEXT" to \
block 18\n\
  18  TZX Stop if 48K             \n\
  19  TZX Set Signal               Set Signal Level:1\n\
  20  TZX Description              Description:Text Description\n\
  21  TZX Message                  Message:Message!  message duration:5s\n\
  22  TZX Archive Info            \n\
  23  TZX Hardware Type           \n\
  24  TZX Custom Info             \n\
  25  TZX Glue Block              \n')

        self.assertEqual(self.runtest("list -od test.tzx"), b"""\
0\tTZX Header\t
1\tTZX Standard Speed\tHeader\tSCREENTEST\tBytes\t16384\t6912\tpause after:\
1000ms
2\tTZX Turbo Speed\tData\tFlag:255\tLength:6912\tpause after:1000ms
3\tTZX Pure Tone\t\tPulse Length:2168\tNumber of Pulses:8063
4\tTZX Pulse Sequence\t\tPulse Sequence Length:[667, 735]
5\tTZX Pure Data\tHeader\tJPSP      \tBytes\t16384\t6912
6\tTZX Direct Recording\t\tpause after:500ms
7\tTZX CSW Recording\t\tpause after:2000ms
8\tTZX Generalized Data\t\tpause after:1000ms
9\tTZX Pause or Stop\t\tPause 32ms
10\tTZX Group Start\t\tGroup Name:Group Test
11\tTZX Group End\t
12\tTZX Jump To\t\tJump To block:10
13\tTZX Loop Start\t\tRepetitions:65534
14\tTZX Loop End\t
15\tTZX Call Sequence\t\tCalls to:[17, 14]
16\tTZX Return from Sequence\t
17\tTZX Select Block\t\tOptions:\t"BACK" to block 16\t"NEXT" to block 18
18\tTZX Stop if 48K\t
19\tTZX Set Signal\t\tLevel:1
20\tTZX Description\t\tDescription:Text Description
21\tTZX Message\t\tMessage:Message!\tduration:5s
22\tTZX Archive Info\tFull title:Full Title\tSoftware house/publisher:Publishe\
r\tAuthor(s):Author\tYear of publication:Year\tLanguage:Language\tGame/utility\
 type:Type\tPrice:Price\tProtection scheme/loader:Protection\tOrigin:Origin\tC\
omment(s):Comments\tOther
23\tTZX Hardware Type\t
24\tTZX Custom Info\t
25\tTZX Glue Block\t
""")
        # tidy up
        os.remove("temp.txt")

    def test_extract(self):
        self.assertEqual(self.runtest("extract 1 arraytest_char.tap temp.bin"),
                         b"")
        self.assertEqual(_getfileasbytes("temp.bin"),
                         _getfileasbytes("arraytest_char.dat"))
        # tidy up
        os.remove("temp.bin")

    def test_copy(self):
        self.assertEqual(self.runtest("copy -s 0-1 screentest.tap temp.tap"),
                         b"")
        self.assertEqual(self.runtest("list -o temp.tap"),
                         b"""block type                content information
   0  TAP Block            Header "SCREENTEST" Bytes 16384,6912
   1  TAP Block            Data   Flag:255, block length:6912
""")
        # ensure overwrite existing works
        self.assertEqual(self.runtest("copy 0 basictest.tap temp.tap"), b"")
        self.assertEqual(self.runtest("list -o temp.tap"),
                         b"""block type                content information
   0  TAP Block            Header "BASIC     " Program
""")

        # ensure append works
        self.assertEqual(self.runtest("copy -a 0-1 screentest.tap temp.tap"),
                         b"")
        self.assertEqual(self.runtest("list -o temp.tap"),
                         b"""block type                content information
   0  TAP Block            Header "BASIC     " Program
   1  TAP Block            Header "SCREENTEST" Bytes 16384,6912
   2  TAP Block            Data   Flag:255, block length:6912
""")

        # ensure copy to specified position works
        self.assertEqual(self.runtest(
            "copy -p 1 0 arraytest_char.tap temp.tap"), b"")
        self.assertEqual(self.runtest("list -o temp.tap"),
                         b"""block type                content information
   0  TAP Block            Header "BASIC     " Program
   1  TAP Block            Header "c         " Character array S$
   2  TAP Block            Header "SCREENTEST" Bytes 16384,6912
   3  TAP Block            Data   Flag:255, block length:6912
""")

        # tidy up
        os.remove("temp.tap")

    def test_delete(self):
        self.assertEqual(self.runtest("delete 0 basictest.tap temp.tap"), b"")
        self.assertEqual(self.runtest("list -o temp.tap"),
                         b"""block type                content information
   0  TAP Block            Data   Flag:255, block length:190
""")

        # create copy
        with open("temp.tap", "wb") as f:
            f.write(_getfileasbytes("basictest.tap"))
        self.assertEqual(self.runtest("delete -s 0-1 temp.tap temp.tap"), b"")
        self.assertEqual(self.runtest("list -o temp.tap"),
                         b"block type                content information\n")
        # tidy up
        os.remove("temp.tap")

    def test_create(self):
        self.assertEqual(self.runtest("create basic --filename TEST \
--autostart 10 basictest.dat temp.tap"), b"")
        self.assertEqual(self.runtest("list -o temp.tap"),
                         b"""block type                content information
   0  TAP Block            Header "TEST      " Program Line:10
   1  TAP Block            Data   Flag:255, block length:190
""")

        self.assertEqual(self.runtest("create code --filename TEST --origin \
0x8000 -a screentest.dat temp.tap"), b"")
        self.assertEqual(self.runtest("list -o temp.tap"),
                         b"""block type                content information
   0  TAP Block            Header "TEST      " Program Line:10
   1  TAP Block            Data   Flag:255, block length:190
   2  TAP Block            Header "TEST      " Bytes 32768,6912
   3  TAP Block            Data   Flag:255, block length:6912
""")

        self.assertEqual(self.runtest("create array --filename ARRAY \
--arraytype string --arrayname S -i temp.tap", "Test1\nTest2\nTest3"), b"")
        self.assertEqual(self.runtest("list -o temp.tap"),
                         b"""block type                content information
   0  TAP Block            Header "ARRAY     " Character array S$
   1  TAP Block            Data   Flag:255, block length:17
""")
        self.assertEqual(self.runtest("extract 1 -o temp.tap"),
                         b"Test1\nTest2\nTest3")

        self.assertEqual(self.runtest("create array --filename ARRAYnum \
--arraytype n --arrayname N arraytest_number.dat temp.tap"), b"")
        self.assertEqual(self.runtest("list -o temp.tap"),
                         b"""block type                content information
   0  TAP Block            Header "ARRAYnum  " Number array N
   1  TAP Block            Data   Flag:255, block length:1005
""")
        self.assertEqual(self.runtest("extract 1 temp.tap temp.bin"), b"")
        self.assertEqual(_getfileasbytes("temp.bin"),
                         _getfileasbytes("arraytest_number.dat"))

        self.assertEqual(self.runtest("create screen --filename SCR \
screentest.dat temp.tap"), b"")
        self.assertEqual(self.runtest("list -o temp.tap"),
                         b"""block type                content information
   0  TAP Block            Header "SCR       " Bytes 16384,6912
   1  TAP Block            Data   Flag:255, block length:6912
""")

        # tidy up
        os.remove("temp.tap")
        os.remove("temp.bin")

    def checkinvalidcommand(self, command, message):
        try:
            spectrumtape._commandline(["x.py"] + command.split())
            self.fail("No SpectrumTranslateError raised")
        except spectrumtranslate.SpectrumTranslateError as se:
            if se.value == message:
                return
            self.fail("Wrong exception message. Got:\n{}\nExpected:\n{}".
                      format(se.value, message))

    def test_invalidcommands(self):
        # incorrect command
        self.checkinvalidcommand("hello", "No command (list, extract, delete, \
copy, create, or help) specified as first argument.")
        # multiple actions
        self.checkinvalidcommand("create list",
                                 "Can't have multiple commands.")
        # no input file
        self.checkinvalidcommand("list", "No input file specified.")
        # no output file
        self.checkinvalidcommand("list infile", "No output file specified.")
        # invalid create command
        self.checkinvalidcommand("create wrong", "Must specify what type of \
file to create. Valid options are basic, code, array, screen, and block.")
        # invalid autostart
        self.checkinvalidcommand("create basic --autostart notnumber",
                                 "notnumber is not a valid autostart number.")
        # invalid variable offset
        self.checkinvalidcommand("create basic --variableoffset notnumber",
                                 "notnumber is not a valid variable offset.")
        # invalid origin
        self.checkinvalidcommand("create code --origin notnumber",
                                 "notnumber is not a valid code origin.")
        self.checkinvalidcommand("create code --origin 65537",
                                 "code origin must be 0-65535 inclusive.")
        # invalid flag
        self.checkinvalidcommand("create block --flag notnumber",
                                 "notnumber is not a valid flag value.")
        self.checkinvalidcommand("create block --flag 256",
                                 "flag value must be 0-255 inclusive.")
        # invalid arrayname
        self.checkinvalidcommand("create array --arrayname wrong",
                                 "wrong is not a valid variable name.")
        # invalid arraytype
        self.checkinvalidcommand("create array --arraytype wrong", "wrong is \
not a valid array type (must be character, number or string).")
        # invalid argument to -p
        self.checkinvalidcommand("copy -p wrong in out", "wrong is not a \
valid index for the output file.")
        # invalid argument to -s
        self.checkinvalidcommand("copy -s wrong in out",
                                 '"wrong" is invalid list of file indexes.')
        # invalid index to extract
        self.checkinvalidcommand("extract wrong in out", "wrong is not a \
valid index in the input file.")
        # no index to extract
        self.checkinvalidcommand("extract -o -i",
                                 "No file index specified to extract.")
        # invalid index to copy or delete
        self.checkinvalidcommand("copy wrong in out",
                                 '"wrong" is invalid list of file indexes.')
        # no index to copy or delete
        self.checkinvalidcommand("delete -o -i",
                                 "No file index(s) specified to delete.")
        # unrecognised argument
        self.checkinvalidcommand("list -o -i extra",
                                 '"extra" is unrecognised argument.')
        # no specified file to extract
        self.checkinvalidcommand("extract -i -o",
                                 "No file index specified to extract.")
        # unspecidied file to copy or delete
        self.checkinvalidcommand("copy -i -o",
                                 "No file index(s) specified to copy.")
        # create without filename
        self.checkinvalidcommand("create basic -i -o",
                                 "You have to specify file name to create.")
        # create array without name or type
        self.checkinvalidcommand("create array --filename X --arraytype s in \
out", "You have to specify array type and name.")
        self.checkinvalidcommand("create array --filename X --arrayname X in \
out", "You have to specify array type and name.")
        # invalid index to extract
        self.checkinvalidcommand("extract 88 screentest.tap out",
                                 "88 is greater than the number of entries in \
the source data.")
        # invalid index to copy
        self.checkinvalidcommand("copy 88 screentest.tap out",
                                 "88 is greater than the number of entries in \
the source data.")
        # can't mix --tap and --tzx
        self.checkinvalidcommand("copy --tap --tzx 1 test.tzx out", "You need \
to specify output as either tap or tzx.")
        self.checkinvalidcommand("copy --tzx --tap 1 test.tzx out", "You need \
to specify output as either tap or tzx.")
        # invalid multiple flag
        self.checkinvalidcommand("list -xyz in out", "-x is not a recognised \
flag.")


if __name__ == "__main__":
    unittest.main()
