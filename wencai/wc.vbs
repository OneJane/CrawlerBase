DIM objShell 
set objShell = wscript.createObject("wscript.shell") 
iReturn = objShell.Run("F:\\MyProject\\CrawlerBase\\wencai\\wc.bat", 0, TRUE)
