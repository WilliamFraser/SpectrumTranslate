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
        # check creation with default values"""
        result = spectrumnumber.SpectrumNumberComponents()
        self.assertEqual(0, result.mantissa)
        self.assertEqual(False, result.negative)
        self.assertEqual(0, result.exponent)

        # Check copy creation
        snc = spectrumnumber.SpectrumNumberComponents()
        snc.mantissa = [0, 20]
        snc.negative = True
        snc.exponent = 4000
        testsnc = spectrumnumber.SpectrumNumberComponents(snc)
        self.assertEqual([0, 20], testsnc.mantissa)
        self.assertEqual(True, testsnc.negative)
        self.assertEqual(4000, testsnc.exponent)

# todo
        # check SpectrumNumber creation

        # ensure falls over with bad input
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumberComponents, 1)
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumberComponents, [1, 2, 3])
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumberComponents, "")


class TestSpectrumNumberComponentsMethods(unittest.TestCase):
    # todo
    def testShiftMantissa(self):
        pass

    # todo
    def testTwosComplementMantissa(self):
        pass

    # todo
    def testNormalise(self):
        pass

    # todo
    def testGetSpectrumNumber(self):
        pass

    def testStr(self):
        snc = spectrumnumber.SpectrumNumberComponents()

        snc.mantissa = 0x80000000
        snc.negative = False
        snc.exponent = 129
        self.assertEqual('1.0 (80000000e+129)', str(snc))

        snc.mantissa = 0x80000000
        snc.negative = False
        snc.exponent = 127
        self.assertEqual('0.25 (80000000e+127)', str(snc))
"""
Test SpectrumNumber
"""


class TestSpectrumNumberCreate(unittest.TestCase):

    def testSpectrumNumberCreate(self):
        # check creation with default values
        result = spectrumnumber.SpectrumNumber()
        self.assertEqual([0, 0, 0, 0, 0], result.data)

        # check creation with list
        # make sure falls over with invalid arguments
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumber, [])
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumber, [0, 1, 2, 3, 4, 5])
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumber, [0, 1, "X"])
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumber, [-1])
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumber, [256])
        # now check it creates correctly
        result = spectrumnumber.SpectrumNumber([0, 0, 1, 0, 0])
        self.assertEqual([0, 0, 1, 0, 0], result.data)
        # check different valid data types, and length of argument
        result = spectrumnumber.SpectrumNumber([float(0), 0, int(2)])
        self.assertEqual([0, 0, 2, 0, 0], result.data)
        # check byte handling
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumber, [128], True)
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumber, [-128], False)

        # check creation with integer
        # check small int creation
        result = spectrumnumber.SpectrumNumber(513)
        self.assertEqual([0, 0, 1, 2, 0], result.data)
        result = spectrumnumber.SpectrumNumber(-513)
        self.assertEqual([0, 0xFF, 0xFF, 0xFD, 0], result.data)
        result = spectrumnumber.SpectrumNumber(65536)
        self.assertEqual([145, 0, 0, 0, 0], result.data)
        result = spectrumnumber.SpectrumNumber(-65536)
        self.assertEqual([145, 0x80, 0, 0, 0], result.data)

        # check creation with float
        result = spectrumnumber.SpectrumNumber(2.0)
        self.assertEqual([0, 0, 2, 0, 0], result.data)
        result = spectrumnumber.SpectrumNumber(0.5)
        self.assertEqual([0x7F, 0x7F, 0xFF, 0xFF, 0xFF], result.data)
        result = spectrumnumber.SpectrumNumber(12.098)
        self.assertEqual(12.098, result)
        return

        # ensure falls over with wrong argument
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumber,
                          spectrumnumber.SpectrumNumberError)

    def testSpectrumNumberIntToFP(self):
        sn = spectrumnumber.SpectrumNumber(2)
        sn.IntToFP()
        self.assertEqual([0x82, 0x00, 0x00, 0x00, 0x00], sn.data)


class TestSpectrumNumberComparisons(unittest.TestCase):
    def testSpectrumNumberEquals(self):
        sn = spectrumnumber.SpectrumNumber(200)
        self.assertEqual(sn, 200)
        sn = spectrumnumber.SpectrumNumber(0.25)
        self.assertEqual(sn, 0.25)
        sn2 = spectrumnumber.SpectrumNumber([0x7F])
        self.assertEqual(sn, sn2)

    def testSpectrumNumberIsZero(self):
        sn = spectrumnumber.SpectrumNumber(0)
        self.assertEqual(sn.IsZero(), True)
        sn = spectrumnumber.SpectrumNumber(1)
        self.assertEqual(sn.IsZero(), False)

    def testSpectrumNumber__nonzero__(self):
        sn = spectrumnumber.SpectrumNumber(0)
        self.assertEqual(sn.__nonzero__(), False)
        sn = spectrumnumber.SpectrumNumber(1)
        self.assertEqual(sn.__nonzero__(), True)

    def testSpectrumNumberLessThanZero(self):
        sn = spectrumnumber.SpectrumNumber(0)
        self.assertEqual(sn.LessThanZero(), False)
        sn = spectrumnumber.SpectrumNumber(1)
        self.assertEqual(sn.LessThanZero(), False)
        sn = spectrumnumber.SpectrumNumber(-1)
        self.assertEqual(sn.LessThanZero(), True)

    def testSpectrumNumberGreaterThanZero(self):
        sn = spectrumnumber.SpectrumNumber(0)
        self.assertEqual(sn.GreaterThanZero(), False)
        sn = spectrumnumber.SpectrumNumber(1)
        self.assertEqual(sn.GreaterThanZero(), True)
        sn = spectrumnumber.SpectrumNumber(-1)
        self.assertEqual(sn.GreaterThanZero(), False)


class TestSpectrumNumberUnaryArithmetic(unittest.TestCase):
    def testSpectrumNumberAbs(self):
        sn = spectrumnumber.SpectrumNumber(200)
        sn = abs(sn)
        self.assertEqual(sn, 200)
        sn = spectrumnumber.SpectrumNumber(-200)
        sn = abs(sn)
        self.assertEqual(sn, 200)
        sn = spectrumnumber.SpectrumNumber(-0.5)
        sn = abs(sn)
        self.assertEqual(sn, 0.5)

    def testSpectrumNumberNegate(self):
        sn = spectrumnumber.SpectrumNumber(200)
        sn = -sn
        self.assertEqual(sn, -200)
        sn = spectrumnumber.SpectrumNumber(-2.7)
        sn = -sn
        self.assertEqual(sn, 2.7)

        sn = spectrumnumber.SpectrumNumber(200)
        sn.Negate()
        self.assertEqual(sn, -200)
        sn = spectrumnumber.SpectrumNumber(-2.7)
        sn.Negate()
        self.assertEqual(sn, 2.7)


class TestSpectrumNumberMethods(unittest.TestCase):
    def testSpectrumNumberTruncate(self):
        sn = spectrumnumber.SpectrumNumber(12.098)
        sn.Truncate()
        self.assertEqual(sn, 12)
        sn = spectrumnumber.SpectrumNumber(-12.098)
        sn.Truncate()
        self.assertEqual(sn, -12)

    def testSpectrumNumberInt(self):
        sn = spectrumnumber.SpectrumNumber(12.098)
        sn.Int()
        self.assertEqual(sn, 12)
        sn = spectrumnumber.SpectrumNumber(-12.098)
        sn = spectrumnumber.Int(sn)
        self.assertEqual(sn, -13)


class TestSpectrumNumberArithmeticMethods(unittest.TestCase):
    def testSpectrumNumberSubtract(self):
        sn = spectrumnumber.SpectrumNumber(300)
        sn -= 20
        self.assertEqual(sn, 280)
        sn = spectrumnumber.SpectrumNumber(300)
        sn -= 2.0
        self.assertEqual(sn, 298)
        sn = spectrumnumber.SpectrumNumber(-1.5)
        sn -= -2.0
        self.assertEqual(sn, 0.5)

if __name__ == "__main__":
    unittest.main()
