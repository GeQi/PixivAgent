# PixivAgent

a friendly GUI downloader for Pixiv base on **Python3** & Qt

# Demo

![demo](http://7u2hae.com1.z0.glb.clouddn.com/demo.gif)

# Installation

1. Install [Qt Community](http://www.qt.io/download-open-source/)
2. Install [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/installation.html)
3. Intall the following liberaries & dependencies

### For Fedora/CentOS:

```
$ sudo yum update
$ sudo yum install python3-lxml ImageMagick-devel
$ sudo pip3 install requests Wand
$ git clone https://github.com/GeQi/PixivAgent.git && cd PixivAgent
```

And then

`$ python3 PixivAgent.py`

### For Debian/Ubuntu:

```
$ sudo apt-get update
$ sudo apt-get install python3-lxml libmagickwand-dev
$ sudo pip3 install requests Wand
$ git clone https://github.com/GeQi/PixivAgent.git && cd PixivAgent
```

And then

`$ python3 PixivAgent.py`

### For Windows:

Use `pip` to `intsall` the `.whl` pakage from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)

Install [ImageMagick on Windows](http://docs.wand-py.org/en/latest/guide/install.html#install-imagemagick-on-windows)

```
$ pip install requests Wand
$ git clone https://github.com/GeQi/PixivAgent.git && cd PixivAgent
```
And then

`$ python PixivAgent.py`

# Credits

- [requests](https://github.com/kennethreitz/requests)
- [lxml](https://github.com/lxml/lxml)
- [wand](https://github.com/dahlia/wand)
- [imagemagick](http://www.imagemagick.org/)
- [pyqt](http://www.riverbankcomputing.co.uk/software/pyqt/intro)
