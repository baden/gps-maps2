http://code.google.com/p/closure-compiler/source/browse/trunk/contrib/externs/?r=747


'java -jar ./closure_compiler/compiler.jar',
'--compilation_level ADVANCED_OPTIMIZATIONS',
# '--formatting PRETTY_PRINT',
'--externs ./closure_compiler/jquery-1.4.4.externs.js',
'--externs ./closure_compiler/jquery.mousewheel.externs.js',
'--externs ./closure_compiler/editor.externs.js',
'--externs ./closure_compiler/rapt.externs.js',
'--js "%s"',
'--js_output_file "%s"'
