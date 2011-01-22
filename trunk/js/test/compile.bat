set CLOSUREPATH=D:\Work\MAIN\GPS\GGT-200\SRC\SITE\googleapp\libs\closure-library
set COMPILER=D:\Work\MAIN\GPS\GGT-200\SRC\SITE\googleapp\libs\compiler\compiler-latest\compiler.jar 

python %CLOSUREPATH%\closure\bin\calcdeps.py -i mapproject\start.js -p %CLOSUREPATH%/ -o script -f "--closure_pass --mark_as_compiled"> testclosure-all.js

rem python %CLOSUREPATH%\closure\bin\calcdeps.py -i mapproject\start.js -p %CLOSUREPATH%/ -o compiled -c %COMPILER% -f "--compilation_level=ADVANCED_OPTIMIZATIONS" > testclosure-all.js
