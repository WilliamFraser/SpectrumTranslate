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
Unit Test for spectrumtapblock file
"""

import subprocess
import unittest
import re
import sys
import os
from os import remove as os_remove
from sys import hexversion as _PYTHON_VERSION_HEX
# imported elsewhere for memory reasons are:
# unicode_escape_decode in the codecs module
# imported io/StringIO later so get python version specific one
# import modules from parent directory
pathtemp = sys.path
sys.path += [os.path.dirname(os.getcwd())]
import spectrumtapblock
import spectrumtranslate
# restore system path
sys.path = pathtemp

if(_PYTHON_VERSION_HEX > 0x03000000):
    from io import StringIO

    def _u(x):
        return x

else:
    # 2to3 will complain but won't cause problems in real life
    from StringIO import StringIO
    from codecs import unicode_escape_decode as _UED

    def _u(x):
        return _UED(x)[0]


def _getfile(name):
    with open(name, 'r') as f:
        return f.read()


def _getfileasbytes(name):
    with open(name, 'rb') as infile:
        return bytearray(infile.read())


class Testutilityfunctions(unittest.TestCase):
    def test_validateandpreparebytes_validate(self):
        if(_PYTHON_VERSION_HEX > 0x03000000):
            self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                              spectrumtapblock._validateandpreparebytes,
                              "Wrong", "test")
        else:
            self.assertTrue(spectrumtapblock._validateandpreparebytes("Hello"))
            # 2to3 will complain but is ok as won't run in python 3
            self.assertTrue(spectrumtapblock._validateandpreparebytes([long(1),
                                                                       long(2)]
                                                                      ))
            # bytes is valid in python 2 as it looks like a string
            # so not checked

        self.assertTrue(spectrumtapblock._validateandpreparebytes(bytes(
                                                                  b"Test")))
        self.assertTrue(spectrumtapblock._validateandpreparebytes(bytearray(
                                                                  b"Test")))
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtapblock._validateandpreparebytes, 1, "X")
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtapblock._validateandpreparebytes,
                          ["Wrong", "input"], "X")
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtapblock._validateandpreparebytes,
                          [0.1, 0.2], "X")
        self.assertTrue(spectrumtapblock._validateandpreparebytes([1, 2]))

    def test_validateandpreparebytes_prepare(self):
        self.assertEqual(spectrumtapblock._validateandpreparebytes([1, 2]),
                         bytearray([1, 2]))
        if(_PYTHON_VERSION_HEX < 0x03000000):
            self.assertEqual(spectrumtapblock._validateandpreparebytes("Test"),
                             bytearray([84, 101, 115, 116]))

        self.assertEqual(spectrumtapblock._validateandpreparebytes(bytearray(
                                                                   b"Test")),
                         bytearray([84, 101, 115, 116]))
        self.assertEqual(spectrumtapblock._validateandpreparebytes(bytes(
                                                                   b"Test")),
                         bytearray([84, 101, 115, 116]))

    def test_get_word(self):
        self.assertEqual(spectrumtapblock._get_word([1, 2, 3]), 0x0201)

    def test_validateandconvertfilename(self):
        self.assertEqual(spectrumtapblock._validateandconvertfilename(
                         [65, 66, 67]), bytearray(b'ABC       '))
        self.assertEqual(spectrumtapblock._validateandconvertfilename(
                         "ABC"), bytearray(b'ABC       '))
        self.assertEqual(spectrumtapblock._validateandconvertfilename(
                         ["A", "B", "C"]), bytearray(b'ABC       '))
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtapblock._validateandconvertfilename,
                          [0.1, 0.2])
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtapblock._validateandconvertfilename,
                          0.1)
        if(_PYTHON_VERSION_HEX < 0x03000000):
            # 2to3 will complain but is ok as won't run in python 3
            self.assertEqual(spectrumtapblock._validateandconvertfilename(
                             [long(65), long(66), long(67)]),
                             bytearray(b'ABC       '))


class TestSpectrumTapBlock(unittest.TestCase):
    def test_create(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.data, bytearray([]))
        self.assertEqual(stb.flag, 0)
        self.assertEqual(stb.filePosition, 0)

        stb = spectrumtapblock.SpectrumTapBlock(flag=255, data=[1, 2])
        self.assertEqual(stb.data, bytearray([1, 2]))
        self.assertEqual(stb.flag, 255)
        self.assertEqual(stb.filePosition, 0)

        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtapblock.SpectrumTapBlock,
                          flag="hello")

    def test_isheadder(self):
        stb = spectrumtapblock.SpectrumTapBlock(data=[0]*17)
        self.assertTrue(stb.isheadder())
        stb.flag = 255
        self.assertFalse(stb.isheadder())
        stb.flag = 0
        stb.data = bytearray([1])
        self.assertFalse(stb.isheadder())

    def test_getfilename(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getfilename(), None)
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getfilename(), "BASIC     ")
        stb.data = bytearray([0, 254, 65, 127, 96, 32, 32, 32, 32, 32, 32, 0,
                              0, 0, 0, 0, 0])
        self.assertEqual(stb.getfilename(), _u('RETURN A\xa9\xa3      '))

    def test_getrawfilename(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getrawfilename(), bytearray([66, 65, 83, 73, 67,
                                                          32, 32, 32, 32, 32]))
        stb.data = bytearray([0, 254, 65, 127, 96, 32, 32, 32, 32, 32, 32, 0,
                              0, 0, 0, 0, 0])
        self.assertEqual(stb.getrawfilename(), bytearray([254, 65, 127, 96, 32,
                                                          32, 32, 32, 32, 32]))

    def test_getfiletypestring(self):
        stb = spectrumtapblock.SpectrumTapBlock()
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

    def test_getfiledetailsstring(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getfiledetailsstring(), None)
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getfiledetailsstring(), '"BASIC     " Program')
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getfiledetailsstring(),
                         '"SCREENTEST" Bytes 16384,6912')
        stb.data = _getfileasbytes("arraytest_number.tap")[3:20]
        self.assertEqual(stb.getfiledetailsstring(),
                         '"x         " Number array X')
        stb.data = _getfileasbytes("arraytest_char.tap")[3:20]
        self.assertEqual(stb.getfiledetailsstring(),
                         '"c         " Character array S$')

    def test_getheadderautostartline(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheadderautostartline(), -2)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheadderautostartline(), -2)
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getheadderautostartline(), -1)
        stb.data[13] = 10
        stb.data[14] = 0
        self.assertEqual(stb.getheadderautostartline(), 10)

    def test_getheaddervariableoffset(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheaddervariableoffset(), -2)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheaddervariableoffset(), -2)
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getheaddervariableoffset(), 78)

    def test_getheaddercodestart(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheaddercodestart(), -2)
        stb.data = _getfileasbytes("basictest.tap")[3:20]
        self.assertEqual(stb.getheaddercodestart(), -2)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheaddercodestart(), 16384)

    def test_getheadderdescribeddatalength(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheadderdescribeddatalength(), -2)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheadderdescribeddatalength(), 6912)

    def test_getheaddervariableletter(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheaddervariableletter(), None)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheaddervariableletter(), None)
        stb.data = _getfileasbytes("arraytest_number.tap")[3:20]
        self.assertEqual(stb.getheaddervariableletter(), "X")
        stb.data = _getfileasbytes("arraytest_char.tap")[3:20]
        self.assertEqual(stb.getheaddervariableletter(), "S")

    def test_getheaddervariablename(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheaddervariablename(), None)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheaddervariablename(), None)
        stb.data = _getfileasbytes("arraytest_number.tap")[3:20]
        self.assertEqual(stb.getheaddervariablename(), "X")
        stb.data = _getfileasbytes("arraytest_char.tap")[3:20]
        self.assertEqual(stb.getheaddervariablename(), "S$")

    def test_getheadderarraydescriptor(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheadderarraydescriptor(), -1)
        stb.data = _getfileasbytes("screentest.tap")[3:20]
        self.assertEqual(stb.getheadderarraydescriptor(), -1)
        stb.data = _getfileasbytes("arraytest_number.tap")[3:20]
        self.assertEqual(stb.getheadderarraydescriptor() & 192, 128)
        stb.data = _getfileasbytes("arraytest_char.tap")[3:20]
        self.assertEqual(stb.getheadderarraydescriptor() & 192, 192)

    def test_getdatastartoffset(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getdatastartoffset(), 3)

    def test__str__(self):
        stb = spectrumtapblock.SpectrumTapBlock(flag=255, data=[1, 2, 3])
        self.assertEqual(str(stb), "Flag:255, block length:3")

    def test_getpackagedforfile(self):
        stb = spectrumtapblock.SpectrumTapBlock(flag=255, data=[1, 2, 3])
        self.assertEqual(stb.getpackagedforfile(),
                         b'\x05\x00\xff\x01\x02\x03\xff')

    def test_savetofile(self):
        stb = spectrumtapblock.SpectrumTapBlock(flag=255, data=[1, 2, 3])
        stb.savetofile("testout.tap", False)
        data = _getfileasbytes("testout.tap")
        self.assertEqual(data, bytearray([5, 0, 255, 1, 2, 3, 255]))
        stb.savetofile("testout.tap")
        data = _getfileasbytes("testout.tap")
        self.assertEqual(data, bytearray([5, 0, 255, 1, 2, 3, 255, 5, 0, 255,
                                          1, 2, 3, 255]))
        os_remove("testout.tap")


class Testmetafunctions(unittest.TestCase):
    def test_gettapblockfromfile(self):
        position = 0
        with open("arraytest_char.tap", "rb") as f:
            tb = spectrumtapblock.gettapblockfromfile(f, position)
            position += 4 + len(tb.data)
            self.assertEqual(tb.data, bytearray([2, 99, 32, 32, 32, 32, 32, 32,
                                                 32, 32, 32, 31, 0, 93, 211, 0,
                                                 128]))
            self.assertEqual(tb.flag, 0)
            self.assertEqual(tb.filePosition, 0)

            tb = spectrumtapblock.gettapblockfromfile(f, position)
            position += 4 + len(tb.data)
            self.assertEqual(tb.data, bytearray([3, 2, 0, 3, 0, 4, 0, 116, 101,
                                                 115, 116, 109, 117, 109, 32,
                                                 103, 111, 111, 100, 111, 110,
                                                 101, 32, 116, 119, 111, 32,
                                                 116, 104, 114, 101]))
            self.assertEqual(tb.flag, 255)
            self.assertEqual(tb.filePosition, 21)

            tb = spectrumtapblock.gettapblockfromfile(f, position)
            self.assertEqual(tb, None)

    def test_gettapblockfrombytes(self):
        tb = spectrumtapblock.gettapblockfrombytes([5, 0, 255, 1, 2, 3, 255])
        self.assertEqual(tb.data, bytearray([1, 2, 3]))
        self.assertEqual(tb.flag, 255)
        self.assertEqual(tb.filePosition, 0)

    def test_gettapblocks(self):
        tbs = spectrumtapblock.gettapblocks("arraytest_char.tap")
        self.assertEqual(len(tbs), 2)
        self.assertTrue(all(isinstance(tb, spectrumtapblock.SpectrumTapBlock)
                            for tb in tbs))

    def test_tapblockfromfile(self):
        tbs = [tb for tb in
               spectrumtapblock.tapblockfromfile("arraytest_char.tap")]
        self.assertEqual(len(tbs), 2)
        self.assertTrue(all(isinstance(tb, spectrumtapblock.SpectrumTapBlock)
                            for tb in tbs))

    def test_tapblockfrombytes(self):
        tbs = [tb for tb in spectrumtapblock.tapblockfrombytes(
               [5, 0, 255, 1, 2, 3, 255, 5, 0, 255, 1, 2, 3, 255])]
        self.assertEqual(len(tbs), 2)
        self.assertTrue(all(isinstance(tb, spectrumtapblock.SpectrumTapBlock)
                            for tb in tbs))

    def test_createbasicheadder(self):
        tb = spectrumtapblock.createbasicheadder("Hello", 20, 30)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([0, 72, 101, 108, 108, 111, 32, 32,
                                             32, 32, 32, 30, 0, 0, 128, 20, 0]
                                            ))

    def test_createcodeheadder(self):
        tb = spectrumtapblock.createcodeheadder("Code", 16384, 6912)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([3, 67, 111, 100, 101, 32, 32, 32,
                                             32, 32, 32, 0, 27, 0, 64, 0, 0]))

    def test_createarrayheadder(self):
        tb = spectrumtapblock.createarrayheadder("Number", 129, 10)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([1, 78, 117, 109, 98, 101, 114, 32,
                                             32, 32, 32, 10, 0, 0, 129, 0, 0]))
        tb = spectrumtapblock.createarrayheadder("Char", 194, 10)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([2, 67, 104, 97, 114, 32, 32, 32,
                                             32, 32, 32, 10, 0, 0, 194, 0, 0]))
        tb = spectrumtapblock.createarrayheadder("String", 194, 10)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([2, 83, 116, 114, 105, 110, 103,
                                             32, 32, 32, 32, 10, 0, 0, 194, 0,
                                             0]))

    def test_createscreenheadder(self):
        tb = spectrumtapblock.createscreenheadder("Screen")
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, bytearray([3, 83, 99, 114, 101, 101, 110, 32,
                                             32, 32, 32, 0, 27, 0, 64, 0, 0]))

    def test_createdatablock(self):
        tb = spectrumtapblock.createdatablock([1, 2, 3], 1)
        self.assertEqual(tb.flag, 1)
        self.assertEqual(tb.data, bytearray([1, 2, 3]))


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
        output, error = self.runpep8("../spectrumtapblock.py", [], [])
        self.assertEqual(output, "", "../spectrumtapblock.py pep8 formatting \
errors:\n" + output)
        self.assertEqual(error, "", "../spectrumtapblock.py pep8 format check \
had errors:\n" + error)

        output, error = self.runpep8("test_spectrumtapblock.py", [], [
            "test_spectrumtapblock.py:60:1: E402 module level import not at \
top of file",
            "test_spectrumtapblock.py:61:1: E402 module level import not at \
top of file"])
        self.assertEqual(output, "", "test_spectrumtapblock.py pep8 \
formatting errors:\n" + output)
        self.assertEqual(error, "", "test_spectrumtapblock.py pep8 format \
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
        output, error = self.run2to3("../spectrumtapblock.py", [], [])
        self.assertEqual(output, [], "../spectrumtapblock.py 2to3 errors:\n" +
                         "".join(output))
        self.assertEqual(error, "",
                         "../spectrumtapblock.py 2to3 check had errors:\n" +
                         error)

        output, error = self.run2to3("test_spectrumtapblock.py", [], [])
        self.assertEqual(output, [],
                         "test_spectrumtapblock.py 2to3 errors:\n" +
                         "".join(output))
        self.assertEqual(error, "",
                         "test_spectrumtapblock.py 2to3 check had errors:\n" +
                         error)


class Testcommandline(unittest.TestCase):
    def runtest(self, command, stdindata):
        saved_output = sys.stdout
        saved_input = sys.stdin
        sys.stdin = StringIO(stdindata)
        output = StringIO()
        sys.stdout = output
        try:
            spectrumtapblock._commandline(["spectrumtapblock.py"] +
                                          command.split())

        finally:
            sys.stdout = saved_output
            sys.stdin = saved_input

        out = output.getvalue()
        output.close()
        return out

    def setUp(self):
        # tidy up
        try:
            os_remove("temp.tap")
        except:
            pass

        try:
            os_remove("temp.txt")
        except:
            pass

        try:
            os_remove("temp.bin")
        except:
            pass

    def test_help(self):
        self.assertEqual(self.runtest("", ""), spectrumtapblock.usage())
        self.assertEqual(self.runtest("help", ""), spectrumtapblock.usage())

    def test_list(self):
        self.assertEqual(self.runtest("list -o basictest.tap", ""),
                         """position type    information
  0      Headder "BASIC     " Program
  1      Data    Flag:255, block length:190
""")

        self.assertEqual(self.runtest("list --details basictest.tap temp.txt",
                                      ""), "")
        self.assertEqual(_getfile("temp.txt"), """\
0\tHeadder\tBASIC     \tProgram\t190\t0\t78
1\tData\t255\t190
""")
        # tidy up
        os_remove("temp.txt")

    def test_extract(self):
        self.assertEqual(self.runtest("extract 1 arraytest_char.tap temp.bin",
                                      ""), "")
        self.assertEqual(_getfileasbytes("temp.bin"),
                         _getfileasbytes("arraytest_char.dat"))
        # tidy up
        os_remove("temp.bin")

    def test_copy(self):
        self.assertEqual(self.runtest("copy -s 0-1 screentest.tap temp.tap",
                                      ""), "")
        self.assertEqual(self.runtest("list -o temp.tap", ""),
                         """position type    information
  0      Headder "SCREENTEST" Bytes 16384,6912
  1      Data    Flag:255, block length:6912
""")
        # ensure overwrite existing works
        self.assertEqual(self.runtest("copy 0 basictest.tap temp.tap", ""), "")
        self.assertEqual(self.runtest("list -o temp.tap", ""),
                         """position type    information
  0      Headder "BASIC     " Program
""")

        # ensure append works
        self.assertEqual(self.runtest("copy -a 0-1 screentest.tap temp.tap",
                                      ""), "")
        self.assertEqual(self.runtest("list -o temp.tap", ""),
                         """position type    information
  0      Headder "BASIC     " Program
  1      Headder "SCREENTEST" Bytes 16384,6912
  2      Data    Flag:255, block length:6912
""")

        # ensure copy to specified position works
        self.assertEqual(self.runtest(
            "copy -p 1 0 arraytest_char.tap temp.tap", ""), "")
        self.assertEqual(self.runtest("list -o temp.tap", ""),
                         """position type    information
  0      Headder "BASIC     " Program
  1      Headder "c         " Character array S$
  2      Headder "SCREENTEST" Bytes 16384,6912
  3      Data    Flag:255, block length:6912
""")

        # tidy up
        os_remove("temp.tap")

    def test_delete(self):
        self.assertEqual(self.runtest("delete 0 basictest.tap temp.tap", ""),
                         "")

        self.assertEqual(self.runtest("list -o temp.tap", ""),
                         """position type    information
  0      Data    Flag:255, block length:190
""")

        # create copy
        with open("temp.tap", "wb") as f:
            f.write(_getfileasbytes("basictest.tap"))
        self.assertEqual(self.runtest("delete -s 0-1 temp.tap temp.tap", ""),
                         "")
        self.assertEqual(self.runtest("list -o temp.tap", ""),
                         """position type    information\n""")
        # tidy up
        os_remove("temp.tap")

    def test_create(self):
        self.assertEqual(self.runtest("create basic --filename TEST \
--autostart 10 basictest.dat temp.tap", ""), "")
        self.assertEqual(self.runtest("list -o temp.tap", ""),
                         """position type    information
  0      Headder "TEST      " Program Line:10
  1      Data    Flag:255, block length:190
""")

        self.assertEqual(self.runtest("create code --filename TEST --origin \
0x8000 -a screentest.dat temp.tap", ""), "")
        self.assertEqual(self.runtest("list -o temp.tap", ""),
                         """position type    information
  0      Headder "TEST      " Program Line:10
  1      Data    Flag:255, block length:190
  2      Headder "TEST      " Bytes 32768,6912
  3      Data    Flag:255, block length:6912
""")

        self.assertEqual(self.runtest("create array --filename ARRAY \
--arraytype string --arrayname S -i temp.tap", "Test1\nTest2\nTest3"), "")
        self.assertEqual(self.runtest("list -o temp.tap", ""),
                         """position type    information
  0      Headder "ARRAY     " Character array S$
  1      Data    Flag:255, block length:17
""")
        self.assertEqual(self.runtest("extract 1 -o temp.tap", ""),
                         "Test1\nTest2\nTest3")

        self.assertEqual(self.runtest("create array --filename ARRAYnum \
--arraytype n --arrayname N arraytest_number.dat temp.tap", ""), "")
        self.assertEqual(self.runtest("list -o temp.tap", ""),
                         """position type    information
  0      Headder "ARRAYnum  " Number array N
  1      Data    Flag:255, block length:1005
""")
        self.assertEqual(self.runtest("extract 1 temp.tap temp.bin", ""), "")
        self.assertEqual(_getfileasbytes("temp.bin"),
                         _getfileasbytes("arraytest_number.dat"))

        self.assertEqual(self.runtest("create screen --filename SCR \
screentest.dat temp.tap", ""), "")
        self.assertEqual(self.runtest("list -o temp.tap", ""),
                         """position type    information
  0      Headder "SCR       " Bytes 16384,6912
  1      Data    Flag:255, block length:6912
""")

        # tidy up
        os_remove("temp.tap")
        os_remove("temp.bin")

    def checkinvalidcommand(self, command, message):
        try:
            spectrumtapblock._commandline(["x.py"] + command.split())
            self.fail("No SpectrumTranslateError raised")
        except spectrumtranslate.SpectrumTranslateError as se:
            if(se.value == message):
                return
            self.fail("Wrong exception message. Got:\n{0}\nExpected:\n{1}".
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


if __name__ == "__main__":
    unittest.main()
