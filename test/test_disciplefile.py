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
Unit Test for disciplefile file
"""

import unittest
import sys
import subprocess
import re
import os
import pycodestyle
from io import StringIO
# import modules from parent directory
import addparentmodules
import disciplefile
import spectrumtranslate


# change to current directory in cae being run from elsewhere
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def _getfile(name):
    with open(name, 'r') as f:
        return f.read()


CHAR80 = '\u2003'.encode('utf-8')
CHAR81 = '\u259D'.encode('utf-8')
CHAR82 = '\u2598'.encode('utf-8')
CHAR83 = '\u2580'.encode('utf-8')


def _getfileasbytes(name):
    with open(name, 'rb') as infile:
        return bytearray(infile.read())


class Testutilityfunctions(unittest.TestCase):
    def test_checkisvalidbytes(self):
        self.assertTrue(disciplefile._validateandpreparebytes(bytes(b"Test"),
                                                              0))
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          disciplefile._validateandpreparebytes, "Wrong", 0)

        self.assertTrue(disciplefile._validateandpreparebytes(bytearray(
                                                              b"Test"), 0))
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          disciplefile._validateandpreparebytes, 1, 0)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          disciplefile._validateandpreparebytes, ["Wrong",
                                                                  "input"],
                          0)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          disciplefile._validateandpreparebytes, [0.1, 0.2], 0)
        self.assertTrue(disciplefile._validateandpreparebytes([1, 2], 0))

    def test_validbytestointlist(self):
        self.assertEqual(disciplefile._validateandpreparebytes([1, 2], ""),
                         bytearray([1, 2]))
        self.assertEqual(disciplefile._validateandpreparebytes(bytearray(
                                                               b"Test"), ""),
                         bytearray([84, 101, 115, 116]))
        self.assertEqual(disciplefile._validateandpreparebytes(bytes(
                                                               b"Test"), ""),
                         bytearray([84, 101, 115, 116]))

    def test_validateandconvertfilename(self):
        self.assertEqual(disciplefile._validateandconvertfilename(
                         [65, 66, 67]),
                         bytearray([65, 66, 67, 32, 32, 32, 32, 32, 32, 32]))
        self.assertEqual(disciplefile._validateandconvertfilename("ABC"),
                         bytearray([65, 66, 67, 32, 32, 32, 32, 32, 32, 32]))
        self.assertEqual(disciplefile._validateandconvertfilename(
                         ["A", "B", "C"]),
                         bytearray([65, 66, 67, 32, 32, 32, 32, 32, 32, 32]))
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          disciplefile._validateandconvertfilename, [0.1, 0.2])
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          disciplefile._validateandconvertfilename, 0.1)

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

    def test_getheader(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getheader(), bytearray(
                         [1, 66, 65, 83, 73, 67, 32, 116, 101, 115, 116, 0, 1,
                          4, 1, 1] +
                         [0] * 195 +
                         [0, 190, 0, 203, 92, 78, 0, 255, 255] +
                         [0] * 36))

    def test_getfiledata(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getfiledata(), _getfileasbytes("basictest.dat"))
        self.assertEqual(df.getfiledata(wantheader=True),
                         bytearray([0, 190, 0, 203, 92, 78, 0, 255, 255]) +
                         _getfileasbytes("basictest.dat"))

    def test_isempty(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertFalse(df.isempty())
        df = disciplefile.DiscipleFile(di, 10)
        self.assertTrue(df.isempty())

    def test_getsectorsused(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getsectorsused(), 1)
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getsectorsused(), 14)

    def test_getfilelength(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getfilelength(), 190)
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getfilelength(), 6912)

    def test_getfiletype(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
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
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
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
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
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
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getfilename(), "BASIC test")
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getfilename(), "Array C   ")
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getfilename(), "Array X   ")
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getfilename(), "Screen    ")

    def test_getrawfilename(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getrawfilename(), bytearray(b'BASIC test'))
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getrawfilename(), bytearray(b'Array C   '))
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getrawfilename(), bytearray(b'Array X   '))
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getrawfilename(), bytearray(b'Screen    '))

    def test_getfiledetails(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getfiledetails(),
                         {'filenumber': 1,
                          'filetype': 1,
                          'filename': 'BASIC test',
                          'rawfilename': bytearray(b'BASIC test'),
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
                          'rawfilename': bytearray(b'Array C   '),
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
                          'rawfilename': bytearray(b'Array X   '),
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
                          'rawfilename': bytearray(b'Screen    '),
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
                          'rawfilename': bytearray([0] * 10),
                          'filetypelong': 'Free/Erased',
                          'filetypeshort': 'ERASED',
                          'sectors': 0,
                          'filelength': 0,
                          'catextradata': ''})

    def test_getfiledetailsstring(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
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
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getautostartline(), -1)
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getautostartline(), -2)

    def test_getvariableoffset(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getvariableoffset(), 78)
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getvariableoffset(), -2)

    def test_getcodestart(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getcodestart(), -2)
        df = disciplefile.DiscipleFile(di, 4)
        self.assertEqual(df.getcodestart(), 16384)

    def test_getvariableletter(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getvariableletter(), None)
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getvariableletter(), "C")
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getvariableletter(), "X")

    def test_getvariablename(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getvariablename(), None)
        df = disciplefile.DiscipleFile(di, 2)
        self.assertEqual(df.getvariablename(), "C$")
        df = disciplefile.DiscipleFile(di, 3)
        self.assertEqual(df.getvariablename(), "X")

    def test_getarraydescriptor(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
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
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
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
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.getdisciplefiledetails(), """\
filenumber: 1
File name: "BASIC test"
File type: 1 = Basic
File length: 190(BE)
Autostart: -1
Variable offset: 78(4E)
file details:     1   BASIC test   1      BAS
directory entry address: T=0 S=1 offset=0
Number of sectors used: 1
Sectors in FAT: 4;1
Sector chain: 4;1(A000) 0;0""")
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
Sectors in FAT: 4;5 4;6 4;7 4;8 4;9 4;10 5;1 5;2 5;3 5;4 5;5 5;6 5;7 5;8
Sector chain: 4;5(A800) 4;6(AA00) 4;7(AC00) 4;8(AE00) 4;9(B000) 4;10(B200) \
5;1(C800) 5;2(CA00) 5;3(CC00) 5;4(CE00) 5;5(D000) 5;6(D200) 5;7(D400) \
5;8(D600) 0;0""")

    def test_checkforfaults(self):
        # create memory copy to play with
        fi = open("diskimagetest.mgt", "rb")
        imagedata = fi.read()
        fi.close()
        di = disciplefile.DiscipleImage()
        di.setbytes(imagedata)

        # test return ok for valid file
        df = disciplefile.DiscipleFile(di, 1)
        self.assertEqual(df.checkforfaults(), None)

        # now break image and test
        # have incorrect file type
        sector = di.getsector(0, 1)
        di.writesector(bytearray([12]) + sector[1:], 0, 1)
        self.assertEqual(df.checkforfaults(), ["Contains invalid filetype"])
        # corrupt FAT table
        di.writesector(sector[:271] + bytearray([3]) + sector[272:], 0, 1)
        self.assertIn("File Allocation Table overlaps with other file(s)",
                      df.checkforfaults())
        # sector map not matching number of sectors used
        di.writesector(sector[:12] + bytearray([2]) + sector[13:], 0, 1)
        self.assertEqual(df.checkforfaults(), ["Number of sectors do not \
match number of sectors in FAT"])
        # number of sectors not matching file size
        di.writesector(sector[:212] + bytearray([10, 10]) + sector[214:], 0, 1)
        self.assertEqual(df.checkforfaults(),
                         ["Wrong length for number of sectors used"])
        # sector not matching sectors owned
        di.writesector(sector[:15] + bytearray([2]) + sector[16:], 0, 1)
        self.assertIn("Used sectors don't match FAT table entries",
                      df.checkforfaults())
        # test multiple results
        self.assertEqual(df.checkforfaults(),
                         ['File Allocation Table overlaps with other file(s)',
                          'Number of sectors do not match number of sectors \
in FAT',
                          'Wrong length for number of sectors used',
                          "Used sectors don't match FAT table entries",
                          'Mismatch between details and sector chain',
                          'Incorect FAT table'])
        # test for fast result
        self.assertEqual(df.checkforfaults(fast=True),
                         ["File Allocation Table overlaps with other file(s)"])
        # premature file chain end
        df = disciplefile.DiscipleFile(di, 4)
        di.writesector(sector, 0, 1)
        di.writesector([0] * 512, 4, 5)
        self.assertEqual(df.checkforfaults(),
                         ["Sector chain terminates early"])
        # invalid sector in file chain
        di.writesector([0] * 510 + [255, 255], 4, 5)
        self.assertEqual(df.checkforfaults(),
                         ["Invalid sector reference in chain"])
        # sector in file chain not owned by file
        di.writesector([0] * 510 + [4, 1], 4, 5)
        self.assertIn("Using sector not owned by this file",
                      df.checkforfaults())
        # track & sector of last sector in file not 0, 0
        di.writesector([0] * 510 + [4, 6], 4, 5)
        di.writesector([0] * 510 + [5, 9], 5, 8)
        self.assertEqual(df.checkforfaults(),
                         ["Mismatch between details and sector chain"])


class TestDiscipleImage(unittest.TestCase):
    def test_create(self):
        di = disciplefile.DiscipleImage()
        self.assertEqual(di.ImageSource, "Undefined")
        self.assertEqual(di.ImageFormat, "Unknown")

        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        self.assertEqual(di.ImageSource, "FileName")
        self.assertEqual(di.ImageFormat, "Unknown")

    def test_setfile(self):
        di = disciplefile.DiscipleImage()
        imagefile = open("diskimagetest.mgt", "rb")
        di.setfile(imagefile, form="MGT")
        self.assertEqual(di.ImageSource, "File")
        self.assertEqual(di.ImageFormat, "MGT")
        imagefile.close()

    def test_setfilename(self):
        di = disciplefile.DiscipleImage()
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.setfilename,  "I don't exist")

        di.setfilename("diskimagetest.mgt", "IMG")
        self.assertEqual(di.ImageSource, "FileName")
        self.assertEqual(di.ImageFormat, "IMG")

    def test_setbytes(self):
        di = disciplefile.DiscipleImage()
        di.setbytes(bytes(b"ABC"))
        self.assertEqual(di.ImageSource, "Bytes")
        self.assertEqual(di.bytedata, bytearray([65, 66, 67]))

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
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.get_offset_and_bit_from_track_and_sector, 3, 1)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.get_offset_and_bit_from_track_and_sector, 208, 1)

    def test_guessimageformat(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        di.guessimageformat()
        self.assertEqual(di.ImageFormat, "MGT")

        di = disciplefile.DiscipleImage("diskimagetest.img")
        di.guessimageformat()
        self.assertEqual(di.ImageFormat, "IMG")

    def test_getsectorposition(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
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

        di = disciplefile.DiscipleImage("diskimagetest.img")
        self.assertEqual(di.getsectorposition(1, 1), 512*10)
        self.assertEqual(di.getsectorposition(128, 1), 512*80*10)
        self.assertEqual(di.getsectorposition(0, 1, 1), 512*80*10)

    def test_getsector(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        self.assertEqual(di.getsector(4, 1), bytearray(
                         [0, 190, 0, 203, 92, 78, 0, 255, 255]) +
                         _getfileasbytes("basictest.dat") + bytearray(313))

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
                    if d1 != d2:
                        diff += [[f * 128 + t, s, d1, d2]]

        return diff

    def test_writesector(self):
        # create copy of file image to play with
        fi = open("diskimagetest.mgt", "rb")
        fo = open("diskimagecopy.mgt", "wb")
        fo.write(fi.read())
        fo.close()
        fi.close()

        di = disciplefile.DiscipleImage("diskimagecopy.mgt")
        # ensure that image opened with incorrect write permission fails
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writesector, [0] * 512, 0, 1)

        # test write to image in file
        di = disciplefile.DiscipleImage("diskimagecopy.mgt",
                                        accessmode="rb+")

        # test sector data size
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writesector, [0], 0, 1)

        # write data to test
        di.writesector([0] * 512, 0, 1)
        di.writesector([1] * 512, 4, 2)

        diff = self.compareimages(di, disciplefile.DiscipleImage(
                                  "diskimagetest.mgt"))
        # check changes have happened
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0][0:3], [0, 1, bytearray([0] * 512)])
        self.assertEqual(diff[1][0:3], [4, 2, bytearray([1] * 512)])

        # tidy up
        del (di)
        os.remove("diskimagecopy.mgt")

        # test write to image in internal byte list
        # undefined image. Will be populated with list when first write happens
        di1 = disciplefile.DiscipleImage()
        di2 = disciplefile.DiscipleImage()

        di1.writesector([2] * 512, 129, 10)
        di2.writesector([3] * 512, 10, 10)

        diff = self.compareimages(di1, di2)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0], [10, 10, bytearray([0] * 512),
                                   bytearray([3] * 512)])
        self.assertEqual(diff[1], [129, 10, bytearray([2] * 512),
                                   bytearray([0] * 512)])

    def test_deleteentry(self):
        # create memory copy to play with
        di = disciplefile.DiscipleImage()
        fi = open("diskimagetest.mgt", "rb")
        di.setbytes(fi.read())
        fi.close()

        # test invalid position values
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.deleteentry, 0)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.deleteentry, 81)

        # test delete entry in 2nd half of directory sector
        di.deleteentry(2)
        di2 = disciplefile.DiscipleImage("diskimagetest.mgt")
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0][:2], [0, 1])
        self.assertEqual(diff[0][3][:256], diff[0][2][:256])
        self.assertEqual(diff[0][3][257:], diff[0][2][257:])
        self.assertNotEqual(diff[0][3][256], diff[0][2][256])
        self.assertEqual(diff[0][2][256], 0)

        # reset image
        fi = open("diskimagetest.mgt", "rb")
        di.setbytes(fi.read())
        fi.close()

        # test delete entry in 1st half of directory sector
        di.deleteentry(3)
        di2 = disciplefile.DiscipleImage("diskimagetest.mgt")
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0][:2], [0, 2])
        self.assertEqual(diff[0][3][1:], diff[0][2][1:])
        self.assertNotEqual(diff[0][3][0], diff[0][2][0])
        self.assertEqual(diff[0][2][0], 0)

    def test_couldbeimage(self):
        di = disciplefile.DiscipleImage()
        # ensure fails with undefined source
        self.assertEqual(di.couldbeimage(), (False, "No image source defined"))
        # ensure fails with wrong byte image size
        di.setbytes([1])
        self.assertEqual(di.couldbeimage(), (False, "Image wrong size for 2 \
sided, 80 track, 10 sector per track, 512 byte sector image."))
        # ensure fails with wrong file image size
        di = disciplefile.DiscipleImage("code.dat")
        self.assertEqual(di.couldbeimage(), (False, "Image wrong size for 2 \
sided, 80 track, 10 sector per track, 512 byte sector image."))
        # ensure valid image works
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
        self.assertEqual(di.couldbeimage(), (True, None))

    def test_isimagevalid(self):
        di = disciplefile.DiscipleImage()
        # ensure fails with unknown format
        di.setbytes([1] * 819200)
        self.assertEqual(di.isimagevalid(), (False, "Can't work out image \
format"))

        # create memory copy to play with
        fi = open("diskimagetest.mgt", "rb")
        imagedata = fi.read()
        fi.close()
        di = disciplefile.DiscipleImage()
        di.setbytes(imagedata)

        # ensure known valid image works
        self.assertEqual(di.isimagevalid(), (True, None))

        # now break image and test
        # have incorrect file type
        sector = di.getsector(0, 1)
        di.writesector(bytearray([12]) + sector[1:], 0, 1)
        self.assertEqual(di.isimagevalid(), (False, "Contains file (number 1) \
with the error: Contains invalid filetype."))
        # track & sector of last sector in file not 0, 0
        di.writesector([0] * 510 + [4, 6], 4, 5)
        di.writesector([0] * 510 + [5, 9], 5, 8)
        self.assertEqual(di.isimagevalid(True), (False, 'Contains file \
(number 1) with the error: Contains invalid filetype.\nContains file (number \
4) with the error: Mismatch between details and sector chain.'))
        # test shallow (faster) test
        self.assertEqual(di.isimagevalid(False), (False, 'Contains file \
(number 1) with the error: Contains invalid filetype.'))

    def test_writefile(self):
        di = disciplefile.DiscipleImage()
        # test write wrong header size
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writefile, [0], [1], -1)
        # test write invalid file position
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writefile, [0] * 256, [1], 81)

        # create memory copy to play with
        fi = open("diskimagetest.mgt", "rb")
        imagedata = fi.read()
        fi.close()
        di = disciplefile.DiscipleImage()
        di.setbytes(imagedata)

        # test write to first empty slot with more than 1 sector's data
        di.writefile([1] * 256, [2] * 600, -1)
        # test write to specified slot
        di.writefile([3] * 256, [4] * 100, 2)
        # test data
        di2 = disciplefile.DiscipleImage("diskimagetest.mgt")
        diff = self.compareimages(di, di2)
        # 5 sectors altered
        self.assertEqual(len(diff), 5)
        # check changes to directory entries
        self.assertEqual(diff[0][:2], [0, 1])
        self.assertEqual(diff[0][2][256:], bytearray([3] * 11 +
                                                     [0, 1, 4, 2, 2] +
                                                     [0] * 194 + [3] * 46))
        self.assertEqual(diff[1][:2], [0, 3])
        self.assertEqual(diff[1][2][:256], bytearray([1] * 11 +
                                                     [0, 2, 5, 9, 0, 0, 12] +
                                                     [0] * 192 + [1] * 46))
        # test data saved
        self.assertEqual(diff[2][:3], [4, 2, bytearray([4] * 100 + [0] * 412)])
        self.assertEqual(diff[3][:3], [5, 9, bytearray([2] * 510 + [5, 10])])
        self.assertEqual(diff[4][:3], [5, 10, bytearray([2] * 90 + [0] * 422)])

        # test for corrupt FAT table
        di.setbytes(imagedata)
        sectordata = di.getsector(0, 1)
        # create fat table useing all sectors
        di.writesector(sectordata[:15] + bytearray([255]) * 195 +
                       sectordata[210:], 0, 1)
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writefile, [0] * 256, [0] * 100, -1)

        # test for no empty headers
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
        di = disciplefile.DiscipleImage("diskimagetest.mgt")
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
        basicdata = _getfileasbytes("basictest.dat")
        di.writebasicfile(basicdata, "Test")
        # create test compare image
        di2 = disciplefile.DiscipleImage()
        di2.setbytes([0] * 819200)

        # check changes have happened
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256], bytearray(
                         [1] + [ord(x) for x in "Test      "] +
                         [0, 1, 4, 1, 1] + [0] * 195 +
                         [0, len(basicdata) & 255, len(basicdata) // 256,
                          0xCB, 0x5C, 78, 0, 0, 128] +
                         [0] * 36))
        self.assertEqual(diff[1][0:2], [4, 1])
        self.assertEqual(diff[1][2], bytearray(
                         [0, len(basicdata) & 255, len(basicdata) // 256,
                          0xCB, 0x5C, 78, 0, 0, 128]) + basicdata +
                         bytearray([0] * (503 - len(basicdata))))

        # check overwrite
        di.writebasicfile(basicdata, "Test", overwritename=True,
                          varposition=0xFFFF, autostartline=10)
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256], bytearray(
                         [1] + [ord(x) for x in "Test      "] +
                         [0, 1, 4, 1, 1] + [0] * 195 +
                         [0, len(basicdata) & 255, len(basicdata) // 256,
                          0xCB, 0x5C, 0xFF, 0xFF, 10, 0] +
                         [0] * 36))

        # check autostartline sanity check
        di.writebasicfile(basicdata, "Test", overwritename=True,
                          varposition=0xFFFF, autostartline=10000)
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256], bytearray(
                         [1] + [ord(x) for x in "Test      "] +
                         [0, 1, 4, 1, 1] + [0] * 195 +
                         [0, len(basicdata) & 255, len(basicdata) // 256,
                          0xCB, 0x5C, 0xFF, 0xFF, 0, 128] +
                         [0] * 36))

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
        self.assertEqual(diff[0][2][:256], bytearray(
                         [4] + [ord(x) for x in "Test      "] +
                         [0, 1, 4, 1, 1] + [0] * 195 +
                         [3, 100, 0, 0, 0, 0, 0, 0, 0] +
                         [0] * 36))
        self.assertEqual(diff[1][0:2], [4, 1])
        self.assertEqual(diff[1][2], bytearray([3, 100, 0, 0, 0, 0, 0, 0, 0] +
                                               [1] * 100 + [0] * 403))

        # check overwrite, and aditional parameters
        di.writecodefile(data, "Test", overwritename=True,
                         codestartaddress=0x1234, coderunaddress=0x5678)
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256], bytearray(
                         [4] + [ord(x) for x in "Test      "] +
                         [0, 1, 4, 1, 1] + [0] * 195 +
                         [3, 100, 0, 0x34, 0x12, 0, 0, 0x78, 0x56] +
                         [0] * 36))

    def test_writearrayfile(self):
        di = disciplefile.DiscipleImage()
        di.setbytes([0] * 819200)
        # check data limit
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writearrayfile, [0] * 65536, "Test", 193)

        # create test compare image
        di2 = disciplefile.DiscipleImage()
        di2.setbytes([0] * 819200)

        stringdata = _getfileasbytes("arraytest_char.dat")
        di.writearrayfile(stringdata, "Char", (ord("C") & 63) | 192)
        numberdata = _getfileasbytes("arraytest_number.dat")
        di.writearrayfile(numberdata, "Number", (ord("N") & 63) | 128)

        # check changes have happened
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 4)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256], bytearray(
                         [3] + [ord(x) for x in "Char      "] +
                         [0, 1, 4, 1, 1] + [0] * 195 +
                         [2, len(stringdata) & 255, len(stringdata) // 256,
                          0, 0, 195, 0, 0, 0] +
                         [0] * 36))
        self.assertEqual(diff[0][2][256:], bytearray(
                         [2] + [ord(x) for x in "Number    "] +
                         [0, 2, 4, 2, 6] + [0] * 195 +
                         [1, len(numberdata) & 255, len(numberdata) // 256,
                          0, 0, 142, 0, 0, 0] +
                         [0] * 36))
        self.assertEqual(diff[1][0:2], [4, 1])
        self.assertEqual(diff[1][2], bytearray([2, len(stringdata) & 255,
                                                len(stringdata) // 256, 0, 0,
                                                195, 0, 0, 0]) +
                         stringdata + bytearray(503 - len(stringdata)))
        self.assertEqual(diff[2][0:2], [4, 2])
        self.assertEqual(diff[2][2], bytearray(
                         [1, len(numberdata) & 255, len(numberdata) // 256,
                          0, 0, 142, 0, 0, 0]) + numberdata[:501] +
                         bytearray([4, 3]))
        self.assertEqual(diff[3][0:2], [4, 3])
        self.assertEqual(diff[3][2], numberdata[501:] + bytearray(512 - 504))

    def test_writescreenfile(self):
        di = disciplefile.DiscipleImage()
        di.setbytes([0] * 819200)
        # check data limit
        self.assertRaises(spectrumtranslate.SpectrumTranslateError,
                          di.writescreenfile, [0] * 10, "Test")

        # create test compare image
        di2 = disciplefile.DiscipleImage()
        di2.setbytes([0] * 819200)

        data = _getfileasbytes("screentest.dat")
        di.writescreenfile(data, "Screen")

        # check changes have happened
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 15)
        self.assertEqual(diff[0][0:2], [0, 1])
        self.assertEqual(diff[0][2][:256], bytearray(
                         [7] + [ord(x) for x in "Screen    "] +
                         [0, 14, 4, 1, 255, 63] + [0] * 194 +
                         [3, 0, 27, 0, 64, 0, 0, 0, 0] +
                         [0] * 36))

        # check overwrite
        di.writescreenfile(data, "Screen", overwritename=True)
        diff = self.compareimages(di, di2)
        self.assertEqual(len(diff), 15)

    def test_iteratedisciplefiles(self):
        di = disciplefile.DiscipleImage("diskimagetest.mgt")

        entries = [df for df in di.iteratedisciplefiles()]
        self.assertEqual(len(entries), 80)


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
        output = self.runpycodestyle("../disciplefile.py", [])
        self.assertEqual(output, "",
                         "../disciplefile.py pep8 formatting errors:\n" +
                         output)

        output = self.runpycodestyle("test_disciplefile.py", [])
        self.assertEqual(output, "",
                         "test_disciplefile.py pep8 formatting errors:\n" +
                         output)


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

    def runtest(self, command, stdindata, wantbytearrayreturned=False):
        saved_output = sys.stdout
        saved_input = sys.stdin
        sys.stdin = Testcommandline.Mystdin(stdindata)
        output = Testcommandline.Mystdout()
        sys.stdout = output
        try:
            disciplefile._commandline(["x.py"] + command.split())

        finally:
            sys.stdout = saved_output
            sys.stdin = saved_input

        out = output.getvalue()
        if len(out) == 0 and len(output.buffer.bytedata) > 0:
            out = output.buffer.bytedata
        output.close()
        return out

    def setUp(self):
        # tidy up
        try:
            os.remove("temp.img")
        except FileNotFoundError:
            pass

        try:
            os.remove("temp.mgt")
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
        self.assertEqual(self.runtest("", ""), disciplefile.usage())
        self.assertEqual(self.runtest("help", ""), disciplefile.usage())

    def test_list(self):
        self.assertEqual(self.runtest("list -o diskimagetest.img", ""),
                         """\
  pos   filename  sectors   type
    1   BASIC test   1      BAS
    2   Array C      1      $.ARRAY
    3   Array X      2      D.ARRAY
    4   Screen      14      SCREEN$
""")

        self.assertEqual(self.runtest("list -oc diskimagetest.img", ""),
                         """\
  pos   filename  sectors   type
    1   BASIC test   1      BAS
    2   Array C      1      $.ARRAY
    3   Array X      2      D.ARRAY
    4   Screen      14      SCREEN$
786420 bytes free.
""")

        self.assertEqual(self.runtest("list -o diskimagetest.img", ""),
                         """\
  pos   filename  sectors   type
    1   BASIC test   1      BAS
    2   Array C      1      $.ARRAY
    3   Array X      2      D.ARRAY
    4   Screen      14      SCREEN$
""")

        self.assertEqual(self.runtest("list --details --listempty \
diskimagetest.img temp.txt", ""), "")
        self.assertEqual(_getfile("temp.txt"), """\
1	BASIC test	1	Basic	1	190	-1	78
2	Array C   	3	String Array	1	31	C	C$	195
3	Array X   	2	Number Array	2	1005	X	X	152
4	Screen    	7	SCREEN$	14	6912
5	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
6	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
7	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
8	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
9	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
10	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
11	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
12	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
13	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
14	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
15	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
16	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
17	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
18	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
19	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
20	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
21	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
22	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
23	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
24	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
25	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
26	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
27	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
28	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
29	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
30	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
31	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
32	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
33	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
34	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
35	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
36	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
37	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
38	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
39	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
40	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
41	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
42	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
43	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
44	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
45	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
46	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
47	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
48	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
49	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
50	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
51	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
52	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
53	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
54	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
55	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
56	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
57	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
58	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
59	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
60	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
61	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
62	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
63	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
64	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
65	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
66	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
67	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
68	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
69	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
70	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
71	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
72	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
73	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
74	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
75	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
76	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
77	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
78	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
79	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
80	^00^00^00^00^00^00^00^00^00^00	0	Free/Erased	0	0
""")
        # tidy up
        os.remove("temp.txt")

    def test_forceformat(self):
        self.assertEqual(self.runtest("list --forceinputformat IMG -o \
diskimagetest.img", ""),
                         """\
  pos   filename  sectors   type
    1   BASIC test   1      BAS
    2   Array C      1      $.ARRAY
    3   Array X      2      D.ARRAY
    4   Screen      14      SCREEN$
""")

        self.assertEqual(self.runtest("list --forceinputformat MGT \
diskimagetest.img temp.txt", ""), "")
        self.assertEqual(_getfileasbytes("temp.txt").replace(b'\r', b''),
                         bytearray(b"""\
  pos   filename  sectors   type
    1   BASIC test   1      BAS
    2   Array C      1      $.ARRAY
    3   Array X      2      D.ARRAY
    4   Screen      14      SCREEN$
   43   ^1F^00DEF FN \\NOT COPY COPY COPY ^03^02   3      D.ARRAY
   45   GO SUB ^03DEF FN \\^98COPY COPY COPY ^02^14  10      BAS
   46   COPY COPY """ + CHAR83 + b"""^1FCOPY COPY COPY """ + CHAR80 +
                                   b"""^19^9939321      None
   47   COPY COPY COPY """ + CHAR81 + b"""^0CTO TO TO """ + CHAR82 +
                                   b"""^0C52428      None
   48   TO TO """ + CHAR82 + b"""LTO TO TO """ + CHAR83 +
                                   b"""^19^9939321      None
   49   ^00^1B^00@COPY COPY COPY COPY ^00^00   0      $.ARRAY
   51   BBBBBBBBBB16962      D.ARRAY
   52   BBBBBBBBBB16962      D.ARRAY
   53   ~~~~~~~~~~32382      None
   54   BBBBBBBBBB16962      D.ARRAY
   55   BBBBBBBBBB16962      D.ARRAY
   56   BBBBBBBBBB16962      D.ARRAY
   59   ||||||||||31868      None
   60   BBBBBBBBBB16962      D.ARRAY
"""))

        self.assertEqual(self.runtest("create code --forceoutputformat IMG \
--filename TEST --origin 0x8000 screentest.dat temp.img", ""), "")
        di = disciplefile.DiscipleImage("temp.img")
        di.guessimageformat()
        self.assertEqual(di.ImageFormat, "IMG")

        self.assertEqual(self.runtest("create code --forceoutputformat MGT \
--filename TEST --origin 0x8000 screentest.dat temp.mgt", ""), "")
        di = disciplefile.DiscipleImage("temp.mgt")
        di.guessimageformat()
        self.assertEqual(di.ImageFormat, "MGT")

        # tidy up
        di = None
        os.remove("temp.txt")
        os.remove("temp.img")
        os.remove("temp.mgt")

    def test_delete(self):
        self.assertEqual(self.runtest("delete 1 diskimagetest.img temp.img",
                                      ""), "")

        self.assertEqual(self.runtest("list -o temp.img", ""),
                         """\
  pos   filename  sectors   type
    2   Array C      1      $.ARRAY
    3   Array X      2      D.ARRAY
    4   Screen      14      SCREEN$
""")
        # tidy up
        os.remove("temp.img")

        # create copy
        with open("temp.img", "wb") as f:
            f.write(_getfileasbytes("diskimagetest.img"))
        self.assertEqual(self.runtest("delete -s 1-2,0x4 temp.img temp.img",
                                      ""), "")
        self.assertEqual(self.runtest("list -o temp.img", ""),
                         """\
  pos   filename  sectors   type
    3   Array X      2      D.ARRAY
""")
        # tidy up
        os.remove("temp.img")

    def test_extract(self):
        self.assertEqual(self.runtest("extract 2 diskimagetest.img temp.bin",
                                      ""), "")
        self.assertEqual(_getfileasbytes("temp.bin"),
                         _getfileasbytes("arraytest_char.dat"))
        # tidy up
        os.remove("temp.bin")

    def test_copy(self):
        self.assertEqual(self.runtest("copy --pos 0x10-0x11 -s 2-3 \
diskimagetest.img temp.img", ""), "")
        self.assertEqual(self.runtest("list -o temp.img", ""),
                         """\
  pos   filename  sectors   type
   16   Array C      1      $.ARRAY
   17   Array X      2      D.ARRAY
""")
        # tidy up
        os.remove("temp.img")

        self.assertEqual(self.runtest("copy --pos 11-14 -s 1-2 \
diskimagetest.img temp.img", ""), "")
        self.assertEqual(self.runtest("list -o temp.img", ""),
                         """\
  pos   filename  sectors   type
   11   BASIC test   1      BAS
   12   Array C      1      $.ARRAY
""")
        # tidy up
        os.remove("temp.img")

        self.assertEqual(self.runtest("copy --pos 11-12 -s 1-4 \
diskimagetest.img temp.img", ""), "")
        self.assertEqual(self.runtest("list -o temp.img", ""),
                         """\
  pos   filename  sectors   type
    1   Array X      2      D.ARRAY
    2   Screen      14      SCREEN$
   11   BASIC test   1      BAS
   12   Array C      1      $.ARRAY
""")
        # tidy up
        os.remove("temp.img")

    def test_create(self):
        self.assertEqual(self.runtest("create basic --filename TEST \
--autostart 10 basictest.dat temp.img", ""), "")
        self.assertEqual(self.runtest("list -o temp.img", ""),
                         """\
  pos   filename  sectors   type
    1   TEST         1      BAS            10
""")

        self.assertEqual(self.runtest("create code --filename TEST \
--donotoverwriteexisting --origin 0x8000 screentest.dat temp.img", ""), "")
        self.assertEqual(self.runtest("list -o temp.img", ""),
                         """\
  pos   filename  sectors   type
    1   TEST         1      BAS            10
    2   TEST        14      CDE         32768,6912
""")

        self.assertEqual(self.runtest("create array --filename ARRAY -p 10 \
--arraytype string --arrayname S -i temp.img", "Test1\nTest2\nTest3"), "")
        self.assertEqual(self.runtest("list -o temp.img", ""),
                         """\
  pos   filename  sectors   type
    1   TEST         1      BAS            10
    2   TEST        14      CDE         32768,6912
   10   ARRAY        1      $.ARRAY
""")
        self.assertEqual(disciplefile.DiscipleFile(disciplefile.DiscipleImage(
            "temp.img"), 10).getfiledata(), bytearray(b"Test1\nTest2\nTest3"))

        self.assertEqual(self.runtest("create screen --filename SCR \
screentest.dat temp.img", ""), "")
        self.assertEqual(self.runtest("list -o temp.img", ""),
                         """\
  pos   filename  sectors   type
    1   TEST         1      BAS            10
    2   TEST        14      CDE         32768,6912
    3   SCR         14      SCREEN$
   10   ARRAY        1      $.ARRAY
""")

        # tidy up
        os.remove("temp.img")

    def test_test(self):
        self.assertEqual(self.runtest("test -o diskimagetest.img", ""),
                         "Valid Image file.\n")
        self.assertEqual(self.runtest("test -o -b diskimagetest.img", ""),
                         "")
        self.assertEqual(self.runtest("test -o --brief diskimagetest.img", ""),
                         "")

        # create copy
        with open("temp.img", "wb") as f:
            f.write(_getfileasbytes("diskimagetest.img"))
        di = disciplefile.DiscipleImage("temp.img", accessmode="rb+")

        # now break image and test
        # have incorrect file type
        sector = di.getsector(0, 1)
        di.writesector(bytearray([12]) + sector[1:], 0, 1)
        # track & sector of last sector in file not 0, 0
        di.writesector([0] * 510 + [4, 6], 4, 5)
        di.writesector([0] * 510 + [5, 9], 5, 8)

        self.assertEqual(self.runtest("test -o -b temp.img", ""),
                         'Invalid Image file.\n')
        self.assertEqual(self.runtest("test -o temp.img", ""),
                         """In MGT format, the errors were:
Contains file (number 1) with the errors: Contains invalid filetype. File \
Allocation Table overlaps with other file(s). Number of sectors do not match \
number of sectors in FAT. Mismatch between details and sector chain. Incorect \
FAT table.
Contains file (number 2) with the errors: File Allocation Table overlaps with \
other file(s). Number of sectors do not match number of sectors in FAT. Wrong \
length for number of sectors used. Mismatch between details and sector chain. \
Incorect FAT table.
Contains file (number 3) with the errors: File Allocation Table overlaps with \
other file(s). Number of sectors do not match number of sectors in FAT. Wrong \
length for number of sectors used. Mismatch between details and sector chain. \
Incorect FAT table.
Contains file (number 4) with the errors: File Allocation Table overlaps with \
other file(s). Number of sectors do not match number of sectors in FAT. Wrong \
length for number of sectors used. Mismatch between details and sector chain. \
Incorect FAT table.
Contains file (number 43) with the errors: File Allocation Table overlaps \
with other file(s). Number of sectors do not match number of sectors in FAT. \
Wrong length for number of sectors used. Invalid first sector.
Contains file (number 45) with the errors: File Allocation Table overlaps \
with other file(s). Number of sectors do not match number of sectors in FAT. \
Wrong length for number of sectors used. Invalid first sector.
Contains file (number 46) with the errors: Contains invalid filetype. File \
Allocation Table overlaps with other file(s). Number of sectors do not match \
number of sectors in FAT. Invalid first sector.
Contains file (number 47) with the errors: Contains invalid filetype. File \
Allocation Table overlaps with other file(s). Number of sectors do not match \
number of sectors in FAT. Invalid first sector.
Contains file (number 48) with the errors: Contains invalid filetype. File \
Allocation Table overlaps with other file(s). Number of sectors do not match \
number of sectors in FAT. Invalid first sector.
Contains file (number 51) with the errors: File Allocation Table overlaps \
with other file(s). Number of sectors do not match number of sectors in FAT. \
Wrong length for number of sectors used. Invalid first sector.
Contains file (number 52) with the errors: File Allocation Table overlaps \
with other file(s). Number of sectors do not match number of sectors in FAT. \
Wrong length for number of sectors used. Invalid first sector.
Contains file (number 53) with the errors: Contains invalid filetype. File \
Allocation Table overlaps with other file(s). Number of sectors do not match \
number of sectors in FAT. Invalid first sector.
Contains file (number 54) with the errors: File Allocation Table overlaps \
with other file(s). Number of sectors do not match number of sectors in FAT. \
Wrong length for number of sectors used. Invalid first sector.
Contains file (number 55) with the errors: File Allocation Table overlaps \
with other file(s). Number of sectors do not match number of sectors in FAT. \
Wrong length for number of sectors used. Invalid first sector.
Contains file (number 56) with the errors: Number of sectors do not match \
number of sectors in FAT. Wrong length for number of sectors used. Invalid \
first sector.
Contains file (number 59) with the errors: Contains invalid filetype. File \
Allocation Table overlaps with other file(s). Number of sectors do not match \
number of sectors in FAT. Invalid first sector.
Contains file (number 60) with the errors: File Allocation Table overlaps \
with other file(s). Number of sectors do not match number of sectors in FAT. \
Wrong length for number of sectors used. Invalid first sector.

In IMG format, the errors were:
Contains file (number 1) with the error: Contains invalid filetype.
""")
        # tidy up
        os.remove("temp.img")

    def checkinvalidcommand(self, command, message):
        try:
            disciplefile._commandline(["disciplefile.py"] + command.split())
            self.fail("No SpectrumTranslateError raised")
        except spectrumtranslate.SpectrumTranslateError as se:
            if se.value == message:
                return
            self.fail("Wrong exception message. Got:\n{0\nExpected:\n{}".
                      format(se.value, message))

    def test_invalidcommands(self):
        # incorrect action
        self.checkinvalidcommand("hello", "No command (list, extract, \
delete, copy, create, test, or help) specified as first argument.")
        # multiple actions
        self.checkinvalidcommand("create list",
                                 "Can't have multiple commands.")
        # no input file
        self.checkinvalidcommand("list", "No input file specified.")
        # no output file
        self.checkinvalidcommand("list infile", "No output file specified.")
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
        self.checkinvalidcommand("copy -s wrong in out", '"wrong" is invalid \
list of file indexes.')
        # invalid index to extract
        self.checkinvalidcommand("extract wrong in out", "wrong is not a \
valid index in the input file.")
        # invalid index to copy or delete
        self.checkinvalidcommand("copy wrong in out", "wrong is not a valid \
index in the input file.")
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
        self.checkinvalidcommand("extract 88 in out", "88 is not a valid \
entry number (should be 1 to 80).")
        # invalid index to copy & delete single or -s
        self.checkinvalidcommand("delete 80-88 in out", "[80, 81, 82, 83, 84, \
85, 86, 87, 88] is not a valid entry number (should be 1 to 80).")
        # invalid multiple flag
        self.checkinvalidcommand("list -xyz in out", "-x is not a recognised \
flag.")
        # invalid forceformat flag
        self.checkinvalidcommand("list -f WRONG in out", "WRONG is not a \
valid format type.")


if __name__ == "__main__":
    unittest.main()
