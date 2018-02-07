#coding:utf-8
"""
########################################
测试：使用类和子类封装os.wall调用手法某些细节，以便进行遍历和搜索
#########################################
"""
###########################################(父类：FileVisitor)############################
import os,sys;
class FileVisitor:
    """
    访问startDir(默认为'.')下所有非目录文件；可通过重载visit*方法定制文件/目录处理器;
    情境参数、属性为可选的子类特意的状态;追踪开关：0代表关闭，1代表显示目录，2代表显
    示目录及文件
    """
    def __init__(self,context=None,trace=2):
        self.fcount = 0
        self.dcount = 0
        self.context = context
        self.trace = trace

    def run(self,startDir=os.curdir,reset=True):
        if reset:self.reset()
        for (thisDir,dirsHere,filesHere) in os.walk(startDir):
            self.visitdir(thisDir)
            for fname in filesHere:                  # 对非目录文件进行迭代
                fpath = os.path.join(thisDir,fname)  #fname不带路径
                self.visitfile(fpath)

    def reset(self):                      #为了重复使用遍历器
        self.fcount = self.dcount = 0      #为了相互独立的遍历操作

    def visitdir(self,dirpath):   #called for each dir
        self.ccount += 1          #待重写或扩展
        if self.trace > 0:print(dirpath,'...')

    def visitfile(self,filepath): #called for each file
        self.fcount += 1          #待重写或扩展
        if self.trace > 1:print(self.fcount,'=>',filepath)
##############################################(父类：FileVisitor)end#################################

###############################################(继承FileVisitor的子类:SearchVisitor)#################
class SearchVisitor(FileVisitor):
    """
    在startDir及其子目录下的文件中搜索字符串;子类：根据需要重新定义visitmatch、扩展列表
    和候选；子类可以使用testexts来指定进行搜索的文件类型(还可以重定义候选以对文本内容使
    用mimetypes:参考之前相关部分)
    """
    skipexts = []
    testexts = ['.txt','.py','.pyw','html','.c','.h']    #搜索带有这些扩展名的文件
    #skipexts = ['.gif','.jpg','.pyc','.o','.a','.exe']       #或者跳过带有这些扩展名的文件

    def __init__(self,searchkey,trace=2):
        FileVisitor.__init__(self,searchkey,trace)
        self.scount = 0

    def reset(self):                               #进行相互独立的遍历时
        self.scount = 0

    def candidate(self,fname):
        ext = os.path.splitest(fname)[1]
        if self.testexts:
            return ext in self.testexts            #在测试列表中时
        else:
            return ext not in self.skipexts

    def visitfile(self,fname):                     #匹配测试
        FileVisitor.visitfile(self,fname)
        if not self.candidate(fname):
            if not self.trace > 0:print('Skipping',fname)
        else:
            text = open(fname).read()             #如果不能解码则使用'rb'模式
            if self.context in text:             #也可以用text.fine()!=-1
                self.visitmatch(fname,text)
                self.scount += 1

    def visitmatch(self,fname,text):             #处理一个匹配文件
        print('%s has %s'%(fname,self.context)) #在低一级的水平重写
#################################################(继承FileVisitor的子类:SearchVisitor)end################

if __name__=='__main__':  #自测逻辑业务
    dolist = 1
    dosearch = 2 # 3=进行列出和搜索
    donext = 4 #添加了下一个测试时

    def selftest(testmask):
        if testmask & dolist:
            visitor = FileVisitor(trace=2)
            visitor.run(sys.argv[2])
            print('Visited %d files and %d dirs '%(visitor.fcount,visitor.dcount))

        if testmask & dosearch:
            visitor = SearchVisitor(sys.argv[3],trace=0)
            visitor.run(sys.argv[2])
            print('Found in %d files,visited %d' %(visitor.scount,visitor.fcount))
    selftest(int(sys.argv[1])) #例如，3 = dolist|dosearch
