DEBUG = False
import cv2
import os
import numpy as np
import time
import matplotlib.pyplot as plt
import shutil
import random
from math import sqrt,cos,sin,asin
pi = 3.1415926#圆周率
work_path = os.getcwd()
order_start = work_path + '/file/adb.exe '
fix_ky,fix_kx = 1,1




#####
Max_step = 1000#每轮最大迭代数，避免死循环
# obj_color_list = [(55,89,106)]

v0_mh = 10#小球初始速度(像素/帧）
dt = 1.0
g = 0.1345#重力加速度

r = 10#小球半径

wall_l_k = 0.95#墙壁弹性系数
obj_l_k = 0.87#物体弹性系数

def my_int(num):
    return int(round(num))

shoot_p = (360,195)#发射位置
ps_start_y = 260#物块最高能到达的位置
R = 360#半屏宽
s_cita = asin((ps_start_y-shoot_p[1])/R)
N = 30#遍历发射角度的数量（精度）
Tap_ps = []#遍历发射按压点
for k in range(0, N):
    d_ct = (pi-2*s_cita)/N
    cita = k*d_ct+s_cita
    x = my_int(R*cos(cita))+shoot_p[0]
    y = my_int(R*sin(cita))+shoot_p[1]
    Tap_ps.append((x, y))

#####
def _run(imgfile_name):
    #如果第一次开始随便点击一下
    if _is_begin():
        _tap()

    #开始循环执行游戏
    is_on = True
    try_n = 0
    i=1
    while is_on:

        _log("第%d次" % i, "EVENT")
        i+=1

        if not _get_screenshot(imgfile_name):
            continue

        img_rgb = _read_screenshot(imgfile_name)
        output_rgb = np.copy(img_rgb)

        if _not_in_game(img_rgb):
            _log("脱离游戏" , "EVENT")
            _tap()
            _tap((360,1050))
            time.sleep(3)
            continue

        best_tap_point = _get_BTP(img_rgb,output_rgb)
        _save_outputimg(output_rgb)
        if DEBUG:
            break
        _tap(best_tap_point)

        time.sleep(5)

def _not_in_game(img_rgb):
    # t = tuple(img_rgb[1][1])

    if tuple(img_rgb[1][1]) == (53,51,46):
        return False
    else:
        return True



def _is_Edge(img_rgb,c_e):

    p1 = (my_int(c_e[1]), my_int(c_e[0]))
    c_color = img_rgb[p1[0],p1[1]]

    if c_color[0] > 100 or c_color[1] > 100 or c_color[2] > 100:
        return True
    else:
        return False

def _init_log():  # 在log中加标记以便与历史纪录区分
    if not os.path.exists("log"):
        os.makedirs("log")
    log_con = "\n\n\n******* 初始化 *******\n"
    with open("log/Logs.log", "a") as f:
        f.write(log_con)


def _log(log_con, type_name, is_print=True, is_save = False):
    if is_print:
        print(log_con)

    if is_save:
        with open("log/Logs.log", "a", encoding="utf-8") as f:
            f.write(log_con)

        with open("log/%s.log" % type_name, "a", encoding="utf-8") as f:
            f.write(log_con)


def _get_screenshot(name):
    if DEBUG:
        return True

    path = 'temp/%s.png'%name
    if os.path.exists(path):
        shutil.copy(path,'temp/last_%s.png'%name)
        os.remove(path)

    while True:
        print("开始截屏...", end="")
        _cmd(order_start + 'shell screencap -p /sdcard/%s.png' % str(name))
        _cmd(order_start + 'pull /sdcard/%s.png ./temp' % str(name))
        if os.path.exists(path):
            print("完成!")
            return True
        else:
            input("获取截图失败，请检查手机是否连接到电脑，并是否开启开发者模式,回车继续")




def find_between(args, con):
    left_index = con.find(args[0])
    right_index = con.rfind(args[1])
    if (left_index + 1) * (right_index + 1):
        return con[left_index + len(args[0]):right_index]
    return


def init_files(cla):  # 检查工作环境和文件存在性，如果不存在报错
    for file_name in cla.work_files:
        cla.work_files[file_name] = os.path.join(cla.work_path,
                                                 cla.work_files[file_name])
        if not os.path.exists(cla.work_files[file_name]):
            os.mknod(cla.work_files[file_name])
    for file_name in cla.work_dirs:
        cla.work_dirs[file_name] = os.path.join(cla.work_path,
                                                 cla.work_dirs[file_name])
        if not os.path.exists(cla.work_dirs[file_name]):
            os.mkdir(cla.work_dirs[file_name])

def _read_screenshot(imgfile_name):
    global fix_ky,fix_kx
    img_rgb = cv2.imread('temp\%s.png' % imgfile_name)
    fix_ky = img_rgb.shape[0] / 1280
    fix_kx = img_rgb.shape[1] / 720
    if fix_kx < fix_ky:
        Ly = 1280 * fix_kx
        b = my_int((img_rgb.shape[0 ] -Ly ) /2)
        e = img_rgb.shape[0] - b
        img_rgb = img_rgb[b:e ,:]
    elif fix_kx > fix_ky:
        Lx = 720 * fix_ky
        b = my_int((img_rgb.shape[1 ] -Lx ) /2)
        e = img_rgb.shape[1] - b
        img_rgb = img_rgb[:, b:e]

    if fix_ky != 1 and fix_kx != 1:
        img = cv2.resize(img_rgb ,(720 ,1280) ,interpolation=cv2.INTER_AREA)
    else:
        img = img_rgb
    return img

def _cmd(cmd_str):
    p = os.popen(cmd_str)
    p.read()
    # print(cmd_str,r.read(),sep="\n")

for dir_name in ["temp"]:
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
if not os.path.exists("file"):
    print("缺少含有必要文件的file文件夹")
    input("再见!回车键结束")
    exit()

def _main():
    # 截图保存名称
    imgfile_name = "screenshot"

    _init_log()
    _log("开始准备...", "EVENT")
    _get_screenshot(imgfile_name)
    img_rgb = _read_screenshot(imgfile_name)
    last_output_rgb = img_rgb

    _log("准备完成！开始运行\n", "EVENT")
    _run(imgfile_name)




BTP_color = (0,255,255);BTP_r = 7
curP_color = (0,255,0);curP_r = 3
ep_color = (255,0,255);ep_r = 0
pengzhuang_color = (255,0,0);pengzhuang_r = 0
e_mean_color = (0, 0, 255);e_mean_r = 2

def _save_outputimg(output_rgb, name="output"):
    # 将图片输出以供调试
    cv2.imwrite(r'temp\%s.png' % name, output_rgb)
    return output_rgb



def _get_BTP(img_rgb,output_rgb):


    best_score = 0
    best_tap_point = None
    _log("正在计算...","EVENT")
    i = 0
    for p in Tap_ps:
        i += 1
        print("%f%%" % (i*100/N),end=" ")
        score = _judge_tap_point(img_rgb,p,output_rgb)
        if score>=best_score:
            best_tap_point = p
            best_score = score
    print()
    cv2.circle(output_rgb, best_tap_point, BTP_r, BTP_color, -1)

    best_output_rgb = np.copy(img_rgb)

    _judge_tap_point(img_rgb, best_tap_point, best_output_rgb)
    cv2.circle(best_output_rgb, best_tap_point, BTP_r, BTP_color, -1)
    _save_outputimg(best_output_rgb,"best_output")

    _log("发现最优点击坐标%d,%d"%best_tap_point,"EVENT")

    return best_tap_point


Circle_E_dps = []

M = 90
for k in range(0,M):
    dct = 2*pi/M
    x = r*cos(k*dct)
    y = r*sin(k*dct)
    Circle_E_dps.append((x,y))

def _int_pos(pos):
    return (my_int(pos[0]),my_int(pos[1]))

def _judge_tap_point(img_rgb,p,output_rgb):
    cur_pos = shoot_p
    v0 = _get_v0(p)
    v = v0
    score = 0
    i = 0
    x = r/(v0_mh*dt)
    while True:
        ds = (v[0]*dt,v[1]*dt)
        cur_pos = (cur_pos[0]+ds[0],cur_pos[1]+ds[1])
        if _is_out(cur_pos) or i > Max_step:
            break

        cv2.circle(output_rgb, _int_pos(cur_pos), curP_r, curP_color, -1)
        dv = (0,g*dt)
        v = (v[0]+dv[0],v[1]+dv[1])

        if i > x:
            v,flag,mean_e = _pengzhuang(img_rgb,cur_pos,v,output_rgb)
        else:
            flag = 0

        if score<flag:
            if DEBUG:
                print("score:",score,"flag:",flag,"tap_p:",p,"mean_e:",mean_e)
            score = flag

        # score += flag

        # if _v2v_mh(v) <0.2:
        #     v = _v_mh2v(10,v)

        i += 1

    if DEBUG:
        print(i,end="\t")





    return score

bottom_y = 1200
def _is_out(pos):
    if pos[1]>bottom_y or pos[0]>=719-r or pos[0] <= r or pos[1]<=r:
        return True
    else:
        return False

def _pengzhuang(img_rgb,cur_pos,v,output_rgb):
    E_p = []
    flag =0
    t_sum_e = (0,0)
    t_e_n = 0

    for c_e_dps in Circle_E_dps:
        c_e = (c_e_dps[0]+cur_pos[0],c_e_dps[1]+cur_pos[1])
        cv2.circle(output_rgb, _int_pos(c_e), pengzhuang_r, pengzhuang_color, -1)

        if _is_Edge(img_rgb,c_e):
            e = c_e
            E_p.append(e)
            cv2.circle(output_rgb, _int_pos(e), ep_r, ep_color, -1)
            t_sum_e = (t_sum_e[0]+e[0],t_sum_e[1]+e[1])
            t_e_n += 1
    mean_e = (-1,-1)
    if(t_e_n):

        mean_e = (t_sum_e[0]/t_e_n,t_sum_e[1]/t_e_n)

        #!!!

        flag = 1000/(mean_e[1]-280)

        lost_k = obj_l_k
        if mean_e[0] >=660 or mean_e[0] <= 55 or mean_e[1] < ps_start_y:
            lost_k = wall_l_k
            flag = 0
        cv2.circle(output_rgb, _int_pos(mean_e), e_mean_r, e_mean_color, -1)
        s = (mean_e[0]-cur_pos[0], mean_e[1]-cur_pos[1])

        v = _cal_pengzhuang_v(s,v,lost_k)


    return v,flag,mean_e

def _v2v_mh(v):
    return sqrt(v[0]*v[0]+v[1]*v[1])

def _v_mh2v(v_mh,r):
    r_mh = sqrt(r[0]*r[0]+r[1]*r[1])
    return (v_mh*r[0]/r_mh,v_mh*r[1]/r_mh)



black_color = np.array([255,255,255])
bg_color = np.array([255,255,255])





def _cal_pengzhuang_v(s,v,lost_k):
    temp1 = float(s[0]*v[0] + s[1]*v[1])
    temp2 = float(s[0]*s[0] + s[1]*s[1])
    if(temp2 and temp1>0):### ###一次是穿模顺向问题，一次是双重碰撞问题
        new_v = ((v[0] - lost_k*s[0]*2*temp1/temp2),(v[1] - lost_k*s[1]*2*temp1/temp2))
    else:
        new_v = v
    return new_v



def _get_v0(p):
    p_mh = (p[0]-shoot_p[0],p[1]-shoot_p[1])
    return _v_mh2v(v0_mh,p_mh)

def _tap(tap_point = (360,1122)):

    cmd_str = order_start + 'shell input tap %d %d' % (my_int(tap_point[0]*fix_kx),my_int(tap_point[1]*fix_ky))
    _cmd(cmd_str)
    _log("点击坐标%d,%d"%tap_point, "EVENT")

def _is_begin():
    return False

if __name__ == "__main__":
    _main()
    # print(_cal_pengzhuang_v((-5,-4),(-0.9,-0.1)))
