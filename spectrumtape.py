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
# Date: 16th April 2024

import spectrumtranslate
import sys
from io import IOBase
from math import ceil, log2
from os.path import isfile
# os.path imported elsewhere so only used for command line


def _isarray(x):
    return isinstance(x, (list, tuple))


def _isarrayofint(x):
    return _isarray(x) and all(isinstance(val, int) for val in x)


def _bytesarevalid(x):
    return isinstance(x, (bytes, bytearray)) or _isarrayofint(x)


def _sourceisvalid(s):
    return isinstance(s, IOBase) or _bytesarevalid(s)


def _validateandpreparebytes(x, m=""):
    if _bytesarevalid(x):
        return bytearray(x)

    raise spectrumtranslate.SpectrumTranslateError("{} needs to be a \
list or tuple of ints, or of type 'bytes' or 'bytearray'".format(m))


def _get_word(s):
    return int.from_bytes(s, 'little')


def word_to_bytes(w, n, signed=False):
    return w.to_bytes(n, 'little', signed=signed)


def _validateandconvertfilename(filename):
    # check filename is valid
    if _isarray(filename):
        # if is list of numbers convert to list of strings
        if _isarrayofint(filename):
            filename = bytearray(filename)

        # if there are only strings in the list then convert list to
        # a string
        if all(isinstance(x, str) for x in filename):
            filename = "".join(filename)

    if isinstance(filename, str):
        filename = bytearray(filename, "utf8")

    if not isinstance(filename, (bytes, bytearray)) or len(filename) > 10:
        raise spectrumtranslate.SpectrumTranslateError(
            "Filename must be a string, or list of ints or strings, of type \
'bytes' or 'bytearray' and of no more than 10 characters.")

    # return filename right padded with spaces
    return bytearray(filename) + bytearray([32] * (10 - len(filename)))


class SpectrumTapeBlock:
    """
    A class that holds information about a block of data from a Spectrum
    Tape file.  These can be used to extract data from a tzx or tap file.
    """

    def __init__(self, filePosition=0, blockPosition=None):
        """
        Creates a new TapeBlock object. filePosition is the offset to the
        data from the start of the stream.  You can safely put 0 here if
        this is of no use to you.  blockPosition is the index of this
        block in the container file.  None if not defined."""

        self.filePosition = filePosition
        self.blockPosition = blockPosition

    def isheader(self):
        """
        Is this Block object probably a header block?
        Header blocks come before the blocks holding the actual file
        data and contain information such as the filename, the file
        type, length, and other information depending on the file type.
        Returns True if this is probably a header, or False if probably
        not.
        """

        # default to not being a header
        return False

    def isdatablock(self):
        """
        Is this Block object probably a data block?
        Data blocks come after the Header blocks and contain the data
        of a file.
        Returns True if this is probably a data, or False if probably
        not.
        """

        # default to not being a datablock
        return False

    def getpayloadlength(self):
        """
        Returns the length of the data described by this block. Note
        that the actual length of a block is longer as it often contains
        details such as the length of a block, a flag, and a checksum.
        """

        # default to no data
        return 0

    def getpayloadstartoffset(self):
        """
        Returns the position in the file of the data described by this
        block.
        """

        # default to no data
        return 0

    def getpayload(self):
        """
        Returns the actual data that the block this describes would hold
        (without flag or checksum).
        Returns None if block doesn't have data in it.
        """

        return None

    def getfilename(self):
        """
        This gets the filename from a header block.  Note that the
        filename is always 10 spectrum characters long and will be
        padded with spaces to make the length up to 10 characters.  Also
        be aware that spectrum characters can contain control codes, or
        names of spectrum BASIC commands, so the resultant extracted
        string could be more than 10 characters in length.  Returns a
        String holding the filename, or None if this object isn't a
        header.
        """

        if not self.isheader():
            return None

        return spectrumtranslate.getspectrumstring(self.getpayload()[1:11])

    def getrawfilename(self):
        """This returns the 10 character file name as a bytearray.
        Returns None if not a header."""

        if not self.isheader():
            return None

        return self.getpayload()[1:11]

    def getfiletypestring(self):
        """
        What type of data does this header block describe.
        Return a string holding the file type, or None if it is not a
        header block.
        """

        if not self.isheader():
            return None

        filetype = self.getpayload()[0]

        if filetype == 0:
            return "Program"
        elif filetype == 1:
            return "Number array"
        elif filetype == 2:
            return "Character array"
        elif filetype == 3:
            return "Bytes"
        else:
            return "Unknown"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """

        if self.isheader():
            # work out any extra details for file
            extra = self.getfiletypestring()
            # get word at 13, and 14 in the data
            x = _get_word(self.getpayload()[13:15])
            filetype = self.getpayload()[0]
            # code file
            if filetype == 3:
                extra += " " + str(x) + "," + \
                         str(_get_word(self.getpayload()[11:13]))

            # program
            if filetype == 0 and x < 10000:
                extra += " Line:" + str(x)

            # array
            if filetype == 1 or filetype == 2:
                extra += " " + self.getheadervariablename()

            return "\"" + self.getfilename() + "\" " + extra

        if self.isdatablock():
            return "Flag:{}, block length:{}".format(
                self.flag, self.getpayloadlength())

        return ""

    def getheaderautostartline(self):
        """
        This returns the Autostart line number for a BASIC file header
        block.  Returns the line number to automatically start at when a
        BASIC file is loaded.  Returns None if no Autostart line is
        specified, or if this object is not a BASIC header block.
        """

        if not self.isheader() or self.getpayload()[0] != 0:
            return None

        start = _get_word(self.getpayload()[13:15])

        if start > 9999:
            return None

        return start

    def getheadervariableoffset(self):
        """
        This returns the offset to the start of the variable area in a
        BASIC file.  This is the same as the length in bytes of the
        BASIC program.  If this is the same as the length of the BASIC
        file then there are no variables saved with the program.
        Returns the byte offset to the start of the variables in the
        file, or None if this object is not a BASIC header block.  This
        is the same as the length of the BASIC program without any
        variables.
        """

        if not self.isheader() or self.getpayload()[0] != 0:
            return None

        return _get_word(self.getpayload()[15:17])

    def getheadercodestart(self):
        """
        This returns the address where a code file was saved from, and
        is the sugested address to load it to.  Returns the code address
        for a code block, or None if this object is not a code header
        block.
        """

        if not self.isheader() or self.getpayload()[0] != 3:
            return None

        return _get_word(self.getpayload()[13:15])

    def getheaderdescribeddatalength(self):
        """
        This returns the length of the data block that this Header
        block details.  Returns the data block block length, or None if
        this object is not a header block.
        """

        if not self.isheader():
            return None

        return _get_word(self.getpayload()[11:13])

    def getheadervariableletter(self):
        """"
        This returns the character of the variable described by an array
        Header block.  Returns the character value of a variable
        described by a header block, or None if this object is not a
        number or character array header block.
        """

        if not self.isheader() or (self.getpayload()[0] != 1 and
           self.getpayload()[0] != 2):
            return None

        return chr((self.getpayload()[14] & 127) | 64)

    def getheadervariablename(self):
        """
        This returns the name of the variable described by an array
        Header block.  This is the letter name of the array, followed
        by '$' if it is a character array.  Returns the name of a
        variable described by a header block, or None if this object is
        not a number or character array header block.
        """

        letter = self.getheadervariableletter()
        if not letter:
            return None

        return letter + ("$" if self.getpayload()[0] == 2 else "")

    def getheaderarraydescriptor(self):
        """
        This returns the array descriptor of an array Header block.
        The descriptor is an 8 bit number.  The lower 6 bits hold the
        ASCII lower 6 bits of the variable name (must be a letter of the
        alphabet).  Bits 6 and 7 describe what type of array the Header
        block describes.  They are 64 for a character array, 128 for a
        number array, and 192 for a string array.  Returns the array
        descriptor of the array described by a header block, or None if
        this object is not a number or character array header block.
        """

        if not self.isheader() or not self.getpayload()[0] in [1, 2]:
            return None

        return self.getpayload()[14]

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "Tape Block"

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        details = "{}\t{}\t".format(self.blockPosition, self.blocktype())

        if self.isheader():
            details += "Header\t{}\t".format(self.getfilename())
            filetype = self.getfiletypestring()
            if filetype == "Program":
                details += "Program\t{}\t{}\t{}".format(
                    self.getheaderdescribeddatalength(),
                    "" if self.getheaderautostartline() is None else
                    self.getheaderautostartline(),
                    self.getheadervariableoffset())
            elif filetype == "Bytes":
                details += "Bytes\t{}\t{}".format(
                    self.getheadercodestart(),
                    self.getheaderdescribeddatalength())
            elif filetype in ["Number array", "Character array"]:
                details += "{}\t{}\t{}\t{}\t{}".format(
                    filetype, self.getheaderdescribeddatalength(),
                    self.getheadervariableletter(),
                    self.getheadervariablename(),
                    self.getheaderarraydescriptor() & 192)
            else:
                details += "Unknown\t{}\t{}".format(
                    self.getpayload()[0],
                    self.getheaderdescribeddatalength())

        elif self.isdatablock():
            details += "Data\tFlag:{}\tLength:{}".format(
                self.flag, self.getpayloadlength())

        return details

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "SpectrumTapeBlock"

    def getpackagedforfile(self):
        """
        returns this TapeBlock packaged up as a bytearray for output to
        a file.
        """

        raise spectrumtranslate.SpectrumTranslateError("Generic Tape Block \
not useable in file. Use child classes instead")


class SpectrumTapBlock(SpectrumTapeBlock):
    """
    A class that holds information about a block of data from a Spectrum
    Tap file format.  These can be used to extract data from a tap file.
    """

    def __init__(self, flag=0, data=[], filePosition=0, blockPosition=None):
        """
        Creates a new TapBlock object. filePosition is the offset to the
        data from the start of the stream.  You can safely put 0 here if
        this is of no use to you.  data if defined has to be list or
        tuple of ints or longs, or of type 'bytes' or 'bytearray'.
        """

        super().__init__(filePosition, blockPosition)

        """
        The 8 bit data identifier value for the block.
        Typically it is 0 for a header and 255 for a data block, but
        custom load and save routines can use any value from 0 to 255.
        """
        if not isinstance(flag, int) or flag < 0 or flag > 255:
            raise spectrumtranslate.SpectrumTranslateError(
                "flag needs to be from 0 to 255 inclusive.")

        self.flag = flag

        # validate and prepare data
        """An array of bytes holding the data for the block."""
        self.data = _validateandpreparebytes(data, "data")

    def isheader(self):
        """
        Is this Block object probably a header block?
        Header blocks come before the blocks holding the actual file
        data and contain information such as the filename, the file
        type, length, and other information depending on the file type.
        Returns True if this is probably a header, or False if probably
        not.
        """

        return (self.flag == 0 and len(self.data) == 17)

    def isdatablock(self):
        """
        Is this Block object probably a data block?
        Data blocks come after the Header blocks and contain the data
        of a file.
        Returns True if this is probably a data, or False if probably
        not.
        """

        return len(self.data) > 0 and not self.isheader()

    def getpayloadlength(self):
        """
        Returns the length of the data described by this block. Note
        that the actual length of a block is longer as it often contains
        details such as the length of a block, a flag, and a checksum.
        """

        return len(self.data)

    def getpayload(self):
        """
        Returns the actual data that the block this describes would hold
        (without flag or checksum).
        Returns None if block doesn't have data in it.
        """

        return self.data

    def getpayloadstartoffset(self):
        """
        This returns the offset to the data of a block of a tap file in
        the origional stream.  This is only as acurate as the offset
        value passed in the contructor.  Returns the offset to the data
        in the origional stream used to create this object.
        """

        return self.filePosition + 3

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TAP Block"

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "Tap file block. Flag:{}, block length:{}".format(
            self.flag, self.getpayloadlength())

    def getpackagedforfile(self):
        """
        returns this TapBlock packaged up with length header, flag and
        checksum ready for saveing to a file.  Will be returned as a
        bytearray.
        """

        # work out length of data+flag+checksum
        length = len(self.data) + 2

        # work out checksum
        checksum = self.flag
        for i in self.data:
            checksum = checksum ^ i

        # merge it into a list, and return
        return word_to_bytes(length, 2) + bytearray([self.flag]) + \
            self.data + bytearray([checksum])


class SpectrumTZXStandardSpeedDataBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Standard Speed Data Block
    from a TZX file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, endPause=0, data=[], filePosition=0,
                 blockPosition=None):
        """
        Creates a new SpectrumTZXStandardSpeedDataBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        data if defined has to be list or tuple of ints or longs, or of
        type 'bytes' or 'bytearray'.
        """

        super().__init__(filePosition, blockPosition)

        # validate and prepare data
        """An array of bytes holding the data for the block."""
        self.data = _validateandpreparebytes(data, "data")

        self.endPause = endPause
        if len(data) > 0:
            self.flag = data[0]

    def isheader(self):
        """
        Is this Block object probably a header block?
        Header blocks come before the blocks holding the actual file
        data and contain information such as the filename, the file
        type, length, and other information depending on the file type.
        Returns True if this is probably a header, or False if probably
        not.
        """

        return len(self.data) == 19 and self.data[0] == 0

    def isdatablock(self):
        """
        Is this Block object probably a data block?
        Data blocks come after the Header blocks and contain the data
        of a file.
        Returns True if this is probably a data, or False if probably
        not.
        """

        return len(self.data) > 0 and not self.isheader()

    def getpayload(self):
        """
        Returns the actual data that the block this describes would hold
        (without flag or checksum).
        Returns None if block doesn't have data in it.
        """

        return self.data[1: -1]

    def getpayloadlength(self):
        """
        Returns the length of the data described by this block. Note
        that the actual length of a block is longer as it often contains
        details such as the length of a block, a flag, and a checksum.
        """

        return len(self.data) - 2

    def getpayloadstartoffset(self):
        """
        This returns the offset to the data of a block of a tzx file in
        the origional stream.  This is only as acurate as the offset
        value passed in the contructor.  Returns the offset to the data
        in the origional stream used to create this object.
        """

        return self.filePosition + 6

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Standard Speed"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """
        return super().getblockinfo() + \
            " pause after:{}ms".format(self.endPause)

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + \
            "\tpause after:{}ms".format(self.endPause)

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Standard Speed Data Block. Flag:{}, block length:{}, \
pause afterwards: {}ms".format(self.flag, self.getpayloadlength(),
                               self.endPause)

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x10]) + \
            word_to_bytes(self.endPause, 2) + \
            word_to_bytes(len(self.data), 2) + self.data


class SpectrumTZXTurboSpeedDataBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Turbo Speed Data Block from
    a TZX file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, endPause=0, data=[], lenPilotPulse=2168,
                 lenSyncPulse1=667, lenSyncPulse2=735, lenZeroPulse=855,
                 lenOnePulse=1710, lenPilotTone=3223,
                 lastByteUsedBits=8, filePosition=0,
                 blockPosition=None):
        """
        Creates a new SpectrumTZXTurboSpeedDataBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        data if defined has to be list or tuple of ints or longs, or of
        type 'bytes' or 'bytearray'.
        """

        super().__init__(filePosition, blockPosition)

        # validate and prepare data
        """An array of bytes holding the data for the block."""
        self.data = _validateandpreparebytes(data, "data")

        self.endPause = endPause
        self.lenPilotPulse = lenPilotPulse
        self.lenSyncPulse1 = lenSyncPulse1
        self.lenSyncPulse2 = lenSyncPulse2
        self.lenZeroPulse = lenZeroPulse
        self.lenOnePulse = lenOnePulse
        self.lenPilotTone = lenPilotTone
        self.lastByteUsedBits = lastByteUsedBits
        if len(data) > 0:
            self.flag = data[0]

    def isheader(self):
        """
        Is this Block object probably a header block?
        Header blocks come before the blocks holding the actual file
        data and contain information such as the filename, the file
        type, length, and other information depending on the file type.
        Returns True if this is probably a header, or False if probably
        not.
        """

        return (len(self.data) == 19 and self.data[0] == 0)

    def isdatablock(self):
        """
        Is this Block object probably a data block?
        Data blocks come after the Header blocks and contain the data
        of a file.
        Returns True if this is probably a data, or False if probably
        not.
        """

        return len(self.data) > 0 and not self.isheader()

    def getpayloadlength(self):
        """
        Returns the length of the data described by this block. Note
        that the actual length of a block is longer as it often contains
        details such as the length of a block, a flag, and a checksum.
        """

        return len(self.data) - 2

    def getpayload(self):
        """
        Returns the actual data that the block this describes would hold
        (without flag or checksum).
        Returns None if block doesn't have data in it.
        """

        return self.data[1: -1]

    def getpayloadstartoffset(self):
        """
        This returns the offset to the data of a block of a tap file in
        the origional stream.  This is only as acurate as the offset
        value passed in the contructor.  Returns the offset to the data
        in the origional stream used to create this object.
        """

        return self.filePosition + 20

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Turbo Speed"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """
        return super().getblockinfo() + " pause after:{}ms".format(
            self.endPause)

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\tpause after:{}ms".format(
            self.endPause)

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Turbo Speed Data Block. Flag:{}, block length:{}, pause \
afterwards: {}ms".format(self.flag, self.getpayloadlength(), self.endPause)

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x11]) + \
            word_to_bytes(self.lenPilotPulse, 2) + \
            word_to_bytes(self.lenSyncPulse1, 2) + \
            word_to_bytes(self.lenSyncPulse2, 2) + \
            word_to_bytes(self.lenZeroPulse, 2) + \
            word_to_bytes(self.lenOnePulse, 2) + \
            word_to_bytes(self.lenPilotTone, 2) + \
            word_to_bytes(self.lastByteUsedBits, 1) + \
            word_to_bytes(self.endPause, 2) + \
            word_to_bytes(len(self.data), 3) + self.data


class SpectrumTZXPureToneBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Pure Tone Block from a TZX
    file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, lenPulse, numberOfPulses, filePosition=0,
                 blockPosition=None):
        """
        Creates a new SpectrumTZXPureToneBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        self.lenPulse = lenPulse
        self.numberOfPulses = numberOfPulses

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Pure Tone"

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\tPulse Length:{}\tNumber of \
Pulses:{}".format(self.lenPulse, self.numberOfPulses)

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Pure Tone Block. Pulse Length:{}, Number of \
Pulses:{}".format(self.lenPulse, self.numberOfPulses)

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x12]) + \
            word_to_bytes(self.lenPilot, 2) + \
            word_to_bytes(self.numberOfPulses, 2)


class SpectrumTZXPulseSequenceBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Pulse Sequence Block from a
    TZX file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, pulses, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXPulseSequenceBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        if not _isarrayofint(pulses):
            raise spectrumtranslate.SpectrumTranslateError(
                "Pulses needs to be a list of numbers.")

        self.pulses = pulses

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Pulse Sequence"

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\tPulse Sequence Length:{}".format(
            self.pulses)

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Pulse Sequence Block. Pulse Sequence Length:{}".format(
            len(self.pulses))

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x13]) + \
            word_to_bytes(len(self.pulses), 1) + self.pulses


class SpectrumTZXPureDataBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Pure Data Block from a TZX
    file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, endPause=0, data=[], lenZeroPulse=855,
                 lenOnePulse=1710, lastByteUsedBits=8, filePosition=0,
                 blockPosition=None):
        """
        Creates a new SpectrumTZXPureDataBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        # validate and prepare data
        """An array of bytes holding the data for the block."""
        self.data = _validateandpreparebytes(data, "data")

        self.endPause = endPause
        self.lenZeroPulse = lenZeroPulse
        self.lenOnePulse = lenOnePulse
        self.lastByteUsedBits = lastByteUsedBits
        if len(data) > 0:
            self.flag = data[0]

    def isheader(self):
        """
        Is this Block object probably a header block?
        Header blocks come before the blocks holding the actual file
        data and contain information such as the filename, the file
        type, length, and other information depending on the file type.
        Returns True if this is probably a header, or False if probably
        not.
        """

        return (len(self.data) == 19 and self.data[0] == 0)

    def isdatablock(self):
        """
        Is this Block object probably a data block?
        Data blocks come after the Header blocks and contain the data
        of a file.
        Returns True if this is probably a data, or False if probably
        not.
        """

        return len(self.data) > 0 and not self.isheader()

    def getpayloadlength(self):
        """
        Returns the length of the data described by this block. Note
        that the actual length of a block is longer as it often contains
        details such as the length of a block, a flag, and a checksum.
        """

        return len(self.data) - 2

    def getpayload(self):
        """
        Returns the actual data that the block this describes would hold
        (without flag or checksum).
        Returns None if block doesn't have data in it.
        """

        return self.data[1: -1]

    def getpayloadstartoffset(self):
        """
        This returns the offset to the data of a block of a tap file in
        the origional stream.  This is only as acurate as the offset
        value passed in the contructor.  Returns the offset to the data
        in the origional stream used to create this object.
        """

        return self.filePosition + 12

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Pure Data"

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Pure Data Block. Flag:{}, block length:{}, pause \
afterwards: {}ms".format(self.flag, self.getpayloadlength(), self.endPause)

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x14]) + \
            word_to_bytes(self.lenZeroPulse, 2) + \
            word_to_bytes(self.lenOnePulse, 2) + \
            word_to_bytes(self.lastByteUsedBits, 1) + \
            word_to_bytes(self.endPause, 2) + \
            word_to_bytes(len(self.data), 3) + self.data


class SpectrumTZXDirectRecordingBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Direct Recording Block from a
    TZX file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, TPerSample, lastByteUsedBits=8, endPause=0,
                 sampleData=[], filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXDirectRecordingBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        # validate and prepare data
        """An array of bytes holding the data for the block."""
        self.sampleData = _validateandpreparebytes(sampleData, "sampleData")

        self.endPause = endPause
        self.TPerSample = TPerSample
        self.lastByteUsedBits = lastByteUsedBits

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Direct Recording"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """
        return super().getblockinfo() + " pause after:{}ms".format(
            self.endPause)

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\tpause after:{}ms".format(
            self.endPause)

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Direct Recording Block. Block length:{}, pause \
afterwards:{}ms".format(len(self.sampleData), self.endPause)

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x15]) + \
            word_to_bytes(self.TPerSample, 2) + \
            word_to_bytes(self.endPause, 2) + \
            word_to_bytes(self.lastByteUsedBits, 1) + \
            word_to_bytes(len(self.sampleData), 3) + self.sampleData


class SpectrumTZXCSWRecording(SpectrumTapeBlock):
    """
    A class that holds information about a CSW Recording Block from a
    TZX file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, sampleRate, compressionType, storedPulses, endPause=0,
                 CSWData=[], filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXCSWRecordingBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        # validate and prepare data
        """An array of bytes holding the data for the block."""
        self.CSWData = _validateandpreparebytes(CSWData, "CSWData")

        self.endPause = endPause
        self.samplesRate = sampleRate
        self.compressionType = compressionType
        self.storedPulses = storedPulses

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX CSW Recording"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """
        return super().getblockinfo() + " pause after:{}ms".format(
            self.endPause)

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\tpause after:{}ms".format(
            self.endPause)

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX CSW Recording Block. Block samples:{}, pause \
afterwards:{}ms".format(self.storedPulses, self.endPause)

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x18]) + \
            word_to_bytes(len(self.CSWData) + 10, 4) + \
            word_to_bytes(self.endPause, 2) + \
            word_to_bytes(self.sampleRate, 3) + \
            word_to_bytes(self.compressionType, 1) + \
            word_to_bytes(self.storedPulses, 4) + \
            self.CSWData


class SpectrumTZXGeneralizedDataBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Generalized Data Block for a
    TZX file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, symbolsInPilotBlock, pulsesPerPilotSymbol,
                 alphabetSizePilot, symbolsInDataBlock, pulsesPerDataSymbol,
                 alphabetSizeData, symbolDefinitionsPilot, dataStreamPilot,
                 symbolDefinitionsData, dataStreamData, endPause=0,
                 filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXGeneralizedDataBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        # validate and prepare data
        """An array of bytes holding the data for the block."""
        self.symbolDefinitionsPilot = symbolDefinitionsPilot
        self.dataStreamPilot = dataStreamPilot
        self.symbolDefinitionsData = symbolDefinitionsData
        self.dataStreamData = _validateandpreparebytes(dataStreamData,
                                                       "dataStreamData")
        self.endPause = endPause
        self.symbolsInPilotBlock = symbolsInPilotBlock
        self.pulsesPerPilotSymbol = pulsesPerPilotSymbol
        self.alphabetSizePilot = alphabetSizePilot
        self.symbolsInDataBlock = symbolsInDataBlock
        self.pulsesPerDataSymbol = pulsesPerDataSymbol
        self.alphabetSizeData = alphabetSizeData

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Generalized Data"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """
        return super().getblockinfo() + " pause after:{}ms".format(
            self.endPause)

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\tpause after:{}ms".format(
            self.endPause)

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Generalized Data Block. Block samples:{}, pause \
afterwards:{}ms".format(self.symbolsInDataBlock, self.endPause)

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        symdefasp = []
        for symdef in self.symbolDefinitionsPilot:
            symdefasp += [symdef[0]]
            for w in symdef[1]:
                symdefasp += word_to_bytes(w, 2)

        prle = []
        for d in self.dataStreamPilot:
            prle += [d[0]] + word_to_bytes(d[1], 2)

        symdefasd = []
        for symdef in self.symbolDefinitionsData:
            symdefasp += [symdef[0]]
            for w in symdef[1]:
                symdefasp += word_to_bytes(w, 2)

        lenstreams = len(symdefasp) + len(prle) + len(symdefasd) + \
            len(self.dataStreamData)

        return bytearray([0x19]) + \
            word_to_bytes(lenstreams + 14, 4) + \
            word_to_bytes(self.endPause, 2) + \
            word_to_bytes(self.symbolsInPilotBlock, 4) + \
            word_to_bytes(self.pulsesPerPilotSymbol, 1) + \
            word_to_bytes(self.alphabetSizePilot, 1) + \
            word_to_bytes(self.symbolsInDataBlock, 4) + \
            word_to_bytes(self.pulsesPerDataSymbol, 1) + \
            word_to_bytes(self.alphabetSizeData, 1) + \
            symdefasp + prle + symdefasd + self.dataStreamData


class SpectrumTZXPauseOrStopBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Pause or Stop Tape Block for
    a TZX file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, pause, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXPauseOrStopBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        self.pause = pause

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Pause or Stop"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """
        return super().getblockinfo() + " {}".format(
            "Stop the Tape" if self.pause == 0 else "Pause {}ms".format(
                self.pause))

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\t{}".format(
            "Stop the Tape" if self.pause == 0 else "Pause {}ms".format(
                self.pause))

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Pause or Stop Tape Block. {}".format(
            "Stop the Tape" if self.pause == 0 else "Pause {}ms".format(
                self.pause))

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x20]) + word_to_bytes(self.pause, 2)


class SpectrumTZXGroupStartBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Group Start Block for a TZX
    file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, groupName, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXGroupStartBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        self.groupName = groupName

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Group Start"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """
        return super().getblockinfo() + " Group Name:{}".format(
            self.groupName.decode("ascii"))

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\tGroup Name:{}".format(
            self.groupName.decode("ascii"))

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Group Start Block. Group Name: {}".format(
            self.groupName.decode("ascii"))

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x21]) + \
            word_to_bytes(len(self.groupName), 1) + self.groupName


class SpectrumTZXGroupEndBlock(SpectrumTapeBlock):
    """
    A class that indicates a Group End Block for a TZX file.  These can
    be used to extract data from a tzx file.
    """

    def __init__(self, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXGroupEndBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Group End"

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Group End Block."

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x22])


class SpectrumTZXJumpToBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Jump To Block for a TZX
    file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, relativeJumpValue, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXJumpToBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        self.relativeJumpValue = relativeJumpValue

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Jump To"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """

        return super().getblockinfo() + " {}".format(
            "" if self.blockPosition is None else "Jump To block:{}".format(
                self.blockPosition + self.relativeJumpValue))

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\t{}".format(
            "" if self.blockPosition is None else "Jump To block:{}".format(
                self.blockPosition + self.relativeJumpValue))

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Jump To Block.{}".format(
            "" if self.blockPosition is None else " Jump To block: {}".format(
                self.blockPosition + self.relativeJumpValue))

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x23]) + \
            word_to_bytes(self.relativeJumpValue, 2, True)


class SpectrumTZXLoopStartBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Loop Start Block for a TZX
    file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, repetitions, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXLoopStartBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        self.repetitions = repetitions

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Loop Start"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """

        return super().getblockinfo() + " Repetitions:{}".format(
            self.repetitions)

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\tRepetitions:{}".format(
            self.repetitions)

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Loop Start Block. Number of repetitions: {}".format(
            self.repetitions)

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x24]) + word_to_bytes(self.repetitions, 2)


class SpectrumTZXLoopEndBlock(SpectrumTapeBlock):
    """
    A class that indicates a Loop End Block for a TZX file.  These can
    be used to extract data from a tzx file.
    """

    def __init__(self, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXLoopEndBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Loop End"

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Loop End Block."

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x25])


class SpectrumTZXCallSequenceBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Call Sequence Block for a TZX
    file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, relativeBlockNumbers, filePosition=0,
                 blockPosition=None):
        """
        Creates a new SpectrumTZXCallSequenceBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        if not _isarrayofint(relativeBlockNumbers):
            raise spectrumtranslate.SpectrumTranslateError(
                "Call Sequence needs an array of relative offsets.")

        self.relativeBlockNumbers = relativeBlockNumbers

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Call Sequence"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """

        return super().getblockinfo()+" Calls to:[{}]".format(
            "" if self.blockPosition is None else ", ".join(
                [str(self.blockPosition + i)
                 for i in self.relativeBlockNumbers]))

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\tCalls to:[{}]".format(
            "" if self.blockPosition is None else ", ".join(
                [str(self.blockPosition + i)
                 for i in self.relativeBlockNumbers]))

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Call Sequence Block.{}".format(
            "" if self.blockPosition is None else "  Calls to {}.".format(
                ", ".join(
                    [str(self.blockPosition + i)
                     for i in self.relativeBlockNumbers])))

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        sequence = []
        for d in self.relativeBlockNumbers:
            sequence += word_to_bytes(d, 2, True)

        return bytearray([0x26]) + \
            word_to_bytes(len(self.relativeBlockNumbers), 2) + \
            sequence


class SpectrumTZXReturnFromSequenceBlock(SpectrumTapeBlock):
    """
    A class that indicates a Return From Sequence Block for a TZX file.
    These can be used to extract data from a tzx file.
    """

    def __init__(self, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXReturnFromSequenceBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Return from Sequence"

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Return From Sequence Block."

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x27])


class SpectrumTZXSelectBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Select Block for a TZX file.
    These can be used to extract data from a tzx file.
    """

    def __init__(self, selectOptions, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXSelectBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        if not _isarray(selectOptions):
            raise spectrumtranslate.SpectrumTranslateError(
                "Call Sequence needs an array of relative offsets.")

        self.selectOptions = selectOptions

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Select Block"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """

        return super().getblockinfo() + " Options: {}".format(", ".join(
            ['"{}" to block {}'.format(
                x[1].decode("ascii"), self.blockPosition + x[0])
             for x in self.selectOptions]))

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\tOptions:\t{}".format("\t".join(
            ['"{}" to block {}'.format(
                x[1].decode("ascii"), self.blockPosition + x[0])
             for x in self.selectOptions]))

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Select Block."

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        selects = []
        for s in self.selectOptions:
            selects += word_to_bytes(s[0], 2, True) + [len(s[1])] + s[1]

        return bytearray([0x28]) + \
            word_to_bytes(len(selects) + 1, 2) + \
            word_to_bytes(len(self.selectOptions), 1) + \
            selects


class SpectrumTZXStopTapeIf48KBlock(SpectrumTapeBlock):
    """
    A class that indicates a Stop Tape if 48K Block for a TZX file.
    These can be used to extract data from a tzx file.
    """

    def __init__(self, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXStopTapeIf48KBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Stop if 48K"

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Stop Tape If 48K Block."

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x2A]) + word_to_bytes(0, 4)


class SpectrumTZXSetSignalLevelBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Set Signal Level Block for a
    TZX file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, level, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXSelectBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        self.level = level

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Set Signal"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """

        return super().getblockinfo()+" Set Signal Level:{}".format(self.level)

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist()+"\tLevel:{}".format(self.level)

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Set Signal Level Block. Level: {}".format(self.level)

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x2B]) + \
            word_to_bytes(1, 4) + \
            word_to_bytes(self.level, 1)


class SpectrumTZXTextDescriptionBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Text Description Block for a
    TZX file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, description, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXTextDescriptionBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        self.description = description

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Description"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """

        return super().getblockinfo()+" Description:{:.20}".format(
            self.description.decode("ascii"))

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist()+"\tDescription:{}".format(
            self.description.decode("ascii"))

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Text Description Block. Description: '{}'".format(
            self.description.decode("ascii"))

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x30]) + \
            word_to_bytes(len(self.description), 1) + \
            self.description


class SpectrumTZXMessageBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Message Block for a
    TZX file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, message, duration, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXMessageBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        self.message = message
        self.duration = duration

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Message"

    def getblockinfo(self):
        """
        This gets a String respresentation of the file information.
        If the block describes a header, then the format of the returned
        string is similar to that displayed by the spectrum as it loads
        a file.
        For data block, the flag and length are returned.
        Other blocks have information about that type of block.
        """

        return super().getblockinfo() + " Message:{:.30}  message \
duration:{}s".format(self.message.decode("ascii"), self.duration)

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        return super().getdetailslist() + "\tMessage:{}\tduration:{}s".format(
            self.message.decode("ascii"), self.duration)

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Message Block. Message: {}, for {} seconds".format(
            self.message.decode("ascii"), self.duration)

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x31]) + \
            word_to_bytes(self.duration, 1) + \
            word_to_bytes(len(self.message), 1) + \
            self.message


class SpectrumTZXArchiveInfoBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Archive Info Block for a TZX
    file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, archiveInfoEntries, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXArchiveInfoBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        if not _isarray(archiveInfoEntries):
            raise spectrumtranslate.SpectrumTranslateError(
                "Archive Info needs an array of Info entries.")

        self.archiveInfoEntries = archiveInfoEntries

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Archive Info"

    def getdetailslist(self):
        """
        Returns info list for this block to display in a listing.
        """

        ids = {0: 'Full title', 1: 'Software house/publisher',
               2: 'Author(s)', 3: 'Year of publication',
               4: 'Language', 5: 'Game/utility type',
               6: 'Price', 7: 'Protection scheme/loader',
               8: 'Origin', 0xFF: 'Comment(s)'}
        info = [((ids[x[0]]+':{}') if x[0] in ids.keys() else '{}').format(
            x[1].decode("ascii")) for x in self.archiveInfoEntries]
        return super().getdetailslist()+"\t".join(info)

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Archive Info Block."

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        infos = []
        for i in self.archiveInfoEntries:
            infos += word_to_bytes(i[0], 1) + [len(i[1])] + i[1]

        return bytearray([0x32]) + \
            word_to_bytes(len(infos) + 1, 2) + \
            word_to_bytes(len(self.archiveInfoEntries), 1) + \
            infos


class SpectrumTZXHardwareTypeBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Hardware Type Block for a TZX
    file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, hardwareTypeEntries, filePosition=0,
                 blockPosition=None):
        """
        Creates a new SpectrumTZXHardwareTypeBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        if not _isarray(hardwareTypeEntries):
            raise spectrumtranslate.SpectrumTranslateError(
                "Hardware Type needs an array of harwdare type entries.")

        self.hardwareTypeEntries = hardwareTypeEntries

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Hardware Type"

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Hardware Type Block."

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        infos = []
        for i in self.hardwareTypeEntries:
            infos += i

        return bytearray([0x33]) + \
            word_to_bytes(len(self.hardwareTypeEntries), 1) + \
            infos


class SpectrumTZXCustomInfoBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Custom Info Block for a TZX
    file.  These can be used to extract data from a tzx file.
    """

    def __init__(self, identification, customInfo, filePosition=0,
                 blockPosition=None):
        """
        Creates a new SpectrumTZXCustomInfoBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)

        self.identification = identification
        self.customInfo = _validateandpreparebytes(customInfo, "customInfo")

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Custom Info"

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Custom Info Block. Identification: {}".format(
            self.identification.decode("ascii"))

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray([0x35]) + \
            self.identification + \
            word_to_bytes(len(self.customInfo), 4) + self.customInfo


class SpectrumTZXHeaderBlock(SpectrumTapeBlock):
    """
    A class that holds information about a Header Block for a TZX file.
    This is also used as a Glue Block when files are merged.
    These can be used to extract data from a tzx file.
    """

    def __init__(self, major, minor, filePosition=0, blockPosition=None):
        """
        Creates a new SpectrumTZXHeaderBlock object.
        filePosition is the offset to the data from the start of the
        stream.  You can safely put 0 here if this is of no use to you.
        """

        super().__init__(filePosition, blockPosition)
        self.major = major
        self.minor = minor

    def blocktype(self):
        """
        This returns the type for this block for use in listing.
        """

        return "TZX Header" if self.blockPosition == 0 else "TZX Glue Block"

    def __str__(self):
        """Returns a basic String summary of the Block object."""

        return "TZX Header" if self.blockPosition == 0 else "TZX Glue Block"

    def getpackagedforfile(self):
        """
        returns this TzxBlock packaged up ready for saveing to a file.
        Will be returned as a bytearray.
        """

        return bytearray(b'ZXTape!\x1a') + \
            word_to_bytes(self.major, 1) + \
            word_to_bytes(self.minor, 1)


class SpectrumTapeSource():
    """
    A class to abstract reading of Spectrum tape images.
    """

    def __init__(self, source):
        """
        Creates a new object that can be read from to abstract the
        differences between bytes and a file.
        source has to be a file object or a byte array or bytes, or list
        or tupple of ints.
        position lists where in the source we curently are.
        """
        if not _sourceisvalid(source):
            raise spectrumtranslate.SpectrumTranslateError("source needs \
to be a file, bytes, bytearray, or a list or tupple of ints.")
        self.source = source
        self.sourceType = 1 if isinstance(source, IOBase) else 0
        self.len = 0 if isinstance(source, IOBase) else len(source)
        self.position = 0

    def getbytes(self, byteswanted):
        """Return up to byteswanted from the input source.
        Returns fewer bytes if fewer bytes left in source, and 0 if at
        end of source.
        """

        # Handle file source
        if self.sourceType == 1:
            b = self.source.read(byteswanted)
            self.position += len(b)
            return b

        # handle other sources
        p = self.position
        n = min(byteswanted, self.len - p)
        self.position += n
        return self.source[p: p + n]

    def getbyte(self):
        """Return a byte from the input source.
        Returns None if at end of source.
        """

        # Handle file source
        if self.sourceType == 1:
            b = self.source.read(1)
        # handle other sources
        else:
            p = self.position
            n = min(1, self.len - p)
            b = self.source[p: p + n]

        self.position += len(b)
        return b[0] if len(b) == 1 else None

    def getword(self, bytesize, signed=False):
        """Returns a word made up of bytesize bytes from the source.
        Raises an IOError with error text if there aren't enough bytes
        in source.
        """

        rawbytes = self.getbytes(bytesize)
        if len(rawbytes) < bytesize:
            raise EOFError("Not Enough Bytes For Word")

        return int.from_bytes(rawbytes, 'little', signed=signed)


def gettapblockfromsource(tapSource, block=0):
    """
    Gets a TapBlock from the specified source.
    Returns None if have reached the end of a file.
    Raises IOError if any problems with file format.
    """

    tb = SpectrumTapBlock(filePosition=tapSource.position, blockPosition=block)

    # read 2 byte tap block length
    lengthbytes = tapSource.getbytes(2)

    # if have hit end of file at start of new tapblock then end nicely
    if len(lengthbytes) == 0:
        return None

    if len(lengthbytes) != 2:
        raise IOError("Malformed .tap File")

    # flag at beginning and checksum at end of data included in length,
    # so actual data is 2 bytes shorter than block length
    blocklength = _get_word(_validateandpreparebytes(lengthbytes)) - 2

    # now process flag
    flagbyte = _validateandpreparebytes(tapSource.getbytes(1))
    if len(flagbyte) != 1:
        raise IOError("Malformed .tap File")

    tb.flag = flagbyte[0]

    tb.data = _validateandpreparebytes(tapSource.getbytes(blocklength))
    if len(tb.data) != blocklength:
        raise IOError("Malformed .tap File")

    # now do checksum
    checkbyte = _validateandpreparebytes(tapSource.getbytes(1))
    if len(checkbyte) != 1:
        raise IOError("Malformed .tap File")

    # ensure checksum is right
    k = tb.flag
    for i in tb.data:
        k = k ^ i

    if (k & 255) != checkbyte[0]:
        raise IOError("Malformed .tap File")

    return tb


def gettzxblockfromsource(tzxsource, block=0):
    """
    Returns next TapeBlock from tzx file.  return None if at end of
    source, or raises IOError if data is corrupt.
    """

    position = tzxsource.position
    blockid = tzxsource.getbyte()

    if blockid is None:
        return None
    try:
        if blockid == 0x10:
            pause = tzxsource.getword(2)
            datalen = tzxsource.getword(2)
            data = tzxsource.getbytes(datalen)
            if len(data) < datalen:
                raise IOError("Corrupt TZX Standard Speed Data Block")
            return SpectrumTZXStandardSpeedDataBlock(pause, data, position,
                                                     block)
        elif blockid == 0x11:
            lenPilotPulse = tzxsource.getword(2)
            lenSyncPulse1 = tzxsource.getword(2)
            lenSyncPulse2 = tzxsource.getword(2)
            lenZeroPulse = tzxsource.getword(2)
            lenOnePulse = tzxsource.getword(2)
            lenPilotTone = tzxsource.getword(2)
            lastByteUsedBits = tzxsource.getword(1)
            endPause = tzxsource.getword(2)
            datalen = tzxsource.getword(3)
            data = tzxsource.getbytes(datalen)
            if len(data) < datalen:
                raise IOError("Corrupt TZX Turbo Speed Data Block")
            return SpectrumTZXTurboSpeedDataBlock(endPause, data,
                                                  lenPilotPulse,
                                                  lenSyncPulse1, lenSyncPulse2,
                                                  lenZeroPulse, lenOnePulse,
                                                  lenPilotTone,
                                                  lastByteUsedBits,
                                                  position, block)
        elif blockid == 0x12:
            lenPulse = tzxsource.getword(2)
            numberOfPulses = tzxsource.getword(2)
            return SpectrumTZXPureToneBlock(lenPulse, numberOfPulses, position,
                                            block)
        elif blockid == 0x13:
            n = tzxsource.getword(1)
            pulses = [tzxsource.getword(2) for _ in range(n)]
            return SpectrumTZXPulseSequenceBlock(pulses, position, block)
        elif blockid == 0x14:
            lenZeroPulse = tzxsource.getword(2)
            lenOnePulse = tzxsource.getword(2)
            lastByteUsedBits = tzxsource.getword(1)
            endPause = tzxsource.getword(2)
            datalen = tzxsource.getword(3)
            data = tzxsource.getbytes(datalen)
            if len(data) < datalen:
                raise IOError("Corrupt TZX Pure Data Block")
            return SpectrumTZXPureDataBlock(endPause, data, lenZeroPulse,
                                            lenOnePulse, lastByteUsedBits,
                                            position, block)
        elif blockid == 0x15:
            TPerSample = tzxsource.getword(2)
            endPause = tzxsource.getword(2)
            lastByteUsedBits = tzxsource.getword(1)
            datalen = tzxsource.getword(3)
            sampleData = tzxsource.getbytes(datalen)
            if len(sampleData) < datalen:
                raise IOError("Corrupt TZX DirectRecording Block")
            return SpectrumTZXDirectRecordingBlock(TPerSample,
                                                   lastByteUsedBits,
                                                   endPause, sampleData,
                                                   position, block)
        elif blockid == 0x18:
            blocklen = tzxsource.getword(4)
            if blocklen < 10:
                raise IOError("Corrupt TZX CSW Recording Block")
            blocklen -= 10
            endPause = tzxsource.getword(2)
            sampleRate = tzxsource.getword(3)
            compressionType = tzxsource.getword(1)
            storedPulses = tzxsource.getword(4)
            CSWData = tzxsource.getbytes(blocklen)
            if len(CSWData) < blocklen:
                raise IOError("Corrupt TZX CSW Recording Block")
            return SpectrumTZXCSWRecording(sampleRate, compressionType,
                                           storedPulses, endPause, CSWData,
                                           position, block)
        elif blockid == 0x19:
            blocklen = tzxsource.getword(4)
            endPause = tzxsource.getword(2)
            symbolsInPilotBlock = tzxsource.getword(4)
            pulsesPerPilotSymbol = tzxsource.getword(1)
            alphabetSizePilot = tzxsource.getword(1)
            symbolsInDataBlock = tzxsource.getword(4)
            pulsesPerDataSymbol = tzxsource.getword(1)
            alphabetSizeData = tzxsource.getword(1)

            def _X(x):
                return [tzxsource.getword(2) for _ in range(x)]

            symbolDefinitionsPilot = [
                (tzxsource.getword(1), _X(pulsesPerPilotSymbol))
                for _ in range(alphabetSizePilot)]
            dataStreamPilot = [
                (tzxsource.getword(1), tzxsource.getword(2))
                for _ in range(symbolsInPilotBlock)]
            symbolDefinitionsData = [
                (tzxsource.getword(1), _X(pulsesPerDataSymbol))
                for _ in range(alphabetSizeData)]
            datastreamsize = ceil(
                ceil(log2(alphabetSizeData)) * symbolsInDataBlock / 8)
            dataStreamData = tzxsource.getbytes(datastreamsize)
            if len(dataStreamData) != datastreamsize:
                raise IOError("Corrupt TZX Generalized Data Block")
            if tzxsource.position != position + 5 + blocklen:
                raise IOError("Corrupt TZX Generalized Data Block")
            return SpectrumTZXGeneralizedDataBlock(symbolsInPilotBlock,
                                                   pulsesPerPilotSymbol,
                                                   alphabetSizePilot,
                                                   symbolsInDataBlock,
                                                   pulsesPerDataSymbol,
                                                   alphabetSizeData,
                                                   symbolDefinitionsPilot,
                                                   dataStreamPilot,
                                                   symbolDefinitionsData,
                                                   dataStreamData,
                                                   endPause,
                                                   position,
                                                   block)
        elif blockid == 0x20:
            return SpectrumTZXPauseOrStopBlock(tzxsource.getword(2), position,
                                               block)
        elif blockid == 0x21:
            namelen = tzxsource.getword(1)
            name = tzxsource.getbytes(namelen)
            if len(name) < namelen:
                raise IOError("Corrupt TZX Group Start Block")
            return SpectrumTZXGroupStartBlock(name, position, block)
        elif blockid == 0x22:
            return SpectrumTZXGroupEndBlock(position, block)
        elif blockid == 0x23:
            return SpectrumTZXJumpToBlock(tzxsource.getword(2, True), position,
                                          block)
        elif blockid == 0x24:
            return SpectrumTZXLoopStartBlock(tzxsource.getword(2), position,
                                             block)
        elif blockid == 0x25:
            return SpectrumTZXLoopEndBlock(position, block)
        elif blockid == 0x26:
            n = tzxsource.getword(2)
            return SpectrumTZXCallSequenceBlock([tzxsource.getword(2, True)
                                                 for _ in range(n)], position,
                                                block)
        elif blockid == 0x27:
            return SpectrumTZXReturnFromSequenceBlock(position, block)
        elif blockid == 0x28:
            blocklen = tzxsource.getword(2)
            n = tzxsource.getword(1)
            selectoptions = [(tzxsource.getword(2, True),
                             tzxsource.getbytes(tzxsource.getword(1)))
                             for _ in range(n)]
            if tzxsource.position != position + 3 + blocklen:
                raise IOError("Corrupt TZX Select Block")
            return SpectrumTZXSelectBlock(selectoptions, position, block)
        elif blockid == 0x2A:
            blocklen = tzxsource.getword(4)
            if blocklen > 0:
                tzxsource.getbytes(l)
            return SpectrumTZXStopTapeIf48KBlock(position, block)
        elif blockid == 0x2B:
            blocklength = tzxsource.getword(4)
            level = tzxsource.getword(1)
            if blocklength > 1:
                tzxsource.getbytes(blocklength - 1)
            return SpectrumTZXSetSignalLevelBlock(level, position, block)
        elif blockid == 0x30:
            descriptionlen = tzxsource.getword(1)
            description = tzxsource.getbytes(descriptionlen)
            if len(description) < descriptionlen:
                raise IOError("Corrupt TZX Text Description Block")
            return SpectrumTZXTextDescriptionBlock(description, position,
                                                   block)
        elif blockid == 0x31:
            duration = tzxsource.getword(1)
            messagelen = tzxsource.getword(1)
            message = tzxsource.getbytes(messagelen)
            if len(message) < messagelen:
                raise IOError("Corrupt Message Block")
            return SpectrumTZXMessageBlock(message, duration, position, block)
        elif blockid == 0x32:
            blocklen = tzxsource.getword(2)
            n = tzxsource.getword(1)
            archiveInfoEntries = [
                (tzxsource.getword(1),
                 tzxsource.getbytes(tzxsource.getword(1)))
                for _ in range(n)]
            if tzxsource.position != position + 3 + blocklen:
                raise IOError("Corrupt TZX Archive Info Block")
            return SpectrumTZXArchiveInfoBlock(archiveInfoEntries, position,
                                               block)
        elif blockid == 0x33:
            n = tzxsource.getword(1)
            return SpectrumTZXHardwareTypeBlock(
                [tzxsource.getbytes(3) for _ in range(n)], position, block)
        elif blockid == 0x35:
            identification = tzxsource.getbytes(10)
            if len(identification) < 10:
                raise IOError("Corrupt TZX Custom Info Block")
            n = tzxsource.getword(4)
            return SpectrumTZXCustomInfoBlock(identification,
                                              tzxsource.getbytes(n),
                                              position, block)
        elif blockid == 0x5A:
            if tzxsource.getbytes(7) != b'XTape!\x1a':
                raise IOError("Corrupt TZX Header Block" if block == 0 else
                              "Corrupt TZX Glue Block")
            return SpectrumTZXHeaderBlock(tzxsource.getbytes(1),
                                          tzxsource.getbytes(1),
                                          position, block)
        else:
            raise IOError(
                "Corrupt TZX file. Unrecognised or Deprecated Block ID")
    except EOFError as e:
        if not hasattr(e, 'message') or \
           e.message != "Not Enough Bytes For Word":
            raise e
        idmessages = {0x10: "Corrupt TZX Standard Speed Data Block",
                      0x11: "Corrupt TZX Turbo Speed Data Block",
                      0x12: "Corrupt TZX Pure Tone Block",
                      0x13: "Corrupt TZX Pulse Sequence Block",
                      0x14: "Corrupt TZX Pure Data Block",
                      0x15: "Corrupt TZX Direct Recording Block",
                      0x18: "Corrupt TZX CSW Recording Block",
                      0x19: "Corrupt TZX Generalized Data Block",
                      0x20: "Corrupt TZX Pause or Stop the Tape Block",
                      0x21: "Corrupt TZX Group Start Block",
                      0x23: "Corrupt TZX Jump To Block",
                      0x24: "Corrupt TZX Loop Start Block",
                      0x26: "Corrupt TZX Call Sequence Block",
                      0x28: "Corrupt TZX Select Block",
                      0x2A: "Corrupt TZX Stop Tape if 48K Block",
                      0x2B: "Corrupt TZX Set Signal Level Block",
                      0x30: "Corrupt TZX Text Description Block",
                      0x31: "Corrupt TZX Message Block",
                      0x32: "Corrupt TZX Archive Info Block",
                      0x33: "Corrupt TZX Hardware Type Block",
                      0x35: "Corrupt TZX Custom Info Block"
                      }
        raise IOError(idmessages[blockid])


def nexttapblock(source):
    """
    Generator function that will supply SpectrumTapBlock objects from a
    tap file.
    source can be a file object, a bytearray, a bytes object, or a list
    or tuple of ints.

    example:
    with open('RebelStar.tap', 'rb') as f:
        for tb in nexttapblock(f):
            do_stuff_with(tb)
    """

    source = SpectrumTapeSource(source)
    block = 0
    while True:
        tb = gettapblockfromsource(source, block)
        if tb:
            block += 1
            yield tb
        else:
            break


def nexttzxblock(source):
    """
    Generator function that will supply SpectrumTzx* objects from a
    tzx file.
    source can be a file object, a bytearray, a bytes object, or a list
    or tuple of ints.

    example:
    with open('RebelStar.tzx', 'rb') as f:
        for tb in nexttzxblock(f):
            do_stuff_with(tb)
    """

    source = SpectrumTapeSource(source)
    block = 0
    while True:
        tb = gettzxblockfromsource(source, block)
        if tb:
            block += 1
            yield tb
        else:
            break


def convertblockformat(block, formatwanted):
    if formatwanted is None:
        return block

    if formatwanted not in ['Tap', 'Tzx']:
        raise spectrumtranslate.SpectrumTranslateError("{} is not a \
recognised or supported tape file format.".format(formatwanted))

    # Tap format to...
    if type(block) is SpectrumTapBlock:
        if formatwanted == 'Tap':
            return block
        # convert to Tzx

        # work out checksum
        checksum = block.flag
        for i in block.data:
            checksum = checksum ^ i

        # merge it into a list
        data = bytearray([block.flag]) + block.data + bytearray([checksum])

        return SpectrumTZXStandardSpeedDataBlock(
            endPause=1000, data=data, blockPosition=block.blockPosition)

    # Tzx format to...
    if formatwanted == 'Tzx':
        return block
    if type(block) not in [SpectrumTZXStandardSpeedDataBlock,
                           SpectrumTZXTurboSpeedDataBlock,
                           SpectrumTZXPureDataBlock]:
        raise spectrumtranslate.SpectrumTranslateError("Can't \
convert {} Block to Tap format.".format(block.blocktype()))
    return SpectrumTapBlock(block.flag, data=block.getpayload(),
                            blockPosition=block.blockPosition)


def getfiletypeandblocksfromsource(source):
    """
    Returns a tuple detailing the file type ("tap", "tzx", or "unknown")
    as the first element, and a list of all the blocks as the second.
    source is a file, bytes, bytearray, or list of ints.
    """

    if isinstance(source, IOBase):
        source = bytearray(source.read())

    try:
        tbs = [*nexttzxblock(source)]
        if len(tbs) > 0:
            return ('Tzx', tbs)
    except IOError:
        pass

    try:
        tbs = [*nexttapblock(source)]
        if len(tbs) > 0:
            return ('Tap', tbs)
    except IOError:
        pass

    return ('unknown', [])


def createbasicheader(filename, VariableOffset, ProgLength, AutoStart=-1):
    """Create a header for a program SpectrumTapBlock."""

    # create basic data block
    tb = SpectrumTapBlock()
    tb.flag = 0
    tb.data = bytearray([0]) + _validateandconvertfilename(filename) + \
        bytearray([0, 0, 0, 0, 0, 0])
    # set program
    tb.data[11] = ProgLength & 0xFF
    tb.data[12] = (ProgLength >> 8) & 0xFF
    # set autostart
    if AutoStart < 0 or AutoStart > 9999:
        AutoStart = 0x8000

    tb.data[13] = AutoStart & 0xFF
    tb.data[14] = (AutoStart >> 8) & 0xFF
    # set variable offset
    tb.data[15] = VariableOffset & 0xFF
    tb.data[16] = (VariableOffset >> 8) & 0xFF

    return tb


def createcodeheader(filename, Origin, Codelength):
    """Create a header for a code SpectrumTapBlock."""

    # create basic data block
    tb = SpectrumTapBlock()
    tb.flag = 0
    tb.data = bytearray([3]) + _validateandconvertfilename(filename) + \
        bytearray([0, 0, 0, 0, 0, 0])

    # set code origin
    tb.data[13] = Origin & 0xFF
    tb.data[14] = (Origin >> 8) & 0xFF
    # set code length
    tb.data[11] = Codelength & 0xFF
    tb.data[12] = (Codelength >> 8) & 0xFF

    return tb


def createarrayheader(filename, VariableDescriptor, ArrayLength):
    """
    Create a header for an array SpectrumTapBlock.
    The VariableDescriptor is composed of the lower 6 bits of the
    variable name (a one letter name), and the upper 2 bits are 64 for a
    character array, 128 for a number array, and 192 for a string array.
    """

    tb = SpectrumTapBlock()
    tb.flag = 0
    tb.data = bytearray([0]) + _validateandconvertfilename(filename) + \
        bytearray([0, 0, 0, 0, 0, 0])

    # set array file type
    tb.data[0] = 1 if VariableDescriptor & 192 == 128 else 2

    # set array length
    tb.data[11] = ArrayLength & 0xFF
    tb.data[12] = (ArrayLength >> 8) & 0xFF

    # set array details
    tb.data[14] = VariableDescriptor

    return tb


def createscreenheader(filename):
    """Create a header for a screen SpectrumTapBlock."""

    # screen is just specialized code file
    return createcodeheader(filename, 16384, 6912)


def createdatablock(data, flag=0xFF):
    """Create a data SpectrumTapBlock."""

    tb = SpectrumTapBlock()
    tb.flag = flag
    tb.data = _validateandpreparebytes(data, "data")

    return tb


def usage():
    """
    returns the command line arguments for spectrumtape as a string.
    """

    return """usage: python spectrumtape.py instruction [args] infile
    outfile

    moves data from infile which should be a tap or tzx file (or data to
    save as a file into a tap or tzx file) and outputs it to outfile.

    instruction is required and specifies what you want to do. It must
    be 'list', 'extract', 'delete', 'copy, or 'create'.  'list' will
    list the contents of the specified file.  'extract' extracts the
    data from a file entry to wherever you want.  'copy' copies the
    specified file entries to another file.  'delete' deletes the
    specified entries from the source file and outputs the resulting
    file. 'create' creates a tap entry (as well as a header entry if
    needed) in outfile using the supplied file data.

    infile and outfile are required unless reading from the standard
    input or outputting to the standard output.  Usually arguments are
    ignored if they don't apply to the selected instruction.

    For the extract instruction, the index of the entry you want to
    extract must be specified before the filenames.

    For the copy and delete instructions, the index(s) of the entry or
    entries you want to copy must be specified before the filename.  You
    do not need to do this if you have already specified which entries
    you want with the -s flag.

    If using the create instruction, you must specify what you are
    creating imediatly after the create instruction.  Valid options are
    'basic', 'code', 'array', 'screen', and 'block'.  You must also
    specify the filnename for the file with the --filename flag unless
    you are creating a data block.  If creating an array, you must also
    specify the name and type of array with the --arraytype and
    --arrayname flags.

    general flags:
    -o specifies that the output from this program is to be directed to
       the standard output and not outputfile which should be omited.
       It can be used for all instructions.
    --tostandardoutput same as -o.
    -i specifies that this program gets it's data from the standard
       input and not inputfile which should be omited.  It can be used
       for all instructions.
    --fromstandardinput same as -i.
    -s specifies which entries you want.  These are the same as returned
       by the list instruction.  You can specify more than one,
       seperated by commas, and can even specify ranges of them with a
       minus.  The numbers are assumed to be decimal unless preceded by
       0x in which case they are assumed to be hexadecimal.
       For example: 2,0x10-20,23 will specify entry 2, 16 to 20
       inclusive, and 23.  This flag is used by list, delete, and copy.
    --specifyfiles same as -s.
    --specificfiles same as -s.
    --tap specifies that you want the output in tap file format.
    --txz specifies that you want the output in tzx file format.
    --notzxheader specifies that you don't want a tzx file header added
                  to a tzx file.  Otherwise one will automatically be
                  generated.  Most emulators will not load, or even
                  recognise a tzx file without it's header.

    list flags:
    -d specifies that we want all information about each file entry
       divided by tabs.  All entries begin with the index of the entry
       in the file, followed by the block type, and then either 'Header'
       for a header, 'Data' for a data block, or nothing if neither.
       For Data entries, the flag value and the data length is listed.
       For Headers the data following this depends on the file type.
       For Program headers, the data given is filename, 'Program',
       length of data in the coresponding data file, the autostart line
       number or -1 if there isn't one, and the offset in bytes to the
       atached variables (will be the same as the length if there are no
       variables).
       For Byte headers there follows the file name, 'Bytes', the
       address where the code was saved from (and would automatically be
       loaded to), and then the length.
       For array headers there follows the filename, 'Number array' or
       'Character array', the length of the array data, the array
       letter, the array variable name, and the array descriptor
       specifying what sort of array it contains.
       Finally for unknown file types, there follows the file name,
       'Unknown', the file type number, and the length of the ascociated
       data.
    --details is the same as -d.

    copy flags:
    -a specifies that the output should be appended to an existing file
       rather than overwriting it.
    -p specifies that the output should be inserted at the position in
       the desitnation file.  The index where you want the copied
       entry(entries) inserted must follow the flag and must be either a
       decimal or hexadecimal number preceded by '0x'.
    --pos same as -p.
    --position same as -p.

    create flags:
    --autostart This is used when creating a BASIC file to specify the
                autostart line.
    --variableoffset This is used to specify the offset into a BASIC
                     listing where the variables start.  If not
                     specified, the program will reliably work out where
                     the variables are unless the BASIC file is very
                     non-standard.  So this flag whould not be used
                     unless you have a very good reason.
    --origin This specifies the address for the origin of a code file.
    --arraytype This specifies the type of array file to create.  It
                must be followed by the type of array to create.  Valid
                options are:
                character or c for a character array, number or n for a
                number array, and string or s for a string.
    --arrayname This specifies the name for a saved array or string.  It
                must be followed by a single letter of the alphabet.
    --flag This specifies the flag byte for the data block. It must be
           followed by a number from 0 to 255.
    -p specifies that the output should be inserted at the position in
       the desitnation file.  The index where you want the copied
       entry(entries) inserted must follow the flag and must be either a
       decimal or hexadecimal number preceded by '0x'.
    --pos same as -p.
    --position same as -p.
"""


def _commandline(args):

    def getint(x):
        return int(x, 16 if x.lower().startswith("0x") else 10)

    def getindices(arg):
        try:
            specifiedfiles = []
            for n in arg.split(','):
                if '-' in n:
                    v = n.split('-', 1)
                    specifiedfiles += list(range(getint(v[0]),
                                                 getint(v[1]) + 1))

                else:
                    specifiedfiles += [getint(n)]

            if len(specifiedfiles) == 0:
                return None

            return specifiedfiles

        except ValueError:
            return None

    i = 0
    mode = None
    wantdetails = False
    fromstandardinput = False
    tostandardoutput = False
    inputfile = None
    outputfile = None
    entrywanted = None
    specifiedfiles = None
    append = False
    copyposition = False
    creating = None
    creatingfilename = None
    creatingautostart = -1
    creatingvariableoffset = -1
    creatingorigin = 0
    creatingarraytype = None
    creatingarrayname = None
    creatingblockflag = 0xFF
    filetyperequested = None
    generatetzxheader = True
    infiletype = None
    outfiletype = None

    # handle no arguments
    if len(args) == 1:
        mode = 'help'

    # go through arguments analysing them
    while i < len(args) - 1:
        i += 1

        arg = args[i]
        if arg in ['help', 'extract', 'list', 'copy', 'delete', 'create']:
            if mode is not None:
                raise spectrumtranslate.SpectrumTranslateError(
                    "Can't have multiple commands.")

            mode = arg
            continue

        if mode is None:
            raise spectrumtranslate.SpectrumTranslateError('No command (list, \
extract, delete, copy, create, or help) specified as first argument.')

        if mode == 'create' and creating is None:
            if arg not in ['basic', 'code', 'array', 'screen', 'block']:
                raise spectrumtranslate.SpectrumTranslateError('Must specify \
what type of file to create. Valid options are basic, code, array, screen, \
and block.')

            creating = arg
            continue

        # chack for multiple flags in one arg and split them
        if arg[0] == '-' and len(arg) > 2 and arg[1] != '-':
            args = args[0:i] + ['-' + x for x in arg[1:]] + args[i + 1:]
            arg = args[i]

        if arg == '--filename':
            i += 1
            creatingfilename = spectrumtranslate.stringtospectrum(args[i])
            continue

        if arg == '--autostart':
            i += 1
            try:
                creatingautostart = getint(args[i])
                continue

            except ValueError:
                raise spectrumtranslate.SpectrumTranslateError(
                    '{} is not a valid autostart number.'.format(args[i]))

        if arg == '--variableoffset':
            i += 1
            try:
                creatingvariableoffset = getint(args[i])
                continue

            except ValueError:
                raise spectrumtranslate.SpectrumTranslateError(
                    '{} is not a valid variable offset.'.format(args[i]))

        if arg == '--origin':
            i += 1
            try:
                creatingorigin = getint(args[i])
            except ValueError:
                raise spectrumtranslate.SpectrumTranslateError(
                    '{} is not a valid code origin.'.format(args[i]))

            if creatingorigin < 0 or creatingorigin > 65535:
                raise spectrumtranslate.SpectrumTranslateError(
                    'code origin must be 0-65535 inclusive.')

            continue

        if arg == '--flag':
            i += 1
            try:
                creatingblockflag = getint(args[i])
            except ValueError:
                raise spectrumtranslate.SpectrumTranslateError(
                    '{} is not a valid flag value.'.format(args[i]))

            if creatingblockflag < 0 or creatingblockflag > 255:
                raise spectrumtranslate.SpectrumTranslateError(
                    'flag value must be 0-255 inclusive.')

            continue

        if arg == '--arraytype':
            i += 1
            if args[i] in ['character', 'c']:
                creatingarraytype = 192
                continue

            elif args[i] in ['number', 'n']:
                creatingarraytype = 128
                continue

            elif args[i] in ['string', 's']:
                creatingarraytype = 64
                continue

            else:
                raise spectrumtranslate.SpectrumTranslateError('{} is not a \
valid array type (must be character, number or string).'.format(args[i]))

        if arg == '--arrayname':
            i += 1
            creatingarrayname = args[i]
            if len(creatingarrayname) == 1 and creatingarrayname.isalpha():
                continue

            raise spectrumtranslate.SpectrumTranslateError(
                '{} is not a valid variable name.'.format(args[i]))

        if arg in ['-i', '--fromstandardinput']:
            fromstandardinput = True
            continue

        if arg in ['-o', '--tostandardoutput']:
            tostandardoutput = True
            continue

        if arg in ['-d', '--details']:
            wantdetails = True
            continue

        if arg in ['-s', '--specifyfiles', '--specificfiles']:
            i += 1
            specifiedfiles = getindices(args[i])
            if specifiedfiles is None:
                raise spectrumtranslate.SpectrumTranslateError(
                    '"' + args[i] + '" is invalid list of file indexes.')
            continue

        if arg in ['-a', '--append']:
            append = True
            continue

        if arg in ['-p', '--position', '--pos']:
            i += 1
            try:
                copyposition = getint(args[i])
            except ValueError:
                raise spectrumtranslate.SpectrumTranslateError('{} is not a \
valid index for the output file.'.format(args[i]))

            continue

        if arg == '--tap':
            if filetyperequested == 'Tzx':
                raise spectrumtranslate.SpectrumTranslateError('You need to \
specify output as either tap or tzx.')
            filetyperequested = 'Tap'
            continue

        if arg == '--tzx':
            if filetyperequested == 'Tap':
                raise spectrumtranslate.SpectrumTranslateError('You need to \
specify output as either tap or tzx.')
            filetyperequested = 'Tzx'
            continue

        if arg == '--notzxheader':
            generatetzxheader = False
            continue

        # have unrecognised argument.
        if arg[0] == '-' or arg[0:2] == '--':
            raise spectrumtranslate.SpectrumTranslateError('{} is not a \
recognised flag.'.format(arg))

        # check if is what entry we want to extract
        if mode == 'extract' and entrywanted is None:
            try:
                entrywanted = getint(arg)

            except ValueError:
                raise spectrumtranslate.SpectrumTranslateError('{} is not a \
valid index in the input file.'.format(arg))

            continue

        # if it is what entries we want to copy
        if mode in ['copy', 'delete'] and specifiedfiles is None:
            specifiedfiles = getindices(arg)
            if specifiedfiles is None:
                raise spectrumtranslate.SpectrumTranslateError(
                    '"' + arg + '" is invalid list of file indexes.')

            continue

        # check if is input or output file
        # will be inputfile if not already defined, and
        # fromstandardinput is False
        if inputfile is None and not fromstandardinput:
            inputfile = arg
            continue

        # will be outputfile if not already defined, tostandardoutput
        # is False, and is last argument
        if outputfile is None and not tostandardoutput and i == len(args) - 1:
            outputfile = arg
            continue

        raise spectrumtranslate.SpectrumTranslateError(
            '"{}" is unrecognised argument.'.format(arg))

    if inputfile is None and not fromstandardinput and mode != 'help':
        raise spectrumtranslate.SpectrumTranslateError(
            'No input file specified.')

    if outputfile is None and not tostandardoutput and mode != 'help':
        raise spectrumtranslate.SpectrumTranslateError(
            'No output file specified.')

    if specifiedfiles is None and entrywanted is None and mode in ['delete',
                                                                   'copy']:
        raise spectrumtranslate.SpectrumTranslateError(
            'No file index(s) specified to {}.'.format(mode))

    if mode in ['delete', 'copy']:
        if specifiedfiles is None:
            specifiedfiles = [entrywanted]

    if mode == 'create' and creating is None:
        raise spectrumtranslate.SpectrumTranslateError(
            'You have to specify file type to create.')

    if mode == 'create' and creatingfilename is None and creating != 'block':
        raise spectrumtranslate.SpectrumTranslateError(
            'You have to specify file name to create.')

    if mode == 'create' and creating == 'array' and \
       (creatingarraytype is None or creatingarrayname is None):
        raise spectrumtranslate.SpectrumTranslateError(
            'You have to specify array type and name.')

    if entrywanted is None and mode == 'extract':
        raise spectrumtranslate.SpectrumTranslateError(
            'No file index specified to extract.')

    # if help is needed display it
    if mode == 'help':
        sys.stdout.write(usage())
        return

    # get data
    if not fromstandardinput:
        with open(inputfile, 'rb') as infile:
            data = bytearray(infile.read())

    else:
        data = sys.stdin.buffer.read()

    # work out output format
    if mode in ['create', 'copy', 'delete'] and not tostandardoutput and \
       isfile(outputfile):
        with open(outputfile, 'rb') as f:
            outfiletype = getfiletypeandblocksfromsource(f)[0]
        if outfiletype is not None and filetyperequested is not None and \
           filetyperequested != outfiletype:
            raise spectrumtranslate.SpectrumTranslateError('{} type \
requested, but "{}" is already {}.'.format(filetyperequested, outputfile,
                                           outfiletype))
    if filetyperequested is not None and outfiletype is None:
        outfiletype = filetyperequested
    if outfiletype is None and not tostandardoutput and isfile(outputfile):
        if outputfile.lower().endswith(".tap"):
            outfiletype = "Tap"
        if outputfile.lower().endswith(".tzx"):
            outfiletype = "Tzx"
    if outfiletype is None:
        outfiletype = "Tap"

    # now do command
    if mode == 'list':
        pos = 0
        retdata = '' if wantdetails else \
            'block type                content information\n'
        (infiletype, tbs) = getfiletypeandblocksfromsource(data)
        for tb in tbs:
            if specifiedfiles is not None and pos not in specifiedfiles:
                pos += 1
                continue

            if wantdetails:
                retdata += tb.getdetailslist() + "\n"
            else:
                retdata += "{:>4}  {:<20.20} {:<6} {}\n".format(
                    pos, tb.blocktype(),
                    "Header" if tb.isheader() else ("Data" if
                                                    tb.isdatablock() else ""),
                    tb.getblockinfo())

            pos += 1

    if mode == 'extract':
        (infiletype, tbs) = getfiletypeandblocksfromsource(data)
        if entrywanted > len(tbs):
            raise spectrumtranslate.SpectrumTranslateError(
                str(entrywanted) + " is greater than the number of entries in \
the source data.")

        retdata = tbs[entrywanted].getpayload()
        if retdata is None:
            raise spectrumtranslate.SpectrumTranslateError("{} does not \
contain accesable file data.".format(entrywanted))

    if mode == 'copy':
        (infiletype, tbs) = getfiletypeandblocksfromsource(data)
        retdata = bytearray()
        for x in specifiedfiles:
            if x > len(tbs):
                raise spectrumtranslate.SpectrumTranslateError(
                    str(x) + " is greater than the number of entries in the \
source data.")

            retdata += convertblockformat(tbs[x],
                                          outfiletype).getpackagedforfile()

    if mode == 'delete':
        (infiletype, tbs) = getfiletypeandblocksfromsource(data)
        retdata = bytearray()
        for x in range(len(tbs)):
            if x not in specifiedfiles:
                retdata += convertblockformat(tbs[x],
                                              outfiletype).getpackagedforfile()

    if mode == 'create':
        retdata = bytearray()

        if creating == 'basic':
            if creatingvariableoffset == -1:
                # work out position of variables
                creatingvariableoffset = spectrumtranslate.\
                    getvariableoffset(data)

            retdata = convertblockformat(createbasicheader(
                creatingfilename, creatingvariableoffset, len(data),
                creatingautostart), outfiletype).getpackagedforfile()

        elif creating == 'code':
            retdata = convertblockformat(createcodeheader(
                creatingfilename, creatingorigin, len(data)),
                outfiletype).getpackagedforfile()

        elif creating == 'array':
            retdata = convertblockformat(createarrayheader(
                creatingfilename,
                creatingarraytype + (ord(creatingarrayname) & 0x3F),
                len(data)), outfiletype).getpackagedforfile()

        elif creating == 'screen':
            retdata = convertblockformat(createscreenheader(
                creatingfilename), outfiletype).getpackagedforfile()

        retdata += convertblockformat(createdatablock(
            data, flag=creatingblockflag if creating == 'block' else 0xFF),
            outfiletype).getpackagedforfile()

    # handle copy or create inserting at position
    if copyposition and mode in ['create', 'copy']:
        if not tostandardoutput and isfile(outputfile):
            # get tapblocks (if any in destination file)
            with open(outputfile, 'rb') as infile:
                outtbs = getfiletypeandblocksfromsource(infile)[1]

            if copyposition < len(outtbs):
                a = [convertblockformat(tb, outfiletype).getpackagedforfile()
                     for tb in outtbs[:copyposition]]
                b = [convertblockformat(tb, outfiletype).getpackagedforfile()
                     for tb in outtbs[copyposition:]]
                retdata = bytearray().join(a) + retdata + bytearray().join(b)

            else:
                retdata = bytearray().join([tb.getpackagedforfile() for tb in
                                            destinationtbs]) + retdata

    # ensure have a tzx header on file if needed
    if generatetzxheader and outfiletype == "Tzx" and mode in [
       'create', 'copy', 'delete'] and retdata[0:8] != b'XTape!\x1a':
        retdata = SpectrumTZXHeaderBlock(1, 20).getpackagedforfile() + retdata

    # output data
    if not tostandardoutput:
        filemode = "a" if mode in ['copy', 'create'] and append else "w"
        with open(outputfile,
                  filemode if mode == 'list' else filemode + 'b') as fo:
            fo.write(retdata)

    else:
        if mode == "list":
            sys.stdout.write(retdata)
        else:
            sys.stdout.buffer.write(retdata)


if __name__ == "__main__":
    try:
        _commandline(sys.argv)
    except spectrumtranslate.SpectrumTranslateError as se:
        sys.stderr.write(se.value + "\n")
        sys.stdout.write(
            "Use 'python spectrumtape.py' to see full list of options.\n")
        sys.exit(2)
