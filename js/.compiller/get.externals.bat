SET curl=D:\Programs\Git\bin\curl.exe
SET svn=D:\Programs\mingw\svn-win32-1.6.2\bin\svn.exe

rem %curl% http://closure-compiler.googlecode.com/files/compiler-latest.zip --output compiler.jar

rem jquery-1.4.4.js
for %%i in (jquery-1.5.js, google_loader_api.js, webkit_console.js, maps/google_maps_api_v3_3.js) do (
%curl% http://closure-compiler.googlecode.com/svn/trunk/contrib/externs/%%i --output externals\%%i
)

rem %svn% checkout http://closure-compiler.googlecode.com/svn/trunk/contrib/externs externals
