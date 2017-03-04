from pip import main as pip_main
from site import getsitepackages
from shutil import copy as shutil_copy
import os

if __name__ == "__main__":
    #set up getch to return keypress in windows or unix like system (linux/mac)
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

    #function to copy files
    def copyfile(src, dest):
        shutil_copy(src,dest)

    #set up PyQt5?
    print("Do You want to install PyQt5 (latest version of Qt needed to run \
graphical interface to SpectrumTranslate)? (y/n/q)")
    while(True):
        c = getch()
        if(c == b'n' or c == b'N'):
            break
        if(c == b'q' or c == b'Q'):
            quit()
        if(c == b'y' or c == b'Y'):
            print()
            pip_main(['install', 'PyQt5'])
            break

    #set up packages needed for development?
    print("\nDo You want to install pep8 and pillow (Only required if running \
development tests)? (y/n/q)")
    while(True):
        c = getch()
        if(c == b'n' or c == b'N'):
            break
        if(c == b'q' or c == b'Q'):
            quit()
        if(c == b'y' or c == b'Y'):
            print()
            pip_main(['install', 'pep8'])
            pip_main(['install', 'pillow'])
            break

    #work out where to copy files to
    packagedirs = [p for p in getsitepackages() if p.endswith('-packages')]
    #if no site-packages or dist-packages directory, get all module directories
    if(not packagedirs):
        packagedirs = getsitepackages()
    #may be more than one.
    #Choose last as first in list more likely to be python root directories
    packagedir = packagedirs[-1]
    print(packagedir)
    ST_dir = os.path.join(packagedir, "SpectrumTranslate")
    print(ST_dir)

    #install as module?
    print("\nDo You want to install SpectrumTranslate as a module that you can \
import from any project for this user? (y/n/q)")
    while(True):
        c = getch()
        if(c == b'n' or c == b'N'):
            break
        if(c == b'q' or c == b'Q'):
            quit()
        if(c == b'y' or c == b'Y'):
            #ensure module directory exists
            if(not os.path.exists(ST_dir)):
                os.makedirs(ST_dir)
            #copy files across
            files = ["licence.txt",
                     "__init__.py",
                     "disciplefile.py",
                     "spectrumnumber.py",
                     "spectrumtapblock.py",
                     "spectrumtranslate.py"]
            for f in files:
                copyfile(f, ST_dir)
            break

    print("\nDone")
