import os, shutil
import re

path = r'D:\Programs\MyResearch\vehicle_data'

pattern = r'vehicle_data'
p0 = r'_0_'  # 黄牌车1，蓝牌车0
p1 = r'binimage'
p2 = r'licenseimage'
p3 = r'image'

c1 = 0
c2 = 0
c3 = 0

for root, dirs, files in os.walk(path):
    for f in files:
        m0 = re.search(p0, f)
        if m0:
            m1 = re.search(p1, f)
            m2 = re.search(p2, f)
            m3 = re.search(p3, f)

            if m1:
                saveroot = re.sub(pattern, p1, root)
                c1 += 1
            elif m2:
                saveroot = re.sub(pattern, p2, root)
                c2 += 1
            elif m3:
                position = f[14:22]
                saveroot = re.sub(pattern, p3, root)
                saveroot = saveroot + '\\' + position
                c3 += 1

            savefullpath = saveroot + '\\' + f
            if not os.path.exists(saveroot):
                os.makedirs(saveroot)
            shutil.copyfile((os.path.join(root, f)), savefullpath)

            print("save to", savefullpath)

print('分离了binimage文件:', str(c1))
print('分离了licenseimage文件:', str(c2))
print('分离了image文件:', str(c3))