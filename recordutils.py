import time
from PIL import ImageGrab,Image
import shelve
import io
# import asyncio
# import cv2
import os
import time
import numpy as np
import pillow_heif
import datetime
from paddleocr import PaddleOCR

pillow_heif.register_heif_opener()#将屏幕截图压缩为heif格式以减小占用
ocr1=PaddleOCR(use_angle_cls=True, lang="ch")
piccache={}
# def cacheall(path,datanames,x,y):
#     global piccache
#     if "data" in path:
#             path1=path
#     else:
#             path1="data/"+path
#     db=shelve.open(path1.replace(".dat",''),flag='r')
#     for i in datanames:
#         cache=[]
#         xyz=db[i][0]
#         pic=Image.open(io.BytesIO(xyz))
#         cur_width, cur_height = pic.size
#         scale = min(y / cur_height, x / cur_width)
#         pic = pic.resize((int(cur_width * scale), int(cur_height * scale)), Image.ANTIALIAS)
#         with io.BytesIO() as bio:
#             pic.save(bio, format="PNG")
#             cache.append(bio.getvalue())
#             cache.append(x)
#             cache.append(y)
#         piccache[i]=cache
#     db.close()
        
#获得一副截图前四张和后四张图用了缓存
def get_surrounding_elements(lst, elem):
    try:
        index = lst.index(elem)
    except ValueError:
        return []
    start = max(0, index - 4)
    end = min(len(lst), index + 5)
    return lst[start:end]
#移除掉不在当前图片周围的图片缓存，以减小内存使用
def remove_unlisted_keys(dct, key_list):
    keys_to_remove = [key for key in dct.keys() if key not in key_list]
    for key in keys_to_remove:
        del dct[key]
    return dct

#刷新缓存，提高图片加载速度
def refresh_cache(path,picname,datanames):
    global piccache
    if "data" in path:
            path1=path
    else:
            path1="data/"+path
    db=shelve.open(path1.replace(".dat",''),flag='r')
    cachenames=get_surrounding_elements(datanames,picname)
    for i in cachenames:
        if i in piccache:
            #print('跳过缓存')
            continue
        xyz=db[i][0]
        pic=Image.open(io.BytesIO(xyz))
        piccache[i]=pic
    piccache=remove_unlisted_keys(piccache,cachenames)
    db.close()
#存储图片与文字识别信息
def save_pic(path,picname,pic,data):
        db=shelve.open(path,flag='c',writeback=True)
        picio=io.BytesIO()
        pic.save(picio,optimize=True)
        db[picname]=[picio.getvalue()]
        db.close()
        path1=str(path.replace('data/',''))
        db1=shelve.open("data/alldata",flag='c',writeback=True)
        if (path1 not in db1)or(db1[path1] is None):
            db1[path1]={}
        db1[path1][picname]=data
        db1.close()
        return True
#获得图片
def get_pic(path,picname):
        if picname in piccache:
            #print('缓存调用!')
            return piccache[picname]
        if "data/" in path:
            path1=path
        else:
            path1="data/"+path
        db=shelve.open(path1.replace(".dat",''),flag='r')
        xyz=db[picname][0]
        pic=Image.open(io.BytesIO(xyz))
        db.close()
        return pic   
#获得文字识别信息
def get_data(path,picname):
    if "data/" in path:
        path=path.replace("data/","")
    db=shelve.open("data/alldata",flag='r')
    data=db[path][picname]
    db.close()

# def get_dataresize(path,picname,x,y):
#     if picname in piccache:
#         print('缓存调用!')
#         return piccache[picname][0]
#     pic=get_data(path,picname)
#     cur_width, cur_height = pic.size
#     scale = min(y / cur_height, x / cur_width)
#     pic = pic.resize((int(cur_width * scale), int(cur_height * scale)), Image.ANTIALIAS)
#     with io.BytesIO() as bio:
#         pic.save(bio, format="PNG")
#         del pic
#         return bio.getvalue()

#获得今天记录的文件名
def get_filename():
    today = datetime.datetime.today()
    filename='data/'+str(today.year)+'.'+str(today.month)+'.'+str(today.day)
    return filename
#捕获截图
def pic_capture():
    global ocr1
    picname=str(time.time())
    try:
        pic=ImageGrab.grab()
    except:
        return False
    result=ocr1.ocr(np.array(pic))
    heifpic=pillow_heif.from_pillow(pic)
    if save_pic(get_filename(),picname,heifpic,result) is False:
        raise Exception('图片存储失败！')
    return True

#用来给文件名排序
def sort_numbers(l):
    a=l.split(".")
    return int(a[0]+a[1]+a[2])
#获得所有文件名
def get_all_filenames():
    filenames = os.listdir("data")
    datanames=[]
    for i in filenames:
        if ("dat" in i)and("alldata" not in i):
            datanames.append(i)
    datanames.sort(key=sort_numbers)
    return datanames
#获得文件中所有图片名字
def get_datanames(dataname):
    if "data" in dataname:
        db=shelve.open(dataname.replace(".dat",''),"r")
    else:
        db=shelve.open("data/"+dataname.replace(".dat",''),"r")
    datas=[]
    for i in db:
        datas.append(i)
    db.close()
    return datas

