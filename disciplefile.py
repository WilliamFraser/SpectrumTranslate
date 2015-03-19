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
import mmap

class DiscipleFile:
    """A class that holds information about a file from a +D/Disciple disk image."""

    def __init__(self,image,filenumber):
        """
        Creates a new DiscipleFile for the specified file in the specified image.
        image is the DiscipleImage to extract the file from.
        filenumber is the filenumber for the file you wish to extract from 1 to 80 inclusive.
        """
        #make note of paarent image
        self.image=image
        
        #make note of filenumber
        self.filenumber=filenumber
        
        #is it a valid filenumber? Origional valid filenumbers are 1 to 80
        if(self.filenumber<1 or self.filenumber>80):
            raise spectrumtranslate.SpectrumTranslateException("Invalid File Number");

    def GetHeadder(self):
        """Returns 256 byte file headder"""
        
        #work out if first or second entry in sector
        headderstart=((self.filenumber-1)&1)*256
        
        return self.image.GetSector((self.filenumber-1)/20,(((self.filenumber-1)/2)%10)+1,0)[headderstart:headderstart+256]

    def GetFileData(self,wantheadder=False,headderdata=None):
        """Get the data of the file. Returns a byte string array containing the file data.
        
        BASIC, code, number array, string array, and screen files have and extra 9 bytes at the
        start of the file (these extra bytes are not included in the file length as returned by
        GetFileLength(). These are a copy of the headder data. Normally you don't want these
        bytes, but use wantheadder=True if you do (it defaults to False if unspecified.
        headderdata is optional but saves resources.
        """

        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()

        #check to make sure is valid file
        if(self.IsEmpty(headderdata)):
            return None
        
        #make note of number of sectors in file
        i=self.GetSectorsUsed(headderdata)
        
        #get map of sectors used
        sectorMap=[ord(x) for x in headderdata[15:210]]
        
        bytestocopy=self.GetFileLength(headderdata)
        
        data=""
        
        #get start track & sector
        track=ord(headderdata[13])
        sector=ord(headderdata[14])
        
        #BASIC, code, number array, string array, or screen have extra 9 bytes of file as copy of headder data.
        t=self.GetFileType(headderdata)
        if((t>0 and t<5) or t==7):
            if(wantheadder):
                readpos=0
                bytestocopy+=9

            else:
                readpos=9
        
        else:
            readpos=0
        
        #now move through file transfering data to array
        while(i>0):
            #sanity check on track & sector
            if(track==0 and sector==0):
                raise spectrumtranslate.SpectrumTranslateException("unexpected early end of file")
                
            if((track&127)>79 or track<4):
                raise spectrumtranslate.SpectrumTranslateException("Invalid track number")
                
            if(sector<1 or sector>10):
                raise spectrumtranslate.SpectrumTranslateException("Invalid sector number")
            
            #calculate offset & bit of this track & sector in sectorMap
            o=(track&127)+(80 if track>=128 else 0)-4
            o*=10
            o+=sector-1
            b=1<<(o%8)
            o/=8
            #check if is sector owned by this file
            if((sectorMap[o]&b)!=b):
                raise spectrumtranslate.SpectrumTranslateException("next sector not matching FAT")
                
            #remove from copy of sectorMap
            sectorMap[o]-=b
            
            #load next sector in chain
            sectordata=self.image.GetSector(track&127,sector,track>>7)
            #copy sector data
            data+=sectordata[readpos:min(510-readpos,bytestocopy)+readpos]
            
            #update track & sector
            track=ord(sectordata[510])
            sector=ord(sectordata[511])
            #update number of bytes left to copy
            bytestocopy-=(510-readpos)
            #decrement number of sectors left to fetch
            i-=1
            #after reading 1st sector won't have any more file headder data at start of sector
            readpos=0
        
        #track & sector of last sector read should be 0
        if(track!=0 and sector!=0):
            raise spectrumtranslate.SpectrumTranslateException("File length mismatch")
        
        #sectorMap should now be blank, otherwise there are unused sectors
        for i in sectorMap:
            if(i!=0):
                raise spectrumtranslate.SpectrumTranslateException("Unused sectors in FAT")
        
        return data

    def IsEmpty(self,headderdata=None):
        """
        Is this DiscipleFile an unused or errased entry?
        headderdata is optional but saves resources.
        """
        
        return self.GetFileType(headderdata)==0

    def GetSectorsUsed(self,headderdata=None):
        """
        Gets the number of sectors used by this file.
        headderdata is optional but saves resources.
        """

        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()
        
        #check to make sure is valid file
        if(self.IsEmpty(headderdata)):
            return 0

        #is stored at offset 11 in motorola byte order (most significant byte first)
        return ord(headderdata[12])+256*ord(headderdata[11])

    def GetFileLength(self,headderdata=None):
        """
        Returns the length of this file.
        headderdata is optional but saves resources.
        NB BASIC, code, number array, string array, and screen files have and extra 9 bytes at the
        start of the file data which is a copy of the 9 byte headder data as if it were saved to
        tape. These 9 bytes are extra to the length of the file as returned by this method.
        """

        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()
        
        t=self.GetFileType(headderdata)
        #the length of the file in bytes depends on the file type
        if(t==0):
            #deleted/empty
            return 0
            
        elif(t==1 or t==2 or t==3 or t==4 or t==7 or t==13):
            #1=basic,2=number array,3=string array,4=code,7=screen$,13=unidos create file
            return ord(headderdata[212])+256*ord(headderdata[213])
        
        elif(t==5):
            #48K snapshot
            return 49152 #3 * 16K ram banks
        
        elif(t==9):
            #128K snapshot
            return 131073 #1 byte page register value + 8 16K ram banks
            
        elif(t==10):
            #opentype
            return ord(headderdata[212])+256*ord(headderdata[213])+65536*ord(headderdata[210])
        elif(t==11):
            #execute
            return 510
        else:
             #default length is size of all used sector (minus chain bytes)
             return self.GetSectorsUsed(headderdata)*510

    def GetFileType(self,headderdata=None):
        """
        Returns the file type the file described by this DiscipleFile.
        This is a number from 0 to 11.
        Values other than this sugest that the image file that this object was created from may be corrupted.
        headderdata is optional but saves resources.
        """

        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()
        
        #&31 to exclude hidden flags
        return ord(headderdata[0])&31

    def GetFileTypeString(self,headderdata=None):
        """
        Returns the file type name of the file described by this DiscipleFile.
        headderdata is optional but saves resources.
        """

        i=self.GetFileType(headderdata)
        if(i>11):
            return None
            
        return ("Free/Erased","Basic","Number Array","String Array","Code","48K Snapshot","Microdrive","SCREEN$",
                "Special","128K Snapshot","Opentype","Execute",#list unidos filenames also
                "SUBDIRECTORY","CREATE")[i]

    def GetFileTypeCatString(self,headderdata=None):
        """
        Returns the file type name use in a catalog listing for the file described by this DiscipleFile.
        headderdata is optional but saves resources.
        """

        i=self.GetFileType(headderdata)
        if(i>11):
            return None

        return ("ERASED","BAS","D.ARRAY","$.ARRAY","CDE","SNP 48k","MD.FILE","SCREEN$","SPECIAL","SNP 128k","OPENTYPE",
                "EXECUTE", #list unidos cat names also
                "DIR","CREATE")[i]

    def GetFileName(self,headderdata=None):
        """
        This gets the filename. Note that the filename is always 10 spectrum
        characters long and will be padded with spaces to make the length up to 10 characters. Also be
        aware that spectrum characters can contain control codes, or names of spectrum BASIC commands,
        so the resultant extracted string could be more than 10 characters in length.
        headderdata is optional but saves resources.
        """
        
        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()

        return spectrumtranslate.get_spectrum_string(headderdata[1:11])

    def GetRawFileName(self,headderdata=None):
        """This returns the 10 character file name as a byte string."""

        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()

        return headderdata[1:11]

    def GetFileDetails(self,headderdata=None):
        """
        This gets tupple mapping with data about the file that a headder block describes.
        The elements returned are similar to that displayed by the full catalog.
        headderdata is optional but saves resources.
        """

        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()

        details={"filenumber":self.filenumber,
                 "filename":self.GetFileName(headderdata),
                 "rawfilename":self.GetRawFileName(headderdata),
                 "sectors":self.GetSectorsUsed(headderdata),
                 "filetype":self.GetFileType(headderdata),
                 "filetypeshort":self.GetFileTypeCatString(headderdata),
                 "filetypelong":self.GetFileTypeString(headderdata),
                 "filelength":self.GetFileLength(headderdata),
                 "catextradata":""
                 }
        if(details["filetype"]==4):
            #code
            details["codeaddress"]=self.GetCodeStart(headderdata)
            details["catextradata"]="%5d,%d" % (self.GetCodeStart(headderdata),self.GetFileLength(headderdata))
            
        if(details["filetype"]==1):
            #basic
            details["autostartline"]=self.GetAutostartLine(headderdata)
            details["variableoffset"]=self.GetVariableOffset(headderdata)
            details["catextradata"]="%5d" % self.GetAutostartLine(headderdata)
        
        if(details["filetype"]==2 or details["filetype"]==3):
            #number or character array
            details["variableletter"]=self.GetVariableLetter(headderdata)
            details["variablename"]=self.GetVariableName(headderdata)
            details["arraydescriptor"]=self.GetArrayDescriptor(headderdata)
        
        return details

    def GetFileDetailsString(self,headderdata=None):
        """
        This gets a String respresentation of the file that a headder block describes.
        The format of the returned string is similar to that displayed by the full catalog.
        headderdata is optional but saves resources.
        """
        
        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()

        s="   %2d   %s%4d      %s" % (self.filenumber,self.GetFileName(headderdata),self.GetSectorsUsed(headderdata),self.GetFileTypeCatString(headderdata))
        t=self.GetFileType(headderdata)
        if(t==4):
            #code
            s+="         %5d,%d" % (self.GetCodeStart(headderdata),self.GetFileLength(headderdata))
            
        if(t==1):
            #basic
            s+="         %5d" % self.GetAutostartLine(headderdata)
        
        return s

    def GetAutostartLine(self,headderdata=None):
        """
        This returns the Autostart line number for a BASIC file.
        Returns the line number to automatically start at when a BASIC file is loaded.
        Returns -1 if no Autostart line is specified, or -2 if not a BASIC file.
        headderdata is optional but saves resources.
        """
         
        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()
        
        if(ord(headderdata[0])!=1):
            return -2
        
        val=ord(headderdata[218])+256*ord(headderdata[219])
        
        if(val>=32768):
            return -1
            
        return val

    def GetVariableOffset(self,headderdata=None):
        """
        This returns the offset to the start of the variable area in a BASIC file. If this is the same
        as the length of the BASIC file then there are no variables saved with the program.
        Returns the byte offset to the start of the variables in the file, or -2 if this object
        is not a BASIC file.
        headderdata is optional but saves resources.
        """
        
        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()

        if(ord(headderdata[0])!=1):
            return -2

        return ord(headderdata[216])+256*ord(headderdata[217])

    def GetCodeStart(self,headderdata=None):
        """
        This returns the address where a code file was saved from, and is the sugested address to
        load it to.
        Returns the code address for a code block, or -2 if this object is not a code file.
        headderdata is optional but saves resources.
        """

        if(ord(headderdata[0])!=4):
            return -2
            
        return ord(headderdata[214])+256*ord(headderdata[215])

    def GetVariableLetter(self,headderdata=None):
        """
        This returns the character of the variable described by an array.
        Returns the character value of a variable, or None if this
        object is not a number or character array.
        headderdata is optional but saves resources.
        """
        
        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()

        if(ord(headderdata[0])==2 or ord(headderdata[0])==3):
            return None
        
        return chr((ord(headderdata[216])&127)|64)

    def GetVariableName(self,headderdata=None):
        """
        This returns the name of the variable described by an array.
        This is the letter name of the array, followed by '$' if it is a character array.
        @return Returns the name of a variable, or null if this object is not a number or character array.
        headderdata is optional but saves resources.
        """
        
        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()

        if(ord(headderdata[0])!=2 and ord(headderdata[0])!=3):
            return None
            
        return self.GetVariableLetter(headderdata)+("$" if ord(headderdata[0])==2 else "")

    def GetArrayDescriptor(self,headderdata=None):
        """
        This returns the array descriptor of an array.
        The descriptor is an 8 bit number. The lower 6 bits hold the ASCII lower 6 bits of the variable
        name (must be a letter of the alphabet).
        Bits 6 and 7 describe what type of array the file. They are 64 for a
        character array, 128 for a number array, and 192 for a string array.
        
        Returns the array descriptor of the array, or -1 if this
        object is not a number or character array.
        
        headderdata is optional but saves resources.
        """
        
        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()

        if(ord(headderdata[0])!=2 and ord(headderdata[0])!=3):
            return -1

        return ord(headderdata[217])

    def GetSnapshotRegisters(self,headderdata=None):
        """
        This returns a dictionary of all the registers in a snapshot.
        It returns None if this file is not a valid snapshot file
        headderdata is optional but saves resources.
        
        The dictionary returned has the following keys:
        The Registers A, F, BC, DE, HL, IY, and IX are the standard Z80 registers.
        A', F', BC', DE', HL' are the alternate registers.
        PC is the program counter, SP is the stack pointer.
        I is the interupt register, and R the refresh register.
        IM is the interupt mode.
        IFF1, and IFF2 are the interupt flags denoting whether interupts are enabled or disabled.
        RAMbank denotes which RAM bank is paged onto loacation 0xC000.
        Screen denotes which screen is being displayed (0 if screen in RAM 5 (at 0x4000), and 1 if from RAM 7.
        ROM is 0 if 128K editor ROM paged in, and 1 if 48K ROM in place.
        IgnorePageChange is 1 if 0x7FFD is locked until a hard reset occurs, and 1 if it can be changed.
        """
         
        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()
        
        if(ord(headderdata[0])!=5 or ord(headderdata[0])!=9):
            return None
        
        regs={}
        #add registers
        regs["IY"]=ord(headderdata[220])+256*ord(headderdata[221])
        regs["IX"]=ord(headderdata[222])+256*ord(headderdata[223])
        regs["DE'"]=ord(headderdata[224])+256*ord(headderdata[225])
        regs["BC'"]=ord(headderdata[226])+256*ord(headderdata[227])
        regs["HL'"]=ord(headderdata[228])+256*ord(headderdata[229])
        regs["F'"]=ord(headderdata[230])
        regs["A'"]=ord(headderdata[231])
        regs["DE"]=ord(headderdata[232])+256*ord(headderdata[233])
        regs["BC"]=ord(headderdata[234])+256*ord(headderdata[235])
        regs["HL"]=ord(headderdata[236])+256*ord(headderdata[237])
        regs["I"]=ord(headderdata[239])
        #value of interupt mode is coded in the I register
        regs["IM"]=1 if (regs["I"]==0 or regs["I"]==63) else 2
        regs["SP"]=ord(headderdata[240])+256*ord(headderdata[241])

        #load up memory        
        mem=self.GetFileData(False,headderdata)

        #handle 128K specific stuff
        if(ord(headderdata[0])==9):
            #get which rambank is paged in
            regs["RAMbank"]=ord(mem[0])&7
            #get which screen
            regs["Screen"]=ord(mem[0]>>3)&1
            #get which ROM
            regs["ROM"]=ord(mem[0]>>4)&1
            #are we ignoreing output to 0x7FFD
            regs["IgnorePageChange"]=ord(mem[0]>>5)&1
            #now set mem to be which pages are loaded
            #RAM5 is at 0x4000 to 0x7FFF
            #RAM2 is at 0x8000 to 0xBFFF
            #paged RAM is at 0xC000 to 0xFFFF
            #Ram banks are offset by 1 byte at [0] which is a record of which bank is paged in
            mem=mem[0x14001:0x18000]+mem[0x8001:0xC000]+mem[regs["RAMbank"]*0x4000+1:(regs["RAMbank"]+1)*0x4000]
        
        #now we have an image of the working RAM at time of snapshot, and can figure out where the stack is
        #extract stack
        mem=mem[regs["SP"]-0x4000:regs["SP"]-0x4000+6]
        
        regs["R"]=ord(mem[1])
        regs["IFF1"]=(ord(mem[0])>>2)&1
        regs["IFF2"]=regs["IFF1"]
        regs["F"]=ord(mem[2])
        regs["A"]=ord(mem[3])
        regs["PC"]=ord(mem[4])+256*ord(mem[5])

        #SP contains values for the R register, AF, and PC pushed on it, hence needs to be 6 higher
        regs["SP"]=(regs["SP"]+6)&0xFFFF

        return regs

    def __str__(self,headderdata=None):
        """
        This returns a basic String summary of the DiscipleFile object.
        This is the same as for a detailed catalog entry but with excess spaces stripped
        headderdata is optional but saves resources.
        """
        
        return self.GetFileDetailsString(headderdata).strip()

    def GetDiscipleFileDetails(self,headderdata=None):
        """
        This returns details of the DiscipleFile object usefull for debugging.
        headderdata is optional but saves resources.
        """
        
        #if no headder supplied, need to load it up
        if(headderdata==None):
            headderdata=self.GetHeadder()

        t=self.GetFileType(headderdata)

        s='filenumber: %d\nFile name: "%s"\n' % (self.filenumber,self.GetFileName(headderdata))
        s+="File type: %d = %s\n" % (t,self.GetFileTypeString(headderdata))
        s+="File length: %d(%X)\n" % (self.GetFileLength(headderdata),self.GetFileLength(headderdata))

        if(t==1): #basic
            s+="Autostart: %d\n" % self.GetAutostartLine(headderdata)
            s+="Variable offfset: %d(%X)\n" % (self.GetVariableOffset(headderdata),self.GetVariableOffset(headderdata))
        
        elif(t==2 or t==3): #number array, or string array
            s+="variable name: %s\n" % self.GetVariableName(headderdata)
        
        elif(t==4 or t==7): #code or screen$
            s+="code start address: %d(%X)\n" % (self.GetCodeStart(headderdata),self.GetCodeStart(headderdata))

        s+="file details: %s\n" % self.GetFileDetailsString(headderdata)
        s+="directory entry address: T=%d S=%d offset=%d\n" % ((self.filenumber-1)/20,(((self.filenumber-1)/2)%10)+1,((self.filenumber-1)&1)*256)
        s+="Number of sectors used: %d\n" % self.GetSectorsUsed(headderdata)

        track=ord(headderdata[13])
        sector=ord(headderdata[14])
        i=self.GetSectorsUsed(headderdata)
        
        s+="Sector chain: "
        while(i>0):
            s+=" %d;%d(%X)" % (track,sector,self.image.GetSectorPos(track&127,sector,track>>7))
            sectordata=self.image.GetSector(track&127,sector,track>>7)
            track=ord(sectordata[510])
            sector=ord(sectordata[511])
            i-=1

        s+=" %d;%d" % (track,sector)
        
        return s
    
class DiscipleImage:
    """A class that holds a +D/Disciple disk image."""

    def __init__(self,fileName=None):
        self.ImageSource="Undefined"
        self.ImageFormat="Unknown"
        
        if(fileName!=None):
            self.setFileName(fileName)
        
    def setFile(self,filehandle,form="Unknown"):
        """
        sets the source for the disciple image to be an open file
        """
        
        self.ImageSource="File"
        self.filehandle=filehandle
        self.setImageFormat(form)
    
    def setFileName(self,filename,form="Unknown",accessmode="rb"):
        """
        sets the source for the disciple image to be a file wiuth the given name.
        Will close this file upon deletion of this object
        """
        try:
            self.filehandle=open(filename,accessmode)
        except:
            raise spectrumtranslate.SpectrumTranslateException('can not open "%s" for reading' % filename)
            return

        self.ImageSource="FileName"
        self.setImageFormat(form)
    
    def setBytes(self,bytedata,form="Unknown"):
        """
        sets the source for the disciple image to be abyte array in a string
        """

        self.ImageSource="Bytes"
        self.bytedata=bytedata[:]
        self.setImageFormat(form)

    def setImageFormat(self,form):
        """
        sets the format for the image:
        "MGT" is side 0 track 0, side 1 track 0, side 0 track 1, side 1 track 1, etc
        "IMG" is side 0 track 0, side 0 track 1, side 0 track 2, ... side 0 track 79, side 1 track 0, side 1 track 1, etc
        """
        if(form=="MGT" or form=="IMG" or form=="Unknown"):
            self.ImageFormat=form
            return
            
        raise spectrumtranslate.SpectrumTranslateException('Only valid image formats are "MGT" and "IMG"')

    def GuessImageFormat(self):
        """
        This method will try and work out and set the image format for this image.
        """
        
        #simplest way I can think of is to try out the different formats
        self.ImageFormat="MGT"
        if(self.CheckImageIsValid(True)):
            return self.ImageFormat
        
        self.ImageFormat="IMG"
        if(self.CheckImageIsValid(True)):
            return self.ImageFormat

        self.ImageFormat="Unknown"
        return self.ImageFormat

    def __del__(self):
        #close filehandle if needed
        if(self.ImageSource=="FileName"):
            self.filehandle.close()        

    def GetSectorPos(self,track,sector,head=-1):
        """
        Calculate the offset in the buffer for the specified sector. This takes into account the image format.
        track is the track from 0 to 79, sector is the sector from 1 to 10, head is the head from 0 to 1.
        head is optional as often the head is embeded as bit 7 of track. If head is not defined or set to -1
        then this method will extract the head from bit 7 of track, and binary and with 127 to remove bit 7.
        Returns the offset in bytes to the start of the specified sector.
        """

        #if we don't know what format we've got then guess
        if(self.ImageFormat=="Unknown"):
            self.GuessImageFormat()

        #is head part of track?
        if(head==-1):
            head=(track>>7)&1
            track&=127

        #sanity check on inputs
        if(head<0 or head>1):
            raise spectrumtranslate.SpectrumTranslateException('Valid head values are 0 and 1')

        if(sector<1 or sector>10):
            raise spectrumtranslate.SpectrumTranslateException('Valid sector values are 1 to 10 inclusive')

        if(track<0 or track>79):
            raise spectrumtranslate.SpectrumTranslateException('Valid track values are 0 to 79 inclusive')

        if(self.ImageFormat=="MGT"):
            return ((sector-1)+(head*10)+(track*20))*512
            
        #otherwise is img file format
        return ((sector-1)+(head*800)+(track*10))*512

    def GetSector(self,track,sector,head=-1):
        """Returns a byte string array of the sector requested."""
        
        #where is sector we're after
        pos=self.GetSectorPos(track,sector,head)
        
        if(self.ImageSource=="Bytes"):
            return self.bytedata[pos:pos+512]

        elif(self.ImageSource=="File" or self.ImageSource=="FileName"):
            if(self.filehandle.tell()!=pos):
                self.filehandle.seek(pos)
                
            return self.filehandle.read(512)
        
        else:
            raise spectrumtranslate.SpectrumTranslateException('Uninitiated DiscipleImage')

    def WriteSector(self,data,track,sector,head=-1):
        """Writes supplied sector to image. data is a 512 byte string to write. If the image is
        not initiated, then it will be set up as a byte image. You will need to save off the
        data at the end to save any changes."""

        if(len(data)!=512 or not isinstance(data,str)):
            raise spectrumtranslate.SpectrumTranslateException('Sector data must be a 512 byte string.')

        #if we've got uninitiated DiscipleImage then set up as byte array
        if(self.ImageSource=="Undefined"):
            self.setBytes('\x00'*819200)
            
        #where is sector we're after
        pos=self.GetSectorPos(track,sector,head)
        if(self.ImageSource=="Bytes"):
            self.bytedata=self.bytedata[:pos]+data+self.bytedata[pos+512:]

        elif(self.ImageSource=="File" or self.ImageSource=="FileName"):
            #have we got overwrite access?
            if(len(self.filehandle.mode)!=3 or 0 in [c in self.filehandle.mode for c in "r+b"]):
                #if not we can't write to it
                raise spectrumtranslate.SpectrumTranslateException('DiscipleImage not opened with access mode rb+')

            #memory map the sector in the file
            mm=mmap.mmap(self.filehandle.fileno(),0)
            #write the data
            mm[pos:pos+512]=data
            mm.flush()
            mm.close()
        
        #this should not happen, but be cautious
        else:
            raise spectrumtranslate.SpectrumTranslateException('Uninitiated DiscipleImage')

    def DeleteEntry(self,entrynumber):
        """
        This method deletes the specified entry in this disk image. Valid entry numbers are 1 to 80.
        """

        #check input
        if(entrynumber>80 or entrynumber<1):
            raise spectrumtranslate.SpectrumTranslateException('Invalid file enty number (must be 1 to 80 inclusive).')
        
        #work out track, sector, and offset for file descriptor byte for file
        headderstart=((entrynumber-1)&1)*256
        track=(entrynumber-1)/20
        sector=(((entrynumber-1)/2)%10)+1
        
        sectordata=self.GetSector(track,sector)
        #set file type byte to 0 to mark it deleted
        sectordata=sectordata[:headderstart]+'\x00'+sectordata[headderstart+1:]
        self.WriteSector(sectordata,track,sector)
        

    def CheckImageIsValid(self,deeptest=False):
        """
        This method will go through all the file entries in an image and ensure they
        have propper values, and that sectors don't overlap.
        N.B. this might return False for an image that works in real life (like hidden sectors
        in the FAT table that aren't in the file chain).
        if deeptest is True, then will go through each track and sector of a file ensureing that
        it matches the FAT. This will involve loading lots of sectors and may take some time.
        """

        #create empty sector map        
        sectorMap=[0]*195
        
        track=-1
        sector=-1
        #iterate through all headders
        for entry in range(1,81):
            headderstart=((entry-1)&1)*256
            #only load sector if needed
            if(track!=(entry-1)/20 or sector!=(((entry-1)/2)%10)+1):
                track=(entry-1)/20
                sector=(((entry-1)/2)%10)+1
                headder=self.GetSector(track,sector,0)
            
            #is filetype (excluding flags) consistent with valid file?
            filetype=ord(headder[headderstart])&31
            #ignore empty sectors
            if(filetype==0):
                continue
            
            if(filetype>11):
                return False
            
            #check sector map
            sectorcount=0
            for i in range(195):
                if(sectorMap[i]&ord(headder[headderstart+15+i])!=0):
                    #we have conflicting FAT entries
                    return False
                
                #update sector map
                sectorMap[i]|=ord(headder[headderstart+15+i])
                #work out number of sectors used
                sectorcount+=bin(ord(headder[headderstart+15+i])).count("1")
            
            #check number of sectors line up with FAT table
            if(sectorcount!=ord(headder[headderstart+12])+256*ord(headder[headderstart+11])):
                return False

            #compare file length against sectors used in FAT table for length workoutable files
            filelen=-1
            if(filetype==1 or filetype==2 or filetype==3 or filetype==4 or filetype==7 or filetype==13):
                #1=basic,2=number array,3=string array,4=code,7=screen$,13=unidos create file
                filelen=ord(headder[headderstart+212])+256*ord(headder[headderstart+213])
            elif(filetype==5):
                #48K snapshot
                filelen=49152 #3 * 16K ram banks
            elif(filetype==9):
                #128K snapshot
                filelen=131073 #1 byte page register value + 8 16K ram banks
            elif(filetype==10):
                #opentype
                filelen=ord(headder[headderstart+212])+256*ord(headder[headderstart+213])+65536*ord(headder[headderstart+210])
            elif(filetype==11):
                #execute
                filelen=510

            #BASIC, code, number array, string array, or screen have 1st 9 bytes of file as copy of headder data.
            if((filetype>0 and filetype<5) or filetype==7):
                filelen+=9

            #compare it to number of sectors used
            if(filelen!=-1):
                #work out how many sectors should be used. round up
                estimatedsectors=(filelen+509)/510
                #now see if matches
                if(sectorcount!=estimatedsectors):
                    return False
            
            #check start sector is in FAT
            startsector=ord(headder[headderstart+14])
            starttrack=ord(headder[headderstart+13])

            #calculate offset & bit of this track & sector in sectorMap
            o=(starttrack&127)+(80 if starttrack>=128 else 0)-4
            o*=10
            o+=startsector-1
            b=1<<(o%8)
            o/=8
            #check if is sector owned by this file
            if((sectorMap[o]&b)!=b):
                return False
            
            if(deeptest):
                #go through file chain matching against sector map & ensure sector map is empty at the end
                
                #get map of sectors used
                sm=[ord(x) for x in headder[headderstart+15:headderstart+210]]

                #if we don't know size of file then estimate it
                if(filelen==-1):
                    filelen=sectorcount*510
                
                #get start track & sector
                t=starttrack
                s=startsector
                
                #now move through
                while(sectorcount>0):
                    #have we reached early end of file?
                    if(t==0 and s==0):
                        return False
                    
                    #do we have valid sector?
                    if((t&127)>79 or t<4 or s<1 or s>10):
                        return False
                    
                    #calculate offset & bit of this track & sector in sectorMap
                    o=(t&127)+(80 if t>=128 else 0)-4
                    o*=10
                    o+=s-1
                    b=1<<(o%8)
                    o/=8
                    #check if is sector owned by this file
                    if((sm[o]&b)!=b):
                        return False
                        
                    #remove from copy of sectorMap
                    sm[o]-=b
                    
                    #load next sector in chain
                    sectordata=self.GetSector(t&127,s,t>>7)
                    
                    #update track & sector
                    t=ord(sectordata[510])
                    s=ord(sectordata[511])
                    #update number of bytes left to copy
                    filelen-=min(510,filelen)
                    #decrement number of sectors left to fetch
                    sectorcount-=1
                
                #track & sector of last sector read should be 0
                if(t!=0 and s!=0):
                    return False
                
                #sectorMap should now be blank, otherwise there are unused sectors
                for i in sm:
                    if(i!=0):
                        return False
                
        return True

    def IterateDiscipleFiles(self):
        """
        This method allows a user to iterate through all the files in this image useing for.
        eg: disciplefiles=[df for df in discipleimage.IterateDiscipleFiles()]
        """

        i=1
        while(i<=80):
            yield DiscipleFile(self,i)
            i+=1

def usage():
    """
    returns the command line arguments for disciplefile as a string.
    """

    return"""usage: python disciplefile.py instruction [args] infile outfile

    moves data from infile which should be a disciple disc image file and
    outputs it to outfile.
    
    instruction is required and specifies what you want to do. It must be 'list'
    'delete' or 'extract'. 'list' will list the contents of the specified image
    file. 'delete' will output a copy of the input with the specified file(s)
    deleted.'extract' extracts the data from an image file entry to wherever you
    want.
    
    infile and outfile are required unless reading from the standard input or
    outputting to the standard output. Usually arguments are ignored if they
    don't apply to the selected instruction.

    For the extract instruction, the index of the image file you want to extract
    must be specified before the filenames.
    
    For the delete instruction, the index of the file in the disk image you want
    to delete must be specified before the filenames. You can have ranges of
    indexes if you want to delete more that one file from the image. The syntax
    is the same as for the -s flag. You can use the -s flag in the delete
    instruction in which case you should not specify a file index before the
    input or output files.
    
    general flags:    
    -o specifies that the output from this program is to be directed to the
       standard output and not outputfile which should be omited. It can be used
       for all instructions.
    --tostandardoutput same as -o.
    -i specifies that this program gets it's data from the standard input and
       not inputfile which should be omited. It can be used for all
       instructions.
    --fromstandardinput same as -i.
    -s specifies which file entries you want. These are the same as returned by
       the list instruction. You can specify more than one, seperated by commas,
       and can even specify ranges of them with a minus. The numbers are assumed
       to be decimal unless preceded by 0x in which case they are assumed to be
       hexadecimal. For example 2,0x10-20,23 will specify entry 2, 16 to 20
       inclusive, and 23. This flag can be used in the list and delete commands.
    --specifyfiles same as -s.
    --specificfiles same as -s.
    
    list flags:
    -d specifies that we want all information about each file entry divided by
       tabs. All entries begin with the index of the entry in the image file,
       followed by the file name (there might be a name in an empty slot if the
       file has been deleted), the file type number, the filetype string, the
       number of sectors used on the disk, and the file length. Further data
       depends on the file type.
       For Program files, The autostart line number (or 0 if there isn't one),
       and the offset in bytes to the atached variables (will be the same as the
       length if there are no variables) follow.
       For Code files there follows the address where the code was saved from
       (and would automatically be loaded to).
       For array files there follows the the array letter, the array variable
       name, and the array descriptor specifying what sort of array it contains.
    --details is the same as -d.
    -l specifies that you want empty file slots to be returned in the listing.
       Normally these are omitted from a listing for increased clarity and
       brevity.
    --listempty same as -l.
"""

def CommandLine(args):
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
    listempty=False

    #handle no arguments
    if(len(args)==1):
        mode='help'    
    
    #go through arguments analysing them
    while(i<len(args)-1):
        i+=1

        arg=args[i]
        if(arg=='help' or arg=='extract' or arg=='list' or arg=='delete'):
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
        
        if(arg=='-l' or arg=='-listempty' or arg=='--l' or arg=='--listempty'):
            listempty=True
            continue
        
        if(arg=='-s' or arg=='-specifyfiles' or arg=='-specificfiles' or arg=='--s' or arg=='--specifyfiles' or arg=='--specificfiles'):
            i+=1
            specifiedfiles=getindices(args[i])
            if(specifiedfiles==None):
                error='"'+args[i]+'" is invalid list of file indexes.'
                break

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

        #check if is what entry we want to extract
        if(mode=='delete' and entrywanted==None and specifiedfiles==None):
            try:
                specifiedfiles=getindices(arg)
                continue
                
            except:
                error='%s is not a valid index in the input file.' % arg
                break

        #check if is input or output file
        #will be inputfile if not already defined, and fromstandardinput is False
        if(inputfile==None and fromstandardinput==False):
            inputfile=arg
            continue

        #will be outputfile if not already defined, tostandardoutput is False, and is last
        #argument
        if(outputfile==None and tostandardoutput==False and i==len(args)-1):
            outputfile=arg
            continue

        error='"%s" is unrecognised argument.' % arg
        break

    if(error==None and mode==None):
        error='No command (list, extract, delete, or help) specified.'

    if(error==None and inputfile==None and fromstandardinput==False and mode!='help'):
        error='No input file specified.'
    
    if(error==None and outputfile==None and tostandardoutput==False and mode!='help'):
        error='No output file specified.'

    if(error==None and entrywanted==None and mode=='extract'):
        error='No file index specified to extract.'

    if(error==None and specifiedfiles==None and entrywanted==None and mode=='delete'):
        error='No file index(s) specified to delete.'

    #handle error with arguments
    if(error!=None):
        sys.stderr.write(error+"\n")
        sys.stdout.write("Use 'python disciplefile.py' to see full list of options.\n")
        sys.exit(2)
    
    #if help is needed display it
    if(mode=='help'):
        sys.stdout.write(usage())
        sys.exit(0)

    #get disc image
    if(fromstandardinput==False):
        #if we're deleteing or copying then we need to work with a copy of the input file
        if(mode=='delete' or mode=='copy'):
            with open(inputfile,'rb') as infile:
                di=DiscipleImage()
                di.setBytes(infile.read())
                
        else:
            di=DiscipleImage(inputfile)
    
    else:
        di=DiscipleImage()
        di.setBytes(sys.stdin.read())
    
    #now do command
    if(mode=='list'):
        for df in di.IterateDiscipleFiles():
            retdata='' if wantdetails else "  pos   filename  sectors   type\n"
            for df in di.IterateDiscipleFiles():
                if(specifiedfiles!=None and not df.filenumber in specifiedfiles):
                    continue
                
                if(listempty==False and df.IsEmpty()):
                    continue
                    
                if(wantdetails):
                    d=df.GetFileDetails()
        
                    retdata+="%i\t%s\t%i\t%s\t%i\t%i" % (d['filenumber'],d['filename'],d['filetype'],d['filetypelong'],d['sectors'],d['filelength'])
                    
                    if(d["filetype"]==1):
                        retdata+="\t"+str(d["autostartline"])+"\t"+str(d["variableoffset"])
        
                    if(d["filetype"]==4):
                        retdata+="\t"+str(d["codeaddress"])
        
                    if(d["filetype"]==2 or d["filetype"]==3):
                        retdata+="\t"+str(d["variableletter"])+"\t"+str(d["variablename"])+"\t"+str(d["arraydescriptor"])
                    
                else:
                    retdata+=df.GetFileDetailsString()
        
                retdata+="\n"

    if(mode=='extract'):
        df=DiscipleFile(di,entrywanted)
        if(entrywanted>80 or entrywanted<1):
            sys.stderr.write(str(entrywanted)+" is not a valid entry number (should be 1 to 80).\n")
            sys.stdout.write("Use 'python disciplefile.py' to see full list of options.\n")
            sys.exit(2)
            
        retdata=df.GetFileData()

    if(mode=='delete'):
        if(specifiedfiles==None):
            specifiedfiles=[entrywanted]
        
        for i in specifiedfiles:
            if(i>80 or i<1):
                sys.stderr.write(str(i)+" is not a valid entry number (should be 1 to 80).\n")
                sys.stdout.write("Use 'python disciplefile.py' to see full list of options.\n")
                sys.exit(2)
            
            di.DeleteEntry(i)
        
        #now set disk image as output
        retdata=di.bytedata


    #output data
    if(tostandardoutput==False):
        fo=open(outputfile,"wb")
        fo.write(retdata)
        fo.close()

    else:
        sys.stdout.write(retdata)


if __name__=="__main__":
    import sys

    CommandLine(sys.argv)
