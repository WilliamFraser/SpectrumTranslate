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
Unit Test for disciplefile file
"""

import disciplefile
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
            self.assertEqual(disciplefile._checkisvalidbytes(bytes(b"Test"),
                                                             0),
                             True)
            self.assertEqual(disciplefile._checkisvalidbytes(bytearray(
                                                             b"Test"), 0),
                             True)
            self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                              disciplefile._checkisvalidbytes, "Wrong", 0)
        else:
            self.assertEqual(disciplefile._checkisvalidbytes("Hello", 0), True)
            # 2to3 will complain but is ok as won't run in python 3
            self.assertEqual(disciplefile._checkisvalidbytes([long(1),
                                                              long(2)], 0),
                             True)
            # bytes is valid in python 2 as it looks like a string
            # so not checked
            self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                              disciplefile._checkisvalidbytes,
                              bytearray(b"Test"), 0)

        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          disciplefile._checkisvalidbytes, 1, 0)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          disciplefile._checkisvalidbytes, ["Wrong", "input"],
                          0)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          disciplefile._checkisvalidbytes, [0.1, 0.2], 0)
        self.assertEqual(disciplefile._checkisvalidbytes([1, 2], 0), True)

    def test_validbytestointlist(self):
        self.assertEqual(disciplefile._validbytestointlist([1, 2]), [1, 2])
        if(_PYTHON_VERSION_HEX > 0x03000000):
            self.assertEqual(disciplefile._validbytestointlist(bytearray(
                                                                   b"Test")),
                             [84, 101, 115, 116])
            self.assertEqual(disciplefile._validbytestointlist(bytes(b"Test")),
                             [84, 101, 115, 116])
        else:
            self.assertEqual(disciplefile._validbytestointlist("Test"),
                             [84, 101, 115, 116])

    def test_validateandconvertfilename(self):
        self.assertEqual(disciplefile._validateandconvertfilename(
                         [65, 66, 67]),
                         [65, 66, 67, 32, 32, 32, 32, 32, 32, 32])
        self.assertEqual(disciplefile._validateandconvertfilename("ABC"),
                         [65, 66, 67, 32, 32, 32, 32, 32, 32, 32])
        self.assertEqual(disciplefile._validateandconvertfilename(
                         ["A", "B", "C"]),
                         [65, 66, 67, 32, 32, 32, 32, 32, 32, 32])
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          disciplefile._validateandconvertfilename, [0.1, 0.2])
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          disciplefile._validateandconvertfilename, 0.1)
        if(_PYTHON_VERSION_HEX < 0x03000000):
            # 2to3 will complain but is ok as won't run in python 3
            self.assertEqual(disciplefile._validateandconvertfilename(
                             [long(65), long(66), long(67)]),
                             [65, 66, 67, 32, 32, 32, 32, 32, 32, 32])

    def test_GetDirectoryEntryPosition(self):
        entry = 1
        for track in range(4):
            for sector in range(1, 11):
                self.assertEqual(disciplefile.GetDirectoryEntryPosition(entry),
                                 (track, sector))
                entry += 1
                self.assertEqual(disciplefile.GetDirectoryEntryPosition(entry),
                                 (track, sector))
                entry += 1


class TestDiscipleFile(unittest.TestCase):
    def test_create(self):
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          disciplefile.DiscipleFile, [], 0)

        df = disciplefile.DiscipleFile([1, 2], 4)
        self.assertEqual(df.image, [1, 2])
        self.assertEqual(df.filenumber, 4)

    def test_getheadder(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getheadder(),
                         [1, 66, 65, 83, 73, 67, 32, 116, 101, 115, 116, 0, 1,
                          4, 1, 1] +
                         [0] * 195 +
                         [0, 190, 0, 203, 92, 78, 0, 255, 255] +
                         [0] * 36)

    def test_getfiledata(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getfiledata(),
                         _getfileaslist("basictest.dat"))
        self.assertEqual(df.getfiledata(wantheadder=True),
                         [0, 190, 0, 203, 92, 78, 0, 255, 255] +
                         _getfileaslist("basictest.dat"))

    def test_isempty(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertFalse(df.isempty())
        df = disciplefile.DiscipleFile(di, 10)
        self.assertTrue(df.isempty())

    def test_getsectorsused(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getsectorsused(), 1)
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getsectorsused(), 14)

    def test_getfilelength(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getfilelength(), 190)
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getfilelength(), 6912)

    def test_getfiletype(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getfiletype(), 1)
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getfiletype(), 3)
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getfiletype(), 2)
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getfiletype(), 7)
        df = disciplefile.DiscipleFile(di, 5)
        self.assertEqual(df.getfiletype(), 0)

    def test_getfiletypestring(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getfiletypestring(), "Basic")
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getfiletypestring(), "String Array")
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getfiletypestring(), "Number Array")
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getfiletypestring(), "SCREEN$")
        df = disciplefile.DiscipleFile(di, 5)
        self.assertEqual(df.getfiletypestring(), "Free/Erased")

    def test_getfiletypecatstring(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getfiletypecatstring(), "BAS")
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getfiletypecatstring(), "$.ARRAY")
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getfiletypecatstring(), "D.ARRAY")
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getfiletypecatstring(), "SCREEN$")
        df = disciplefile.DiscipleFile(di, 5)
        self.assertEqual(df.getfiletypecatstring(), "ERASED")

    def test_getfilename(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getfilename(), "BASIC test")
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getfilename(), "Array C   ")
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getfilename(), "Array X   ")
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getfilename(), "Screen    ")

    def test_getrawfilename(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getrawfilename(), [ord(x) for x in "BASIC test"])
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getrawfilename(), [ord(x) for x in "Array C   "])
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getrawfilename(), [ord(x) for x in "Array X   "])
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getrawfilename(), [ord(x) for x in "Screen    "])

    def test_getfiledetails(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getfiledetails(),
                         {'filenumber': 1,
                          'filetype': 1,
                          'filename': 'BASIC test',
                          'rawfilename': [ord(x) for x in "BASIC test"],
                          'filetypelong': 'Basic',
                          'filetypeshort': 'BAS',
                          'filelength': 190,
                          'sectors': 1,
                          'catextradata': '',
                          'autostartline': -1,
                          'variableoffset': 78})
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getfiledetails(),
                         {'filenumber': 2,
                          'filetype': 3,
                          'filename': 'Array C   ',
                          'rawfilename': [ord(x) for x in "Array C   "],
                          'filetypelong': 'String Array',
                          'filetypeshort': '$.ARRAY',
                          'filelength': 31,
                          'sectors': 1,
                          'catextradata': '',
                          'variableletter': 'C',
                          'arraydescriptor': 195,
                          'variablename': 'C$'})
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getfiledetails(),
                         {'filenumber': 3,
                          'filetype': 2,
                          'filename': 'Array X   ',
                          'rawfilename': [ord(x) for x in "Array X   "],
                          'filetypelong': 'Number Array',
                          'filetypeshort': 'D.ARRAY',
                          'filelength': 1005,
                          'sectors': 2,
                          'catextradata': '',
                          'variableletter': 'X',
                          'arraydescriptor': 152,
                          'variablename': 'X'})
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getfiledetails(),
                         {'filenumber': 4,
                          'filetype': 7,
                          'filename': 'Screen    ',
                          'rawfilename': [ord(x) for x in "Screen    "],
                          'filetypelong': 'SCREEN$',
                          'filetypeshort': 'SCREEN$',
                          'sectors': 14,
                          'filelength': 6912,
                          'catextradata': ''})
        df = disciplefile.DiscipleFile(di, 5)
        self.assertEqual(df.getfiledetails(),
                         {'filenumber': 5,
                          'filetype': 0,
                          'filename': '^00^00^00^00^00^00^00^00^00^00',
                          'rawfilename': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          'filetypelong': 'Free/Erased',
                          'filetypeshort': 'ERASED',
                          'sectors': 0,
                          'filelength': 0,
                          'catextradata': ''})

    def test_getfiledetailsstring(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getfiledetailsstring(),
                         '    1   BASIC test   1      BAS')
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getfiledetailsstring(),
                         '    2   Array C      1      $.ARRAY')
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getfiledetailsstring(),
                         '    3   Array X      2      D.ARRAY')
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getfiledetailsstring(),
                         '    4   Screen      14      SCREEN$')
        df = disciplefile.DiscipleFile(di, 5)
        self.assertEqual(df.getfiledetailsstring(), """\
    5   ^00^00^00^00^00^00^00^00^00^00   0      ERASED""")

    def test_getautostartline(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getautostartline(), -1)
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getautostartline(), -2)

    def test_getvariableoffset(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getvariableoffset(), 78)
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getvariableoffset(), -2)

    def test_getcodestart(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getcodestart(), -2)
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getcodestart(), 16384)

    def test_getvariableletter(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getvariableletter(), None)
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getvariableletter(), "C")
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getvariableletter(), "X")

    def test_getvariablename(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getvariablename(), None)
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getvariablename(), "C$")
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getvariablename(), "X")

    def test_getarraydescriptor(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getarraydescriptor(), -1)
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getarraydescriptor(), 195)
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getarraydescriptor(), 152)

    def test_getsnapshotregisters(self):
        # todo: check once have access to snapshot files
        pass

    def test__str__(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(str(df), '1   BASIC test   1      BAS')
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(str(df), '2   Array C      1      $.ARRAY')
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(str(df), '3   Array X      2      D.ARRAY')
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(str(df), '4   Screen      14      SCREEN$')
        df = disciplefile.DiscipleFile(di, 5)
        self.assertEqual(str(df), """\
5   ^00^00^00^00^00^00^00^00^00^00   0      ERASED""")

    def test_getdisciplefiledetails(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getdisciplefiledetails(), """\
filenumber: 1
File name: "BASIC test"
File type: 1 = Basic
File length: 190(BE)
Autostart: -1
Variable offfset: 78(4E)
file details:     1   BASIC test   1      BAS
directory entry address: T=0 S=1 offset=0
Number of sectors used: 1
Sector chain:  4;1(A000) 0;0""")
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getdisciplefiledetails(), """\
filenumber: 4
File name: "Screen    "
File type: 7 = SCREEN$
File length: 6912(1B00)
code start address: 16384(4000)
file details:     4   Screen      14      SCREEN$
directory entry address: T=0 S=2 offset=256
Number of sectors used: 14
Sector chain:  4;5(A800) 4;6(AA00) 4;7(AC00) 4;8(AE00) 4;9(B000) 4;10(B200) \
5;1(C800) 5;2(CA00) 5;3(CC00) 5;4(CE00) 5;5(D000) 5;6(D200) 5;7(D400) \
5;8(D600) 0;0""")


class TestDiscipleImage(unittest.TestCase):
    def test_create(self):
        di = disciplefile.DiscipleImage()
        self.assertEqual(di.ImageSource, "Undefined")
        self.assertEqual(di.ImageFormat, "Unknown")

        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        self.assertEqual(di.ImageSource, "FileName")
        self.assertEqual(di.ImageFormat, "Unknown")

    def test_setfile(self):
        di = disciplefile.DiscipleImage()
        imagefile = open(_TEST_DIRECTORY + "diskimagetest.mgt", "rb")
        di.setfile(imagefile, form="MGT")
        self.assertEqual(di.ImageSource, "File")
        self.assertEqual(di.ImageFormat, "MGT")

    def test_setfilename(self):
        di = disciplefile.DiscipleImage()
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.setfilename,  "I don't exist")

        di.setfilename(_TEST_DIRECTORY + "diskimagetest.mgt", "IMG")
        self.assertEqual(di.ImageSource, "FileName")
        self.assertEqual(di.ImageFormat, "IMG")

    def test_setbytes(self):
        di = disciplefile.DiscipleImage()
        di.setbytes(bytes(b"ABC"))
        self.assertEqual(di.ImageSource, "Bytes")
        self.assertEqual(di.bytedata, [65, 66, 67])

    def test_setimageformat(self):
        di = disciplefile.DiscipleImage()
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.setimageformat,  "invalid format")

        di.setimageformat("MGT")
        self.assertEqual(di.ImageFormat, "MGT")

    def test_get_offset_and_bit_from_track_and_sector(self):
        di = disciplefile.DiscipleImage()
        self.assertEqual(di.get_offset_and_bit_from_track_and_sector(4, 1),
                         (0, 1))
        self.assertEqual(di.get_offset_and_bit_from_track_and_sector(128, 3),
                         (95, 4))

    def test_guessimageformat(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        di.guessimageformat()
        self.assertEqual(di.ImageFormat, "MGT")

        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.img")
        di.guessimageformat()
        self.assertEqual(di.ImageFormat, "IMG")

    def test_getsectorposition(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.getsectorposition, 0, 0)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.getsectorposition, 0, 11)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.getsectorposition, 80, 1)
        self.assertEqual(di.getsectorposition(0, 1), 0)
        self.assertEqual(di.getsectorposition(0, 2), 512)
        self.assertEqual(di.getsectorposition(1, 1), 512*20)
        self.assertEqual(di.getsectorposition(128, 1), 512*10)
        self.assertEqual(di.getsectorposition(0, 1, 1), 512*10)

        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.img")
        self.assertEqual(di.getsectorposition(1, 1), 512*10)
        self.assertEqual(di.getsectorposition(128, 1), 512*80*10)
        self.assertEqual(di.getsectorposition(0, 1, 1), 512*80*10)

    def test_getsector(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        self.assertEqual(di.getsector(4, 1),
                         [0, 190, 0, 203, 92, 78, 0, 255, 255] +
                         _getfileaslist("basictest.dat") + [0] * 313)

        # test for reading uninitiated image
        di = disciplefile.DiscipleImage()
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.getsector, 0, 1)

    def compareimages(self, img1, img2):
        # function to return different sectors between 2 images
        diff = []
        for f in range(2):
            for t in range(80):
                for s in range(1, 11):
                    d1 = img1.getsector(f * 128 + t, s)
                    d2 = img2.getsector(f * 128 + t, s)
                    if(d1 != d2):
                        diff += [[f * 128 + t, s, d1, d2]]

        return diff

    def test_writesector(self):
        # create copy of file image to play with
        fi = open(_TEST_DIRECTORY + "diskimagetest.mgt", "rb")
        fo = open(_TEST_DIRECTORY + "diskimagecopy.mgt", "wb")
        fo.write(fi.read())
        fo.close()
        fi.close()

        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagecopy.mgt")
        # ensure that image opened with incorrect write permission fails
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writesector, [0] * 512, 0, 1)

        # test write to image in file
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagecopy.mgt",
                                        accessmode="rb+")

        # test sector data size
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writesector, [0], 0, 1)

        # write data to test
        di.writesector([0] * 512, 0, 1)
        di.writesector([1] * 512, 4, 2)

        diff = self.compareimages(di, disciplefile.DiscipleImage(
                                  _TEST_DIRECTORY + "diskimagetest.mgt"))
        # check changes have happened
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0][0:3], [0, 1, [0] * 512])
        self.assertEqual(diff[1][0:3], [4, 2, [1] * 512])

        # tidy up
        os_remove(_TEST_DIRECTORY + "diskimagecopy.mgt")

        # test write to image in internal byte list
        # undefined image. Will be populated with list when first write happens
        di1 = disciplefile.DiscipleImage()
        di2 = disciplefile.DiscipleImage()

        di1.writesector([2] * 512, 129, 10)
        di2.writesector([3] * 512, 10, 10)

        diff = self.compareimages(di1, di2)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0], [10, 10, [0] * 512, [3] * 512])
        self.assertEqual(diff[1], [129, 10, [2] * 512, [0] * 512])

    def test_deleteentry(self):
        # create memory copy to play with
        di = disciplefile.DiscipleImage()
        fi = open(_TEST_DIRECTORY + "diskimagetest.mgt", "rb")
        di.setbytes(fi.read())
        fi.close()

        # test invalid position values
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.deleteentry, 0)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.deleteentry, 81)

        # test delete entry in 2nd half of directory sector
        di.deleteentry(2)
        di2 = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0][:2], [0, 1])
        self.assertEqual(diff[0][3][:256], diff[0][2][:256])
        self.assertEqual(diff[0][3][257:], diff[0][2][257:])
        self.assertNotEqual(diff[0][3][256], diff[0][2][256])
        self.assertEqual(diff[0][2][256], 0)

        # reset image
        fi = open(_TEST_DIRECTORY + "diskimagetest.mgt", "rb")
        di.setbytes(fi.read())
        fi.close()

        # test delete entry in 1st half of directory sector
        di.deleteentry(3)
        di2 = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0][:2], [0, 2])
        self.assertEqual(diff[0][3][1:], diff[0][2][1:])
        self.assertNotEqual(diff[0][3][0], diff[0][2][0])
        self.assertEqual(diff[0][2][0], 0)

    def test_isimagevalid(self):
        di = disciplefile.DiscipleImage()
        # ensure fails with undefined source
        self.assertFalse(di.isimagevalid())
        # ensure fails with unknown format
        di.ImageSource = "Bytes"
        self.assertFalse(di.isimagevalid())
        # ensure fails with wrong byte size
        di.setbytes([1])
        self.assertFalse(di.isimagevalid())
        # ensure fails with bad data
        di.setbytes([1] * 819200)
        self.assertFalse(di.isimagevalid())

        # create memory copy to play with
        fi = open(_TEST_DIRECTORY + "diskimagetest.mgt", "rb")
        imagedata = fi.read()
        fi.close()
        di = disciplefile.DiscipleImage()
        di.setbytes(imagedata)

        # ensure known valid image works
        self.assertTrue(di.isimagevalid())

        # now break image and test
        # have incorrect file type
        sector = di.getsector(0, 1)
        di.writesector([12] + sector[1:], 0, 1)
        self.assertFalse(di.isimagevalid())
        # corrupt FAT table
        di.writesector(sector[:271] + [3] + sector[272:], 0, 1)
        self.assertFalse(di.isimagevalid())
        # sector not matching sectors owned
        di.writesector(sector[:15] + [2] + sector[16:], 0, 1)
        self.assertFalse(di.isimagevalid())
        # sector map not matching number of sectors used
        di.writesector(sector[:15] + [3] + sector[16:], 0, 1)
        self.assertFalse(di.isimagevalid())
        # number of sectors not matching file size
        di.writesector(sector[:212] + [10, 10] + sector[214:], 0, 1)
        self.assertFalse(di.isimagevalid())
        # premature file chain end
        di.writesector(sector, 0, 1)
        di.writesector([0] * 512, 4, 5)
        self.assertFalse(di.isimagevalid(True))
        # invalid sector in file chain
        di.writesector([0] * 510 + [255, 255], 4, 5)
        self.assertFalse(di.isimagevalid(True))
        # sector in file chain not owned by file
        di.writesector([0] * 510 + [4, 1], 4, 5)
        self.assertFalse(di.isimagevalid(True))
        # track & sector of last sector in file not 0, 0
        di.writesector([0] * 510 + [4, 6], 4, 5)
        di.writesector([0] * 510 + [5, 9], 5, 8)
        self.assertFalse(di.isimagevalid(True))

    def test_writefile(self):
        di = disciplefile.DiscipleImage()
        # test write wrong headder size
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writefile, [0], [1], -1)
        # test write invalid file position
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writefile, [0] * 256, [1], 81)

        # create memory copy to play with
        fi = open(_TEST_DIRECTORY + "diskimagetest.mgt", "rb")
        imagedata = fi.read()
        fi.close()
        di = disciplefile.DiscipleImage()
        di.setbytes(imagedata)

        # test write to first empty slot with more than 1 sector's data
        di.writefile([1] * 256, [2] * 600, -1)
        # test write to specified slot
        di.writefile([3] * 256, [4] * 100, 2)
        # test data
        di2 = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        diff = self.compareimages(di, di2)
        # 5 sectors altered
        self.assertEqual(len(diff), 5)
        # check changes to directory entries
        self.assertEqual(diff[0][:2], [0, 1])
        self.assertEqual(diff[0][2][256:], [3] * 11 + [0, 1, 4, 2, 2] +
                                           [0] * 194 + [3] * 46)
        self.assertEqual(diff[1][:2], [0, 3])
        self.assertEqual(diff[1][2][:256], [1] * 11 + [0, 2, 5, 9, 0, 0, 12] +
                                           [0] * 192 + [1] * 46)
        # test data saved
        self.assertEqual(diff[2][:3], [4, 2, [4] * 100 + [0] * 412])
        self.assertEqual(diff[3][:3], [5, 9, [2] * 510 + [5, 10]])
        self.assertEqual(diff[4][:3], [5, 10, [2] * 90 + [0] * 422])

        # test for corrupt FAT table
        di.setbytes(imagedata)
        sectordata = di.getsector(0, 1)
        # create fat table useing all sectors
        di.writesector(sectordata[:15] + [255] * 195 + sectordata[210:], 0, 1)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writefile, [0] * 256, [0] * 100, -1)

        # test for no empty headders
        di.setbytes(imagedata)
        # create lots of file entries
        for s in range(3, 11):
            di.writesector([1] + [0] * 255 + [1] + [0] * 255, 0, s)
        for t in range(1, 4):
            for s in range(1, 11):
                di.writesector([1] + [0] * 255 + [1] + [0] * 255, t, s)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writefile, [0] * 256, [0] * 100, -1)

        # test for not enough space on disk
        di = disciplefile.DiscipleImage()
        di.writesector([1] + [0] * 14 + [254] + [255] * 240 + [0] * 256, 0, 1)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writefile, [0] * 256, [0] * 600, -1)

    def test_fileindexfromname(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")
        self.assertEqual(di.fileindexfromname("BASIC test"), [1])
        self.assertEqual(di.fileindexfromname("BASIC test", True), [])
        self.assertEqual(di.fileindexfromname([0] * 10), [])
        self.assertEqual(di.fileindexfromname([0] * 10, True),
                         list(range(5, 81)))
        self.assertEqual(di.fileindexfromname("not exist"), [])

    def test_writebasicfile(self):
        di = disciplefile.DiscipleImage()
        di.setbytes([0] * 819200)
        # check data limit
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writebasicfile, [0] * (65535 - 23755 + 1), "Test")

        # get basic file data
        basicdata = _getfileaslist("basictest.dat")
        di.writebasicfile(basicdata, "Test")
        # create test compare image
        di2 = disciplefile.DiscipleImage()
        di2.setbytes([0] * 819200)

        # check changes have happened
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256],
                         [1] + [ord(x) for x in "Test      "] +
                         [0, 1, 4, 1, 1] + [0] * 195 +
                         [0, len(basicdata) & 255, len(basicdata) // 256,
                          0xCB, 0x5C, 78, 0, 0, 128] +
                         [0] * 36)
        self.assertEqual(diff[1][0:2], [4, 1])
        self.assertEqual(diff[1][2],
                         [0, len(basicdata) & 255, len(basicdata) // 256,
                          0xCB, 0x5C, 78, 0, 0, 128] + basicdata +
                         [0] * (503 - len(basicdata)))

        # check overwrite
        di.writebasicfile(basicdata, "Test", overwritename=True,
                          varposition=0xFFFF, autostartline=10)
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256],
                         [1] + [ord(x) for x in "Test      "] +
                         [0, 1, 4, 1, 1] + [0] * 195 +
                         [0, len(basicdata) & 255, len(basicdata) // 256,
                          0xCB, 0x5C, 0xFF, 0xFF, 10, 0] +
                         [0] * 36)

        # check autostartline sanity check
        di.writebasicfile(basicdata, "Test", overwritename=True,
                          varposition=0xFFFF, autostartline=10000)
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256],
                         [1] + [ord(x) for x in "Test      "] +
                         [0, 1, 4, 1, 1] + [0] * 195 +
                         [0, len(basicdata) & 255, len(basicdata) // 256,
                          0xCB, 0x5C, 0xFF, 0xFF, 0, 128] +
                         [0] * 36)

    def test_writecodefile(self):
        di = disciplefile.DiscipleImage()
        di.setbytes([0] * 819200)
        # check data limit
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writecodefile, [0] * 65536, "Test")

        # create test compare image
        di2 = disciplefile.DiscipleImage()
        di2.setbytes([0] * 819200)

        data = [1] * 100
        di.writecodefile(data, "Test")

        # check changes have happened
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256],
                         [4] + [ord(x) for x in "Test      "] +
                         [0, 1, 4, 1, 1] + [0] * 195 +
                         [3, 100, 0, 0, 0, 0, 0, 0, 0] +
                         [0] * 36)
        self.assertEqual(diff[1][0:2], [4, 1])
        self.assertEqual(diff[1][2],
                         [3, 100, 0, 0, 0, 0, 0, 0, 0] + [1] * 100 + [0] * 403)

        # check overwrite, and aditional parameters
        di.writecodefile(data, "Test", overwritename=True,
                         codestartaddress=0x1234, coderunaddress=0x5678)
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256],
                         [4] + [ord(x) for x in "Test      "] +
                         [0, 1, 4, 1, 1] + [0] * 195 +
                         [3, 100, 0, 0x34, 0x12, 0, 0, 0x78, 0x56] +
                         [0] * 36)

    def test_writearrayfile(self):
        di = disciplefile.DiscipleImage()
        di.setbytes([0] * 819200)
        # check data limit
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writearrayfile, [0] * 65536, "Test", 193)

        # create test compare image
        di2 = disciplefile.DiscipleImage()
        di2.setbytes([0] * 819200)

        stringdata = _getfileaslist("arraytest_char.dat")
        di.writearrayfile(stringdata, "Char", (ord("C") & 63) | 192)
        numberdata = _getfileaslist("arraytest_number.dat")
        di.writearrayfile(numberdata, "Number", (ord("N") & 63) | 128)

        # check changes have happened
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 4)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256],
                         [3] + [ord(x) for x in "Char      "] +
                         [0, 1, 4, 1, 1] + [0] * 195 +
                         [2, len(stringdata) & 255, len(stringdata) // 256,
                         0, 0, 195, 0, 0, 0] +
                         [0] * 36)
        self.assertEqual(diff[0][2][256:],
                         [2] + [ord(x) for x in "Number    "] +
                         [0, 2, 4, 2, 6] + [0] * 195 +
                         [1, len(numberdata) & 255, len(numberdata) // 256,
                          0, 0, 142, 0, 0, 0] +
                         [0] * 36)
        self.assertEqual(diff[1][0:2], [4, 1])
        self.assertEqual(diff[1][2],
                         [2, len(stringdata) & 255, len(stringdata) // 256,
                          0, 0, 195, 0, 0, 0] + stringdata +
                         [0] * (503 - len(stringdata)))
        self.assertEqual(diff[2][0:2], [4, 2])
        self.assertEqual(diff[2][2],
                         [1, len(numberdata) & 255, len(numberdata) // 256,
                          0, 0, 142, 0, 0, 0] + numberdata[:501] + [4, 3])
        self.assertEqual(diff[3][0:2], [4, 3])
        self.assertEqual(diff[3][2],
                         numberdata[501:] + [0] * (512 - 504))

    def test_writescreenfile(self):
        di = disciplefile.DiscipleImage()
        di.setbytes([0] * 819200)
        # check data limit
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writescreenfile, [0] * 10, "Test")

        # create test compare image
        di2 = disciplefile.DiscipleImage()
        di2.setbytes([0] * 819200)

        data = _getfileaslist("screentest.dat")
        di.writescreenfile(data, "Screen")

        # check changes have happened
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 15)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256],
                         [7] + [ord(x) for x in "Screen    "] +
                         [0, 14, 4, 1, 255, 63] + [0] * 194 +
                         [3, 0, 27, 0, 64, 0, 0, 0, 0] +
                         [0] * 36)

        # check overwrite
        di.writescreenfile(data, "Screen", overwritename=True)
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 15)

    def test_iteratedisciplefiles(self):
        di = disciplefile.DiscipleImage(_TEST_DIRECTORY + "diskimagetest.mgt")

        entries = [df for df in di.iteratedisciplefiles()]
        self.assertEqual(len(entries), 80)

# todo test command line

if __name__ == "__main__":
    unittest.main()
