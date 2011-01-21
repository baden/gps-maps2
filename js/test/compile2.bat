set CLOSUREPATH=D:\Work\MAIN\GPS\GGT-200\SRC\SITE\googleapp\libs\closure-library
set COMPILER=D:\Work\MAIN\GPS\GGT-200\SRC\SITE\googleapp\libs\compiler\compiler-latest\compiler.jar 

rem python %CLOSUREPATH%\closure\bin\calcdeps.py -i testclosure.js -p %CLOSUREPATH%/ -o deps > testclosure-deps.js

rem python %CLOSUREPATH%\closure\bin\calcdeps.py -i testclosure.js -p %CLOSUREPATH%/ -o compiled -c %COMPILER% -f "--compilation_level=ADVANCED_OPTIMIZATIONS" > testclosure-all.js
rem python %CLOSUREPATH%\closure\bin\calcdeps.py -i testclosure.js -p %CLOSUREPATH%/ -o compiled -c compiler.jar > testclosure-all.js


python %CLOSUREPATH%\closure\bin\build\closurebuilder.py --root=%CLOSUREPATH%/ --root=mapproject/ --namespace="mapproject.start" --output_mode=compiled --compiler_jar=%COMPILER% --compiler_flags="--compilation_level=ADVANCED_OPTIMIZATIONS" >testclosure-build.js
