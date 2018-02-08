#coding:utf-8
#!/usr/local/bin/python
"""
尝试打开任意一种媒体文件。总是使用通用网页浏览器构架，不过也允许使用特定播放器。代码不经修改，
有可能在你的系统上无法正常工作；对于音频文件，在Unix下使用filter和命令行打开，在Windows下利用
文件名关联通过start命令打开（也就是说，使用你的机器上的程序打开.au文件，可能是一个音频播放器，
也可能是一个网页浏览器）。可以根据需要进行配置和扩展。playknowfile假定你知道想打开的文件的媒体
类型，而playfile尝试利用Pythonmimetypes模块自动决定
"""
import os,sys,mimetypes,webbrowser

helpmsg = """
Sorry:can't find a media player for '%s' on your system!
Add an entry for your system to the media player dictionary
for this type of file in playfile.py,or play the file manually.
"""

def trace(*args):print(*args)#用空格隔开
################################################################################
#播放器技巧：通用或特定：带扩展
################################################################################

class MediaTool:
    def __init__(self,runtext=''):
        self.runtext = runtext

    def run(self,mediafile,**options):         #多数情况下将忽略options
        fullpath = os.path.abspath(mediafile)  #当前工作目录可以是任何路径
        self.open(fullpath,**options)

class Filter(MediaTool):
    def open(self,mediafile,**ignored):
        media = open(mediafile,'rb')
        player = os.popen(self.runtext,'w')    #派生shell工具
        player.write(media.read())              #发送到它的stdin

class Cmdline(MediaTool):
    def open(self,mediafile,**ignored):
        cmdline = self.runtext % mediafile     #运行任何命令行
        os.system(cmdline)                     #用%s代表文件名

class Winstart(MediaTool):                        #采用Windows注册表
    def open(self,mediafile,wait=False,**other):  #也可以使用os.system('start file')
        if not wait:                               #允许对单前媒体的等待
            os.startfile(mediafile)
        else:
            os.system('start /WAIT ' + mediafile)

class Webbrowser(MediaTool):
    # file://必须用绝对路径
    def open(self,mediafile,**options):
        webbrowser.open_new('file://%s' % mediafile,**options)

######################################################################################
#媒体类型特异且系统平台特异的策略：修改，或者传入一个新的策略作为代替
######################################################################################

# 建立系统平台和播放器的对应关系：在此修改！

audiotools = {      #声频工具
    'sunos5':Filter('/usr/bin/audioplay'),      #os.popen().write()
    'linux2':Cmdline('cat %s > /dev/audio'),    #至少在zaurus系统上是这样的
    'sunos4':Filter('/usr/demo/SOUND/play'),    #是的,就是有这么老！
    'win32':Winstart()  #用startfile或system打开
    #'win32':Cmdline('start %s')
    }

videotools = {      #视频工具
    'linux2':Cmdline('tkcVideo_c700 %s'),     #zaurus pda
    'win32':Winstart(),                          #避免弹出DOS窗口
    }

imagetools = {     #图片工具
    'linux2':Cmdline('zimager %s'),            #zaurus pda
    'win32':Winstart(),
    }

texttools = {     #文本工具
    'linux2':Cmdline('vi %s'),                 #zaurus pda
    'win32':Winstart('notpad %s'),            #要不试试P有Edit?
    }

apptools = {
    'win32':Winstart()                          #doc,xls,等等：一切风险自行承担
    }

#建立文件名的mimetype与播放器表格的对应关系

mimetable = {'audio':audiotools,
             'video':videotools,
             'image':imagetools,
             'text':texttools,                 #不是html文本：否则用浏览器
             'application':apptools}

#########################################################################################
#顶层接口
#########################################################################################

def trywebbrowser(filename,helpmsg = helpmsg,**options):
    """
    用网页浏览器打开文本/html,另外对于其他文本类型，如果碰到未知mimetype
    或系统平台，也用网页浏览器进行尝试，作为最后办法
    :param filename:
    :param helpmsg:
    :param options:
    :return:
    """
    trace('trying browser',filename)
    try:
        player = Webbrowser()  #在本地浏览器中打开
        player.run(filename,**options)
    except:
        print(helpmsg % filename)  #否则没有能打开的程序

def playknownfile(filename,playertable={},**options):
    """
    播放类型已知的媒体文件：使用平台特异的播放器对象，如果这个平台下没有相应
    工具则派生一个网页浏览器；接受媒体特异的播放器表格
    :param filename:
    :param playertable:
    :param options:
    :return:
    """
    if sys.platform in playertable:
        playertable[sys.platform].run(filename,**options)  #特殊工具
    else:
        trywebbrowser(filename,**options)                  #通用架构

def playfile(filename,mimetable=mimetable,**options):
    """
    播放任意类型媒体文件：使用mimetypes猜测媒体类型并对应到平台特异的播放器表格；
    如果是文本/html,或者未知媒体类型，或者没有播放器表格，则派生网页浏览器
    :param filename:
    :param mimetable:
    :param options:
    :return:
    """
    contenttype,encoding = mimetypes.guess_type(filename)    #检查名称
    if contenttype == None or encoding is not None:       #无法猜测
        contenttype = '?/?'                                 #可能是.txt.gz
    maintype,subtype = contenttype.split('/',1)              #字符串格式：'图片/jepg'
    if maintype == 'text' and subtype == 'html':
        trywebbrowser(filename,**options)                    #特例
    elif maintype in mimetable:
        playknownfile(filename,mimetable[maintype],**options) #尝试使用播放器表格
    else:
        trywebbrowser(filename,**options)                    #其他类型

###############################################################
#自测代码
###############################################################

if __name__ == '__main__':                                  #媒体类型已知
    playknownfile('sousa.au',audiotools,wait=True)
    playknownfile('ora-pp3e.gif',imagetools,wait=True)
    playknownfile('ora-lp4e.jpg',imagetools)

    #媒体类型猜测完毕
    input('Stop players and press Enter')
    # playfile('ora-lp4e.jpg')                                #图像/jpeg
    # playfile('ora-pp3e.gif')                                #图像/gif
    # playfile('priorcalendar.html')                          #文本/html
    # playfile('lp4e-preface-preview.html')                   #文本/html
    # playfile('lp-code-readme.txt')                          #文本/纯文件
    # playfile('spam.doc')                                    #程序
    # playfile('spreadsheet.xls')                             #程序
    # playfile('sousa.au',wait=True)                          #音频/基本
    input('Done')                                            #保持打开,单击关闭
