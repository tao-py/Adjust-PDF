import fitz
from paddleocr import PaddleOCR
import tkinter as tk
from tkinter import filedialog
import os

'''打开选择文件夹对话框'''
root = tk.Tk()
root.withdraw()
# fname = filedialog.askdirectory()#获得选择好的文件夹路径
fname = filedialog.askopenfile()
print(fname)

'''重命名所选取的文件'''
st = str(fname)#转为字符串
begin=st.index("'")
over=st.index("'",begin+1)
reflname = st[begin+1:over-4]+"adjust"+st[over-4:over]
def flcut(filename,self):
    st=str(filename)
    print(st)
    begin = st.index("'")
    over = st.index("'", begin + 1)
    st=st[begin+1:over]
    find=[]
    for i in range(len(st)):
        if st[i] == self:
            find.append(i)
    return st[:find[-1]]

'''使用PyMuPDF库对PDF文件，提取图纸页码信息部分指定区域截图'''
doc = fitz.open(fname)  # 打开文件
pagenumber=doc.page_count #PDF的总页数
for page in doc:  # iterate through the pages
    mat = fitz.Matrix(2, 2)  # zoom factor 2 in each direction
    rect = page.rect  # the page rectangle
    mp = (rect.tl + rect.br) * 0.85  # its middle point, becomes top-left of clip
    print(mp+30, rect.br*0.95)
    clip = fitz.Rect(mp+35, rect.br*0.945).round()  # the area we want
    # clip = fitz.Rect(0, -1, 124, 456).round()  # the area we want
    pix = page.get_pixmap(matrix=mat, clip=clip)  # render page to an image
    pix.save("page-%i.png" % page.number)  # store image as a PNG
'''使用Paddleocr库对页码图片信息进行文字提取'''
pageID={}
box=[]
ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory
for i in range(pagenumber):
    img_path = "{}\page-{}.png".format(os.getcwd(), i)
    result = ocr.ocr(img_path, cls=True)
    for idx in range(len(result)):
        res = result[idx]
        if res == []:            #如果识别页面结果为空，认定为封面页，封面页顺序自调，封面页PDF图纸信息赋值为“0”。
            box.append(("0","0"))
            print("wu")
        for line in res:
            print(line)  #用于显示文字识别位置信息、结果、精确度的数组
            for j in line:
                print(j)
                box.append(j)
    print(box)
    os.remove(img_path)###删除已识别的图片
    st=box[-1][0].replace(" ","")#去掉PDF图纸页码信息中包含的空格，暂存在st中
    print(st)
    yema = ""
    for j in st:
        if j == "/":
            break
        else:
            yema+= j
    pageID.setdefault(i,eval(yema))
'''pageID以字典的格式储存PDF位置页码和图纸页码，其中字典的键为PDF位置页码,字典的值为PDF图纸页码'''
print(pageID)
'''定义adjuast_pg函数，实现adjustID = {}字典存储去除封面页PDF图纸信息为“0”的，待处理信息'''
def adjust_pg(pageID,i):
    adjustID = {}  #储存待调节的页码信息，调整后随之变动，动态字典。
    for j in range(pagenumber-i):
        pdf_page = pageID[j]
        if pdf_page > 0:
            adjustID.setdefault(j, pdf_page)
    return (adjustID)

'''仅修改有指定区域的页码，图纸页码信息为0未有效提取，亦为封面页'''
adjustID = adjust_pg(pageID,0)
size_0 = len(adjustID)
print("初始长度为：", len(adjustID))
#########################################################################
                        #页码自动调整部分#
#########################################################################
for i in range(len(adjustID)):
    adjustID=adjust_pg(pageID,i)#调用adjuast_pg函数
    print("字典adjustID最小值对应的键值=",min(adjustID, key=adjustID.get))
    #字典中最小值对应的键值，即图纸页码最小所在PDF位置页码的值，将其移动至最后，它之后的PDF位置信息将减少1。
    min_page = min(adjustID, key=adjustID.get)#获取字典adjuastID中最小值所对应的键。即图纸页码最小所在PDF位置页码的值。
    pno = min_page
    doc.move_page(pno, to=-1)#使用PyMuPDF，document.move移动至最后一页
    size_1 = len(adjustID)
    size = size_0-size_1
    for j in range(pagenumber-size-min_page-1):
        print(min_page + j, "=", min_page + j + 1)
        pageID[min_page + j] = pageID[min_page + j + 1]
    pageID.pop(pagenumber - i - 1)
doc.save(reflname) #另存为reflname
os.startfile(flcut(fname,"/"))#打开保存处理后PDF所在文件夹窗口。