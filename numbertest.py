"""
Unit Test for SpectrumNumber Module
"""

import spectrumnumber
import unittest

"""
Test SpectrumNumber
"""

class TestSpectrumNumberComponentsCreate(unittest.TestCase):
    
    def testSpectrumNumberComponentsCreate(self):
        #check creation with default values"""
        result=spectrumnumber.SpectrumNumberComponents()
        self.assertEqual(0,result.mantissa)
        self.assertEqual(False,result.negative)
        self.assertEqual(0,result.exponent)

        #Check copy creation
        snc=spectrumnumber.SpectrumNumberComponents()
        snc.mantissa=20L
        snc.negative=True
        snc.exponent=4000
        testsnc=spectrumnumber.SpectrumNumberComponents(snc)
        self.assertEqual(20L,testsnc.mantissa)
        self.assertEqual(True,testsnc.negative)
        self.assertEqual(4000,testsnc.exponent)

#todo
        #check SpectrumNumber creation
        
        #ensure falls over with bad input
        self.assertRaises(spectrumnumber.SpectrumNumberException,spectrumnumber.SpectrumNumberComponents,1)
        self.assertRaises(spectrumnumber.SpectrumNumberException,spectrumnumber.SpectrumNumberComponents,[1,2,3])
        self.assertRaises(spectrumnumber.SpectrumNumberException,spectrumnumber.SpectrumNumberComponents,"")


class TestSpectrumNumberComponentsMethods(unittest.TestCase):
#todo
    def testShiftMantissa(self):
        pass

#todo
    def testTwosComplementMantissa(self):
        pass

#todo
    def testNormalise(self):
        pass

#todo
    def testGetSpectrumNumber(self):
        pass

    def testtoString(self):
        #test debug function
        snc=spectrumnumber.SpectrumNumberComponents()
        
        snc.mantissa=20L
        snc.negative=True
        snc.exponent=4000
        self.assertEqual('00000014^-4000',snc._toString())

        snc.mantissa=-100L
        snc.negative=False
        snc.exponent=1
        self.assertEqual('-0000064^+1',snc._toString())

    def testStr(self):
        snc=spectrumnumber.SpectrumNumberComponents()

        snc.mantissa=0x80000000
        snc.negative=False
        snc.exponent=129
        self.assertEqual('1.000000 (80000000e+129)',str(snc))

        snc.mantissa=0x80000000
        snc.negative=False
        snc.exponent=127
        self.assertEqual('0.250000 (80000000e+127)',str(snc))
"""
Test SpectrumNumber
"""

class TestSpectrumNumberCreate(unittest.TestCase):
    
    def testSpectrumNumberCreate(self):
        #check creation with default values
        result=spectrumnumber.SpectrumNumber()
        self.assertEqual([0,0,0,0,0],result.data)

        #check creation with list
        #make sure falls over with invalid arguments
        self.assertRaises(spectrumnumber.SpectrumNumberException,spectrumnumber.SpectrumNumber,[])
        self.assertRaises(spectrumnumber.SpectrumNumberException,spectrumnumber.SpectrumNumber,[0,1,2,3,4,5])
        self.assertRaises(spectrumnumber.SpectrumNumberException,spectrumnumber.SpectrumNumber,[0,1,"X"])
        self.assertRaises(spectrumnumber.SpectrumNumberException,spectrumnumber.SpectrumNumber,[-1])
        self.assertRaises(spectrumnumber.SpectrumNumberException,spectrumnumber.SpectrumNumber,[256])
        #now check it creates correctly
        result=spectrumnumber.SpectrumNumber([0,0,1,0,0])
        self.assertEqual([0,0,1,0,0],result.data)
        #check different valid data types, and length of argument
        result=spectrumnumber.SpectrumNumber([float(0),0,long(2)])
        self.assertEqual([0,0,2,0,0],result.data)
        #check byte handling
        self.assertRaises(spectrumnumber.SpectrumNumberException,spectrumnumber.SpectrumNumber,[128],True)
        self.assertRaises(spectrumnumber.SpectrumNumberException,spectrumnumber.SpectrumNumber,[-128],False)

        #check creation with integer
        #check small int creation
        result=spectrumnumber.SpectrumNumber(513)
        self.assertEqual([0,0,1,2,0],result.data)
        result=spectrumnumber.SpectrumNumber(-513)
        self.assertEqual([0,0xFF,0xFF,0xFD,0],result.data)
        result=spectrumnumber.SpectrumNumber(65536)
        self.assertEqual([145,0,0,0,0],result.data)
        result=spectrumnumber.SpectrumNumber(-65536)
        self.assertEqual([145,0x80,0,0,0],result.data)

        #check creation with float
        result=spectrumnumber.SpectrumNumber(2.0)
        self.assertEqual([0,0,2,0,0],result.data)
        result=spectrumnumber.SpectrumNumber(0.5)
        self.assertEqual([0x7F,0x7F,0xFF,0xFF,0xFF],result.data)
        result=spectrumnumber.SpectrumNumber(12.098)
        self.assertEqual(12.098,result)
        return

        #ensure falls over with wrong argument
        self.assertRaises(spectrumnumber.SpectrumNumberException,spectrumnumber.SpectrumNumber,spectrumnumber.SpectrumNumberException)

    def testSpectrumNumberIntToFP(self):
        sn=spectrumnumber.SpectrumNumber(2)
        sn.IntToFP()
        self.assertEqual([0x82,0x00,0x00,0x00,0x00],sn.data)

class TestSpectrumNumberComparisons(unittest.TestCase):
    def testSpectrumNumberEquals(self):
        sn=spectrumnumber.SpectrumNumber(200)
        self.assertEqual(sn,200)
        sn=spectrumnumber.SpectrumNumber(0.25)
        self.assertEqual(sn,0.25)
        sn2=spectrumnumber.SpectrumNumber([0x7F])
        self.assertEqual(sn,sn2)

    def testSpectrumNumberIsZero(self):
        sn=spectrumnumber.SpectrumNumber(0)
        self.assertEqual(sn.IsZero(),True)
        sn=spectrumnumber.SpectrumNumber(1)
        self.assertEqual(sn.IsZero(),False)

    def testSpectrumNumber__nonzero__(self):
        sn=spectrumnumber.SpectrumNumber(0)
        self.assertEqual(sn.__nonzero__(),False)
        sn=spectrumnumber.SpectrumNumber(1)
        self.assertEqual(sn.__nonzero__(),True)

    def testSpectrumNumberLessThanZero(self):
        sn=spectrumnumber.SpectrumNumber(0)
        self.assertEqual(sn.LessThanZero(),False)
        sn=spectrumnumber.SpectrumNumber(1)
        self.assertEqual(sn.LessThanZero(),False)
        sn=spectrumnumber.SpectrumNumber(-1)
        self.assertEqual(sn.LessThanZero(),True)

    def testSpectrumNumberGreaterThanZero(self):
        sn=spectrumnumber.SpectrumNumber(0)
        self.assertEqual(sn.GreaterThanZero(),False)
        sn=spectrumnumber.SpectrumNumber(1)
        self.assertEqual(sn.GreaterThanZero(),True)
        sn=spectrumnumber.SpectrumNumber(-1)
        self.assertEqual(sn.GreaterThanZero(),False)


class TestSpectrumNumberUnaryArithmetic(unittest.TestCase):
    def testSpectrumNumberAbs(self):
        sn=spectrumnumber.SpectrumNumber(200)
        sn=abs(sn)
        self.assertEqual(sn,200)
        sn=spectrumnumber.SpectrumNumber(-200)
        sn=abs(sn)
        self.assertEqual(sn,200)
        sn=spectrumnumber.SpectrumNumber(-0.5)
        sn=abs(sn)
        self.assertEqual(sn,0.5)

    def testSpectrumNumberNegate(self):
        sn=spectrumnumber.SpectrumNumber(200)
        sn=-sn
        self.assertEqual(sn,-200)
        sn=spectrumnumber.SpectrumNumber(-2.7)
        sn=-sn
        self.assertEqual(sn,2.7)
        
        sn=spectrumnumber.SpectrumNumber(200)
        sn.Negate()
        self.assertEqual(sn,-200)
        sn=spectrumnumber.SpectrumNumber(-2.7)
        sn.Negate()
        self.assertEqual(sn,2.7)


class TestSpectrumNumberMethods(unittest.TestCase):
    def testSpectrumNumberTruncate(self):
        sn=spectrumnumber.SpectrumNumber(12.098)
        sn.Truncate()
        self.assertEqual(sn,12)
        sn=spectrumnumber.SpectrumNumber(-12.098)
        sn.Truncate()
        self.assertEqual(sn,-12)

    def testSpectrumNumberInt(self):
        sn=spectrumnumber.SpectrumNumber(12.098)
        sn.Int()
        self.assertEqual(sn,12)
        sn=spectrumnumber.SpectrumNumber(-12.098)
        sn=spectrumnumber.Int(sn)
        self.assertEqual(sn,-13)

class TestSpectrumNumberArithmeticMethods(unittest.TestCase):
    def testSpectrumNumberSubtract(self):
        sn=spectrumnumber.SpectrumNumber(300)
        sn-=20
        self.assertEqual(sn,280)
        sn=spectrumnumber.SpectrumNumber(300)
        sn-=2.0
        self.assertEqual(sn,298)
        sn=spectrumnumber.SpectrumNumber(-1.5)
        sn-=-2.0
        self.assertEqual(sn,0.5)

if __name__ == "__main__":
    unittest.main()
