from distutils.core import setup
import py2exe
import sys
includes = ["encodings", "encodings.*"]  
sys.argv.append("py2exe")
options = {"py2exe": {"bundle_files": 1,
                      "dll_excludes": ["MSVCP90.dll", "HID.DLL", "w9xpopen.exe"],
                      "includes": ["lxml.etree", "lxml._elementpath", "gzip", "sip"]
                     }
           }
setup(options = options,
	  zipfile = None,
      data_files = [("",["icon.png"])],
	  windows = [{"script":"PixivAgent.py", "icon_resources": [(1, "icon.ico")]}])