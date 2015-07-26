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
Unit Test for spectrumtapblock file
"""

import spectrumtapblock
import spectrumtranslate
import unittest
from os import remove as os_remove
from sys import hexversion as _PYTHON_VERSION_HEX
# imported elsewhere for memory reasons are:
# unicode_escape_decode in the codecs module

_TEST_DIRECTORY = "test/"

if(_PYTHON_VERSION_HEX > 0x03000000):
    def _u(x):
        return x

    def _getfileaslist(name):
        with open(_TEST_DIRECTORY + name, 'rb') as infile:
            return [b for b in infile.read()]

else:
    from codecs import unicode_escape_decode as _UED
    # 2to3 will complain about this but won't cause problems in real life

    def _u(x):
        return _UED(x)[0]

    def _getfileaslist(name):
        with open(_TEST_DIRECTORY + name, 'rb') as infile:
            return [ord(b) for b in infile.read()]


class Testutilityfunctions(unittest.TestCase):
    def test_checkisvalidbytes(self):
        if(_PYTHON_VERSION_HEX > 0x03000000):
            self.assertTrue(spectrumtapblock._checkisvalidbytes(bytes(
                                                                b"Test")))
            self.assertTrue(spectrumtapblock._checkisvalidbytes(bytearray(
                                                                b"Test")))
            self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                              spectrumtapblock._checkisvalidbytes, "Wrong")
        else:
            self.assertTrue(spectrumtapblock._checkisvalidbytes("Hello"))
            # 2to3 will complain but is ok as won't run in python 3
            self.assertTrue(spectrumtapblock._checkisvalidbytes([long(1),
                                                                 long(2)]))
            # bytes is valid in python 2 as it looks like a string
            # so not checked
            self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                              spectrumtapblock._checkisvalidbytes,
                              bytearray(b"Test"))

        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtapblock._checkisvalidbytes, 1)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtapblock._checkisvalidbytes,
                          ["Wrong", "input"])
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          spectrumtapblock._checkisvalidbytes,
                          [0.1, 0.2])
        self.assertTrue(spectrumtapblock._checkisvalidbytes([1, 2]))

    def test_validbytestointlist(self):
        self.assertEqual(spectrumtapblock._validbytestointlist([1, 2]), [1, 2])
        if(_PYTHON_VERSION_HEX > 0x03000000):
            self.assertEqual(spectrumtapblock._validbytestointlist(bytearray(
                                                                   b"Test")),
                             [84, 101, 115, 116])
            self.assertEqual(spectrumtapblock._validbytestointlist(bytes(
                                                                   b"Test")),
                             [84, 101, 115, 116])
        else:
            self.assertEqual(spectrumtapblock._validbytestointlist("Test"),
                             [84, 101, 115, 116])

    def test_get_word(self):
        self.assertEqual(spectrumtapblock._get_word([1, 2, 3]), 0x0201)

    def test_validateandconvertfilename(self):
        self.assertEqual(spectrumtapblock._validateandconvertfilename(
                         [65, 66, 67]),
                         [65, 66, 67, 32, 32, 32, 32, 32, 32, 32])
        self.assertEqual(spectrumtapblock._validateandconvertfilename(
                         "ABC"),
                         [65, 66, 67, 32, 32, 32, 32, 32, 32, 32])
        self.assertEqual(spectrumtapblock._validateandconvertfilename(
                         ["A", "B", "C"]),
                         [65, 66, 67, 32, 32, 32, 32, 32, 32, 32])
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
                             [65, 66, 67, 32, 32, 32, 32, 32, 32, 32])


class TestSpectrumTapBlock(unittest.TestCase):
    def test_create(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.data, [])
        self.assertEqual(stb.flag, 0)
        self.assertEqual(stb.filePosition, 0)

        stb = spectrumtapblock.SpectrumTapBlock(flag=255, data=[1, 2])
        self.assertEqual(stb.data, [1, 2])
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
        stb.data = [1]
        self.assertFalse(stb.isheadder())

    def test_getfilename(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getfilename(), None)
        stb.data = _getfileaslist("basictest.tap")[3:20]
        self.assertEqual(stb.getfilename(), "BASIC     ")
        stb.data = [0, 254, 65, 127, 96, 32, 32, 32, 32, 32, 32, 0, 0, 0, 0, 0,
                    0]
        self.assertEqual(stb.getfilename(), _u('RETURN A\xa9\xa3      '))

    def test_getrawfilename(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        stb.data = _getfileaslist("basictest.tap")[3:20]
        self.assertEqual(stb.getrawfilename(), [66, 65, 83, 73, 67, 32, 32, 32,
                                                32, 32])
        stb.data = [0, 254, 65, 127, 96, 32, 32, 32, 32, 32, 32, 0, 0, 0, 0, 0,
                    0]
        self.assertEqual(stb.getrawfilename(), [254, 65, 127, 96, 32, 32, 32,
                                                32, 32, 32])

    def test_getfiletypestring(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getfiletypestring(), None)
        stb.data = _getfileaslist("basictest.tap")[3:20]
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
        stb.data = _getfileaslist("basictest.tap")[3:20]
        self.assertEqual(stb.getfiledetailsstring(), '"BASIC     " Program')
        stb.data = _getfileaslist("screentest.tap")[3:20]
        self.assertEqual(stb.getfiledetailsstring(),
                         '"SCREENTEST" Bytes 16384,6912')
        stb.data = _getfileaslist("arraytest_number.tap")[3:20]
        self.assertEqual(stb.getfiledetailsstring(),
                         '"x         " Number array X')
        stb.data = _getfileaslist("arraytest_char.tap")[3:20]
        self.assertEqual(stb.getfiledetailsstring(),
                         '"c         " Character array S$')

    def test_getheadderautostartline(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheadderautostartline(), -2)
        stb.data = _getfileaslist("screentest.tap")[3:20]
        self.assertEqual(stb.getheadderautostartline(), -2)
        stb.data = _getfileaslist("basictest.tap")[3:20]
        self.assertEqual(stb.getheadderautostartline(), -1)
        stb.data[13] = 10
        stb.data[14] = 0
        self.assertEqual(stb.getheadderautostartline(), 10)

    def test_getheaddervariableoffset(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheaddervariableoffset(), -2)
        stb.data = _getfileaslist("screentest.tap")[3:20]
        self.assertEqual(stb.getheaddervariableoffset(), -2)
        stb.data = _getfileaslist("basictest.tap")[3:20]
        self.assertEqual(stb.getheaddervariableoffset(), 78)

    def test_getheaddercodestart(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheaddercodestart(), -2)
        stb.data = _getfileaslist("basictest.tap")[3:20]
        self.assertEqual(stb.getheaddercodestart(), -2)
        stb.data = _getfileaslist("screentest.tap")[3:20]
        self.assertEqual(stb.getheaddercodestart(), 16384)

    def test_getheadderdescribeddatalength(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheadderdescribeddatalength(), -2)
        stb.data = _getfileaslist("screentest.tap")[3:20]
        self.assertEqual(stb.getheadderdescribeddatalength(), 6912)

    def test_getheaddervariableletter(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheaddervariableletter(), None)
        stb.data = _getfileaslist("screentest.tap")[3:20]
        self.assertEqual(stb.getheaddervariableletter(), None)
        stb.data = _getfileaslist("arraytest_number.tap")[3:20]
        self.assertEqual(stb.getheaddervariableletter(), "X")
        stb.data = _getfileaslist("arraytest_char.tap")[3:20]
        self.assertEqual(stb.getheaddervariableletter(), "S")

    def test_getheaddervariablename(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheaddervariablename(), None)
        stb.data = _getfileaslist("screentest.tap")[3:20]
        self.assertEqual(stb.getheaddervariablename(), None)
        stb.data = _getfileaslist("arraytest_number.tap")[3:20]
        self.assertEqual(stb.getheaddervariablename(), "X")
        stb.data = _getfileaslist("arraytest_char.tap")[3:20]
        self.assertEqual(stb.getheaddervariablename(), "S$")

    def test_getheadderarraydescriptor(self):
        stb = spectrumtapblock.SpectrumTapBlock()
        self.assertEqual(stb.getheadderarraydescriptor(), -1)
        stb.data = _getfileaslist("screentest.tap")[3:20]
        self.assertEqual(stb.getheadderarraydescriptor(), -1)
        stb.data = _getfileaslist("arraytest_number.tap")[3:20]
        self.assertEqual(stb.getheadderarraydescriptor() & 192, 128)
        stb.data = _getfileaslist("arraytest_char.tap")[3:20]
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
        stb.savetofile(_TEST_DIRECTORY + "testout.tap", False)
        data = _getfileaslist("testout.tap")
        self.assertEqual(data, [5, 0, 255, 1, 2, 3, 255])
        stb.savetofile(_TEST_DIRECTORY + "testout.tap")
        data = _getfileaslist("testout.tap")
        self.assertEqual(data, [5, 0, 255, 1, 2, 3, 255, 5, 0, 255, 1, 2, 3,
                                255])
        os_remove(_TEST_DIRECTORY + "testout.tap")


class Testmetafunctions(unittest.TestCase):
    def test_gettapblockfromfile(self):
        position = 0
        with open(_TEST_DIRECTORY + "arraytest_char.tap", "rb") as f:
            tb = spectrumtapblock.gettapblockfromfile(f, position)
            position += 4 + len(tb.data)
            self.assertEqual(tb.data, [2, 99, 32, 32, 32, 32, 32, 32, 32, 32,
                                       32, 31, 0, 93, 211, 0, 128])
            self.assertEqual(tb.flag, 0)
            self.assertEqual(tb.filePosition, 0)

            tb = spectrumtapblock.gettapblockfromfile(f, position)
            position += 4 + len(tb.data)
            self.assertEqual(tb.data, [3, 2, 0, 3, 0, 4, 0, 116, 101, 115, 116,
                                       109, 117, 109, 32, 103, 111, 111, 100,
                                       111, 110, 101, 32, 116, 119, 111, 32,
                                       116, 104, 114, 101])
            self.assertEqual(tb.flag, 255)
            self.assertEqual(tb.filePosition, 21)

            tb = spectrumtapblock.gettapblockfromfile(f, position)
            self.assertEqual(tb, None)

    def test_gettapblockfrombytes(self):
        tb = spectrumtapblock.gettapblockfrombytes([5, 0, 255, 1, 2, 3, 255])
        self.assertEqual(tb.data, [1, 2, 3])
        self.assertEqual(tb.flag, 255)
        self.assertEqual(tb.filePosition, 0)

    def test_gettapblocks(self):
        tbs = spectrumtapblock.gettapblocks(_TEST_DIRECTORY +
                                            "arraytest_char.tap")
        self.assertEqual(len(tbs), 2)
        self.assertTrue(all(isinstance(tb, spectrumtapblock.SpectrumTapBlock)
                            for tb in tbs))

    def test_tapblockfromfile(self):
        tbs = [tb for tb in
               spectrumtapblock.tapblockfromfile(_TEST_DIRECTORY +
                                                 "arraytest_char.tap")]
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
        self.assertEqual(tb.data, [0, 72, 101, 108, 108, 111, 32, 32, 32, 32,
                                   32, 30, 0, 0, 128, 20, 0])

    def test_createcodeheadder(self):
        tb = spectrumtapblock.createcodeheadder("Code", 16384, 6912)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, [3, 67, 111, 100, 101, 32, 32, 32, 32, 32,
                                   32, 0, 27, 0, 64, 0, 0])

    def test_createarrayheadder(self):
        tb = spectrumtapblock.createarrayheadder("Number", 129, 10)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, [1, 78, 117, 109, 98, 101, 114, 32, 32, 32,
                                   32, 10, 0, 0, 129, 0, 0])
        tb = spectrumtapblock.createarrayheadder("Char", 194, 10)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, [2, 67, 104, 97, 114, 32, 32, 32, 32, 32,
                                   32, 10, 0, 0, 194, 0, 0])
        tb = spectrumtapblock.createarrayheadder("String", 194, 10)
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, [2, 83, 116, 114, 105, 110, 103, 32, 32, 32,
                                   32, 10, 0, 0, 194, 0, 0])

    def test_createscreenheadder(self):
        tb = spectrumtapblock.createscreenheadder("Screen")
        self.assertEqual(tb.flag, 0)
        self.assertEqual(tb.data, [3, 83, 99, 114, 101, 101, 110, 32, 32, 32,
                                   32, 0, 27, 0, 64, 0, 0])

    def test_createdatablock(self):
        tb = spectrumtapblock.createdatablock([1, 2, 3], 1)
        self.assertEqual(tb.flag, 1)
        self.assertEqual(tb.data, [1, 2, 3])


# todo test command line

if __name__ == "__main__":
    unittest.main()
