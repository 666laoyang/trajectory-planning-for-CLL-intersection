import os
import sys
import optparse
import traci
import pandas as pd
'''证明环境变量设置好了'''
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


if __name__ == "__main__":
    options = get_options()   
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')
    traci.start([sumoBinary, "-c", "shiyan3.sumocfg"])
    '''----------------------------------------------------------------------------------------------'''
    '''创建存储车辆x和v的表格'''
    totaltime = 240  # 仿真时长s

    cartime = 120

    list = []
    for i in range(0, 1):
        list.append(f'car.{i}')

    position = pd.DataFrame(index=range(0, totaltime), columns=list)
    speed = pd.DataFrame(index=range(0, totaltime), columns=list)
    hhh = pd.DataFrame(index=range(0, totaltime), columns=list)
    acceleration = pd.DataFrame(index=range(0, totaltime), columns=list)

    for step in range(0, totaltime):
        if (traci.edge.getLastStepVehicleNumber('E5') > traci.edge.getLastStepVehicleNumber('E13')) and (traci.trafficlight.getRedYellowGreenState('J12') == 'GG'):  # 如果常规车道上的车辆数小于借道车道（当前步长）
            a = []
            a = traci.edge.getLastStepVehicleIDs('E4')   # 得到路段E4上车辆的ID
            if a:
                # if (traci.vehicle.getPosition(a[-1])[0] + traci.vehicle.getSpeed(a[-1]) + 0.5 * traci.vehicle.getAcceleration(a[-1])) >250:

                # if (traci.vehicle.getPosition(a[-1])[0] >= 240) and (traci.vehicle.getPosition(a[-1])[0] <= 250):
                traci.vehicle.setRoute(a[-1], ['E4', 'E7', 'E13', 'E14'])
                print(a[-1])

        # position.iloc[[step],[f'car.{i}']] = [(traci.vehicle.getPosition(i)) for i in all_vehicle_id]
        # 提取车辆x,v
        all_vehicle_id = traci.vehicle.getIDList()  # 获取所有车辆的ID
        for i in all_vehicle_id:
            position.loc[[step], [i]] = traci.vehicle.getDistance(i)
            hhh.loc[[step], [i]] = traci.vehicle.getPosition(i)[1]
            speed.loc[[step], [i]] = traci.vehicle.getSpeed(i)
            acceleration.loc[[step], [i]] = traci.vehicle.getAcceleration(i)
            # print(traci.vehicle.getTimeLoss(i))
            if step >= 120:
                if pd.notnull(position.at[step-120, i]):
                    traci.vehicle.remove(i, reason=3)

        traci.simulationStep()

    kkk = 2

    ######
    ppp = 3.5
    position.to_excel(f"C:\\Users\\User\\Desktop\\实验\\敏感性分析\\3流量\\{ppp}\\{ppp} sumo结果x{kkk}.xlsx")
    speed.to_excel(f"C:\\Users\\User\\Desktop\\实验\\敏感性分析\\3流量\\{ppp}\\{ppp} sumo结果v{kkk}.xlsx")
    hhh.to_excel(f"C:\\Users\\User\\Desktop\\实验\\敏感性分析\\3流量\\{ppp}\\{ppp} sumo结果h{kkk}.xlsx")
    acceleration.to_excel(f"C:\\Users\\User\\Desktop\\实验\\敏感性分析\\3流量\\{ppp}\\{ppp} sumo结果a{kkk}.xlsx")
    traci.close()
