"""
用法："python ...\Tools\visitor_edit.py string rootdir?"。
对SearchVisitor添加一个作为外部子类组分的编辑器自动行为；在遍历过程种
对含有字符串的每个文件自动弹出一个编辑器；在Windows下还可以使用editor='edit'
或'notepad';也可以传入一个搜索命令，在某些编辑器启动时即跳到第一处匹配；
"""

import os,sys
from visitor import SearchVisitor

class EditVisitor(SearchVisitor):
    """
    编辑startDir及其子目录下含有字符串的文件
    """
    editor = r'D:\Program Files (x86)\Notepad++\notepad++.exe'  #你的计算机上的编辑器可能有所不同

    def visitmatch(self,fpathname,text):
        os.system('%s %s' %(self.editor,fpathname))

if __name__=='__main__':
    visitor = EditVisitor(sys.argv[1])
    visitor.run('.'if len(sys.argv) < 3 else sys.argv[2])
    print('Edited %d files,visited %d' % (visitor.scount,visitor.fcount))
