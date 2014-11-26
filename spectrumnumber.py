class SpectrumNumberException(Exception):
    """
    A class to flag up an Exception raised during working with SpectrumNumber class objects
    """
    
    def __init__(self,arg):
#        Exception.__init__(self,arg)
        self.value=arg
    
    def __str__(self):
        return repr(self.value)
        
"""
SpectrumNumberComparisonPrecission determines how precicely the equals compares two numbers.
It is essentially the number of least significant bits in the mantissa of the difference
between two numbers to ignore. The Spectrum didn't ignore any, but this caused some odd 
logic such as "((-1.5)-(-2))=0.5" returns 0 (false), but "0.5=((-1.5)-(-2))" returns 1 (true).
N.B. '=' in the Spectrum is the same as '==' in python when used for comparison
For authentic Number comparison set this to 0, but 2 seems to iron out most of the odd behaviour,
and make it useable.
"""
spectrum_number_comparison_precission=2

class SpectrumNumber:
    """
    A class that emulates a ZX Spectrum (48K & 128K) 40 bit number.
    This format allows for both integer & floating points to be emulated.
    On the origional Spectrum, BASIC numbers are held in 5 bytes (40 bits).
    The 5 bytes hold different values depending on whether it is representing a 16 bit integer, or a floating point number.
    
    If a 16 bit integer is being held, then the first byte is 0, byte 1 is 0 for a positive integer, and 255 for a negative integer.
    Bytes 2 and 3 hold the 16 bit value of the integer with the least significant byte (bits 0-7) in byte 2, and the most significant byte (bits 8-15) in byte 3.
    If the integer is negative then 65536 is added to it before it is stored in bytes 2 and 3.
    
    For floating point numbers, the first byte is the base 2 exponent + 128 (so exponent 0 is 128, -127 is 1, +127 is 255 etc).
    The remaining 4 bytes hold the mantissa.
    Because the mantissa is adjusted so that the top bit always holds the most significant bit, it is always 1.
    This bit is thus used to encode the sign of the number - 1 for negative and 0 for positive.
    You have to remember to set the most significant bit to 1 when converting the number back.
    """
    #An array of bytes holding the details of the largest positive number that a SpectrumNumber can hold.
    #This can be used to initialise or set a SpectrumNumber.
    MAX_VALUE=(0xFF,0x7F,0xFF,0xFF,0xFF)

    #An array of bytes holding the details of the smallest positive nonzero number that a SpectrumNumber can hold.
    #This can be used to initialise or set a SpectrumNumber.
    #@see #SpectrumNumber(byte[])
    MIN_VALUE=(0x01,0x00,0x00,0x00,0x00)

    def __init__(self,data=None,listContainsBytes=False):
        """
        Creates a SpectrumNumber object.
        optional argument data is a 1-5 number list to initialise the Spectrumnumber,
        or another SpectrumNUmber, or an int, or a float, or a long
        This raises an Exception if the float value is too big or too small to be represented by a SpectrumNumber, or
        the number list contains numbers not in the range 0-255, and not 1-5 numbers.
        The optional argument listContainsBytes is used if a list is supplied as a constructor, in which
        case the list contains numbers in the range -128 to +127
        """
        #array to hold 8bit exponent, 1 bit sign, and 31 bit mantissa
        #1st byte is exponent+128
        #bit 7 of 2nd byte is sign:0=positive, 1=negative
        #remaining 31 bits are mantissa. NB is actually 32 bit, with most significant bit always 1
        #small integers: -65535 to 65535 are stored with byte0=0, byte1=0positive/FFnegative, bytes 2&3 16 bit value
        self.data=[0,0,0,0,0]

        self.SetValue(data,listContainsBytes)

    #IO Methods

    def SetValue(self,data=None,listContainsBytes=False):
        """
        sets the value of a SpectrumNumber object.
        Argument data is a 1-5 number list,
        another SpectrumNumber, an int, a float, or a tuple.
        This raises an Exception if the float value is too big or too small to be represented by a SpectrumNumber, or
        the number list contains numbers not in the range 0-255, and not 1-5 numbers.
        """
        if(data==None):
            return

        #if is tuple, then cast to list
        if(data is ()):
            data=list(data)

        if(isinstance(data,list)):
            #should be 1-5 numbers between 0 and 255 inclusive
            if(len(data)<1 or len(data)>5):
                raise SpectrumNumberException("List or Tuple argument must contain from 1 to 5 numbers")
            
            if(all(isinstance(val,(int,float,long)) for val in data) is False):
                raise SpectrumNumberException("List or Tuple argument must contain numbers")
            
            #check and correct if bytes supplied in list
            if(listContainsBytes):
                if(all(val>=-128 and val<=127 for val in data) is False):
                    raise SpectrumNumberException("List or Tuple argument must contain numbers from 0 to 255 inclusive (or -128 to +127 if bytes)")
                #convert byte to unsigned int
                data=[(byte+256)&255 for byte in data]
            
            if(all(val>=0 and val<=255 for val in data) is False):
                raise SpectrumNumberException("List or Tuple argument must contain numbers from 0 to 255 inclusive (or -128 to +127 if bytes)")
            
            #set to 0 in case doesn't contain 5 numbers
            self.data=[0,0,0,0,0]
            #copy data across
            for i in range(len(data)):
                self.data[i]=int(data[i])
            return
            
        if(isinstance(data,SpectrumNumber)):
            self.data=list(data.data)
            return

        if(isinstance(data,(long,int))):
            #if simple int, save it as such in spectrum format
            if(data<=65535 and data>=-65535):
                self.data[0]=0
                self.data[1]=data<0 and 0xFF or 0
                if(data<0):
                    data+=65536
                self.data[2]=data&0xFF
                self.data[3]=(data>>8)&0xFF
                self.data[4]=0
            else:
                #too big for simple format, but still able to save as floating point
                snc=SpectrumNumberComponents()

                snc.negative=data<0
                snc.exponent=32
                snc.mantissa=long(snc.negative and -data or data)
                snc.mantissa&=0xFFFFFFFF
                #shift to most significant byte
                while((snc.mantissa&0x80000000)==0):
                    snc.mantissa<<=1
                    snc.exponent-=1
                snc.exponent+=128

                self.SetValue(snc.get_SpectrumNumber())

            return

        if(type(data) is float):
            self.SetValue(get_SpectrumNumber_from_string(str(data)))
            return

        if(type(data) is str):
            self.SetValue(get_SpectrumNumber_from_string(data))
            return

        raise SpectrumNumberException("Invalid argument to SpectrumNumber constructor")


    def __str__(self):
        """
        Returns a String of the current SpectrumNumber.
        This is the same as the Spectrum display of a number as done by the routine at 0x2DE3 in the 48K Spectrum ROM.
        """
        return toString(self)


    def __float__(self):
        """Returns the current SpectrumNumber as a float."""
        
        if(self.data[0]==0): #simple integer number
            return float(self.GetSmallInt())
        
        #left with 5 byte floating point value:
        #byte 0 is exponent, bit 7 of byte 1 is sign (1=negative, 0 positive)
        #byte 1 from bit 6 onwards is mantisa, bit 7 should always be 1 but is used for sign

        man=((self.data[1]&0x7F)<<24)|((self.data[2])<<16)|((self.data[3])<<8)|(self.data[4])|0x80000000
        f=float(man)
        f/=256
        f/=256
        f/=256
        f/=128
        f*=2**(self.data[0]-129)
        if(self.data[1]>127):
            f*=-1

        return f
        
    def __complex__(self):
        return complex(self.__float__(),0)

    def __int__(self):
        return int(self.__float__())

    def __long__(self):
        return long(self.__float__())


#todo
#def __iadd__(self, other)
#def __isub__(self, other)
#def __imul__(self, other)
#def __idiv__(self, other)
#def __itruediv__(self, other)
#def __ifloordiv__(self, other)
#def __imod__(self, other)
#def __ipow__(self, other[, modulo])
#def __ilshift__(self, other)
#def __irshift__(self, other)
#def __iand__(self, other)
#def __ixor__(self, other)
#def __ior__(self, other)
#These methods are called to implement the augmented arithmetic assignments (+=, -=, *=, /=, //=, %=, **=, <<=, >>=, &=, ^=, |=)


    #comparison methods

    def __eq__(self,other):
        """
        Tests if this Spectrum Number holds the same value as another SpectrumNumber, or number.
        see details of spectrum_number_comparison_precission about how acurate the compatison is.
        """
      
        if(isinstance(other,(SpectrumNumber,int,long,float,str))):
            try:
                #first subtract one from the other (convert other to a Spectrum Number just in case)
                sn=Subtract(self,SpectrumNumber(other))
                
                #in Spectrum there is a bug with precission in the way numbers are added (and so subtracted)
                #try this in a spectrum (remember one '=' is same as == in python):
                #((-1.5)-(-2))=0.5 returns 0 (false), but
                #0.5=((-1.5)-(-2)) returns 1 (true).
                #This is because least significant bit of mantisa is 1 when subtract one way but not other
                #To get round this, see how many least significant bits to ignore
                return IsZero(sn) or sn.data[0]<=96+spectrum_number_comparison_precission
            except SpectrumNumberException:
                #if exception is raised constructing a spectrum number with the given
                #int or float, then it can't possibly equal a spectrum number
                return False
                
        return NotImplemented

    def __lt__(self,other):
        """Is this SpectrumNumber less than the supplied object?"""
        
        if(isinstance(other,(SpectrumNumber,int,long,float))):
            #first subtract one from the other (convert other to a Spectrum Number just in case)
            sn=Subtract(self,SpectrumNumber(other))

            #if difference is zero then are same so not less than
            if(IsZero(sn) or sn.data[0]<=96+spectrum_number_comparison_precission):
                return False

            #if result is less than zero then self must be less than other
            return LessThanZero(sn)
                
        return NotImplemented
        
    def __le__(self,other):
        """Is this SpectrumNumber less than or equal to the supplied object?"""
        
        if(isinstance(other,(SpectrumNumber,int,long,float))):
            #first subtract one from the other (convert other to a Spectrum Number just in case)
            sn=Subtract(self,SpectrumNumber(other))

            #if difference is zero then are equal
            if(IsZero(sn) or sn.data[0]<=96+spectrum_number_comparison_precission):
                return True

            #if result is less than zero then self must be less than other
            return LessThanZero(sn)
                
        return NotImplemented

    def __ne__(self,other):
        """Is this SpectrumNumber not equal to the supplied object?"""
        equal=self.__eq__(other)
        
        #if is not implemented then object can't be equal to this SpectrumNumber
        #otherwise return inverse of equal
        return equal==NotImplemented and True or (not equal)
        
    def __gt__(self,other):
        """Is this SpectrumNumber greater than the supplied object?"""
        
        if(isinstance(other,(SpectrumNumber,int,long,float))):
            #first subtract one from the other (convert other to a Spectrum Number just in case)
            sn=Subtract(self,SpectrumNumber(other))

            #if difference is zero then are same so not greater than
            if(IsZero(sn) or sn.data[0]<=96+spectrum_number_comparison_precission):
                return False

            #if result is greater than zero then self must be greater than other
            return GreaterThanZero(sn)
                
        return NotImplemented
        
    def __ge__(self,other):
        """Is this SpectrumNumber greater than or equal to the supplied object?"""
        
        if(isinstance(other,(SpectrumNumber,int,long,float))):
            #first subtract one from the other (convert other to a Spectrum Number just in case)
            sn=Subtract(self,SpectrumNumber(other))

            #if difference is zero then are equal
            if(IsZero(sn) or sn.data[0]<=96+spectrum_number_comparison_precission):
                return True

            #if result is greater than zero then self must be greater than other
            return GreaterThanZero(sn)
                
        return NotImplemented

    def IsZero(self):
        """Returns true if the SpectrumNumber is zero."""
        return IsZero(self)

    #for comparison reasons
    def __nonzero__(self):
        """Returns true if the SpectrumNumber is non zero."""
        return (not self.IsZero())

    #calculator command #36: less-0 (#3506)
    def LessThanZero(self):
        """
        Returns True if the SpectrumNumber is less than zero (negative).
        This is the same as the Spectrum floating point calculator command 0x36 at 0x3506 in the 48K Spectrum ROM.
        """
        return LessThanZero(self)

    #calculator command #37: greater-0 (#34F9)
    def GreaterThanZero(self):
        """
        Returns True if the SpectrumNumber is greater than zero.
        This is the same as the Spectrum floating point calculator command 0x37 at 0x34F9 in the 48K Spectrum ROM.
        """
        return GreaterThanZero(self)


    """        
    #todo
    #commands that can alter Spectrum Numbers (as done in spectrum calculator)
    /*
     * These still need implementing
       True binary operations.

          DEFW    L3851           ; $06 Address: $3851 - to-power
  
          DEFW    L353B           ; $09 Address: $353B - no-l-eql
          DEFW    L353B           ; $0A Address: $353B - no-gr-eql
          DEFW    L353B           ; $0B Address: $353B - nos-neql
          DEFW    L353B           ; $0C Address: $353B - no-grtr
          DEFW    L353B           ; $0D Address: $353B - no-less
          DEFW    L353B           ; $0E Address: $353B - nos-eql

        ;   Unary follow.

        DEFW    L37B5           ; $1F Address: $37B5 - sin
        DEFW    L37AA           ; $20 Address: $37AA - cos
        DEFW    L37DA           ; $21 Address: $37DA - tan
        DEFW    L3833           ; $22 Address: $3833 - asn
        DEFW    L3843           ; $23 Address: $3843 - acs
        DEFW    L37E2           ; $24 Address: $37E2 - atn
        DEFW    L3713           ; $25 Address: $3713 - ln
        DEFW    L36C4           ; $26 Address: $36C4 - exp
        DEFW    L384A           ; $28 Address: $384A - sqr

    ;   End of true unary.

        DEFW    L36A0           ; $32 Address: $36A0 - n-mod-m
        DEFW    L3783           ; $39 Address: $3783 - get-argt
    """

    #unary arithmetic methods

    #__invert__(self) (or ~) is not implemented as a SpectrumNumber can be a float,
    #and to only implement it some of the time would be inconsistant

    #calculator command #2A : abs (#346A)
    def Abs(self):
        """
        Sets this SpectrumNumber to hold the absolute (non-negative) value of what it curently holds.
        This is the same as the Spectrum floating point calculator command 0x2A at 0x3464 in the 48K Spectrum ROM.
        """
        self.SetValue(Abs(self))
        return self

    #do so can do abs(SpectrumNumber object)
    def __abs__(self):
        """
        returns this SpectrumNumber as absolute (non-negative) value of what it curently holds.
        """
        return Abs(self)

    #calculator command #1B : negate(#346E)
    def Negate(self):
        """
        Reverses the sign for this SpectrumNumber.
        This is the same as the Spectrum floating point calculator command 0x1B at 0x346E in the 48K Spectrum ROM.
        It efectively multiplies it by -1;
        """
        self.SetValue(Negate(self))
        return self

    def __neg__(self):
        """Returns negative version of this number"""
        return Negate(self)


    def __pos__(self):
        """Returns + version of this number (Doesn't seem to do much but implement anyway)"""
        return SpectrumNumber(self)

    #calculator command #29: sign (#3492)
    def Sign(self):
        """
        Sets this SpectrumNumber to the sign of the current value.
        The sign is -1 for a negative value, 0 for zero, and +1 for any positive value.
        This is the same as the Spectrum floating point calculator command 0x29 at 0x3492 in the 48K Spectrum ROM.
        """
        self.SetValue(Sign(self))
        return self

    #calculator command #3A : truncate (#3214)
    def Truncate(self):
        """
        Sets this SpectrumNumber to hold the integer truncate towards zero value of what it curently holds.
        Basically, the number is rounded down to the nearest whole number if above zero, or up to the nearest whole number if below zero.
        This is the same as the Spectrum floating point calculator command 0x3A at 0x3214 in the 48K Spectrum ROM.
        """
        self.SetValue(Truncate(self))
        return self


    #calculator command #27 : Int (#36AF)
    def Int(self):
        """
        Sets this SpectrumNumber to hold the integer value of what it curently holds.
        Basically, the number is rounded down to the nearest whole number.
        This is the same as the Spectrum floating point calculator command 0x27 at 0x36AF in the 48K Spectrum ROM.
        SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
        """
        self.SetValue(Int(self))
        return self

    #arithmetic methods        
#todo
#def __mod__(self, other)
#def __divmod__(self, other)
#def __pow__(self, other[, modulo])
#def __lshift__(self, other)
#def __rshift__(self, other)
#def __and__(self, other)
#def __xor__(self, other)
#def __or__(self, other)

    #calculator command #03 : subtract (#300F)
    def Subtract(self,val):
        """
        Subtracts the supplied SpectrumNumber from this SpectrumNumber.
        This is the same as the Spectrum floating point calculator command 0x03 at 0x300F in the 48K Spectrum ROM.
        SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
        """
        self.SetValue(Subtract(self,val))
        return self

    def __sub__(self,val):
        """
        Subtracts the supplied SpectrumNumber (or float,long, or int) from this SpectrumNumber using the -= syntax.
        This is the same as the Spectrum floating point calculator command 0x03 at 0x300F in the 48K Spectrum ROM.
        SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
        SpectrumNumberException is also raised if an incorect argument is supplied.
        """
        #if is long, int, or float convert to SpectrumNumber
        if(isinstance(val,(long,int,float))):
            val=SpectrumNumber(val)
            
        #ensure we have valid argument
        if(not isinstance(val,SpectrumNumber)):
            raise SpectrumNumberException("Argument must be SpectrumNumber, int, float, or long")

        return Subtract(self,val)

    #calculator command #0F : addition (#3014)
    def Add(self,val):
        """
        Adds the supplied SpectrumNumber to this SpectrumNumber.
        This is the same as the Spectrum floating point calculator command 0x0F at 0x3014 in the 48K Spectrum ROM.
        SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
        """
        self.SetValue(Add(self,val))
        return self

    def __add__(self,val):
        """
        Adds the supplied SpectrumNumber (or float,long, or int) to this SpectrumNumber using the += syntax.
        This is the same as the Spectrum floating point calculator command 0x0F at 0x3014 in the 48K Spectrum ROM.
        SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
        SpectrumNumberException is also raised if an incorect argument is supplied.
        """
        #if is long, int, or float convert to SpectrumNumber
        if(isinstance(val,(long,int,float))):
            val=SpectrumNumber(val)

        #ensure we have valid argument
        if(not isinstance(val,SpectrumNumber)):
            raise SpectrumNumberException("Argument must be SpectrumNumber, int, float, or long")

        return Add(self,val)

    #calculator command #04 : multiply (#30CA)
    def Multiply(self,val):
        """
        Multiplies this SpectrumNumber by the supplied SpectrumNumber.
        This is the same as the Spectrum floating point calculator command 0x04 at 0x30CA in the 48K Spectrum ROM.
        SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
        """
        self.SetValue(Multiply(self,val))
        return self

    def __mul__(self,val):
        """
        Multiplies the supplied SpectrumNumber (or float,long, or int) by this SpectrumNumber using the *= syntax.
        This is the same as the Spectrum floating point calculator command 0x04 at 0x30CA in the 48K Spectrum ROM.
        SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
        SpectrumNumberException is also raised if an incorect argument is supplied.
        """
        #if is long, int, or float convert to SpectrumNumber
        if(isinstance(val,(long,int,float))):
            val=SpectrumNumber(val)

        #ensure we have valid argument
        if(not isinstance(val,SpectrumNumber)):
            raise SpectrumNumberException("Argument must be SpectrumNumber, int, float, or long")

        return Multiply(self,val)

    #calculator command #05 : division (#31AF)
    def Divide(self,val):
        """
        Divides this SpectrumNumber by the supplied SpectrumNumber.
        This is the same as the Spectrum floating point calculator command 0x05 at 0x31AF in the 48K Spectrum ROM.
        SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
        """
        self.SetValue(Divide(self,val))
        return self
        
    def __floordiv__(self,val):
        """
        Divide this SpectrumNumber by the supplied SpectrumNumber. It Rounds down the result to the nearest integer.
        """
        self.Divide(val)
        self.Int()
        return self

    def __div__(self,val):
        """
        Divide the supplied SpectrumNumber (or float,long, or int) by this SpectrumNumber using the /= syntax.
        This is the same as the Spectrum floating point calculator command 0x05 at 0x31AF in the 48K Spectrum ROM.
        SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
        SpectrumNumberException is also raised if an incorect argument is supplied.
        """
        #if is long, int, or float convert to SpectrumNumber
        if(isinstance(val,(long,int,float))):
            val=SpectrumNumber(val)

        #ensure we have valid argument
        if(not isinstance(val,SpectrumNumber)):
            raise SpectrumNumberException("Argument must be SpectrumNumber, int, float, or long")

        return Divide(self,val)
        
    def __truediv__(self,val):
        #SpectrumNumbers represent float numbers, so __truediv__ is the same as __div__
        return self.__div__(val)
        
        
    #calculator command #3C : e-to-fp (#2D4F)
    #origional assumes that e is not more than 39
    def E_to_FP(self,exponent):
        """
        Multiplies this SpectrumNumber by 10 to the power of the supplied int.
        It essentially treats the current Value as the mantissa, with the supplied number as the base 10 exponent.
        This is the same as the Spectrum floating point calculator command 0x3C at 0x2D4F in the 48K Spectrum ROM.
        SpectrumNUmberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
        """
        self.SetValue(E_to_FP(self,exponent))
        return self


    """
    todo
    #calculator command #30: not (#3501)
    /**
     * Sets this SpectrumNumber to the logical NOT of the current value.
     * The logical NOT is 1 if the value is 0, or 0 if the value is not 0.
     * This is the same as the Spectrum floating point calculator command 0x30 at 0x3501 in the 48K Spectrum ROM.
     */
    public void Not() {
      SetValue(Not(this));
    }
    /**
     * Returns the logical NOT of the supplied SpectrumNumber.
     * The logical NOT is 1 if the value is 0, or 0 if the value is not 0.
     * This is the same as the Spectrum floating point calculator command 0x30 at 0x3501 in the 48K Spectrum ROM.
     * @param sn This is the SpectrumNumber you want the logical NOT of.
     * @return Returns a new SpectrumNumber holding the logical NOT.
     */
    public static SpectrumNumber Not(SpectrumNumber sn) {
      return new SpectrumNumber(0,0,IsZero(sn)?1:0,0,0);
    }

    #calculator command #07: or (#351B)
    /**
     * Sets this SpectrumNumber to the current value logical OR the supplied value.
     * The spectrum floating point calculator version of logical OR returns the first number if the second number is zero, otherwise it returns 0 if the first number is zero, and 1 if the first number is not zero.
     * This is the same as the Spectrum floating point calculator command 0x07 at 0x351B in the 48K Spectrum ROM.
     * @param sn This is the SpectrumNumber you want to combine to the current object using logical OR.
     */
    public void Or(SpectrumNumber sn) {
      SetValue(Or(this,sn));
    }
    /**
     * Returns the logical OR of the two supplied SpectrumNumbers.
     * The spectrum floating point calculator version of logical OR returns the first number if the second number is zero, otherwise it returns 0 if the first number is zero, and 1 if the first number is not zero.
     * This is the same as the Spectrum floating point calculator command 0x07 at 0x351B in the 48K Spectrum ROM.
     * @param sn1 This is the first SpectrumNumber you want the logical OR of.
     * @param sn2 This is the second SpectrumNumber you want the logical OR of.
     * @return Returns a new SpectrumNumber holding the logical OR of the two supplied numbers.
     */
    public static SpectrumNumber Or(SpectrumNumber sn1,SpectrumNumber sn2) {
      if(IsZero(sn2)) return new SpectrumNumber(sn1);
      return new SpectrumNumber(0,0,IsZero(sn1)?0:1,0,0);
    }

    #calculator command #08: no-&-no boolean (#3524)
    /**
     * Sets this SpectrumNumber to the current value boolean AND the supplied value.
     * The Spectrum floating point calculator implementation of boolean AND returns 0 if either number is 0, or the first number if neither number is zero.
     * This is the same as the Spectrum floating point calculator command 0x08 at 0x3524 in the 48K Spectrum ROM.
     * @param sn This is the SpectrumNumber you want to combine to the current object using boolean AND.
     */
    public void And(SpectrumNumber sn) {
      SetValue(And(this,sn));
    }
    /**
     * Returns the boolean AND of the two supplied SpectrumNumbers.
     * The Spectrum floating point calculator implementation of boolean AND returns 0 if either number is 0, or the first number if neither number is zero.
     * This is the same as the Spectrum floating point calculator command 0x08 at 0x3524 in the 48K Spectrum ROM.
     * @param sn1 This is the first SpectrumNumber you want the boolean AND of.
     * @param sn2 This is the second SpectrumNumber you want the boolean AND of.
     * @return Returns a new SpectrumNumber holding the boolean AND of the two supplied numbers.
     */
    public static SpectrumNumber And(SpectrumNumber sn1,SpectrumNumber sn2) {
      if(IsZero(sn2)) return new SpectrumNumber(0,0,0,0,0);
      return new SpectrumNumber(sn1);
    }


}
    """

    #return the small integer stored
    def GetSmallInt(self):
        return self.data[2]+256*self.data[3] - (self.data[1]==0xFF and 65536 or 0)

    #convert small int to full floating point
    def IntToFP(self):
        #first check if already is a floating point number
        if(self.data[0]!=0 or self.IsZero()):
            return SpectrumNumber(self)
  
        i=self.GetSmallInt()
        if(i<0):
            i*=-1
  
        e=144
        if(i<255):
            e=136
            i<<=8
  
        while(i<32768):
            e-=1
            i<<=1

        i&=0x7FFF
        i|=(self.data[1]&1)<<15
        
        self.SetValue([e,(i>>8)&0xFF,i&0xFF,0,0])
        return self

    def _get_internals(self,printdetails=True):
        #if is int then display this
        if(self.data[0]==0):
            s='%i %s' % (self.GetSmallInt(),self.data)
            if(printdetails==True):
                print s
            return s
            
        #else is float
        man=((self.data[1]&0x7F)<<24)|((self.data[2])<<16)|((self.data[3])<<8)|(self.data[4])|0x80000000
        f=float(man)
        f/=256
        f/=256
        f/=256
        f/=128
        f*=2**(self.data[0]-129)
        if(self.data[1]>127):
            f*=-1
        s='%f %s' % (f,self.data)
        if(printdetails==True):
            print s
        return s
"""
These are Module functions
"""
#unary arithmetic functions

def Abs(sn):
    """
    Returns the absolute (non-negative) value of the supplied SpectrumNumber.
    This is the same as the Spectrum floating point calculator command 0x2A at 0x3464 in the 48K Spectrum ROM.
    """
    #create copy to work with
    sn=SpectrumNumber(sn)
    #deal with floating point
    if(sn.data[0]!=0):
        sn.data[1]&=0x7F
    #deal with negative small ints
    elif(sn.data[1]!=0):
        sn.SetValue(-sn.GetSmallInt())

    return sn

def Negate(sn):
    """
    Returns the SpectrumNumber supplied with the sign inverted.
    It efectively multiplies it by -1;
    This is the same as the Spectrum floating point calculator command 0x1B at 0x346E in the 48K Spectrum ROM.
    """
    sn=SpectrumNumber(sn)

    if(sn.IsZero()):
        return sn

    #floating point numbers
    if(sn.data[0]!=0):
        #this will toggle bit 7: byte so will ignore any carry
        sn.data[1]+=128
        sn.data[1]&=0xFF
    #handle integer numbers
    else:
        sn.SetValue(-sn.GetSmallInt())

    return sn


def Truncate(sn):
    """
    Returns the integer truncate towards zero value of the supplied SpectrumNumber.
    Basically, the number is rounded down to the nearest whole number if above zero, or up to the nearest whole number if below zero.
    This is the same as the Spectrum floating point calculator command 0x3A at 0x3214 in the 48K Spectrum ROM.
    """
    #create copy to work with
    sn=SpectrumNumber(sn)

    e=sn.data[0]

    #return if is integer: so already truncated
    if(e==0):
        return sn

    #if small fraction then set to 0
    if(e<129):
        sn.SetValue([0,0,0,0,0])
        return sn

    #omit check for -65536 as this would incorrectly change it to -1
    #skip code from #3223 until 323E

    #if exponent is between 129 and 144
    if(e<145):
        #how many bits to shift to eradicate decimal
        e=144-e
        #sign
        s=(sn.data[1]&128)==128 and -1 or 1
        #get number & set most significant bit (bit 15)
        n=(sn.data[2]+256*sn.data[1])|0x8000
        #remove anything after decimal
        n>>=e
        #set truncated value
        sn.SetValue(s*n)

        return sn

    #if exponent is 160 or more then no significant digits after decimal so simply return
    if(e>=160):
        return sn

    #now left with exponents from 145 to 159
    #work out how many bits need clearing
    #SUB #A0
    e+=256-160
    #NEG
    e=256-e

    #clear whole bytes first
    i=4
    while(e>=8):
        sn.data[i]=0
        i-=1
        e-=8
    #now clear any remaining bits
    if(e>0):
        #make bit mask
        e=0xFF-((1<<e)-1)
        #clear unused bits
        sn.data[i]&=e

    return sn

def Int(sn):
    """
    Returns the integer value of the supplied SpectrumNumber.
    Basically, the number is rounded down to the nearest whole number.
    This is the same as the Spectrum floating point calculator command 0x27 at 0x36AF in the 48K Spectrum ROM.
    SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
    """
    sn=SpectrumNumber(sn)

    #if not negative, simply truncate
    if(not sn.LessThanZero()):
        sn.Truncate()
        return sn

    #round down negative numbers unless exact integer
    snTrunc=Truncate(sn)

    sn-=snTrunc
    #if is exact negative int then return
    if(sn.IsZero()):
        return snTrunc

    #otherwise reduce by 1;
    snTrunc-=1

    return snTrunc

def Sign(sn):
    """
    Returns the sign of the supplied SpectrumNumber.
    The sign is -1 for a negative value, 0 for zero, and +1 for any positive value.
    This is the same as the Spectrum floating point calculator command 0x29 at 0x3492 in the 48K Spectrum ROM.
    """
    if(IsZero(sn)):
        return SpectrumNumber((0,0,0,0,0))
    return SpectrumNumber((0,(sn.data[1]&128)!=0 and 0xFF or 0,1,0,0))


#arithmetic functions
def Subtract(sn1,sn2):
    """
    Subtracts one SpectrumNumber from another.
    This is the same as the Spectrum floating point calculator command 0x03 at 0x300F in the 48K Spectrum ROM.
    SpectrumNumberException this is raised if the result is too big or small to acurately be held by a SpectrumNumber.
    """
    return Add(sn1,Negate(sn2))

def Add(sn1,sn2):
    """
    Adds one SpectrumNumber to another.
    This is the same as the Spectrum floating point calculator command 0x0F at 0x3014 in the 48K Spectrum ROM.
    SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
    """
    
    if((sn1.data[0]|sn2.data[0])==0): #both small integers
        i=sn1.GetSmallInt()+sn2.GetSmallInt()
        if(i<=65535 and i>-65535):
            return SpectrumNumber(i)

    #convert to floating point numbers components
    nc1=SpectrumNumberComponents(sn1)
    nc2=SpectrumNumberComponents(sn2)

    #complement mantissas if numbers are negative
    if(nc1.negative):
        nc1.twos_complement_mantissa()
    if(nc2.negative):
        nc2.twos_complement_mantissa()

    #ensure nc1 is larger number (bigger exponent)
    if(nc1.exponent<nc2.exponent):#swap if not
        nc1,nc2=nc2,nc1

    #make sure mantissa's line up
    if(nc1.exponent!=nc2.exponent):
        #? is altering exponent needed. Keeps number correct
        nc2.shift_mantissa(nc1.exponent-nc2.exponent,nc2.negative and 0xFF or 0x00)
        nc2.exponent=nc1.exponent

    #variable to hold result (return value)
    ncRet=SpectrumNumberComponents()
    ncRet.exponent=nc1.exponent

    #add mantissas
    ncRet.mantissa=nc1.mantissa+nc2.mantissa
    ncRet.mantissa&=0xFFFFFFFFL

    #did adding mantissas carry over?
    carry=((nc1.mantissa+nc2.mantissa)&0x100000000L)==0x100000000L

    #do we need to shift result(two positive with carry, or 2 negative without)
    if((carry and nc1.negative==False and nc2.negative==False) or (not carry and nc1.negative and nc2.negative)):
        ncRet.shift_mantissa(1,carry and 0x01 or 0xFE)
        ncRet.exponent+=1
        if(ncRet.exponent==256):
            raise SpectrumNumberException("Number too big")

    #get sign of result
    ncRet.negative=(nc1.negative and nc2.negative) or (not carry and (nc1.negative or nc2.negative))

    #if negative calculate two'2 complement of mantissa
    if(ncRet.negative):
        if(ncRet.twos_complement_mantissa()):
            #overflow reverting back to positive(when two negative numbers added to give exact power of 2
            ncRet.mantissa=0x80000000L
            ncRet.exponent+=1
            if(ncRet.exponent==256):
                raise SpectrumNumberException("Number too big")

    #Normalise number
    ncRet.normalise(0)

    return ncRet.get_SpectrumNumber()

def Multiply(sn1,sn2):
    """
    Multiply one SpectrumNumber to another.
    This is the same as the Spectrum floating point calculator command 0x04 at 0x30CA in the 48K Spectrum ROM.
    SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
    """
    #if both simple numbers then return multiplying them
    #in spectrum need to check for overflow but SpectrumNumber(int) already puts values bigger than 65535 in FP form
    if(sn1.data[0]==0 and sn2.data[0]==0):
        return SpectrumNumber(sn1.GetSmallInt()*sn2.GetSmallInt())

    #if either number is zero, result will be zero
    if(IsZero(sn1) or IsZero(sn2)):
        return SpectrumNumber(0)

    #deal with 1 or 2 FP numbers

    #convert to floating point numbers components
    nc1=SpectrumNumberComponents(sn1)
    nc2=SpectrumNumberComponents(sn2)

    #Numbercomponent to hold result
    ncRet=SpectrumNumberComponents()

    #calculate sign: positive if same, negative if different
    ncRet.negative=(nc1.negative!=nc2.negative)

    #multiply mantissas
    ncRet.mantissa=nc1.mantissa*nc2.mantissa
    #shift bits back where they ought to be
    #remember 8 most significant bits that are beeing lost incase we're normalizinig later
    norm=int((ncRet.mantissa>>24)&0xFF)
    ncRet.mantissa>>=32

    #calculate exponent
    ncRet.exponent=nc1.exponent+nc2.exponent
    #adjust to match spectrum number
    ncRet.exponent-=128
    #check if too big
    if(ncRet.exponent>256 or (ncRet.exponent==256 and (ncRet.mantissa&80000000L)!=0)):
        raise SpectrumNumberException("Number too big")
    #check if too small
    if(ncRet.exponent==0 and (ncRet.mantissa&80000000L)!=0):
        return SpectrumNumber([1,ncRet.negative and 128 or 0,0,0,0]);
    if(ncRet.exponent<1):
        return SpectrumNumber(0)

    #normalise number
    ncRet.normalise(norm)

    return ncRet.get_SpectrumNumber()

def Divide(sn1,sn2):
    """
    Divides one SpectrumNumber by another.
    This is the same as the Spectrum floating point calculator command 0x05 at 0x31AF in the 48K Spectrum ROM.
    Returns a new SpectrumNumber holding the result.
    SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber. An exception is also thrown if you try to divide by zero.
    """
    if(sn2.IsZero()):
        raise SpectrumNumberException("Number too big")
    if(sn1.IsZero()):
        return SpectrumNumber(0)

    #convert to floating point numbers components
    nc1=SpectrumNumberComponents(sn1)
    nc2=SpectrumNumberComponents(sn2)

    #Numbercomponent to hold result
    ncRet=SpectrumNumberComponents()

    #divide mantissa
    #counter
    b=-33
    norm=0

    while(True):
        #if been round loop already possibility that bit 32 might be set
        #same as carry set after adding divisor in origional code
        #in which case, need to subtact divisor from dividend regardless

        #if dividend greater or equal to divisor then subtract divisor from dividend
        if((nc1.mantissa&0x100000000L)!=0 or nc1.mantissa>=nc2.mantissa):
            nc1.mantissa&=0xFFFFFFFFL
            nc1.mantissa-=nc2.mantissa
            #concat 1 to right end of quotient
            c=1
        else:
            #concat 0 to right end of quotient
            c=0

        b+=1
        if(b==0):
            norm=c<<6
            continue
        if(b==1):
            norm|=c<<7
            break

        #make room to concat onto end of quotient
        ncRet.mantissa<<=1
        #do the concatination
        ncRet.mantissa+=c

        #shift divisor one place
        nc1.mantissa<<=1
        nc1.mantissa&=0x1FFFFFFFFL

    #calculate sign: positive if same, negative if different
    ncRet.negative=(nc1.negative!=nc2.negative)

    #calculate exponent
    ncRet.exponent=nc1.exponent-nc2.exponent
    #adjust to match spectrum number
    ncRet.exponent+=129
    #check if too big
    if(ncRet.exponent>256 or (ncRet.exponent==256 and (ncRet.mantissa&80000000L)!=0)):
        raise SpectrumNumberException("Number too big")
    #check if too small
    if(ncRet.exponent==0 and (ncRet.mantissa&80000000L)!=0):
        return SpectrumNumber([1,ncRet.negative and 128 or 0,0,0,0])
    if(ncRet.exponent<1):
        return SpectrumNumber(0)

    #normalise number
    ncRet.normalise(norm)

    return ncRet.get_SpectrumNumber()

def E_to_FP(sn,exponent):
    """
    Multiplies a SpectrumNumber by 10 to the power of the supplied int.
    It essentially treats the SpectrumNumber as the mantissa, with the supplied int as the base 10 exponent.
    This is the same as the Spectrum floating point calculator command 0x3C at 0x2D4F in the 48K Spectrum ROM.
    SpectrumNumberException is raised if the result is too big or small to acurately be held by a SpectrumNumber.
    """
    
    #make working copy
    sn=SpectrumNumber(sn)

    #split exponent into sign and magnitude
    ePositive=(exponent>=0)
    if(not ePositive):
        exponent*=-1

    snTemp=SpectrumNumber(10)

    while(exponent>0):
        if((exponent&1)==1):
            if(ePositive):
                sn*=snTemp
            else:
                sn/=snTemp

        exponent>>=1
        if(exponent==0):
            break
        snTemp.Multiply(snTemp)

    return sn;

#comparison functions

def IsZero(sn):
    """Returns True if the supplied SpectrumNumber is zero.
    It only compares the first 4 bytes of a number to avoid small differences in binary floating point representation
    """
    return (sn.data[0]|sn.data[1]|sn.data[2]|sn.data[3])==0

def LessThanZero(sn):
    """
    Returns True if the supplied SpectrumNumber is less than zero (negative).
    This is the same as the Spectrum floating point calculator command 0x36 at 0x3506 in the 48K Spectrum ROM.
    """
    return (sn.data[1]&128)==128

def GreaterThanZero(sn):
    """
    Returns True if the supplied SpectrumNumber is greater than zero.
    This is the same as the Spectrum floating point calculator command 0x37 at 0x34F9 in the 48K Spectrum ROM.
    """
    if(IsZero(sn)):
        return False
    return (sn.data[1]&128)==0

#IO functions
def get_SpectrumNumber_from_string(s):
    """
    Converts a StringBuffer holding a SpectrumNumber (in ZX Spectrum number format) to a SpectrumNumber.
    Returns a SpectrumNumber.
    SpectrumNumberException is raised if the StringBuffer did not contain a valid spectrum format SpectrumNumber or it was too big.
    """
    #number to return
    sn=SpectrumNumber(0)
    IsNegative=False
    SkipFraction=False

    if(s==None or len(s)==0):
        raise SpectrumNumberException("Invalid Number")

    #origional doesn't deal with '-' at start of numbers but will implement to make more user friendly
    if(s[0]=='-'):
        IsNegative=True
        
        #Remove negative & check for end
        s=s[1:]
        if(s==None or len(s)==0):
            raise SpectrumNumberException("Invalid Number")

    #if starting with decimal
    if(s[0]=='.'):
        #must be followed by digit or is invalid
        s=s[1:]
        if(s==None or len(s)==0 or not s[0].isdigit()):
            raise SpectrumNumberException("Invalid Number")
    #otherwise get number up to possible decimal
    else:
        while(s[0].isdigit()):
            sn*=10
            sn+=int(s[0])
            s=s[1:]
            if(s==None or len(s)==0):
                break

        #can have number after decimal then exponent, or exponent
        if(len(s)==0 or s[0]!='.'):
            SkipFraction=True
            
        else:
            #move past decimal point
            s=s[1:]
            SkipFraction=len(s)==0 or not s[0].isdigit()

    #deal with non-exponent part of decimal
    if(SkipFraction==False):
        snFract=SpectrumNumber(1)
        #loop through digits of decimal
        while(s[0].isdigit()):
            snFract/=10
            sn+=snFract*int(s[0])
            s=s[1:]
            if(s==None or len(s)==0):
                break

    #if negative, adjust number now
    if(IsNegative):
        sn.Negate()

    #return if end of number
    if(len(s)==0 or (s[0]!='e' and s[0]!='E')):
        return sn
        
    #now deal with 'E' format

    #remove 'E'
    s=s[1:]
    #check sign of exponent
    if(len(s)==0):
        raise SpectrumNumberException("Invalid Number")
    
    #process sign of exponent
    exponentSign=1
    if(s[0]=='-' or s[0]=='+'):
        exponentSign=s[0]=='-' and -1 or 1
        s=s[1:]
        if(len(s)==0):
            raise SpectrumNumberException("Invalid Number")

    if(not s[0].isdigit()):
        raise SpectrumNumberException("Invalid Number")

    exponent=0
    while(s[0].isdigit()):
        exponent*=10
        exponent+=int(s[0])
        s=s[1:]
        if(s==None or len(s)==0):
            break

    if(exponent>127):
        raise SpectrumNumberException("Number too big")

    return sn.E_to_FP(exponent*exponentSign)

    #efectively the print a floating point number routine at #2DE3
def toString(sn):
    """
    Returns a String of the supplied SpectrumNumber.
    This is the same as the Spectrum display of a number as done by the routine at 0x2DE3 in the 48K Spectrum ROM.
    SpectrumNumberException is raised if during processing the number a component is too big or small to display. In theory It should not happen, but I've not been able to work it out one way or another so I'm erring on the side of caution.
    """

    #nested function
    def digit_buffer_to_string(digitBuffer,iDigitsPrintable,iDigitsBeforeDecimal):
        strRet=''  
        #point to start of digit buffer
        i=0
        #deal with digits before decimal
        while(True):
            while(iDigitsBeforeDecimal>0):
                if(iDigitsPrintable==0):
                    strRet+='0'
                else:
                    strRet+=str(digitBuffer[i])
                    i+=1
                    iDigitsPrintable-=1
    
                iDigitsBeforeDecimal-=1
    
            if(iDigitsPrintable==0):
                return strRet
                
            strRet+='.'
            iDigitsBeforeDecimal*=-1
            while(iDigitsBeforeDecimal>0):
                strRet+='0'
                iDigitsBeforeDecimal-=1
    
            iDigitsBeforeDecimal=iDigitsPrintable
    
    #end nested function

    #deal with simple case
    if(sn.IsZero()):
        return "0"

    #make local copy we can change if needed
    sn=SpectrumNumber(sn)

    strRet=''

    #is it a negative number
    if((sn.data[1]&128)==128):
        #if so print '-' and abs number
        strRet="-"
        sn.Abs()

    #split the number into int and fraction parts
    snInt=Int(sn)
    snFrac=Subtract(sn,snInt)

    #emulate how spectrum does this for greater acuracy
    iDigitsPrintable=0
    iDigitsBeforeDecimal=0
    digitBuffer=[0,0,0,0,0,0,0,0,0,0]
    rounding=-1

    #is it large number (exponent>=28)
    while(snInt.data[0]-128>=28):
        snTemp=SpectrumNumber(snInt.data[0]-128)
        #multiply by log2
        snTemp*=SpectrumNumber([0x7F,0x1A,0x20,0x9A,0x85])
        snTemp.Int()
        i=snTemp.GetSmallInt()-7
        iDigitsBeforeDecimal+=i
        #multiply down
        sn=E_to_FP(sn,-i)
        #recalculate integer and floating point parts
        snInt=Int(sn)
        snFrac=Subtract(sn,snInt)

    #deal with integer component>0
    if(not snInt.IsZero()):
        #deal with medium numbers (large numbers sorted in previous loop
        if(snInt.data[0]!=0):
            #is medium number (exponent 0-27, but not small int)
            BitsToPrint=0L
            for i in range(1,5):
                BitsToPrint<<=8
                BitsToPrint|=snInt.data[i]

            #add in most significant bit
            BitsToPrint|=0x80000000L
            NumberOfBitsToPrint=snInt.data[0]-128

        #deal with small ints
        else:
            BitsToPrint=snInt.GetSmallInt()
            BitsToPrint<<=(snInt.data[3]==0) and 24 or 16
            NumberOfBitsToPrint=(snInt.data[3]==0) and 8 or 16

        #PF_BITS to print bits

        #generate decimal digits in array digitBuffer
        while(True):
            c=(BitsToPrint>>31)&1
            BitsToPrint<<=1
            BitsToPrint&=0xFFFFFFFFL

            #binary coded decimal emulated
            for i in range(9,0,-1):
                digitBuffer[i]+=digitBuffer[i]+c
                c=digitBuffer[i]/10
                digitBuffer[i]%=10

            NumberOfBitsToPrint-=1

            if(not NumberOfBitsToPrint>0):
                break

        #now move digits to begining of array and calculate how many digits there are
        bFoundNonZero=False
        c=0
        for i in range(1,10):
            if(digitBuffer[i]>0 or bFoundNonZero):
                digitBuffer[c]=digitBuffer[i]
                c+=1
                bFoundNonZero=True
                iDigitsPrintable+=1
                iDigitsBeforeDecimal+=1


        #check if have enough digits or needs rounding
        if(iDigitsPrintable>8):
            iDigitsPrintable-=1
            rounding=(digitBuffer[8]>4) and 1 or 0

        #default not to go to rounding

    #PF-SMALL
    #integer part is zero so dealing with pure fraction
    else:
        snTemp=SpectrumNumber(snFrac.data[0]-126)
        #multiply by log2
        snTemp*=SpectrumNumber([0x7F,0x1A,0x20,0x9A,0x85])
        snTemp.Int()
        snTemp.Abs()
        i=snTemp.GetSmallInt()
        iDigitsBeforeDecimal-=i
        snFrac=E_to_FP(snFrac,i)

        digitBuffer[0]=Int(snFrac).GetSmallInt()
        snFrac.Subtract(Int(snFrac))

        if(digitBuffer[0]==0):
            i=0
        else:
            i=1
            
        iDigitsPrintable=i
        iDigitsBeforeDecimal+=i


    #PF-FRACTN
    #if not rounding, check if fraction part to add first
    if(rounding==-1):
        nc=SpectrumNumberComponents(snFrac)
        nc.shift_mantissa(128-nc.exponent,0)

        #print extra bits of fraction
        while(iDigitsPrintable<8):
            nc.mantissa*=10
            digitBuffer[iDigitsPrintable]=int(nc.mantissa>>32)
            nc.mantissa&=0xFFFFFFFFL
            iDigitsPrintable+=1

        #note if need to round
        rounding=((nc.mantissa&0x80000000L)!=0) and 1 or 0

    #do rounding of number
    #also ensures no unneeded zeros after decimal point
    i=iDigitsPrintable
    while(True):
        i-=1
        digitBuffer[i]+=rounding
        if(digitBuffer[i]!=0 and digitBuffer[i]!=10):
            break
            
        rounding=digitBuffer[i]/10
        iDigitsPrintable-=1
        if(iDigitsPrintable!=0):
            continue
            
        #digit overflow
        digitBuffer[0]=1
        #indicate one digit;
        iDigitsPrintable+=1
        iDigitsBeforeDecimal+=1
        break

    #now do printing

    #if digits before decimal >=9 or <-4 then floating point format
    if(iDigitsBeforeDecimal>8 or iDigitsBeforeDecimal<-4):
        #print out mantissa as x.xxxxx
        strRet+=digit_buffer_to_string(digitBuffer,iDigitsPrintable,1)
        strRet+='E'
        iDigitsBeforeDecimal-=1
        if(iDigitsBeforeDecimal>=0):
            strRet+='+'
        strRet+=str(iDigitsBeforeDecimal)

    #otherwise normal print format
    else:
        #ensure that if number is .X* where x=1-9 that 0 is printed first
        if(iDigitsBeforeDecimal==0):
            strRet+='0'
        #output number
        strRet+=digit_buffer_to_string(digitBuffer,iDigitsPrintable,iDigitsBeforeDecimal);

    return strRet

class SpectrumNumberComponents:
    """
    Class to hold expanded components of a SpectrumNumber for processing reasons
    """

    def __init__(self,data=None):
        #int has enough bits to hold the 31 bits+1 of mantissa
        #however in system without unsigned ints or carry notification, easier to use a long
        self.mantissa=long(0)
        self.negative=False
        self.exponent=0

        if(data==None):
            return

        if(isinstance(data,SpectrumNumberComponents)):
            self.mantissa=data.mantissa
            self.negative=data.negative
            self.exponent=data.exponent
            return

        if(isinstance(data,SpectrumNumber)):
            #convert to floating point
            #with 32 bit mantissa can hold 16 bit ints without loss of precission
            data=data.IntToFP()
    
            self.exponent=data.data[0]
            self.negative=(data.data[1]&128)==128
            for i in range(1,5):
                self.mantissa<<=8
                self.mantissa|=data.data[i]
            self.mantissa|=0x80000000L
            return
            
        raise SpectrumNumberException("Invalid SpectrumNumberComponents constructor argument")

    #Right shift mantissa by specified number of bits
    def shift_mantissa(self,shift,LeftBitBuffer):
        if(shift==0):
            return

        if(shift>32): #only 32 bits in mantissa so would shift to nothing
            self.mantissa=0
            self.negative=False
            return

    #shift mantissa required number of places
        c=0
        while(shift>0):
            #remember least significant byte
            c=int(self.mantissa&1)
            self.mantissa=(self.mantissa>>1)|long((LeftBitBuffer&1)<<31)
            shift-=1
            LeftBitBuffer>>=1;
            LeftBitBuffer|=((LeftBitBuffer<<1)&0x80);

        if(c==1):
            #add back in carry if needed: round up
            self.mantissa+=1;
            #ensure limited to 32 bits
            self.mantissa&=0xFFFFFFFF;
            if(self.mantissa==0):
                self.negative=False;


    #returns true if overflows
    def twos_complement_mantissa(self):
        self.mantissa=~self.mantissa
        self.mantissa+=1;
        #ensure limited to 32 bits
        self.mantissa&=0xFFFFFFFF;
        return self.mantissa==0;

    #ensures mantissa is using most significant bit
    # ie is 1.32E4 rather than 13.2E5 or 0.132E3
    #extra used for extra precission in multiplication/divission
    def normalise(self,extra):
        #normalise by up to 32 bits
        count=32;

        while((self.mantissa&0x80000000)==0):
            self.mantissa<<=1
            self.mantissa=self.mantissa|((extra>>7)&1)
            extra=extra<<1
            extra=extra&0xFF

            self.exponent-=1

            #check to see if have 2^-129, with bit in which case round up or without in which case round to 0
            if(self.exponent==0):
                self.mantissa&=0x80000000
                self.exponent=int(self.mantissa>>31)
                return

            #check to see if moved 32 bits: if have won't ever find set bit, so stop
            count-=1
            if(count==0):
                self.mantissa=0
                self.negative=False
                self.exponent=0
                return

        #extra info: do we need to round up?
        if((extra&0x80)==0x80):
            self.mantissa+=1
            if(self.mantissa==0x100000000L):
                self.mantissa>>=1
                self.exponent+=1
                if(self.exponent==256):
                    raise SpectrumNumberException("Number too big")

    #convert back to a spectrum number
    def get_SpectrumNumber(self):
        return SpectrumNumber([self.exponent,
                               int(((self.mantissa>>24)&0x7F)|(self.negative and 0x80 or 0)),
                               int((self.mantissa>>16)&0xFF),
                               int((self.mantissa>>8)&0xFF),
                               int(self.mantissa&0xFF)])

    def __str__(self):
        f=float(self.mantissa)
        f/=256
        f/=256
        f/=256
        f/=128
        f*=2**(self.exponent-129)
        if(self.negative):
            f*=-1
        return '%f (%08Xe%s%s)' % (f,self.mantissa,self.negative and '-' or '+',str(self.exponent))

if __name__=="__main__":
    pass
