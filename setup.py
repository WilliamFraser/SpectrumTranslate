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
# Date: 12th March 2017

from pip import main as pip_main
from site import getusersitepackages
from shutil import copy as shutil_copy
import os
import tempfile

if __name__ == "__main__":
    # set up getch to return keypress in windows or unix like system (linux/mac)
    try:
        from msvcrt import getch
    except ImportError:
        def getch():
            import tty, sys, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    # function to copy files
    def copyfile(src, dest):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            with open(src) as src_file:
                for line in src_file:
                    if line.startswith("import spectrumtranslate"):
                        line = "from . import spectrumtranslate\n"
                    elif line.startswith("import spectrumnumber"):
                        line = "from . import spectrumnumber\n"
                    temp_file.write(line.encode())
            temp_file.close()
            shutil_copy(temp_file.name, os.path.join(dest, src))
            os.remove(temp_file.name)

    # set up PyQt5?
    print("Do You want to install PyQt5 (latest version of Qt needed to run \
graphical interface to SpectrumTranslate) and PyQtWebEngine? (y/n/q)")
    while True:
        c = getch()
        if c in [b'n', b'N', 'n', 'N']:
            break
        if c in [b'q', b'Q', 'q', 'Q']:
            quit()
        if c in [b'y', b'Y', 'y', 'Y']:
            print()
            pip_main(['install', 'PyQt5'])
            pip_main(['install', 'PyQtWebEngine'])
            break

    # set up packages needed for development?
    print("\nDo You want to install pycodestyle and pillow (Only required if \
running development tests)? (y/n/q)")
    while True:
        c = getch()
        if c in [b'n', b'N', 'n', 'N']:
            break
        if c in [b'q', b'Q', 'q', 'Q']:
            quit()
        if c in [b'y', b'Y', 'y', 'Y']:
            print()
            pip_main(['install', 'pycodestyle'])
            pip_main(['install', 'pillow'])
            break

    # work out where to copy files to
    ST_dir = os.path.join(getusersitepackages(), "SpectrumTranslate")
    # install as module?
    print("\nDo You want to install SpectrumTranslate as a module that you can \
import from any project for this user? (y/n/q)")
    while True:
        c = getch()
        if c in [b'n', b'N', 'n', 'N']:
            break
        if c in [b'q', b'Q', 'q', 'Q']:
            quit()
        if c in [b'y', b'Y', 'y', 'Y']:
            # ensure module directory exists
            if not os.path.exists(ST_dir):
                os.makedirs(ST_dir)
            # copy files across
            files = ["licence.txt",
                     "__init__.py",
                     "disciplefile.py",
                     "spectrumnumber.py",
                     "spectrumtape.py",
                     "spectrumtranslate.py"]
            for f in files:
                copyfile(f, ST_dir)
            break

    print("\nDone")
