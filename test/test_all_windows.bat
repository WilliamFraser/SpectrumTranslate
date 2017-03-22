@REM you need to create python2.bat with the line: C:\path_to_python2_exe\python.exe %1 %2 %3 %4 %5 %6 %7 %8 %9
@REM you need to do the same for python3

@echo Testing test_disciplefile.py in python 2
@call python2 test_disciplefile.py
@echo Testing test_disciplefile.py in python 3
@call python3 test_disciplefile.py

@echo Testing test_spectrumnumber.py in python 2
@call python2 test_spectrumnumber.py
@echo Testing test_spectrumnumber.py in python 3
@call python3 test_spectrumnumber.py

@echo Testing test_spectrumtapblock.py in python 2
@call python2 test_spectrumtapblock.py
@echo Testing test_spectrumtapblock.py in python 3
@call python3 test_spectrumtapblock.py

@echo Testing test_spectrumtranslate.py in python 2
@call python2 test_spectrumtranslate.py
@echo Testing test_spectrumtranslate.py in python 3
@call python3 test_spectrumtranslate.py

@echo Done
