import gurobipy as gp
from gurobipy import *
import pandas as pd
from gurobipy import Model
'''②优化a'''
'''—————————————————————————————————————参数——————————————————————————————————————'''
a_min = -5
a_max = 5
v_max = 16
xs = 300
xf = 235
sf = 15
Q = 10000
time = 120
tt = 1
q = 0.0001
aT = 120
dv = 5
ds = 1
hs = 2

number_car = [18, 22, 15, 16, 12, 20, 18, 18, 14, 16, 20, 17, 19, 21, 21]

kkk = 11
totalcar = number_car[kkk-1]

######
ppp = 3.5

dfx = pd.read_excel(f'C:\\Users\\User\\Desktop\\实验\\敏感性分析\\3流量\\{ppp}\\{ppp} sumo结果x{kkk}.xlsx')
dfv = pd.read_excel(f'C:\\Users\\User\\Desktop\\实验\\敏感性分析\\3流量\\{ppp}\\{ppp} sumo结果v{kkk}.xlsx')
dfL = pd.read_excel(f'C:\\Users\\User\\Desktop\\实验\\敏感性分析\\3流量\\{ppp}\\{ppp} 初步L{kkk}.xlsx')
totaltime = 240  # 仿真时长480s
cartime = 120

list = []
t0 = []
v0 = []
for i in range(0, totalcar):
    list.append(f'car.{i}')
for j in list:
    for i in range(0, totaltime-120):
        if dfx.loc[i, j] == 0:
            t0.append(i)
            v0.append(dfv.loc[i, j])
            break
# 至此，确定了t0，v0
car = [i for i in range(1, len(t0)+1)]
# 确定出car1,car2

car1 = []
car2 = []
for j in range(1, totalcar):
    if dfL.loc[t0[j-1]+aT, j] == 0:
        car1.append(j)
    elif dfL.loc[t0[j-1]+aT, j] == 1:
        car2.append(j)

m = Model('借道左转轨迹控制')

T, a, v, x, g, la, k, P, L, l, o, e, s, = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

for i in car:
    T[i] = range(t0[i - 1], t0[i - 1] + aT + 1, tt)  # T从1开始，T[1]
TT = range(0, 241, tt)

for i in car:
    for t in T[i]:
        a[i, t] = m.addVar(lb=a_min, ub=a_max, vtype=gp.GRB.CONTINUOUS, name="a(%d,%d)" % (i, t))
        v[i, t] = m.addVar(lb=0, ub=v_max, vtype=gp.GRB.CONTINUOUS, name="v(%d,%d)" % (i, t))
        x[i, t] = m.addVar(lb=0, vtype=gp.GRB.CONTINUOUS, name="x(%d,%d)" % (i, t))

        P[i, t] = m.addVar(vtype=gp.GRB.BINARY, name="P(%d,%d)" % (i, t))
        L[i, t] = m.addVar(vtype=gp.GRB.BINARY, name="L(%d,%d)" % (i, t))
        # l[i, t] = m.addVar(vtype=gp.GRB.BINARY, name="l(%d,%d)" % (i, t))
        # aa[i, t] = m.addVar(vtype=gp.GRB.CONTINUOUS, name="aa(%d,%d)" % (i, t))

for i in range(2, len(car) + 1):
    for ii in range(1, i):
        for t in T[i]:
            if (t >= t0[i - 1]) and (t <= t0[i - 2] + aT):
                o[i, ii, t] = m.addVar(lb=-1, ub=1, vtype=gp.GRB.INTEGER, name="o(%d,%d,%d)" % (i, ii, t))
                e[i, ii, t] = m.addVar(lb=0, ub=1, vtype=gp.GRB.INTEGER, name="e(%d,%d,%d)" % (i, ii, t))
                # s[i, ii, t] = m.addVar(vtype=gp.GRB.BINARY, name="s(%d,%d,%d)" % (i, ii, t))

G = m.addVars(TT, vtype=gp.GRB.BINARY, name="G")
m.update()

'''m.setObjectiveN(quicksum(-x[i, t0[i - 1] + aT] for t in T[i] for i in car), index=0, priority=5)
m.setObjectiveN(quicksum(-x[i, t] for i in car for t in
            (set(T[i]) & (set(range(30, 120)) | set(range(150, 240)) |
                          set(range(270, 360))))), index=1, priority=10)'''

m.setObjective(quicksum((-x[i, t0[i-1]+aT])for i in car) + 0.1 * quicksum(a[i, t] ** 2 for i in car2 for t in T[i]) +
             1/90*quicksum(-x[i, t] for i in car1 for t in (set(T[i]) & (set(range(31, 121)) | set(range(131, 241))))),
               gp.GRB.MINIMIZE)
# m.setObjective(quicksum((x[i, t0[i-1]+aT])for i in car) - quicksum(a[i, t] ** 2 for i in car for t in T[i]), gp.GRB.MAXIMIZE) 反例
for i in car1:
    m.addConstr(L[i, t0[i-1]+aT] == 0)
for i in car2:
    m.addConstr(L[i, t0[i-1]+aT] == 1)
m.addConstr(L[totalcar, t0[totalcar-1]+aT] == 0)
'''m.addConstr(L[7, t0[6] + aT] == 1)
m.addConstr(L[8, t0[7] + aT] == 1)
m.addConstr(L[9, t0[8]+aT] == 1)
m.addConstr(L[10, t0[9]+aT] == 1)
m.addConstr(L[11, t0[10]+aT] == 1)
m.addConstr(L[12, t0[11]+aT] == 1)'''
'''for i in range(8,15):
    m.addConstr(L[i, t0[i - 1] + aT] == 1)'''


'''初始设置约束'''
for i in car:
    m.addConstr(v[i, t0[i - 1]] == v0[i - 1])  # 初始速度
    m.addConstr(x[i, t0[i - 1]] == 0)  # 初始位置
    m.addConstr(L[i, t0[i - 1]] == 0)  # 初始车道
'''动力学约束'''
for i in car:
    for t in T[i]:  # T[i]是range，从0开始
        if t == T[i][0]:
            continue  # 使得t的循环从第二个元素开始
        m.addConstr(v[i, t] == v[i, t - 1] + a[i, t - 1] * tt)
        m.addConstr(x[i, t] == x[i, t - 1] + v[i, t - 1] * tt + 0.5 * a[i, t - 1] * (tt ** 2))
'''车道变换约束'''
for i in car:
    for t in T[i]:
        if t == T[i][0]:
            continue
        m.addConstr(L[i, t] >= L[i, t - 1])  # L不能减少，初始为0，只能变为1，不能1变0
        m.addConstr((xs - x[i, t] + Q * G[t] + Q * P[i, t - 1]) >= 0)  # 位置约束
        m.addConstr(L[i, t] - L[i, t - 1] <= x[i, t] / xf)  # 变道位置约束
        m.addConstr(Q * (1 - (L[i, t] - L[i, t - 1])) >= x[i, t] - xf - sf)
for t in TT:
    if t == 0:
        continue
    m.addConstr(quicksum((L[i, t] - L[i, t-1]) for i in car if (t-1 in T[i]) and (t in T[i])) <= 1)  # 一个时刻只有一辆车变道

'''车道约束''''''主和预双红灯且没过停止线时，车辆不能在借道左转车道'''
for i in car:
    for t in (set(T[i]) & (set(range(31, 99)) | set(range(151, 219)))):
        if t == T[i][0]:
            continue
        m.addConstr(L[i, t] - Q * P[i, t - 1] <= 0)  # 30的时候没过停车线，31的车道只能为0
'''信号灯约束'''
for t in TT:
    if t <= 120:
        m.addConstr(Q * (G[t] - 1) - q <= 30 - t)  # t为30时，G绿1；t为120时，G红0 （不然车辆在120位置大于300）
        m.addConstr(30 - t <= Q * G[t] - q)
    elif (t > 120) and (t <= 240):
        m.addConstr(Q * (G[t] - 1) - q <= 150 - t)
        m.addConstr(150 - t <= Q * G[t] - q)
    '''elif (t > 240) and (t <= 360):
        m.addConstr(Q * (G[t] - 1) - q <= 270 - t)
        m.addConstr(270 - t <= Q * G[t] - q)
    else:
        m.addConstr(Q * (G[t] - 1) - q <= 390 - t)
        m.addConstr(390 - t <= Q * G[t] - q)'''


'''停止线约束'''
for i in car:
    for t in T[i]:
        m.addConstr(Q * (P[i, t] - 1) + q <= x[i, t] - xs)  #
        m.addConstr(x[i, t] - xs <= Q * P[i, t] + q)
        # m.addConstr(aa[i, t] == (a[i, t] ** 2))

'''开口禁停约束,无法实现
for i in car:
    for t in T[i]:
        if t == T[i][0]:
            continue
        m.addConstr(Q * (xx[i, t] - 1) + q <= x[i, t] - x[i, t-1] - ee)
        m.addConstr(x[i, t] - x[i, t-1] - ee <= Q * xx[i, t] + q)
        m.addConstr(Q * (xd[i, t] - 1) + q <= xf + sf - x[i, t] - dv)
        m.addConstr(xf + sf - x[i, t] - dv <= Q * xd[i, t] + q)
for i in range(2, len(car)+1):
    for t in (set(T[i-1]) & set(T[i])):
        m.addConstr((xf - x[i, t] + Q * xx[i-1, t] + Q * xd[i-1, t]) >= 0)'''
'''车间距约束'''
'''for i in range(2, len(car) + 1):
    for t in T[i]:
        if t < t0[i - 1] + 14:
            m.addConstr(x[i - 1, t] - x[i, t] - (dv + ds + v[i, t] * hs) >= 0)'''
'''for i in range(2, len(car)+1):
    for t in T[i]:
        m.addConstr(D[i, t] >= dv + ds + v[i, t] * hs)'''
'''for i in range(2, len(car) + 1):
    for ii in range(1, i):
        for t in T[i]:
            if (t >= t0[i - 1] + 14) and (t <= t0[ii - 1] + aT):
                m.addConstr(x[ii, t] - x[i, t] - (dv + ds + v[i, t] * hs) >= -Q * e[i, ii, t])
                m.addConstr(o[i, ii, t] == (L[i, t] - L[ii, t]))
                m.addConstr(e[i, ii, t] == abs_(o[i, ii, t]))'''


'''def vehdistance (m, where):
    if where == GRB.Callback.MIPSOL:
        print('m._vars', m.cbGetSolution(m._x))

m._x = m.getVars()
# m.Params.lazyConstraints = 1'''

# Set the TuneResults parameter to 1
# m.Params.Heuristics = 0.5
# m.Params.MIPGap = 0.003
# m.Params.SimplexPricing = 2
# m.Params.GomoryPasses = 5
for i in range(2, len(car) + 1):
    for t in T[i]:
        if t == t0[i-1]:
            m.addConstr(x[i-1, t] - x[i, t] - (dv + ds) >= 0)
        elif t0[i-1] < t <= t0[i-1] + 14:
            m.addConstr(x[i-1, t] - x[i, t] - (dv + ds + v[i, t] * hs) >= 0)

for i in range(2, len(car) + 1):
    for ii in range(1, i):
        for t in T[i]:
            if (t > t0[i-1] + 14) and (t <= t0[ii-1] + aT):
                m.addConstr(x[ii, t] - x[i, t] - (dv + ds + v[i, t] * hs) >= -Q * e[i, ii, t])
                m.addConstr(o[i, ii, t] == (L[i, t] - L[ii, t]))
                m.addConstr(e[i, ii, t] == abs_(o[i, ii, t]))

# m.Params.NonConvex = 2
m.optimize()
'''m.tune()
if m.TuneResultCount > 0:
    m.getTuneResult(0)'''
# m._L = m.getVars()


    # Write tuned parameters to a file
     # m.write('tune2.prm')'''
# print(oo[14,13,148], e[14,13,148])
# data = open(r"C:\Users\ASUS\Desktop\实验\python\结果.txt", 'w+')
'''print(x, L, g, la, file=data)
data.close()
#输出 x_result = pd.DataFrame()
for i in car:
    for t in T[i]:

        x_result[i,t] = x[i, t]
x_result.to_excel(f"C:\\Users\\ASUS\\Desktop\\实验\\python\\x结果.xlsx")
'''
if m.Status == GRB.OPTIMAL:
    x_result = pd.DataFrame(index=TT, columns=car)
    L_result = pd.DataFrame(index=TT, columns=car)
    a_result = pd.DataFrame(index=TT, columns=car)
    v_result = pd.DataFrame(index=TT, columns=car)
    for i in car:
        for t in T[i]:
            x_result.iloc[t][i] = x[i, t].x
            L_result.iloc[t][i] = L[i, t].x
            a_result.iloc[t][i] = a[i, t].x
            v_result.iloc[t][i] = v[i, t].x
    x_result.to_excel(f"C:\\Users\\User\\Desktop\\实验\\敏感性分析\\3流量\\{ppp}\\{ppp} 最终x{kkk}.xlsx")
    L_result.to_excel(f"C:\\Users\\User\\Desktop\\实验\\敏感性分析\\3流量\\{ppp}\\{ppp} 最终L{kkk}.xlsx")
    a_result.to_excel(f"C:\\Users\\User\\Desktop\\实验\\敏感性分析\\3流量\\{ppp}\\{ppp} 最终a{kkk}.xlsx")
    v_result.to_excel(f"C:\\Users\\User\\Desktop\\实验\\敏感性分析\\3流量\\{ppp}\\{ppp} 最终v{kkk}.xlsx")