#!/usr/bin/python
#
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

import spectrumnumber
import sys
import re
from numbers import Integral as _INT_OR_LONG
from functools import reduce
from operator import attrgetter

# ensure this code runs on python 2 and 3
if(sys.hexversion > 0x03000000):
    _unistr = str

    def _u(x):
        return x

    def _validateandpreparebytes(x, m):
        if(isinstance(x, (bytes, bytearray)) or
           (isinstance(x, (list, tuple)) and
           all(isinstance(val, int) for val in x))):
            return bytearray(x)

        if(isinstance(x, str)):
            return bytearray(x, 'latin-1')

        raise SpectrumTranslateError("{0} needs to be a list or tuple of \
ints, or of type 'bytes' or 'bytearray'".format(m))

else:
    # 2to3 will complain but this code is python 2 & 3 compatible
    _unistr = unicode
    from codecs import unicode_escape_decode as _UED

    def _u(x):
        return _UED(x)[0]

    def _validateandpreparebytes(x, m):
        # function to convert any valid source to a list of ints and
        # except if not
        if(isinstance(x, (str, bytes, bytearray)) or
           (isinstance(x, (list, tuple)) and
           all(isinstance(val, _INT_OR_LONG) for val in x))):
            return bytearray(x)

        raise SpectrumTranslateError("{0} needs to be a byte string, or a \
list or tuple of ints or longs, or of type 'bytes' or 'bytearray'".format(m))


# tables of all the opcodes
Z80_OPCODES = {
  "base": (
    "NOP", "LD BC,nn", "LD (BC),A", "INC BC",
    "INC B", "DEC B", "LD B,n", "RLCA",
    "EX AF,AF'", "ADD HL,BC", "LD A,(BC)", "DEC BC",
    "INC C", "DEC C", "LD C,n", "RRCA",
    "DJNZ j", "LD DE,nn", "LD (DE),A", "INC DE",
    "INC D", "DEC D", "LD D,n", "RLA",
    "JR j", "ADD HL,DE", "LD A,(DE)", "DEC DE",
    "INC E", "DEC E", "LD E,n", "RRA",
    "JR NZ,j", "LD HL,nn", "LD (aa),HL", "INC HL",
    "INC H", "DEC H", "LD H,n", "DAA",
    "JR Z,j", "ADD HL,HL", "LD HL,(aa)", "DEC HL",
    "INC L", "DEC L", "LD L,n", "CPL",
    "JR NC,j", "LD SP,aa", "LD (aa),A", "INC SP",
    "INC (HL)", "DEC (HL)", "LD (HL),n", "SCF",
    "JR C,j", "ADD HL,SP", "LD A,(aa)", "DEC SP",
    "INC A", "DEC A", "LD A,n", "CCF",
    "LD B,B", "LD B,C", "LD B,D", "LD B,E",
    "LD B,H", "LD B,L", "LD B,(HL)", "LD B,A",
    "LD C,B", "LD C,C", "LD C,D", "LD C,E",
    "LD C,H", "LD C,L", "LD C,(HL)", "LD C,A",
    "LD D,B", "LD D,C", "LD D,D", "LD D,E",
    "LD D,H", "LD D,L", "LD D,(HL)", "LD D,A",
    "LD E,B", "LD E,C", "LD E,D", "LD E,E",
    "LD E,H", "LD E,L", "LD E,(HL)", "LD E,A",
    "LD H,B", "LD H,C", "LD H,D", "LD H,E",
    "LD H,H", "LD H,L", "LD H,(HL)", "LD H,A",
    "LD L,B", "LD L,C", "LD L,D", "LD L,E",
    "LD L,H", "LD L,L", "LD L,(HL)", "LD L,A",
    "LD (HL),B", "LD (HL),C", "LD (HL),D", "LD (HL),E",
    "LD (HL),H", "LD (HL),L", "HALT", "LD (HL),A",
    "LD A,B", "LD A,C", "LD A,D", "LD A,E",
    "LD A,H", "LD A,L", "LD A,(HL)", "LD A,A",
    "ADD A,B", "ADD A,C", "ADD A,D", "ADD A,E",
    "ADD A,H", "ADD A,L", "ADD A,(HL)", "ADD A,A",
    "ADC A,B", "ADC A,C", "ADC A,D", "ADC A,E",
    "ADC A,H", "ADC A,L", "ADC A,(HL)", "ADC A,A",
    "SUB B", "SUB C", "SUB D", "SUB E",
    "SUB H", "SUB L", "SUB (HL)", "SUB A",
    "SBC A,B", "SBC A,C", "SBC A,D", "SBC A,E",
    "SBC A,H", "SBC A,L", "SBC A,(HL)", "SBC A,A",
    "AND B", "AND C", "AND D", "AND E",
    "AND H", "AND L", "AND (HL)", "AND A",
    "XOR B", "XOR C", "XOR D", "XOR E",
    "XOR H", "XOR L", "XOR (HL)", "XOR A",
    "OR B", "OR C", "OR D", "OR E",
    "OR H", "OR L", "OR (HL)", "OR A",
    "CP B", "CP C", "CP D", "CP E",
    "CP H", "CP L", "CP (HL)", "CP A",
    "RET NZ", "POP BC", "JP NZ,aa", "JP aa",
    "CALL NZ,aa", "PUSH BC", "ADD A,n", "RST 00H",
    "RET Z", "RET", "JP Z,aa", None,
    "CALL Z,aa", "CALL aa", "ADC A,n", "RST 08H",
    "RET NC", "POP DE", "JP NC,aa", "OUT (n),A",
    "CALL NC,aa", "PUSH DE", "SUB n", "RST 10H",
    "RET C", "EXX", "JP C,aa", "IN A,(n)",
    "CALL C,aa", None, "SBC A,n", "RST 18H",
    "RET PO", "POP HL", "JP PO,aa", "EX (SP),HL",
    "CALL PO,aa", "PUSH HL", "AND n", "RST 20H",
    "RET PE", "JP HL", "JP PE,aa", "EX DE,HL",
    "CALL PE,aa", None, "XOR n", "RST 28H",
    "RET P", "POP AF", "JP P,aa", "DI",
    "CALL P,aa", "PUSH AF", "OR n", "RST 30H",
    "RET M", "LD SP,HL", "JP M,aa", "EI",
    "CALL M,aa", None, "CP n", "RST 38H"),
  "CB": (
    "RLC B", "RLC C", "RLC D", "RLC E", "RLC H", "RLC L", "RLC (HL)", "RLC A",
    "RRC B", "RRC C", "RRC D", "RRC E", "RRC H", "RRC L", "RRC (HL)", "RRC A",
    "RL B", "RL C", "RL D", "RL E", "RL H", "RL L", "RL (HL)", "RL A",
    "RR B", "RR C", "RR D", "RR E", "RR H", "RR L", "RR (HL)", "RR A",
    "SLA B", "SLA C", "SLA D", "SLA E", "SLA H", "SLA L", "SLA (HL)", "SLA A",
    "SRA B", "SRA C", "SRA D", "SRA E", "SRA H", "SRA L", "SRA (HL)", "SRA A",
    "SLL/SL1 B", "SLL/SL1 C", "SLL/SL1 D", "SLL/SL1 E", "SLL/SL1 H",
    "SLL/SL1 L", "SLL/SL1 (HL)", "SLL/SL1 A",
    "SRL B", "SRL C", "SRL D", "SRL E", "SRL H", "SRL L", "SRL (HL)", "SRL A",
    "BIT 0,B", "BIT 0,C", "BIT 0,D", "BIT 0,E", "BIT 0,H", "BIT 0,L",
    "BIT 0,(HL)", "BIT 0,A",
    "BIT 1,B", "BIT 1,C", "BIT 1,D", "BIT 1,E", "BIT 1,H", "BIT 1,L",
    "BIT 1,(HL)", "BIT 1,A",
    "BIT 2,B", "BIT 2,C", "BIT 2,D", "BIT 2,E", "BIT 2,H", "BIT 2,L",
    "BIT 2,(HL)", "BIT 2,A",
    "BIT 3,B", "BIT 3,C", "BIT 3,D", "BIT 3,E", "BIT 3,H", "BIT 3,L",
    "BIT 3,(HL)", "BIT 3,A",
    "BIT 4,B", "BIT 4,C", "BIT 4,D", "BIT 4,E", "BIT 4,H", "BIT 4,L",
    "BIT 4,(HL)", "BIT 4,A",
    "BIT 5,B", "BIT 5,C", "BIT 5,D", "BIT 5,E", "BIT 5,H", "BIT 5,L",
    "BIT 5,(HL)", "BIT 5,A",
    "BIT 6,B", "BIT 6,C", "BIT 6,D", "BIT 6,E", "BIT 6,H", "BIT 6,L",
    "BIT 6,(HL)", "BIT 6,A",
    "BIT 7,B", "BIT 7,C", "BIT 7,D", "BIT 7,E", "BIT 7,H", "BIT 7,L",
    "BIT 7,(HL)", "BIT 7,A",
    "RES 0,B", "RES 0,C", "RES 0,D", "RES 0,E", "RES 0,H", "RES 0,L",
    "RES 0,(HL)", "RES 0,A",
    "RES 1,B", "RES 1,C", "RES 1,D", "RES 1,E", "RES 1,H", "RES 1,L",
    "RES 1,(HL)", "RES 1,A",
    "RES 2,B", "RES 2,C", "RES 2,D", "RES 2,E", "RES 2,H", "RES 2,L",
    "RES 2,(HL)", "RES 2,A",
    "RES 3,B", "RES 3,C", "RES 3,D", "RES 3,E", "RES 3,H", "RES 3,L",
    "RES 3,(HL)", "RES 3,A",
    "RES 4,B", "RES 4,C", "RES 4,D", "RES 4,E", "RES 4,H", "RES 4,L",
    "RES 4,(HL)", "RES 4,A",
    "RES 5,B", "RES 5,C", "RES 5,D", "RES 5,E", "RES 5,H", "RES 5,L",
    "RES 5,(HL)", "RES 5,A",
    "RES 6,B", "RES 6,C", "RES 6,D", "RES 6,E", "RES 6,H", "RES 6,L",
    "RES 6,(HL)", "RES 6,A",
    "RES 7,B", "RES 7,C", "RES 7,D", "RES 7,E", "RES 7,H", "RES 7,L",
    "RES 7,(HL)", "RES 7,A",
    "SET 0,B", "SET 0,C", "SET 0,D", "SET 0,E", "SET 0,H", "SET 0,L",
    "SET 0,(HL)", "SET 0,A",
    "SET 1,B", "SET 1,C", "SET 1,D", "SET 1,E", "SET 1,H", "SET 1,L",
    "SET 1,(HL)", "SET 1,A",
    "SET 2,B", "SET 2,C", "SET 2,D", "SET 2,E", "SET 2,H", "SET 2,L",
    "SET 2,(HL)", "SET 2,A",
    "SET 3,B", "SET 3,C", "SET 3,D", "SET 3,E", "SET 3,H", "SET 3,L",
    "SET 3,(HL)", "SET 3,A",
    "SET 4,B", "SET 4,C", "SET 4,D", "SET 4,E", "SET 4,H", "SET 4,L",
    "SET 4,(HL)", "SET 4,A",
    "SET 5,B", "SET 5,C", "SET 5,D", "SET 5,E", "SET 5,H", "SET 5,L",
    "SET 5,(HL)", "SET 5,A",
    "SET 6,B", "SET 6,C", "SET 6,D", "SET 6,E", "SET 6,H", "SET 6,L",
    "SET 6,(HL)", "SET 6,A",
    "SET 7,B", "SET 7,C", "SET 7,D", "SET 7,E", "SET 7,H", "SET 7,L",
    "SET 7,(HL)", "SET 7,A"),
  "DD": (
    None, None, None, None, None, None, None, None,
    None, "ADD IX,BC", None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, "ADD IX,DE", None, None, None, None, None, None,
    None, "LD IX,nn", "LD (aa),IX", "INC IX", "INC IXH", "DEC IXH", "LD IXH,n",
    None,
    None, "ADD IX,IX", "LD IX,(aa)", "DEC IX", "INC IXL", "DEC IXL",
    "LD IXL,n", None,
    None, None, None, None, "INC (IX+d)", "DEC (IX+d)", "LD (IX+d),n", None,
    None, "ADD IX,SP", None, None, None, None, None, None,
    None, None, None, None, "LD B,IXH", "LD B,IXL", "LD B,(IX+d)", None,
    None, None, None, None, "LD C,IXH", "LD C,IXL", "LD C,(IX+d)", None,
    None, None, None, None, "LD D,IXH", "LD D,IXL", "LD D,(IX+d)", None,
    None, None, None, None, "LD E,IXH", "LD E,IXL", "LD E,(IX+d)", None,
    "LD IXH,B", "LD IXH,C", "LD IXH,D", "LD IXH,E", "LD IXH,IXH", "LD IXH,IXL",
    "LD H,(IX+d)", "LD IXH,A",
    "LD IXL,B", "LD IXL,C", "LD IXL,D", "LD IXL,E", "LD IXL,IXH", "LD IXL,IXL",
    "LD L,(IX+d)", "LD IXL,A",
    "LD (IX+d),B", "LD (IX+d),C", "LD (IX+d),D", "LD (IX+d),E", "LD (IX+d),H",
    "LD (IX+d),L", None, "LD (IX+d),A",
    None, None, None, None, "LD A,IXH", "LD A,IXL", "LD A,(IX+d)", None,
    None, None, None, None, "ADD A,IXH", "ADD A,IXL", "ADD A,(IX+d)", None,
    None, None, None, None, "ADC A,IXH", "ADC A,IXL", "ADC A,(IX+d)", None,
    None, None, None, None, "SUB IXH", "SUB IXL", "SUB (IX+d)", None,
    None, None, None, None, "SBC A,IXH", "SBC A,IXL", "SBC A,(IX+d)", None,
    None, None, None, None, "AND IXH", "AND IXL", "AND (IX+d)", None,
    None, None, None, None, "XOR IXH", "XOR IXL", "XOR (IX+d)", None,
    None, None, None, None, "OR IXH", "OR IXL", "OR (IX+d)", None,
    None, None, None, None, "CP IXH", "CP IXL", "CP (IX+d)", None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, "POP IX", None, "EX (SP),IX", None, "PUSH IX", None, None,
    None, "JP (IX)", None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, "LD SP,IX", None, None, None, None, None, None),
  "DDCB": (
    "LD B,RLC (IX+d)", "LD C,RLC (IX+d)", "LD D,RLC (IX+d)", "LD E,RLC (IX+d)",
    "LD H,RLC (IX+d)", "LD L,RLC (IX+d)", "RLC (IX+d)", "LD A,RLC (IX+d)",
    "LD B,RRC (IX+d)", "LD C,RRC (IX+d)", "LD D,RRC (IX+d)", "LD E,RRC (IX+d)",
    "LD H,RRC (IX+d)", "LD L,RRC (IX+d)", "RRC (IX+d)", "LD A,RRC (IX+d)",
    "LD B,RL (IX+d)", "LD C,RL (IX+d)", "LD D,RL (IX+d)", "LD E,RL (IX+d)",
    "LD H,RL (IX+d)", "LD L,RL (IX+d)", "RL (IX+d)", "LD A,RL (IX+d)",
    "LD B,RR (IX+d)", "LD C,RR (IX+d)", "LD D,RR (IX+d)", "LD E,RR (IX+d)",
    "LD H,RR (IX+d)", "LD L,RR (IX+d)", "RR (IX+d)", "LD A,RR (IX+d)",
    "LD B,SLA (IX+d)", "LD C,SLA (IX+d)", "LD D,SLA (IX+d)", "LD E,SLA (IX+d)",
    "LD H,SLA (IX+d)", "LD L,SLA (IX+d)", "SLA (IX+d)", "LD A,SLA (IX+d)",
    "LD B,SRA (IX+d)", "LD C,SRA (IX+d)", "LD D,SRA (IX+d)", "LD E,SRA (IX+d)",
    "LD H,SRA (IX+d)", "LD L,SRA (IX+d)", "SRA (IX+d)", "LD A,SRA (IX+d)",
    "LD B,SLL/SL1 (IX+d)", "LD C,SLL/SL1 (IX+d)", "LD D,SLL/SL1 (IX+d)",
    "LD E,SLL/SL1 (IX+d)", "LD H,SLL/SL1 (IX+d)", "LD L,SLL/SL1 (IX+d)",
    "SLL/SL1 (IX+d)", "LD A,SLL/SL1 (IX+d)",
    "LD B,SRL (IX+d)", "LD C,SRL (IX+d)", "LD D,SRL (IX+d)", "LD E,SRL (IX+d)",
    "LD H,SRL (IX+d)", "LD L,SRL (IX+d)", "SRL (IX+d)", "LD A,SRL (IX+d)",
    "BIT 0,(IX+d)", "BIT 0,(IX+d)", "BIT 0,(IX+d)", "BIT 0,(IX+d)",
    "BIT 0,(IX+d)", "BIT 0,(IX+d)", "BIT 0,(IX+d)", "BIT 0,(IX+d)",
    "BIT 1,(IX+d)", "BIT 1,(IX+d)", "BIT 1,(IX+d)", "BIT 1,(IX+d)",
    "BIT 1,(IX+d)", "BIT 1,(IX+d)", "BIT 1,(IX+d)", "BIT 1,(IX+d)",
    "BIT 2,(IX+d)", "BIT 2,(IX+d)", "BIT 2,(IX+d)", "BIT 2,(IX+d)",
    "BIT 2,(IX+d)", "BIT 2,(IX+d)", "BIT 2,(IX+d)", "BIT 2,(IX+d)",
    "BIT 3,(IX+d)", "BIT 3,(IX+d)", "BIT 3,(IX+d)", "BIT 3,(IX+d)",
    "BIT 3,(IX+d)", "BIT 3,(IX+d)", "BIT 3,(IX+d)", "BIT 3,(IX+d)",
    "BIT 4,(IX+d)", "BIT 4,(IX+d)", "BIT 4,(IX+d)", "BIT 4,(IX+d)",
    "BIT 4,(IX+d)", "BIT 4,(IX+d)", "BIT 4,(IX+d)", "BIT 4,(IX+d)",
    "BIT 5,(IX+d)", "BIT 5,(IX+d)", "BIT 5,(IX+d)", "BIT 5,(IX+d)",
    "BIT 5,(IX+d)", "BIT 5,(IX+d)", "BIT 5,(IX+d)", "BIT 5,(IX+d)",
    "BIT 6,(IX+d)", "BIT 6,(IX+d)", "BIT 6,(IX+d)", "BIT 6,(IX+d)",
    "BIT 6,(IX+d)", "BIT 6,(IX+d)", "BIT 6,(IX+d)", "BIT 6,(IX+d)",
    "BIT 7,(IX+d)", "BIT 7,(IX+d)", "BIT 7,(IX+d)", "BIT 7,(IX+d)",
    "BIT 7,(IX+d)", "BIT 7,(IX+d)", "BIT 7,(IX+d)", "BIT 7,(IX+d)",
    "LD B,RES 0,(IX+d)", "LD C,RES 0,(IX+d)", "LD D,RES 0,(IX+d)",
    "LD E,RES 0,(IX+d)", "LD H,RES 0,(IX+d)", "LD L,RES 0,(IX+d)",
    "RES 0,(IX+d)", "LD A,RES 0,(IX+d)",
    "LD B,RES 1,(IX+d)", "LD C,RES 1,(IX+d)", "LD D,RES 1,(IX+d)",
    "LD E,RES 1,(IX+d)", "LD H,RES 1,(IX+d)", "LD L,RES 1,(IX+d)",
    "RES 1,(IX+d)", "LD A,RES 1,(IX+d)",
    "LD B,RES 2,(IX+d)", "LD C,RES 2,(IX+d)", "LD D,RES 2,(IX+d)",
    "LD E,RES 2,(IX+d)", "LD H,RES 2,(IX+d)", "LD L,RES 2,(IX+d)",
    "RES 2,(IX+d)", "LD A,RES 2,(IX+d)",
    "LD B,RES 3,(IX+d)", "LD C,RES 3,(IX+d)", "LD D,RES 3,(IX+d)",
    "LD E,RES 3,(IX+d)", "LD H,RES 3,(IX+d)", "LD L,RES 3,(IX+d)",
    "RES 3,(IX+d)", "LD A,RES 3,(IX+d)",
    "LD B,RES 4,(IX+d)", "LD C,RES 4,(IX+d)", "LD D,RES 4,(IX+d)",
    "LD E,RES 4,(IX+d)", "LD H,RES 4,(IX+d)", "LD L,RES 4,(IX+d)",
    "RES 4,(IX+d)", "LD A,RES 4,(IX+d)",
    "LD B,RES 5,(IX+d)", "LD C,RES 5,(IX+d)", "LD D,RES 5,(IX+d)",
    "LD E,RES 5,(IX+d)", "LD H,RES 5,(IX+d)", "LD L,RES 5,(IX+d)",
    "RES 5,(IX+d)", "LD A,RES 5,(IX+d)",
    "LD B,RES 6,(IX+d)", "LD C,RES 6,(IX+d)", "LD D,RES 6,(IX+d)",
    "LD E,RES 6,(IX+d)", "LD H,RES 6,(IX+d)", "LD L,RES 6,(IX+d)",
    "RES 6,(IX+d)", "LD A,RES 6,(IX+d)",
    "LD B,RES 7,(IX+d)", "LD C,RES 7,(IX+d)", "LD D,RES 7,(IX+d)",
    "LD E,RES 7,(IX+d)", "LD H,RES 7,(IX+d)", "LD L,RES 7,(IX+d)",
    "RES 7,(IX+d)", "LD A,RES 7,(IX+d)",
    "LD B,SET 0,(IX+d)", "LD C,SET 0,(IX+d)", "LD D,SET 0,(IX+d)",
    "LD E,SET 0,(IX+d)", "LD H,SET 0,(IX+d)", "LD L,SET 0,(IX+d)",
    "SET 0,(IX+d)", "LD A,SET 0,(IX+d)",
    "LD B,SET 1,(IX+d)", "LD C,SET 1,(IX+d)", "LD D,SET 1,(IX+d)",
    "LD E,SET 1,(IX+d)", "LD H,SET 1,(IX+d)", "LD L,SET 1,(IX+d)",
    "SET 1,(IX+d)", "LD A,SET 1,(IX+d)",
    "LD B,SET 2,(IX+d)", "LD C,SET 2,(IX+d)", "LD D,SET 2,(IX+d)",
    "LD E,SET 2,(IX+d)", "LD H,SET 2,(IX+d)", "LD L,SET 2,(IX+d)",
    "SET 2,(IX+d)", "LD A,SET 2,(IX+d)",
    "LD B,SET 3,(IX+d)", "LD C,SET 3,(IX+d)", "LD D,SET 3,(IX+d)",
    "LD E,SET 3,(IX+d)", "LD H,SET 3,(IX+d)", "LD L,SET 3,(IX+d)",
    "SET 3,(IX+d)", "LD A,SET 3,(IX+d)",
    "LD B,SET 4,(IX+d)", "LD C,SET 4,(IX+d)", "LD D,SET 4,(IX+d)",
    "LD E,SET 4,(IX+d)", "LD H,SET 4,(IX+d)", "LD L,SET 4,(IX+d)",
    "SET 4,(IX+d)", "LD A,SET 4,(IX+d)",
    "LD B,SET 5,(IX+d)", "LD C,SET 5,(IX+d)", "LD D,SET 5,(IX+d)",
    "LD E,SET 5,(IX+d)", "LD H,SET 5,(IX+d)", "LD L,SET 5,(IX+d)",
    "SET 5,(IX+d)", "LD A,SET 5,(IX+d)",
    "LD B,SET 6,(IX+d)", "LD C,SET 6,(IX+d)", "LD D,SET 6,(IX+d)",
    "LD E,SET 6,(IX+d)", "LD H,SET 6,(IX+d)", "LD L,SET 6,(IX+d)",
    "SET 6,(IX+d)", "LD A,SET 6,(IX+d)",
    "LD B,SET 7,(IX+d)", "LD C,SET 7,(IX+d)", "LD D,SET 7,(IX+d)",
    "LD E,SET 7,(IX+d)", "LD H,SET 7,(IX+d)", "LD L,SET 7,(IX+d)",
    "SET 7,(IX+d)", "LD A,SET 7,(IX+d)"),
  "ED": (
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    "IN B,(C)", "OUT (C),B", "SBC HL,BC", "LD (aa),BC", "NEG", "RETN", "IM 0",
    "LD I,A",
    "IN C,(C)", "OUT (C),C", "ADC HL,BC", "LD BC,(aa)", "NEG", "RETI",
    "IM 0/1", "LD R,A",
    "IN D,(C)", "OUT (C),D", "SBC HL,DE", "LD (aa),DE", "NEG", "RETN", "IM 1",
    "LD A,I",
    "IN E,(C)", "OUT (C),E", "ADC HL,DE", "LD DE,(aa)", "NEG", "RETN", "IM 2",
    "LD A,R",
    "IN H,(C)", "OUT (C),H", "SBC HL,HL", "LD (aa),HL", "NEG", "RETN", "IM 0",
    "RRD",
    "IN L,(C)", "OUT (C),L", "ADC HL,HL", "LD HL,(aa)", "NEG", "RETN",
    "IM 0/1", "RLD",
    "IN F,(C) / IN (C)", "OUT (C),0", "SBC HL,SP", "LD (aa),SP", "NEG", "RETN",
    "IM 1", None,
    "IN A,(C)", "OUT (C),A", "ADC HL,SP", "LD SP,(aa)", "NEG", "RETN", "IM 2",
    None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    "LDI", "CPI", "INI", "OUTI", None, None, None, None,
    "LDD", "CPD", "IND", "OUTD", None, None, None, None,
    "LDIR", "CPIR", "INIR", "OTIR", None, None, None, None,
    "LDDR", "CPDR", "INDR", "OTDR", None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None),
  "FD": (
    None, None, None, None, None, None, None, None,
    None, "ADD IY,BC", None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, "ADD IY,DE", None, None, None, None, None, None,
    None, "LD IY,nn", "LD (aa),IY", "INC IY", "INC IYH", "DEC IYH", "LD IYH,n",
    None,
    None, "ADD IY,IY", "LD IY,(aa)", "DEC IY", "INC IYL", "DEC IYL",
    "LD IYL,n", None,
    None, None, None, None, "INC (IY+d)", "DEC (IY+d)", "LD (IY+d),n", None,
    None, "ADD IY,SP", None, None, None, None, None, None,
    None, None, None, None, "LD B,IYH", "LD B,IYL", "LD B,(IY+d)", None,
    None, None, None, None, "LD C,IYH", "LD C,IYL", "LD C,(IY+d)", None,
    None, None, None, None, "LD D,IYH", "LD D,IYL", "LD D,(IY+d)", None,
    None, None, None, None, "LD E,IYH", "LD E,IYL", "LD E,(IY+d)", None,
    "LD IYH,B", "LD IYH,C", "LD IYH,D", "LD IYH,E", "LD IYH,IYH", "LD IYH,IYL",
    "LD H,(IY+d)", "LD IYH,A",
    "LD IYL,B", "LD IYL,C", "LD IYL,D", "LD IYL,E", "LD IYL,IYH", "LD IYL,IYL",
    "LD L,(IY+d)", "LD IYL,A",
    "LD (IY+d),B", "LD (IY+d),C", "LD (IY+d),D", "LD (IY+d),E", "LD (IY+d),H",
    "LD (IY+d),L", None, "LD (IY+d),A",
    None, None, None, None, "LD A,IYH", "LD A,IYL", "LD A,(IY+d)", None,
    None, None, None, None, "ADD A,IYH", "ADD A,IYL", "ADD A,(IY+d)", None,
    None, None, None, None, "ADC A,IYH", "ADC A,IYL", "ADC A,(IY+d)", None,
    None, None, None, None, "SUB IYH", "SUB IYL", "SUB (IY+d)", None,
    None, None, None, None, "SBC A,IYH", "SBC A,IYL", "SBC A,(IY+d)", None,
    None, None, None, None, "AND IYH", "AND IYL", "AND (IY+d)", None,
    None, None, None, None, "XOR IYH", "XOR IYL", "XOR (IY+d)", None,
    None, None, None, None, "OR IYH", "OR IYL", "OR (IY+d)", None,
    None, None, None, None, "CP IYH", "CP IYL", "CP (IY+d)", None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, "POP IY", None, "EX (SP),IY", None, "PUSH IY", None, None,
    None, "JP (IY)", None, None, None, None, None, None,
    None, None, None, None, None, None, None, None,
    None, "LD SP,IY", None, None, None, None, None, None),
  "FDCB": (
    "LD B,RLC (IY+d)", "LD C,RLC (IY+d)", "LD D,RLC (IY+d)", "LD E,RLC (IY+d)",
    "LD H,RLC (IY+d)", "LD L,RLC (IY+d)", "RLC (IY+d)", "LD A,RLC (IY+d)",
    "LD B,RRC (IY+d)", "LD C,RRC (IY+d)", "LD D,RRC (IY+d)", "LD E,RRC (IY+d)",
    "LD H,RRC (IY+d)", "LD L,RRC (IY+d)", "RRC (IY+d)", "LD A,RRC (IY+d)",
    "LD B,RL (IY+d)", "LD C,RL (IY+d)", "LD D,RL (IY+d)", "LD E,RL (IY+d)",
    "LD H,RL (IY+d)", "LD L,RL (IY+d)", "RL (IY+d)", "LD A,RL (IY+d)",
    "LD B,RR (IY+d)", "LD C,RR (IY+d)", "LD D,RR (IY+d)", "LD E,RR (IY+d)",
    "LD H,RR (IY+d)", "LD L,RR (IY+d)", "RR (IY+d)", "LD A,RR (IY+d)",
    "LD B,SLA (IY+d)", "LD C,SLA (IY+d)", "LD D,SLA (IY+d)", "LD E,SLA (IY+d)",
    "LD H,SLA (IY+d)", "LD L,SLA (IY+d)", "SLA (IY+d)", "LD A,SLA (IY+d)",
    "LD B,SRA (IY+d)", "LD C,SRA (IY+d)", "LD D,SRA (IY+d)", "LD E,SRA (IY+d)",
    "LD H,SRA (IY+d)", "LD L,SRA (IY+d)", "SRA (IY+d)", "LD A,SRA (IY+d)",
    "LD B,SLL/SL1 (IY+d)", "LD C,SLL/SL1 (IY+d)", "LD D,SLL/SL1 (IY+d)",
    "LD E,SLL/SL1 (IY+d)", "LD H,SLL/SL1 (IY+d)", "LD L,SLL/SL1 (IY+d)",
    "SLL/SL1 (IY+d)", "LD A,SLL/SL1 (IY+d)",
    "LD B,SRL (IY+d)", "LD C,SRL (IY+d)", "LD D,SRL (IY+d)", "LD E,SRL (IY+d)",
    "LD H,SRL (IY+d)", "LD L,SRL (IY+d)", "SRL (IY+d)", "LD A,SRL (IY+d)",
    "BIT 0,(IY+d)", "BIT 0,(IY+d)", "BIT 0,(IY+d)", "BIT 0,(IY+d)",
    "BIT 0,(IY+d)", "BIT 0,(IY+d)", "BIT 0,(IY+d)", "BIT 0,(IY+d)",
    "BIT 1,(IY+d)", "BIT 1,(IY+d)", "BIT 1,(IY+d)", "BIT 1,(IY+d)",
    "BIT 1,(IY+d)", "BIT 1,(IY+d)", "BIT 1,(IY+d)", "BIT 1,(IY+d)",
    "BIT 2,(IY+d)", "BIT 2,(IY+d)", "BIT 2,(IY+d)", "BIT 2,(IY+d)",
    "BIT 2,(IY+d)", "BIT 2,(IY+d)", "BIT 2,(IY+d)", "BIT 2,(IY+d)",
    "BIT 3,(IY+d)", "BIT 3,(IY+d)", "BIT 3,(IY+d)", "BIT 3,(IY+d)",
    "BIT 3,(IY+d)", "BIT 3,(IY+d)", "BIT 3,(IY+d)", "BIT 3,(IY+d)",
    "BIT 4,(IY+d)", "BIT 4,(IY+d)", "BIT 4,(IY+d)", "BIT 4,(IY+d)",
    "BIT 4,(IY+d)", "BIT 4,(IY+d)", "BIT 4,(IY+d)", "BIT 4,(IY+d)",
    "BIT 5,(IY+d)", "BIT 5,(IY+d)", "BIT 5,(IY+d)", "BIT 5,(IY+d)",
    "BIT 5,(IY+d)", "BIT 5,(IY+d)", "BIT 5,(IY+d)", "BIT 5,(IY+d)",
    "BIT 6,(IY+d)", "BIT 6,(IY+d)", "BIT 6,(IY+d)", "BIT 6,(IY+d)",
    "BIT 6,(IY+d)", "BIT 6,(IY+d)", "BIT 6,(IY+d)", "BIT 6,(IY+d)",
    "BIT 7,(IY+d)", "BIT 7,(IY+d)", "BIT 7,(IY+d)", "BIT 7,(IY+d)",
    "BIT 7,(IY+d)", "BIT 7,(IY+d)", "BIT 7,(IY+d)", "BIT 7,(IY+d)",
    "LD B,RES 0,(IY+d)", "LD C,RES 0,(IY+d)", "LD D,RES 0,(IY+d)",
    "LD E,RES 0,(IY+d)", "LD H,RES 0,(IY+d)", "LD L,RES 0,(IY+d)",
    "RES 0,(IY+d)", "LD A,RES 0,(IY+d)",
    "LD B,RES 1,(IY+d)", "LD C,RES 1,(IY+d)", "LD D,RES 1,(IY+d)",
    "LD E,RES 1,(IY+d)", "LD H,RES 1,(IY+d)", "LD L,RES 1,(IY+d)",
    "RES 1,(IY+d)", "LD A,RES 1,(IY+d)",
    "LD B,RES 2,(IY+d)", "LD C,RES 2,(IY+d)", "LD D,RES 2,(IY+d)",
    "LD E,RES 2,(IY+d)", "LD H,RES 2,(IY+d)", "LD L,RES 2,(IY+d)",
    "RES 2,(IY+d)", "LD A,RES 2,(IY+d)",
    "LD B,RES 3,(IY+d)", "LD C,RES 3,(IY+d)", "LD D,RES 3,(IY+d)",
    "LD E,RES 3,(IY+d)", "LD H,RES 3,(IY+d)", "LD L,RES 3,(IY+d)",
    "RES 3,(IY+d)", "LD A,RES 3,(IY+d)",
    "LD B,RES 4,(IY+d)", "LD C,RES 4,(IY+d)", "LD D,RES 4,(IY+d)",
    "LD E,RES 4,(IY+d)", "LD H,RES 4,(IY+d)", "LD L,RES 4,(IY+d)",
    "RES 4,(IY+d)", "LD A,RES 4,(IY+d)",
    "LD B,RES 5,(IY+d)", "LD C,RES 5,(IY+d)", "LD D,RES 5,(IY+d)",
    "LD E,RES 5,(IY+d)", "LD H,RES 5,(IY+d)", "LD L,RES 5,(IY+d)",
    "RES 5,(IY+d)", "LD A,RES 5,(IY+d)",
    "LD B,RES 6,(IY+d)", "LD C,RES 6,(IY+d)", "LD D,RES 6,(IY+d)",
    "LD E,RES 6,(IY+d)", "LD H,RES 6,(IY+d)", "LD L,RES 6,(IY+d)",
    "RES 6,(IY+d)", "LD A,RES 6,(IY+d)",
    "LD B,RES 7,(IY+d)", "LD C,RES 7,(IY+d)", "LD D,RES 7,(IY+d)",
    "LD E,RES 7,(IY+d)", "LD H,RES 7,(IY+d)", "LD L,RES 7,(IY+d)",
    "RES 7,(IY+d)", "LD A,RES 7,(IY+d)",
    "LD B,SET 0,(IY+d)", "LD C,SET 0,(IY+d)", "LD D,SET 0,(IY+d)",
    "LD E,SET 0,(IY+d)", "LD H,SET 0,(IY+d)", "LD L,SET 0,(IY+d)",
    "SET 0,(IY+d)", "LD A,SET 0,(IY+d)",
    "LD B,SET 1,(IY+d)", "LD C,SET 1,(IY+d)", "LD D,SET 1,(IY+d)",
    "LD E,SET 1,(IY+d)", "LD H,SET 1,(IY+d)", "LD L,SET 1,(IY+d)",
    "SET 1,(IY+d)", "LD A,SET 1,(IY+d)",
    "LD B,SET 2,(IY+d)", "LD C,SET 2,(IY+d)", "LD D,SET 2,(IY+d)",
    "LD E,SET 2,(IY+d)", "LD H,SET 2,(IY+d)", "LD L,SET 2,(IY+d)",
    "SET 2,(IY+d)", "LD A,SET 2,(IY+d)",
    "LD B,SET 3,(IY+d)", "LD C,SET 3,(IY+d)", "LD D,SET 3,(IY+d)",
    "LD E,SET 3,(IY+d)", "LD H,SET 3,(IY+d)", "LD L,SET 3,(IY+d)",
    "SET 3,(IY+d)", "LD A,SET 3,(IY+d)",
    "LD B,SET 4,(IY+d)", "LD C,SET 4,(IY+d)", "LD D,SET 4,(IY+d)",
    "LD E,SET 4,(IY+d)", "LD H,SET 4,(IY+d)", "LD L,SET 4,(IY+d)",
    "SET 4,(IY+d)", "LD A,SET 4,(IY+d)",
    "LD B,SET 5,(IY+d)", "LD C,SET 5,(IY+d)", "LD D,SET 5,(IY+d)",
    "LD E,SET 5,(IY+d)", "LD H,SET 5,(IY+d)", "LD L,SET 5,(IY+d)",
    "SET 5,(IY+d)", "LD A,SET 5,(IY+d)",
    "LD B,SET 6,(IY+d)", "LD C,SET 6,(IY+d)", "LD D,SET 6,(IY+d)",
    "LD E,SET 6,(IY+d)", "LD H,SET 6,(IY+d)", "LD L,SET 6,(IY+d)",
    "SET 6,(IY+d)", "LD A,SET 6,(IY+d)",
    "LD B,SET 7,(IY+d)", "LD C,SET 7,(IY+d)", "LD D,SET 7,(IY+d)",
    "LD E,SET 7,(IY+d)", "LD H,SET 7,(IY+d)", "LD L,SET 7,(IY+d)",
    "SET 7,(IY+d)", "LD A,SET 7,(IY+d)")
}

"""
up to 6 machine states per command so 3 bits to code xxx
4 possible machine state lengths (3,4,5,6) so 2 bits and up to 6 of
them: aa bb cc dd ee ff
2 possible machine command lengths so length 2 yyy, state lengths2 gg hh
ii jj kk ll
flag to say if machine command time state lengths unknown z=1 then T
value in ffeeddccbbaaxxx as number and same for llkkjjiihhggyyy

2 bits to hold if new line needed after command mm

flags: Sign, Zero, Halfcarry, Parity/overflow, N add/subtract, Carry
values for each flag:
  0=flag is non-standardly changed (? in string)
  1=flag is unafected              (- in string)
  2=flag is set as you'd expect    (+ in string)
  3=flag is reset                  (0 in string)
  4=flag is set                    (1 in string)
for parity overflow: 2 other options
  5=flag is set as per parity      (P in string)
  6=flag is set as per overflow    (V in string)

 3 bits to hold Carry nnn
 3 bits to hold add/subtract ooo
 3 bits to hold parity/overflow ppp
 3 bits to hold halfcarry qqq
 3 bits to hold zero rrr
 3 bits to hold sign sss

1 bit to indicate if have flags t

1 bit to indicate if undocumented command u


timeing format:

 31    24 23    16 15     8 7      0
 |      | |      | |      | |      |
 0llkkjji ihhggyyy ffeeddcc bbaaxxxz

data format:
 31    24 23    16 15     8 7      0
 |      | |      | |      | |      |
 00000000 00utsssr rrqqqppp ooonnnmm
"""

Z80_OPCODE_TIMES = {
  "base": (
    18, 22, 20, 50, 18, 18, 20, 18,
    18, 86, 20, 50, 18, 18, 20, 18,
    1180198, 22, 20, 50, 18, 18, 20, 18,
    534, 86, 20, 50, 18, 18, 20, 18,
    655894, 22, 26, 50, 18, 18, 20, 18,
    655894, 86, 26, 50, 18, 18, 20, 18,
    655894, 22, 24, 50, 22, 86, 22, 18,
    655894, 86, 24, 50, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    20, 20, 20, 20, 20, 20, 18, 20,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    18, 18, 18, 18, 18, 18, 20, 18,
    1114150, 22, 22, 22, 721178, 38, 20, 38,
    1114150, 22, 22, 0, 721178, 282, 20, 38,
    1114150, 22, 22, 278, 721178, 38, 20, 38,
    1114150, 18, 22, 278, 721178, 0, 20, 38,
    1114150, 22, 22, 8474, 721178, 38, 20, 38,
    1114150, 18, 22, 18, 721178, 0, 20, 38,
    1114150, 22, 22, 18, 721178, 38, 20, 38,
    1114150, 50, 22, 18, 721178, 0, 20, 38),
  "CB": (
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    1, 1, 1, 1, 1, 1, 1, 1,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 342, 84,
    84, 84, 84, 84, 84, 84, 342, 84,
    84, 84, 84, 84, 84, 84, 342, 84,
    84, 84, 84, 84, 84, 84, 342, 84,
    84, 84, 84, 84, 84, 84, 342, 84,
    84, 84, 84, 84, 84, 84, 342, 84,
    84, 84, 84, 84, 84, 84, 342, 84,
    84, 84, 84, 84, 84, 84, 342, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84,
    84, 84, 84, 84, 84, 84, 344, 84),
  "DD": (
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 344, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 344, 0, 0, 0, 0, 0, 0,
    0, 88, 92, 212, 1, 1, 1, 0,
    0, 344, 92, 212, 1, 1, 1, 0,
    0, 0, 0, 0, 6236, 6236, 2138, 0,
    0, 344, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    1, 1, 1, 1, 1, 1, 2138, 1,
    1, 1, 1, 1, 1, 1, 2138, 1,
    2138, 2138, 2138, 2138, 2138, 2138, 0, 2138,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 88, 0, 33884, 0, 152, 0, 0,
    0, 84, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 212, 0, 0, 0, 0, 0, 0),
  "DDCB": (
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1),
  "ED": (
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    342, 342, 344, 92, 84, 88, 84, 148,
    342, 342, 344, 92, 1, 88, 1, 148,
    342, 342, 344, 92, 1, 1, 84, 148,
    342, 342, 344, 92, 1, 1, 84, 148,
    342, 342, 344, 92, 1, 1, 1, 1114,
    342, 342, 344, 92, 1, 1, 1, 1114,
    342, 1, 344, 92, 1, 1, 1, 0,
    342, 342, 344, 92, 1, 1, 1, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    2136, 2136, 1176, 1176, 0, 0, 0, 0,
    2136, 2136, 1176, 1176, 0, 0, 0, 0,
    70002778, 70002778, 38544538, 38544538, 0, 0, 0, 0,
    70002778, 70002778, 38544538, 38544538, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0),
  "FD": (
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 344, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 344, 0, 0, 0, 0, 0, 0,
    0, 88, 92, 212, 1, 1, 1, 0,
    0, 344, 92, 212, 1, 1, 1, 0,
    0, 0, 0, 0, 6236, 6236, 2138, 0,
    0, 344, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    1, 1, 1, 1, 1, 1, 2138, 1,
    1, 1, 1, 1, 1, 1, 2138, 1,
    2138, 2138, 2138, 2138, 2138, 2138, 0, 2138,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 1, 1, 2138, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 88, 0, 33884, 0, 152, 0, 0,
    0, 84, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 212, 0, 0, 0, 0, 0, 0),
  "FDCB": (
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6234, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1,
    1, 1, 1, 1, 1, 1, 6236, 1),
}

Z80_OPCODE_DATA = {
  "base": (
    1198372, 1198372, 1198372, 1198372, 1349220, 1349252, 1198372, 1202536,
    1348168, 1200488, 1198372, 1198372, 1349220, 1349252, 1198372, 1202536,
    1198373, 1198372, 1198372, 1198372, 1349220, 1349252, 1198372, 1202536,
    1198374, 1200488, 1198372, 1198372, 1349220, 1349252, 1198372, 1202536,
    1198373, 1198372, 1198372, 1198372, 1349220, 1349252, 1198372, 1344800,
    1198373, 1200488, 1198372, 1198372, 1349220, 1349252, 1198372, 1204612,
    1198373, 1198372, 1198372, 1198372, 1349220, 1349252, 1198372, 1202544,
    1198373, 1200488, 1198372, 1198372, 1349220, 1349252, 1198372, 1196392,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1349224, 1349224, 1349224, 1349224, 1349224, 1349224, 1349224, 1349224,
    1349224, 1349224, 1349224, 1349224, 1349224, 1349224, 1349224, 1349224,
    1349256, 1349256, 1349256, 1349256, 1349256, 1349256, 1349256, 1349256,
    1349256, 1349256, 1349256, 1349256, 1349256, 1349256, 1349256, 1349256,
    1353068, 1353068, 1353068, 1353068, 1353068, 1353068, 1353068, 1353068,
    1351020, 1351020, 1351020, 1351020, 1351020, 1351020, 1351020, 1351020,
    1351020, 1351020, 1351020, 1351020, 1351020, 1351020, 1351020, 1351020,
    1349256, 1349256, 1349256, 1349256, 1349256, 1349256, 1349256, 1349256,
    1198373, 1198372, 1198373, 1198374, 1198372, 1198372, 1349224, 1198372,
    1198373, 1198374, 1198373, 0, 1198372, 1198372, 1349224, 1198372,
    1198373, 1198372, 1198373, 1198372, 1198372, 1198372, 1349256, 1198372,
    1198373, 1198372, 1198373, 1198372, 1198372, 0, 1349256, 1198372,
    1198373, 1198372, 1198373, 1198372, 1198372, 1198372, 1353068, 1198372,
    1198373, 1198374, 1198373, 1198372, 1198372, 0, 1351020, 1198372,
    1198373, 1348168, 1198373, 1198372, 1198372, 1198372, 1351020, 1198372,
    1198373, 1198372, 1198373, 1198372, 1198372, 0, 1349256, 1198372),
  "CB": (
    1351016, 1351016, 1351016, 1351016, 1351016, 1351016, 1351016, 1351016,
    1351016, 1351016, 1351016, 1351016, 1351016, 1351016, 1351016, 1351016,
    1351016, 1351016, 1351016, 1351016, 1351016, 1351016, 1351016, 1351016,
    1351016, 1351016, 1351016, 1351016, 1351016, 1351016, 1351016, 1351016,
    1351016, 1351016, 1351016, 1351016, 1351016, 1351016, 1351016, 1351016,
    1351016, 1351016, 1351016, 1351016, 1351016, 1351016, 1351016, 1351016,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 2097152,
    1482088, 1482088, 1482088, 1482088, 1482088, 1482088, 1482088, 1482088,
    1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636,
    1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636,
    1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636,
    1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636,
    1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636,
    1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636,
    1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636,
    1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636, 1089636,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 1198372),
  "DD": (
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1200488, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1200488, 0, 0, 0, 0, 0, 0,
    0, 1198372, 1198372, 1198372, 2097152, 2097152, 3295524, 0,
    0, 1200488, 1198372, 1198372, 2097152, 2097152, 3295524, 0,
    0, 0, 0, 0, 1349220, 1349252, 1198372, 0,
    0, 1200488, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 3295524, 3295524, 1198372, 0,
    0, 0, 0, 0, 3295524, 3295524, 1198372, 0,
    0, 0, 0, 0, 3295524, 3295524, 1198372, 0,
    0, 0, 0, 0, 3295524, 3295524, 1198372, 0,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 0, 1198372,
    0, 0, 0, 0, 3295524, 3295524, 1198372, 0,
    0, 0, 0, 0, 2097152, 2097152, 1349224, 0,
    0, 0, 0, 0, 2097152, 2097152, 1349224, 0,
    0, 0, 0, 0, 2097152, 2097152, 1349256, 0,
    0, 0, 0, 0, 2097152, 2097152, 1349256, 0,
    0, 0, 0, 0, 2097152, 2097152, 1353068, 0,
    0, 0, 0, 0, 2097152, 2097152, 1351020, 0,
    0, 0, 0, 0, 2097152, 2097152, 1351020, 0,
    0, 0, 0, 0, 2097152, 2097152, 1349256, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1198372, 0, 1198372, 0, 1198372, 0, 0,
    0, 1198374, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1198372, 0, 0, 0, 0, 0, 0),
  "DDCB": (
    3448168, 3448168, 3448168, 3448168, 3448168, 3448168, 1351016, 3448168,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1351016, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1351016, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1351016, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1351016, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1351016, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1482088, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524),
  "ED": (
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1351012, 1198372, 1349256, 1198372, 1349248, 1198372, 1198372, 1198372,
    1351012, 1198372, 1349224, 1198372, 2097152, 1198372, 2097152, 1198372,
    1351012, 1198372, 1349256, 1198372, 2097152, 2097152, 1198372, 1349732,
    1351012, 1198372, 1349224, 1198372, 2097152, 2097152, 1198372, 1349732,
    1351012, 1198372, 1349256, 1198372, 2097152, 2097152, 2097152, 1351012,
    1351012, 1198372, 1349224, 1198372, 2097152, 2097152, 2097152, 1351012,
    3448164, 3295524, 1349256, 1198372, 2097152, 2097152, 2097152, 0,
    1351012, 1198372, 1349224, 1198372, 2097152, 2097152, 2097152, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1202276, 1347716, 1048708, 1048708, 0, 0, 0, 0,
    1202276, 1347716, 1048708, 1048708, 0, 0, 0, 0,
    1203044, 1347716, 1114244, 1114244, 0, 0, 0, 0,
    1203044, 1347716, 1114244, 1114244, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0),
  "FD": (
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1200488, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1200488, 0, 0, 0, 0, 0, 0,
    0, 1198372, 1198372, 1198372, 2097152, 2097152, 3295524, 0,
    0, 1200488, 1198372, 1198372, 2097152, 2097152, 3295524, 0,
    0, 0, 0, 0, 1349220, 1349252, 1198372, 0,
    0, 1200488, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 3295524, 3295524, 1198372, 0,
    0, 0, 0, 0, 3295524, 3295524, 1198372, 0,
    0, 0, 0, 0, 3295524, 3295524, 1198372, 0,
    0, 0, 0, 0, 3295524, 3295524, 1198372, 0,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    1198372, 1198372, 1198372, 1198372, 1198372, 1198372, 0, 1198372,
    0, 0, 0, 0, 3295524, 3295524, 1198372, 0,
    0, 0, 0, 0, 2097152, 2097152, 1349224, 0,
    0, 0, 0, 0, 2097152, 2097152, 1349224, 0,
    0, 0, 0, 0, 2097152, 2097152, 1349256, 0,
    0, 0, 0, 0, 2097152, 2097152, 1349256, 0,
    0, 0, 0, 0, 2097152, 2097152, 1353068, 0,
    0, 0, 0, 0, 2097152, 2097152, 1351020, 0,
    0, 0, 0, 0, 2097152, 2097152, 1351020, 0,
    0, 0, 0, 0, 2097152, 2097152, 1349256, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1198372, 0, 1198372, 0, 1198372, 0, 0,
    0, 1198374, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1198372, 0, 0, 0, 0, 0, 0),
  "FDCB": (
    3448168, 3448168, 3448168, 3448168, 3448168, 3448168, 1351016, 3448168,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1351016, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1351016, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1351016, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1351016, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1351016, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1482088, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1089636, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    2097152, 2097152, 2097152, 2097152, 2097152, 2097152, 1198372, 2097152,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524,
    3295524, 3295524, 3295524, 3295524, 3295524, 3295524, 1198372, 3295524)
}

SPECTRUM_COMMANDS = (
    "SPECTRUM", "PLAY", "RND", "INKEY$", "PI", "FN", "POINT", "SCREEN$",
    "ATTR", "AT", "TAB", "VAL$", "CODE", "VAL", "LEN", "SIN", "COS", "TAN",
    "ASN", "ACS", "ATN", "LN", "EXP", "INT", "SQR", "SGN", "ABS", "PEEK", "IN",
    "USR", "STR$", "CHR$", "NOT", "BIN", "OR", "AND", "<=", ">=", "<>", "LINE",
    "THEN", "TO", "STEP", "DEF FN", "CAT", "FORMAT", "MOVE", "ERASE", "OPEN #",
    "CLOSE #", "MERGE", "VERIFY", "BEEP", "CIRCLE", "INK", "PAPER", "FLASH",
    "BRIGHT", "INVERSE", "OVER", "OUT", "LPRINT", "LLIST", "STOP", "READ",
    "DATA", "RESTORE", "NEW", "BORDER", "CONTINUE", "DIM", "REM", "FOR",
    "GO TO", "GO SUB", "INPUT", "LOAD", "LIST", "LET", "PAUSE", "NEXT", "POKE",
    "PRINT", "PLOT", "RUN", "SAVE", "RANDOMIZE", "IF", "CLS", "DRAW", "CLEAR",
    "RETURN", "COPY")


def getvariableoffset(data):
    """This function works out where variables start in a sepctrum basic
    program listing.  It returns the offset from the start of the data
    to where the variables are.
    """

    # validate and convert data from string to bytearray if needed
    data = _validateandpreparebytes(data, "data")

    # work out position of variables
    offset = 0
    while(offset < len(data)):
        linenumber = (data[offset] * 256) + data[offset + 1]
        # bits 5,6,7 of variable code will be 16384 or
        # more as the max line number is 9999
        if(linenumber > 9999):
            # too big for line number: is 1st variable
            break

        # otherwise move to next line
        linelength = data[offset + 2] + data[offset + 3] * 256
        offset += linelength + 4

    return offset


def basictotext(data, iAutostart=-1, ivariableOffset=-1, hexfornonascii=False):
    """This function returns a string representation of the list of
    numbers, bytes or bytearray object supplied of a basic program.  Due
    to the way program data was stored, it is possible that non-
    printable characters were in the line.  In this case these
    characters are represented by ^ followed by a 2 digit hexadecimal
    representation of the character. Also floating point numbers are
    stored after the visible digits.  Sometimes for space reasons or to
    hide the true numbers, these did not match up.  If The true floating
    point representation of a number differs from the visible one, then
    the true value is displayed in brackets after the visible number.

    data is list of numbers, or of type bytes or bytearray of the data
    of the program.  The program is assumed to begin at the start of the
    array to the end of the array.
    iAutostart is the line number where the program auto starts (less
    than 0 or >9999 if no autostart).  ivariableOffset is the offset
    from the start of the array to where variables are stored.  If not
    specified then this will be worked out.

    hexfornonascii sets if you want the character returned as it would
    in a spectrum (ie "COPY " for 255, copyright symbol for 127, or
    blocks for character 129) by setting this to False (the default),
    or to return any non-ascii character as ^ followed by a 2 digit
    hexadecimal number.
    """

    # validate and convert data from string to bytearray if needed
    data = _validateandpreparebytes(data, "data")

    # if no variable offset supplied then work out where
    if(ivariableOffset == -1):
        ivariableOffset = getvariableoffset(data)

    text = ''

    if(iAutostart >= 0 and iAutostart < 10000):
        text = "Autostart at line:{0}\n".format(iAutostart)

    i = 0

    # move through program listing lines
    while(i < ivariableOffset):
        # get line number
        # line number is high byte first
        iLineNumber = data[i+1] + 256 * data[i]
        i += 2
        if(iLineNumber > 9999):
            raise SpectrumTranslateError("Line number cannot exceed 9999")

        text += "{0} ".format(iLineNumber)

        # get line length
        iLineLen = data[i] + 256 * data[i+1]
        i += 2

        sNumber = ''
        bInQuotes = False
        bPostREM = False
        bPostDEF = False
        Lastchar = ord(' ')

        # now move through line
        l = 0
        k = data[i]
        while(l < iLineLen):
            # get next line entry character
            k = data[i]
            i += 1

            # if we're in a REM statement display characters.  ignore
            # last character as should be new line character
            if(bPostREM and l < iLineLen - 1):
                text += getspectrumchar(k, hexfornonascii)
                l += 1
                continue

            # have we reached end of number without hitting number
            # definition?
            if(len(sNumber) > 0 and  # are we in a number?
               k != 0x0E and         # and not hitting a hidden number
               not(                  # and not an extension of number
                                     # 0-9
                   (k >= 0x30 and k <= 0x39 and ' ' not in sNumber) or
                   k == ord('E') or k == ord('e') or     # an exponent symbol
                   # a plus of minus after an exponent symbol
                   ((k == ord('+') or k == ord('-')) and
                    (sNumber[-1] == ord('E') or sNumber[-1] == ord('e'))) or
                   k == 32                   # hit a space
               )):
                # if so exit number gathering routine without gathering
                # number definition
                text += sNumber
                text += "(number without value)"
                sNumber = ''

            # are we entering/leaving a quote
            if(k == ord('"')):
                bInQuotes = not bInQuotes

            # are we entering or definately leaving a DEF
            if(k == ord(')')):
                bPostDEF = False

            if(k == 206):
                bPostDEF = True

            # deal with non-printable characters, and user-defined
            # characters
            if(k < 32 or (k > 127 and k < 163)):
                if(k == 13):  # end of line
                    # if still characters hidden after end-of line char
                    # then print them
                    if(l != iLineLen - 1):
                        while(l < iLineLen):
                            text += '^{0:02X}'.format(data[i])
                            i += 1
                            l += 1
                    text += "\n"

                elif(k == 14):  # number definition
                    # if not enough bytes before end of line or program
                    # then we have a problem
                    if(l + 5 >= iLineLen or i + 5 >= len(data)):
                        raise SpectrumTranslateError(
                            "Error with number format")

                    sn = spectrumnumber.SpectrumNumber(data[i:i+5])
                    i += 5
                    l += 5
                    # ignore what happens after def
                    if(bPostDEF):
                        sNumber = ''

                    # output displayed number
                    else:
                        text += sNumber
                        # check if displayed number same as hidden one,
                        # and if not also display real number  can cause
                        # exceptions so catch them, although is very
                        # unlikely.  trying to get value of empty string
                        # however will cause exception so test for this
                        # case & handle it first
                        if(len(sNumber) == 0):
                            text += "({0!s})".format(sn)
                        else:
                            try:
                                if(sn != sNumber):
                                    text += "({0!s})".format(sn)
                            except:
                                text += "(real value unclear)"

                        sNumber = ''

                # deal with commands like INK, PAPER etc that have a
                # single byte argument
                elif((k >= 16 and k <= 21) or k == 23):
                    text += "^{0:02X}^{1:02X}".format(k, data[i])
                    i += 1
                    l += 1

                # deal with AT with x & y coordinates after
                elif(k == 22):
                    text += "^{0:02X}^{1:02X}^{2:02X}".format(k, data[i],
                                                              data[i+1])
                    i += 2
                    l += 2

                else:
                    text += "^{0:02X}".format(k)
                    i += 1
                    l += 1

            # see if is valid number digit.  If so store it
            if(not bInQuotes and not bPostREM and (
               (k >= 0x30 and k <= 0x39) or
               k == ord('.') or
               ((k == ord('E') or k == ord('e')) and len(sNumber) > 0) or
               ((k == ord('-') or k == ord('+')) and len(sNumber) > 0 and
                (sNumber[-1] == ord('E') or sNumber[-1] == ord('e')))
               )):
                sNumber += chr(k)
                Lastchar = k
                l += 1
                continue

            # printable characters
            if(k > 31 and k < 128):
                text += getspectrumchar(k, hexfornonascii)

            # check for commands
            if(k > 162):
                if(k == 234):
                    bPostREM = True

                if(Lastchar != ord(' ') and not bInQuotes):
                    text += ' '

                text += SPECTRUM_COMMANDS[k - 163] + " "
                k = ord(' ')

            Lastchar = k
            # exit if hit end of line
            if(k == 13):
                break

            l += 1

        # see if hit end of program marker
        if(k == 128):
            break

    # end program part of code

    # do variables
    if(i < len(data)):
        text += "\n\nVariables:\n"

    while(i < len(data)):
        # get indicator of type of variable
        k = (data[i] >> 5) & 0x7

        VarName = getspectrumchar((data[i] & 0x1F) + 0x60, hexfornonascii)

        # number who's name is one letter only
        if(k == 3):
            text += VarName + "="
            text += _sn_to_string(data[i + 1:i + 6],
                                  "unable to extract number")
            text += "\n"
            i += 6

        # number who's name is greater than 1 letter
        elif(k == 5):
            text += VarName
            i += 1

            while(True):
                text += getspectrumchar(data[i] & 0x7F, hexfornonascii)
                if(data[i] > 127):
                    break

                i += 1

            i += 1
            text += "=" + _sn_to_string(data[i:i + 5],
                                        "unable to extract number")
            text += "\n"
            i += 5

        # array of numbers
        elif(k == 4):
            text += VarName
            i += 1

            # for each dimension, print its length
            for x in range(data[i + 2]):
                text += "[{0}]".format(data[i+3+x+x] + 256 * data[i+4+x+x])

            text += "=" + arraytotext(data[i+2:], 128, hexfornonascii) + "\n"
            i += 2 + data[i] + 256 * data[i+1]

        # for next loop control
        elif(k == 7):
            try:
                text += "FOR...NEXT, {0} Value={1} Limit={2} Step={3}".format(
                    VarName, _sn_to_string(data[i+1:i+6]),
                    _sn_to_string(data[i+6:i+11]),
                    _sn_to_string(data[i+11:i+16]))
                text += " Loop back to line={0}, statement={1}\n".format(
                    data[i+16] + 256 * data[i+17], data[i+18])
            except:
                text += "Unable to extract FOR...NEXT variable VarName"

            i += 19

        # string
        elif(k == 2):
            strlen = data[i+1] + 256 * data[i+2]
            text += VarName + '$="' + getspectrumstring(data[i+3:i+3+strlen],
                                                        hexfornonascii) + '"\n'
            i += strlen + 3

        # array of characters
        elif(k == 6):
            text += VarName + "$"
            i += 1

            # for each dimension, print it's length
            for x in range(data[i+2]):
                text += "[{0}]".format(data[i+3+x*2] + 256 * data[i+4+x*2])

            text += "=" + arraytotext(data[i+2:], 192, hexfornonascii) + "\n"
            i += 2 + data[i] + 256 * data[i+1]

        else:
            raise SpectrumTranslateError("Unrecognised variable type")

    return text


def basictoxml(data, iAutostart=-1, ivariableOffset=-1, hexfornonascii=False):
    """This function returns an XML representation as a string of the
    list or bytes or bytearray object supplied of a basic program.  Due
    to the way program data was stored, it is possible that non-
    printable characters were in the line.  In this case these
    characters are represented by ^ followed by a 2 digit hexadecimal
    representation of the character.  Also floating point numbers are
    stored after the visible digits.  Sometimes for space reasons or to
    hide the true numbers, these did not match up.  If The true floating
    point representation of a number differs from the visible one, then
    the true value is also listed.

    data is list of numbers, or of type bytes or bytearray of the data
    of the program.  The program is assumed to begin at he start of the
    array to the end of the array.
    iAutostart is the line number where the program auto starts (less
    than 0 or >9999 if no autostart).  ivariableOffset is the offset
    from the start of the array to where variables are stored.  If not
    specified then this will be worked out.

    hexfornonascii sets if you want the character returned as it would
    in a spectrum (ie "COPY " for 255, copyright symbol for 127, or
    blocks for character 129) by setting this to False (the default),
    or to return any non-ascii character as ^ followed by a 2 digit
    hexadecimal number.
    """

    # validate and convert data from string to bytearray if needed
    data = _validateandpreparebytes(data, "data")

    # if no variable offset supplied then work out where
    if(ivariableOffset == -1):
        ivariableOffset = getvariableoffset(data)

    text = '<?xml version="1.0" encoding="UTF-8" ?>\n<basiclisting>\n'

    if(iAutostart >= 0 and iAutostart < 10000):
        text += "  <autostart>" + str(iAutostart) + "</autostart>\n"

    i = 0

    # move through program listing lines
    while(i < ivariableOffset):
        # get line number
        # line number is high byte first
        iLineNumber = data[i+1] + 256*data[i]
        i += 2
        if(iLineNumber > 9999):
            raise SpectrumTranslateError("Line number cannot exceed 9999")

        text += "  <line>\n    <linenumber>{0}</linenumber>\n".format(
            iLineNumber)

        # get line length
        iLineLen = data[i] + 256*data[i+1]
        i += 2

        sNumber = ''
        bInQuotes = False
        bPostREM = False
        bPostDEF = False
        bInInstruction = False
        bInstructionHadArgument = False

        # now move through line
        l = 0
        while(l < iLineLen):
            # get next line entry character
            k = data[i]
            i += 1

            # have we hit an argument for an instruction?
            if(bInInstruction and not bInstructionHadArgument and
               not bInQuotes and k != ord(':') and k != 13):
                text += '\n      <argument>'
                bInstructionHadArgument = True

            # if we're in a REM statement display characters.  ignore
            # last character as should be new line character
            if(bPostREM and l < iLineLen - 1):
                text += getspectrumchar(k, hexfornonascii)
                l += 1
                continue

            # have we reached end of number without hitting number
            # definition?
            if(len(sNumber) > 0 and  # are we in a number?
               k != 0x0E and         # and not hitting a hidden number
               not(                 # and not an extension of the number
                   # have 0-9
                   (k >= 0x30 and k <= 0x39 and ' ' not in sNumber) or
                   k == ord('E') or k == ord('e') or     # an exponent symbol
                   # a plus of minus after an exponent symbol
                   ((k == ord('+') or k == ord('-')) and
                    (sNumber[-1] == ord('E') or
                    sNumber[-1] == ord('e'))) or
                   k == 32                   # hit a space
               )):
                # if so exit number gathering routine without gathering
                # number definition
                text += "<number>" + sNumber
                text += "<realvalue>number without value</realvalue>"
                text += "</number>"
                sNumber = ''

            # are we entering/leaving a quote
            if(k == ord('"')):
                bInQuotes = not bInQuotes

            # are we entering or definately leaving a DEF
            if(k == ord(')')):
                bPostDEF = False

            if(k == 206):
                bPostDEF = True

            # deal with non-printable characters, and user-defined
            # characters
            if(k < 32 or (k > 127 and k < 163)):
                if(k == 13):  # end of line
                    # if still characters hidden after end-of line char
                    # then print them
                    if(l != iLineLen-1):
                        text += '<hiddendata>'
                        while(l < iLineLen):
                            text += '^{0:02X}'.format(data[i])
                            i += 1
                            l += 1

                        text += '</hiddendata>'

                    if(bInInstruction and bInstructionHadArgument):
                        text += '</argument>'
                        bInstructionHadArgument = False

                    # terminate command if we have to
                    if(bInInstruction):
                        text += '\n    </instruction>'
                        bInInstruction = False

                    text += "\n"

                elif(k == 14):  # number definition
                    # if not enough bytes before end of line or program
                    # then we have a problem
                    if(l + 5 >= iLineLen or i + 5 >= len(data)):
                        raise SpectrumTranslateError("Number format error")

                    sn = spectrumnumber.SpectrumNumber(data[i:i+5])
                    i += 5
                    l += 5
                    # ignore what happens after def
                    if(bPostDEF):
                        sNumber = ''

                    # output displayed number
                    else:
                        text += '<number>'+sNumber
                        # check if displayed number same as hidden one,
                        # and if not also display real number can cause
                        # exceptions so catch them, although is very
                        # unlikely.  Trying to get value of empty string
                        # however will cause exception so test for this
                        # case & handle it first
                        if(len(sNumber) == 0):
                            text += "<{1}>{0!s}</{1}>".format(
                                sn, "realvalue")
                        else:
                            try:
                                if(sn != sNumber):
                                    text += "<{1}>{0!s}</{1}>".format(
                                        sn, "realvalue")
                            except:
                                text += "<realvalue>real value unclear\
</realvalue>"

                        sNumber = ''
                        text += '</number>'

                # deal with commands like INK, PAPER etc that have a
                # single byte argument
                elif((k >= 16 and k <= 21) or k == 23):
                    text += '<format>' + ("INK", "PAPER", "FLASH", "BRIGHT",
                                          "INVERSE", "OVER", "", "TAB")[k-16]
                    text += ' ' + str(data[i]) + '</format>'
                    i += 1
                    l += 1

                # deal with AT with x & y coordinates after
                elif(k == 22):
                    text += '<format>AT {0!s},{1!s}</format>'.format(data[i],
                                                                     data[i+1])
                    i += 2
                    l += 2

                else:
                    text += '<{0}>{1!s}</{0}>'.format("nonprintablecharacter",
                                                      k)
                    i += 1
                    l += 1

            # see if is valid number digit.  If so store it
            if(not bInQuotes and not bPostREM and (
               (k >= 0x30 and k <= 0x39) or
               k == ord('.') or
               ((k == ord('E') or k == ord('e')) and len(sNumber) > 0) or
               ((k == ord('-') or k == ord('+')) and len(sNumber) > 0 and
                (sNumber[-1] == ord('E') or sNumber[-1] == ord('e')))
               )):
                sNumber += chr(k)
                l += 1
                continue

            # have we hit an instruction seperator?
            if(bInInstruction and not bInQuotes and k == 58):
                # check to see if we need to close argument xml tag
                if(bInstructionHadArgument):
                    text += '</argument>'

                text += '\n    </instruction>\n    \
<instructionseperator>:</instructionseperator>\n'

                bInInstruction = False

            # printable characters not handled elsewhere
            if(k > 31 and k < 128 and k != ord(':')):
                text += getspectrumchar(k, hexfornonascii)

            # check for commands
            if(k > 162):
                if(k == 234):
                    bPostREM = True

                # are we entering an instruction
                if(not bInInstruction):
                    # if so make a note of it and output xml
                    text += '    <instruction>\n      '
                    bInInstruction = True
                    bInstructionHadArgument = False

                text += '<keyword>' + SPECTRUM_COMMANDS[k-163] + '</keyword>'

            # exit if hit end of line
            if(k == 13):
                break

            l += 1

        # exit line
        text += "  </line>\n"

        # see if hit end of program marker
        if(k == 128):
            break

    # end program part of code

    # do variables
    if(i < len(data)):
        text += "  <variables>\n"

        while(i < len(data)):
            # get indicator of type of variable
            k = (data[i] >> 5) & 0x7

            VarName = getspectrumchar((data[i] & 0x1F) + 0x60, hexfornonascii)

            # number who's name is one letter only
            if(k == 3):
                text += '    <variable>\n      <name>' + VarName
                text += '</name>\n      <type>number</type>\n'
                text += '      <value>'
                text += _sn_to_string(data[i+1:i+6],
                                      "unable to extract number")
                text += '</value>\n    </variable>\n'
                i += 6

            # number who's name is greater than 1 letter
            elif(k == 5):
                text += '    <variable>\n      <name>' + VarName
                i += 1

                while(True):
                    text += getspectrumchar(data[i] & 0x7F, hexfornonascii)
                    if(data[i] > 127):
                        break

                    i += 1

                text += '</name>\n      <type>number</type>\n'
                text += '      <value>'
                text += _sn_to_string(data[i+1:i+6],
                                      "unable to extract number")
                text += '</value>\n    </variable>\n'
                i += 6

            # array of numbers
            elif(k == 4):
                text += '    <variable>\n      <name>' + VarName
                text += '</name>\n      <type>numberarray</type>\n'
                text += '      <value>\n'
                i += 1

                text += '\n'.join(['        ' + x for x in arraytoxml(
                                       data[i+2:], 128,
                                       hexfornonascii).splitlines()])
                text += '\n      </value>\n    </variable>\n'
                i += 2 + data[i] + 256*data[i+1]

            # for next loop control
            elif(k == 7):
                try:
                    text += '    <variable>\n      <name>' + VarName
                    text += '</name>\n      <type>fornext</type>\n'
                    fortext = '      <value>' + _sn_to_string(data[i+1:i+6])
                    fortext += '</value>\n'
                    fortext += '      <limit>' + _sn_to_string(data[i+6:i+11])
                    fortext += '</limit>\n'
                    fortext += '      <step>' + _sn_to_string(data[i+11:i+16])
                    fortext += '</step>\n'
                    fortext += '      <loopbackto>\n        <line>'
                    fortext += str(data[i+16]+256*data[i+17]) + '</line>\n'
                    fortext += '        <statement>' + str(data[i+18])
                    fortext += '</statement>\n      </loopback>\n'
                    fortext += '    </variable>\n'
                    text += fortext
                except:
                    text += '      Unable to extract FOR...NEXT variables\n'
                    text += '    </variable>\n'

                i += 19

            # string
            elif(k == 2):
                text += '    <variable>\n      <name>' + VarName
                text += '$</name>\n      <type>string</type>\n'
                strlen = data[i+1] + 256*data[i+2]
                text += "      <value>" + getspectrumstring(
                    data[i+3:i+3+strlen], hexfornonascii) + \
                    "</value>\n    </variable>\n"
                i += strlen + 3

            # array of characters
            elif(k == 6):
                text += '    <variable>\n      <name>' + VarName + '$</name>\n'
                text += '      <type>characterarray</type>\n      <value>\n'
                i += 1

                text += '\n'.join(['        ' + x for x in
                                   arraytoxml(data[i+2:], 192,
                                              hexfornonascii).splitlines()])
                text += '\n      </value>\n    </variable>\n'
                i += 2 + data[i] + 256*data[i+1]

            else:
                raise SpectrumTranslateError("Unrecognised variable type")

        text += "  </variables>\n"

    # exit listing
    text += '</basiclisting>\n'

    return text


def getarraydepth(data, descriptor):
    """This function works out how many dimensions there are in a
    spectrum file array.  data is the spectrum file array data as a list
    or tuple of ints or longs, or a byte string in python 2, or of type
    'bytes' or 'bytearray'.  descriptor is the file descriptor for the
    file array.  The lower 6 bits specify the array name (a single
    character).  The top 2 specify the array type.  You don't have to
    single out these bits as this function will only consider bits 6 and
    7.  The top 2 bits are 128 for a number array, 192 for a character
    array, and 64 for a string array.  Returns the number of dimensions
    in the array, or -1 if not a recognised format.

    NB strings are an array of characters and thus array such as
    String[] would have depth of 2: array of array of characters.
    """

    # validate and convert data from string to bytearray if needed
    data = _validateandpreparebytes(data, "data")

    # number array or character array
    if((descriptor & 192) == 128 or (descriptor & 192) == 192):
        return data[0]

    # string
    if((descriptor & 192) == 64):
        # always unidimensional
        return 1

    return -1


def extractarray(data, descriptor):
    """This function extracts a spectrum array (number, character, or
    string) from data.  data must be a list or tuple of ints or longs,
    or a byte string in python 2, or a bytes or bytearray object.
    Note that the data returned if it's string is in raw spectum bytes,
    and that it may need to be output through a function to code escape
    characters and commands (function such as getspectrumstring).  Also
    numbers are extracted into lists of SpectrumNumber objects.

    data is the spectrum file array data supplied as a list or tuple of
    ints or longs, or a byte string in python 2, or a bytes or bytearray
    object.
    descriptor is the file descriptor for the file array.
        The lower 6 bits specify the array name (a single character).
        The top 2 specify the array type.
        You don't have to single out these bits as this function will
        only consider bits 6 and 7.  The
        top 2 bits are 128 for a number array, 192 for a character
        array, and 64 for a string array.
    """

    # return array including subarrays
    def getSubArray(dims, data, isnumber, offset):
        # have we reached last dimension?
        if(len(dims) == 1):
            # if so it's either number
            if(isnumber):
                # in which case return list of numbers
                return [spectrumnumber.SpectrumNumber(data[i:i+5]) for i in
                        range(offset, offset + 5*dims[0], 5)]
            # or a string
            else:
                return ''.join([chr(c) for c in data[offset:offset + dims[0]]])

        # otherwise we need to return a sub-array
        # first work out offset to where data is held: work out the
        # number of elements in sub arrays
        o = reduce(lambda x, y: x * y, dims[1:])
        # if is number then each element takes up 5 bytes of memory
        if(isnumber):
            o *= 5

        # return the array as made up of sub arrays
        return [getSubArray(dims[1:], data, isnumber, offset + i*o) for i in
                range(dims[0])]

    # validate and convert data from string to bytearray if needed
    data = _validateandpreparebytes(data, "data")

    # number array or character array
    if(descriptor & 128 == 128):
        # get dimension lengths
        dim_lengths = [data[x] + 256*data[x+1] for x in range(1, data[0]*2, 2)]
        # o is current offset.  Set to past dimensions details pointing
        # at first element
        o = len(dim_lengths)*2 + 1
        # get arrays and return them
        return getSubArray(dim_lengths, data, descriptor & 192 == 128, o)

    # string
    if(descriptor & 192 == 64):
        return data[:]

    return None


def arraytotext(data, descriptor, hexfornonascii=False):
    """This function converts a spectrum array (number, character, or
    string) to text.  The elements returned are seperated by commas, and
    the individual dimensions are seperated by curly brackets.

    data is the spectrum file array data supplied as a list or tuple of
    ints or longs, or a byte string in python 2, or a bytes or bytearray
    object.
    descriptor is the file descriptor for the file array.
        The lower 6 bits specify the array name (a single character).
        The top 2 specify the array type.
        You don't have to single out these bits as this function will
        only consider bits 6 and 7.  The
        top 2 bits are 128 for a number array, 192 for a character
        array, and 64 for a string array.

    hexfornonascii sets if you want the character returned as it would
    in a spectrum (ie "COPY " for 255, copyright symbol for 127, or
    blocks for character 129) by setting this to False (the default),
    or to return any non-ascii character as ^ followed by a 2 digit
    hexadecimal number.
    """

    # return array including subarrays with bounding braces, and
    # apropriate indentation
    def getSubArray(data, isnumber, indent):
        # have we reached last subarray (will be string or number, but
        # not a list)
        if(not isinstance(data[0], list)):
            # if so it's either number
            if(isnumber):
                # in which case return list of numbers
                return indent + ', '.join([str(i) for i in data])
            # or a string
            else:
                return indent + '"' + ('",\n' + indent + '"').join(
                    [getspectrumstring(s, hexfornonascii) for s in data]) + '"'

        # otherwise we need to return a sub-array
        return indent + '{\n' + ('\n' + indent + '},\n' + indent + '{\n').join(
            [getSubArray(sub, isnumber, indent + "  ") for sub in data]
            ) + '\n' + indent + '}'

    # validate and convert data from string to bytearray if needed
    data = _validateandpreparebytes(data, "data")

    # number array or character array
    if(descriptor & 128 == 128):
        return '{\n' + getSubArray(extractarray(data, descriptor),
                                   (descriptor & 192 == 128), "  ") + '\n}'

    # string
    if(descriptor & 192 == 64):
        return getspectrumstring(data, hexfornonascii)

    return None


def arraytoxml(data, descriptor, hexfornonascii=False):
    """
    This function converts a spectrum array (number, character, or
    string) to XML.

    data is the spectrum file array data supplied as a list or tuple of
    ints or longs, or a byte string in python 2, or a bytes or bytearray
    object.
    descriptor is the file descriptor for the file array.
        The lower 6 bits specify the array name (a single character).
        The top 2 specify the array type.
        You don't have to single out these bits as this function will
        only consider bits 6 and 7.  The
        top 2 bits are 128 for a number array, 192 for a character
        array, and 64 for a string array.

    hexfornonascii sets if you want the character returned as it would
    in a spectrum (ie "COPY " for 255, copyright symbol for 127, or
    blocks for character 129) by setting this to False (the default),
    or to return any non-ascii character as ^ followed by a 2 digit
    hexadecimal number.
    """

    # return array including subarrays with bounding braces, and
    # apropriate indentation
    def getSubArray(data, isnumber, indent):
        # have we reached last subarray (will be string or number, but
        # not a list)
        if(not isinstance(data[0], list)):
            # if so it's either number
            if(isnumber):
                # in which case return list of numbers
                return indent + '<number>' + (
                    '</number>\n' + indent + '<number>').join(
                        [str(i) for i in data]) + '</number>'
            # or a string
            else:
                return indent + '<string>' + (
                    '</string>\n' + indent + '<string>').join(
                        [getspectrumstring(s,
                                           hexfornonascii) for s in data]) + \
                    '</string>'

        # otherwise we need to return a sub-array
        return indent + '<dimension>\n' + ('\n' + indent + '</dimension>\n' +
                                           indent + '<dimension>\n').join(
            [getSubArray(sub, isnumber, indent + "  ") for sub in data]) + \
            '\n' + indent + '</dimension>'

    # validate and convert data from string to bytearray if needed
    data = _validateandpreparebytes(data, "data")

    # number array or character array
    if(descriptor & 128 == 128):
        return '<dimension>\n' + getSubArray(extractarray(data, descriptor),
                                             (descriptor & 192 == 128),
                                             "  ") + '\n</dimension>'

    # string
    if(descriptor & 192 == 64):
        return '<string>' + getspectrumstring(data, hexfornonascii) + \
               '</string>'

    return None


def _sn_to_string(data, message=-1):
    # function to transfer number to string and handle exceptions

    try:
        # get number
        sn = spectrumnumber.SpectrumNumber(data)

        # convert to string: can cause exceptions
        return str(sn)
    except:
        if(message == -1):
            raise

        return message


def getspectrumchar(c, hexfornonascii=False):
    """This function converts the 8 bit integer value of a spectrum
    character to a string representation of the spectrum character.  The
    lower part is mostly in line with ASCII standard with a couple of
    exceptions:  character decimal 96 is the pound sign, character
    decimal 94 is an up arrow (there is no ^ in the spectrum character
    set), and character decimal 127 is a copyright symbol.  characters
    decimal 164 up to 255 (162 to 255 in the 128K versions) are not
    simple characters but are the names of the spectrum commands with a
    space after them.  From decimal 144 to 163 (or 161 on 128K machines)
    were used for the user defined characters.  From 128 to 143
    inclusive are block characters.
    This function will return the spectrum character of the character,
    the command, or the value in 2 digit hexadecimal preceded by a '^'.

    hexfornonascii sets if you want the character returned as it would
    in a spectrum (ie "COPY " for 255, copyright symbol for 127, or
    blocks for character 129) by setting this to False (the default),
    or to return any non-ascii character as ^ followed by a 2 digit
    hexadecimal number.

    Returns the Spectrum string representation of the int supplied
    """

    # convert to int if needed
    if(isinstance(c, (str, _unistr))):
        c = ord(c[0]) & 0xFF

    if(c == 127):
        return "^7F" if hexfornonascii else _u("\u00A9")
    if(c == 96):
        return "^60" if hexfornonascii else _u("\u00A3")
    if(c == 94):
        return "^5E" if hexfornonascii else _u("\u2191")
    if(c >= 128 and c <= 143 and not hexfornonascii):
        return (_u('\u2003'), _u('\u259D'), _u('\u2598'), _u('\u2580'),
                _u('\u2597'), _u('\u2590'), _u('\u259A'), _u('\u259C'),
                _u('\u2596'), _u('\u259E'), _u('\u258C'), _u('\u259B'),
                _u('\u2584'), _u('\u259F'), _u('\u2599'), _u('\u2588')
                )[c-128]
    if(c >= 163 and not hexfornonascii):
        return SPECTRUM_COMMANDS[c-163] + ' '
    if(c < 32 or c > 127):
        return '^{0:02X}'.format(c)

    return chr(c)


def getspectrumstring(s, hexfornonascii=False):
    """This function converts a byte sting of 8 bit integer values to a
    string representation of the spectrum character.  The lower part is
    mostly in line with ASCII standard with a couple of exceptions:
    character decimal 96 is the pound sign, character decimal 94 is an
    up arrow (there is no ^ in the spectrum character set), and
    character decimal 127 is a copyright symbol.  characters decimal 164
    up to 255 (162 to 255 in the 128K versions) are not simple
    characters but are the names of the spectrum commands with a space
    after them.  From decimal 144 to 163 (or 161 on 128K machines) were
    used for the user defined characters.  This function will return the
    spectrum character of the character, the command, or the value in 2
    digit hexadecimal preceded by a '^'.  From 128 to 143 inclusive are
    block characters.

    hexfornonascii sets if you want the character returned as it would
    in a spectrum (ie "COPY " for 255, copyright symbol for 127, or
    blocks for character 129) by setting this to False (the default),
    or to return any non-ascii character as ^ followed by a 2 digit
    hexadecimal number.

    Returns the Spectrum string representation of the bytes supplied
    """

    if(isinstance(s, list)):
        s = [chr(x) for x in s]

    return ''.join([getspectrumchar(c, hexfornonascii) for c in s])


def chartospectrum(c):
    """This function takes a string or character or number and returns
    the spectrum equivalent.  It converts commands (like LOAD, or
    PRINT), and non-ASCII characters like the copyright symbol, uparrow
    (which is used instead of ^), the pound sign, and the graphical
    blocks and returns character in the range 0 to 255.  It also will
    convert coded values denoted by ^ followed by a 2 digit hexadecimal
    number.  It will raise a SpectrumTranslateError if the input is not
    a valid spectrum character.
    """

    # handle control codes
    if(isinstance(c, (str, _unistr)) and len(c) == 3 and c[0] == '^'):
        try:
            return chr(int(c[1:], 16))
        except:
            raise SpectrumTranslateError(
                "code must be ^ followed by 2 digit hexadecimal number.")

    # If not a single character, check for command
    if(isinstance(c, (str, _unistr)) and len(c) != 1):
        for i in range(len(SPECTRUM_COMMANDS)):
            if(SPECTRUM_COMMANDS[i] + ' ' == c or
               SPECTRUM_COMMANDS[i] == c):
                return chr(i + 163)
        raise SpectrumTranslateError("Not recognised spectrum command.")

    # convert to number
    if(isinstance(c, (str, _unistr))):
        c = ord(c)

    if(c == 0x00A9):
        return chr(127)
    if(c == 0x00A3):
        return chr(96)
    if(c == 0x2191):
        return chr(94)
    blockcodes = (0x2003, 0x259D, 0x2598, 0x2580, 0x2597, 0x2590, 0x259A,
                  0x259C, 0x2596, 0x259E, 0x258C, 0x259B, 0x2584, 0x259F,
                  0x2599, 0x2588)
    if(c in blockcodes):
        for i in range(len(blockcodes)):
            if(c == blockcodes[i]):
                return chr(i + 128)

    if(c < 0 or c > 255):
        raise SpectrumTranslateError(
            chr(c) + " is invalid spectrum character.")

    return chr(c)


def stringtospectrum(s, wantcommands=True):
    """This function takes a string and returns the spectrum equivalent.
    It converts commands (like LOAD, or PRINT, and remembering that they
    must have a space after them), and non-ASCII characters like the
    copyright symbol, uparrow (which is used instead of ^), the pound
    sign, and the graphical blocks and returns character in the range 0
    to 255.  It also will convert coded values denoted by ^ followed by
    a 2 digit hexadecimal number.  It will raise a
    SpectrumTranslateError if the input contains a non-valid spectrum
    character.
    """

    ret = []
    i = 0
    while(i < len(s)):
        # deal with escape codes
        if(s[i] == '^'):
            ret += chartospectrum(s[i:i+3])
            i += 3
            continue

        # now check for commands if needed
        if(wantcommands):
            foundcommand = False
            for c in range(len(SPECTRUM_COMMANDS)):
                if(s[i:].startswith(SPECTRUM_COMMANDS[c] + ' ')):
                    ret += chr(c + 163)
                    # move past command and terminating space
                    i += len(SPECTRUM_COMMANDS[c]) + 1
                    foundcommand = True
                    break

            if(foundcommand):
                continue

        # otherwise just treat as one character
        ret += chartospectrum(s[i])
        i += 1

    return "".join(ret)

# array to map from colours to colour data so that bright black & not
# bright black both map to 0x000000
_COLOUR_MAP = (0, 1, 2, 3, 4, 5, 6, 7, 0, 9, 10, 11, 12, 13, 14, 15)
# array of ZX spectrum colours
_ZXCOLOURTORGB = (0x000000, 0x0000CD, 0xCD0000, 0xCD00CD,
                  0x00CD00, 0x00CDCD, 0xCDCD00, 0xCDCDCD,
                  0x000000, 0x0000FF, 0xFF0000, 0xFF00FF,
                  0x00FF00, 0x00FFFF, 0xFFFF00, 0xFFFFFF)
_ZXCOLOURTORGBLIST = ([0x00, 0x00, 0x00], [0x00, 0x00, 0xCD],
                      [0xCD, 0x00, 0x00], [0xCD, 0x00, 0xCD],
                      [0x00, 0xCD, 0x00], [0x00, 0xCD, 0xCD],
                      [0xCD, 0xCD, 0x00], [0xCD, 0xCD, 0xCD],
                      [0x00, 0x00, 0x00], [0x00, 0x00, 0xFF],
                      [0xFF, 0x00, 0x00], [0xFF, 0x00, 0xFF],
                      [0x00, 0xFF, 0x00], [0x00, 0xFF, 0xFF],
                      [0xFF, 0xFF, 0x00], [0xFF, 0xFF, 0xFF])


def getgiffromscreen(data, delay=320):
    """This function extracts an Image from spectrum screen format data.
    It outputs it as an array of byte in the format of a GIF file.  This
    can either be saved to a file as a GIF image or used as the argument
    for a PIL (Python Image Library) object wia stringIO for example.
    This function returns an animated GIF if the flash attribute is
    used.  The delay value specifies the length of time for each version
    of the screen to be displayed with the flash blocks in either state.
    On the origional spectrum this was 16 frames which at 50Hz for
    screen refresh equates to 320 milliseconds.  If there is no flash
    being used then it returns a normal static GIF image.

    data must be a list or tuple of ints or longs, or a byte string in
    python 2, or a bytes or bytearray object.

    delay is the delay between flashing images in milliseconds if the
    image has flashing colours.  If you don't want a flashing image then
    pass -1 for delay and the function will return a static GIF image of
    the screen effectively with all flash attributes turned off.  If you
    want a static image with the flash attributes in the flashing state,
    pass -2 to this argument.

    This returns a bytearray which holds the screen image in GIF format.
    It will be static or 2 frame animated depending on whether there are
    flashing colours and if you want them.  You can simply save the byte
    array to a file for it to be used as a GIF image, or pass it on to
    other functions.  It returns None if the function encounters any
    problems.
    """

    class _gif_encoder_stream():
        # private class to encode gif data
        output_masks = (0x0000, 0x0001, 0x0003, 0x0007, 0x000F, 0x001F, 0x003F,
                        0x007F, 0x00FF, 0x01FF, 0x03FF, 0x07FF, 0x0FFF, 0x1FFF,
                        0x3FFF, 0x7FFF, 0xFFFF)

        MaxOutputCode = 0xFFF

        def __init__(self, data):
            # remember screen we're encodeing
            self.data = data
            self.out = []

        def PutImageAsGif(self, bFlash, delay, bFirst):
            """this method outputs an image to the supplied stream."""

            # output graphic control extension
            self.PutByte(0x21)  # extension introducer
            self.PutByte(0xf9)  # GCE label
            self.PutByte(4)     # data block size
            self.PutByte(0)     # no transparency
            # delay in 1/100 of seconds
            self.PutWord(0 if (delay == -1 or delay == -2) else delay//10)
            self.PutByte(0)     # transparent color index
            self.PutByte(0)     # block terminator

            # output image desriptor
            self.PutByte(0x2c)  # image separator
            self.PutWord(0)     # image position x,y = 0,0
            self.PutWord(0)
            self.PutWord(256)   # image size
            self.PutWord(192)
            # packed fields
            # no Local Colour Table if first frame, othewise 4 bit LCT
            self.PutByte(0 if bFirst else 0x83)

            # output colour map if not first
            if(not bFirst):
                for i in _COLOUR_MAP:
                    self.PutByte((_ZXCOLOURTORGB[i] >> 16) & 0XFF)
                    self.PutByte((_ZXCOLOURTORGB[i] >> 8) & 0XFF)
                    self.PutByte(_ZXCOLOURTORGB[i] & 0XFF)

            # record initial code bit size
            self.PutByte(4)

            # output compressed image
            # add 1 to code size to accomodate control codes
            self.compress(not bFirst or delay == -2, 5)

            # write block terminator
            self.PutByte(0)

        def compress(self, bFlash, initialDataBitSize):
            """compress image to output stream using LZW compression"""

            # initiate bit cue & byte cue
            self.cue = [0]*255
            self.output_cue = 0
            self.output_cueBits = 0
            self.output_dataSize = initialDataBitSize
            self.output_cuePointer = 0

            # initiate compression stuff
            code_tableReset = 1 << (initialDataBitSize-1)
            code_EOF = code_tableReset + 1
            incBitsAt = (1 << initialDataBitSize) + 1
            compressionArray = [0]*(self.MaxOutputCode + 1)
            compressionArraySize = code_EOF + 1
            for i in range(code_EOF):
                compressionArray[i] = i | 0xFFFF000

            # start by issuing table reset code
            self.OutputBits(code_tableReset)
            # set no previous sequence
            CompressionValue = 0
            # get first pixel
            OldCompressionValue = self.GetPixelColour(0, 0, bFlash)
            # set where to start looking for sequence to see if we've
            # encountered it before
            # Code_EOF+1 will be first code not used by control code or
            # basic colours
            SearchPoint = code_EOF + 1

            # now go through image compressing pixels
            # start with x=1 on first line of y
            startx = 1
            for y in range(192):
                for x in range(startx, 256):
                    # calculate internal code for sequence+next pixel
                    CompressionValue = (OldCompressionValue << 12) | \
                                       self.GetPixelColour(x, y, bFlash)
                    # search list of sequences to see if current
                    # sequence already exists
                    i = SearchPoint
                    while(i < compressionArraySize):
                        if(compressionArray[i] == CompressionValue):
                            break

                        i += 1

                    # if sequence already exists, then remember loop
                    # back to look for longer sequence
                    if(i < compressionArraySize):
                        # longer matching sequence will come later in
                        # sequence table if exists so no point searching
                        # first part of sequence table again.  Setting
                        # Search Point avoids this.
                        OldCompressionValue = i
                        SearchPoint = i
                        continue

                    # have found a new pixel sequence, so add it to the
                    # list of sequences
                    compressionArray[compressionArraySize] = CompressionValue
                    compressionArraySize += 1
                    # reset where to search sequence table from as will
                    # be starting a new sequence now
                    SearchPoint = code_EOF + 1
                    # output existing sequence
                    self.OutputBits(OldCompressionValue)
                    # start new sequence with first pixel that doesn't
                    # match existing pixel sequence
                    OldCompressionValue = CompressionValue & 0xFFF
                    # check if have reached maximum number of sequences
                    # possible
                    if(compressionArraySize == self.MaxOutputCode):
                        # if so then output code to note table reset
                        self.OutputBits(code_tableReset)
                        # reset sequence table
                        compressionArraySize = code_EOF + 1
                        # reset output code bit size as will be shorter
                        # code for sequences
                        self.output_dataSize = initialDataBitSize
                        # work out when will need to increase output
                        # code bit size
                        incBitsAt = (1 << initialDataBitSize) + 1

                    # if we have to have more bits in output code to
                    # hold sequence code then increment output bits and
                    # make note of when to increase the number of output
                    # bits again
                    if(compressionArraySize == incBitsAt):
                        self.output_dataSize += 1
                        incBitsAt = (1 << self.output_dataSize) + 1

                startx = 0

            # finished going through image.
            # There will be sequence still left in output buffer so
            # output this
            self.OutputBits(OldCompressionValue & 0xFFF)
            # output end of file code
            self.OutputBits(code_EOF)
            # if there are bits waiting to be written int the output cue
            # write them now
            while(self.output_cueBits > 0):
                self.cue[self.output_cuePointer] = self.output_cue & 0xFF
                self.output_cuePointer += 1
                # if cue full, then output it
                if(self.output_cuePointer == 255):
                    self.out += [0xFF]
                    self.out += self.cue
                    self.output_cuePointer = 0

                self.output_cue >>= 8
                self.output_cueBits -= 8

            # if still bits in cue
            if(self.output_cuePointer > 0):
                self.out += [self.output_cuePointer]
                self.out += self.cue[0:self.output_cuePointer]

        def GetPixelColour(self, x, y, bFlash):
            """
            get colour 1-15 of specified pixel, inverted if is flashing.
            """
            colour = self.data[0x1800 + ((y >> 3) << 5) + (x >> 3)]
            fg = _COLOUR_MAP[(colour & 7) + ((colour >> 3) & 8)]
            bg = _COLOUR_MAP[(colour >> 3) & 15]

            # swap foreground & background if flash & second image
            if(colour >= 128 and bFlash):
                fg, bg = bg, fg

            pixels = self.data[((y >> 6) << 11) + ((y & 7) << 8) +
                               (((y >> 3) & 7) << 5) + (x >> 3)]

            return fg if ((pixels >> (7-(x & 7))) & 1) == 1 else bg

        # output bits to bit output cue
        def OutputBits(self, bits):
            # tidy bitcue in case loose bits attached (not sure if this
            # is strictly needed but is safe)
            self.output_cue &= self.output_masks[self.output_cueBits]
            # add new bits to bitcue
            if(self.output_cueBits > 0):
                self.output_cue |= bits << self.output_cueBits

            # no bitcue so set bitcue as bits to add
            else:
                self.output_cue = bits

            # update how many bits in bitcue
            self.output_cueBits += self.output_dataSize
            # if more than 8 bits in bitcue, output a byte at a time
            while(self.output_cueBits >= 8):
                # add from bitcue to byte cue
                self.cue[self.output_cuePointer] = self.output_cue & 0xFF
                # increment number of bytes in byte cue
                self.output_cuePointer += 1
                # if buffer full, output them to stream
                if(self.output_cuePointer == 255):
                    # block headder
                    self.out += [0xFF]
                    # output cue
                    self.out += self.cue
                    # reset byte cue pointer
                    self.output_cuePointer = 0

                # 8 bits have been moved from bit cue to byte cue.
                # Update bitcue & bitcue length
                self.output_cue >>= 8
                self.output_cueBits -= 8

        # output 2 byte word
        def PutWord(self, w):
            self.out += [w & 0xff, (w >> 8) & 0xff]

        # output string
        def PutString(self, s):
            self.out += [ord(x) for x in s]

        # output single byte
        def PutByte(self, b):
            self.out += [b]

    # end of private class

    # if not enough data for image supplied
    if(len(data) < 6912):
        return None

    # validate and convert data from string to bytearray if needed
    data = _validateandpreparebytes(data, "data")

    # is there a flash atribute in the screen
    bFlash = False

    # is there a flash flag set in the colour area?
    i = 0x1800
    while(i < 0x1B00):
        if(data[i] >= 0x80):
            bFlash = True
            break

        i += 1

    # create object to encode gif data
    ges = _gif_encoder_stream(data)

    # put headder
    ges.PutString("GIF89a")
    # width
    ges.PutWord(256)
    # height
    ges.PutWord(192)
    # bits per pixel+other flags
    ges.PutByte(243)
    ges.PutByte(0)
    ges.PutByte(0)

    # output colour map
    for i in _COLOUR_MAP:
        ges.PutByte((_ZXCOLOURTORGB[i] >> 16) & 0XFF)
        ges.PutByte((_ZXCOLOURTORGB[i] >> 8) & 0XFF)
        ges.PutByte(_ZXCOLOURTORGB[i] & 0XFF)

    # put delay if have flash & want flashing image (delay != -1 and -2)
    if(bFlash and delay > 0):
        ges.PutByte(0x21)  # extension introducer
        ges.PutByte(0xff)  # app extension label
        ges.PutByte(11)    # block size
        ges.PutString("NETSCAPE2.0")   # app id + auth code
        ges.PutByte(3)     # sub-block size
        ges.PutByte(1)     # loop sub-block id
        ges.PutWord(0)     # loop count (0=repeat forever)
        ges.PutByte(0)     # block terminator

    # output Image
    ges.PutImageAsGif(bFlash, delay, True)
    # output 2nd image if apropriate
    if(bFlash and delay != -1):
        ges.PutImageAsGif(bFlash, delay, False)

    # gif trailer
    ges.PutByte(0x3b)

    return bytearray(ges.out)


def getrgbfromscreen(data, alphamask=0xFF, imageformat=0):
    """This function extracts an Image from spectrum screen format data.

    data must be a list or tuple of ints or longs, or a byte string in
    python 2, or a bytes or bytearray object.

    This returns a 2 element list.  Because of flashing colours in the
    spectrum, there are efectively 2 images: one for each of the 2
    flashing colour states.  Image 0 is the normal Image.  If there are
    no flashing colours in the image, then the second element in the
    returned list is None, otherwise it is the image with the flashing
    colours inverted.

    The images are 256 pixels wide, and 192 pixels high, starting at
    the top left so any pixel can be extracted with by useing
    image[x+y*256].

    The alphamask variable sets what you want the alpha component to be.
    It should be a number from 0 to 255.  Set it to be -1 if you don't
    want an alpha component.

    imageformat specifies what format you want the image to be output
    as.  0 for a list of ARGB integers (bits 24-31 are alpha if wanted,
    bits 16-23 are red, 8-15 are green, and 0-7 are Blue), or 1 for a
    list of lists containing [Red, Green, Blue, Alpha] (or [Red, Green,
    Blue] if alpha isn't wanted).
    """

    # validate inputs
    if(imageformat < 0 or imageformat > 1):
        raise SpectrumTranslateError("Invalid imageformat.")

    if(alphamask < -1 or alphamask > 255):
        raise SpectrumTranslateError("Invalid alphamask.")

    # validate and convert data from string to bytearray if needed
    data = _validateandpreparebytes(data, "data")

    if(imageformat == 0):
        alpha = 0 if alphamask == -1 else alphamask << 24
        colourtransform = _ZXCOLOURTORGB
    else:
        alpha = [] if alphamask == -1 else [alphamask]
        colourtransform = _ZXCOLOURTORGBLIST

    # calculate number of images needed: is there a flash flag set in
    # the colour area?
    bFlash = False
    i = 0x1800
    while(i < 0x1B00):
        if(data[i] >= 0x80):
            bFlash = True
            break

        i += 1

    image1 = []
    for y in range(192):
        # get pixel address for start of row
        p = ((y >> 6) << 11) + ((y & 7) << 8) + (((y >> 3) & 7) << 5)
        # get colour address for start of row
        c = 0x1800 + ((y >> 3) << 5)
        for x in range(0, 256, 8):
            # work out foreground & background colour
            i = data[c]
            fg = colourtransform[(i & 7) + ((i >> 3) & 8)] + alpha
            bg = colourtransform[(i >> 3) & 15] + alpha
            # get pixel data for 8 pixel row
            i = data[p]
            image1 += [bg if (i & 128) == 0 else fg,
                       bg if (i & 64) == 0 else fg,
                       bg if (i & 32) == 0 else fg,
                       bg if (i & 16) == 0 else fg,
                       bg if (i & 8) == 0 else fg,
                       bg if (i & 4) == 0 else fg,
                       bg if (i & 2) == 0 else fg,
                       bg if (i & 1) == 0 else fg]
            c += 1
            p += 1

    # now deal with flash image if needed
    if(bFlash):
        image2 = []
        for y in range(192):
            # get pixel address for start of row
            p = ((y >> 6) << 11) + ((y & 7) << 8) + (((y >> 3) & 7) << 5)
            # get colour address for start of row
            c = 0x1800 + ((y >> 3) << 5)
            for x in range(0, 256, 8):
                # work out foreground & background colour
                i = data[c]
                fg = colourtransform[(i & 7) + ((i >> 3) & 8)] + alpha
                bg = colourtransform[(i >> 3) & 15] + alpha
                if(i >= 128):
                    # swap foreground & background as flashing
                    fg, bg = bg, fg

                # get pixel data for 8 pixel row
                i = data[p]
                image2 += [bg if (i & 128) == 0 else fg,
                           bg if (i & 64) == 0 else fg,
                           bg if (i & 32) == 0 else fg,
                           bg if (i & 16) == 0 else fg,
                           bg if (i & 8) == 0 else fg,
                           bg if (i & 4) == 0 else fg,
                           bg if (i & 2) == 0 else fg,
                           bg if (i & 1) == 0 else fg]
                c += 1
                p += 1

        # return 2 images
        return [image1, image2]

    # return only one image as no flash
    return [image1, None]


def snaptosna(data, register, border=0):
    """Function to convert data of +D/Disciple format snapshot to .SNA
    format byte string that can be saved.

    Register is a dictionary of the various registers.  A,F,BC,DE,HL,I,
    R,IX,IY,SP,PC,A',F',BC',DE',HL',IFF2 (the interupt state), and IM
    (the interupt mode) are all required.  RAMbank is required in any
    128K snapshot.

    The type of snapshot is determined by the size of data which is the
    memory of the snapshot.  For 48K images it should be 49152 bytes
    (memory address 0x4000 to 0xFFFF inclusive).  For 128K it has to be
    131072 bytes (the 16K ram pages in order 0 to 7).

    border is the border colour.

    data must be a list or tuple of ints or longs, or a byte string in
    python 2, or a bytes or bytearray object.
    """

    # first check have valid data
    # return if not 48k or 128K
    if(len(data) != 49152 and len(data) != 131072):
        raise SpectrumTranslateError("Wrong size memory")

    # validate and convert data to bytearray if needed
    data = _validateandpreparebytes(data, "data")

    # output common headder registers
    out = [register["I"] & 0xFF,
           register["HL'"] & 0xFF, (register["HL'"] >> 8) & 0xFF,
           register["DE'"] & 0xFF, (register["DE'"] >> 8) & 0xFF,
           register["BC'"] & 0xFF, (register["BC'"] >> 8) & 0xFF,
           register["F'"] & 0xFF,
           register["A'"] & 0xFF,
           register["HL"] & 0xFF, (register["HL"] >> 8) & 0xFF,
           register["DE"] & 0xFF, (register["DE"] >> 8) & 0xFF,
           register["BC"] & 0xFF, (register["BC"] >> 8) & 0xFF,
           register["IY"] & 0xFF, (register["IY"] >> 8) & 0xFF,
           register["IX"] & 0xFF, (register["IX"] >> 8) & 0xFF,
           4 if register["IFF2"] == 1 else 0,
           register["R"] & 0xFF,
           register["F"] & 0xFF,
           register["A"] & 0xFF,
           register["SP"] & 0xFF, (register["SP"] >> 8) & 0xFF,
           register["IM"] & 0xFF,
           border & 7]

    # if 48K then add memory dump & return
    if(len(data) == 49152):
        # Program Counter needs to be on the stack so can't simply dump
        # memory contents
        # calculate where SP offset is in data
        SPoffset = SP-0x4000
        # first save off the data before the stack pointer
        out += data[0:SPoffset]
        # output program counter
        out += [PC & 0xFF, (PC >> 8) & 0xFF]
        # save off data after stack pointer+2
        # +2 to skip 2 bytes taken up by PC
        out += data[SPoffset+2:]
        # return snapshot as byte array string
        return ''.join([chr(c) for c in out])

    # should be 128K snapshots only now

    # output ram bank 5
    out += data[5*16384:6*16384]
    # output ram bank 2
    out += data[2*16384:3*16384]
    # check if valid bank
    if(register["RAMbank"] < 0 or register["RAMbank"] > 7):
        raise SpectrumTranslateError("RAMbank has to be 0 to 7 inclusive.")

    # output currently paged ram bank
    out += data[register["RAMbank"]*16384:(register["RAMbank"] + 1)*16384]

    # output program counter
    out += [PC & 0xFF, (PC >> 8) & 0xFF]
    # output port 7FFD setting
    out += [register["RAMbank"] +
            (8 if regs["Screen"] == 1 else 0) +
            (16 if regs["ROM"] == 1 else 0) +
            (32 if regs["IgnorePageChange"] == 1 else 0)]
    # output 0 as TR-DOS ROM is not paged in
    out += [0]

    # now output remaining RAM banks
    for i in range(8):
        # check if RAM bank already output
        if(i == 2 or i == 5 or i == register["RAMbank"]):
            continue

        # otherwise output RAM bank
        out += data[i * 16384:(i + 1) * 16384]

    return bytearray(out)


def snaptoz80(data, register, version=3, compressed=True, border=0):
    """Function to convert data of +D/Disciple format snapshot to .Z80
    format byte string that can be saved.

    data must be a list or tuple of ints or longs, or a byte string in
    python 2, or a bytes or bytearray object.

    Register is a dictionary of the various registers.  A,F,BC,DE,HL,I,
    R,IX,IY,SP,PC,A',F',BC',DE',HL',IFF2 (the interupt state), and IM
    (the interupt mode) are all required.  RAMbank is required in any
    128K snapshot.  IFF1 is optional.  Screen is optional and is 1 if
    screen in RAM bank 7 is being displayed otherwise the screen in RAM
    bank 5 is displayed.  ROM is optional and is 1 if 48K ROM is paged
    in a 128K machine, or 0 if the 128K ROM is paged in at 0x0000.  This
    defaults to 1.  IgnorePageChange is optional and is 1 if 0x7FFD is
    locked until hard reset and defaults to 0.

    The type of snapshot is determined by the size of data which is the
    memory of the snapshot.  For 48K images it should be 49152 bytes
    (memory address 0x4000 to 0xFFFF inclusive).  For 128K it has to be
    131072 bytes (the 16K rampages in order 0 to 7).

    border is the border colour.

    compressed is if you want compression in your file.

    version is the Z80 file format version (defaults to 3)
    """

    # nested function to compress memory
    def compress(mem, wantblockterminator=False):
        out = []
        i = 0

        # loop through memory stopping 4 bytes before end
        while(i < len(mem) - 4):
            x = mem[i]
            # check for runs of 5 or more bytes, or 2 or more if ED
            if((x == mem[i+1] and x == mem[i+2] and x == mem[i+3] and
                x == mem[i+4]) or
               (x == 0xED and mem[i+1] == 0xED)):
                c = 0
                while(i < len(mem) and x == mem[i]):
                    c += 1
                    i += 1

                out += [0xED, 0xED, c, x]

            elif(x == 0xED):
                out += [0xED, mem[i+1]]
                i += 2

            else:
                out += [x]
                i += 1

        if(i < len(mem)):
            out += mem[i:]

        if(wantblockterminator):
            out += [0, 0xED, 0xED, 0]

        return out

    # first check have valid data
    # return if not 48k or 128K
    if(len(data) != 49152 and len(data) != 131072):
        raise SpectrumTranslateError("Wrong size memory")

    # version 1 can only handle 48K snapshots
    if(version == 1 and len(data) != 49152):
        raise SpectrumTranslateError(
            "version 1 of Z80 format can't handle 128K snapshots.")

    # ensure we have valid version
    if(version != 1 and version != 2 and version != 3):
        raise SpectrumTranslateError(
            "Valid version numbers for Z80 files are 1, 2, and 3.")

    # validate and convert data to bytearray if needed
    data = _validateandpreparebytes(data)

    # save off basic registers in 30 byte headder
    out = [register["A"],
           register["F"],
           register["BC"] & 0xFF, (register["BC"] >> 8) & 0xFF,
           register["HL"] & 0xFF, (register["HL"] >> 8) & 0xFF,
           0 if version > 1 else register["PC"] & 0xFF,
           0 if version > 1 else (register["PC"] >> 8) & 0xFF,
           register["SP"] & 0xFF, (register["SP"] >> 8) & 0xFF,
           register["I"],
           register["R"],
           ((register["R"] >> 7) & 1) + ((border & 7) << 1) +
           32 if compressed else 0,
           register["DE"] & 0xFF, (register["DE"] >> 8) & 0xFF,
           register["BC'"] & 0xFF, (register["BC'"] >> 8) & 0xFF,
           register["DE'"] & 0xFF, (register["DE'"] >> 8) & 0xFF,
           register["HL'"] & 0xFF, (register["HL'"] >> 8) & 0xFF,
           register["A'"],
           register["F'"],
           register["IY"] & 0xFF, (register["IY"] >> 8) & 0xFF,
           register["IX"] & 0xFF, (register["IX"] >> 8) & 0xFF,
           register["IFF2"] if "IFF1" not in register else register["IFF1"],
           register["IFF2"],
           register["IM"] & 3]

    if(version == 1):
        # add memory
        if(compressed):
            out += compress(data, True)

        else:
            out += data

        # return as byte array
        return ''.join([chr(x) for x in out])

    # now version 2 or 3
    out += [23 if version == 2 else 54, 0]
    out += [register["PC"] & 0xFF, (register["PC"] >> 8) & 0xFF]
    # hardware: will be 48K/128K in V2, otherwise 48K+MGT/128K+MGT in V3
    out += [(0 if len(data) == 49152 else 3) + (0 if version == 2 else 3)]
    out += [register["RAMbank"] +
            (8 if "Screen" in register and register["Screen"] == 1 else 0) +
            (0 if "ROM" in register and register["ROM"] == 0 else 16) +
            (32 if "IgnorePageChange" in register and
            register["IgnorePageChange"] == 1 else 0)]
    out += [0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    if(version == 3):
        out += [0]*28
        out += [16, 0, 0]

    # handle 48K data
    if(len(data) == 49152):
        # move through pages
        for page, address in ((8, 0), (4, 0x4000), (5, 0x8000)):
            if(compressed):
                compdat = compress(data[address:address + 0x3FFF])
                out += [len(compdat) & 0xFF, (len(compdat) >> 8) & 0xFF,
                        page] + compdat

            else:
                out += [0xFF, 0xFF, page] + data[address:address + 0x3FFF]

    # handle 128K
    else:
        # move through pages
        for page in range(8):
            if(compressed):
                compdat = compress(data[page*0x4000:page*0x4000 + 0x3FFF])
                out += [len(compdat) & 0xFF, (len(compdat) >> 8) & 0xFF,
                        page + 3] + compdat

            else:
                out += [0xFF, 0xFF, page + 3] + \
                       data[page*0x4000:page*0x4000 + 0x3FFF]

    return bytearray(out)


def disassemble(data, offset, origin, length, SpecialInstructions=None,
                progressfunction=None):
    """This function will disassemble a byte string or list holding Z80
    code.  You can specify instructions to alter the disassembled
    output.

    data must be a list or tuple of ints or longs, or a byte string in
    python 2, or a bytes or bytearray object.
    offset is how far into the array to start disassembling.
    origin is the address of the first byte in the byte array.
    length is how many bytes to disassemble
    SpecialInstructions is a list of DisassembleInstruction instructing
    things like output format, and data blocks.  Should be None if no
    array to pass.
    progressfunction is a function that takes X arguments. The first is
    a string detailing what the Disassembler is currently doing.  The
    second is how far through the current section of work it is, and
    the third is how much work there is in the current section.  To get
    a percentage of how much work in the current section use argument2
    / argument3 * 100. The fourth argument gives the overall work done,
    and the fifth argument the overall work to do. Note that the work
    done can change, and the total work to do can increase as the
    disassembly progresses, but the ratio (and thus the percentage work
    done) will never decrease.

    Returns a String representation of the data.
    """

    # nested functions

    # get string for used flags
    def getFlagChanges(instructionData):
        # do we have flag data?
        if(((instructionData >> 20) & 1) == 0):
            # if not return None
            return None

        # holds flag indicators
        FlagStates = ("?", "-", "+", "0", "1", "P", "V")

        s = "S{0} Z{1} H{2} PV{3} N{4} C{5}".format(
            FlagStates[(instructionData >> 17) & 7],
            FlagStates[(instructionData >> 14) & 7],
            FlagStates[(instructionData >> 11) & 7],
            FlagStates[(instructionData >> 8) & 7],
            FlagStates[(instructionData >> 5) & 7],
            FlagStates[(instructionData >> 2) & 7])

        return s

    # extract timing information
    def GetTimingInfo(instructionTimes):
        # calculate times
        # first clear variables where results will be calculated
        duration = [0, 0]
        states = None

        # if only overall T length known then extract this now
        if((instructionTimes & 0x1) != 0):
            duration = [(instructionTimes >> 1) & 0x7FFF,
                        (instructionTimes >> 17) & 0x7FFF]

        # otherwise individual component parts of time known
        else:
            states = [[], []]
            # get number of T states
            k = (instructionTimes >> 1) & 7
            # offset
            i = 4
            while(k > 0):
                t = ((instructionTimes >> i) & 3) + 3
                states[0].append(t)
                duration[0] += t
                i += 2
                k -= 1

            # do alternative length if exists
            k = (instructionTimes >> 16) & 7
            i = 19
            while(k > 0):
                t = ((instructionTimes >> i) & 3) + 3
                states[1].append(t)
                duration[1] += t
                i += 2
                k -= 1

        return duration, states

    def CommentOutput(comment, XMLOutput):
        if(XMLOutput == 1):
            return "  <line><comment>" + comment + "</comment></line>"
        else:
            linestart = "\0" + chr(12) + chr(0) + "0000" + Seperator + ";"
            return "\n".join([linestart + txt for txt in comment.split("\n")])

    # end nested functions

    # holds how long address is in each number format
    FormatAddressLength = (4, 5, 7, 17)
    # holds how long byte is in each number format
    FormatByteLength = (2, 3, 3, 8)
    # holds max length of opcode for each number format
    FormatOpCodeMaxLength = (19, 20, 21, 27)

    maxAddressLength = 0

    # work out where we are
    currentAddress = origin + offset

    # validate and convert data to bytearray if needed
    data = _validateandpreparebytes(data, "data")

    # get list of line numbers that are being referenced
    ReferencedLineNumbers = [currentAddress]

    # set format flags to default
    AddressOutput = 0        # 0=hex,1=decimal,2=octal,3=binary
    NumberOutput = 0         # 0=hex,1=decimal,2=octal,3=binary
    CommandOutput = 0        # 0=hex,1=decimal,2=octal,3=binary
    # 0=no, 1=total only, 2=list state times, 3=total & state times
    OutputTStates = 0
    # 0=no empty lines, 1=after absolute jumps/rets, 2=after all rets/jumps
    BreakAfterJumps = 1
    LineNumberOutput = 0     # 0=All, 1=None, 2=only referenced lines
    # list every X lines regardless of LineNumberOutput
    ListEveryXLines = 0
    # 0=empty line after data, 1=no empty line after data
    BreakAfterData = 0
    # 0=track line numbers for display purposes, 1=don't
    TreatDataNumbersAsLineReferences = 0
    DisplayCommandBytes = 0  # 0=print them, 1=don't
    DisplayComments = 0      # 0=display them, 1=don't
    Seperator = "  "
    ShowFlags = 0            # 0=no, 1=yes
    MarkUndocumenedCommand = 0  # 0=no, 1=yes
    XMLOutput = 0            # 0=no, 1=yes
    HexForNonASCII = 0       # 0=no, 1=yes
    CommentEnd = ""
    CommentAfter = ""
    CommentReferences = []
    FunctionMatcher = re.compile("^\s*%![a-zA-Z_][a-zA-Z_0-9]*[(].*[)]\s*$",
                                 re.DOTALL)
    MatcherinBraces = re.compile(
        "^\s*%[(]\s*%!([a-zA-Z_][a-zA-Z_0-9]*[(].*[)])\s*%[)](\s*%#[^\n]*?)?$",
        re.DOTALL)

    # Work out how much there is to process for progress callback
    # faster going through formatting at end than actual disassembling
    # assume that phase 1 where process instructions will take 10%
    # this may be wrong but good average: simple instructions will take
    # less and complex will take longer.
    worktodo1 = 0           # default no work pre-processing
    worktodo2 = length * 2  # *2 for disassembling
    worktodo3 = length      # for formatting
    workdone = 0
    # now look at special instructions as this can increase workload
    if(SpecialInstructions is not None and len(SpecialInstructions) > 0):
        for di in SpecialInstructions:
            worktodo1 += 1
            if(di.instruction == DisassembleInstruction.DISASSEMBLE_CODES[
                    "Pattern Data Block"] or
               di.instruction == DisassembleInstruction.DISASSEMBLE_CODES[
                    "Comment Pattern"]):
                # work out start and end points
                e = di.end
                if(e >= origin + len(data)):
                    e = origin + len(data)-1
                s = di.start
                if(s < origin):
                    s = origin
                # must process once before disassembly
                worktodo1 += (e - s) * 2

    # process special instructions
    DisassembleInstructions = []
    if(SpecialInstructions is not None and len(SpecialInstructions) > 0):
        for di in SpecialInstructions:
            # update progress
            workdone += 1
            # call progress update
            if(progressfunction is not None):
                progressfunction("Evaluating Instructions",
                                 workdone, worktodo1,
                                 (workdone * 10) / worktodo1, 100)

            # check if special formatting commands for default for whole
            # output
            if(di.start == 0x0000 and di.end >= 0xFFFF):
                if(di.instruction & 0xFFFF00 == 0x000100):
                    # AddressOutputFormat
                    AddressOutput = di.instruction & 0x03
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000200):
                    # NumberOutputFormat
                    NumberOutput = di.instruction & 0x03
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000300):
                    # CommandOutputFormat
                    CommandOutput = di.instruction & 0x03
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000400):
                    # OutputTStatesFormat
                    OutputTStates = di.instruction & 0x03
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000500):
                    # LineAfterJumpOutputFormat
                    BreakAfterJumps = di.instruction & 0x03
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000600):
                    # DefaultFormat
                    AddressOutput = di.instruction & 0x03
                    NumberOutput = di.instruction & 0x03
                    CommandOutput = di.instruction & 0x03
                    OutputTStates = 0
                    BreakAfterJumps = 1
                    LineNumberOutput = 0
                    ListEveryXLines = 0
                    BreakAfterData = 0
                    TreatDataNumbersAsLineReferences = 0
                    DisplayCommandBytes = 0
                    DisplayComments = 0
                    Seperator = "  "
                    ShowFlags = 0
                    MarkUndocumenedCommand = 0
                    XMLOutput = 0
                    HexForNonASCII = 0
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000700):
                    # CustomFormat
                    settingstemp = get_custom_format_values(di.data, False)
                    AddressOutput = settingstemp["AddressOutput"]
                    NumberOutput = settingstemp["NumberOutput"]
                    CommandOutput = settingstemp["CommandOutput"]
                    OutputTStates = settingstemp["OutputTStates"]
                    BreakAfterJumps = settingstemp["BreakAfterJumps"]
                    LineNumberOutput = settingstemp["LineNumberOutput"]
                    ListEveryXLines = settingstemp["ListEveryXLines"]
                    BreakAfterData = settingstemp["BreakAfterData"]
                    TreatDataNumbersAsLineReferences = settingstemp[
                        "TreatDataNumbersAsLineReferences"]
                    DisplayCommandBytes = settingstemp["DisplayCommandBytes"]
                    DisplayComments = settingstemp["DisplayComments"]
                    Seperator = settingstemp["Seperator"]
                    ShowFlags = settingstemp["ShowFlags"]
                    MarkUndocumenedCommand = settingstemp[
                        "MarkUndocumenedCommand"]
                    XMLOutput = settingstemp["XMLOutput"]
                    HexForNonASCII = settingstemp["HexForNonASCII"]
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000800):
                    # LineNumberOutput
                    LineNumberOutput = di.instruction & 0x03
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000900):
                    # ListEveryXLines
                    ListEveryXLines = int(di.data, 16)
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000A00):
                    # BreakAfterData
                    BreakAfterData = di.instruction & 0x01
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000B00):
                    # TreatDataNumbersAsLineReferences
                    TreatDataNumbersAsLineReferences = di.instruction & 0x01
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000C00):
                    # DisplayCommandBytes
                    DisplayCommandBytes = di.instruction & 0x01
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000D00):
                    # DisplayComments
                    DisplayComments = di.instruction & 0x01
                    continue

                elif(di.instruction & 0xFFFFFF == 0x000E00):
                    # Seperator space
                    Seperator = "  "
                    continue

                elif(di.instruction & 0xFFFFFF == 0x000E01):
                    # Seperator tab
                    Seperator = "\t"
                    continue

                elif(di.instruction & 0xFFFFFF == 0x000E02):
                    # Seperator custom
                    Seperator = di.data
                    continue

                elif(di.instruction & 0xFFFF00 == 0x000F00):
                    # Display flags
                    ShowFlags = di.instruction & 0x01
                    continue

                elif(di.instruction & 0xFFFF00 == 0x001000):
                    # note undocumened commands
                    MarkUndocumenedCommand = di.instruction & 0x01
                    continue

                elif(di.instruction & 0xFFFF00 == 0x001200):
                    # XML mode
                    XMLOutput = di.instruction & 0x01
                    continue

                elif(di.instruction & 0xFFFF00 == 0x001300):
                    # HexForNonASCII mode
                    HexForNonASCII = di.instruction & 0x01
                    continue

            # check if end after end of code, in which case truncate it
            if(di.end >= origin + len(data)):
                di.end = origin + len(data)-1

            # check if start before start of code, but ends inside code,
            # in which case truncate it
            if(di.start < origin and di.end > origin):
                di.start = origin

            # is this a patterndatablock instruction or a find&comment
            if(di.instruction == DisassembleInstruction.DISASSEMBLE_CODES[
                    "Pattern Data Block"] or
               di.instruction == DisassembleInstruction.DISASSEMBLE_CODES[
                    "Comment Pattern"]):
                # get parts of patterndatablock
                TestBlock, PrepBlock, ActionBlock = getpartsofpatterndatablock(
                    di.data)

                # first check is valid test block
                if(TestBlock is None):
                    raise SpectrumTranslateError(
                        "patern to search for must be inside brackets")

                # now check is valid preperation block
                if(PrepBlock is None):
                    raise SpectrumTranslateError(
                        "preperation block must be inside brackets")

                # now should have valid pattern match we can work with

                # setup environment ready to search for matches
                Settings = {"DATASTRINGPOS": 0,
                            "NUMBERFORMAT": 0,
                            "NUMBERSIGNED": 0,
                            "NUMBERWORDORDER": 0,
                            "DISPLAYEVERYXLINES": 1,
                            "ORIGIONALSEPERATOR": Seperator,
                            "SEPERATOR": Seperator,
                            "ORIGIN": origin,
                            "ADDRESSOUTPUT": AddressOutput,
                            "NUMBEROUTPUT": NumberOutput,
                            "COMMANDOUTPUT": CommandOutput,
                            "XMLOutput": XMLOutput,
                            "HexForNonASCII": HexForNonASCII,
                            "InstructionsToAdd": []}

                Vars = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, di.start, 0, 0, di.start,
                        di.end]

                # work done after done this
                wdafter = workdone + ((di.end - di.start) * 2)

                matches = []
                # handle predefined routine
                match = MatcherinBraces.match(TestBlock)
                if(match):
                    if(progressfunction is not None):
                        progressfunction("Evaluating Instructions", workdone,
                                         worktodo1,
                                         (workdone * 10) / worktodo1, 100)
                    details = _ProcessFunctionDetails(match.group(1))
                    if(isinstance(details, str)):
                        raise SpectrumTranslateError(details)

                    # check is valid command
                    if(details[0] not in
                       DisassembleInstruction.PredefinedRoutines):
                        raise SpectrumTranslateError(
                            'Routine "{0}" not defined'.format(details[0]))

                    # process routine
                    Vars = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, di.start, 0, 0,
                            di.start, di.end]
                    args = [data, Settings, Vars] + details[1]
                    keyargs = details[2]
                    matches = DisassembleInstruction.\
                        PredefinedRoutines[details[0]](*args, **keyargs)
                else:
                    # search for matches using scripting language

                    # move through area covered by instruction & check for
                    # matches
                    k = di.start
                    while(k <= di.end):
                        # update progress
                        workdone += 2
                        # call progress update
                        if(progressfunction is not None):
                            progressfunction("Evaluating Instructions",
                                             workdone, worktodo1,
                                             (workdone * 10) / worktodo1, 100)
                        try:
                            Settings["DATASTRINGPOS"] = 0
                            Vars[0x00] = k
                            Vars[0x01] = di.end
                            Vars[0x0C] = 0
                            Vars[0x0A] = k
                            Vars[0x0D] = k
                            Vars[0x0E] = di.end
                            # test each address
                            # will fail for Comment pattern but only after
                            # pattern has been added
                            if((_processcommandblock(TestBlock, Vars, Settings,
                                                     data, True,
                                                     True)[0] & 1) == 1):
                                matches += [k]
                            k += 1

                        except IndexError:
                            # continue gracefully if test involves bytes
                            # outside supplied data.
                            continue

                blockdetails = []
                # process matches if needed
                match = MatcherinBraces.match(PrepBlock)
                if(len(matches) > 0 and isinstance(matches[0], list)):
                    # matching routine has returned list of blockdetails
                    blockdetails = matches
                elif(len(matches) > 0 and match):
                    details = _ProcessFunctionDetails(match.group(1))
                    if(isinstance(details, str)):
                        raise SpectrumTranslateError(details)

                    # check is valid command
                    if(details[0] not in
                       DisassembleInstruction.PredefinedRoutines):
                        raise SpectrumTranslateError(
                            'Routine "{0}" not defined'.format(details[0]))

                    # process routine
                    Vars = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, di.start, 0, 0,
                            di.start, di.end]
                    args = [data, Settings, Vars, matches] + details[1]
                    keyargs = details[2]
                    blockdetails = DisassembleInstruction.\
                        PredefinedRoutines[details[0]](*args, **keyargs)
                elif(len(matches) > 0):
                    # process matches using scripting
                    for k in matches:
                        try:
                            Settings["DATASTRINGPOS"] = 0
                            Vars[0x00] = k
                            Vars[0x01] = di.end
                            Vars[0x0C] = 0
                            Vars[0x0A] = k
                            Vars[0x0D] = k
                            Vars[0x0E] = di.end
                            # now adjust variables as needed
                            _processcommandblock(PrepBlock, Vars, Settings,
                                                 data, True, False)
                            blockdetails += [[Vars[0x00], Vars[0x01]]]
                        except IndexError:
                            # continue gracefully if test involves bytes
                            # outside supplied data.
                            continue

                # add data blocks
                for start, end in blockdetails:
                    # add datablock
                    DisassembleInstructions += [DisassembleInstruction(
                        DisassembleInstruction.DISASSEMBLE_CODES["Data Block"],
                        start, end, ActionBlock)]

                    # increase work in disassembly phase for each block
                    worktodo2 += (end - start) * 2

                # if have instructions, add them
                if(len(Settings["InstructionsToAdd"]) > 0):
                    DisassembleInstructions += Settings["InstructionsToAdd"]

                workdone = wdafter

                continue

            # check if is reference instruction
            if(di.instruction == DisassembleInstruction.DISASSEMBLE_CODES[
                    "Reference Line"]):
                ReferencedLineNumbers += [di.start]
                continue

            if(di.instruction == DisassembleInstruction.DISASSEMBLE_CODES[
                    "Data Block"]):
                # increase work in disassembly phase
                worktodo2 += (di.end - di.start) * 2

            # add instruction to list of stuff to do during disassembly
            DisassembleInstructions += [di]

        # sort instructions by their start address
        DisassembleInstructions = sorted(DisassembleInstructions,
                                         key=attrgetter('start', 'end'))

    # should now be sorted along by start

    # adjust workdone to be 10% of total work to stop progress going
    # backwards with extra work in disassembly phase
    worktodo1 = (worktodo2 + worktodo3) / 9
    workdone = 0

    # set up format stack to hold current format
    # hold formatting instructions
    s = get_custom_format_string(AddressOutput, NumberOutput, CommandOutput,
                                 OutputTStates, BreakAfterJumps,
                                 LineNumberOutput, ListEveryXLines,
                                 BreakAfterData,
                                 TreatDataNumbersAsLineReferences,
                                 DisplayCommandBytes, DisplayComments,
                                 Seperator, ShowFlags, MarkUndocumenedCommand,
                                 XMLOutput, HexForNonASCII)
    Format = [DisassembleInstruction(DisassembleInstruction.DISASSEMBLE_CODES[
        "Custom Format"], 0, 65536, s)]
    CurrentFormatEnd = 65536  # end after

    # hold data formatting instructions
    nextDataFormatStart = 65536  # start after
    nextDataFormatEnd = 65536    # end after

    # output start text
    if(XMLOutput == 1):
        soutput = ['<?xml version="1.0" encoding="UTF-8" ?>', '<z80code>',
                   '  <org>' + _numbertostring(currentAddress, 16,
                                               AddressOutput) + '</org>']

    else:
        soutput = ['ORG ' + _numbertostring(currentAddress, 16, AddressOutput),
                   '']

    # start disassembling
    while(length > 0):
        # call progress update
        if(progressfunction is not None):
            progressfunction("Disassembling", workdone, worktodo2,
                             workdone + worktodo1,
                             worktodo1 + worktodo2 + worktodo3)

        # are we exiting format section?
        if(currentAddress > CurrentFormatEnd):
            # if so recover details of underlying format
            diTemp = Format.pop()
            settingstemp = get_custom_format_values(diTemp.data, False)
            AddressOutput = settingstemp["AddressOutput"]
            NumberOutput = settingstemp["NumberOutput"]
            CommandOutput = settingstemp["CommandOutput"]
            OutputTStates = settingstemp["OutputTStates"]
            BreakAfterJumps = settingstemp["BreakAfterJumps"]
            LineNumberOutput = settingstemp["LineNumberOutput"]
            ListEveryXLines = settingstemp["ListEveryXLines"]
            BreakAfterData = settingstemp["BreakAfterData"]
            TreatDataNumbersAsLineReferences = settingstemp[
                "TreatDataNumbersAsLineReferences"]
            DisplayCommandBytes = settingstemp["DisplayCommandBytes"]
            DisplayComments = settingstemp["DisplayComments"]
            Seperator = settingstemp["Seperator"]
            ShowFlags = settingstemp["ShowFlags"]
            MarkUndocumenedCommand = settingstemp["MarkUndocumenedCommand"]
            XMLOutput = settingstemp["XMLOutput"]
            HexForNonASCII = settingstemp["HexForNonASCII"]

            CurrentFormatEnd = diTemp.end
            continue

        # remove expired comment references
        if(CommentReferences and currentAddress >= CommentReferences[0].end):
            CommentReferences = [x for x in CommentReferences if
                                 x.end > currentAddress]

        # skip past instructions not relavent to code
        while(DisassembleInstructions and
              currentAddress > DisassembleInstructions[0].end):
            DisassembleInstructions.pop(0)
        # get instruction or set to None
        if(DisassembleInstructions and
           currentAddress >= DisassembleInstructions[0].start):
            di = DisassembleInstructions.pop(0)
        else:
            di = None

        # first check if in data block
        if(di is not None and
           di.instruction == DisassembleInstruction.DISASSEMBLE_CODES[
               "Data Block"]):
            Settings = {"DATASTRINGPOS": 0,
                        "NUMBERFORMAT": 0,
                        "NUMBERSIGNED": 0,
                        "NUMBERWORDORDER": 0,
                        "DISPLAYEVERYXLINES": 1,
                        "ORIGIONALSEPERATOR": Seperator,
                        "SEPERATOR": Seperator,
                        "ORIGIN": origin,
                        "ADDRESSOUTPUT": AddressOutput,
                        "NUMBEROUTPUT": NumberOutput,
                        "COMMANDOUTPUT": CommandOutput,
                        "XMLOutput": XMLOutput,
                        "HexForNonASCII": HexForNonASCII,
                        "COMMENTCONTROL": [DisassembleInstructions,
                                           DisplayComments, CommentEnd,
                                           CommentAfter, CommentOutput]}
            if(TreatDataNumbersAsLineReferences == 0):
                Settings["ReferencedLineNumbers"] = ReferencedLineNumbers

            if(FunctionMatcher.match(di.data)):
                details = _ProcessFunctionDetails(di.data.strip()[2:])
                if(isinstance(details, str)):
                    raise SpectrumTranslateError(details)

                # check is valid command
                if(details[0] not in
                   DisassembleInstruction.PredefinedRoutines):
                    raise SpectrumTranslateError(
                        'Routine "{0}" not defined'.format(details[0]))

                # process routine
                Vars = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, di.start, 0, 0, di.start,
                        di.end]
                args = [data, Settings, Vars] + details[1]
                keyargs = details[2]
                result = DisassembleInstruction.PredefinedRoutines[details[0]](
                    *args, **keyargs)
                # adjust end of data block
                di.end = Vars[10] - 1
                # extract text from result
                if(isinstance(result, (str, _unistr))):
                    txt = result
                elif(isinstance(result, list) and len(result) > 0 and
                     isinstance(result[0], (str, _unistr))):
                    txt = result[0]
                elif(isinstance(result, list) and len(result) > 1 and
                     isinstance(result[1], (str, _unistr))):
                    txt = result[1]
                else:
                    txt = ""
            else:
                di.end, txt = di.disassembledatablock(Settings, data)

            if(txt.endswith("\n")):
                txt = txt[:-1]
            soutput += txt.split("\n")

            # update comments
            CommentEnd = Settings["COMMENTCONTROL"][2]
            CommentAfter = Settings["COMMENTCONTROL"][3]

            # adjust length
            length -= di.end-currentAddress + 1

            # point to end of data block
            currentAddress = di.end + 1

            # adjust offset
            offset = currentAddress-origin

            # update work done
            workdone += (di.end - di.start) * 2

            # put empty line after data if needed
            if(("LINEAFTERDATA" in Settings and Settings["LINEAFTERDATA"]) or
               (BreakAfterData == 0 and "LINEAFTERDATA" not in Settings)):
                soutput += ['']

            continue

        # check formatting command
        if(di is not None and di.isformatinstruction()):
            # record current format state in custom, place on stack
            s = get_custom_format_string(AddressOutput, NumberOutput,
                                         CommandOutput, OutputTStates,
                                         BreakAfterJumps, LineNumberOutput,
                                         ListEveryXLines, BreakAfterData,
                                         TreatDataNumbersAsLineReferences,
                                         DisplayCommandBytes, DisplayComments,
                                         Seperator, ShowFlags,
                                         MarkUndocumenedCommand, XMLOutput,
                                         HexForNonASCII)
            Format += [DisassembleInstruction(
                DisassembleInstruction.DISASSEMBLE_CODES["Custom Format"],
                currentAddress, CurrentFormatEnd, s)]

            # deal with format commands
            if(di.instruction & 0xFFFF00 == 0x000100):
                # AddressOutputFormat
                AddressOutput = di.instruction & 0x03

            elif(di.instruction & 0xFFFF00 == 0x000200):
                # NumberOutputFormat
                NumberOutput = di.instruction & 0x03

            elif(di.instruction & 0xFFFF00 == 0x000300):
                # CommandOutputFormat
                CommandOutput = di.instruction & 0x03

            elif(di.instruction & 0xFFFF00 == 0x000400):
                # OutputTStatesFormat
                OutputTStates = di.instruction & 0x03

            elif(di.instruction & 0xFFFF00 == 0x000500):
                # LineAfterJumpOutputFormat
                BreakAfterJumps = di.instruction & 0x03

            elif(di.instruction & 0xFFFF00 == 0x000600):
                # DefaultFormat
                AddressOutput = di.instruction & 0x03
                NumberOutput = di.instruction & 0x03
                CommandOutput = di.instruction & 0x03
                OutputTStates = 0
                BreakAfterJumps = 1
                LineNumberOutput = 0
                ListEveryXLines = 0
                BreakAfterData = 0
                TreatDataNumbersAsLineReferences = 0
                DisplayCommandBytes = 0
                DisplayComments = 0
                Seperator = "  "
                ShowFlags = 0
                MarkUndocumenedCommand = 0
                XMLOutput = 0
                HexForNonASCII = 0

            elif(di.instruction & 0xFFFF00 == 0x000700):
                # CustomFormat
                settingstemp = get_custom_format_values(di.data, False)
                AddressOutput = settingstemp["AddressOutput"]
                NumberOutput = settingstemp["NumberOutput"]
                CommandOutput = settingstemp["CommandOutput"]
                OutputTStates = settingstemp["OutputTStates"]
                BreakAfterJumps = settingstemp["BreakAfterJumps"]
                LineNumberOutput = settingstemp["LineNumberOutput"]
                ListEveryXLines = settingstemp["ListEveryXLines"]
                BreakAfterData = settingstemp["BreakAfterData"]
                TreatDataNumbersAsLineReferences = settingstemp[
                    "TreatDataNumbersAsLineReferences"]
                DisplayCommandBytes = settingstemp["DisplayCommandBytes"]
                DisplayComments = settingstemp["DisplayComments"]
                Seperator = settingstemp["Seperator"]
                ShowFlags = settingstemp["ShowFlags"]
                MarkUndocumenedCommand = settingstemp["MarkUndocumenedCommand"]
                XMLOutput = settingstemp["XMLOutput"]
                HexForNonASCII = settingstemp["HexForNonASCII"]

            elif(di.instruction & 0xFFFF00 == 0x000800):
                # LineNumberOutput
                LineNumberOutput = di.instruction & 0x03

            elif(di.instruction & 0xFFFF00 == 0x000900):
                # ListEveryXLines
                ListEveryXLines = int(di.data, 16)

            elif(di.instruction & 0xFFFF00 == 0x000A00):
                # BreakAfterData
                BreakAfterData = di.instruction & 0x01

            elif(di.instruction & 0xFFFF00 == 0x000B00):
                # TreatDataNumbersAsLineReferences
                TreatDataNumbersAsLineReferences = di.instruction & 0x01

            elif(di.instruction & 0xFFFF00 == 0x000C00):
                # DisplayCommandBytes
                DisplayCommandBytes = di.instruction & 0x01

            elif(di.instruction & 0xFFFF00 == 0x000D00):
                # DisplayComments
                DisplayComments = di.instruction & 0x01

            elif(di.instruction & 0xFFFFFF == 0x000E00):
                # Seperator space
                Seperator = "  "

            elif(di.instruction & 0xFFFFFF == 0x000E01):
                # Seperator tab
                Seperator = "\t"

            elif(di.instruction & 0xFFFFFF == 0x000E02):
                # Seperator custom
                Seperator = di.data

            elif(di.instruction & 0xFFFF00 == 0x000F00):
                # Display flags
                ShowFlags = di.instruction & 0x01

            elif(di.instruction & 0xFFFF00 == 0x001000):
                # note undocumened commands
                MarkUndocumenedCommand = di.instruction & 0x01

            elif(di.instruction & 0xFFFF00 == 0x001200):
                # XML mode
                XMLOutput = di.instruction & 0x01

            elif(di.instruction & 0xFFFF00 == 0x001300):
                # HexForNonASCII mode
                HexForNonASCII = di.instruction & 0x01

            CurrentFormatEnd = di.end
            continue

        # check is comment
        if(di is not None and di.instruction & 0xFFFF00 == 0x030000 and
           di.data is not None and di.data is not ""):
            # handle commenmts before this line first
            if(di.instruction == DisassembleInstruction.DISASSEMBLE_CODES[
                    "Comment Before"]):
                if(DisplayComments == 0):
                    soutput += CommentOutput(di.data, XMLOutput).split("\n")

                continue
            # otherwise comnment end of this line or after
            if(di.instruction == 0x030002):
                if(CommentAfter is not ""):
                    CommentAfter += "\n"
                CommentAfter += di.data
            else:
                if(CommentEnd is not ""):
                    CommentEnd += ". "
                CommentEnd += di.data

            continue

        # check is reference comment
        if(di is not None and di.instruction & 0xFFFF00 == 0x030100):
            # make note of address referenced
            di.reference = int(di.data[:4], 16)
            # get flags
            di.flag = int(di.data[4:5], 16)
            # make note of comment
            di.comment = di.data[5:]
            # add it to list to look for
            CommentReferences += [di]
            # now sort it so 1st is next to expire
            CommentReferences.sort(key=attrgetter('end'))
            continue

        # now deal with machine code

        # set length for standard command (ignoring any associated data)
        commandlength = 1
        # offset to data
        dataOffset = 1
        # get opcode details
        s = Z80_OPCODES["base"][data[offset]]
        instructionData = Z80_OPCODE_DATA["base"][data[offset]]
        instructionTimes = Z80_OPCODE_TIMES["base"][data[offset]]

        # deal with CB,DD,ED,and FD
        if(s is None):
            if(data[offset] == 0xCB):
                s = Z80_OPCODES["CB"][data[offset + 1]]
                instructionData = Z80_OPCODE_DATA["CB"][data[offset + 1]]
                instructionTimes = Z80_OPCODE_TIMES["CB"][data[offset + 1]]
                commandlength = 2

            elif(data[offset] == 0xED):
                s = Z80_OPCODES["ED"][data[offset + 1]]
                instructionData = Z80_OPCODE_DATA["ED"][data[offset + 1]]
                instructionTimes = Z80_OPCODE_TIMES["ED"][data[offset + 1]]
                commandlength = 2
                dataOffset = 2
                # convert invalid ED codes to do nothing (is like 2
                # NOPs)
                if(s is None):
                    s = ""
                    instructionData = 0
                    instructionTimes = 1

            else:  # is DD or FD
                dataOffset = 2
                codehex = '{0:02X}'.format(data[offset])
                s = Z80_OPCODES[codehex][data[offset + 1]]
                instructionData = Z80_OPCODE_DATA[codehex][data[offset + 1]]
                instructionTimes = Z80_OPCODE_TIMES[codehex][data[offset + 1]]
                commandlength = 2
                # deal with DDCB or FDCB
                if(data[offset + 1] == 0xCB):
                    commandlength = 3
                    s = Z80_OPCODES[codehex + "CB"][data[offset + 3]]
                    instructionData = Z80_OPCODE_DATA[codehex + "CB"][data[
                        offset + 3]]
                    instructionTimes = Z80_OPCODE_TIMES[codehex + "CB"][data[
                        offset + 3]]

                # deal with invalid DD/FD codes (is like a NOP)
                if(s is None):
                    s = ""
                    instructionData = 0
                    instructionTimes = 1
                    commandlength = 1

        # now have opcode description in s, number of bytes in command
        # (excluding data) in commandlength, and where to start looking
        # for data in dataOffset
        # data holds information about timing, T states, if needs new
        # line etc

        # place in try block to catch trying to get extra data from
        # beyond end of supplied bytes
        try:
            # first check for & replace displacement byte
            if("d" in s):
                s = s.replace("d", _numbertostring(data[offset + dataOffset],
                                                   8, NumberOutput, True))
                dataOffset += 1
                commandlength += 1

            # check for & replace relative jump byte
            if("j" in s):
                # calculate address of next command
                i = currentAddress + commandlength + 1
                # add displacement
                i += data[offset + dataOffset] if (
                    data[offset + dataOffset] < 128) else \
                    data[offset + dataOffset] - 256

                s = s.replace("j", _numbertostring(i, 16, AddressOutput, True))
                dataOffset += 1
                commandlength += 1

                # make note of referenced line
                ReferencedLineNumbers += [i]

            # check for & replace 2 byte address
            if("aa" in s):
                # get number
                i = data[offset + dataOffset] + \
                    256*data[offset + dataOffset + 1]

                # check for reference comments
                for di in CommentReferences:
                    # have we got right reference
                    if(di.reference != i):
                        continue
                    # do the flags match
                    if((di.flag & 1 == 1 and '(' in s) or
                       (di.flag & 2 == 2 and s == 'LD SP,aa') or
                       (di.flag & 4 == 4 and s[0] == 'C') or
                       (di.flag & 8 == 8 and s[0] == 'J')):
                        # handle comment
                        if(di.instruction & 3 == 1):
                            if(DisplayComments == 0):
                                soutput += CommentOutput(di.comment,
                                                         XMLOutput).split("\n")
                        # otherwise comnment end of this line or after
                        elif(di.instruction & 3 == 2):
                            if(CommentAfter is not ""):
                                CommentAfter += "\n"
                            CommentAfter += di.comment
                        else:
                            if(CommentEnd is not ""):
                                CommentEnd += ". "
                            CommentEnd += di.comment

                s = s.replace("aa", _numbertostring(i, 16, AddressOutput,
                                                    True))
                dataOffset += 2
                commandlength += 2

                # make note of referenced address
                ReferencedLineNumbers += [i]

            # check for & replace 2 byte number
            if("nn" in s):
                # get number
                i = data[offset + dataOffset] + \
                    256*data[offset + dataOffset + 1]

                # check for reference comments
                for di in CommentReferences:
                    # have we got right reference
                    if(di.reference != i):
                        continue
                    # do the flags match
                    if(di.flag & 2 == 2):
                        # handle comment
                        if(di.instruction & 3 == 1):
                            if(DisplayComments == 0):
                                soutput += CommentOutput(di.comment,
                                                         XMLOutput).split("\n")
                        # otherwise comnment end of this line or after
                        elif(di.instruction & 3 == 2):
                            if(CommentAfter is not ""):
                                CommentAfter += "\n"
                            CommentAfter += di.comment
                        else:
                            if(CommentEnd is not ""):
                                CommentEnd += ". "
                            CommentEnd += di.comment

                s = s.replace("nn", _numbertostring(i, 16, NumberOutput, True))
                dataOffset += 2
                commandlength += 2

                # make note of referenced number
                if(TreatDataNumbersAsLineReferences == 0):
                    ReferencedLineNumbers += [i]

            # check for & replace 1 byte number
            if("n" in s):
                s = s.replace("n", _numbertostring(data[offset + dataOffset],
                                                   8, NumberOutput, True))
                dataOffset += 1
                commandlength += 1

        # catch if tried to get data from beyond end of supplied data
        except IndexError:
            # have tried to access bytes from beyond end of given data
            # output bytes as DB data
            # create DisassembleInstruction to do this
            DisassembleInstructions.insert(0, DisassembleInstruction(
                DisassembleInstruction.DISASSEMBLE_CODES["Data Block"],
                currentAddress, currentAddress + len(data)-offset-1,
                "%!DefineByte()"))
            # back too start of while loop & should enter data block
            continue

        # commandlength now holds number of bytes in current command
        # s holds assembly command
        # now do output

        # Handle XML output
        if(XMLOutput == 1):
            currentline = "  <line><address>" + _numbertostring(
                currentAddress, 16, AddressOutput, AddressOutput > 1) + \
                "</address>"

        # handle non-XML
        else:
            # work out max length of address
            maxAddressLength = max(FormatAddressLength[AddressOutput],
                                   maxAddressLength)

            # output address ready for processing later
            i = AddressOutput + (LineNumberOutput << 3)
            if(Seperator != "  "):
                i += 1 << 5

            currentline = "\0" + chr(i) + chr(ListEveryXLines)
            currentline += _numbertostring(currentAddress, 16, 0, False)

            # add seperator after address
            currentline += Seperator

            # remember where commands start
            k = len(currentline)

        # output bytes of commands
        # Handle XML output
        if(XMLOutput == 1):
            currentline += "<bytes>{0}</bytes>".format(
                ",".join([_numbertostring(b, 8, CommandOutput, False) for b in
                          data[offset:offset + commandlength]]))

        # handle non-XML
        else:
            # only do if want them output
            if(DisplayCommandBytes == 0):
                currentline += ",".join(
                    [_numbertostring(b, 8, CommandOutput, False) for b in
                     data[offset:offset + commandlength]])

                # now ensure opcodes line up
                # don't need to bother if using tabs
                if(Seperator == "  "):
                    i = 5*FormatByteLength[CommandOutput]
                    # adjust for commas
                    if(CommandOutput > 0):
                        i += 4
                    i += k
                    i -= len(currentline)
                    while(i >= 0):
                        currentline += " "
                        i -= 1

            # add seperator after command bytes
            # needed even if no command bytes as can go from disply
            # command bytes to not and have to ensure output stays in
            # same column in case tab seperated output is used in
            # spreadsheet
            currentline += Seperator

        # output opcode
        # Handle XML output
        if(XMLOutput == 1):
            currentline += "<instruction>" + s + "</instruction>"

        # handle non-XML
        else:
            currentline += s

        # Handle XML output of stuff in comments (timing, flags,
        # undocumented commands)
        if(XMLOutput == 1):
            # do comment
            if(DisplayComments == 0 and CommentEnd is not ""):
                currentline += "<comment>" + CommentEnd + "</comment>"

            # do flags
            sflags = getFlagChanges(instructionData)
            # output flag states if we have them
            if(sflags is not None):
                currentline += "<flags>" + sflags + "</flags>"

            # do times
            # get times
            duration, states = GetTimingInfo(instructionTimes)

            # now output timings
            currentline += "<timeing><cycles>"
            currentline += "unknown" if duration[0] == 0 else str(duration[0])
            currentline += "</cycles>"

            if(states is not None):
                currentline += "<tstates>" + ",".join(
                    str(x) for x in states[0])
                currentline += "</tstates>"

            currentline += "</timeing>"

            if(duration[1] != 0):
                currentline += '<timeing alternate="true"><cycles>'
                currentline += str(duration[1]) + "</cycles>"

                if(states is not None):
                    currentline += "<tstates>"
                    currentline += ",".join(str(x) for x in states[1])
                    currentline += "</tstates>"

                currentline += "</timeing>"

            # do undocumented comments if needed
            if(((instructionData >> 21) & 1) == 1):
                currentline += "<undocumented/>"

        # if we're not doing XML and want comments, do so
        elif(DisplayComments == 0):
            precomment = ""

            # align any comments
            # don't need to bother if using tabs
            if(Seperator == "  "):
                precomment = " " * (FormatOpCodeMaxLength[AddressOutput] if
                                    FormatOpCodeMaxLength[AddressOutput] >
                                    FormatOpCodeMaxLength[NumberOutput] else
                                    FormatOpCodeMaxLength[NumberOutput] -
                                    len(s))

            # space between opcode and comments, and comment marker
            precomment += Seperator + ";"

            # will we need a space before this comment (and any comment
            # following)
            bNeedSpace = False

            # do comment
            if(CommentEnd is not ""):
                # output pre comment text
                currentline += precomment
                # note has been output
                precomment = None

                if(CommentEnd.find("\n") == -1):
                    currentline += CommentEnd

                else:
                    comments = CommentEnd.split("\n")
                    currentline += comments[0]
                    if(CommentAfter is not ""):
                        CommentAfter = "\n" + CommentAfter
                    CommentAfter = "\n".join(comments[1:]) + CommentAfter

                # mark will need space if any comment following
                bNeedSpace = True

            # are we listing flags?
            if(ShowFlags > 0):
                if(precomment):
                    # output pre comment text
                    currentline += precomment
                    # note has been output
                    precomment = None

                # insert space if needed
                if(bNeedSpace):
                    currentline += "  "

                # get flag states for this instruction
                sflags = getFlagChanges(instructionData)
                # output flag states if we have them
                if(sflags is not None):
                    currentline += sflags

                    # mark will need space if any comment following
                    bNeedSpace = True

            if(OutputTStates > 0):
                if(precomment):
                    # output pre comment text
                    currentline += precomment
                    # note has been output
                    precomment = None

                # insert space if needed
                if(bNeedSpace):
                    currentline += "  "

                # get times
                duration, states = GetTimingInfo(instructionTimes)

                # now output timings
                currentline += "T="
                if((OutputTStates & 1) == 1):
                    if(duration[0] == 0):
                        currentline += "unknown"
                    else:
                        currentline += str(duration[0])

                if((OutputTStates & 2) == 2 and states is not None):
                    currentline += "(" + ",".join(
                        str(x) for x in states[0]) + ")"

                if(duration[1] != 0):
                    currentline += "/"
                    if((OutputTStates & 1) == 1):
                        currentline += str(duration[1])

                    if((OutputTStates & 2) == 2 and states is not None):
                        currentline += "(" + ",".join(
                            str(x) for x in states[1]) + ")"

                bNeedSpace = True

            # are we noteing undocumented commands?
            if(MarkUndocumenedCommand > 0 and
               ((instructionData >> 21) & 1) == 1):
                if(precomment):
                    # output pre comment text
                    currentline += precomment
                    # note has been output
                    precomment = None

                # do we need gap?
                if(bNeedSpace):
                    currentline += "  "

                # record that is undocumented
                currentline += "Undocumented Command"

        # end of line
        # Handle XML output
        if(XMLOutput == 1):
            currentline += "</line>"

        soutput += [currentline]

        # handle comments after line
        if(DisplayComments == 0 and CommentAfter is not ""):
            soutput += CommentOutput(CommentAfter, XMLOutput).split('\n')

        # clear comments
        CommentEnd = ""
        CommentAfter = ""

        # do we need to have newline after command to make more
        # readable.  Only needed if not doing XML
        i = instructionData & 3
        if(XMLOutput == 0 and BreakAfterJumps != 0 and i != 0):
            if(BreakAfterJumps != 1 or i != 1):
                soutput += ['']

        length -= commandlength
        offset += commandlength
        offset &= 0xFFFF
        currentAddress += commandlength

        workdone += commandlength * 2

    # end 1st pass
    if(XMLOutput == 1):
        soutput += ["</z80code>"]
    else:
        soutput += ['']

    # now search for line numbers and remove them if not needed
    lastLineInData = -1  # -1 start, 0=last in code, 1=last in data
    # count how many lines since last address reference
    lineCounter = 0

    # keep track of where we are in text
    k = 0
    lines = len(soutput)

    workdone = worktodo1 + worktodo2

    # search for address markers
    while(k < lines):
        # call progress update
        if(progressfunction is not None):
            progressfunction("Formatting", k, lines,
                             ((k * worktodo3) / lines) + workdone,
                             worktodo1 + worktodo2 + worktodo3)

        # skip lines that don't need formatting
        if(len(soutput[k]) < 1 or soutput[k][0] != '\0'):
            k += 1
            continue

        # retrieve Address output formating details
        AddressOutput = ord(soutput[k][1])
        # are we in a data block?
        bInData = (AddressOutput & 4) == 4
        # 0=All, 1=None,  2=only referenced lines
        LineNumberOutput = (AddressOutput >> 3) & 3
        # 0=2 spaces
        SeperatorMode = (AddressOutput >> 5) & 1
        # list every X lines regardless of LineNumberOutput
        ListEveryXLines = ord(soutput[k][2])
        AddressOutput &= 3

        # if moved from data to code
        if(lastLineInData != 0 and not bInData):
            # this will force line to be rendered
            lineCounter = ListEveryXLines

        # remember if last in code or data
        lastLineInData = 1 if bInData else 0

        # increment line counter
        lineCounter += 1

        # retrieve address to format
        currentAddress = int(soutput[k][3:7], 16)

        s = ""
        if(LineNumberOutput == 0 or
           (lineCounter >= ListEveryXLines and ListEveryXLines != 0) or
           (LineNumberOutput == 2 and currentAddress in ReferencedLineNumbers)
           ):
            # output address
            s = _numbertostring(currentAddress, 16, AddressOutput,
                                AddressOutput > 1)

            # reset line counter
            lineCounter = 0

        # if space seperator mode then pad with spaces if needed
        if(SeperatorMode == 0):
            m = maxAddressLength - len(s)
            s += " " * m

        # replace address sting with correct text
        soutput[k] = s + soutput[k][7:]
        # next line
        k += 1

    # report job done
    if(progressfunction is not None):
        progressfunction("Done", 100, 100, worktodo1 + worktodo2 + worktodo3,
                         worktodo1 + worktodo2 + worktodo3)

    return "\n".join(soutput)


def PredefinedStartLine(Settings, Vars, datatitle):
    """This functions starts off a line for predefined functions."""

    soutput = ""

    # check if any comments to be added to this data
    if("COMMENTCONTROL" in Settings):
        # move past any instructions that has been & gone
        dis = Settings["COMMENTCONTROL"][0]
        #get rid of passed commands
        while(dis and Vars[0x0A] > dis[0].end):
            dis.pop(0)
        # cycle through commands for this line to find comments
        i = 0
        while(dis and Vars[0x0A] >= dis[i].start):
            # if is comment instruction process it
            if(dis[i].instruction & 0xFFFF00 == 0x030000 and
               dis[i].data is not None and dis[i].data is not ""):
                di = dis.pop(i)
                if(di.instruction == DisassembleInstruction.DISASSEMBLE_CODES[
                   "Comment Before"]):
                    if(Settings["COMMENTCONTROL"][1] == 0):
                        soutput += Settings["COMMENTCONTROL"][4](
                            di.data, Settings["XMLOutput"]) + "\n"
                
                # otherwise comnment end of this line or after
                elif(di.instruction == 0x030002):
                    if(Settings["COMMENTCONTROL"][3] is not ""):
                        Settings["COMMENTCONTROL"][3] += "\n"
                    Settings["COMMENTCONTROL"][3] += di.data
                else:
                    if(Settings["COMMENTCONTROL"][2] is not ""):
                        Settings["COMMENTCONTROL"][2] += ". "
                    Settings["COMMENTCONTROL"][2] += di.data
            else:
                i += 1

    # output line details
    if(Settings["XMLOutput"] == 1):
        if(not Settings["HadLineStart"]):
            soutput += "  <line>"
        soutput += "<address>{0}</address>".format(
            _numbertostring(Vars[10], 16, Settings["ADDRESSOUTPUT"], False))
        soutput += "<instruction>{0}</instruction>".format(datatitle)
    else:
        i = Settings["ADDRESSOUTPUT"] + 4
        if(Settings["SEPERATOR"] != "  "):
            i += 1 << 5
        soutput += "\0" + chr(i) + chr(Settings["DISPLAYEVERYXLINES"])
        soutput += "{0:04X}{1}{1}{2}{1}".format(Vars[10],
                                                Settings["SEPERATOR"],
                                                datatitle)

    Settings["HadLineStart"] = True
    Settings["HadLineEnd"] = False

    return soutput


def PredefinedEndLine(Settings, Vars):
    """This functions ends a line for predefined functions."""

    soutput = ""

    # update position
    Vars[0x0A] += Vars[0x0C]
    # update line number
    Vars[0x0B] += 1

    # do comment
    if("COMMENTCONTROL" in Settings and
       Settings["COMMENTCONTROL"][1] == 0 and
       Settings["COMMENTCONTROL"][2] is not ""):
        # XML comments
        if(Settings["XMLOutput"] == 1):
            soutput += "<comment>{0}</comment>".format(
                Settings["COMMENTCONTROL"][2])
        # plain text comments
        else:
            # output pre comment text
            soutput += Settings["SEPERATOR"] + ';'

            if(Settings["COMMENTCONTROL"][2].find("\n") == -1):
                soutput += Settings["COMMENTCONTROL"][2]

            else:
                comments = Settings["COMMENTCONTROL"][2].split("\n")
                soutput += comments[0] + "\n"
                soutput += Settings["COMMENTCONTROL"][4](
                    "".join(comments[1:]), Settings["XMLOutput"])

    if(not Settings["HadLineEnd"]):
        # end of line
        if(Settings["XMLOutput"] == 1):
            soutput += '</line>'

        # new line
        soutput += "\n"

    # handle comments after line
    if("COMMENTCONTROL" in Settings):
        if(Settings["COMMENTCONTROL"][1] == 0 and
           Settings["COMMENTCONTROL"][3] is not ""):
            soutput += Settings["COMMENTCONTROL"][4](
                Settings["COMMENTCONTROL"][3],
                Settings["XMLOutput"]) + "\n"

        # clear comments
        Settings["COMMENTCONTROL"][2] = ""
        Settings["COMMENTCONTROL"][3] = ""

    Settings["HadLineStart"] = False
    Settings["HadLineEnd"] = True

    return soutput


# pre-defined Functions
def _PredefinedDefineByte(data, Settings, Vars, Signed=False, Format=0,
                          FormatIdentifyer=True, GapFrequency=1, Gap=",",
                          MaxPerLine=1):
    """Outputs data as bytes.

data is the data to process.
Settings is a dictionary containing needed setings such as the origin of
  the code, if wanting XML output, formats for adress, numbers, and
  commands. This is the same as for the disassembledatablock in a
  DisassembleInstruction object.
Vars is a list of variables as used internally to process the scripting
  code used by the disassembler. Of note Vars[0x0A] is the address of
  the current line, Vars[0x0E] is the last byte that's part of the data,
  and Vars[0x0C] is the offset of the current byte being processed in
  bytes from Vars[0x0A].
Signed specifies if 255 (0xFF) is 255 or -1.
Format specifies the number format: 0 for Hexadecimal, 1 for decimal,
  2 for octal, 3 for binary, 4 to use the same format as is used for
  addresses, 5 to use same format as for numbers, and 6 to use the
  same format as the bytes of a command
FormatIdentifyer specifies if you want a label to identify the data:
  # for hexadecimal numbers, b for binary, o for octal, nothing for
  decimal. Set this to text if you want to specify your own identifyer
  to use infront of a number.
GapFrequency is how many bytes between gaps in the data output.
  Set this to 0 if you don't want any gaps.
Gap specifies what text you want to use between bytes in the output as
  controlled by GapFrequency.
MaxPerLine specified the maximum number of bytes output per line of data
  before moveing onto a new line."""

    if(Format == 4):
        Format = Settings["ADDRESSOUTPUT"]
    elif(Format == 5):
        Format = Settings["NUMBEROUTPUT"]
    elif(Format == 6):
        Format = Settings["COMMANDOUTPUT"]
    dataformat = FormatIdentifyer if isinstance(FormatIdentifyer, str) else \
        (("#", "", "o", "b")[Format] if FormatIdentifyer else "")
    dataformat += ("{0:02X}", "{0}", "{0:03o}", "{0:08b}")[Format]

    soutput = ""

    # look until have passed end point
    while(Vars[0x0A] <= Vars[0x0E]):
        # output line details
        soutput += PredefinedStartLine(Settings, Vars,
                                       "SB" if Signed else "DB")

        # loop until run out of data area or hit max line length
        Vars[0x0C] = 0
        while(Vars[0x0A] + Vars[0x0C] <= Vars[0x0E] and
              Vars[0x0C] < MaxPerLine):
            if(Settings["XMLOutput"] == 1):
                soutput += "<data>"
            elif(GapFrequency > 0 and Vars[0x0C] > 0 and
                 Vars[0x0C] % GapFrequency == 0):
                soutput += Gap

            # get value to output
            n = data[Vars[0x0A] + Vars[0x0C] - Settings["ORIGIN"]]
            # handle negative
            if(Signed and n > 127):
                soutput += "-"
                n = 256 - n
            # output value
            soutput += dataformat.format(n)
            if(Settings["XMLOutput"] == 1):
                soutput += "</data>"
            Vars[0x0C] += 1

        # end of line
        soutput += PredefinedEndLine(Settings, Vars)

    Vars[0x0E] = Vars[0x0A] - 1
    return soutput


def _PredefinedDefineWord(data, Settings, Vars, Signed=False, Format=0,
                          FormatIdentifyer=True, GapFrequency=1, Gap=',',
                          MaxPerLine=1, LittleEndian=True):
    """Outputs data as 2 byte words.

data is the data to process.
Settings is a dictionary containing needed setings such as the origin of
  the code, if wanting XML output, formats for adress, numbers, and
  commands. This is the same as for the disassembledatablock in a
  DisassembleInstruction object.
Vars is a list of variables as used internally to process the scripting
  code used by the disassembler. Of note Vars[0x0A] is the address of
  the current line, Vars[0x0E] is the last byte that's part of the data,
  and Vars[0x0C] is the offset of the current byte being processed in
  bytes from Vars[0x0A].
Signed specifies if 255 (0xFF) is 255 or -1.
Format specifies the number format: 0 for Hexadecimal, 1 for decimal,
  2 for octal, 3 for binary, 4 to use the same format as is used for
  addresses, 5 to use same format as for numbers, and 6 to use the
  same format as the bytes of a command
FormatIdentifyer specifies if you want a label to identify the data:
  # for hexadecimal numbers, b for binary, o for octal, nothing for
  decimal. Set this to text if you want to specify your own identifyer
  to use infront of a number.
GapFrequency is how many words between gaps in the data output.
  Set this to 0 if you don't want any gaps.
Gap specifies what text you want to use between words in the output as
  controlled by GapFrequency.
MaxPerLine specified the maximum number of words output per line of data
  before moveing onto a new line."""

    if(Format == 4):
        Format = Settings["ADDRESSOUTPUT"]
    elif(Format == 5):
        Format = Settings["NUMBEROUTPUT"]
    elif(Format == 6):
        Format = Settings["COMMANDOUTPUT"]
    dataformat = FormatIdentifyer if isinstance(FormatIdentifyer, str) else \
        (("#", "", "o", "b")[Format] if FormatIdentifyer else "")
    dataformat += ("{0:04X}", "{0}", "{0:06o}", "{0:016b}")[Format]
    datatitle = "{0}{1}".format("SW" if Signed else "DW",
                                "" if LittleEndian else "BE")

    soutput = ""

    # look until have passed end point
    while(Vars[0x0A] <= Vars[0x0E]):
        # output line details
        soutput += PredefinedStartLine(Settings, Vars, datatitle)

        # loop until run out of data area or hit max line length
        Vars[0x0C] = 0
        while(Vars[0x0A] + Vars[0x0C] <= Vars[0x0E] and
              Vars[0x0C] < (MaxPerLine * 2)):
            if(Settings["XMLOutput"] == 1):
                soutput += "<data>"
            elif(GapFrequency > 0 and Vars[0x0C] > 0 and
                 Vars[0x0C] % (GapFrequency * 2) == 0):
                soutput += Gap

            # get value to output
            n = Vars[0x0A] + Vars[0x0C] - Settings["ORIGIN"]
            n = (data[n] + 256 * data[n + 1]) if LittleEndian else \
                (data[n + 1] + 256 * data[n])
            # handle negative
            if(Signed and n > 0x7FFF):
                soutput += "-"
                n = 65536 - n
            # output value
            soutput += dataformat.format(n)
            if(Settings["XMLOutput"] == 1):
                soutput += "</data>"
            Vars[0x0C] += 2

        # end of line
        soutput += PredefinedEndLine(Settings, Vars)

    Vars[0x0E] = Vars[0x0A] - 1

    return soutput


def _PredefinedDefineMessage(data, Settings, Vars, DataType="DM",
                             Noncharoutofquotes=False):
    """Outputs data as text.

data is the data to process.
Settings is a dictionary containing needed setings such as the origin of
  the code, if wanting XML output, formats for adress, numbers, and
  commands. This is the same as for the disassembledatablock in a
  DisassembleInstruction object.
Vars is a list of variables as used internally to process the scripting
  code used by the disassembler. Of note Vars[0x0A] is the address of
  the current line, Vars[0x0E] is the last byte that's part of the data,
  and Vars[0x0C] is the offset of the current byte being processed in
  bytes from Vars[0x0A].
DataType specifies the length encoding of the message. "DM" to be length
  of the data block, "DM0" to be terminated by a zero byte (ignoring a
  zero after a control code), "DM7" to be terminated by bit 7 being set
  on the last character, "DMLB" where the string length is encoded as a
  byte at the start of the string, "DMLW" where the length is encoded as
  a Little endian string before the start of a string, and "DMLWBE"
  where he length is encoded as a big-endian word before the string.
Noncharoutofquotes defines if you want non characters (ie control codes,
  or commands if the "Hex instead of non-ASCII On" control is being
  used) displayed as hex numbers outside of strings instead of 2 digit
  hexacecimal numbers preceded by '^' (which is never used on the
  spectrum) inside a string."""
    endings = {"DM": "DM",
               "DM0": "DM0", "0": "DM0",
               "DM7": "DM7", "7": "DM7",
               "DMLB": "DMLB", "LB": "DMLB",
               "DMLW": "DMLW", "LW": "DMLW",
               "DMLWBE": "DMLWBE", "LWBE": "DMLWBE", "BE": "DMLWBE"}
    if(DataType not in endings):
        raise SpectrumTranslateError("{0} not a recognised Word format".format(
            DataType))
    datatitle = endings[DataType]

    soutput = ""
    maxaddress = len(data) + Settings["ORIGIN"] - 1

    # look until have passed end point
    while(Vars[0x0A] <= Vars[0x0E]):
        # output line details
        soutput += PredefinedStartLine(Settings, Vars, datatitle)
        Vars[0x0C] = 0
        # get last char of string
        if(datatitle == "DM"):
            end = Vars[0x0E]
        elif(datatitle == "DM0"):
            bytesaftercontrol = -1
            end = Vars[0x0A]
            while(end < maxaddress and (data[end - Settings["ORIGIN"]] != 0 or
                  bytesaftercontrol > 0)):
                bytesaftercontrol -= 1
                d = data[end - Settings["ORIGIN"]]
                end += 1
                if(d >= 16 and d <= 21):
                    bytesaftercontrol = 1
                elif(d == 22):
                    bytesaftercontrol = 2
        elif(datatitle == "DM7"):
            bytesaftercontrol = -1
            end = Vars[0x0A]
            while(end < maxaddress and (data[end - Settings["ORIGIN"]] < 128 or
                  bytesaftercontrol > 0)):
                bytesaftercontrol -= 1
                d = data[end - Settings["ORIGIN"]]
                end += 1
                if(d >= 16 and d <= 21):
                    bytesaftercontrol = 1
                elif(d == 22):
                    bytesaftercontrol = 2
        elif(datatitle == "DMLB"):
            length = data[Vars[0x0A] - Settings["ORIGIN"]]
            end = min(maxaddress, Vars[0x0A] + length)
            Vars[0x0C] = 1
        elif(datatitle == "DMLW"):
            length = data[Vars[0x0A] - Settings["ORIGIN"]] + \
                     256 * data[Vars[0x0A] - Settings["ORIGIN"] + 1]
            end = min(maxaddress, Vars[0x0A] + length + 1)
            Vars[0x0C] = 2
        else:
            length = data[Vars[0x0A] - Settings["ORIGIN"] + 1] + \
                     256 * data[Vars[0x0A] - Settings["ORIGIN"]]
            end = min(maxaddress, Vars[0x0A] + length + 1)
            Vars[0x0C] = 2

        if(Settings["XMLOutput"] == 1):
            soutput += "<data>"
        # loop until run out of data area or hit max line length
        bytesaftercontrol = 0
        inquotes = False
        startoffset = Vars[0x0C]
        while(Vars[0x0A] + Vars[0x0C] <= end):
            n = data[Vars[0x0A] + Vars[0x0C] - Settings["ORIGIN"]]
            c = getspectrumchar(n, Settings["HexForNonASCII"])
            # force bytes after control character to be number not char
            # also bytes>127 in bit 7 mode
            if(bytesaftercontrol > 0 or (datatitle == "DM7" and n > 127)):
                c = "^{0:02X}".format(n)
            bytesaftercontrol -= 1
            # handle numbers outside quotes
            if(c[0] == '^' and Noncharoutofquotes):
                if(inquotes):
                    soutput += '"'
                    inquotes = False
                soutput += "{0}0x{1:02X}".format(
                    "" if Vars[0x0C] == startoffset else ",", n)
            else:
                # print enter quotes if needed
                if(not inquotes):
                    if(Vars[0x0C] > startoffset):
                        soutput += ','
                    soutput += '"'
                    inquotes = True
                soutput += c

            # if is control code, work out how many bytes follow
            if(n >= 16 and n <= 21):
                bytesaftercontrol = 1
            elif(n == 22):
                bytesaftercontrol = 2

            # move to next char
            Vars[0x0C] += 1

        # close quotes if needed
        if(inquotes):
            soutput += '"'

        if(Settings["XMLOutput"] == 1):
            soutput += "</data>"
        # end of line
        soutput += PredefinedEndLine(Settings, Vars)

    Vars[0x0E] = end

    return soutput


def _PredefinedFindPattern(data, Settings, Vars, *args):
    """Returns a list of matching addresses to the supplied list of
bytes. After the basic data, just supp;y the vlues to search for in
order."""
    arglen = len(args)
    if(arglen == 0):
        raise SpectrumTranslateError("No bytes to match")

    matches = []
    pos = Vars[0x0A]
    origin = Settings["ORIGIN"]
    l = len(data)
    # convert args to a bytearray so can be matched
    args = bytearray(args)
    while(pos <= Vars[0x0E] and pos - origin < l):
        n = pos - origin
        if(data[n:n + arglen] == args):
            matches += [pos]
        pos += 1

    return matches


def _PredefinedStartandEndByOffset(data, Settings, Vars, addresses,
                                   startoffset=0, endoffset=0):
    """Returns a list of lists for start and end addresses, given the
offsets and origional addresses."""

    return [[x + startoffset, x + endoffset] for x in addresses]


class DisassembleInstruction:
    DISASSEMBLE_CODES = {
        "Address Output Format Hex": 0x0100,
        "Address Output Format Decimal": 0x0101,
        "Address Output Format Octal": 0x0102,
        "Address Output Format Binary": 0x0103,
        "Number Output Format Hex": 0x0200,
        "Number Output Format Decimal": 0x0201,
        "Number Output Format Octal": 0x0202,
        "Number Output Format Binary": 0x0203,
        "Command Output Format Hex": 0x0300,
        "Command Output Format Decimal": 0x0301,
        "Command Output Format Octal": 0x0302,
        "Command Output Format Binary": 0x0303,
        "Output T States Format None": 0x0400,
        "Output T States Format Total": 0x0401,
        "Output T States Format List States": 0x0402,
        "Output T States Format List All": 0x0403,
        "Line After Jump None": 0x0500,
        "Line After Jump After Absolute": 0x0501,
        "Line After Jump After All": 0x0502,
        "Default Format Hex": 0x0600,
        "Default Format Decimal": 0x0601,
        "Default Format Octal": 0x0602,
        "Default Format Binary": 0x0603,
        "Custom Format": 0x0700,
        "Line Numbers All": 0x0800,
        "Line Numbers None": 0x0801,
        "Line Numbers Referenced": 0x0802,
        "Line Number Every X": 0x0900,
        "Empty Line After Data On": 0x0A00,
        "Empty Line After Data Off": 0x0A01,
        "Reference Data Numbers On": 0x0B00,
        "Reference Data Numbers Off": 0x0B01,
        "List Command Bytes On": 0x0C00,
        "List Command Bytes Off": 0x0C01,
        "Comments On": 0x0D00,
        "Comments Off": 0x0D01,
        "Seperators Space": 0x0E00,
        "Seperators Tab": 0x0E01,
        "Seperators Custom": 0x0E02,
        "Display Flags Off": 0x0F00,
        "Display Flags On": 0x0F01,
        "Mark Undocumented Command Off": 0x1000,
        "Mark Undocumented Command On": 0x1001,
        "Reference Line": 0x1100,
        "XML Output Off": 0x1200,
        "XML Output On": 0x1201,
        "Hex instead of non-ASCII Off": 0x1300,
        "Hex instead of non-ASCII On": 0x1301,
        "Data Block": 0x010000,
        "Pattern Data Block": 0x020000,
        "Comment": 0x030000,
        "Comment Before": 0x030001,
        "Comment After": 0x030002,
        "Comment Reference": 0x030100,
        "Comment Reference Before": 0x030101,
        "Comment Reference After": 0x030102,
        "Comment Pattern": 0x040001}

    DISASSEMBLE_DATABLOCK_CODES = {
        "Define Byte Hex": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DB        %#output instruction (DB or define byte in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0000    %#set format to hexadecimal
%F0100    %#set format to unsigned
#         %#output '#' to indicate hex number following
%B0F      %#output contents at current position as byte,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Byte Decimal": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DB        %#output instruction (DB or define byte in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0001    %#set format to decimal
%F0100    %#set format to unsigned
%B0F      %#output contents at current position as byte,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Byte Octal": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DB        %#output instruction (DB or define byte in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0002    %#set format to octal
%F0100    %#set format to unsigned
o         %#output 'o' to indicate octal number following
%B0F      %#output contents at current position as byte,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Byte Binary": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DB        %#output instruction (DB or define byte in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0003    %#set format to binary
%F0100    %#set format to unsigned
b         %#output 'b' to indicate binary number following
%B0F      %#output contents at current position as byte,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Byte": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DB        %#output instruction (DB or define byte in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0000    %#set format to hexadecimal (default for generic define byte)
%F0100    %#set format to unsigned
#         %#output '#' to indicate hex number following
%B0F      %#output contents at current position as byte,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Byte Hex": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SB        %#output instruction (SB or signed byte in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0000    %#set format to hexadecimal
%F0101    %#set format to signed
#         %#output '#' to indicate hex number following
%B0F      %#output contents at current position as byte,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Byte Decimal": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SB        %#output instruction (SB or signed byte in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0001    %#set format to decimal
%F0101    %#set format to signed
%B0F      %#output contents at current position as byte,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Byte Octal": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SB        %#output instruction (SB or signed byte in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0002    %#set format to octal
%F0101    %#set format to signed
o         %#output 'o' to indicate octal number following
%B0F      %#output contents at current position as byte,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Byte Binary": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SB        %#output instruction (SB or signed byte in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0003    %#set format to binary
%F0101    %#set format to signed
b         %#output 'b' to indicate binary number following
%B0F      %#output contents at current position as byte,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Byte": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SB        %#output instruction (SB or signed byte in this case) default to hex
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0000    %#set format to hexadecimal
%F0101    %#set format to signed
#         %#output '#' to indicate hex number following
%B0F      %#output contents at current position as byte,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Word Hex": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DW        %#output instruction (DW or define word in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0000    %#set format to hexadecimal
%F0100    %#set format to unsigned
%F0200    %#set words little endian (least significant byte first)
#         %#output '#' to indicate hex number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Word Decimal": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DW        %#output instruction (DW or define word in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0001    %#set format to decimal
%F0100    %#set format to unsigned
%F0200    %#set words little endian (least significant byte first)
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Word Octal": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DW        %#output instruction (DW or define word in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0002    %#set format to octal
%F0100    %#set format to unsigned
%F0200    %#set words little endian (least significant byte first)
o         %#output 'o' to indicate octal number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Word Binary": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DW        %#output instruction (DW or define word in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0003    %#set format to binary
%F0100    %#set format to unsigned
%F0200    %#set words little endian (least significant byte first)
b         %#output 'b' to indicate binary number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Word": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DW        %#output instruction (DW or define word in this case) default to hex
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0000    %#set format to hexadecimal
%F0100    %#set format to unsigned
%F0200    %#set words little endian (least significant byte first)
#         %#output '#' to indicate hex number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Word Hex": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SW        %#output instruction (SW or signed word in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0000    %#set format to hexadecimal
%F0101    %#set format to signed
%F0200    %#set words little endian (least significant byte first)
#         %#output '#' to indicate hex number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Word Decimal": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SW        %#output instruction (SW or signed word in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0001    %#set format to decimal
%F0101    %#set format to signed
%F0200    %#set words little endian (least significant byte first)
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Word Octal": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SW        %#output instruction (SW or signed word in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0002    %#set format to octal
%F0101    %#set format to signed
%F0200    %#set words little endian (least significant byte first)
o         %#output 'o' to indicate octal number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Word Binary": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SW        %#output instruction (SW or signed word in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0003    %#set format to binary
%F0101    %#set format to signed
%F0200    %#set words little endian (least significant byte first)
b         %#output 'b' to indicate binary number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Word": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SW        %#output instruction (SW or signed word in this case) default to hex
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0000    %#set format to hexadecimal
%F0101    %#set format to signed
%F0200    %#set words little endian (least significant byte first)
#         %#output '#' to indicate hex number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Word BigEndian Hex": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DWBE      %#output instruction (DWBE or define word big endian in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0000    %#set format to hexadecimal
%F0100    %#set format to unsigned
%F0201    %#set words big endian (most significant byte first)
#         %#output '#' to indicate hex number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Word BigEndian Decimal": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DWBE      %#output instruction (DWBE or define word big endian in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0001    %#set format to decimal
%F0100    %#set format to unsigned
%F0201    %#set words big endian (most significant byte first)
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Word BigEndian Octal": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DWBE      %#output instruction (DWBE or define word big endian in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0002    %#set format to octal
%F0100    %#set format to unsigned
%F0201    %#set words big endian (most significant byte first)
o         %#output 'o' to indicate octal number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Word BigEndian Binary": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DWBE      %#output instruction (DWBE or define word big endian in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0003    %#set format to binary
%F0100    %#set format to unsigned
%F0201    %#set words big endian (most significant byte first)
b         %#output 'b' to indicate binary number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Word BigEndian": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
DWBE      %#output instruction (DWBE or define word big endian in this case)
          %#default to hexadecimal
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0000    %#set format to hexadecimal
%F0100    %#set format to unsigned
%F0201    %#set words big endian (most significant byte first)
#         %#output '#' to indicate hex number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Word BigEndian Hex": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SWBE      %#output instruction (SWBE or signed word big endian in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0000    %#set format to hexadecimal
%F0101    %#set format to signed
%F0201    %#set words big endian (most significant byte first)
#         %#output '#' to indicate hex number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Word BigEndian Decimal": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SWBE      %#output instruction (SWBE or signed word big endian in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0001    %#set format to decimal
%F0101    %#set format to signed
%F0201    %#set words big endian (most significant byte first)
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Word BigEndian Octal": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SWBE      %#output instruction (SWBE or signed word big endian in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0002    %#set format to octal
%F0101    %#set format to signed
%F0201    %#set words big endian (most significant byte first)
o         %#output 'o' to indicate octal number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Word BigEndian Binary": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SWBE      %#output instruction (SWBE or signed word big endian in this case)
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0003    %#set format to hexadecimal
%F0101    %#set format to signed
%F0201    %#set words big endian (most significant byte first)
b         %#output 'b' to indicate binary number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Signed Word BigEndian": """\
%$A       %#start address xml tag
%F0004    %#set output format to general output format
%ACA      %#output line address as address
%$-A      %#close address xml tag
%S%S      %#seperator
%$I       %#start instruction xml tag
SWBE      %#output instruction (SWBE or signed word big endian in this case)
          %#default to hexadecimal
%$-I      %#close instruction tag
%S        %#seperator
%$D       %#start data tag
%F0000    %#set format to hexadecimal
%F0101    %#set format to signed
%F0201    %#set words big endian (most significant byte first)
#         %#output '#' to indicate hex number following
%W0F      %#output contents at current position as word,
          %#and increment current position
%$-D      %#close data xml tag""",
        "Define Message": """\
%$A             %#start address xml tag
%F0004          %#set output format to general output format
%ACA            %#output line address as address
%$-A            %#close address xml tag
%S%S            %#seperator
%$I             %#start instruction xml tag
DM              %#output instuction (DM or Define Message)
%$-I            %#close instruction xml tag
%S
%$D             %#start data tag
%X01000000      %#set var0 to 0 (used as flag: 0=out of quotes, 1=in quotes)
%L%(            %#define loop,staring with the while condition
  %?LE%V0F%V0E  %#while current position is less than end position
%)              %#end while test
%(              %#start of loop section
  %I%(          %#start of if
    %(%?EQ%V000001                              %#if we're inside quotes
      %?BA                                      %#and
      %(%?LT%MV0F0020          %#the contents of the current position
                               %#are less than 0x20 (ie is not ascii character)
        %?BO                                    %#or
        %(%?MT%MV0F007F%?BA%?LT%MV0F00A3%)%)%)  %#the contents of the current
                               %#position are greater than 0x7F, and less than
                               %#0xA3 (not printable character: NB codes A3 and
                               %#above are valid printable spectrum
                               %#characters - the commands)
    %?BO                                        %#or
    %(%?EQ%V000000                              %#we're not inside quotes
      %?BA                                      %#and
      %(%?MT%MV0F00A2          %#the contents of the current position is a
                               %#command: valid spectrum character
        %?BO                                    %#or
        %(%?MT%MV0F001F%?BA%?LT%MV0F0080%)%)%)  %#the contents of the current
                    %# position are >0x1F and <0x80 (ie valid character)
  %)                %#end if test
  %(                %#are we in a quote & have an unprintable character or
                    %#outside a quote, and have a printable character
    "               %#print a quote
    %X03000001%V00  %#take var0 from 1 and store in var0: toggles var0 swapping
                    %#from inside to outside quotes and vice versa
  %)                %#end if action
  %C0F              %#output contents at current position as character,
                    %#and increment current position
%)                  %#end while loop
%I%(                %#if to see if still inside quotes
  %?EQ%V000001      %#is var0 equal to 1
%)
%(
  "                 %#print closeing quote if we are
%)
%$-D      %#close data xml tag""",
        "Define Message zero terminated": """\
%$A             %#start address xml tag
%F0004          %#set output format to general output format
%ACA            %#output line address as address
%$-A            %#close address xml tag
%S%S            %#seperator
%$I             %#start instruction xml tag
DM0             %#output instuction (DM0 or Define Message 0 ternminated)
%$-I            %#close instruction xml tag
%S
%$D             %#start data tag
%X01000000      %#set var0 to 0 (used as flag: 0=out of quotes, 1=in quotes)
%L%(            %#define while condition for loop
  %?NE%MV0F0000 %#while the contents of the current position are not equal to 0
%)
%(              %#start of loop section
  %I%(          %#start of if
    %(%?EQ%V000001            %#if we're inside quotes
      %?BA                    %#and
      %(%?LT%MV0F0020         %#the contents of the current position are less
                              %#than 0x20 (ie is not ascii character)
        %?BO                  %#or
        %(%?MT%MV0F007F%?BA%?LT%MV0F00A3%)%)%)  %#the contents of the current
                              %#position are greater than 0x7F, and less than
                              %#0xA3 (not printable character: NB codes A3 and
                              %#above are valid printable spectrum
                              %#characters - the commands)
    %?BO                      %#or
    %(%?EQ%V000000            %#we're not inside quotes
      %?BA                    %#and
      %(%?MT%MV0F00A2         %#the contents of the current position is a
                              %#command: valid spectrum character
        %?BO                  %#or
        %(%?MT%MV0F001F%?BA%?LT%MV0F0080%)%)%)  %#the contents of the current
                    %#position are >0x1F and <0x80 (ie valid character)
  %)                %#end if test
  %(                %#are we in a quote & have an unprintable character or
                    %#outside a quote, and have a printable character
    "               %#print a quote
    %X03000001%V00  %#take var0 from 1 and store in var0: toggles var0 swapping
                    %#from inside to outside quotes and vice versa
  %)                %#end if action
  %C0F              %#output contents at current position as character,
                    %#and increment current position
%)                  %#end while loop
%I%(                %#if to see if still inside quotes
  %?EQ%V000001      %#is var0 equal to 1
%)
%(
  "                 %#print closeing quote if we are
%)
,                   %#print comma
%X020C%V0C0001      %#add offset from linestart and 1 and save as offset from
                    %#line start.  moves past 0 terminating byte
#00                 %#print #00 as for terminating 0x00
%$-D                %#close data xml tag""",
        "Define Message bit 7 terminated": """\
%$A             %#start address xml tag
%F0004          %#number format to same as general address format
%ACA            %#output line address (variable 0x0A) as an address,
                %#don't increment line address(set bit 6),
                %#is variable and not what points to we want (bit 7)
%$-A            %#close address xml tag
%S%S            %#seperator
%$I             %#start instruction xml tag
DM7             %#output instuction (DM7 or Define Message bit7 ternminated)
%$-I            %#close instruction xml tag
%S
%$D             %#start data tag
%X01000000         %#set var0 to 0 (used as flag: 0=out of quotes, 1=in quotes)
%L%(               %#enter while() do{} loop
  %?EQ00000000     %# 0==0: ie true.  this will loop until loop broken out of
%)                 %#end of while test
%(                 %#enter do part of loop
  %X0701%MV0F007F  %#set var1 to contents of current position & 0x7F
  %X0702%MV0F0080  %#set var2 to contents of current position & 0x80
  %X020C%V0C0001   %#increment current position
  %I%(             %#check if entering or leaving printable character
    %( %?EQ%V000001 %?BA %?LT%V010020 %)   %#if in quotes & var1<0x20
    %?BO           %#or
    %( %?EQ%V000000 %?BA %?MT%V01001F %)   %#if not in quotes & var1>0x1F
  %)               %#end of if test
  %(               %#start of what to do if test true
    "              %#output quotes
    %X03000001%V00 %#set var0 to 1-var0 (so will set to 1 if was 0 and 0 if
                   %#was 1: toggles if in quotes)
  %)               %#end if action
  %CC1             %#output character: var1 (what's at current position&0x7F)
                   %#(bit 6=don't increment, bit7=contents of address pointer
                   %#to by current address register)
  %I%(             %#start if
    %?EQ%V020080   %#is var2==0x80 (ie was bit 7 set in currentcharacter before
                   %#incrementing?
  %)               %#end of if test
  %(               %#start of what to do if test true
    %Y             %#break out of loop: have reached character with bit 7 set
  %)               %#end if action
%)                 %#end of loop

%I%(               %#start of if
  %?EQ%V000001     %#if var0==1 (is inside a quote)
%)                 %#end of if test
%(                 %#start of what to do if test true
  "                %#print closing quote
%)                 %#end of what to do if test true
%$-D                %#close data xml tag""",
        "Define Message Length Byte": """\
%$A            %#start address xml tag
%F0004         %#number format to same as general address format
%ACA           %#output line address (variable 0x0A) as an address,
               %#don't increment line address(set bit 6),
               %#is variable and not what points to we want (bit 7)
%$-A           %#close address xml tag
%S%S           %#seperator
%$I            %#start instruction xml tag
DMLB           %#output instuction (DMLB or Define Message Length Byte)
%$-I           %#close instruction xml tag
%S
%$D            %#start data tag
%X01000000     %#set var0 to 0 (used as flag: 0=out of quotes, 1=inside quotes)
%X0101%MV0F    %#var1 to contents of current address: number of bytes in string
%X020C%V0C0001 %#increment current position to point to 1st byte of string

%L%(           %#enter while() do{} loop
  %?MT%V010000 %# Var1>0: ie true while still have characters to print
%)             %#end of while test
%(             %#enter do part of loop
  %I%(         %#enter if check
    %(%?EQ%V000001 %?BA
      %(%?LT%MV0F0020 %?BO
        %(%?MT%MV0F007F %?BA %?LT%MV0F00A3%)
      %)
    %)         %#if in quotes & not prinatable character
    %?BO       %#or
    %(%?EQ%V000000 %?BA
      %(%?MT%MV0F00A2 %?BO
        %(%?MT%MV0F001F %?BA %?LT%MV0F0080%)
      %)
    %)             %#not in quotes & printable character
  %)               %#end condition block
  %(               %#start block if true
    "              %#print quote
    %X03000001%V00 %#toggle var1 stateing in quotes
  %)
  %C0F             %#print char at current position, increase current position
  %X0301%V010001   %#decrement var1 by 1
%)                 %#end loop
%I%(               %#start if block
  %?EQ%V000001     %#are we in quotes
%)
%(
  "                %#if so print close quotes
%)
%$-D                %#close data xml tag""",
        "Define Message Length Word": """\
%$A            %#start address xml tag
%F0004         %#number format to same as general address format
%ACA           %#output line address (variable 0x0A) as an address,
               %#don't increment line address(set bit 6),
               %#is variable and not what points to we want (bit 7)
%$-A           %#close address xml tag
%S%S           %#seperator
%$I            %#start instruction xml tag
DMLW           %#output instuction (DMLW or Define Message Length Word)
%$-I           %#close instruction xml tag
%S
%$D            %#start data tag
%X01000000     %#set var0 to 0 (used as flag: 0=out of quotes, 1=in quotes)
%F0200         %#set little endian
%X0101%MWV0F   %#set var1 to contents of current address: string len in bytes
%X020F%V0F0002 %#increment current position to point to 1st byte of string

%L%(           %#enter while() do{} loop
  %?NE%V010000 %# Var1!=0: ie true while still have characters to print
%)             %#end of while test
%(             %#enter do part of loop
  %I%(         %#enter if check
    %(%?EQ%V000001 %?BA
      %(%?LT%MV0F0020 %?BO
        %(%?MT%MV0F007F %?BA %?LT%MV0F00A3%)
      %)
    %)         %#if in quotes & not prinatable character
    %?BO       %#or
    %(%?EQ%V000000 %?BA
      %(%?MT%MV0F00A2 %?BO
        %(%?MT%MV0F001F %?BA %?LT%MV0F0080%)
      %)
    %)             %#not in quotes & printable character
  %)               %#end condition block
  %(               %#start block if true
    "              %#print quote
    %X03000001%V00 %#toggle var1 stateing in quotes
  %)
  %C0F             %#print char at current position, increase current position
  %X0301%V010001   %#decrement var1 by 1
%)                 %#end loop
%I%(               %#start if block
  %?EQ%V000001     %#are we in quotes
%)
%(
  "                %#if so print close quotes
%)
%$-D                %#close data xml tag""",
        "Define Message Length Word Bigendian": """\
%$A            %#start address xml tag
%F0004         %#number format to same as general address format
%ACA           %#output line address (variable 0x0A) as an address,
               %#don't increment line address(set bit 6),
               %#is variable and not what points to we want (bit 7)
%$-A           %#close address xml tag
%S%S           %#seperator
%$I            %#start instruction xml tag
DMLWBE         %#output instuction (DMLWBE or Define Message Length Word Big
               %#Endian)
%$-I           %#close instruction xml tag
%S
%$D            %#start data tag
%X01000000     %#set var0 to 0 (used as flag: 0=out of quotes, 1=inside quotes)
%F0201         %#set big endian
%X0101%MWV0F   %#set var1 to contents of current address: string len in bytes
%X020F%V0F0002 %#increment current position to point to 1st byte of string

%L%(           %#enter while() do{} loop
  %?NE%V010000 %# Var1!=0: ie true while still have characters to print
%)             %#end of while test
%(             %#enter do part of loop
  %I%(         %#enter if check
    %(%?EQ%V000001 %?BA
      %(%?LT%MV0F0020 %?BO
        %(%?MT%MV0F007F %?BA %?LT%MV0F00A3%)
      %)
    %)         %#if in quotes & not prinatable character
    %?BO       %#or
    %(%?EQ%V000000 %?BA
      %(%?MT%MV0F00A2 %?BO
        %(%?MT%MV0F001F %?BA %?LT%MV0F0080%)
      %)
    %)             %#not in quotes & printable character
  %)               %#end condition block
  %(               %#start block if true
    "              %#print quote
    %X03000001%V00 %#toggle var1 stateing in quotes
  %)
  %C0F             %#print char at current position,
                   %#and increase current position
  %X0301%V010001   %#decrement var1 by 1
%)                 %#end loop
%I%(               %#start if block
  %?EQ%V000001     %#are we in quotes
%)
%(
  "                %#if so print close quotes
%)
%$-D                %#close data xml tag""",
        "Custom": ""
        }

    # so can tell order
    DISASSEMBLE_DATABLOCK_CODES_ORDERED = (
        "Define Byte Hex",
        "Define Byte Decimal",
        "Define Byte Octal",
        "Define Byte Binary",
        "Define Byte",
        "Signed Byte Hex",
        "Signed Byte Decimal",
        "Signed Byte Octal",
        "Signed Byte Binary",
        "Signed Byte",
        "Define Word Hex",
        "Define Word Decimal",
        "Define Word Octal",
        "Define Word Binary",
        "Define Word",
        "Signed Word Hex",
        "Signed Word Decimal",
        "Signed Word Octal",
        "Signed Word Binary",
        "Signed Word",
        "Define Word BigEndian Hex",
        "Define Word BigEndian Decimal",
        "Define Word BigEndian Octal",
        "Define Word BigEndian Binary",
        "Define Word BigEndian",
        "Signed Word BigEndian Hex",
        "Signed Word BigEndian Decimal",
        "Signed Word BigEndian Octal",
        "Signed Word BigEndian Binary",
        "Signed Word BigEndian",
        "Define Message",
        "Define Message zero terminated",
        "Define Message bit 7 terminated",
        "Define Message Length Byte",
        "Define Message Length Word",
        "Define Message Length Word Bigendian",
        "Custom")

    DISASSEMBLE_PATTERNBLOCK_CODES = {
        "RST#08 (Error)": """\
%(               %#start test block
  %?EQ%MV0F00CF  %#does the first byte equal 0xCF (code for RST #08)
%)               %#end test block

%(               %#block to define first & last address of data block
  %X0200%V0F0001 %#start position (var0) is position of RST #08 command +1
  %X0101%V00     %#end position (var1) is start position (only 1 byte affter
                 %#                                       error restart)
%)               %#end variable setup block
                 %#start of data handling block
%S%S
%$I              %#start instruction xml tag
DEFB             %#output instuction (DEFB or Define Byte)
%$-I             %#close instruction xml tag
%S
%$D              %#start data tag
%F0000           %#set hex mode
%F0100           %#set unsigned
#%B0F            %#output contents of current address as byte and increment
                 %#current address
%$-D             %#close data tag""",
        "RST#28 (Calculator)": """\
%(                 %#start test block
  %?EQ%MV0F00EF    %#does the first byte equal 0xEF (code for RST #28)
%)                 %#end test block

%(                 %#block to define first & last address of data block
  %X0200%V0F0001   %#start position (var0) is position of RST #28 command +1
  %X0101%V00       %#set end pos (var1) is start position
  %L%(
    %?NE%MV010038  %#loop until reach a byte #38 used to mark end of calculate
  %)
  %(
    %X0201%V010001 %#add 1 to end pos (var1) each time byte is not #38
  %)
%)                 %#end variable setup block

                   %#start of data handling block
%S%S
%$I                %#start instruction xml tag
DEFB               %#output instuction (DEFB or Define Byte)
%$-I               %#close instruction xml tag
%S
%$D                %#start data tag
%F0000             %#set hex mode
%F0100             %#set unsigned
#%B0F              %#output contents of current address as byte and increment
                   %#current address
%$-D               %#close data tag""",
        "Custom": ""
    }

    DISASSEMBLE_PATTERNBLOCK_CODES_ORDERED = (
        "RST#08 (Error)",
        "RST#28 (Calculator)",
        "Custom")

    # list of predefined functions and routines
    PredefinedFunctions = {"DefineByte": _PredefinedDefineByte,
                           "DefineWord": _PredefinedDefineWord,
                           "DefineMessage": _PredefinedDefineMessage}
    PredefinedRoutines = {"DefineByte": _PredefinedDefineByte,
                          "DefineWord": _PredefinedDefineWord,
                          "DefineMessage": _PredefinedDefineMessage,
                          "FindPattern": _PredefinedFindPattern,
                          "StartandEndbyOffset": _PredefinedStartandEndByOffset
                          }

    def __init__(self, arg, start=0, end=65536, data=None):
        """Creates a new DisassembleInstruction which is used to control
        disassembly of Z80 code.

        The only required argument is either a DisassembleInstruction to
        copy, an int of the instruction to carry out, or a string with a
        packed DisassembleInstruction in it (see __str__() for packing
        this string.

        Optional arguments are ignored for everything other than an
        initial int argument.  They are:
        start is the address from where this instruction applies.
        end is the address up to and including that this instruction
        applies.
        data is a string that is needed by the DisassembleInstruction to
        carry out it's instructions.
        """

        # if constructor arg is another DisassembleInstruction then make
        # a copy
        if(isinstance(arg, DisassembleInstruction)):
            data = None if arg.data is None else str(arg.data)
            end = arg.end
            start = arg.start
            arg = arg.instruction

        # if argument is string for instruction type then get code
        if(arg in DisassembleInstruction.DISASSEMBLE_CODES):
            arg = DisassembleInstruction.DISASSEMBLE_CODES[arg]

        # if constructor arg is a string then unpack the contained data
        if(isinstance(arg, str)):
            # break data into components
            parts = arg.split("#", 4)
            arg = int(parts[0], 16)
            start = int(parts[1], 16)
            end = int(parts[2], 16)
            data = parts[4] if len(parts) == 5 else None
            # handle multiline data
            if(len(parts[3]) > 0):
                # re-insert newline characters
                for pos in parts[3].split(','):
                    pos = int(pos, 16)
                    data = data[:pos] + "\n" + data[pos:]

        self.instruction = arg
        self.start = start
        self.end = end
        # make copy of string
        self.data = None if data is None else str(data)

    def isformatinstruction(self):
        """Tests if the DisassembleInstruction is a format instruction.
        """

        return self.instruction != 0 and (self.instruction & 0xFF0000) == 0

    def __str__(self):
        """Returns a String representation of the
        DisassembleInstruction.  This is the instruction code in
        hexadecimal, followed by a '#' followed by the start address in
        hexadecimal, followed by a '#', followed by the end address in
        hexadecimal, followed by a '#'.  If the data property is not
        None then a comma seperated list of positions for new line
        characters in the data field follows, then another '#', and then
        the data field with newline characters stripped out.

        This can be used as an argument to the constructor to create a
        new DisassembleInstruction
        """

        if(self.data is None or self.data == ''):
            return "{0.instruction:X}#{0.start:X}#{0.end:X}#".format(self)

        return "{0.instruction:X}#{0.start:X}#{0.end:X}#{1}#{2}".format(
            self,
            ','.join(["{0:X}".format(i) for i, c in enumerate(self.data) if
                      c == '\n']),
            self.data.replace('\n', ''))

    # for python 3, need lt to sort
    if(sys.hexversion > 0x03000000):
        def __lt__(self, other):
            # defined so can sort by starting address
            if(self.start == other.start):
                return self.end.__lt__(other.end)
            return self.start.__lt__(other.start)

    def disassembledatablock(self, Settings, data):
        """This method will disassemble the given data according to the
        current DisassembleInstruction.
        """

        """
        var[0-9]  %V00-%V09
        line address (not changable)  %V0A
        line number (not changable)   %V0B
        offset from line start        %V0C
        start pos (not changable)     %V0D
        end pos                       %V0E
        current pos (not changable)   %V0F
        """
        Vars = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, self.start, 0, 0, self.start,
                self.end]
        soutput = ""

        # loop through commandline block
        while(Vars[0x0A] <= Vars[0x0E]):
            # check if any comments to be added to this data
            if("COMMENTCONTROL" in Settings):
                # move past any instructions that has been & gone
                dis = Settings["COMMENTCONTROL"][0]
                while(dis and Vars[0x0A] > dis[0].end):
                    dis.pop(0)
                # if is comment instruction process it
                if(dis and
                   Vars[0x0A] >= dis[0].start and
                   dis[0].instruction & 0xFFFF00 == 0x030000 and
                   dis[0].data is not None and dis[0].data is not ""):
                    di = dis.pop(0)
                    if(di.instruction == self.DISASSEMBLE_CODES[
                       "Comment Before"]):
                        if(Settings["COMMENTCONTROL"][1] == 0):
                            soutput += Settings["COMMENTCONTROL"][4](
                                di.data, Settings["XMLOutput"]) + "\n"

                        continue
                    # otherwise comnment end of this line or after
                    if(di.instruction == 0x030002):
                        if(Settings["COMMENTCONTROL"][3] is not ""):
                            Settings["COMMENTCONTROL"][3] += "\n"
                        Settings["COMMENTCONTROL"][3] += di.data
                    else:
                        if(Settings["COMMENTCONTROL"][2] is not ""):
                            Settings["COMMENTCONTROL"][2] += ". "
                        Settings["COMMENTCONTROL"][2] += di.data

                    continue

            Vars[0x0C] = 0  # point to start of line

            # for each line go through commandline instructions
            # character by chracter
            Settings["DATASTRINGPOS"] = 0

            # output start line if needed
            if(Settings["XMLOutput"] == 1):
                soutput += '  <line>'
            Settings["HadLineStart"] = True
            Settings["HadLineEnd"] = False

            while(Settings["DATASTRINGPOS"] < len(self.data)):
                # make note of where command starts in case we have
                # error
                commandstart = Settings["DATASTRINGPOS"]

                # get next char
                s = _getnextcharacters(self.data, Settings, 1)

                if(s == ""):
                    break

                # deal with non-control characters first
                if(s[0] != '%'):
                    soutput += getspectrumchar(s[0],
                                               Settings["HexForNonASCII"])
                    continue

                # reset position
                Settings["DATASTRINGPOS"] = commandstart

                # deal with any instructions
                # can ignore result
                try:
                    res, txt = _processcommandblock(self.data, Vars, Settings,
                                                    data, False, False)
                except IndexError:
                    raise _newSpectrumTranslateError(
                        Vars[0x0A], 0, self.data,
                        "attempt to access data outside of supplied code")

                soutput += txt

            # update line address
            Vars[0x0A] += Vars[0x0C]
            # update line number
            Vars[0x0B] += 1

            # do comment
            if("COMMENTCONTROL" in Settings and
               Settings["COMMENTCONTROL"][1] == 0 and
               Settings["COMMENTCONTROL"][2] is not ""):
                # XML comments
                if(Settings["XMLOutput"] == 1):
                    soutput += "<comment>{0}</comment>".format(
                        Settings["COMMENTCONTROL"][2])
                # plain text comments
                else:
                    # output pre comment text
                    soutput += Settings["SEPERATOR"] + ';'

                    if(Settings["COMMENTCONTROL"][2].find("\n") == -1):
                        soutput += Settings["COMMENTCONTROL"][2]

                    else:
                        comments = Settings["COMMENTCONTROL"][2].split("\n")
                        soutput += comments[0]
                        if(Settings["COMMENTCONTROL"][3] is not ""):
                            Settings["COMMENTCONTROL"][3] = "\n" +\
                                Settings["COMMENTCONTROL"][3]
                        Settings["COMMENTCONTROL"][3] = "\n".join(
                            comments[1:]) + Settings["COMMENTCONTROL"][3]

            if(not Settings["HadLineEnd"]):
                # output end start line if needed
                if(Settings["XMLOutput"] == 1):
                    soutput += '</line>'

                # new line
                soutput += "\n"

            # handle comments after line
            if("COMMENTCONTROL" in Settings):
                if(Settings["COMMENTCONTROL"][1] == 0 and
                   Settings["COMMENTCONTROL"][3] is not ""):
                    soutput += Settings["COMMENTCONTROL"][4](
                        Settings["COMMENTCONTROL"][3],
                        Settings["XMLOutput"]) + "\n"

                # clear comments
                Settings["COMMENTCONTROL"][2] = ""
                Settings["COMMENTCONTROL"][3] = ""

        # return end of data block as might have changed
        return Vars[0x0E], soutput


def isfindandcomment(instructions):
    """Tests if the supplied instructions is a valid find and comment
    routine.

    Note that this routine is not perfect, as to be so would be too
    complex.  It simply ensures that the code can be broken into three
    sections like a pattern data block, and that the first section
    contains the %; command.
    """

    test, prep, action = getpartsofpatterndatablock(instructions)

    # must have a test area and must contain %;
    if(not test or test.find("%;") == -1):
        return False

    return True


def _numbertostring(n, bits, form, typeindicator=True):
    """format: 0=hex,1=decimal,2=octal,3=binary
    typeindictor specifies display type specifer before number: "" for
    decimal, "#" for hex, "b" for binary, "o" for octal.
    """
    if(form == 0):
        # hex
        return ("{0}{1:0" + str(bits >> 2) + "X}").format(
            "#" if typeindicator else "", n)

    elif(form == 1):
        # decimal
        return "{0}".format(n)

    elif(form == 2):
        # octal
        return ("{0}{1:0" + str((bits + 2)//3) + "o}").format(
            "o" if typeindicator else "", n)

    elif(form == 3):
        # binary
        return ("{0}{1:0" + str(bits) + "b}").format(
            "b" if typeindicator else "", n)

    else:
        return ""


def _getnextcharacters(instructions, Settings, numberToGet):
    """Returns required number of characters skipping space, new line,
    tabs, and comments.
    """

    s = ""

    # loop until have requested number of non whitespace characters or
    # hit end of commands
    while(len(s) < numberToGet and
          Settings["DATASTRINGPOS"] < len(instructions)):
        c = instructions[Settings["DATASTRINGPOS"]]

        # if found comment, move to end of line
        if(c == '%' and len(instructions) > Settings["DATASTRINGPOS"] + 1 and
           instructions[Settings["DATASTRINGPOS"] + 1] == "#"):
            # check just incase have %%# which is display %#
            escapes = 1
            # see how far back escapes go back
            while(escapes > Settings["DATASTRINGPOS"] and
                  instructions[Settings["DATASTRINGPOS"]-escapes] == "%"):
                escapes += 1

            # should have an odd number of escapes if this a comment
            if(escapes & 1 == 1):
                # move position to new line character
                Settings["DATASTRINGPOS"] = instructions.find(
                    "\n", Settings["DATASTRINGPOS"])
                # if newline not found,
                if(Settings["DATASTRINGPOS"] == -1):
                    # set to end of line
                    Settings["DATASTRINGPOS"] = len(instructions)

                # loop back to deal with next character
                continue

            # otherwise is a hash to display

        if(c != ' ' and c != '\t' and c != '\n'):
            s += c
        Settings["DATASTRINGPOS"] += 1

    return s


def _movetoblockend(instructions, Vars, Settings, commandstart):
    """move to end of specified command block"""

    # for each line go through commands instructions character by
    # chracter
    while(Settings["DATASTRINGPOS"] < len(instructions)):
        # get next char
        s = _getnextcharacters(instructions, Settings, 1)

        if(s == ""):
            break

        # skip non-control characters first
        if(s != "%"):
            continue

        # get next char
        s = _getnextcharacters(instructions, Settings, 1)

        if(s == ""):
            break

        # what command is it?
        if(s[0] == "("):
            # move to end of nested block
            _movetoblockend(instructions, Vars, Settings, commandstart)

        # return if found end of block
        elif(s[0] == ')'):
            return

        # otherwise skip command

    # should always find end of block with close brackets, error if
    # block not closed
    raise _newSpectrumTranslateError(Vars[0x0A], commandstart, instructions,
                                     "no closing brackets to block")


def _processcommandblock(instructions, Vars, Settings, data, inBrackets,
                         InTest):
    """processes an instruction block.
       return bit 0 1=true, 0=false
       bit 1 2=break, 0=not break
       bit 2 4=continue, 0=not continue
       ,output text
    """

    # nested functions needed by _processcommandblock
    def inc_var_if_needed(var_num, Vars, inc_amount):
        """increment variable if apropriate"""
        if((var_num & 0x40) == 0 and ((var_num & 0x3F) < 0x0A or
           (var_num & 0x3F) == 0x0C or (var_num & 0x3F) == 0x0F)):
            Vars[0x0C if ((var_num & 0x3F) == 0x0F) else
                 var_num & 0x3F] += inc_amount

    def get_number_var_or_memory(instructions, Vars, Settings, data,
                                 commandstart):
        # how many bytes are we getting
        getByte = True
        # remember where we started
        pos = Settings["DATASTRINGPOS"]

        # get next char
        s = _getnextcharacters(instructions, Settings, 1)

        if(s == ""):
            raise _newSpectrumTranslateError(
                Vars[0x0A], commandstart, instructions,
                "Invalid variable or number definition")

        # first check if is a number
        if(s[0] != "%"):
            # restore pointer to where it was
            Settings["DATASTRINGPOS"] = pos

            # extract number
            i = int(_getnextcharacters(instructions, Settings, 4), 16)
            # deal with error
            if(i < 0):
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "number must be 4 digit hexadecimal number")

            return i

        # get next char
        s = _getnextcharacters(instructions, Settings, 1)

        if(s[0] == "V"):
            # get variable number
            i = int(_getnextcharacters(instructions, Settings, 2), 16)
            # deal with invalid variable number
            if(i < 0 or i > 0x0F):
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions, "invalid variable")

            # return variable's content
            return Vars[0x0A] + Vars[0x0C] if (i == 0x0F) else Vars[i]

        # should now be 'M', handle if not
        if(s[0] != "M"):
            raise _newSpectrumTranslateError(
                Vars[0x0A], commandstart, instructions,
                "argument must be number, variable, or memory content")

        pos = Settings["DATASTRINGPOS"]

        # get next char
        s = _getnextcharacters(instructions, Settings, 1)

        # if next char is 'W' then need to get 2 bytes
        if(s[0] == "W"):
            # make note we need word not byte
            getByte = False

            # get next char
            s = _getnextcharacters(instructions, Settings, 1)

            pos = Settings["DATASTRINGPOS"]

        # now get into i address of where to extract data from

        # if next char is 'V' then variable pointing to memory address
        if(s[0] == "V"):
            # get variable number
            i = int(_getnextcharacters(instructions, Settings, 2), 16)
            # deal with invalid variable number
            if(i < 0 or i > 0x0F):
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "invalid variable number for memory address")

            # get number variable's content
            i = Vars[0x0A] + Vars[0x0C] if (i == 0x0F) else Vars[i]

        # otherwise should be 4 hex digit address
        else:
            # in checking to see if next char was V will move pointer,
            # so reset to where it should be
            Settings["DATASTRINGPOS"] = pos

            # extract number
            i = int(_getnextcharacters(instructions, Settings, 4), 16)
            # deal with error
            if(i < 0):
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "should be 4 digit hexadecimal number for memory address")

        # now have address we need to extract in i, and if we want byte
        # or not in getByte
        # deal with byte
        if(getByte):
            return data[i-Settings["ORIGIN"]]

        # deal with word taking into account endedness of number we want
        return data[i-Settings["ORIGIN"] + Settings["NUMBERWORDORDER"]] + \
            256*data[i-Settings["ORIGIN"] +
                     1-Settings["NUMBERWORDORDER"]]

    def combineresults(mode, a, b):
        if(mode == 0):
            return a and b
        if(mode == 1):
            return a or b
        if(mode == 2):
            return a ^ b

    # end of _processcommandblock's nested functions

    boolState = False
    boolMode = 1      # 0=and, 1=or, 2=xor
    soutput = ""

    # for each line go through commands instructions character by
    # character
    while(Settings["DATASTRINGPOS"] < len(instructions)):
        # make note of where command starts in case we have error
        commandstart = Settings["DATASTRINGPOS"]

        # get next char
        s = _getnextcharacters(instructions, Settings, 1)

        if(s == ""):
            break

        # deal with non-control characters first
        if(s[0] != '%'):
            soutput += getspectrumchar(s[0], Settings["HexForNonASCII"])
            continue

        # space after % will get missed by _getnextcharacters so handle
        if(instructions[Settings["DATASTRINGPOS"]] == ' '):  # output space
            soutput += ' '
            continue

        # get next char (command
        s = _getnextcharacters(instructions, Settings, 1)

        # what command is it?
        if(s[0] == 'F'):  # //format settings
            # get sub command & which format
            i = int(_getnextcharacters(instructions, Settings, 4), 16)
            if((i >> 8) == 0):  # format hex/decimal/octal/binary
                if((i & 0xFF) > 6):
                    raise _newSpectrumTranslateError(
                        Vars[0x0A], commandstart, instructions,
                        "Number format argument must be 0 to 6")

                if((i & 0xFF) == 4):
                    Settings["NUMBERFORMAT"] = Settings["ADDRESSOUTPUT"]

                elif((i & 0xFF) == 5):
                    Settings["NUMBERFORMAT"] = Settings["NUMBEROUTPUT"]

                elif((i & 0xFF) == 6):
                    Settings["NUMBERFORMAT"] = Settings["COMMANDOUTPUT"]

                else:
                    Settings["NUMBERFORMAT"] = i & 0xFF

            elif((i >> 8) == 1):  # number unsigned/signed
                if((i & 0xFF) > 1):
                    raise _newSpectrumTranslateError(
                        Vars[0x0A], commandstart, instructions,
                        "Number sign argument must be 0 or 1")

                Settings["NUMBERSIGNED"] = i & 0xFF

            elif((i >> 8) == 2):  # word mode little/big endian
                if((i & 0xFF) > 1):
                    raise _newSpectrumTranslateError(
                        Vars[0x0A], commandstart, instructions,
                        "Word endedness argument must be 0 or 1")

                Settings["NUMBERWORDORDER"] = i & 0xFF

            elif((i >> 8) == 3):  # display line address every X line
                k = int(_getnextcharacters(instructions, Settings, 2), 16)
                if(k < 0 or k > 255):
                    raise _newSpectrumTranslateError(
                        Vars[0x0A], commandstart, instructions,
                        "Display line address every X line argument must be 2 \
digit hexadecimal number")

                Settings["DISPLAYEVERYXLINES"] = k + ((i & 0xFF) << 8)

            elif((i >> 8) == 4):  # separator to space/tab/default
                if((i & 0xFF) > 2):
                    raise _newSpectrumTranslateError(
                        Vars[0x0A], commandstart, instructions,
                        "Seperator setting argument must be 0 to 2")

                if((i & 0xFF) == 0):
                    Settings["SEPERATOR"] = "  "

                elif((i & 0xFF) == 1):
                    Settings["SEPERATOR"] = "\t"

                else:
                    Settings["SEPERATOR"] = Settings["ORIGIONALSEPERATOR"]

            elif((i >> 8) == 5):  # blank line after data default/always/never
                if((i & 0xFF) > 2):
                    raise _newSpectrumTranslateError(
                        Vars[0x0A], commandstart, instructions,
                        "line after data setting argument must be 0 to 2")

                if((i & 0xFF) == 0):
                    if("LINEAFTERDATA" in Settings):
                        del Settings["LINEAFTERDATA"]
                else:
                    Settings["LINEAFTERDATA"] = (i & 0xFF) == 1

            else:
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "unrecognised format setting")

        elif(s[0] == '!'):  # process predefined routine
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "Predefined routines not allowed inside instructions. Use \
predefined Functions instead.")

        elif(s[0] == 'P'):  # process predefined function
            # get details of command and it's arguments
            details = _ProcessFunctionDetails(
                instructions[Settings["DATASTRINGPOS"]:])
            if(isinstance(details, str)):
                raise _newSpectrumTranslateError(Vars[0x0A], commandstart,
                                                 instructions, details)

            # check is valid command
            if(details[0] not in DisassembleInstruction.PredefinedFunctions):
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    'function "{0}" not defined'.format(details[0]))

            # process function and combine result
            args = [data, Settings, Vars] + details[1]
            keyargs = details[2]
            result = DisassembleInstruction.PredefinedFunctions[details[0]](
                *args, **keyargs)
            # extract text and logic from result
            if(isinstance(result, (str, (_unistr, str)))):
                txt = result
                logic = None
            elif(isinstance(result, (bool, int))):
                txt = None
                logic = result
            elif(isinstance(result, (list, tuple)) and len(result) > 1 and
                 isinstance(result[1], (str, (_unistr, str))) and
                 isinstance(result[0], (bool, int))):
                txt = result[1]
                logic = result[0]
            elif(isinstance(result, (list, tuple)) and len(result) > 1 and
                 isinstance(result[0], (str, (_unistr, str))) and
                 isinstance(result[1], (bool, int))):
                txt = result[0]
                logic = result[1]
            elif(isinstance(result, (list, tuple)) and len(result) > 0 and
                 isinstance(result[0], (str, (_unistr, str)))):
                txt = result[0]
                logic = None
            elif(isinstance(result, (list, tuple)) and len(result) > 0 and
                 isinstance(result[0], (bool, int))):
                txt = None
                logic = result[0]
            else:
                txt = None
                logic = None

            # update pointer to instructions
            Settings["DATASTRINGPOS"] += details[3]

            # process text and logic
            if(txt):
                soutput += txt
            if(logic is not None and isinstance(logic, bool)):
                boolState = combineresults(boolMode, boolState, logic)
            elif(logic is not None and isinstance(logic, int)):
                boolState = combineresults(boolMode, boolState,
                                           (logic & 1) == 1)
            # if break or continue, leave, this will be False for bool
            if(isinstance(logic, int) and logic & 6 != 0):
                # leave block
                return (logic & 6) + (1 if boolState else 0), soutput

        elif(s[0] == 'B'):  # ouput byte
            # get info
            i = int(_getnextcharacters(instructions, Settings, 2), 16)
            if((i & 0x3F) == 0x3F):  # dealing with addresses
                # get address
                k = int(_getnextcharacters(instructions, Settings, 4), 16)
                # getbyte at address, adjust for offset
                k = data[k-Settings["ORIGIN"]]

            elif((i & 0x3F) < 0x10):
                # get variable content
                k = Vars[0x0A] + \
                    Vars[0x0C] if ((i & 0x3F) == 0x0F) else Vars[i & 0x3F]
                # get content of memory address if this is a reference
                if((i & 0x80) == 0):
                    k = data[k-Settings["ORIGIN"]]
                # increment if apropriate
                inc_var_if_needed(i, Vars, 1)

            else:
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "invalid byte output argument")

            # handle negative number if signed and not an address
            if(Settings["NUMBERSIGNED"] == 1 and (i & 0x80) == 0x80):
                k = 0x100-k
                soutput += "-"

            # output byte
            soutput += _numbertostring(k, 8, Settings["NUMBERFORMAT"], False)

        elif(s[0] == 'W'):  # output word
            # get info
            i = int(_getnextcharacters(instructions, Settings, 2), 16)
            if((i & 0x3F) == 0x3F):  # dealing with addresses
                # get address
                k = int(_getnextcharacters(instructions, Settings, 4), 16)
                # getbyte, adjust for offset
                k = data[k-Settings["ORIGIN"] +
                         Settings["NUMBERWORDORDER"]] + \
                    256*data[k-Settings["ORIGIN"] +
                             1-Settings["NUMBERWORDORDER"]]

            elif((i & 0x3F) < 0x10):
                # get variable content
                k = Vars[0x0A] + \
                    Vars[0x0C] if ((i & 0x3F) == 0x0F) else Vars[i & 0x3F]
                # get content of memory address if this is a reference
                if((i & 0x80) == 0):
                    k = data[k-Settings["ORIGIN"] +
                             Settings["NUMBERWORDORDER"]] + \
                        256*data[k-Settings["ORIGIN"] +
                                 1-Settings["NUMBERWORDORDER"]]

                # increment if apropriate
                inc_var_if_needed(i, Vars, 2)

            else:
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "invalid number output argument")

            # handle negative number if signed and not an addrss
            if(Settings["NUMBERSIGNED"] == 1 and (i & 0x80) == 0x80):
                k = 0x100-k
                soutput += "-"

            # output word
            soutput += _numbertostring(k, 16, Settings["NUMBERFORMAT"], False)
            # remember number incase it is line number
            if("ReferencedLineNumbers" in Settings):
                Settings["ReferencedLineNumbers"] += [k]

        elif(s[0] == 'A'):  # output address
            # get info
            i = int(_getnextcharacters(instructions, Settings, 2), 16)
            if((i & 0x3F) == 0x3F):  # dealing with addresses
                # get address
                k = int(_getnextcharacters(instructions, Settings, 4), 16)
                # getbyte, adjust for offset
                k = data[k-Settings["ORIGIN"] +
                         Settings["NUMBERWORDORDER"]] + \
                    256*data[k-Settings["ORIGIN"] +
                             1-Settings["NUMBERWORDORDER"]]

            elif((i & 0x3F) < 0x10):
                # get variable content
                k = Vars[0x0A] + \
                    Vars[0x0C] if ((i & 0x3F) == 0x0F) else Vars[i & 0x3F]
                # get content of memory address if this is a reference
                if((i & 0x80) == 0):
                    k = data[k-Settings["ORIGIN"] +
                             Settings["NUMBERWORDORDER"]] + \
                        256*data[k-Settings["ORIGIN"] +
                                 1-Settings["NUMBERWORDORDER"]]
                # increment if apropriate
                inc_var_if_needed(i, Vars, 2)

            else:
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "invalid address output argument")

            # output address
            if(Settings["XMLOutput"] == 1):
                soutput += _numbertostring(k, 16, Settings["NUMBERFORMAT"],
                                           False)

            else:
                i = Settings["ADDRESSOUTPUT"] + 4
                if(Settings["SEPERATOR"] != "  "):
                    i += 1 << 5
                soutput += "\0" + chr(i) + chr(Settings["DISPLAYEVERYXLINES"])
                soutput += _numbertostring(k, 16, 0, False)

        # output char, defaults to unsigned byte if not printable
        elif(s[0] == 'C'):
            # get info
            i = int(_getnextcharacters(instructions, Settings, 2), 16)
            if((i & 0x3F) == 0x3F):  # dealing with addresses
                # get address
                k = int(_getnextcharacters(instructions, Settings, 4), 16)
                # getbyte, adjust for offset
                k = data[k-Settings["ORIGIN"]]

            elif((i & 0x3F) < 0x10):
                # get variable content
                k = Vars[0x0A] + \
                    Vars[0x0C] if ((i & 0x3F) == 0x0F) else Vars[i & 0x3F]
                # get content of memory address if this is a reference
                if((i & 0x80) == 0):
                    k = data[k-Settings["ORIGIN"]]
                # increment if apropriate
                inc_var_if_needed(i, Vars, 1)

            else:
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "invalid character output argument")

            # output character
            soutput += getspectrumchar(k, Settings["HexForNonASCII"])

        elif(s[0] == 'G'):  # output 5 byte floating point number
            # get info
            i = int(_getnextcharacters(instructions, Settings, 2), 16)
            if((i & 0x3F) == 0x3F):  # dealing with addresses
                # get address
                k = int(_getnextcharacters(instructions, Settings, 4), 16)
                # get and output floating point number
                soutput += str(SpectrumNumber(data[k-Settings["ORIGIN"]:
                                                   k-Settings["ORIGIN"] + 5]))

            elif((i & 0x3F) < 0x10):
                # get variable content
                k = Vars[0x0A] + \
                    Vars[0x0C] if ((i & 0x3F) == 0x0F) else Vars[i & 0x3F]
                # has to be a memory address that holds 5 byte number
                if((i & 0x80) != 0):
                    raise _newSpectrumTranslateError(
                        Vars[0x0A], commandstart, instructions,
                        "invalid floating point number output argument")

                # get and output floating point number
                soutput += str(SpectrumNumber(data[k-Settings["ORIGIN"]:
                                                   k-Settings["ORIGIN"] + 5]))
                # increment if apropriate
                inc_var_if_needed(i, Vars, 5)

            else:
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "invalid floating point number output argument")

        elif(s[0] == '%'):  # output '%'
            soutput += '%'

        elif(s[0] == 'S'):  # output seperator
            # only output if not in xml mode
            if(Settings["XMLOutput"] == 0):
                soutput += Settings["SEPERATOR"]

        elif(s[0] == 'N'):  # output newline
            soutput += '\n'

        elif(s[0] == 'T'):  # output tab
            soutput += '\t'

        # maths
        elif(s[0] == 'X'):
            # get sub command
            i = int(_getnextcharacters(instructions, Settings, 2), 16)
            # check if valid command
            if(i < 0 or i > 9):
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "invalid arithmetic operation. Must be 0 to 9")

            # where to store result
            result = int(_getnextcharacters(instructions, Settings, 2), 16)
            # check is valid resultlocation
            if(result < 0 or (result > 9 and result != 0x0C and
               result != 0x0E and result != 0x0F)):
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "invalid arithmetic destination")

            # get first argument
            arga = get_number_var_or_memory(instructions, Vars, Settings, data,
                                            commandstart)
            # get 2nd argument if needed & keep compiler happy otherwise
            argb = get_number_var_or_memory(instructions, Vars, Settings, data,
                                            commandstart) if (i != 1) else 0

            # now process variables
            if(i == 1):    # let
                k = arga
            elif(i == 2):  # add
                k = arga + argb
            elif(i == 3):  # subtract
                k = arga - argb
            elif(i == 4):  # multiply
                k = arga * argb
            elif(i == 5):  # divide
                k = arga // argb
            elif(i == 6):  # modulus
                k = arga % argb
            elif(i == 7):  # binary and
                k = arga & argb
            elif(i == 8):  # binary or
                k = arga | argb
            elif(i == 9):  # binary xor
                k = arga ^ argb
            else:
                k = 0

            # ensure is 16 bit result
            k &= 0xFFFF

            # save variable
            if(result == 0x0F):
                Vars[0x0C] = k-Vars[0x0A]
            else:
                Vars[result] = k

        # flow
        elif(s[0] == '('):
            # process contents of brackets and combine result
            i, txt = _processcommandblock(instructions, Vars, Settings, data,
                                          True, InTest)
            soutput += txt
            boolState = combineresults(boolMode, boolState, (i & 1) == 1)
            i = i & 6
            # if break or continue, leave
            if(i != 0):
                # move to end of current block
                _movetoblockend(instructions, Vars, Settings, commandstart)
                # leave block
                return i + (1 if boolState else 0), soutput

        elif(s[0] == ')'):
            # if not in brackets  then error
            if(not inBrackets):
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "Closing brackets without opening brackets")

            # otherwise ought to return from command
            return 1 if boolState else 0, soutput

        elif(s[0] == 'I'):  # if then block
            # should have brackets afterwards
            if(_getnextcharacters(instructions, Settings, 2) != "%("):
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "bracket bound test must follow if statement")

            # test if block
            result, txt = _processcommandblock(instructions, Vars, Settings,
                                               data, True, True)
            bTest = (result & 1) == 1
            soutput += txt

            # should have brackets afterwards for instruction block
            if(_getnextcharacters(instructions, Settings, 2) != "%("):
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "bracket bound action must follow if test")

            # signal no break or continue
            k = 0
            # if contition met then process block
            if(bTest):
                k, txt = _processcommandblock(instructions, Vars, Settings,
                                              data, True, InTest)
                soutput += txt

            # otherwise move past command block
            else:
                _movetoblockend(instructions, Vars, Settings, commandstart)

            # save position before checking to see if is else statement
            # following
            i = Settings["DATASTRINGPOS"]
            # see if is an else block
            if(_getnextcharacters(instructions, Settings, 2) == "%J"):
                # should have brackets afterwards for instruction block
                if(_getnextcharacters(instructions, Settings, 2) != "%("):
                    raise _newSpectrumTranslateError(
                        Vars[0x0A], commandstart, instructions,
                        "bracket bound action must follow else statement")

                # process block
                k, txt = _processcommandblock(instructions, Vars, Settings,
                                              data, True, InTest)
                if(not bTest):
                    soutput += txt

            # otherwise reset string position
            else:
                Settings["DATASTRINGPOS"] = i

            # if break or continue happened inside if or else block then
            # leave
            if((k & 6) != 0):
                # move to end of current block
                _movetoblockend(instructions, Vars, Settings, commandstart)
                # leave block
                return k, soutput

        elif(s[0] == 'L'):  # while do loop
            # should have brackets afterwards
            if(_getnextcharacters(instructions, Settings, 2) != "%("):
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "bracket bound test must follow loop statement")

            # make note of where while do loop starts
            i = Settings["DATASTRINGPOS"]

            bTest = True

            # loop until test condition is false;
            while(bTest):
                # set where while do loop starts
                Settings["DATASTRINGPOS"] = i

                # test if block
                result, txt = _processcommandblock(instructions, Vars,
                                                   Settings, data, True, True)
                bTest = (result & 1) == 1
                soutput += txt

                # should have brackets afterwards for instruction block
                if(_getnextcharacters(instructions, Settings, 2) != "%("):
                    raise _newSpectrumTranslateError(
                        Vars[0x0A], commandstart, instructions,
                        "bracket bound action must follow loop test")

                # if contition met then process block
                if(bTest):
                    result, txt = _processcommandblock(instructions, Vars,
                                                       Settings, data, True,
                                                       InTest)
                    soutput += txt
                    if((result & 2) == 2):
                        # if break from routine then break out of loop

                        # move to end of current block
                        _movetoblockend(instructions, Vars, Settings,
                                        commandstart)

                        break

                # otherwise move past command block
                if(not bTest):
                    _movetoblockend(instructions, Vars, Settings,
                                    commandstart)

        # end data block
        elif(s[0] == 'Q'):
            # setting end of data block as current position, then ending
            # line will quit data block
            Vars[0x0E] = Vars[0x0A] + Vars[0x0C] - 1

            # by setting position to end of data string and returning,
            # this will end line
            Settings["DATASTRINGPOS"] = len(instructions)
            return 1 if boolState else 0, soutput

        # end line
        elif(s[0] == 'E'):
            # by setting position to end of data string and returning,
            # this will end line
            Settings["DATASTRINGPOS"] = len(instructions)
            return 1 if boolState else 0, soutput

        # break;
        elif(s[0] == 'Y'):
            # return
            return 3 if boolState else 2, soutput

        # continue
        elif(s[0] == 'Z'):
            # return
            return 5 if boolState else 4, soutput

        # comparitors
        elif(s[0] == '?'):
            # get next chars
            comp = _getnextcharacters(instructions, Settings, 2)

            # check if mode change
            if(comp[0] == 'B'):
                if(comp[1] == 'A'):  # and
                    boolMode = 0
                elif(comp[1] == 'O'):  # or
                    boolMode = 1
                elif(comp[1] == 'X'):  # xor
                    boolMode = 2
                else:  # unrecognised mode command
                    raise _newSpectrumTranslateError(
                        Vars[0x0A], commandstart, instructions,
                        "unrecognised boolean combination mode")

                continue

            # have we tested enough already?
            # can we end testing based on results so far without further
            # testing?
            if(InTest and (    # are we in a test situation?
               # are we anding with false: answer will be false
               (boolMode == 0 and not boolState) or
               # are we oring with true: answer will be true
               (boolMode == 1 and boolState))
               ):
                # can leave test as have found answer
                # move to end of current block
                _movetoblockend(instructions, Vars, Settings, commandstart)
                # return from test block
                return 1 if boolState else 0, soutput

            # should now be tests
            # get which one
            try:
                i = {"LT": 0, "MT": 1, "EQ": 2, "LE": 3, "ME": 4,
                     "NE": 5}[comp]
            except:
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "unrecognised comparison")

            # get 2 arguments
            arga = get_number_var_or_memory(instructions, Vars, Settings, data,
                                            commandstart)
            # get 2nd argument if needed
            argb = get_number_var_or_memory(instructions, Vars, Settings, data,
                                            commandstart)

            # now do text
            if(i == 0):  # less than
                boolState = combineresults(boolMode, boolState, arga < argb)
            elif(i == 1):  # more than
                boolState = combineresults(boolMode, boolState, arga > argb)
            elif(i == 2):  # equal
                boolState = combineresults(boolMode, boolState, arga == argb)
            elif(i == 3):  # less than or equal
                boolState = combineresults(boolMode, boolState, arga <= argb)
            elif(i == 4):  # more than or equal
                boolState = combineresults(boolMode, boolState, arga >= argb)
            elif(i == 5):  # not equal
                boolState = combineresults(boolMode, boolState, arga != argb)

        # XML tags
        elif(s[0] == '$'):
            # default to normal tag
            emptytag = False
            closetag = False

            # get next char
            nextchar = _getnextcharacters(instructions, Settings, 1)

            # check & handle empty tag
            if(nextchar == '$'):
                emptytag = True
                nextchar = _getnextcharacters(instructions, Settings, 1)

            # check and handle closeing tag
            elif(nextchar == '-'):
                closetag = True
                nextchar = _getnextcharacters(instructions, Settings, 1)

            # now figure out command
            if(nextchar == 'A'):
                tag = 'address'

            elif(nextchar == 'B'):
                tag = 'bytes'

            elif(nextchar == 'C'):
                tag = 'comment'

            elif(nextchar == 'D'):
                tag = 'data'

            elif(nextchar == 'F'):
                tag = 'flags'

            elif(nextchar == 'I'):
                tag = 'instruction'

            elif(nextchar == 'L'):
                tag = 'line'

            elif(nextchar == 'T'):
                tag = 'timeing'

            elif(nextchar == '<'):
                # get position of closeing bracket
                closepos = instructions.find(">", Settings["DATASTRINGPOS"])

                # handle no closeing bracket
                if(closepos == -1):
                    raise _newSpectrumTranslateError(
                        Vars[0x0A], commandstart, instructions,
                        "no closeing bracket on XML tag")

                # get tag name from between brackets
                tag = instructions[Settings["DATASTRINGPOS"]:closepos]
                # update instructions position
                Settings["DATASTRINGPOS"] = closepos + 1

            else:
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "unrecognised predefined XML tag")

            # if in xml mode then output tag
            if(Settings["XMLOutput"] == 1):
                if(not closetag and tag == 'line'):
                    sputput += "  "

                soutput += '<'

                if(closetag):
                    soutput += '/'

                soutput += tag

                if(emptytag):
                    soutput += '/'

                soutput += '>'

        # add comment
        elif(s[0] == ';'):
            commentstart = get_number_var_or_memory(instructions, Vars,
                                                    Settings, data,
                                                    commandstart)
            commentend = get_number_var_or_memory(instructions, Vars, Settings,
                                                  data, commandstart)

            # get what comment is to be
            nextchar = _getnextcharacters(instructions, Settings, 1)
            if(nextchar == "0"):
                commentinstruction = DisassembleInstruction.\
                    DISASSEMBLE_CODES["Comment"]
            elif(nextchar == "1"):
                commentinstruction = DisassembleInstruction.\
                    DISASSEMBLE_CODES["Comment Before"]
            elif(nextchar == "2"):
                commentinstruction = DisassembleInstruction.\
                    DISASSEMBLE_CODES["Comment After"]
            else:
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "bad comment position")

            # find out where to get comment from
            nextchar = _getnextcharacters(instructions, Settings, 1)

            # check if comment is text to end of line
            if(nextchar == "1"):
                # find end of line
                endofline = instructions.find("\n", Settings["DATASTRINGPOS"])
                # if newline not found, set to end of line
                if(endofline == -1):
                    endofline = len(instructions)

                # set comment to be text to end of line
                commenttext = nextchar + instructions[
                    Settings["DATASTRINGPOS"]:endofline]

                # move current position past end of line
                Settings["DATASTRINGPOS"] = endofline

            # if is text so far
            elif(nextchar == "0"):
                commenttext = soutput

            # otherwise has been incorrect value
            else:
                raise _newSpectrumTranslateError(
                    Vars[0x0A], commandstart, instructions,
                    "bad comment source")

            # create instruction
            di = DisassembleInstruction(commentinstruction, commentstart,
                                        commentend, commenttext)
            # add to list of instructions
            Settings["InstructionsToAdd"] += [di]

        else:  # unrecognised command
            raise _newSpectrumTranslateError(
                Vars[0x0A], commandstart, instructions, "unrecognised command")

    return 1 if boolState else 0, soutput


def _ProcessFunctionDetails(txt):
    # get function name, arguments, and offset to end of call

    # get function name or fail
    x = re.match("([a-zA-Z_][a-zA-Z_0-9]*)[(]", txt)
    if(not x):
        return "Invalid function name"
    function_name = x.group(1)
    # remove function name from text
    length = x.end()
    txt = txt[length:]

    args = []
    argmatch = re.compile("\s*(?:([a-zA-Z_][a-zA-Z_0-9]*)(?:\s*[=]\s*))?\
(\"[^\"]*\"|\'[^\']*\'|\-?#[0-9a-fA-F]+|-?0[xX][0-9a-fA-F]+|-?o[0-7]+|\
-?[0-9]+|-?b[0-1]+|[Tt][Rr][Uu][Ee]|[Ff][Aa][Ll][Ss][Ee])\s*,?", re.DOTALL)
    keywordsused = 0
    # cycle through the arguments
    while(True):
        # return error if end text without closing bracket
        if(not txt):
            return "No closing bracket"
        # end loop if have hit end bracket
        if(txt[0] == ')'):
            break
        # match string, boolean or number
        x = argmatch.match(txt)
        if(not x or len(x.groups()) != 2):
            return "Invalid argument: " + txt
        if(keywordsused == 1 and not x.group(1)):
            return "Can't declare non-keyword argument after keyword argument"
        if(x.group(1)):
            keywordsused = 1
            args += [[x.group(1), x.group(2)]]
        else:
            keywordsused = 0
            args += [x.group(2)]
        txt = txt[x.end():]
        length += x.end()

    # convert text args into string, int, or boolean
    # add to list or dict
    keys = {}
    nonkeys = []
    for a in args:
        arg = a[1] if isinstance(a, list) else a
        c = arg[0]
        if(c == '-'):
            isminus = True
            arg = arg[1:]
            c = arg[0]
        else:
            isminus = False
        if(c == '"' or c == "'"):
            arg = str(arg[1:-1])
        elif(c == 'T' or c == 't'):
            arg = True
        elif(c == 'F' or c == 'f'):
            arg = False
        elif(c == '#'):
            arg = int(arg[1:], 16)
        elif(c == '0' and len(arg) > 1 and (arg[1] == 'x' or arg[1] == 'X')):
            arg = int(arg[2:], 16)
        elif(c == 'o'):
            arg = int(arg[1:], 8)
        elif(c == 'b'):
            arg = int(arg[1:], 2)
        else:
            arg = int(arg)

        if(isminus):
            arg *= -1

        if(isinstance(a, list)):
            keys[a[0]] = arg
        else:
            nonkeys += [arg]

    # return results (+1 to length for closing brackets)
    return function_name, nonkeys, keys, length + 1


def _newSpectrumTranslateError(address, pos, instructions, details):
    line = instructions[:pos].count('\n')
    bits = instructions[:pos].rpartition('\n')
    pos = pos - len(bits[0] + bits[1])
    # generate exception
    return SpectrumTranslateError('Data Format error processing "{0}" after \
character {1} on line {2}, starting at address {3:04X}\n{4}'.format(
    instructions, pos, line, address, details))


def get_custom_format_string(AddressOutput, NumberOutput, CommandOutput,
                             OutputTStates, BreakAfterJumps, LineNumberOutput,
                             ListEveryXLines, BreakAfterData,
                             TreatDataNumbersAsLineReferences,
                             DisplayCommandBytes, DisplayComments, Seperator,
                             ShowFlags, MarkUndocumenedCommand, XMLOutput,
                             HexForNonASCII):
    """This function converts the various format settings into a String
    that can be used as an argument for the CustomFormat instruction in
    a DisassembleInstruction.  You can pass the apropriate format
    instructions as arguments to this function: you can use the "Address
    Output Format *" instructions as the AddressOutput value to set the
    address format in the custom format.  The same is true of the
    "Number Output Format *" instructions for NumberOutput, "Command
    Output Format *" for CommandOutput, "Output T States Format *" for
    OutputTStates, "Line After Jump *" for BreakAfterJumps, "Line
    Numbers *" for LineNumberOutput, Line Number Every X for
    ListEveryXLines, "Empty Line After Data *" for BreakAfterData,
    "Reference Data Numbers *" for TreatDataNumbersAsLineReferences,
    "List Command Bytes *" for DisplayCommandBytes, "Comments *" for
    DisplayComments, "Seperators *" for Seperator, "Display Flags *" for
    ShowFlags, "Mark Undocumented Command *" for MarkUndocumenedCommand,
    "XML Output *" for XMLOutput, and "Hex instead of non-ASCII *" for
    HexForNonASCII.

    AddressOutput is the format of the address at the begining of the
    line.
    NumberOutput is the format of numbers being displayed.
    CommandOutput is the format of the bytes of a command being
    displayed.
    OutputTStates is how the command lengths are displayed.
    BreakAfterJumps is if a blank line after a jump or return is
    displayed.
    LineNumberOutput is which line addresses are displayed.
    ListEveryXLines is if line addresses are displayed every X lines &
    their spacing.
    BreakAfterData is if a blank line is displayed after a data block.
    TreatDataNumbersAsLineReferences is if numbers in data are used as
    line references.
    DisplayCommandBytes is whether the bytes making up a command are
    displayed.
    DisplayComments is whether comments (and thus flags, timings, and
    undocumented command notification) are displayed.
    Seperator is the seperator between parts of the output in non-XML
    mode.  It is either a number (DisassembleCode for either "Seperators
    Space" or "Seperators Tab"), or is a string that is to be used as a
    seperator.
    ShowFlags is whether flags are displayed or not.
    MarkUndocumenedCommand is if undocumented commands are noted.
    XMLOutput is if outputting as XML or not.
    HexForNonASCII is if outputing non-ascii characters as codes or
    unicode characters.

    Returns a string version of the settings as a hexadecimal number
    usable with a CustomFormat instruction.
    """

    # custom format bits 0&1=address, 2&3=number, 4&5=command,
    # 6&7=tstates, 8&9=line after jump, A&B=linenumbers,
    # C-13=lineeveryX, 14=emptylineafterdata, 15=referencedatanumbers,
    # 16=listcommandbytes, 17=comments, 18=ShowFlags,
    # 19=MarkUndocumenedCommand, 1A=XMLOutput, 1B=HexForNonASCII

    i = (AddressOutput & 3) + ((NumberOutput & 3) << 2)
    i += ((CommandOutput & 3) << 4) + ((OutputTStates & 3) << 6)
    i += ((BreakAfterJumps & 3) << 8) + ((LineNumberOutput & 3) << 0x0A)
    i += ((ListEveryXLines & 255) << 0x0C) + ((BreakAfterData & 1) << 0x14)
    i += ((TreatDataNumbersAsLineReferences & 1) << 0x15)
    i += ((DisplayCommandBytes & 1) << 0x16) + ((DisplayComments & 1) << 0x17)
    i += ((ShowFlags & 1) << 0x18) + ((MarkUndocumenedCommand & 1) << 0x19)
    i += ((XMLOutput & 1) << 0x1A) + ((HexForNonASCII & 1) << 0x1B)

    if(isinstance(Seperator, str)):
        sep = Seperator

    elif(isinstance(Seperator, int) and
         (Seperator == DisassembleInstruction.DISASSEMBLE_CODES[
             "Seperators Tab"] or
          Seperator == DisassembleInstruction.DISASSEMBLE_CODES[
            "Seperators Space"])):
        sep = "  " if Seperator == DisassembleInstruction.DISASSEMBLE_CODES[
            "Seperators Space"] else "\t"

    # check for valid seperator
    else:
        raise SpectrumTranslateError("invalid seperator")

    return "{0:07X}{1}".format(i, sep)


def get_custom_format_values(data, bWantInstructionCode=False):
    """This function extracts the various format settings from a String
    that is the argument for the CustomFormat instruction in a
    DisassembleInstruction.  The values for the various settings are
    absolute values (except the seperator value).  The values are
    intended for use by SpectrumFileTranslate and
    SpectrumFileTranslateGUI.  Set the bWantInstructionCode option to
    True if you want the returned values to be valid
    DisassembleInstruction instruction codes.

    data is the data variable from a CustomFormat instruction.
    bWantInstructionCode is True if you want the returned values to be
    valid
    instructions (other than number 6: how often to display unreferenced
    lines) which should be
    converted to a String and used as the argument for a
    LineNumberEvery_X instruction.  Otherwise it simply returns absolute
    values of more use to internal functions.  Seperator will be text of
    the seperator.

    returns a mapping.  The values are:
    "AddressOutput" - The number format of address at the beginning of a
    line.
    "NumberOutput" - The number format for numbers being displayed.
    "CommandOutput" - The format of the bytes of a command.
    "OutputTStates" - The format for command timings.
    "BreakAfterJumps" - When to display an empty line after jumps.
    "LineNumberOutput" - Which line numbers to display.
    "ListEveryXLines" - How often to display line numbers not
    refferenced.
    "BreakAfterData" - If you want blank lines after data blocks.
    "TreatDataNumbersAsLineReferences" - Whether to treat numbers in
    data as line references.
    "DisplayCommandBytes" - Whether to display the bytes of commands.
    "DisplayComments" - Whether to display comments.
    "Seperator" - The separator to use betwen fields in the non-XML
    output.
    "ShowFlags" - Whether to show flags.
    "MarkUndocumenedCommand" - Whether to mark undocumented commands.
    "XMLOutput" - are we outputing in XML?
    "HexForNonASCII" - are we outputting codes for non-ascii characters.
    """

    i = int(data[0:7], 16)

    ret = {
        "AddressOutput": i & 0x03,
        "NumberOutput": (i >> 2) & 0x03,
        "CommandOutput": (i >> 4) & 0x03,
        "OutputTStates": (i >> 6) & 0x03,
        "BreakAfterJumps": (i >> 8) & 0x03,
        "LineNumberOutput": (i >> 0xA) & 0x03,
        "ListEveryXLines": (i >> 0xC) & 0xFF,
        "BreakAfterData": (i >> 0x14) & 0x01,
        "TreatDataNumbersAsLineReferences": (i >> 0x15) & 0x01,
        "DisplayCommandBytes": (i >> 0x16) & 0x01,
        "DisplayComments": (i >> 0x17) & 0x01,
        "ShowFlags": (i >> 0x18) & 0x01,
        "MarkUndocumenedCommand": (i >> 0x19) & 0x01,
        "XMLOutput": (i >> 0x1A) & 0x01,
        "HexForNonASCII": (i >> 0x1B) & 0x01,
        "Seperator": data[7:]
        }

    # convert results to instruction codes if requested
    if(bWantInstructionCode):
        ret["AddressOutput"] |= DisassembleInstruction.DISASSEMBLE_CODES[
            "Address Output Format Hex"]
        ret["NumberOutput"] |= DisassembleInstruction.DISASSEMBLE_CODES[
            "Number Output Format Hex"]
        ret["CommandOutput"] |= DisassembleInstruction.DISASSEMBLE_CODES[
            "Command Output Format Hex"]
        ret["OutputTStates"] |= DisassembleInstruction.DISASSEMBLE_CODES[
            "Output T States Format None"]
        ret["BreakAfterJumps"] |= DisassembleInstruction.DISASSEMBLE_CODES[
            "Line After Jump None"]
        ret["LineNumberOutput"] |= DisassembleInstruction.DISASSEMBLE_CODES[
            "Line Numbers All"]
        ret["BreakAfterData"] |= DisassembleInstruction.DISASSEMBLE_CODES[
            "Empty Line After Data On"]
        ret["TreatDataNumbersAsLineReferences"] |= \
            DisassembleInstruction.DISASSEMBLE_CODES[
                "Reference Data Numbers On"]
        ret["DisplayCommandBytes"] |= DisassembleInstruction.DISASSEMBLE_CODES[
            "List Command Bytes On"]
        ret["DisplayComments"] |= DisassembleInstruction.DISASSEMBLE_CODES[
            "Comments On"]
        ret["ShowFlags"] |= DisassembleInstruction.DISASSEMBLE_CODES[
            "Display Flags Off"]
        ret["MarkUndocumenedCommand"] |= \
            DisassembleInstruction.DISASSEMBLE_CODES[
                "Mark Undocumented Command Off"]
        ret["XMLOutput"] |= DisassembleInstruction.DISASSEMBLE_CODES[
            "XML Output Off"]
        ret["HexForNonASCII"] |= DisassembleInstruction.DISASSEMBLE_CODES[
            "Hex instead of non-ASCII Off"]

    return ret


def getpartsofpatterndatablock(pdb):
    """
    Returns list of the 3 parts of of a patternDataBlock.
    """

    # nested function to move past any comments
    def passcommentifneeded(instructions, Settings):
        # remember where we are
        pos = Settings["DATASTRINGPOS"]

        s = ""

        # loop until have next 2 characters of non whitespace characters
        # or hit end of commands, or end of line
        while(len(s) < 2 and Settings["DATASTRINGPOS"] < len(instructions)):
            c = instructions[Settings["DATASTRINGPOS"]]

            # ignore whitespace but not newline
            if(c != ' ' and c != '\t'):
                s += c

            Settings["DATASTRINGPOS"] += 1

        # is next thing a comment?
        if(s == "%#"):
            # if so move past it
            Settings["DATASTRINGPOS"] = instructions.find(
                "\n", Settings["DATASTRINGPOS"])
            # if newline not found,
            if(Settings["DATASTRINGPOS"] == -1):
                # set to end of line
                Settings["DATASTRINGPOS"] = len(instructions)

        else:
            # otherwise reset position
            Settings["DATASTRINGPOS"] = pos

    # break Pattern Data Block into sections
    test = None
    prep = None
    action = None

    try:
        Settings = {"DATASTRINGPOS": 0}
        Vars = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xFFFF]

        # first check is valid test block & record where
        s = _getnextcharacters(pdb, Settings, 2)
        if(s != "%("):
            return (test, prep, action)

        # record test start
        k = Settings["DATASTRINGPOS"]
        # move to end of test block
        _movetoblockend(pdb, Vars, Settings, 0)
        # move past comment if one exists on same line as close block
        passcommentifneeded(pdb, Settings)
        # calculate test string
        test = "%(" + pdb[k:Settings["DATASTRINGPOS"]]

        # now check is valid preperation block & record where
        s = _getnextcharacters(pdb, Settings, 2)
        if(s != "%("):
            return (test, prep, action)

        # record preperation block start
        k = Settings["DATASTRINGPOS"]
        # move to end of preperation block
        _movetoblockend(pdb, Vars, Settings, 0)
        # move past comment if one exists on same line as close block
        passcommentifneeded(pdb, Settings)
        # calculate preperation string
        prep = "%(" + pdb[k:Settings["DATASTRINGPOS"]]

        # calculate action string
        action = pdb[Settings["DATASTRINGPOS"]:]

        return (test, prep, action)

    except:
        return (test, prep, action)


def createfindandcomment(test, comment, commandlength, position):
    """This function returns a string that can be used as the
    instruction for a Comment Pattern DisassembleInstruction.
    test and comment are strings encoded to be processed as a data block
    instuction (use the stringtoinstructiontext to convert a normal
    string to a valid instruction). command length is the length of the
    command you are finding, and position is 0 for the comment to be
    placed at the end of a line, 1 if before the matched line, and 2
    if after the matched line.
    """

    return """\
%(                   %#start test block
  %(                 %#start test code
{0}
  %)                 %#end test code

  %?BA
  %?EQ00000000       %#test to ensure that false test fails now

  %X0200%V0F{1:04X}     %#var0 is position of code to check + length of command
                     %#start comment text
{2}
                     %#end comment text
  %;%V0F%V00{3:X}0       %#Create comment instruction

  %?BA
  %?EQ00000001       %#Force fail test otherwise will be processed as pattern
%)                   %#end test block

%(
%)
""".format(test, commandlength - 1, comment, position)


def detailsfromfindandcomment(code):
    """This function returns a list of the components of a find and
    comment instruction. Returns None if the supplied argument is not a
    valid find and comment instruction.
    Item 0 is the test code. Item 1 is the comment (encoded to be run
    by the command interpeter, so use instructiontexttostring to get it
    converted to plain text). Item 2 is the command length to be matched
    as an int. Item 3 is the comment position as an int (0 at the end
    of the matched line, 1 before the matched line, and 2 after the
    metched line.
    """

    try:
        match = re.search(".*%\(\s*%#start test code\n(.*)\n  %\)\s*%#end test\
 code.*%X0200%V0F([0-9A-F]{4})\s*%#var0 is position of code to check \+ length\
 of command.*%#start comment text\n(.*)\n\s*%#end comment text.*%;%V0F%V00([0-\
2])0\s*%#Create comment instruction", code, re.DOTALL)
        return [match.group(1), match.group(3), int(match.group(2), 16) + 1,
                int(match.group(4), 16)]
    except:
        return None


def instructiontexttostring(instructiontext):
    """This function returns text as would be printed out by data block
    instructiontext.
    """

    Settings = {"DATASTRINGPOS": 0,
                "NUMBERFORMAT": 0,
                "NUMBERSIGNED": 0,
                "NUMBERWORDORDER": 0,
                "DISPLAYEVERYXLINES": 1,
                "ORIGIONALSEPERATOR": "  ",
                "SEPERATOR": "  ",
                "ORIGIN": 0x4000,
                "ADDRESSOUTPUT": 0,
                "NUMBEROUTPUT": 0,
                "COMMANDOUTPUT": 0,
                "XMLOutput": 0,
                "HexForNonASCII": 0}
    Vars = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x4000, 0, 0, 0x4000, 0x4001]

    flag, text = _processcommandblock(instructiontext, Vars, Settings, None,
                                      False, True)

    return text


def stringtoinstructiontext(text):
    """This function returns the datablock instruction to display text.
    """

    return text.replace("%", "%%").replace(" ", "% ").replace("\n", "%N").\
        replace("\t", "%T")


def get_disassemblecodename_from_value(value):
    """Returns the name of the DisassembleCode given it's numerical
    value.  Returns None if not a valid DisassembleCode.
    """

    for instructionname, code in list(DisassembleInstruction.
                                      DISASSEMBLE_CODES.items()):
        if(code == value):
            return instructionname

    return None


def get_disassembleblockname_from_value(value):
    """Returns the name of the DisassembleDataBlockCode or
    DisassemblePatternBlockCode given it's numerical value.
    Returns None if not a valid DisassembleDataBlockCode or
    DisassemblePatternBlockCode.
    """

    if(value in list(DisassembleInstruction.DISASSEMBLE_DATABLOCK_CODES.
                     values())):
        for blockname, code in list(DisassembleInstruction.
                                    DISASSEMBLE_DATABLOCK_CODES.items()):
            if(code == value):
                return blockname

    if(value in list(DisassembleInstruction.DISASSEMBLE_PATTERNBLOCK_CODES.
                     values())):
        for blockname, code in list(DisassembleInstruction.
                                    DISASSEMBLE_PATTERNBLOCK_CODES.items()):
            if(code == value):
                return blockname

    return None


class SpectrumTranslateError(Exception):
    """A class to flag up an Exception raised during woring with
    SpectrumTranslate objects.
    """

    def __init__(self, arg):
        self.value = arg

    def __str__(self):
        return repr(self.value)


def usage():
    """
    returns the command line arguments for spectrumtranslate as a string.
    """

    return """\
usage: python spectrumtranslate.py translatemode [args] infile outfile

Translates data in infile and outputs it to outfile.

translatemode is required and specifies how to treat the data.  It must be
'basic', 'code', 'screen', 'text', 'array', or 'instruction'.  basic, code,
screen, and array treat the input as the code of a basic program, code file,
screen memory (or saved to a file), or an array file as saved to tape.  text
takes as it's input a spectrum string or character and outputs it in a more
readable format (although sometimes non-printable characters are replaced
with a ^ followed by a 2 character hexadecimal number).  The spectrum did not
have ^ in it's character set, instead useing an upward pointing arrow.
instruction is used to manipulate or convert disassembly instructions.

infile and outfile are required unless reading from the standard input or
outputting to the standard output.  Usually arguments are ignored if they
don't apply to the selected translation mode.

-o specifies that the output from this program is to be directed to the
   standard output and not outputfile which should be omited.  It can be used
   for all translation modes.
--tostandardoutput same as -o.
-i specifies that this program gets it's data from the standard input and
   not inputfile which should be omited.  It can be used for all translation
   modes.
--fromstandardinput same as -i.
-x specifies that the user wants the output as XML rather than plain text.
   This can be used for basic, code, and array translation modes.
--xml same as -x.
-a specifies that you want the output to have any non-standard ascii
   characters output as a '^' followed by it's 2 digit hexadecimal value
   rather than a non-ascii character (like the copyright symbol, and the
   graphical symbols.  This can be used for the basic, text, and array
   conversion modes.
--ascii same as -a.
-k specifies the how many bytes to skip from the input before using the
   data.  This is useful for example if you had a 64K memory dump, and
   wanted to get to the screen memory by skipping the first 16384 bytes.
   If omitted no bytes are skipped.  It must be folloed by the number of
   bytes to skip in decimal or a hexadecimal number starting with 0x.
--skip same as -k.
-l specifies how many bytes to translate from the input.  This is used
   for example if you have a 64K memory dump, and wanted to translate
   the screen which is only 6912 bytes long.  If omitted, all bytes are
   used. It must be folloed by the number of bytes to skip in decimal or
   a hexadecimal number starting with 0x.
--len same as -l.
--length same as -l.

basic flags:
-s specifies the auto start line (where a program is run from when loaded)
   and requires an aditional argument which can be a hexadecimal or decimal
   number.  The -s option is not required.
--start same as -s.
-v specifies the offset in bytes to any variables saved with the BASIC
   program.  It requires an aditional argument which can be a hexadecimal or
   decimal number.  The -v option is not required and if not present, it is
   assumed that there are no variables with the BASIC program.
--variableoffset same as -v.

array flags:
-t specifies the array type.  This is required for all array functions.  It
   must be followed by the type descriptor which can be a number with bits 6
   and 7 as 64, 128, or 192, or be 'number', 'character', or 'string'
   depending on the type of array.
--type same as -t.
-d specifies that we want the dimensions of an array and not it's content.
--dimensions same as -d.

screen flags:
-g specifies that we want the image to be outputed as a gif file (possibly
   animated) as opposed to a RGB file.
--gif same as -g.
-f Specifies the number of milliseconds between the two images in a gif
   image of a screen with flashing colours.  If not supplied the default
   is 320.  Set this to -1 if you want a non-flashing image, and -2 if
   you want a non-flashing image with any parts in their flash state.
--flashrate same as -f.

code flags:
-b specifies the base address for assebmbly code.  If omitted the base
   address will be assumed to be 0x0000.
--base same as -b.
--baseaddress same as -b.
-c specifies special instructions are to be used in disassembling the
   assembly code.  If omitted then it is assumed that there are no special
   instructions.  If this flag is used it must be followed by either f or s
   (or si) for file input or standard input as the source of the special
   instructions.  If file input is specified then it must be followed by the
   filename of the special instruction data file.  If s is specified and the
   -i flag is being used then the special instructions must be passed first
   and be ended by a single empty line before the code to disassemble is
   passed through the standard input.
--commands same as -c.

instruction flags:
    the input and output are string arguments for creating disassemble
    instructions.  Unless the flags below are used, then it is assumed that
    there is one instruction per line.

-m  specifies that both the input and output are definitions of instructions
    spread over multiple lines.  The instruction name or decimal code, or
    hexadecimal code preceded by '0x' is on the first line, the start
    address is on the second line (decimal or hexadecimal preceded by '0x'),
    the end address (either decimal or '0x' hexadecimal) is on the third
    line, and any data is from the fourth line onwards.
--multiline same as -m.
-mi same as -m flag but indicates that only the input is multiline.
--multilinein same as -mi.
-mo same as -m flag but indicates that only the output is multiline.
--multilineout same as -mo.
-n  specifies that want names of instruction or data rather than code in the
    output.  Input will accept either instruction number, data code,
    instruction name, or data instruction name.
--namewanted same as -n.
"""


def _commandline(args):
    # analyse args
    i = 0
    mode = None
    xml = False
    start = -1
    varoff = -1
    descriptor = None
    fromstandardinput = False
    tostandardoutput = False
    inputfile = None
    outputfile = None
    wantarraydimensions = False
    flashrate = 320
    imageFormat = "RGB"
    baseaddress = 0
    commandsource = None
    multilinein = False
    multilineout = False
    wantinstructionname = False
    hexfornonascii = False
    skipbytes = None
    usebytes = None

    def getint(x):
        return int(x, 16 if x.lower().startswith("0x") else 10)

    # handle no arguments
    if(len(args) == 1):
        mode = 'help'

    # go through arguments analysing them
    while(i < len(args) - 1):
        i += 1

        arg = args[i]
        if(arg == 'basic' or arg == 'array' or arg == 'text' or
           arg == 'screen' or arg == 'code' or arg == 'instruction' or
           arg == 'help'):
            if(mode is not None):
                raise SpectrumTranslateError(
                    "Can't have multiple formats to convert into.")

            mode = arg
            continue

        if(not mode):
            raise SpectrumTranslateError('No translateing mode (basic, code, \
screen, array, text, or instruction) specified.')

        if(arg == '-x' or arg == '-xml' or arg == '--x' or arg == '--xml'):
            xml = True
            continue

        if(arg == '-s' or arg == '-start' or arg == '--s' or arg == '--start'):
            try:
                i += 1
                start = getint(args[i])
                continue
            except:
                raise SpectrumTranslateError(
                    "Missing or invalid autostart line number.")

        if(arg == '-v' or arg == '-variableoffset' or arg == '--v' or
           arg == '--variableoffset'):
            try:
                i += 1
                varoff = getint(args[i])
                continue
            except:
                raise SpectrumTranslateError(
                    "Missing or invalid offset to variables.")

        if(arg == '-t' or arg == '-type' or arg == '--t' or arg == '--type'):
            try:
                i += 1
                opt = args[i]

                if(opt == 'number' or opt == 'numberarray'):
                    descriptor = 128

                elif(opt == 'character' or opt == 'characterarray'):
                    descriptor = 192

                elif(opt == 'string'):
                    descriptor = 64

                else:
                    descriptor = getint(opt)
                    # am only interested in bits 6 and 7.
                    # Only invalid if they are both 0
                    if(descriptor & 192 == 0):
                        raise SpectrumTranslateError("Invalid array \
description. Must have integer with bits 6 and 7 as 64, 128, or 192, or be \
number, character, or string.")

                continue
            except SpectrumTranslateError:
                raise
            except:
                raise SpectrumTranslateError(
                    "Missing or invalid array description.")

        if(arg == '-d' or arg == '-dimensions' or arg == '--d' or
           arg == '--dimensions'):
            wantarraydimensions = True
            continue

        if(arg == '-i' or arg == '-fromstandardinput' or arg == '--i' or
           arg == '--fromstandardinput'):
            fromstandardinput = True
            continue

        if(arg == '-o' or arg == '-tostandardoutput' or arg == '--o' or
           arg == '--tostandardoutput'):
            tostandardoutput = True
            continue

        if(arg == '-h' or arg == '-help' or arg == '--h' or arg == '--help'):
            mode = 'help'
            break

        if(arg == '-f' or arg == '-flashrate' or arg == '--f' or
           arg == '--flashrate'):
            try:
                i += 1
                flashrate = getint(args[i])
                continue
            except:
                raise SpectrumTranslateError(
                    "Missing or invalid image flash rate.")

        if(arg == '-g' or arg == '-gif' or arg == '--g' or arg == '--gif'):
            imageFormat = "GIF"
            continue

        if(arg == '-b' or arg == '-baseaddress' or arg == '-base' or
           arg == '--b' or arg == '--baseaddress' or arg == '--base'):
            try:
                i += 1
                baseaddress = getint(args[i])
                continue
            except:
                raise SpectrumTranslateError(
                    "Missing or invalid base code address.")

        if(arg == '-c' or arg == '-commands' or arg == '--c' or
           arg == '--commands'):
            try:
                i += 1
                if(args[i] != 'f' and args[i] != 's' and args[i] != 'si'):
                    raise SpectrumTranslateError("Missing or invalid input \
source descriptor for special instructions.")

                commandsource = 'f' if args[i] == 'f' else 's'

                if(commandsource == 'f'):
                    i += 1
                    commandsourcefile = args[i]

                continue
            except SpectrumTranslateError:
                raise
            except:
                raise SpectrumTranslateError(
                    "Missing or invalid commands information.")

        if(arg == '-m' or arg == '-multiline' or arg == '--m' or
           arg == '--multiline'):
            multilinein = True
            multilineout = True
            continue

        if(arg == '-mi' or arg == '-multilinein' or arg == '--mi' or
           arg == '--multilinein'):
            multilinein = True
            continue

        if(arg == '-mo' or arg == '-multilineout' or arg == '--mo' or
           arg == '--multilineout'):
            multilineout = True
            continue

        if(arg == '-n' or arg == '-namewanted' or arg == '--n' or
           arg == '--namewanted'):
            wantinstructionname = True
            continue

        if(arg == '-a' or arg == '-ascii' or arg == '--a' or arg == '--ascii'):
            hexfornonascii = True
            continue

        if(arg == '-k' or arg == '--skip'):
            try:
                i += 1
                skipbytes = getint(args[i])
                continue
            except:
                raise SpectrumTranslateError(
                    "Missing or invalid number of bytes to skip.")

        if(arg == '-l' or arg == '-len' or arg == '-length' or arg == '--l' or
           arg == '--len' or arg == '--length'):
            try:
                i += 1
                usebytes = getint(args[i])
                continue
            except:
                raise SpectrumTranslateError(
                    "Missing or invalid bytes length number.")

        # have unrecognised argument.
        # check if is input or output file
        # will be inputfile if not already defined, and
        # fromstandardinput is False
        if(inputfile is None and not fromstandardinput and i >= len(args) -
           (2 if outputfile is None and not tostandardoutput else 1)):
            inputfile = arg
            continue

        # will be outputfile if not already defined, tostandardoutput is
        # False, and is last argument
        if(outputfile is None and not tostandardoutput and i == len(args) - 1):
            if(inputfile is None and not fromstandardinput):
                raise SpectrumTranslateError('No input file specified.')
            outputfile = arg
            continue

        raise SpectrumTranslateError(
            '"{0}" is unrecognised argument.'.format(arg))

    # finished processing arguments now.
    # Check we've got what we need
    if(inputfile is None and not fromstandardinput and mode != 'help'):
        raise SpectrumTranslateError('No input file specified.')

    if(outputfile is None and not tostandardoutput and mode != 'help'):
        raise SpectrumTranslateError('No output file specified.')

    if(mode == 'array' and descriptor is None):
        raise SpectrumTranslateError("Missing array type.")

    # if help is needed display it
    if(mode == 'help'):
        sys.stdout.write(usage())
        return

    # get special instructions if needed
    specialInstructions = None
    if(mode == 'code' and commandsource is not None):
        if(commandsource == 'f'):
            # get instructions from file
            try:
                fo = open(commandsourcefile, "r")
                specialInstructions = [DisassembleInstruction(
                    line.rstrip('\n')) for line in fo]
                fo.close()
            except:
                raise SpectrumTranslateError('Failed to read instructions \
from "{0}".'.format(commandsourcefile))

        else:
            try:
                # if there is only the commands commeing from standard
                # input then no blank lines
                if(not fromstandardinput):
                    specialInstructions = [DisassembleInstruction(
                        line.rstrip('\n')) for line in sys.stdin]

                # otherwise will be blank line terminated
                else:
                    while(True):
                        line = sys.stdin.readline()
                        if(line is None or line == '\n'):
                            break

                        if(specialInstructions is None):
                            specialInstructions = [DisassembleInstruction(
                                line.rstrip('\n'))]

                        else:
                            specialInstructions += [DisassembleInstruction(
                                line.rstrip('\n'))]

            except:
                raise SpectrumTranslateError('Failed to read instructions \
from standard input.')

    # get data
    if(not fromstandardinput):
        with open(inputfile, 'rb') as infile:
            data = infile.read()

    else:
        if(sys.hexversion > 0x03000000 and mode != 'instruction'):
            data = sys.stdin.buffer.read()
        else:
            data = sys.stdin.read()

    # apply skip and length options if needed
    if(skipbytes):
        if(skipbytes < 0 or skipbytes > len(data)):
            raise SpectrumTranslateError('Invalid skip value.')
        data = data[skipbytes:]
    if(usebytes):
        data = data[:usebytes]
        if(usebytes < 1 or usebytes > len(data)):
            raise SpectrumTranslateError('Invalid length value.')

    # now translate the data
    if(mode == 'basic'):
        if(xml):
            retdata = basictoxml(data, start, varoff, hexfornonascii)

        else:
            retdata = basictotext(data, start, varoff, hexfornonascii)

    elif(mode == 'text'):
        retdata = getspectrumstring(data, hexfornonascii)

    elif(mode == 'array'):
        if(wantarraydimensions):
            retdata = str(getarraydepth(data, descriptor))

        elif(xml):
            retdata = arraytoxml(data, descriptor, hexfornonascii)

        else:
            retdata = arraytotext(data, descriptor, hexfornonascii)

    elif(mode == 'screen'):
        if(imageFormat == "GIF"):
            retdata = getgiffromscreen(data, flashrate)

        else:
            rgbdata = getrgbfromscreen(data, alphamask=-1, imageformat=1)
            iwanted = 1 if flashrate == -2 and rgbdata[1] is not None else 0
            retdata = rgbdata[iwanted]
            retdata = bytearray([x[i] for x in retdata for i in (0, 1, 2)])

    elif(mode == 'code'):
        if(xml):
            if(specialInstructions is None):
                specialInstructions = [DisassembleInstruction("XML Output On")]

            else:
                specialInstructions = [DisassembleInstruction(
                    "XML Output On")] + specialInstructions

        retdata = disassemble(data, 0, baseaddress, len(data),
                              specialInstructions)

    if(mode == 'instruction'):
        # get instructions
        if(not multilinein):
            # instructions in non-multiline can be on multiple lines
            di = [DisassembleInstruction(line) for line in data.splitlines()]

        else:
            lines = data.splitlines()

            # if argument is string for instruction type then get
            # code
            if(lines[0] in DisassembleInstruction.DISASSEMBLE_CODES):
                di = DisassembleInstruction(lines[0])

            else:
                di = DisassembleInstruction(getint(lines[0]))

            di.start = getint(lines[1])
            di.end = getint(lines[2])
            lines = '\n'.join(lines[3:])
            if(lines in list(
               DisassembleInstruction.DISASSEMBLE_DATABLOCK_CODES.keys())):
                di.data = DisassembleInstruction.\
                              DISASSEMBLE_DATABLOCK_CODES[lines]

            elif(lines in
                 list(DisassembleInstruction.
                      DISASSEMBLE_PATTERNBLOCK_CODES.keys())):
                di.data = DisassembleInstruction.\
                              DISASSEMBLE_PATTERNBLOCK_CODES[lines]

            else:
                di.data = None if lines == '' else lines

            di = [di]

        # now prepare them for output
        if(not multilineout):
            retdata = '\n'.join([str(x) for x in di])

        else:
            if(wantinstructionname):
                def nameornumber(c):
                    if(get_disassemblecodename_from_value(c) is None):
                        return "{0:X}".format(c)

                    return get_disassemblecodename_from_value(c)

                def nameorcode(c):
                    if(get_disassembleblockname_from_value(c) is None):
                        return c

                    return get_disassembleblockname_from_value(c)

                retdata = '\n'.join(
                    "{0}\n{1.start:X}\n{1.end:X}\n{2}".format(
                        nameornumber(x.instruction), x,
                        '' if x.data is None or x.data == '' else
                        nameorcode(x.data)
                        )
                    for x in di)

            else:
                retdata = '\n'.join(
                  "{0.instruction:X}\n{0.start:X}\n{0.end:X}\n{1}".format(
                    x, '' if x.data is None else x.data) for x in di)

    # output data
    if(not tostandardoutput):
        if(mode == "screen"):
            fo = open(outputfile, "wb")
            fo.write(retdata)
        else:
            if(sys.hexversion > 0x03000000):
                fo = open(outputfile, "w")
                fo.write(retdata)
            else:
                fo = open(outputfile, "wb")
                fo.write(retdata.encode('utf-8'))
        fo.close()

    else:
        if(mode == "screen"):
            if(sys.hexversion > 0x03000000):
                sys.stdout.buffer.write(retdata)
            else:
                sys.stdout.write("".join([chr(x) for x in retdata]))
        else:
            if(sys.hexversion > 0x03000000):
                sys.stdout.write(retdata)
            else:
                sys.stdout.write(retdata.encode('utf-8'))


if __name__ == "__main__":
    try:
        _commandline(sys.argv)
    except SpectrumTranslateError as se:
        sys.stderr.write(se.value + "\n")
        sys.stdout.write(
            "Use 'python spectrumtranslate.py' to see full list of options.\n")
        sys.exit(2)
