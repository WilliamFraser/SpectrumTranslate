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

import spectrumtranslate
from mmap import mmap as _mmap
from os.path import isfile as _isfile
from numbers import Integral as _INT_OR_LONG
from sys import hexversion as _PYTHON_VERSION_HEX
# sys and codecs are imported if run from the command line


if(_PYTHON_VERSION_HEX > 0x03000000):
    def _checkisvalidbytes(x, m):
        if(isinstance(x, (bytes, bytearray)) or
           (isinstance(x, (list, tuple)) and
           all(isinstance(val, int) for val in x))):
            return True

        raise spectrumtranslate.SpectrumTranslateError("{0} needs to be a \
list or tuple of ints, or of type 'bytes' or 'bytearray'".format(m))

    def _validbytestointlist(x):
        # function to convert any valid source to a list of ints
        if(isinstance(x, (bytes, bytearray))):
            return [b for b in x]

        return x[:]

else:
    def _checkisvalidbytes(x, m):
        if(isinstance(x, str) or
           (isinstance(x, (list, tuple)) and
           all(isinstance(val, _INT_OR_LONG) for val in x))):
            return True

        raise spectrumtranslate.SpectrumTranslateError("{0} needs to be a \
byte string, or a list or tuple of ints or longs".format(m))

    def _validbytestointlist(x):
        # function to convert any valid source to a list of ints
        if(isinstance(x, str)):
            return [ord(b) for b in x]

        return x[:]


def _validateandconvertfilename(filename):
    # check filename is valid
    if(isinstance(filename, list)):
        # if is list of numbers convert to list of strings
        if(False not in [isinstance(x, _INT_OR_LONG) for x in filename]):
            filename = [chr(x) for x in filename]

        # if there are only strings in the list then convert list to
        # a string
        if(False not in [isinstance(x, str) for x in filename]):
            filename = "".join(filename)

    if(not isinstance(filename, str) or len(filename) > 10):
        raise spectrumtranslate.SpectrumTranslateError(
            "Filename must be a string, or list of ints or strings of no \
more than 10 characters.")

    # return filename right padded with spaces
    return [ord(x) for x in filename] + [32] * (10 - len(filename))


def GetDirectoryEntryPosition(num):
    """Returns the track, and sector of given directory number."""

    return (num-1) // 20, (((num-1) // 2) % 10) + 1


class DiscipleFile:
    """A class that holds information about a file from a +D/Disciple
       disk image.
       fs"""

    def __init__(self, image, filenumber):
        """Creates a new DiscipleFile for the specified file in the
        specified image.  image is the DiscipleImage to extract the file
        from.  filenumber is the filenumber for the file you wish to
        extract from 1 to 80 inclusive.
        """

        # make note of parent image
        self.image = image

        # make note of filenumber
        self.filenumber = filenumber

        # is it a valid filenumber?
        # Origional valid filenumbers are 1 to 80
        if(self.filenumber < 1 or self.filenumber > 80):
            raise spectrumtranslate.SpectrumTranslateError(
                "Invalid File Number")

    def getheadder(self):
        """Returns 256 byte file headder"""

        # work out if first or second entry in sector
        headderstart = ((self.filenumber-1) & 1) * 256

        t, s = GetDirectoryEntryPosition(self.filenumber)
        return self.image.getsector(t, s)[headderstart: headderstart + 256]

    def getfiledata(self, wantheadder=False, headderdata=None):
        """Get the data of the file. Returns a byte string array
        containing the file data.

        BASIC, code, number array, string array, and screen files have
        and extra 9 bytes at the start of the file (these extra bytes
        are not included in the file length as returned by
        getfilelength().  These are a copy of the headder data. Normally
        you don't want these bytes, but use wantheadder=True if you do
        (it defaults to False if unspecified).  headderdata is optional
        but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        # check to make sure is valid file
        if(self.isempty(headderdata)):
            return None

        # make note of number of sectors in file
        i = self.getsectorsused(headderdata)

        # get map of sectors used
        sectorMap = headderdata[15:210]

        bytestocopy = self.getfilelength(headderdata)

        data = []

        # get start track & sector
        track = headderdata[13]
        sector = headderdata[14]

        # BASIC, code, number array, string array, or screen have extra
        # 9 bytes of file as copy of headder data.
        t = self.getfiletype(headderdata)
        if((t > 0 and t < 5) or t == 7):
            if(wantheadder):
                readpos = 0
                bytestocopy += 9

            else:
                readpos = 9

        else:
            readpos = 0

        # now move through file transfering data to array
        while(i > 0):
            # sanity check on track & sector
            if(track == 0 and sector == 0):
                raise spectrumtranslate.SpectrumTranslateError(
                    "unexpected early end of file")

            if((track & 127) > 79 or track < 4):
                raise spectrumtranslate.SpectrumTranslateError(
                    "Invalid track number")

            if(sector < 1 or sector > 10):
                raise spectrumtranslate.SpectrumTranslateError(
                    "Invalid sector number")

            # calculate offset & bit of this track & sector in sectorMap
            o = (track & 127) + (80 if track >= 128 else 0) - 4
            o *= 10
            o += sector-1
            b = 1 << (o % 8)
            o = o // 8
            # check if is sector owned by this file
            if((sectorMap[o] & b) != b):
                raise spectrumtranslate.SpectrumTranslateError(
                    "next sector not matching FAT")

            # remove from copy of sectorMap
            sectorMap[o] -= b

            # load next sector in chain
            sectordata = self.image.getsector(track & 127, sector, track >> 7)
            # copy sector data
            data += sectordata[readpos:min(510 - readpos, bytestocopy) +
                               readpos]

            # update track & sector
            track = sectordata[510]
            sector = sectordata[511]
            # update number of bytes left to copy
            bytestocopy -= (510 - readpos)
            # decrement number of sectors left to fetch
            i -= 1
            # after reading 1st sector won't have any more file headder
            # data at start of sector
            readpos = 0

        # track & sector of last sector read should be 0
        if(track != 0 and sector != 0):
            raise spectrumtranslate.SpectrumTranslateError(
                "File length mismatch")

        # sectorMap should now be blank
        # otherwise there are unused sectors
        for i in sectorMap:
            if(i != 0):
                raise spectrumtranslate.SpectrumTranslateError(
                    "Unused sectors in FAT")

        return data

    def isempty(self, headderdata=None):
        """
        Is this DiscipleFile an unused or errased entry?
        headderdata is optional but saves resources.
        """

        return self.getfiletype(headderdata) == 0

    def getsectorsused(self, headderdata=None):
        """
        Gets the number of sectors used by this file.
        headderdata is optional but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        # check to make sure is valid file
        if(self.isempty(headderdata)):
            return 0

        # is stored at offset 11 in motorola byte order (most significant
        # byte first)
        return headderdata[12] + 256 * headderdata[11]

    def getfilelength(self, headderdata=None):
        """Returns the length of this file.
        headderdata is optional but saves resources.
        NB BASIC, code, number array, string array, and screen files
        have and extra 9 bytes at the start of the file data which is a
        copy of the 9 byte headder data as if it were saved to tape.
        These 9 bytes are extra to the length of the file as returned by
        this method.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        t = self.getfiletype(headderdata)
        # the length of the file in bytes depends on the file type
        if(t == 0):
            # deleted/empty
            return 0

        elif(t == 1 or t == 2 or t == 3 or t == 4 or t == 7 or t == 13):
            # 1=basic,2=number array,3=string array,4=code,7=screen$,
            # 13=unidos create file
            return headderdata[212] + 256 * headderdata[213]

        elif(t == 5):
            # 48K snapshot
            return 49152  # 3 * 16K ram banks

        elif(t == 9):
            # 128K snapshot
            return 131073  # 1 byte page register value + 8 16K ram banks

        elif(t == 10):
            # opentype
            return headderdata[212] +\
                   256 * headderdata[213] +\
                   65536 * headderdata[210]

        elif(t == 11):
            # execute
            return 510
        else:
            # default length is size of all used sector (minus chain bytes)
            return self.getsectorsused(headderdata) * 510

    def getfiletype(self, headderdata=None):
        """
        Returns the file type the file described by this DiscipleFile.
        This is a number from 0 to 11.
        Values other than this sugest that the image file that this
        object was created from may be corrupted.
        headderdata is optional but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        # &31 to exclude hidden flags
        return headderdata[0] & 31

    def getfiletypestring(self, headderdata=None):
        """
        Returns the file type name of the file described by this
        DiscipleFile.
        headderdata is optional but saves resources.
        """

        i = self.getfiletype(headderdata)
        if(i > 11):
            return None

        return ("Free/Erased", "Basic", "Number Array", "String Array", "Code",
                "48K Snapshot", "Microdrive", "SCREEN$", "Special",
                "128K Snapshot", "Opentype", "Execute",  # unidos filenames
                "SUBDIRECTORY", "CREATE")[i]

    def getfiletypecatstring(self, headderdata=None):
        """
        Returns the file type name use in a catalog listing for the file
        described by this DiscipleFile.
        headderdata is optional but saves resources.
        """

        i = self.getfiletype(headderdata)
        if(i > 11):
            return None

        return ("ERASED", "BAS", "D.ARRAY", "$.ARRAY", "CDE", "SNP 48k",
                "MD.FILE", "SCREEN$", "SPECIAL", "SNP 128k", "OPENTYPE",
                "EXECUTE",  # list unidos cat names also
                "DIR", "CREATE")[i]

    def getfilename(self, headderdata=None):
        """
        This gets the filename. Note that the filename is always 10
        spectrum characters long and will be padded with spaces to make
        the length up to 10 characters.  Also be aware that spectrum
        characters can contain control codes, or names of spectrum
        BASIC commands, so the resultant extracted string could be more
        than 10 characters in length.
        headderdata is optional but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        return spectrumtranslate.getspectrumstring(headderdata[1:11])

    def getrawfilename(self, headderdata=None):
        """This returns the 10 character file name as a list of ints."""

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        return headderdata[1:11]

    def getfiledetails(self, headderdata=None):
        """
        This gets tupple mapping with data about the file that a headder
        block describes.  The elements returned are similar to that
        displayed by the full catalog.
        headderdata is optional but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        details = {"filenumber": self.filenumber,
                   "filename": self.getfilename(headderdata),
                   "rawfilename": self.getrawfilename(headderdata),
                   "sectors": self.getsectorsused(headderdata),
                   "filetype": self.getfiletype(headderdata),
                   "filetypeshort": self.getfiletypecatstring(headderdata),
                   "filetypelong": self.getfiletypestring(headderdata),
                   "filelength": self.getfilelength(headderdata),
                   "catextradata": ""}

        if(details["filetype"] == 4):
            # code
            details["codeaddress"] = self.getcodestart(headderdata)
            details["catextradata"] = "{0:5},{1:5}".format(
                self.getcodestart(headderdata),
                self.getfilelength(headderdata))
            details["coderunaddress"] = headderdata[218] +\
                256 * headderdata[219]

        if(details["filetype"] == 1):
            # basic
            details["autostartline"] = self.getautostartline(headderdata)
            details["variableoffset"] = self.getvariableoffset(headderdata)
            if(self.getautostartline(headderdata) >= 0):
                details["catextradata"] = "{0:5}".format(self.getautostartline(
                                                         headderdata))

        if(details["filetype"] == 2 or details["filetype"] == 3):
            # number or character array
            details["variableletter"] = self.getvariableletter(headderdata)
            details["variablename"] = self.getvariablename(headderdata)
            details["arraydescriptor"] = self.getarraydescriptor(headderdata)

        return details

    def getfiledetailsstring(self, headderdata=None):
        """
        This gets a String respresentation of the file that a headder
        block describes.  The format of the returned string is similar
        to that displayed by the full catalog.
        headderdata is optional but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        s = "   {0:2}   {1}{2:4}      {3}".format(
            self.filenumber, self.getfilename(headderdata),
            self.getsectorsused(headderdata),
            self.getfiletypecatstring(headderdata))

        t = self.getfiletype(headderdata)
        if(t == 4):
            # code
            s += "         {0:5},{1}".format(self.getcodestart(headderdata),
                                             self.getfilelength(headderdata))

        if(t == 1):
            # basic
            if(self.getautostartline(headderdata) >= 0):
                s += "         {0:5}".format(self.getautostartline(
                                             headderdata))

        return s

    def getautostartline(self, headderdata=None):
        """
        This returns the Autostart line number for a BASIC file.
        Returns the line number to automatically start at when a BASIC
        file is loaded.  Returns -1 if no Autostart line is specified,
        or -2 if not a BASIC file.
        headderdata is optional but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        if(headderdata[0] != 1):
            return -2

        val = headderdata[218] + 256 * headderdata[219]

        if(val > 9999):
            return -1

        return val

    def getvariableoffset(self, headderdata=None):
        """
        This returns the offset to the start of the variable area in a
        BASIC file.  If this is the same as the length of the BASIC file
        then there are no variables saved with the program.  Returns the
        byte offset to the start of the variables in the file, or -2 if
        this object is not a BASIC file.
        headderdata is optional but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        if(headderdata[0] != 1):
            return -2

        return headderdata[216] + 256 * headderdata[217]

    def getcodestart(self, headderdata=None):
        """
        This returns the address where a code file was saved from, and
        is the sugested address to load it to.  Returns the code
        address for a code block, or -2 if this object is not a code
        file.
        headderdata is optional but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        if(headderdata[0] != 4 and headderdata[0] != 7):
            return -2

        return headderdata[214] + 256 * headderdata[215]

    def getvariableletter(self, headderdata=None):
        """
        This returns the character of the variable described by an
        array.  Returns the character value of a variable, or None if
        this object is not a number or character array.
        headderdata is optional but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        if(headderdata[0] != 2 and headderdata[0] != 3):
            return None

        return chr((headderdata[216] & 127) | 64)

    def getvariablename(self, headderdata=None):
        """
        This returns the name of the variable described by an array.
        This is the letter name of the array, followed by '$' if it is a
        character array.
        Returns the name of a variable, or null if this object is not a
        number or character array.
        headderdata is optional but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        if(headderdata[0] != 2 and headderdata[0] != 3):
            return None

        return self.getvariableletter(headderdata) + \
            ("$" if headderdata[0] == 3 else "")

    def getarraydescriptor(self, headderdata=None):
        """
        This returns the array descriptor of an array.
        The descriptor is an 8 bit number.  The lower 6 bits hold the
        ASCII lower 6 bits of the variable name (must be a letter of the
        alphabet).  Bits 6 and 7 describe what type of array the file.
        They are 64 for a character array, 128 for a number array, and
        192 for a string array.

        Returns the array descriptor of the array, or -1 if this
        object is not a number or character array.

        headderdata is optional but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        if(headderdata[0] != 2 and headderdata[0] != 3):
            return -1

        return headderdata[216]

    def getsnapshotregisters(self, headderdata=None):
        """
        This returns a dictionary of all the registers in a snapshot.
        It returns None if this file is not a valid snapshot file
        headderdata is optional but saves resources.

        The dictionary returned has the following keys:
        The Registers A, F, BC, DE, HL, IY, and IX are the standard Z80
        registers.
        A', F', BC', DE', HL' are the alternate registers.
        PC is the program counter, SP is the stack pointer.
        I is the interupt register, and R the refresh register.
        IM is the interupt mode.
        IFF1, and IFF2 are the interupt flags denoting whether interupts
        are enabled or disabled.
        RAMbank denotes which RAM bank is paged onto loacation 0xC000.
        Screen denotes which screen is being displayed (0 if screen in
        RAM 5 (at 0x4000), and 1 if from RAM 7.
        ROM is 0 if 128K editor ROM paged in, and 1 if 48K ROM in place.
        IgnorePageChange is 1 if 0x7FFD is locked until a hard reset
        occurs, and 1 if it can be changed.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        if(headderdata[0] != 5 or headderdata[0] != 9):
            return None

        regs = {}
        # add registers
        regs["IY"] = headderdata[220] + 256 * headderdata[221]
        regs["IX"] = headderdata[222] + 256 * headderdata[223]
        regs["DE'"] = headderdata[224] + 256 * headderdata[225]
        regs["BC'"] = headderdata[226] + 256 * headderdata[227]
        regs["HL'"] = headderdata[228] + 256 * headderdata[229]
        regs["F'"] = headderdata[230]
        regs["A'"] = headderdata[231]
        regs["DE"] = headderdata[232] + 256 * headderdata[233]
        regs["BC"] = headderdata[234] + 256 * headderdata[235]
        regs["HL"] = headderdata[236] + 256 * headderdata[237]
        regs["I"] = headderdata[239]
        # value of interupt mode is coded in the I register
        regs["IM"] = 1 if (regs["I"] == 0 or regs["I"] == 63) else 2
        regs["SP"] = headderdata[240] + 256 * headderdata[241]

        # load up memory
        mem = self.getfiledata(False, headderdata)

        # handle 128K specific stuff
        if(headderdata[0] == 9):
            # get which rambank is paged in
            regs["RAMbank"] = mem[0] & 7
            # get which screen
            regs["Screen"] = (mem[0] >> 3) & 1
            # get which ROM
            regs["ROM"] = (mem[0] >> 4) & 1
            # are we ignoreing output to 0x7FFD
            regs["IgnorePageChange"] = (mem[0] >> 5) & 1
            # now set mem to be which pages are loaded
            # RAM5 is at 0x4000 to 0x7FFF
            # RAM2 is at 0x8000 to 0xBFFF
            # paged RAM is at 0xC000 to 0xFFFF
            # Ram banks are offset by 1 byte at [0] which is a record of which
            # bank is paged in
            mem = mem[0x14001:0x18000] + mem[0x8001:0xC000] + mem[
                regs["RAMbank"] * 0x4000 + 1:(regs["RAMbank"] + 1) * 0x4000]

        # now we have an image of the working RAM at time of snapshot, and can
        # figure out where the stack is
        # extract stack
        mem = mem[regs["SP"] - 0x4000:regs["SP"] - 0x4000 + 6]

        regs["R"] = mem[1]
        regs["IFF1"] = (mem[0] >> 2) & 1
        regs["IFF2"] = regs["IFF1"]
        regs["F"] = mem[2]
        regs["A"] = mem[3]
        regs["PC"] = mem[4] + 256 * mem[5]

        # SP contains values for the R register, AF, and PC pushed on it, hence
        # needs to be 6 higher
        regs["SP"] = (regs["SP"] + 6) & 0xFFFF

        return regs

    def __str__(self, headderdata=None):
        """
        This returns a basic String summary of the DiscipleFile object.
        This is the same as for a detailed catalog entry but with
        excess spaces stripped
        headderdata is optional but saves resources.
        """

        return self.getfiledetailsstring(headderdata).strip()

    def getdisciplefiledetails(self, headderdata=None):
        """
        This returns details of the DiscipleFile object usefull for
        debugging.
        headderdata is optional but saves resources.
        """

        # if no headder supplied, need to load it up
        if(headderdata is None):
            headderdata = self.getheadder()

        t = self.getfiletype(headderdata)

        s = 'filenumber: {0}\nFile name: "{1}"\n'.format(
            self.filenumber, self.getfilename(headderdata))
        s += "File type: {0} = {1}\n".format(
            t, self.getfiletypestring(headderdata))
        s += "File length: {0}({0:X})\n".format(
            self.getfilelength(headderdata))

        if(t == 1):  # basic
            s += "Autostart: {0}\nVariable offfset: {1}({1:X})\n".format(
                self.getautostartline(headderdata),
                self.getvariableoffset(headderdata))

        elif(t == 2 or t == 3):  # number array, or string array
            s += "variable name: {0}\n".format(
                self.getvariablename(headderdata))

        elif(t == 4 or t == 7):  # code or screen$
            s += "code start address: {0}({0:X})\n".format(
                self.getcodestart(headderdata))

        s += "file details: {0}\n".format(
            self.getfiledetailsstring(headderdata))
        s += "directory entry address: T={0[0]} S={0[1]} offset={1}\n".format(
            GetDirectoryEntryPosition(self.filenumber),
            ((self.filenumber - 1) & 1) * 256)
        s += "Number of sectors used: {0}\n".format(
            self.getsectorsused(headderdata))

        track = headderdata[13]
        sector = headderdata[14]
        i = self.getsectorsused(headderdata)

        s += "Sector chain: "
        while(i > 0):
            s += " {0};{1}({2:X})".format(
                track, sector,
                self.image.getsectorposition(track & 127, sector, track >> 7))
            sectordata = self.image.getsector(track & 127, sector, track >> 7)
            track = sectordata[510]
            sector = sectordata[511]
            i -= 1

        s += " {0};{1}".format(track, sector)

        return s


class DiscipleImage:
    """A class that holds a +D/Disciple disk image."""

    def __init__(self, fileName=None, accessmode="rb"):
        self.ImageSource = "Undefined"
        self.ImageFormat = "Unknown"

        if(fileName is not None):
            self.setfilename(fileName, accessmode=accessmode)

    def setfile(self, filehandle, form="Unknown"):
        """
        sets the source for the disciple image to be an open file
        """

        self.ImageSource = "File"
        self.filehandle = filehandle
        self.setimageformat(form)

    def setfilename(self, filename, form="Unknown", accessmode="rb"):
        """
        sets the source for the disciple image to be a file with the
        given name.
        Will close this file upon deletion of this object
        """
        try:
            self.filehandle = open(filename, accessmode)
        except:
            raise spectrumtranslate.SpectrumTranslateError(
                'can not open "{0}" for reading'.format(filename))
            return

        self.ImageSource = "FileName"
        self.setimageformat(form)

    def setbytes(self, bytedata, form="Unknown"):
        """
        Sets the source for the disciple image to be a byte string, a
        list or tuple of ints or longs, or can also be bytes or
        bytearray in python 3.
        """

        _checkisvalidbytes(bytedata, "bytedata")

        # convert bytedata to list of ints
        self.bytedata = _validbytestointlist(bytedata)

        self.ImageSource = "Bytes"
        self.setimageformat(form)

    def setimageformat(self, form):
        """
        sets the format for the image:
        "MGT" is side 0 track 0, side 1 track 0, side 0 track 1, side 1
        track 1, etc
        "IMG" is side 0 track 0, side 0 track 1, side 0 track 2, ...
        side 0 track 79, side 1 track 0, side 1 track 1, etc
        """
        if(form == "MGT" or form == "IMG" or form == "Unknown"):
            self.ImageFormat = form
            return

        raise spectrumtranslate.SpectrumTranslateError(
            'Only valid image formats are "MGT" and "IMG"')

    def get_offset_and_bit_from_track_and_sector(self, track, sector):
        """calculate offset & bit of this track & sector in sectorMap"""
        o = (track & 127) + (80 if track >= 128 else 0) - 4
        o *= 10
        o += sector - 1
        b = 1 << (o % 8)
        o = o // 8

        return o, b

    def guessimageformat(self):
        """
        This method will try and work out and set the image format for
        this image.
        """

        # simplest way I can think of is to try out the different formats
        self.ImageFormat = "MGT"
        if(self.isimagevalid(True)):
            return self.ImageFormat

        self.ImageFormat = "IMG"
        if(self.isimagevalid(True)):
            return self.ImageFormat

        self.ImageFormat = "Unknown"
        return self.ImageFormat

    def __del__(self):
        # close filehandle if needed
        if(self.ImageSource == "FileName"):
            self.filehandle.close()

    def getsectorposition(self, track, sector, head=-1):
        """
        Calculate the offset in the buffer for the specified sector.
        This takes into account the image format.  track is the track
        from 0 to 79, sector is the sector from 1 to 10, head is the
        head from 0 to 1.  head is optional as often the head is embeded
        as bit 7 of track.  If head is not defined or set to -1 then
        this method will extract the head from bit 7 of track, and
        binary and with 127 to remove bit 7.  Returns the offset in
        bytes to the start of the specified sector.
        """

        # if we don't know what format we've got then guess
        if(self.ImageFormat == "Unknown"):
            self.guessimageformat()

        # is head part of track?
        if(head == -1):
            head = (track >> 7) & 1
            track &= 127

        # sanity check on inputs
        if(head < 0 or head > 1):
            raise spectrumtranslate.SpectrumTranslateError(
                'Valid head values are 0 and 1')

        if(sector < 1 or sector > 10):
            raise spectrumtranslate.SpectrumTranslateError(
                'Valid sector values are 1 to 10 inclusive')

        if(track < 0 or track > 79):
            raise spectrumtranslate.SpectrumTranslateError(
                'Valid track values are 0 to 79 inclusive')

        if(self.ImageFormat == "MGT"):
            return ((sector - 1) + (head * 10) + (track * 20)) * 512

        # otherwise is img file format
        return ((sector - 1) + (head * 800) + (track * 10)) * 512

    def getsector(self, track, sector, head=-1):
        """Returns a list of ints of the sector requested."""

        # where is sector we're after
        pos = self.getsectorposition(track, sector, head)

        if(self.ImageSource == "Bytes"):
            return self.bytedata[pos:pos + 512]

        elif(self.ImageSource == "File" or self.ImageSource == "FileName"):
            if(self.filehandle.tell() != pos):
                self.filehandle.seek(pos)

            # in python 2 convert byte string to list of ints
            if(not _PYTHON_VERSION_HEX > 0x03000000):
                return [ord(x) for x in self.filehandle.read(512)]

            # return list in python 3
            return [x for x in self.filehandle.read(512)]

        else:
            raise spectrumtranslate.SpectrumTranslateError(
                'Uninitiated DiscipleImage')

    def writesector(self, data, track, sector, head=-1):
        """Writes supplied sector to image. data has to be 512 long and
        is the data to be written to the sector.  In python 2 it must be
        a list or tuple of ints or longs, and in python 3 it can also be
        a bytearray or bytes.  If the image is not initiated, then it
        will be set up as a byte image.  You will need to save off the
        data at the end to save any changes.
        """

        _checkisvalidbytes(data, "data must be 512 bytes long, and")
        if(len(data) != 512):
            raise spectrumtranslate.SpectrumTranslateError("data must be a \
512 bytes in length, and a list or tuple of int or long, or a byte string in \
python 2, or of type 'byte' or 'bytearray' in python 3.")

        # if we've got uninitiated DiscipleImage then set up as bytearray
        if(self.ImageSource == "Undefined"):
            self.setbytes([0] * 819200)

        # convert data to list of ints
        data = _validbytestointlist(data)

        # where is sector we're after
        pos = self.getsectorposition(track, sector, head)
        if(self.ImageSource == "Bytes"):
            self.bytedata = self.bytedata[:pos] + data + self.bytedata[
                pos + 512:]

        elif(self.ImageSource == "File" or self.ImageSource == "FileName"):
            # have we got overwrite access?
            if(len(self.filehandle.mode) != 3 or
               0 in [c in self.filehandle.mode for c in "r+b"]):
                # if not we can't write to it
                raise spectrumtranslate.SpectrumTranslateError(
                    'DiscipleImage not opened with access mode rb+')

            # memory map the sector in the file
            mm = _mmap(self.filehandle.fileno(), 0)
            # write the data
            if(_PYTHON_VERSION_HEX > 0x03000000):
                mm[pos:pos + 512] = bytes("".join([chr(x) for x in data]),
                                          'utf-8')
            else:
                mm[pos:pos + 512] = "".join([chr(x) for x in data])
            mm.flush()
            mm.close()

        # this should not happen, but be cautious
        else:
            raise spectrumtranslate.SpectrumTranslateError(
                'Uninitiated DiscipleImage')

    def deleteentry(self, entrynumber):
        """
        This method deletes the specified entry in this disk image.
        Valid entry numbers are 1 to 80.
        """

        # check input
        if(entrynumber > 80 or entrynumber < 1):
            raise spectrumtranslate.SpectrumTranslateError(
                'Invalid file enty number (must be 1 to 80 inclusive).')

        # work out track, sector, and offset for file descriptor byte for
        # file
        headderstart = ((entrynumber - 1) & 1) * 256
        track, sector = GetDirectoryEntryPosition(entrynumber)

        sectordata = self.getsector(track, sector)
        # set file type byte to 0 to mark it deleted
        sectordata[headderstart] = 0

        self.writesector(sectordata, track, sector)

    def isimagevalid(self, deeptest=False):
        """
        This method will go through all the file entries in an image and
        ensure they have propper values, and that sectors don't overlap.
        N.B. this might return False for an image that works in real
        life (like hidden sectors in the FAT table that aren't in the
        file chain).
        if deeptest is True, then will go through each track and sector
        of a file ensureing that it matches the FAT. This will involve
        loading lots of sectors and may take some time.
        """

        # check image source
        if(self.ImageSource == "Undefined"):
            return False

        if(self.ImageFormat == "Unknown"):
            self.guessimageformat()
            if(self.ImageFormat == "Unknown"):
                return False

        # todo handle non 80 track, 2 sided disks
        if(self.ImageSource == "Bytes" and (not hasattr(self, "bytedata") or
           len(self.bytedata) != 819200)):
            return False

        # create empty sector map
        sectorMap = [0] * 195

        track = -1
        sector = -1
        # iterate through all headders
        for entry in range(1, 81):
            headderstart = ((entry - 1) & 1) * 256
            # only load sector if needed
            newtrack, newsector = GetDirectoryEntryPosition(entry)
            if(track != newtrack or sector != newsector):
                track = newtrack
                sector = newsector
                headder = self.getsector(track, sector)

            # is filetype (excluding flags) consistent with valid file?
            filetype = headder[headderstart] & 31
            # ignore empty directory entries
            if(filetype == 0):
                continue

            if(filetype > 11):
                return False

            # check sector map
            sectorcount = 0

            for i in range(195):
                if(sectorMap[i] & headder[headderstart + 15 + i] != 0):
                    # we have conflicting FAT entries
                    return False

                # update sector map
                sectorMap[i] |= headder[headderstart + 15 + i]
                # work out number of sectors used
                sectorcount += bin(headder[headderstart + 15 + i]).count("1")

            # check number of sectors line up with FAT table
            if(sectorcount != headder[headderstart + 12] + 256 *
                    headder[headderstart + 11]):
                return False

            # compare file length against sectors used in FAT table for
            # length workoutable files
            filelen = -1
            if(filetype == 1 or filetype == 2 or filetype == 3 or
               filetype == 4 or filetype == 7 or filetype == 13):
                # 1=basic,2=number array,3=string array,4=code,7=screen$,
                # 13=unidos create file
                filelen = headder[headderstart + 212] + \
                          256 * headder[headderstart + 213]
            elif(filetype == 5):
                # 48K snapshot
                filelen = 49152  # 3 * 16K ram banks
            elif(filetype == 9):
                # 128K snapshot
                # 1 byte page register value + 8 16K ram banks
                filelen = 131073
            elif(filetype == 10):
                # opentype
                filelen = headder[headderstart + 212] + \
                          256 * headder[headderstart + 213] + \
                          65536 * headder[headderstart + 210]
            elif(filetype == 11):
                # execute
                filelen = 510

            # BASIC, code, number array, string array, or screen have 1st
            # 9 bytes of file as copy of headder data.
            if((filetype > 0 and filetype < 5) or filetype == 7):
                filelen += 9

            # compare it to number of sectors used
            if(filelen != -1):
                # work out how many sectors should be used. round up
                estimatedsectors = (filelen + 509) // 510
                # now see if matches
                if(sectorcount != estimatedsectors):
                    return False

            # check start sector is in FAT
            startsector = headder[headderstart + 14]
            starttrack = headder[headderstart + 13]

            # calculate offset & bit of this track & sector in sectorMap
            o, b = self.get_offset_and_bit_from_track_and_sector(starttrack,
                                                                 startsector)
            # check if is sector owned by this file
            if((sectorMap[o] & b) != b):
                return False

            if(deeptest):
                # go through file chain matching against sector map &
                # ensure sector map is empty at the end

                # get map of sectors used
                sm = headder[headderstart + 15:headderstart + 210]

                # if we don't know size of file then estimate it
                if(filelen == -1):
                    filelen = sectorcount * 510

                # get start track & sector
                t = starttrack
                s = startsector

                # now move through file sectors
                while(sectorcount > 0):
                    # have we reached early end of file?
                    if(t == 0 and s == 0):
                        return False

                    # do we have valid sector?
                    if((t & 127) > 79 or t < 4 or s < 1 or s > 10):
                        return False

                    # calculate offset & bit of this track & sector in
                    # sectorMap
                    o, b = self.get_offset_and_bit_from_track_and_sector(t, s)
                    # check if is sector owned by this file
                    if((sm[o] & b) != b):
                        return False

                    # remove from copy of sectorMap
                    sm[o] -= b

                    # load next sector in chain
                    sectordata = self.getsector(t, s)

                    # update track & sector
                    t = sectordata[510]
                    s = sectordata[511]
                    # update number of bytes left to copy
                    filelen -= min(510, filelen)
                    # decrement number of sectors left to fetch
                    sectorcount -= 1

                # track & sector of last sector read should be 0
                if(t != 0 and s != 0):
                    return False

                # sectorMap should now be blank, otherwise there are
                # unused sectors.
                # in theory this shouldn't happen as each sector in the
                # chain is goine through, and we compare the number of
                # sectors in the FAT table with the number stated in the
                # directory entry that this file uses.
                # Still just in case...
                for i in sm:
                    if(i != 0):
                        return False

        return True

    def writefile(self, headder, filedata, position=-1):
        """This method will write the supplied filedata to the disk
        image with the headder as specified by headder.  headder has to
        be a 256 byte list or tuple of ints or longs (or a bytes or
        a bytearraystring object in python 3) for the file.  Bytes 11 to
        209 will be ignored and overwritten, but the other bytes have to
        correct for the file.  filedata is then written to the disk.
        position is optional, but specifies into which file entry you
        want this saved.  If it's -1 then it will be saved to the first
        free headder slot.
        """

        # first check input
        if(len(headder) != 256):
            raise spectrumtranslate.SpectrumTranslateError(
                "Header block must be 256 bytes long.")

        _checkisvalidbytes(headder, "headder")
        _checkisvalidbytes(filedata, "filedata")

        if(position != -1 and position < 1 and position > 80):
            raise spectrumtranslate.SpectrumTranslateError(
                "Invalid file position.")

        # find first empty headder slot and build map of used sectors
        i = 1
        sectorcount = 0
        # create empty sector map
        sectorMap = [0] * 195
        while(i <= 80):
            t, s = GetDirectoryEntryPosition(i)
            sector = self.getsector(t, s)
            for headderoffset in (0, 256):
                # if empty check if we can use it
                if(sector[headderoffset] == 0):
                    if(position == -1):
                        position = i

                # if used then make note of sectors used if we're not
                # overwriting
                elif(position != i):
                    for l in range(195):
                        if(sectorMap[l] & sector[headderoffset + 15 + l] != 0):
                            # we have conflicting FAT entries
                            raise spectrumtranslate.SpectrumTranslateError(
                                "Corrupt FAT table in destination image.")

                        # update sector map
                        sectorMap[l] |= sector[headderoffset + 15 + l]
                        # work out number of sectors used
                        sectorcount += bin(
                            sector[headderoffset + 15 + l]).count("1")

                i += 1

        # if no empty headders and not wanting to over-write then raise
        # error
        if(position == -1):
            raise spectrumtranslate.SpectrumTranslateError(
                "No empty headder entries.")

        # check if we have enogh sectors. 510 bytes can be saved per
        # sector
        sectorsused = (len(filedata) + 509) // 510

        if(sectorsused + sectorcount > 1560):
            raise spectrumtranslate.SpectrumTranslateError(
                "Not enough space on disk for file.")

        # define nested function to search for next unused sector
        def NextUnusedSector(sectormap):
            for i in range(195):
                if(sectormap[i] == 255):
                    continue

                for b in range(8):
                    if(sectormap[i] & (1 << b) == 0):
                        # work out track & sector
                        s = i * 8 + b
                        t = (s // 10) + 4
                        if(t > 79):
                            t += 48

                        s = (s % 10) + 1
                        return [t, s]

            raise spectrumtranslate.SpectrumTranslateError("Image full.")

        # make copy of headder localy to alter
        headder = _validbytestointlist(headder)

        # clear FAT table for file headder
        for i in range(195):
            headder[i + 15] = 0

        # get starting sector, and remember it in headder
        t, s = NextUnusedSector(sectorMap)

        headder[13] = t
        headder[14] = s

        # make note of number of sectors
        headder[12] = sectorsused & 0xFF
        headder[11] = sectorsused // 0x100

        # now save file
        l = 0
        while(l < len(filedata)):
            # mark sector as being used in disk FAT & file FAT
            o, b = self.get_offset_and_bit_from_track_and_sector(t, s)
            sectorMap[o] |= b
            headder[15 + o] |= b

            # work out how much to save in this sector
            chunklength = min(len(filedata) - l, 510)

            # work out what next track & sector will be
            # will be 0,0 if last sector in chain
            if(len(filedata) - l <= 510):
                nextsector = [0, 0]

            else:
                nextsector = NextUnusedSector(sectorMap)

            # create sector padding with 0 and finishing off with next
            # sector
            sectordata = filedata[l:l + chunklength] + \
                [0] * (510 - chunklength) + nextsector
            self.writesector(sectordata, t, s)

            # update counters and next sectors
            t, s = nextsector
            l += chunklength

        # now save headder
        # work out track, sector, and offset for headder for file
        headderstart = ((position - 1) & 1) * 256
        track, sector = GetDirectoryEntryPosition(position)

        sectordata = self.getsector(track, sector)
        sectordata = sectordata[:headderstart] + headder + sectordata[
            headderstart + 256:]
        self.writesector(sectordata, track, sector)

    def fileindexfromname(self, filename, wantdeleted=False):
        """Returns a list of directory positions for the supplied
        filename. It returns an empty list if the filename is not found.
        """

        hits = []

        # ensure filename is valid
        filename = _validateandconvertfilename(filename)

        # search to see if file exists
        i = 1
        while(i <= 80):
            t, s = GetDirectoryEntryPosition(i)
            sector = self.getsector(t, s)
            for headderoffset in (0, 256):
                # if is the file we're after then note it
                if(((not wantdeleted and sector[headderoffset] != 0) or
                    (wantdeleted and sector[headderoffset] == 0)) and
                   sector[headderoffset + 1:headderoffset + 11] == filename):
                    hits += [i]

                i += 1

        return hits

    def writebasicfile(self, filedata, filename, position=-1, autostartline=-1,
                       varposition=-1, overwritename=True):
        """This method writes a BASIC file to the disk image.  filedata
        is a list or tuple of ints or longs (or a bytes or bytearray
        object in python 3) of the BASIC file (with or without extra
        variables).  filename is the name to save the BASIC file as on
        the disk image.  Normaly this method would overwrite an existing
        file with the same name.  If overwritename is False then it will
        not overwrite the existing file.  Haveing two files with the
        same name on a disk is not impossible but is confusing.
        position can be used to specify which directory entry to save
        the file details at.  If -1 it will use the first available
        empty slot (assuming that we're not overwriting a file with the
        same name), otherwise it will save the file in this slot even if
        a file with the same name exists in another directory slot.
        autostartline specifies the line to automatically start running
        if loaded.  If not specified then no automatic start line is
        set.  varposition specifies the offset to the variables being
        saved with the BASIC program.  If set to None then it will save
        the file as if there were no variables, if -1 then this method
        will work out where the variables are (if any).  Only set this
        manually if you know the correct value as this could cause
        confusion if wrong.  If in doubt use -1.
        Filenames consist of up to 10 characters as either a string, or
        a list of strings or list of numbers for the character values.
        The method will raise an exception if the filename is invalid.
        """

        # validate input
        if(len(filedata) > 65535 - 23755):
            raise spectrumtranslate.SpectrumTranslateError(
                "Data too big to fit in spectrum memory.")

        _checkisvalidbytes(filedata, "filedata")

        # create headder and validate filename
        headder = [0] + _validateandconvertfilename(filename) + ([0] * 245)

        # set basic file
        headder[0] = 1
        headder[211] = 0
        # set length
        headder[212] = len(filedata) & 255
        headder[213] = len(filedata) // 256
        # set start
        headder[214] = 23755 & 255
        headder[215] = 23755 // 256
        # set variable offset
        if(varposition is None or varposition == -1):
            # work out position of variables
            varposition = spectrumtranslate.getvariableoffset(filedata)

        headder[216] = varposition & 255
        headder[217] = varposition // 256

        # setautostart
        if(autostartline < 0 or autostartline > 9999):
            autostartline = 0x8000

        headder[218] = autostartline & 255
        headder[219] = autostartline // 256

        # outputfile
        # first work out if we're overwriting existing filename
        if(overwritename):
            # if so get index or -1
            hits = self.fileindexfromname(headder[1:11])
            position = -1 if len(hits) == 0 else hits[0]

        # NB basic, code, and variable files have 9 byte extra headder
        # saved before the filedata
        self.writefile(headder, headder[211:220] + filedata, position)

    def writecodefile(self, filedata, filename, position=-1,
                      codestartaddress=0, overwritename=True,
                      coderunaddress=0):
        """This method writes a code file to the disk image.  filedata
        is a list or tuple of ints or longs (or a bytes or bytearray
        object in python 3) of the code.  filename is the name to save
        the code file as on the disk image.  Normaly this method would
        overwrite an existing file with the same name.  If overwritename
        is False then it will not overwrite the existing file.  Haveing
        two files with the same name on a disk is not impossible but is
        confusing.  position can be used to specify which directory
        entry to save the file details at.  If -1 it will use the first
        available empty slot (assuming that we're not overwriting a file
        with the same name), otherwise it will save the file in this
        slot even if a file with the same name exists in another
        directory slot.  codestartaddress specifies the address to which
        the code should be loaded.  coderunaddress specifies the
        address which should be called after the code is loaded.  If 0
        it is ignored.  Filenames consist of up to 10 characters as
        either a string, or a list of strings or list of numbers for the
        character values.  The method will raise an exception if the
        filename is invalid.
        """

        # validate input
        if(len(filedata) > 65535):
            raise spectrumtranslate.SpectrumTranslateError(
                "Data too big to fit in spectrum memory.")

        # create headder and validate filename
        headder = [0] + _validateandconvertfilename(filename) + ([0] * 245)

        # set code file
        headder[0] = 4
        headder[211] = 3
        # set length
        headder[212] = len(filedata) & 255
        headder[213] = len(filedata) // 256
        # set codestartaddress
        headder[214] = codestartaddress & 255
        headder[215] = codestartaddress // 256
        # set coderunaddress
        headder[218] = coderunaddress & 255
        headder[219] = coderunaddress // 256

        # outputfile
        # first work out if we're overwriting existing filename
        if(overwritename):
            # if so get index or -1
            hits = self.fileindexfromname(headder[1:11])
            position = -1 if len(hits) == 0 else hits[0]

        # NB basic, code, and variable files have 9 byte extra headder
        # saved before the filedata
        self.writefile(headder, headder[211:220] + filedata, position)

    def writearrayfile(self, filedata, filename, VariableDescriptor,
                       position=-1, overwritename=True):
        """This method writes an array file to the disk image.  filedata
        is a list or tuple of ints or longs (or a bytes or bytearray
        object in python 3) of the array data.  filename is the name to
        save the file as on the disk image.  Normaly this method would
        overwrite an existing file with the same name.  If overwritename
        is False then it will not overwrite the existing file.  Haveing
        two files with the same name on a disk is not impossible but is
        confusing.  position can be used to specify which directory
        entry to save the file details at.  If -1 it will use the first
        available empty slot (assuming that we're not overwriting a file
        with the same name), otherwise it will save the file in this
        slot even if a file with the same name exists in another
        directory slot.  The VariableDescriptor is composed of the lower
        6 bits of the variable name (a one letter name), and the upper 2
        bits are 64 for a character array, 128 for a number array, and
        192 for a string array.  Filenames consist of up to 10
        characters as either a string, or a list of strings or list of
        numbers for the character values.  The method will raise an
        exception if the filename is invalid.
        """

        # validate input
        if(len(filedata) > 65535 - 23755):
            raise spectrumtranslate.SpectrumTranslateError(
                "Data too big to fit in spectrum memory.")

        # create headder and validate filename
        headder = [0] + _validateandconvertfilename(filename) + ([0] * 245)

        # set variable file
        headder[211] = 1 if VariableDescriptor & 192 == 128 else 2
        headder[0] = headder[211] + 1
        # set length
        headder[212] = len(filedata) & 255
        headder[213] = len(filedata) // 256
        # set variabledescriptor
        headder[216] = VariableDescriptor

        # outputfile
        # first work out if we're overwriting existing filename
        if(overwritename):
            # if so get index or -1
            hits = self.fileindexfromname(headder[1:11])
            position = -1 if len(hits) == 0 else hits[0]

        # NB basic, code, and variable files have 9 byte extra headder
        # saved before the filedata
        self.writefile(headder, headder[211:220] + filedata, position)

    def writescreenfile(self, filedata, filename, position=-1,
                        overwritename=True):
        """This method writes a screen file to the disk image.  filedata
        is a list or tuple of ints or longs (or a bytes or bytearray
        object in python 3) of the screen.  filename is the name to save
        the file as on the disk image.  Normaly this method would
        overwrite an existing file with the same name.  If overwritename
        is False then it will not overwrite the existing file.  Haveing
        two files with the same name on a disk is not impossible but is
        confusing.  position can be used to specify which directory
        entry to save the file details at.  If -1 it will use the first
        available empty slot (assuming that we're not overwriting a file
        with the same name), otherwise it will save the file in this
        slot even if a file with the same name exists in another
        directory slot.  Filenames consist of up to 10 characters as
        either a string, or a list of strings or list of numbers for the
        character values.  The method will raise an exception if the
        filename is invalid.
        """

        # validate input
        if(len(filedata) != 6912):
            raise spectrumtranslate.SpectrumTranslateError(
                "filedata is wrong length for a spectrum screen file.")

        # create headder and validate filename
        headder = [0] + _validateandconvertfilename(filename) + ([0] * 245)

        # set screen file
        headder[0] = 7
        headder[211] = 3
        # set length
        headder[212] = 0
        headder[213] = 0x1B
        # set codestartaddress
        headder[214] = 0
        headder[215] = 0x40

        # outputfile
        # first work out if we're overwriting existing filename
        if(overwritename):
            # if so get index or -1
            hits = self.fileindexfromname(headder[1:11])
            position = -1 if len(hits) == 0 else hits[0]

        # NB basic, code, and variable files have 9 byte extra headder
        # saved before the filedata
        self.writefile(headder, headder[211:220] + filedata, position)

    def iteratedisciplefiles(self):
        """
        This method allows a user to iterate through all the files in
        this image using for.
        eg:
        disciplefiles = [df for df in di.iteratedisciplefiles()]
        """

        i = 1
        while(i <= 80):
            yield DiscipleFile(self, i)
            i += 1


def usage():
    """
    returns the command line arguments for disciplefile as a string.
    """

    return"""usage: python disciplefile.py instruction [args] infile
    outfile

    moves data from infile which should be a disciple disc image file or
    file data and outputs it to outfile.

    instruction is required and specifies what you want to do.  It must
    be 'list', 'delete', 'copy', 'extract', or 'create'.  'list' will
    list the contents of the specified image file.  'delete' will output
    a copy of the input with the specified file(s) deleted.  'extract'
    extracts the data from an image file entry to wherever you want.
    'copy' copies the specified file(s) from one image to another.
    'create' creates a new file in outfile useing the supplied file
    data.  With copy, create, and delete a new disk image will be
    created if outfile is not an image file.

    infile and outfile are required unless reading from the standard
    input or outputting to the standard output.  Usually arguments are
    ignored if they don't apply to the selected instruction.

    For the extract instruction, the index of the image file you want to
    extract must be specified before the filenames.

    For the delete and copy instructions, the index of the file in the
    disk image you want to copy or delete must be specified before the
    filenames.  You can have ranges of indexes if you want to delete or
    copy more that one file from the image.  The syntax is the same as
    for the -s flag.  You can use the -s flag in the instruction in
    which case you should not specify a file index before the input or
    output files.

    If using the create instruction, you must specify what you are
    creating imediatly after the create instruction.  Valid options are
    'basic', 'code', 'array', and 'screen'.  You must also specify the
    filnename for the file with the -filename flag.  If creating an
    array, you must also specify the name and type of array with the
    -arraytype and -arrayname flags.

    general flags:
    -o specifies that the output from this program is to be directed to
       the standard output and not outputfile which should be omited.
       It can be used for all instructions.
    --tostandardoutput same as -o.
    -i specifies that this program gets it's data from the standard
       input and not inputfile which should be omited.  It can be used
       for all instructions.
    --fromstandardinput same as -i.
    -s specifies which file entries you want.  These are the same as
       returned by the list instruction.  You can specify more than one,
       seperated by commas, and can even specify ranges of them with a
       minus.  The numbers are assumed to be decimal unless preceded by
       0x in which case they are assumed to be hexadecimal.  For example
       2,0x10-20,23 will specify entry 2, 16 to 20 inclusive, and 23.
       This flag can be used in the list and delete commands.
    --specifyfiles same as -s.
    --specificfiles same as -s.

    list flags:
    -d specifies that we want all information about each file entry
       divided by tabs.  All entries begin with the index of the entry
       in the image file, followed by the file name (there might be a
       name in an empty slot if the file has been deleted), the file
       type number, the filetype string, the number of sectors used on
       the disk, and the file length. Further data depends on the file
       type.
       For Program files, The autostart line number (or -1 if there
       isn't one), and the offset in bytes to the atached variables
       (will be the same as the length if there are no variables)
       follow.
       For Code files there follows the address where the code was saved
       from (and would automatically be loaded to).  Then is the autorun
       address (or 0 if no autorun).
       For array files there follows the the array letter, the array
       variable name, and the array descriptor specifying what sort of
       array it contains.
    --details is the same as -d.
    -l specifies that you want empty file slots to be returned in the
       listing.  Normally these are omitted from a listing for increased
       clarity and brevity.
    --listempty same as -l.
    -c specifies that after the listing is complete you want the number
       of bytes free on the disk to be displayed on a new line.
    --capacity same as -c.
    -ck same as -c but number of free K on disk is listed.  If the
        number seems odd then remember that only 510 bytes can be fitted
        in per sector.
    -cs same as -c but number of free sectors on disk is listed.

    copy flags:
    -p specifies the positions where you want to copy the file entries
       to.  You can specify more than one, seperated by commas, and can
       even specify ranges of them with a minus.  The numbers are
       assumed to be decimal unless preceded by 0x in which case they
       are assumed to be hexadecimal.  For example 2,0x10-20,23 will
       specify entry 2, 16 to 20 inclusive, and 23.  These positions
       will be worked through in order as the source files are copied
       across.  If there are more destination positions than source
       files, then the extra positions will be ignored.  If there are
       fewer specified destination positions than files to copy, then
       the extra files will be saved to the first empty directry entries
       in the disk image.
    --pos same as -p.
    --position same as -p.

    create flags:
    --autostart This is used when creating a BASIC file to specify the
                autostart line, or with code files when you are
                specifying the autostart address to run when loaded.
    --variableoffset This is used to specify the offset into a BASIC
                     listing where the variables start.  If not
                     specified, the program will reliably work out where
                     the variables are unless the BASIC file is very
                     non-standard.  So this flag whould not be used
                     unless you have a very good reason.
    --donotoverwriteexisting The default mode of opperation is to
                             overwrite a file with the same name when
                             saving or finding the first available slot
                             if the filename has not been used before in
                             the disk image, and if the directory slot
                             has not been specified with the -p flag.
                             This flag overrides this so you can save a
                             file into the next avalable slot without
                             overwriting an existing file. It is
                             possible but confusing to have more than
                             one file with the same name.
    --origin This specifies the address for the origin of a code file.
    --arraytype This specifies the type of array file to create.  It
                must be followed by the type of array to create.  Valid
                options are:
                character or c for a character array, number or n for a
                number array, and string or s for a string.
    --arrayname This specifies the name for a saved array or string.  It
                must be followed by a single letter of the alphabet.
    -p This allows the user to specify where in the directory the file
       is saved.
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
                if('-' in n):
                    v = n.split('-', 1)
                    specifiedfiles += list(range(getint(v[0]),
                                                 getint(v[1]) + 1))

                else:
                    specifiedfiles += [getint(n)]

            if(len(specifiedfiles) == 0):
                return None

            return specifiedfiles

        except:
            return None

    try:
        i = 0
        mode = None
        error = None
        wantdetails = False
        fromstandardinput = False
        tostandardoutput = False
        inputfile = None
        outputfile = None
        entrywanted = None
        specifiedfiles = None
        listempty = False
        copyposition = []
        wantdiskcapacity = False
        capacityformat = "Bytes"
        creating = None
        creatingfilename = None
        creatingautostart = -1
        creatingvariableoffset = -1
        creatingoverwritename = True
        creatingorigin = 0
        creatingarraytype = None
        creatingarrayname = None

        # handle no arguments
        if(len(args) == 1):
            mode = 'help'

        # go through arguments analysing them
        while(i < len(args)-1):
            i += 1

            arg = args[i]
            if(arg == 'help' or arg == 'extract' or arg == 'list' or
               arg == 'delete' or arg == 'copy' or arg == 'create'):
                if(mode is not None):
                    error = "Can't have multiple commands."
                    break

                mode = arg
                continue

            if(mode == 'create' and creating is None):
                if(arg != 'basic' and arg != 'code' and arg != 'array' and
                   arg != 'screen'):
                    error = 'Must specify what type of file to create. Valid \
options are basic, code, array, and screen.'
                    break

                creating = arg
                continue

            if(arg == '-filename' or arg == '--filename'):
                i += 1
                creatingfilename = spectrumtranslate.stringtospectrum(args[i])
                continue

            if(arg == '-autostart' or arg == '--autostart'):
                i += 1
                try:
                    creatingautostart = getint(args[i])
                    continue

                except:
                    error = '{0} is not a valid autostart number.'.format(
                        args[i])
                    break

            if(arg == '-variableoffset' or arg == '--variableoffset'):
                i += 1
                try:
                    creatingvariableoffset = getint(args[i])
                    continue

                except:
                    error = '{0} is not a valid variable offset.'.format(
                        args[i])
                    break

            if(arg == '-donotoverwriteexisting' or
               arg == '--donotoverwriteexisting'):
                creatingoverwritename = False
                continue

            if(arg == '-origin' or arg == '--origin'):
                i += 1
                try:
                    creatingorigin = getint(args[i])
                    if(creatingorigin < 0 or creatingorigin > 65535):
                        error = 'code origin must be 0-65535 inclusive.'
                        break

                    continue

                except:
                    error = '{0} is not a valid code origin.'.format(
                        args[i])
                    break

            if(arg == '-arraytype' or arg == '--arraytype'):
                i += 1
                if(args[i] == 'character' or args[i] == 'c'):
                    creatingarraytype = 192
                    continue

                elif(args[i] == 'number' or args[i] == 'n'):
                    creatingarraytype = 128
                    continue

                elif(args[i] == 'string' or args[i] == 's'):
                    creatingarraytype = 64
                    continue

                else:
                    error = '{0} is not a valid array type (must be \
character, number or string).'.format(args[i])
                    break

            if(arg == '-arrayname' or arg == '--arrayname'):
                i += 1
                creatingarrayname = args[i]
                if(len(creatingarrayname) == 1 and
                   creatingarrayname.isalpha()):
                    continue

                error = '{0} is not a valid variable name.'.format(args[i])
                break

            if(arg == '-i' or arg == '-fromstandardinput' or arg == '--i' or
               arg == '--fromstandardinput'):
                fromstandardinput = True
                continue

            if(arg == '-o' or arg == '-tostandardoutput' or arg == '--o' or
               arg == '--tostandardoutput'):
                tostandardoutput = True
                continue

            if(arg == '-d' or arg == '-details' or arg == '--d' or
               arg == '--details'):
                wantdetails = True
                continue

            if(arg == '-l' or arg == '-listempty' or arg == '--l' or
               arg == '--listempty'):
                listempty = True
                continue

            if(arg == '-c' or arg == '-capacity' or arg == '--c' or
               arg == '--capacity'):
                wantdiskcapacity = True
                continue

            if(arg == '-cs' or arg == '--cs'):
                wantdiskcapacity = True
                capacityformat = "Sector"
                continue

            if(arg == '-ck' or arg == '--ck'):
                wantdiskcapacity = True
                capacityformat = "K"
                continue

            if(arg == '-s' or arg == '-specifyfiles' or
               arg == '-specificfiles' or arg == '--s' or
               arg == '--specifyfiles' or arg == '--specificfiles'):
                i += 1
                specifiedfiles = getindices(args[i])
                if(specifiedfiles is None):
                    error = '"' + args[i] + '" is invalid list of file indexes\
.'
                    break

                continue

            if(arg == '-p' or arg == '-position' or arg == '-pos' or
               arg == '--p' or arg == '--position' or arg == '--pos'):
                i += 1
                try:
                    copyposition = getindices(args[i])
                    continue

                except:
                    error = '{0} is not a valid index for the output file\.'.\
                        format(args[i])
                    break

            # have unrecognised argument.

            # check if is what entry we want to extract
            if(mode == 'extract' and entrywanted is None):
                try:
                    entrywanted = getint(arg)
                    continue

                except:
                    error = '{0} is not a valid index in the input file.'.\
                        format(arg)
                    break

            # check if is what entry we want to delete or copy
            if((mode == 'delete' or mode == 'copy') and
               entrywanted is None and specifiedfiles is None):
                try:
                    specifiedfiles = getindices(arg)
                    continue

                except:
                    error = '{0} is not a valid index in the input file.'.\
                        format(arg)
                    break

            # check if is input or output file
            # will be inputfile if not already defined, and
            # fromstandardinput is False
            if(inputfile is None and not fromstandardinput):
                inputfile = arg
                continue

            # will be outputfile if not already defined, tostandardoutput
            # is False, and is last
            # argument
            if(outputfile is None and not tostandardoutput and
               i == len(args)-1):
                outputfile = arg
                continue

            error = '"{0}" is unrecognised argument.'.format(arg)
            break

        # check we have all needed arguments
        if(error is None and mode is None):
            error = 'No command (list, extract, delete, copy, create, or help)\
 specified.'

        if(error is None and inputfile is None and not fromstandardinput and
           mode != 'help'):
            error = 'No input file specified.'

        if(error is None and outputfile is None and not tostandardoutput and
           mode != 'help'):
            error = 'No output file specified.'

        if(error is None and entrywanted is None and mode == 'extract'):
            error = 'No file index specified to extract.'

        if(error is None and specifiedfiles is None and entrywanted is None and
           mode == 'delete'):
            error = 'No file index(s) specified to delete.'

        if(error is None and mode == 'create' and creating is None):
            error = 'You have to specify file type to create.'

        if(error is None and mode == 'create' and creatingfilename is None):
            error = 'You have to specify file name to create.'

        if(error is None and mode == 'create' and creating == 'array' and
           (creatingarraytype is None or creatingarrayname is None)):
            error = 'You have to specify array type and name.'

        # handle error with arguments
        if(error is not None):
            sys.stderr.write(error + "\n")
            sys.stdout.write(
                "Use 'python disciplefile.py' to see full list of options.\n")
            sys.exit(2)

        # if help is needed display it
        if(mode == 'help'):
            sys.stdout.write(usage())
            sys.exit(0)

        # get input data
        if(mode == 'create'):
            if(not fromstandardinput):
                with open(inputfile, 'rb') as infile:
                    datain = infile.read()
            else:
                datain = sys.stdin.read()

        else:
            # get disc image
            if(not fromstandardinput):
                # if we're deleteing then we need to work with a copy of
                # the input file
                if(mode == 'delete'):
                    with open(inputfile, 'rb') as infile:
                        di = DiscipleImage()
                        di.setbytes(infile.read())

                else:
                    di = DiscipleImage(inputfile)

            else:
                di = DiscipleImage()
                di.setbytes(sys.stdin.read())

        # now do command
        if(mode == 'list'):
            retdata = '' if wantdetails else "  pos   filename  sectors   \
type\n"
            sectorsused = 0
            for df in di.iteratedisciplefiles():
                if(specifiedfiles is not None and
                   df.filenumber not in specifiedfiles):
                    continue

                if(not listempty and df.isempty()):
                    continue

                if(wantdetails):
                    d = df.getfiledetails()

                    retdata += "{filenumber}\t{filename}\t{filetype}\t{\
filetypelong}\t{sectors}\t{filelength}".format(**d)

                    if(d["filetype"] == 1):
                        retdata += "\t{autostartline}\t{variableoffset}".\
                            format(**d)

                    if(d["filetype"] == 4):
                        retdata += "\t" + str(d["codeaddress"]) + "\t" + \
                            str(d["coderunaddress"])

                    if(d["filetype"] == 2 or d["filetype"] == 3):
                        retdata += "\t" + str(d["variableletter"]) + "\t" + \
                            str(d["variablename"]) + "\t" + \
                            str(d["arraydescriptor"])

                else:
                    retdata += df.getfiledetailsstring()

                sectorsused += df.getsectorsused()

                retdata += "\n"

            if(wantdiskcapacity):
                if(capacityformat == "Sector"):
                    retdata += str(1560 - sectorsused) + " sectors free.\n"
                elif(capacityformat == "K"):
                    retdata += str(((1560 - sectorsused) * 510) / 1024.0) + "K\
 free.\n"
                else:
                    retdata += str((1560 - sectorsused) * 510) + " bytes free.\
\n"

        if(mode == 'extract'):
            df = DiscipleFile(di, entrywanted)
            if(entrywanted > 80 or entrywanted < 1):
                sys.stderr.write(
                    str(entrywanted) + " is not a valid entry number (should \
be 1 to 80).\n")
                sys.stdout.write("Use 'python disciplefile.py' to see full \
list of options.\n")
                sys.exit(2)

            retdata = df.getfiledata()

        if(mode == 'delete'):
            if(specifiedfiles is None):
                specifiedfiles = [entrywanted]

            for i in specifiedfiles:
                if(i > 80 or i < 1):
                    sys.stderr.write(str(i) + " is not a valid entry number \
(should be 1 to 80).\n")
                    sys.stdout.write("Use 'python disciplefile.py' to see full\
 list of options.\n")
                    sys.exit(2)

                di.deleteentry(i)

            # now set disk image as output
            retdata = di.bytedata

        if(mode == 'copy'):
            # create output image to copy into
            diout = DiscipleImage()
            # if we're writing to an existing file then load it into our
            # image
            if(not tostandardoutput and _isfile(outputfile)):
                with open(outputfile, 'rb') as outfile:
                    diout.setbytes(outfile.read())
            else:
                diout.setbytes([0] * 819200)

            if(specifiedfiles is None):
                specifiedfiles = [entrywanted]

            copypositionindex = 0

            for i in specifiedfiles:
                if(i > 80 or i < 1):
                    sys.stderr.write(str(i) + " is not a valid entry number \
(should be 1 to 80).\n")
                    sys.stdout.write("Use 'python disciplefile.py' to see full\
 list of options.\n")
                    sys.exit(2)

                # get file and it's details
                df = DiscipleFile(di, i)
                headder = df.getheadder()
                filedata = df.getfiledata(wantheadder=True,
                                          headderdata=headder)
                # write file
                diout.writefile(headder, filedata,
                                -1 if copypositionindex >= len(
                                    copyposition) else
                                copyposition[copypositionindex])

                copypositionindex += 1

            # now set disk image as output
            retdata = diout.bytedata

        if(mode == 'create'):
            # create output image to copy into
            diout = DiscipleImage()
            # if we're writing to an existing file then load it into our
            # image
            if(not tostandardoutput and _isfile(outputfile)):
                with open(outputfile, 'rb') as outfile:
                    diout.setbytes(outfile.read())
            else:
                diout.setbytes([0] * 819200)

            # get where to save to or go for first available slot
            copyposition = -1 if len(copyposition) == 0 else copyposition[0]

            if(creating == 'basic'):
                diout.writebasicfile(datain, creatingfilename,
                                     position=copyposition,
                                     autostartline=creatingautostart,
                                     varposition=creatingvariableoffset,
                                     overwritename=creatingoverwritename)

            elif(creating == 'code'):
                diout.writecodefile(datain, creatingfilename,
                                    position=copyposition,
                                    codestartaddress=creatingorigin,
                                    overwritename=creatingoverwritename,
                                    coderunaddress=creatingautostart)

            elif(creating == 'array'):
                diout.writearrayfile(datain, creatingfilename,
                                     creatingarraytype + (ord(
                                         creatingarrayname) & 0x3F),
                                     position=copyposition,
                                     overwritename=creatingoverwritename)

            elif(creating == 'screen'):
                diout.writescreenfile(datain, creatingfilename,
                                      position=copyposition,
                                      overwritename=creatingoverwritename)

            # now set disk image as output
            retdata = diout.bytedata

        # prepare data for output
        if(_PYTHON_VERSION_HEX > 0x03000000):
            retdata = bytes(retdata)
        else:
            if(not isinstance(retdata, str)):
                retdata = ''.join([chr(x) for x in retdata])

        # output data
        if(not tostandardoutput):
            fo = open(outputfile, "wb")
            fo.write(retdata)
            fo.close()

        else:
            sys.stdout.write(retdata)

    # catch and handle expected exceptions nicely
    except spectrumtranslate.SpectrumTranslateError as se:
        sys.stderr.write(se.value + "\n")

if __name__ == "__main__":
    # import here as only needed for command line
    import sys

    # set encodeing so can handle non ascii characters
    from codecs import getwriter
    sys.stdout = getwriter('utf8')(sys.stdout)
    sys.stderr = getwriter('utf8')(sys.stderr)

    _commandline(sys.argv)
