import spectrumtranslate

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

    def GetFileData(self):
        """Get the data of the file. Returns a byte string array containing the file data."""

        #load file headder
        headder=self.GetHeadder()

        #make note of number of sectors in file
        i=self.GetSectorsUsed(headder)
        
        #get map of sectors used
        sectorMap=[ord(x) for x in headder[15:210]]
        
        bytestocopy=self.GetFileLength(headder)
        
        data=""
        
        #get start track & sector
        track=ord(headder[13])
        sector=ord(headder[14])
        
        #BASIC, code, number array, string array, or screen have 1st 9 bytes of file as copy of headder data.
        #can be ignored and can be infered from the directory entry
        t=self.GetFileType(headder)
        if((t>0 and t<5) or t==7):
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
        
        #is stored at offset 11 in motorola byte order (most significant byte first)
        return ord(headderdata[12])+256*ord(headderdata[11])

    def GetFileLength(self,headderdata=None):
        """
        Returns the length of this file.
        headderdata is optional but saves resources.
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

        return ("","BAS","D.ARRAY","$.ARRAY","CDE","SNP 48k","MD.FILE","SCREEN$","SPECIAL","SNP 128k","OPENTYPE",
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
            details["catextradata"]="%5d" % self.GetAutostartLine(headderdata)
        
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

        s+="file details: %s" % self.GetFileDetailsString(headderdata)
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
    
    def setFileName(self,filename,form="Unknown"):
        """
        sets the source for the disciple image to be a file wiuth the given name.
        Will close this file upon deletion of this object
        """
        try:
            self.filehandle=open(filename,"rb")
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

if __name__=="__main__":
    di=DiscipleImage("/home/william/java/tap reader/01.img")

    for df in di.IterateDiscipleFiles():
        print df.GetFileDetailsString()
    
    print di.CheckImageIsValid(True)
    print di.ImageFormat
