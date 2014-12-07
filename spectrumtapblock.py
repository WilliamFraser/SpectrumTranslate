import spectrumtranslate

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
    

if __name__=="__main__":
    
    #for tb in TapBlock_from_file('/home/william/java/RebelStar/source/Data/Rebelstar 1 Player.tap'):
    #for tb in TapBlock_from_file('/home/william/java/RebelStar/source/Rebelstar 2 2 Player.tap'):
    #for tb in TapBlock_from_file('/home/william/RR.tap/REBRAID1.TAP'):
    #    print tb
    #    print tb.get_file_details_string()

    tbs=get_TapBlocks('/home/william/RR.tap/REBRAID1.TAP')
    print tbs[1]
    pass

    f=open("x.bin","rb")
    data=f.read()
    f.close()
    
    tb=CreateDataBlock(data,0xFF)
    data=tb.getPackagedForFile()
    
    data=[ord(x) for x in data]
    
    print data
