import os
import cv2 as cv
import numpy as np
import re

src_path = r'D:\Programs\MyResearch\cars\image'     # 最好用cars计算均值
sub_dirs = os.listdir(src_path)
size = (512, 261)      # 设定图片resize尺寸
counter = 0
sum_img = np.zeros([size[1], size[0], 3], np.uint16)


def read_files(root, f):        # 负责读取和调整图片大小
    pattern = '.jpg'
    match = re.search(pattern, f)       # 匹配jpg类型文件
    if match:
        img_path = root + '//' + f
        img = cv.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)     # 读取图片
        img = cv.resize(img, size)      # 重设大小
        return img      # 返回图片


# 主程序
if __name__ == '__main__':
    # 遍历目录
    for i in sub_dirs:      # 循环所有子目录
        iter_path = src_path + '\\' + i
        for root, dirs, files in os.walk(iter_path):
            for f in files:
                img = read_files(root, f)
                if img is None:
                    continue
                sum_img = sum_img + img
                counter += 1
            if not dirs:        # 完成一次子目录循环后，计算平均并存储
                aver_img = (sum_img / len(files)).astype(np.uint8)
                save_name = iter_path + '\\' + root[-8:] + '.jpg'
                cv.imwrite(save_name, aver_img)
                print('save file to ' + save_name)
                sum_img = np.zeros([size[1], size[0], 3], np.uint16)
    cv.waitKey(0)