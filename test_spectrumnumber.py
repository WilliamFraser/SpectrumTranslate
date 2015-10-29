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
# Date: 14th January 2015

"""
Unit Test for SpectrumNumber Module
"""

import spectrumnumber
import unittest
import sys
import subprocess
import re

# 2to3 will complain about these lines but is 2 & 3 compatible
if(sys.hexversion > 0x03000000):
    _longint = int
else:
    # 2to3 will complain but won't cause problems in real life
    _longint = long


"""
Test SpectrumNumber
"""


class TestSpectrumNumberComponentsCreate(unittest.TestCase):

    def testSpectrumNumberComponentsCreate(self):
        # check creation with default values"""
        result = spectrumnumber.SpectrumNumberComponents()
        self.assertEqual(0, result.mantissa)
        self.assertFalse(result.negative)
        self.assertEqual(0, result.exponent)

        # Check copy creation
        snc = spectrumnumber.SpectrumNumberComponents()
        snc.mantissa = 20
        snc.negative = True
        snc.exponent = 4000
        testsnc = spectrumnumber.SpectrumNumberComponents(snc)
        self.assertEqual(20, testsnc.mantissa)
        self.assertTrue(testsnc.negative)
        self.assertEqual(4000, testsnc.exponent)

        # Check spectrumnumber creation
        snc = spectrumnumber.SpectrumNumberComponents(
            spectrumnumber.SpectrumNumber(1))
        self.assertEqual(_longint(0x80000000), snc.mantissa)
        self.assertFalse(snc.negative)
        self.assertEqual(129, snc.exponent)

        snc = spectrumnumber.SpectrumNumberComponents(
            spectrumnumber.SpectrumNumber(-0.25))
        self.assertEqual(_longint(0xFFFFFFFF), snc.mantissa)
        self.assertTrue(snc.negative)
        self.assertEqual(126, snc.exponent)

        # ensure falls over with bad input
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumberComponents, 1)
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumberComponents, [1, 2, 3])
        self.assertRaises(spectrumnumber.SpectrumNumberError,
                          spectrumnumber.SpectrumNumberComponents, "")


class TestSpectrumNumberComponentsMethods(unittest.TestCase):
    def testShiftMantissa(self):
        snc = spectrumnumber.SpectrumNumberComponents()
        snc.mantissa = _longint(0xFFFFFFFF)
        snc.negative = False
        snc.exponent = 0

        snc.shift_mantissa(33, 0)
        self.assertEqual(_longint(0), snc.mantissa)
        self.assertFalse(snc.negative)
        self.assertEqual(0, snc.exponent)

        snc.mantissa = _longint(0xFFFFFFFF)
        snc.shift_mantissa(2, 1)
        self.assertEqual(_longint(0x80000000), snc.mantissa)

    def testTwosComplementMantissa(self):
        snc = spectrumnumber.SpectrumNumberComponents()
        snc.mantissa = _longint(0xFFFFFFFF)
        snc.twos_complement_mantissa()
        self.assertEqual(_longint(1), snc.mantissa)
        snc.mantissa = _longint(2)
        snc.twos_complement_mantissa()
        self.assertEqual(_longint(0xFFFFFFFE), snc.mantissa)

    def testNormalise(self):
        snc = spectrumnumber.SpectrumNumberComponents()
        snc.mantissa = _longint(0xFF)
        snc.negative = False
        snc.exponent = 128

        snc.normalise(0xE)
        self.assertEqual(_longint(0xFF0E0000), snc.mantissa)
        self.assertEqual(104, snc.exponent)

        snc.mantissa = _longint(0)
        snc.normalise(0)
        self.assertEqual(_longint(0), snc.mantissa)
        self.assertEqual(0, snc.exponent)

        snc.mantissa = _longint(0xFF)
        snc.exponent = 2
        snc.normalise(0)
        self.assertEqual(_longint(0), snc.mantissa)
        self.assertEqual(0, snc.exponent)
        snc.mantissa = _longint(0x40000000)
        snc.exponent = 1
        snc.normalise(1)
        self.assertEqual(_longint(0x80000000), snc.mantissa)
        self.assertEqual(1, snc.exponent)

        snc.mantissa = _longint(0x7FFFFFFF)
        snc.exponent = 128
        snc.normalise(0xFF)
        self.assertEqual(_longint(0x80000000), snc.mantissa)
        self.assertEqual(128, snc.exponent)
        snc.mantissa = _longint(0x7FFFFFFF)
        snc.exponent = 128
        snc.normalise(0)
        self.assertEqual(_longint(0xFFFFFFFE), snc.mantissa)
        self.assertEqual(127, snc.exponent)
        snc.mantissa = _longint(0xFFFFFFFF)
        snc.exponent = 255
        self.assertRaises(spectrumnumber.SpectrumNumberError, snc.normalise,
                          0xFF)

    def testGetSpectrumNumber(self):
        snc = spectrumnumber.SpectrumNumberComponents()
        snc.mantissa = _longint(0x80000000)
        snc.negative = False
        snc.exponent = 128
        self.assertEqual("0.5", str(snc.get_SpectrumNumber()))
        snc.negative = True
        self.assertEqual("-0.5", str(snc.get_SpectrumNumber()))
        snc.mantissa = _longint(0xC0000000)
        self.assertEqual("-0.75", str(snc.get_SpectrumNumber()))
        snc.exponent = 127
        self.assertEqual("-0.375", str(snc.get_SpectrumNumber()))

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
        self.assertTrue(sn.IsZero())
        sn = spectrumnumber.SpectrumNumber(1)
        self.assertFalse(sn.IsZero())

    def testSpectrumNumber__nonzero__(self):
        sn = spectrumnumber.SpectrumNumber(0)
        self.assertFalse(sn.__nonzero__())
        sn = spectrumnumber.SpectrumNumber(1)
        self.assertTrue(sn.__nonzero__())

    def testSpectrumNumberLessThanZero(self):
        sn = spectrumnumber.SpectrumNumber(0)
        self.assertFalse(sn.LessThanZero())
        sn = spectrumnumber.SpectrumNumber(1)
        self.assertFalse(sn.LessThanZero())
        sn = spectrumnumber.SpectrumNumber(-1)
        self.assertTrue(sn.LessThanZero())

    def testSpectrumNumberGreaterThanZero(self):
        sn = spectrumnumber.SpectrumNumber(0)
        self.assertFalse(sn.GreaterThanZero())
        sn = spectrumnumber.SpectrumNumber(1)
        self.assertTrue(sn.GreaterThanZero())
        sn = spectrumnumber.SpectrumNumber(-1)
        self.assertFalse(sn.GreaterThanZero())


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


class Testformating(unittest.TestCase):
    def runpep8(self, py_file, errignore, stdoutignore):
        p = subprocess.Popen(["python",
                              "/usr/local/lib/python2.6/dist-packages/pep8.py",
                              "--repeat", py_file],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()

        output = output.splitlines()
        if(len(output) > 0 and isinstance(output[0], bytes)):
            output = [x.decode("utf-8") for x in output]
        if(stdoutignore):
            output = [x for x in output if x not in stdoutignore]

        error = error.splitlines()
        if(len(error) > 0 and isinstance(error[0], bytes)):
            error = [x.decode("utf-8") for x in error]
        if(errignore):
            error = [x for x in error if x not in errignore]

        return "\n".join(output), "\n".join(error)

    def test_pep8(self):
        output, error = self.runpep8("spectrumnumber.py", [], [])
        self.assertEqual(output, "", "spectrumnumber.py pep8 formatting \
errors:\n" + output)
        self.assertEqual(error, "", "spectrumnumber.py pep8 format check had \
errors:\n" + error)

        output, error = self.runpep8("test_spectrumnumber.py", [], [])
        self.assertEqual(output, "", "test_spectrumnumber.py pep8 formatting \
errors:\n" + output)
        self.assertEqual(error, "", "test_spectrumnumber.py pep8 format check \
had errors:\n" + error)


class Test2_3compatibility(unittest.TestCase):
    def run2to3(self, py_file, errignore, stdoutignore):
        p = subprocess.Popen(["/usr/bin/2to3", py_file],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()

        # remove refactoring info
        output = output.splitlines()
        if(len(output) > 0 and isinstance(output[0], bytes)):
            output = [x.decode("utf-8") for x in output]
        refactorignore = ["--- " + py_file + " (original)",
                          "+++ " + py_file + " (refactored)"]
        output = "\n".join([x for x in output if x not in refactorignore])
        # split into diffs
        chunks = re.compile(
            "^(@@\s[\-\+0-9]*,[0-9]*\s[\+\-0-9]+,[0-9]+\s@@$\n)",
            re.MULTILINE).split(output)
        chunks = [x for x in chunks if len(x) > 0]
        # prepare matcher if is problem commented to ignore
        commentmatcher = re.compile("^([^\-\+].*?\n)*(\s*# 2to3 will complain \
but.*?\n)([\-\+].*?\n)*([^\-\+].*?\n?)*$")
        # filter out stuff want to ignore
        output = []
        for x in range(0, len(chunks), 2):
            if(commentmatcher.match(chunks[x + 1])):
                continue
            if(chunks[x + 1] not in stdoutignore):
                output += [chunks[x], chunks[x + 1]]

        error = error.splitlines()
        if(len(error) > 0 and isinstance(error[0], bytes)):
            error = [x.decode("utf-8") for x in error]
        if(not errignore):
            errignore = []
        errignore += [
            "AssertionError: {0} 2to3 check had errors:".format(py_file),
            "RefactoringTool: Skipping implicit fixer: buffer",
            "RefactoringTool: Skipping implicit fixer: idioms",
            "RefactoringTool: Skipping implicit fixer: set_literal",
            "RefactoringTool: Skipping implicit fixer: ws_comma",
            "RefactoringTool: Refactored {0}".format(py_file),
            "RefactoringTool: Files that need to be modified:",
            "RefactoringTool: {0}".format(py_file),
            "RefactoringTool: No changes to {0}".format(py_file)]

        error = [x for x in error if x not in errignore]

        return output, "".join(error)

    def test_2to3(self):
        output, error = self.run2to3("spectrumnumber.py", [], [])
        self.assertEqual(output, [], "spectrumnumber.py 2to3 errors:\n" +
                         "".join(output))
        self.assertEqual(error, "",
                         "spectrumnumber.py 2to3 check had errors:\n" + error)

        output, error = self.run2to3("test_spectrumnumber.py", [], [])
        self.assertEqual(output, [], "test_spectrumnumber.py 2to3 errors:\n" +
                         "".join(output))
        self.assertEqual(error, "", "test_spectrumnumber.py 2to3 check had \
errors:\n" + error)


if __name__ == "__main__":
    unittest.main()
