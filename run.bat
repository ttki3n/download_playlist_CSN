@echo off

rem flac 500 320 128 32 
SET FORMAT=32
SET PLAYLIST=http://chiasenhac.vn/nghe-album/the-spectre~alan-walker-danny-shah~tsvdsb67qm4qkt.html

call python download_chiasenhac.py %PLAYLIST% %FORMAT%

pause
