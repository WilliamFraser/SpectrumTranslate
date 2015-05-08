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
import io
# sys and codecs imported elsewhere so only used for command line


class SpectrumTapBlock:
    """
    A class that holds information about a block of data from a Spectrum
    Tap file format.  These can be used to extract data from a tap file.
    """

    def __init__(self, flag=0, data='', filePosition=0):
        """
        Creates a new TapBlock object from an input stream.
        tapfile is the Tap file from which to read the data.
        position is the offset to the data from the start of the stream.
        You can safely put 0 here if this is of no use to you.
        """

        # initialise data

        """An array of bytes holding the data for the block."""
        self.data = data[:]

        """
        The 8 bit data identifier value for the block.
        Typically it is 0 for a headder and 255 for a data block, but
        custom load and save routines can use any value
        from 0 to 255.
        """
        self.flag = flag

        """The offset from the start of the stream to the start of this
        block."""
        self.filePosition = filePosition

    def isheadder(self):
        """
        Is this TapBlock object probably a headder block.
        Headder blocks come before the blocks holding the actual file
        data and contain information such as the filename, the file
        type, length, and other information depending on the file type.
        Returns True if this is probably a headder, or False if probably
        not.
        """

        return (self.flag == 0 and len(self.data) == 17)

    def getfilename(self):
        """
        This gets the filename from a headder block.  Note that the
        filename is always 10 spectrum characters long and will be
        padded with spaces to make the length up to 10 characters.  Also
        be aware that spectrum characters can contain control codes, or
        names of spectrum BASIC commands, so the resultant extracted
        string could be more than 10 characters in length.  Returns a
        String holding the filename, or None if this object isn't a
        headder.
        """

        if(not self.isheadder()):
            return None

        return spectrumtranslate.getspectrumstring(self.data[1:11])

    def getrawfilename(self):
        """This returns the 10 character file name as a byte string."""

        return self.data[1:11]

    def getfiletypestring(self):
        """
        What type of data does this headder block describe.
        Return a string holding the file type, or None if it is not a
        headder block.
        """

        if(not self.isheadder()):
            return None

        filetype = self.getbyte(0)

        if(filetype == 0):
            return "Program"
        elif(filetype == 1):
            return "Number array"
        elif(filetype == 2):
            return "Character array"
        elif(filetype == 3):
            return "Bytes"
        else:
            return "Unknown"

    def getfiledetailsstring(self):
        """
        This gets a String respresentation of the file that a headder
        block describes.  The format of the returned string is similar
        to that displayed by the spectrum as it loads a file.  Returns a
        string holding the details of the file described by the block,
        or None if this object isn't a headder.
        """

        if(not self.isheadder()):
            return None

        # work out any extra details for file
        extra = self.getfiletypestring()
        # get word at 13, and 14 in the data
        x = _get_word(self.getbytes(13, 15))
        filetype = self.getbyte(0)
        # code file
        if(filetype == 3):
            extra += " " + str(x) + "," + str(_get_word(self.getbytes(11, 13)))

        # program
        if(filetype == 0 and x < 10000):
            extra += " Line:" + str(x)

        # array
        if(filetype == 1 or filetype == 2):
            extra += " " + self.getheaddervariablename()

        return "\"" + self.getfilename() + "\" " + extra

    def getheadderautostartline(self):
        """
        This returns the Autostart line number for a BASIC file headder
        block.  Returns the line number to automatically start at when a
        BASIC file is loaded.  Returns -1 if no Autostart line is
        specified, or -2 if this object is not a BASIC headder block.
        """

        if(not self.isheadder() or self.getbyte(0) != 0):
            return -2

        start = _get_word(self.getbytes(13, 15))

        if(start > 9999):
            return -1

        return start

    def getheaddervariableoffset(self):
        """
        This returns the offset to the start of the variable area in a
        BASIC file.  This is the same as the length in bytes of the
        BASIC program.  If this is the same as the length of the BASIC
        file then there are no variables saved with the program.
        Returns the byte offset to the start of the variables in the
        file, or -2 if this object is not a BASIC headder block.  This
        is the same as the length of the BASIC program without any
        variables.
        """

        if(not self.isheadder() or self.getbyte(0) != 0):
            return -2

        return _get_word(self.getbytes(15, 17))

    def getheaddercodestart(self):
        """
        This returns the address where a code file was saved from, and
        is the sugested address to load it to.  Returns the code address
        for a code block, or -2 if this object is not a code headder
        block.
        """

        if(not self.isheadder() or self.getbyte(0) != 3):
            return -2

        return _get_word(self.getbytes(13, 15))

    def getheadderdescribeddatalength(self):
        """
        This returns the length of the data block that this Headder
        block details.  Returns the data block block length, or -2 if
        this object is not a headder block.
        """

        if(not self.isheadder()):
            return -2

        return _get_word(self.getbytes(11, 13))

    def getheaddervariableletter(self):
        """"
        This returns the character of the variable described by an array
        Headder block.  Returns the character value of a variable
        described by a headder block, or None if this object is not a
        number or character array headder block.
        """

        if(not self.isheadder() or (self.getbyte(0) != 1 and
           self.getbyte(0) != 2)):
            return None

        return chr((self.getbyte(14) & 127) | 64)

    def getheaddervariablename(self):
        """
        This returns the name of the variable described by an array
        Headder block.  This is the letter name of the array, followed
        by '$' if it is a character array.  Returns the name of a
        variable described by a headder block, or None if this object is
        not a number or character array headder block.
        """

        if(not self.isheadder() or (self.getbyte(0) != 1 and
           self.getbyte(0) != 2)):
            return None

        return self.getheaddervariableletter() + (
            "$" if self.getbyte(0) == 2 else "")

    def getheadderarraydescriptor(self):
        """
        This returns the array descriptor of an array Headder block.
        The descriptor is an 8 bit number.  The lower 6 bits hold the
        ASCII lower 6 bits of the variable name (must be a letter of the
        alphabet).  Bits 6 and 7 describe what type of array the Headder
        block describes.  They are 64 for a character array, 128 for a
        number array, and 192 for a string array.  Returns the array
        descriptor of the array described by a headder block, or -1 if
        this object is not a number or character array headder block.
        """

        if(not self.isheadder() or (self.getbyte(0) != 1 and
           self.getbyte(0) != 2)):
            return -1

        return self.getbyte(14)

    def getdatastartoffset(self):
        """
        This returns the offset to the data of a block of a tap file in
        the origional stream.  This is only as acurate as the offset
        value passed in the contructor.  Returns the offset to the data
        in the origional stream used to create this object.
        """

        return self.filePosition + 3

    def __str__(self):
        """Returns a basic String summary of the TapBlock object."""

        return "Flag:{0}, block length:{1}".format(self.flag, len(self.data))

    def getbyte(self, pos):
        """
        returns the data held by this TapBlock at the specified position
        as an int.
        """

        return ord(self.data[pos])

    def getbytes(self, start=0, end=None):
        """
        returns the data held by this TapBlock as a list of ints.
        """

        if(end is None):
            return [ord(x[0]) for x in self.data[start:]]

        return [ord(x[0]) for x in self.data[start:end]]

    def getpackagedforfile(self):
        """
        returns this TapBlock packaged up with length headder, flag and
        checksum ready for saveing to a file.
        """

        # work out length of data+flag+checksum
        length = len(self.data) + 2

        # get data to put in tapblock
        data = self.getbytes()

        # work out checksum
        checksum = self.flag
        for i in data:
            checksum = checksum ^ i

        # merge it into a list
        package = [length & 0xFF, (length >> 8) & 0xFF,
                   self.flag] + data + [checksum]

        # return converted to bytes in string
        return ''.join([chr(x) for x in package])

    def savetofile(self, filename, append=True):
        """
        Saves this TapBlock to the specified file. Optionally append
        specifies whether to overwrite or append the TapBlock to the
        file.
        """

        with open(filename, "ab" if append else "wb") as f:
            f.write(self.getpackagedforfile())


# utility function
def _get_word(s):
    if(isinstance(s, str)):
        s = [ord(x) for x in s]

    return s[0] + 256 * s[1]


def gettapblockfromfile(tapfile, position=0):
    """
    Gets a TapBlock from the specified file.
    Returns None if have reached the end of a file.  Raises IOError if
    any problems with file format.  The position variable is not used to
    read the tap block, only so that it can be found again if needed.
    If you don't need to know where a tap block was in the file, them
    you can safely ignore this.
    """

    tb = SpectrumTapBlock(filePosition=position)

    # read 2 byte tap block length
    lengthbytes = tapfile.read(2)

    # if have hit end of file at start of new tapblock then end nicely
    if(len(lengthbytes) == 0):
        return None

    if(len(lengthbytes) != 2):
        raise IOError("Malformed .tap File")

    # flag at beginning and checksum at end of data included in length,
    # so actual data is 2 bytes shorter than block length
    blocklength = _get_word([ord(x[0]) for x in lengthbytes]) - 2

    # now process byte
    flagbyte = tapfile.read(1)
    if(len(flagbyte) != 1):
        raise IOError("Malformed .tap File")

    tb.flag = ord(flagbyte[0])

    tb.data = tapfile.read(blocklength)
    if(len(tb.data) != blocklength):
        raise IOError("Malformed .tap File")

    # now do checksum
    checkbyte = tapfile.read(1)
    if(len(checkbyte) != 1):
        raise IOError("Malformed .tap File")

    # ensure checksum is right
    k = tb.flag
    for i in tb.getbytes():
        k = k ^ i

    if((k & 255) != ord(checkbyte[0])):
        raise IOError("Malformed .tap File")

    return tb


def gettapblocks(tapfile, position=0):
    """"
    Creates a list of TapBlock objects from a file.
    This reads as much information as it can from the file.
    """

    return [tb for tb in tapblockfromfile(tapfile, position)]


def tapblockfromfile(filename, position=0):
    """
    Generator function that will supply TapBlock objects
    example:
    for tb in tapblockfromfile('RebelStar.tap'):
        do_stuff_with(tb)
    """

    with open(filename, "rb") as f:
        while True:
            tb = gettapblockfromfile(f, position)
            if(tb):
                # 2 bytes block length, 1 byte flag, 1 byte checksum, and
                # the rest for the block data
                position += 4 + len(tb.data)

                yield tb

            else:
                break


def tapblockfrombytestring(bytestring, position=0):
    """
    Generator function that will supply TapBlock objects
    example:
    for tb in tapblockfromfile(data):
        do_stuff_with(tb)
    """
    with io.BytesIO(bytestring) as f:
        while True:
            tb = gettapblockfromfile(f, position)
            if(tb):
                # 2 bytes block length, 1 byte flag, 1 byte checksum, and
                # the rest for the block data
                position += 4 + len(tb.data)

                yield tb

            else:
                break


def createbasicheadder(filename, VariableOffset, ProgLength, AutoStart=-1):
    """
    Create a headder for a program SpectrumTapBlock.
    """

    # create basic data block
    tb = SpectrumTapBlock()
    tb.flag = 0
    tb.data = [0, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 0, 0, 0, 0, 0, 0]
    # set filename
    for i in range(min(len(filename), 10)):
        tb.data[i + 1] = ord(filename[i])

    # set program
    tb.data[11] = ProgLength & 0xFF
    tb.data[12] = (ProgLength >> 8) & 0xFF
    # set autostart
    if(AutoStart < 0 or AutoStart > 9999):
        AutoStart = 0x8000

    tb.data[13] = AutoStart & 0xFF
    tb.data[14] = (AutoStart >> 8) & 0xFF
    # set variable offset
    tb.data[15] = VariableOffset & 0xFF
    tb.data[16] = (VariableOffset >> 8) & 0xFF

    # convert to bytes in string
    tb.data = ''.join([chr(x) for x in tb.data])

    return tb


def createcodeheadder(filename, Origin, Codelength):
    """
    Create a headder for a code SpectrumTapBlock.
    """

    # create basic data block
    tb = SpectrumTapBlock()
    tb.flag = 0
    tb.data = [3, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 0, 0, 0, 0, 0, 0]
    # set filename
    for i in range(min(len(filename), 10)):
        tb.data[i + 1] = ord(filename[i])

    # set code origin
    tb.data[13] = Origin & 0xFF
    tb.data[14] = (Origin >> 8) & 0xFF
    # set code length
    tb.data[11] = Codelength & 0xFF
    tb.data[12] = (Codelength >> 8) & 0xFF

    # convert to bytes in string
    tb.data = ''.join([chr(x) for x in tb.data])

    return tb


def createarrayheadder(filename, VariableDescriptor, ArrayLength):
    """
    Create a headder for an array SpectrumTapBlock.
    The VariableDescriptor is composed of the lower 6 bits of the
    variable name (a one letter name), and the upper 2 bits are 64 for a
    character array, 128 for a number array, and 192 for a string array.
    """

    tb = SpectrumTapBlock()
    tb.flag = 0
    tb.data = [0, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 0, 0, 0, 0, 0, 0]
    # set filename
    for i in range(min(len(filename), 10)):
        tb.data[i + 1] = ord(filename[i])

    # set array file type
    tb.data[0] = 1 if VariableDescriptor & 192 == 128 else 2

    # set array length
    tb.data[11] = ArrayLength & 0xFF
    tb.data[12] = (ArrayLength >> 8) & 0xFF

    # set array details
    tb.data[14] = VariableDescriptor

    # convert to bytes in string
    tb.data = ''.join([chr(x) for x in tb.data])

    return tb


def createscreenheadder(filename):
    """
    Create a headder for a screen SpectrumTapBlock.
    """

    # screen is just specialized code file
    return createcodeheadder(filename, 16384, 6912)


def createdatablock(data, flag=0xFF):
    """
    Create a data SpectrumTapBlock.
    """

    tb = SpectrumTapBlock()
    tb.flag = flag
    # make copy of data, ensureing is bytes in string
    if(isinstance(data, str)):
        tb.data = data

    else:
        tb.data = ''.join([chr(x) for x in data])

    return tb


def usage():
    """
    returns the command line arguments for spectrumtapblock as a string.
    """

    return"""usage: python spectrumtapblock.py instruction [args] infile
    outfile

    moves data from infile which should be a tap file and outputs it to
    outfile.

    instruction is required and specifies what you want to do. It must
    be 'list', 'extract', 'delete' or 'copy.  'list' will list the
    contents of the specified tapfile.  'extract' extracts the data from
    a tap file entry to wherever you want.  'copy' copies the specified
    tap file entries to another tap file.  'delete' deletes the
    specified entries from the source tap file and outputs the resulting
    tap file.

    infile and outfile are required unless reading from the standard
    input or outputting to the standard output.  Usually arguments are
    ignored if they don't apply to the selected instruction.

    For the extract instruction, the index of the tap entry you want to
    extract must be specified before the filenames.

    For the copy and delete instructions, the index(s) of the tap
    entry(entries) you want to copy must be specified before the
    filename.  You do not need to do this if you have already specified
    which entries you want with the -s flag.

    general flags:
    -o specifies that the output from this program is to be directed to
       the standard output and not outputfile which should be omited.
       It can be used for all instructions.
    --tostandardoutput same as -o.
    -i specifies that this program gets it's data from the standard
       input and not inputfile which should be omited.  It can be used
       for all instructions.
    --fromstandardinput same as -i.
    -s specifies which tap entries you want.  These are the same as
       returned by the list instruction.  You can specify more than one,
       seperated by commas, and can even specify ranges of them with a
       minus.  The numbers are assumed to be decimal unless preceded by
       0x in which case they are assumed to be hexadecimal.
       For example: 2,0x10-20,23 will specify entry 2, 16 to 20
       inclusive, and 23.  This flag is used by list, delete, and copy.
    --specifyfiles same as -s.
    --specificfiles same as -s.

    list flags:
    -d specifies that we want all information about each tap file entry
       divided by tabs.  All entries begin with the index of the entry
       in the tap file, followed by either 'Headder' for a headder or
       'Data' for data.  For Data entries, the flag value and then the
       data length is listed.  For Headders the data following this
       depends on the file type.
       For Program headders, the data given is filename, 'Program',
       length of data in the coresponding data file, the autostart line
       number or -1 if there isn't one, and the offset in bytes to the
       atached variables (will be the same as the length if there are no
       variables).
       For Byte headders there follows the file name, 'Bytes', the
       address where the code was saved from (and would automatically be
       loaded to), and then the length.
       For array headders there follows the filename, 'Number array' or
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
"""


def commandline(args):

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

        # handle no arguments
        if(len(args) == 1):
            mode = 'help'

        # go through arguments analysing them
        while(i < len(args) - 1):
            i += 1

            arg = args[i]
            if(arg == 'help' or arg == 'extract' or arg == 'list' or
               arg == 'copy' or arg == 'delete' or arg == 'create'):
                if(mode is not None):
                    error = "Can't have multiple commands."
                    break

                mode = arg
                continue

            if(mode == 'create' and creating is None):
                if(arg != 'basic' and arg != 'code' and arg != 'array' and
                   arg != 'screen' and arg != 'block'):
                    error = 'Must specify what type of file to create. Valid \
options are basic, code, array, screen, and block.'
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

            if(arg == '-origin' or arg == '--origin'):
                i += 1
                try:
                    creatingorigin = getint(args[i])
                    if(creatingorigin < 0 or creatingorigin > 65535):
                        error = 'code origin must be 0-65535 inclusive.'
                        break

                    continue

                except:
                    error = '{0} is not a valid code origin.'.format(args[i])
                    break

            if(arg == '-flag' or arg == '--flag'):
                i += 1
                try:
                    creatingblockflag = getint(args[i])
                    if(creatingblockflag < 0 or creatingblockflag > 255):
                        error = 'flag value must be 0-255 inclusive.'
                        break

                    continue

                except:
                    error = '{0} is not a valid flag value.'.format(args[i])
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
                    error = '{0} is not a valid array type (must be character\
, number or string).'.format(args[i])
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

            if(arg == '-a' or arg == '-append' or arg == '--a' or
               arg == '--append'):
                append = True
                continue

            if(arg == '-p' or arg == '-position' or arg == '-pos' or
               arg == '--p' or arg == '--position' or arg == '--pos'):
                i += 1
                try:
                    copyposition = getint(args[i])
                    continue

                except:
                    error = '{0} is not a valid index for the output file.'.\
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

            # if it is what entries we want to copy
            if((mode == 'copy' or mode == 'delete') and
               specifiedfiles is None):
                specifiedfiles = getindices(arg)
                if(specifiedfiles is None):
                    error = '"' + arg + '" is invalid list of file indexes.'
                    break

                continue

            # check if is input or output file
            # will be inputfile if not already defined, and
            # fromstandardinput is False
            if(inputfile is None and not fromstandardinput):
                inputfile = arg
                continue

            # will be outputfile if not already defined, tostandardoutput
            # is False, and is last argument
            if(outputfile is None and not tostandardoutput and
               i == len(args) - 1):
                outputfile = arg
                continue

            error = '"{0}" is unrecognised argument.'.format(arg)
            break

        if(error is None and mode is None):
            error = 'No command (list, extract, copy, delete, create, or help)\
 specified.'

        if(error is None and inputfile is None and not fromstandardinput and
           mode != 'help'):
            error = 'No input file specified.'

        if(error is None and outputfile is None and not tostandardoutput and
           mode != 'help'):
            error = 'No output file specified.'

        if(error is None and (mode == 'copy' or mode == 'delete') and
           specifiedfiles is None):
            error = 'No entries specified to ' + mode + '.'

        if(error is None and mode == 'create' and creating is None):
            error = 'You have to specify file type to create.'

        if(error is None and mode == 'create' and creatingfilename is None and
           creating != 'block'):
            error = 'You have to specify file name to create.'

        if(error is None and mode == 'create' and creating == 'array' and
           (creatingarraytype is None or creatingarrayname is None)):
            error = 'You have to specify array type and name.'

        # handle error with arguments
        if(error is not None):
            sys.stderr.write(error + "\n")
            sys.stdout.write("Use 'python spectrumtapblock.py' to see full \
list of options.\n")
            sys.exit(2)

        # if help is needed display it
        if(mode == 'help'):
            sys.stdout.write(usage())
            sys.exit(0)

        # get data
        if(not fromstandardinput):
            with open(inputfile, 'rb') as infile:
                data = infile.read()

        else:
            data = sys.stdin.read()

        # now do command
        if(mode == 'list'):
            pos = 0
            retdata = '' if wantdetails else 'position type    information\n'
            for tb in tapblockfrombytestring(data):
                if(specifiedfiles is not None and pos not in specifiedfiles):
                    pos += 1
                    continue

                if(wantdetails):
                    if(not tb.isheadder()):
                        retdata += "{0}\tData\t{1}\t{2}\n".format(pos, tb.flag,
                                                                  len(tb.data))

                    else:
                        filetype = tb.getfiletypestring()
                        if(filetype == "Program"):
                            retdata += \
                                "{0}\tHeadder\t{1}\tProgram\t{2}\t{3}\t{4}\n".\
                                format(
                                 pos, tb.getfilename(),
                                 tb.getheadderdescribeddatalength(),
                                 0 if tb.getheadderautostartline() < 0 else
                                 tb.getheadderautostartline(),
                                 tb.getheaddervariableoffset())
                        elif(filetype == "Bytes"):
                            retdata += "{0}\tHeadder\t{1}\tBytes\t{2}\t{3}\n".\
                                format(
                                 pos, tb.getfilename(),
                                 tb.getheaddercodestart(),
                                 tb.getheadderdescribeddatalength())
                        elif(filetype == "Number array" or
                             filetype == "Character array"):
                            retdata += \
                              "{0}\tHeadder\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".\
                              format(pos, tb.getfilename(), filetype,
                                     tb.getheadderdescribeddatalength(),
                                     tb.getheaddervariableletter(),
                                     tb.getheaddervariablename(),
                                     tb.getheadderarraydescriptor() & 192)
                        else:
                            retdata += \
                                "{0}\tHeadder\t{1}\tUnknown\t{2}\t{3}\n".\
                                format(pos, tb.getfilename(),
                                       tb.getbyte(0),
                                       tb.getheadderdescribeddatalength())

                else:
                    retdata += "{0:3}      {1} {2}\n".format(
                        pos, "Headder" if tb.isheadder() else "Data   ",
                        tb.getfiledetailsstring() if tb.isheadder() else
                        str(tb))

                pos += 1

        if(mode == 'extract'):
            tbs = [tb for tb in tapblockfrombytestring(data)]
            if(entrywanted > len(tbs)):
                sys.stderr.write(str(entrywanted) + " is greater than the \
number of entries in the source data.\n")
                sys.stdout.write("Use 'python spectrumtapblock.py' to see full\
 list of options.\n")
                sys.exit(2)

            retdata = tbs[entrywanted].data

        if(mode == 'copy'):
            tbs = [tb for tb in tapblockfrombytestring(data)]
            retdata = ''
            for x in specifiedfiles:
                if(x > len(tbs)):
                    sys.stderr.write(str(x) + " is greater than the number of \
entries in the source data.\n")
                    sys.stdout.write("Use 'python spectrumtapblock.py' to see\
 full list of options.\n")
                    sys.exit(2)

                retdata += tbs[x].getpackagedforfile()

        if(mode == 'delete'):
            tbs = [tb for tb in tapblockfrombytestring(data)]
            retdata = ''
            for x in range(len(tbs)):
                if(x not in specifiedfiles):
                    retdata += tbs[x].getpackagedforfile()

        if(mode == 'create'):
            retdata = ''

            if(creating == 'basic'):
                if(creatingvariableoffset == -1):
                    # work out position of variables
                    offset = 0
                    while(offset < len(data)):
                        linenumber = (ord(data[offset]) * 256) + ord(
                            data[offset + 1])
                        # bits 5,6,7 of variable code will be 16384 or
                        # more as the max line number is 9999
                        if(linenumber > 9999):
                            # too big for line number: is 1st variable
                            break

                        # otherwise move to next line
                        linelength = ord(data[offset + 2]) + (ord(
                            data[offset + 3]) * 256)
                        offset += linelength + 4

                    creatingvariableoffset = min(offset, len(data))

                retdata = createbasicheadder(creatingfilename,
                                             creatingvariableoffset, len(data),
                                             creatingautostart
                                             ).getpackagedforfile()

            elif(creating == 'code'):
                retdata = createcodeheadder(creatingfilename,
                                            creatingorigin, len(data)
                                            ).getpackagedforfile()

            elif(creating == 'array'):
                retdata = createarrayheadder(creatingfilename,
                                             creatingarraytype + (ord(
                                               creatingarrayname) & 0x3F),
                                             len(data)).getpackagedforfile()

            elif(creating == 'screen'):
                retdata = createscreenheadder(
                    creatingfilename).getpackagedforfile()

            retdata += createdatablock(data,
                                       flag=creatingblockflag if
                                       creating == 'block' else 0xFF
                                       ).getpackagedforfile()

        # handle copy or create inserting at position
        if(copyposition and (mode == 'create' or mode == 'copy')):
            import os.path
            if(not tostandardoutput and os.path.isfile(outputfile)):
                # get tapblocks (if any in destination file)
                with open(outputfile, 'rb') as infile:
                    destinationtbs = [tb for tb in tapblockfrombytestring(
                        infile.read())]

                if(copyposition < len(destinationtbs)):
                    retdata = "".join(
                        [tb.getpackagedforfile() for tb in destinationtbs[
                            :copyposition]]) + retdata + "".join(
                            [tb.getpackagedforfile() for tb in destinationtbs[
                                copyposition:]])

                else:
                    retdata = destinationtbs + retdata

        # output data
        if(not tostandardoutput):
            fo = open(outputfile, "ab" if mode == 'copy' and append else "wb")
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
    import codecs
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)

    commandline(sys.argv)
