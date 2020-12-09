import os
import cv2 as cv
import re
import numpy as np
import copy

src_path = r'D:\Programs\MyResearch\trucks\image\20'       # 设定批处理图片路径
size = (512, 261)      # 设定图片resize尺寸
minArea = 50
counter = 1
compen = 20     # 检测通常能得到车头部分，但货箱部分有时和路面颜色接近，导致丢失信息，设定一个补偿值


def read_files(root, f):        # 负责读取和调整图片大小
    pattern = '.jpg'
    match = re.search(pattern, f)
    if match:
        img_path = root + '//' + f
        img = cv.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)     # 读取图片
        img = cv.resize(img, size)      # 重设大小
        return img      # 返回图片


def calculate_diff(f, img):
    averfile_name = f[14:22] + '.jpg'       # 门架和视频点位号
    averfile_path = src_path + '\\' + averfile_name
    aver_img = cv.imread(averfile_path)
    if aver_img is None:
        print('没有找到原图片或均值图。')       # 其实出现这个基本都是因为遍历了均值图，问题不大不优化了
        return None
    diff_img = cv.absdiff(img, aver_img)
    return diff_img


def process(img):
    img = cv.GaussianBlur(img, (3, 3), 0)
    img2Gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, imgGray = cv.threshold(img2Gray, 30, 255, cv.THRESH_TOZERO)        # 进行阈值截止处理
    # cv.imshow("imgGray", imgGray)       # 显示灰度图

    kernel = np.ones((10, 10), np.uint8)
    imgOpen = cv.morphologyEx(imgGray, cv.MORPH_OPEN, kernel)
    # cv.imshow("imgOpen", imgOpen)       # 显示开操作后的图

    imgOpenWeight = cv.addWeighted(imgGray, 1, imgOpen, -0.2, 20)
    # cv.imshow("imgOpenWeight", imgOpenWeight)       # 显示加权开操作后的图

    ret, imgBin = cv.threshold(imgOpenWeight, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)    # 进行二值化操作
    # cv.imshow("imgBin", imgBin)     # 显示二值操作后的图

    kernel = np.ones((5, 5), np.uint8)      # 对二值化图像做一次腐蚀操作，去掉杂点
    imgErode = cv.erode(imgBin, kernel)

    imgEdge = cv.Canny(imgErode, 50, 100)
    # cv.imshow("imgCanny", imgEdge)       # 显示取canny边缘后的图

    kernel = np.ones((60, 40), np.uint8)
    imgEdge = cv.morphologyEx(imgEdge, cv.MORPH_CLOSE, kernel)
    imgEdge = cv.morphologyEx(imgEdge, cv.MORPH_OPEN, kernel)

    # cv.imshow("imgEdge", imgEdge)      # 显示处理边缘后的图
    return imgEdge


def find_contours(imgEdge):
    contours, hierarchy = cv.findContours(imgEdge, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    contours = [cnt for cnt in contours if cv.contourArea(cnt) > minArea]
    return contours


def find_box(contours, img, f):
    global counter
    img_ori = copy.copy(img)
    for index, contour in enumerate(contours):
        rect = cv.boundingRect(contour)     # 获取矩形
        x = rect[0]
        y = rect[1]
        w = rect[2]
        h = rect[3]
        scale = h / w
        if scale > 1 and scale < 3:
            color = (255, 255, 255)
            cv.drawContours(img_ori, contours, index, (0, 0, 255), 1)
            if y-compen > 0:
                newimg = img[y - compen:y + h, x:x + w, :]
            else:
                newimg = img[y:y + h, x:x + w, :]
            if newimg.size > 0:
                # cv.imshow('cut', newimg)
                save_path = r'./save/' + src_path[-2:]
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                save_name = save_path + '/extract_' + str(counter) + '_' + f[-19:-10] + '.jpg'
                cv.imencode('.jpg', newimg)[1].tofile(save_name)
                # cv.imwrite(save_name, newimg)     # imwrite中文乱码
                print('图片提取至：' + save_name)
                counter += 1

    # cv.imshow("img_detect", img_ori)
    # cv.waitKey(0)


# 主程序
if __name__ == '__main__':
    # 遍历
    for root, dirs, files in os.walk(src_path):
        for f in files:
            img = read_files(root, f)
            if img is None:
                continue
            diff_img = calculate_diff(f, img)
            if diff_img is None:
                continue
            imgEdge = process(diff_img)
            contours = find_contours(imgEdge)
            find_box(contours, img, f)
    print('提取完成，共计 ' + str(counter), '张。')
    cv.waitKey(0)