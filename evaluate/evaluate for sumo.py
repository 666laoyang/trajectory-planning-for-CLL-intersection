import pandas as pd
import math
number_car = [11, 13, 12, 13, 10, 13, 15, 13, 10, 11, 14, 13, 12, 14, 12]

kkk = 15
totalcar = number_car[kkk-1]

######
ppp = 1.0


dfx = pd.read_excel(f'C:\\Users\\User\\Desktop\\实验\\敏感性分析\\1绿信比\\{ppp}\\{ppp} sumo结果x{kkk}.xlsx')
dfv = pd.read_excel(f'C:\\Users\\User\\Desktop\\实验\\敏感性分析\\1绿信比\\{ppp}\\{ppp} sumo结果v{kkk}.xlsx')
dfa = pd.read_excel(f'C:\\Users\\User\\Desktop\\实验\\敏感性分析\\1绿信比\\{ppp}\\{ppp} sumo结果a{kkk}.xlsx')

totaltime = 240  # 仿真时长480s
flow = 400  # 流量400veh/h
cartime = 120

list = []
xmax = []
v0 = []
t0 = []

#  dfx.iloc[12][2] 对应左边的数字，车辆即列从1开始

for j in range(1, totalcar+1):
    for i in range(0, totaltime-120):
        if dfx.iloc[i][j] == 0:
            xmax.append(dfx.iloc[i+120][j])   # 找到车辆120s后的位置
            v0.append(dfv.iloc[i][j])    # 找到车辆的初始速度
            t0.append(i)   # 找到车辆的进场时间
            break
vmax = 16
amax = 5
aT = 120
'''-----------------------计算延误---------------------------'''
delay = 0
for i in range(0, totalcar):
    delay = delay + 120-((vmax - v0[i]) / amax + (xmax[i] - (vmax**2 - v0[i]**2) / (2 * amax)) / vmax)  # 所有车辆的延误
aver_delay = delay / totalcar  # 计算平均延误
print(aver_delay)
'''----------------------计算舒适度---------------------------'''
comfort = 0
for j in range(1, totalcar+1):
    comfort = comfort + sum(dfa.iloc[i][j] ** 2 for i in range(t0[j-1], t0[j-1]+120))  # 最后1s的加速度不算

distance = 0
for i in range(0, totalcar):
    distance = distance + xmax[i]

print(comfort / distance * 1000)
'''-----------------------计算燃油-------------------------'''
fuel = 0
# 做k,c系数表
k = [[-7.735, 0.2295, -5.61*10**-3, 9.773*10**-5], [0.02799, 0.0068, -7.722*10**-4, 8.38*10**-6],
     [-2.228*10**-4, -4.402*10**-5, 7.90*10**-7, 8.17*10**-7], [1.09*10**-6, 4.80*10**-8, 3.27*10**-8, -7.79*10**-9]]
c = [[-7.735, -0.01799, -4.27*10**-3, 1.8829*10**-4], [0.02804, 7.72*10**-3, 8.375*10**-4, 3.387*10**-5],
     [-2.199*10**-4, -5.219*10**-5, -7.44*10**-6, 2.77*10**-7], [1.08*10**-6, 2.47*10**-7, 4.87*10**-8, 3.79*10**-10]]
for j in range(1, totalcar+1):
    for i in range(t0[j-1], t0[j-1]+120):
        if dfa.iloc[i][j] >= 0:
            fuel = fuel + math.exp(sum(k[j1][j2] * (dfv.iloc[i][j]*3.6)**j1 * (dfa.iloc[i][j]*3.6)**j2
                                       for j1 in range(0, 4) for j2 in range(0, 4)))
        elif dfa.iloc[i][j] < 0:
            fuel = fuel + math.exp(sum(c[j1][j2] * (dfv.iloc[i][j]*3.6)**j1 * (dfa.iloc[i][j]*3.6)**j2
                                       for j1 in range(0, 4) for j2 in range(0, 4)))


print(fuel / distance * 1000)

