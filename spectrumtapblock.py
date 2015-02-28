# This file is part of the SpectrumTranslate python module.
#
# It's licenced under GPL version 3 (www.gnu.org/licenses/gpl.html) with a few extra stipulations:
# 1) These first lines in this file as far as the line with the date needs to be left in so anyone
# who gets a copy of this file has access to the licence, extra stipulations, and disclaimors.
# 2) If this code is used as part of another project, I'd apreciate a mention in that project's
# documentation.
# 3) If you improve on any of the routines, I'd be most grateful if you would pass them back to
# me so that I can have the option to incorporate them into the origional module with apropriate
# attribution under this licence and stipulations.
#
# A copy of the licence and stipulations is bundled with the source files as licence.txt, or you
# can go to the GNU website for the terms of the GPL licence.
#
# If you try hard enough, I'm sure someone could damage something (software, data, system, hardware)
# useing it. I've put a lot of time and effort into this software, and have removed any obvious
# bugs, but nothing is perfect. If you spot any flaws, please let me know so that I might be able to
# fix them. However I reserve the right not to fix flaws that I don't have the time, or resources
# to fix, or that I feel that fixing would detriment the software overall. By useing this software
# you accept this, and any potential risk to your own hardware, software, data, and/or physical and
# mental health. This software is provided "as is" and any express or implied warranties,
# including, but not limited to, the implied warranties of merchantability and fitness for a
# particular purpose are disclaimed. In no event shall I or any contributors be liable for any
# direct, indirect, incidental, special, exemplary, or consequential damages (including, but not
# limited to, procurement of substitute goods or services; loss of use, data, or profits; or
# business interruption) however caused and on any theory of liability, whether in contract, strict
# liability, or tort (including negligence or otherwise) arising in any way out of the use of this
# software, even if advised of the possibility of such damage.
#
# Author: william.fraser@virgin.net
# Date: 14th January 2015

import spectrumtranslate
import sys
import io

class SpectrumTapBlock:
    """
    A class that holds information about a block of data from a Spectrum Tap file format.
    These can be used to extract data from a tap file.
    """

    def __init__(self,flag=0,data='',filePosition=0):
        """
        Creates a new TapBlock object from an input stream.
        tapfile is the Tap file from which to read the data.
        position is the offset to the data from the start of the stream. You can safely put 0 here if this is of no use to you.
        """

        #initialise data

        """An array of bytes holding the data for the block."""
        self.data=data[:]
        
        """
        The 8 bit data identifier value for the block.
        Typically it is 0 for a headder and 255 for a data block, but custom load and save routines can use any value
        from 0 to 255.
        """
        self.flag=flag
        
        """The offset from the start of the stream to the start of this block."""
        self.filePosition=filePosition

    def is_headder(self):
        """
        Is this TapBlock object probably a headder block.
        Headder blocks come before the blocks holding the actual file data and contain information such
        as the filename, the file type, length, and other information depending on the file type.
        Returns True if this is probably a headder, or False if probably not.
        """
        
        return (self.flag==0 and len(self.data)==17)

    def get_file_name(self):
        """
        This gets the filename from a headder block. Note that the filename is always 10 spectrum
        characters long and will be padded with spaces to make the length up to 10 characters. Also be
        aware that spectrum characters can contain control codes, or names of spectrum BASIC commands,
        so the resultant extracted string could be more than 10 characters in length.
        Returns a String holding the filename, or None if this object isn't a headder.
        """
        
        if(not self.is_headder()):
            return None
       
        return spectrumtranslate.get_spectrum_string(self.data[1:11])

    def get_raw_file_name(self):
        """This returns the 10 character file name as a byte string."""
        
        return self.data[1:11]

    def get_file_type_string(self):
        """
        What type of data does this headder block describe.
        Return a string holding the file type, or None if it is not a headder block.
        """
    
        if(not self.is_headder()):
            return None
            
        filetype=self.getbyte(0)

        if(filetype==0):
            return "Program"
        elif(filetype==1):
            return "Number array"
        elif(filetype==2):
            return "Character array"
        elif(filetype==3):
            return "Bytes"
        else:
            return "Unknown"

    def get_file_details_string(self):
        """
        This gets a String respresentation of the file that a headder block describes.
        The format of the returned string is similar to that displayed by the spectrum as it loads a file.
        Returns a string holding the details of the file described by the block, or None if this object isn't a headder.
        """
        
        if(not self.is_headder()):
            return None

        #work out any extra details for file
        extra=''
        #get word at 13, and 14 in the data
        x=_get_word(self.getbytes(13,15))
        filetype=self.getbyte(0)
        #code file
        if(filetype==3):
            extra=" "+str(x)+","+str(_get_word(self.getbytes(11,13)))
        
        #program
        if(filetype==0 and x<32768):
            extra=" Line:"+str(x)
        
        #array
        if(filetype==1 or filetype==2):
            extra=" "+self.get_headder_variable_name()
            
        return "\""+self.get_file_name()+"\" "+self.get_file_type_string()+extra;


    def get_headder_autostart_line(self):
        """
        This returns the Autostart line number for a BASIC file headder block.
        Returns the line number to automatically start at when a BASIC file is loaded. Returns
        -1 if no Autostart line is specified, or -2 if this object is not a BASIC headder block.
        """
        
        if(not self.is_headder() or self.getbyte(0)!=0):
            return -2

        start=_get_word(self.getbytes(13,15))
        
        if(start>=32768):
            return -1
            
        return start

    def get_headder_variable_offset(self):
        """
        This returns the offset to the start of the variable area in a BASIC file. This is the same as
        the length in bytes of the BASIc program. If this is the same
        as the length of the BASIC file then there are no variables saved with the program.
        Returns the byte offset to the start of the variables in the file, or -2 if this object
        is not a BASIC headder block. This is the same as the length of the BASIC program without any
        variables.
        """

        if(not self.is_headder() or self.getbyte(0)!=0):
            return -2
        
        return _get_word(self.getbytes(15,17))

    def get_headder_code_start(self):
        """
        This returns the address where a code file was saved from, and is the sugested address to
        load it to.
        Returns the code address for a code block, or -2 if this object is not a code headder block
        """
        
        if(not self.is_headder() or self.getbyte(0)!=3):
            return -2
            
        return _get_word(self.getbytes(13,15))

    def get_headder_described_data_length(self):
        """
        This returns the length of the data block that this Headder block details.
        Returns the data block block length, or -2 if this object is not a headder block.
        """
        
        if(not self.is_headder()):
            return -2
            
        return _get_word(self.getbytes(11,13))

    def get_headder_variable_letter(self):
        """"
        This returns the character of the variable described by an array Headder block.
        Returns the character value of a variable described by a headder block, or None if this
        object is not a number or character array headder block.
        """
        
        if(not self.is_headder() or (self.getbyte(0)!=1 and self.getbyte(0)!=2)):
            return None
            
        return chr((self.getbyte(14)&127)|64)

    def get_headder_variable_name(self):
        """
        This returns the name of the variable described by an array Headder block.
        This is the letter name of the array, followed by '$' if it is a character array.
        Returns the name of a variable described by a headder block, or None if this
        object is not a number or character array headder block.
        """
        
        if(not self.is_headder() or (self.getbyte(0)!=1 and self.getbyte(0)!=2)):
            return None
        
        return self.get_headder_variable_letter()+(self.getbyte(0)==2 and "$" or"")

    def get_headder_array_descriptor(self):
        """
        This returns the array descriptor of an array Headder block.
        The descriptor is an 8 bit number. The lower 6 bits hold the ASCII lower 6 bits of the variable
        name (must be a letter of the alphabet).
        Bits 6 and 7 describe what type of array the Headder block describes. They are 64 for a
        character array, 128 for a number array, and 192 for a string array.
        Returns the array descriptor of the array described by a headder block, or -1 if this
        object is not a number or character array headder block.
        """
        
        if(not self.is_headder() or (self.getbyte(0)!=1 and self.getbyte(0)!=2)):
            return -1
        
        return self.getbyte(14)

    def get_data_start_offset(self):
        """
        This returns the offset to the data of a block of a tap file in the origional stream.
        This is only as acurate as the offset value passed in the contructor.
        Returns the offset to the data in the origional stream used to create this object.
        """
        
        return self.filePosition+3

    def __str__(self):
        """This returns a basic String summary of the TapBlock object."""
        
        return "Flag:%i, block length:%i" % (self.flag,len(self.data))

    def getbyte(self,pos):
        """
        returns the data held by this TapBlock at the specified position as an int
        """
        
        return ord(self.data[pos])
        
    def getbytes(self,start=0,end=None):
        """
        returns the data held by this TapBlock as a list of ints
        """
        
        if(end==None):
            return [ord(x[0]) for x in self.data[start:]]
        
        return [ord(x[0]) for x in self.data[start:end]]

    def getPackagedForFile(self):
        """
        returns this TapBlock packaged up with length headder, flag and checksum ready for saveing to a file.
        """
        
        #work out length of data+flag+checksum
        length=len(self.data)+2
        
        #get data to put in tapblock
        data=self.getbytes()
        
        #work out checksum
        checksum=self.flag
        for i in data:
            checksum=checksum^i

        #merge it into a list
        package=[length&0xFF,(length>>8)&0xFF,self.flag]+data+[checksum]

        #return converted to bytes in string
        return ''.join([chr(x) for x in package])
    
    def SaveTofile(self,filename,append=True):
        """
        Saves this TapBlock to the specified file. Optionally append specifies whether to overwrite
        or append the TapBlock to the file.
        """
        
        with open(filename,"ab" if append else "wb") as f:
            f.write(self.getPackagedForFile())


#utility function
def _get_word(s):
    if(isinstance(s,str)):
        s=[ord(x) for x in s]
        
    return s[0]+256*s[1]
    
def get_TapBlock_from_file(tapfile,position=0):
    """
    Gets a TapBlock from the specified file.
    returns None if have reached the end of a file.
    Raised IOError if any problems with file format.
    The position variable is not used to read the tap block, only so that it can be found again if needed.
    If you don't need to know where a tap block was in the file, them you can safely ignore this.
    """ 
    
    tb=SpectrumTapBlock(filePosition=position)

    #read 2 byte tap block length
    lengthbytes=tapfile.read(2)
    
    #if have hit end of file at start of new tapblock then end nicely
    if(len(lengthbytes)==0):
        return None

    if(len(lengthbytes)!=2):
        raise IOError("Malformed .tap File")
    
    #flag at beginning and checksum at end of data included in length,
    #so actual data is 2 bytes shorter than block length
    blocklength=_get_word([ord(x[0]) for x in lengthbytes])-2

    #now process byte
    flagbyte=tapfile.read(1)
    if(len(flagbyte)!=1):
        raise IOError("Malformed .tap File")
    
    tb.flag=ord(flagbyte[0])

    tb.data=tapfile.read(blocklength)
    if(len(tb.data)!=blocklength):
        raise IOError("Malformed .tap File")

    #now do checksum
    checkbyte=tapfile.read(1)
    if(len(checkbyte)!=1):
        raise IOError("Malformed .tap File")
    
    #ensure checksum is right
    k=tb.flag
    for i in tb.getbytes():
        k=k^i

    if((k&255)!=ord(checkbyte[0])):
        raise IOError("Malformed .tap File")

    return tb

def get_TapBlocks(tapfile,position=0):
    """"
    Creates a list of TapBlock objects from a file.
    This reads as much information as it can from the file.
    """

    return [tb for tb in TapBlock_from_file(tapfile,position)]

def TapBlock_from_file(filename,position=0):
    """
    Generator function that will supply TapBlock objects
    example:
    for tb in TapBlock_from_file('RebelStar.tap'):
        do_stuff_with(tb)
    """
    
    with open(filename,"rb") as f:
        while True:
            tb=get_TapBlock_from_file(f,position)
            if(tb):
                #2 bytes block length, 1 byte flag, 1 byte checksum, and the rest for the block data
                position+=4+len(tb.data)

                yield tb

            else:
                break

def TapBlock_from_bytestring(bytestring,position=0):
    """
    Generator function that will supply TapBlock objects
    example:
    for tb in TapBlock_from_file(data):
        do_stuff_with(tb)
    """
    with io.BytesIO(bytestring) as f:
        while True:
            tb=get_TapBlock_from_file(f,position)
            if(tb):
                #2 bytes block length, 1 byte flag, 1 byte checksum, and the rest for the block data
                position+=4+len(tb.data)

                yield tb

            else:
                break

def CreateProgramHeadder(filename,VariableOffset,ProgLength,AutoStart=0):
    """
    Create a headder for a program SpectrumTapBlock.
    """

    #create basic data block
    tb=SpectrumTapBlock()    
    tb.flag=0
    tb.data=[0,32,32,32,32,32,32,32,32,32,32,0,0,0,0,0,0]
    #set filename
    for i in range(min(len(filename),10)):
        tb.data[i+1]=ord(filename[i])
        
    #set program
    tb.data[11]=ProgLength&0xFF
    tb.data[12]=(ProgLength>>8)&0xFF
    #set autostart
    tb.data[13]=AutoStart&0xFF
    tb.data[14]=(AutoStart>>8)&0xFF
    #set variable offset
    tb.data[15]=VariableOffset&0xFF
    tb.data[16]=(VariableOffset>>8)&0xFF

    #convert to bytes in string
    tb.data=''.join([chr(x) for x in tb.data])

    return tb

def CreateCodeHeadder(filename,Origin,Codelength):
    """
    Create a headder for a code SpectrumTapBlock.
    """

    #create basic data block
    tb=SpectrumTapBlock()    
    tb.flag=0
    tb.data=[3,32,32,32,32,32,32,32,32,32,32,0,0,0,0,0,0]
    #set filename
    for i in range(min(len(filename),10)):
        tb.data[i+1]=ord(filename[i])

    #set code origin
    tb.data[13]=Origin&0xFF
    tb.data[14]=(Origin>>8)&0xFF
    #set code length
    tb.data[11]=Codelength&0xFF
    tb.data[12]=(Codelength>>8)&0xFF

    #convert to bytes in string
    tb.data=''.join([chr(x) for x in tb.data])

    return tb

def CreateArrayHeadder(filename,VariableDescriptor,ArrayLength):
    """
    Create a headder for an array SpectrumTapBlock.
    The VariableDescriptor is composed of the lower 6 bits of the variable name (a one letter name),
    and the upper 2 bits are 64 for a character array, 128 for a number array, and 192 for a string array.
    """

    tb=SpectrumTapBlock()
    tb.flag=0
    tb.data=[0,32,32,32,32,32,32,32,32,32,32,0,0,0,0,0,0]
    #set filename
    for i in range(min(len(filename),10)):
        tb.data[i+1]=ord(filename[i])

    #set array file type
    tb.data[0]=1 if VariableDescriptor&192==128 else 2
    
    #set array length
    tb.data[11]=ArrayLength&0xFF
    tb.data[12]=(ArrayLength>>8)&0xFF
    
    #set array details
    tb.data[14]=VariableDescriptor

    #convert to bytes in string
    tb.data=''.join([chr(x) for x in tb.data])

    return tb

def CreateScreenHeadder(filename):
    """
    Create a headder for a screen SpectrumTapBlock.
    """

    #screen is just specialized code file
    return CreateCodeHeadder(filename,16384,6912)

def CreateDataBlock(data,flag=0xFF):
    """
    Create a data SpectrumTapBlock.
    """

    tb=SpectrumTapBlock()    
    tb.flag=flag
    #make copy of data, ensureing is bytes in string
    if(isinstance(data,str)):
        tb.data=data
    
    else:
        tb.data=''.join([chr(x) for x in data])
    
    return tb
    
def usage():
    """
    returns the command line arguments for spectrumtapblock as a string.
    """

    return"""usage: python spectrumtapblock.py instruction [args] infile outfile

    moves data from infile which should be a tap file and outputs it to outfile.
    
    instruction is required and specifies what you want to do. It must be 'list'
    'extract', or 'copy. 'list' will list the contents of the specified tapfile.
    'extract' extracts the data from a tap file entry to wherever you want.
    'copy' copies the specified tap file entries to another tap file.
    
    infile and outfile are required unless reading from the standard input or
    outputting to the standard output. Usually arguments are ignored if they
    don't apply to the selected instruction.

    For the extract instruction, the index of the tap entry you want to extract
    must be specified before the filenames.
    
    For the copy instruction, the index(s) of the tap entry(entries) you want to
    copy must be specified before the filename. You do not need to do this if
    you have already specified which entries you want with the -s flag.

    general flags:    
    -o specifies that the output from this program is to be directed to the
       standard output and not outputfile which should be omited. It can be used
       for all instructions.
    --tostandardoutput same as -o.
    -i specifies that this program gets it's data from the standard input and
       not inputfile which should be omited. It can be used for all
       instructions.
    --fromstandardinput same as -i.
    -s specifies which tap entries you want. These are the same as returned by
       the list instruction. You can specify more than one, seperated by commas,
       and can even specify ranges of them with a minus. The numbers are assumed
       to be decimal unless preceded by 0x in which case they are assumed to be
       hexadecimal. For example 2,0x10-20,23 will specify entry 2, 16 to 20
       inclusive, and 23. This flag is used by list, and copy.
    --specifyfiles same as -s.
    --specificfiles same as -s.
    
    list flags:
    -d specifies that we want all information about each tap file entry divided
       by tabs. All entries begin with the index of the entry in the tap file,
       followed by either 'Headder' for a headder or 'Data' for data. For Data
       entries, the flag value and then the data length is listed. For Headders
       the data following this depends on the file type.
       For Program headders, the data given is filename, 'Program', length of
       data in the coresponding data file, the autostart line number or 0 if
       there isn't one, and the offset in bytes to the atached variables (will
       be the same as the length if there are no variables).
       For Byte headders there follows the file name, 'Bytes', the address where
       the code was saved from (and would automatically be loaded to), and then
       the length.
       For array headders there follows the filename, 'Number array' or
       'Character array', the length of the array data, the array letter, the
       array variable name, and the array descriptor specifying what sort of
       array it contains.
       Finally for unknown file types, there follows the file name, 'Unknown',
       the file type number, and the length of the ascociated data.
    --details is the same as -d.

    copy flags:
    -a specifies that the output should be appended to an existing file rather
       than overwriting it.
"""

if __name__=="__main__":

    getint=lambda x: int(x,16 if x.lower().startswith("0x") else 10)

    def getindices(arg):
        try:
            specifiedfiles=[]
            for n in arg.split(','):
                if('-' in n):
                    v=n.split('-',1)
                    specifiedfiles+=range(getint(v[0]),getint(v[1])+1)
                
                else:
                    specifiedfiles+=[getint(n)]
            
            if(len(specifiedfiles)==0):
                return None
            
            return specifiedfiles

        except:
            return None


    i=0
    mode=None
    error=None
    wantdetails=False
    fromstandardinput=False
    tostandardoutput=False
    inputfile=None
    outputfile=None
    entrywanted=None
    specifiedfiles=None
    append=False

    #handle no arguments
    if(len(sys.argv)==1):
        mode='help'    
    
    #go through arguments analysing them
    while(i<len(sys.argv)-1):
        i+=1

        arg=sys.argv[i]
        if(arg=='help' or arg=='extract' or arg=='list' or arg=='copy'):
            if(mode!=None):
                error="Can't have multiple commands."
                break
            
            mode=arg
            continue
        
        if(arg=='-i' or arg=='-fromstandardinput' or arg=='--i' or arg=='--fromstandardinput'):
            fromstandardinput=True
            continue

        if(arg=='-o' or arg=='-tostandardoutput' or arg=='--o' or arg=='--tostandardoutput'):
            tostandardoutput=True
            continue

        if(arg=='-d' or arg=='-details' or arg=='--d' or arg=='--details'):
            wantdetails=True
            continue
        
        if(arg=='-s' or arg=='-specifyfiles' or arg=='-specificfiles' or arg=='--s' or arg=='--specifyfiles' or arg=='--specificfiles'):
            i+=1
            specifiedfiles=getindices(sys.argv[i])
            if(specifiedfiles==None):
                error='"'+sys.argv[i]+'" is invalid list of file indexes.'
                break

            continue

        if(arg=='-a' or arg=='-append' or arg=='--a' or arg=='--append'):
            append=True
            continue

        #have unrecognised argument.
        
        #check if is what entry we want to extract
        if(mode=='extract' and entrywanted==None):
            try:
                entrywanted=getint(arg)
                continue
                
            except:
                error='%s is not a valid index in the input file.' % arg
                break

        #if it is what entries we want to copy
        if(mode=='copy' and specifiedfiles==None):
            specifiedfiles=getindices(arg)
            if(specifiedfiles==None):
                error='"'+arg+'" is invalid list of file indexes.'
                break

            continue
       
        #check if is input or output file
        #will be inputfile if not already defined, and fromstandardinput is False
        if(inputfile==None and fromstandardinput==False):
            inputfile=arg
            continue

        #will be outputfile if not already defined, tostandardoutput is False, and is last
        #argument
        if(outputfile==None and tostandardoutput==False and i==len(sys.argv)-1):
            outputfile=arg
            continue

        error='"%s" is unrecognised argument.' % arg
        break

    if(error==None and mode==None):
        error='No command (list, extract, copy, or help) specified.'

    if(error==None and inputfile==None and fromstandardinput==False and mode!='help'):
        error='No input file specified.'
    
    if(error==None and outputfile==None and tostandardoutput==False and mode!='help'):
        error='No output file specified.'

    if(error==None and mode=='copy' and specifiedfiles==None):
        error='No entries specified to copy.'
        
    #handle error with arguments
    if(error!=None):
        sys.stderr.write(error+"\n")
        sys.stdout.write("Use 'python spectrumtapblock.py' to see full list of options.\n")
        sys.exit(2)
    
    #if help is needed display it
    if(mode=='help'):
        print usage()
        sys.exit(0)

    #get data
    if(fromstandardinput==False):
        with open(inputfile,'rb') as infile:
            data=infile.read()
    
    else:
        data=sys.stdin.read()
    
    #now do command
    if(mode=='list'):
        pos=0
        retdata='' if wantdetails else 'position type    information\n'
        for tb in TapBlock_from_bytestring(data):
            if(specifiedfiles!=None and not pos in specifiedfiles):
                pos+=1
                continue
                
            if(wantdetails):
                if(not tb.is_headder()):
                    retdata+="%i\tData\t%i\t%i\n" % (pos,tb.flag,len(tb.data))
                    
                else:
                    filetype=tb.get_file_type_string()
                    if(filetype=="Program"):
                        retdata+="%i\tHeadder\t%s\tProgram\t%i\t%i\t%i\n" % (pos,tb.get_file_name(),tb.get_headder_described_data_length(),0 if tb.get_headder_autostart_line()<0 else tb.get_headder_autostart_line(),tb.get_headder_variable_offset())
                    elif(filetype=="Bytes"):
                        retdata+="%i\tHeadder\t%s\tBytes\t%i\t%i\n" % (pos,tb.get_file_name(),tb.get_headder_code_start(),tb.get_headder_described_data_length())
                    elif(filetype=="Number array" or filetype=="Character array"):
                        retdata+="%i\tHeadder\t%s\t%s\t%i\t%s\t%s\t%i\n" % (pos,tb.get_file_name(),filetype,tb.get_headder_described_data_length(),tb.get_headder_variable_letter(),tb.get_headder_variable_name(),tb.get_headder_array_descriptor()&192)
                    else:
                        retdata+="%i\tHeadder\t%s\tUnknown\t%i\t%i\n" % (pos,tb.get_file_name(),tb.getbyte(0),tb.get_headder_described_data_length())
                
            else:
                retdata+="%3i      %s %s\n" % (pos,"Headder" if tb.is_headder() else "Data   ",tb.get_file_details_string() if tb.is_headder() else str(tb))

            pos+=1

    if(mode=='extract'):
        tbs=[tb for tb in TapBlock_from_bytestring(data)]
        if(entrywanted>len(tbs)):
            sys.stderr.write(str(entrywanted)+" is greater than the number of entries in the source data.\n")
            sys.stdout.write("Use 'python spectrumtapblock.py' to see full list of options.\n")
            sys.exit(2)
            
        retdata=tbs[entrywanted].data

    if(mode=='copy'):
        tbs=[tb for tb in TapBlock_from_bytestring(data)]
        retdata=''
        for x in specifiedfiles:
            if(x>len(tbs)):
                sys.stderr.write(str(x)+" is greater than the number of entries in the source data.\n")
                sys.stdout.write("Use 'python spectrumtapblock.py' to see full list of options.\n")
                sys.exit(2)
            
            retdata+=tbs[x].getPackagedForFile()

    #output data
    if(tostandardoutput==False):
        fo=open(outputfile,"ab" if mode=='copy' and append else "wb")
        fo.write(retdata)
        fo.close()

    else:
        sys.stdout.write(retdata)
