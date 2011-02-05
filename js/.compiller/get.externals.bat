SET curl=D:\Programs\Git\bin\curl.exe
SET svn=D:\Programs\mingw\svn-win32-1.6.2\bin\svn.exe

%curl% http://closure-compiler.googlecode.com/files/compiler-latest.zip --output compiler.jar
%svn% checkout http://closure-compiler.googlecode.com/svn/trunk/contrib/externs externals
