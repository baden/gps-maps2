set CLOSUREPATH=D:\Work\MAIN\GPS\GGT-200\SRC\SITE\googleapp\libs\closure-library
set COMPILER=D:\Work\MAIN\GPS\GGT-200\SRC\SITE\googleapp\libs\compiler\compiler-latest\compiler.jar 



rem python %CLOSUREPATH%\closure\bin\build\closurebuilder.py --root=%CLOSUREPATH%/ --root=mapproject/ --namespace="mapproject.start" --output_mode=compiled --compiler_jar=%COMPILER% --compiler_flags="--compilation_level=ADVANCED_OPTIMIZATIONS" >testclosure-build.js
python %CLOSUREPATH%\closure\bin\build\closurebuilder.py --root=%CLOSUREPATH%/ --root=mapproject/ --namespace="mapproject.start" --output_mode=compiled --compiler_jar=%COMPILER% --compiler_flags="--compilation_level=ADVANCED_OPTIMIZATIONS" --compiler_flags="--formatting=PRETTY_PRINT" --compiler_flags="--create_name_map_files=true" --compiler_flags="--charset=utf-8" --compiler_flags="--define=COMPILED=true">testclosure-build.js
