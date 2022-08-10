# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 20:18:59 2022
@author: Administrator
"""
import pandas as pd
import gurobipy as gb
from gurobipy import *
import numpy as np
import math
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import logging 

# DATE TIME USE FOR PRIORITY CALCULATION
import datetime

# DISTANCE CALCULATION USING LATITUDE AND LONGTITUDE
def deg2rad(deg):
  return deg * (math.pi/180)

def getDistanceFromLatLonInKm(lat1,lon1,lat2,lon2):
  # Radius of the earth in km
  R = 6371; 
  dLat = deg2rad(lat2-lat1)
  dLon = deg2rad(lon2-lon1)
  a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  # Distance in km
  d = R * c; 
  return d

#DISTANCE MATRIX
def readKeyInfo(filePath):
    distance_list = []
    actualduration_list = []
    dateDifferences_list = []
    customerPriority_list = []
    locationIndices_list = []
    
    # WE MAY UPDATE RUNNING DATE TO DIFFERENT DATES ONCE WE IMPLEMENT LOOP FOR THE WHOLE YEAR
    # REQUEST START DATE IS 10/6/2020. THUS, WE START FROM 10/8/2020
    # todayStr= "2020-10-6"
    todayStr= "2020-10-06"
    today = datetime.datetime.strptime(todayStr, '%Y-%m-%d')
    
    terminateDateStr = "2021-11-01"
    terminateDate = datetime.datetime.strptime(terminateDateStr, '%Y-%m-%d')
    
    #filepath =  r"C:\Users\Administrator\Downloads\Master Data.csv"
    data = pd.read_csv(filepath, encoding = "ISO-8859-1")
    # data = data.sort_values(by="CreatedDate", ascending = True)
    temp_data = data
    temp_data = temp_data.iloc[0:0]
    
    for index, row in data.iterrows():
        tempCreateDate_str = row["CreatedDate"]
        tempCreateDate_str = tempCreateDate_str.replace("/","-")
        tempCreateDate = datetime.datetime.strptime(tempCreateDate_str, '%Y-%m-%d')
        #print("Create Date: " + str(tempCreateDate))
        if (today >= tempCreateDate):
            temp_data = temp_data.append(row)
            # temp_data = pd.concat(temp_data, row, axis=0, join="outer")
        else:
            #print('today',today)
            temp_data['geocode_lat'] = temp_data['geocode_lat'].astype(float)
            temp_data['geocode_long'] = temp_data['geocode_long'].astype(float)

            # NUMBER OF RECORDS NEED TO BE UPDATED BASED ON HOW MANY ROWS WE HAVE
            actualduration = np.array(temp_data['ActualDurationMin'])
            actualduration = np.nan_to_num(actualduration)
            actualduration_list.append(actualduration)

            createDate = np.array(temp_data['CreatedDate'])
            dateDifferences = []
            dateDifferences.append(0)
            
            for i in range(len(createDate)):
                dateStr = createDate[i]
                dateStr = dateStr.replace("/","-")
                date_time_obj = datetime.datetime.strptime(dateStr, '%Y-%m-%d')
                createDate[i] = date_time_obj
                difference_in_days = today - date_time_obj
                dateDifferences.append(difference_in_days.days)
            dateDifferences_list.append(dateDifferences)
            
            customerPriorityList = []
            customerPriorityList.append("0")
            customerPriority = np.array(temp_data['customer_priority'])
            for i in range(len(customerPriority)):
                priorityStr = customerPriority[i]
                if (priorityStr == "PREFERRED"):
                    customerPriority[i] = "5"
                    customerPriorityList.append("5");
                elif (priorityStr == "NONPREFERRED"):
                    customerPriority[i] = "1"
                    customerPriorityList.append("1")
                else:
                    customerPriorityList.append(customerPriority[i])
            customerPriority_list.append(customerPriorityList)
            
            #Start from a depot location
            startLocation = [32.737261, -117.1311481]
            tickets_loc = []
            tickets_loc.append([startLocation[0], startLocation[1]])
            for index, row in temp_data.iterrows():
              tickets_loc.append([temp_data['geocode_lat'][index], temp_data['geocode_long'][index]])
            # TOTAL AMOUNT OF TICKET PLACES
            total_requests = len(tickets_loc)
            #print(total_requests)
            
            # stop = False
            # INITIALIZE DISTANCE NUMPY ARRAY - WITH DIMENSION N X N
            distance_array = np.zeros((total_requests,total_requests))
            count = 0
            # distance_array = np.empty([10, 10], dtype="S10")
            for i in range(total_requests):
              for j in range(total_requests):
                if i == j:
                  distance_array[i][j] = 0
                else:
                  loc_src = tickets_loc[i]
                  loc_src_lat = loc_src[0]
                  loc_src_long = loc_src[1]
                  loc_dest = tickets_loc[j]
                  loc_dest_lat = loc_dest[0]
                  loc_dest_long = loc_dest[1]
                  distance = getDistanceFromLatLonInKm(loc_src_lat,loc_src_long,loc_dest_lat,loc_dest_long)
                  distance_array[i][j] = round(float(distance), 2)
                count += 1
            distance_list.append(distance_array)
            locationIndices = []
            for i in range(len(distance_array) - 1):
                locationIndices.append(i+1)
            locationIndices_list.append(locationIndices)        
            print("Date Range: " + str(today) + " - " + str(today + datetime.timedelta(days = 1)))
            if (today > terminateDate):
                print(locationIndices_list)
                return [distance_list, actualduration_list, dateDifferences_list, customerPriority_list, locationIndices_list]
            while (today < tempCreateDate):
                today = today + datetime.timedelta(days = 1)
                if (today < tempCreateDate):
                    distance_list.append([])
                    actualduration_list.append([])
                    dateDifferences_list.append([])
                    customerPriority_list.append([])
                    locationIndices_list.append([])
            temp_data = temp_data.iloc[0:0]
            if (today == tempCreateDate):
                temp_data = temp_data.append(row)

    print(locationIndices_list)
            #print('distance array', distance_array)
    return [distance_list, actualduration_list, dateDifferences_list, customerPriority_list, locationIndices_list]

summary_total_employees = []
summary_finished_requests = []
summary_unfinished_requests = []
summary_caseAges = []
summary_travelDistance = []
summary_tech_untilization = []
summary_infeasibleCount = 0
summary_feasibleCount = 0

# logging
LOG_FILE = r"C:\Users\Administrator\Downloads\report.txt"
file = open(LOG_FILE,"a")

count = 0
# VARIABLE SETUP
filepath =  r"C:\Users\Administrator\Downloads\master_data_sandiego.csv"
dist_list, actualDurationArray_list, requestAge_list, customerPriority_list, cycle_requests_list = readKeyInfo(filepath)

todayStr= "2020-10-6"
today = datetime.datetime.strptime(todayStr, '%Y-%m-%d')
while count < len(dist_list):
    model = gb.Model('Tasks Distribution Model')
    # SET EACH OPTIMIZATION TIME LIMITS - 3 MINUTES PER OPTIMIZATION
    model.setParam('TimeLimit', 3 * 60)
    dist = dist_list[count]
    actualDurationArray = actualDurationArray_list[count]
    requestAge = requestAge_list[count]
    customerPriority = customerPriority_list[count]
    cycle_requests = cycle_requests_list[count]
    # print(dist)
    # NO REQUESTS WITHIN THIS TIME FRAME
    if (len(cycle_requests) == 0):
        file.write("\n")
        file.write("-----------------Summary CYCLE " + str(count) + "-----------------")
        file.write("\n")
        file.write("Date: " + str(today))
        file.write("\n")
        file.write("NO Requests in Cycle: " + str(count + 1))
        file.write("\n")
        count += 1
        today = today + datetime.timedelta(days = 1)
        continue

    # print(actualDurationArray)
    # print(requestAge)
    # print(customerPriority)
    # print(cycle_requests)

    total_employees = 0
    finished_requests = []
    unfinished_requests = []
    caseAges = []
    travelDistance = []
    # print("Headers: " + str(dist))
    # print(customerPriority)
    n = len(dist) - 1 #NUMBER OF REQUEST LOCATIONS
    dist = np.array(dist)
    distCoefficient = np.amax(dist) / 5
    
    #print(len(dist))
    N = [i for i in range (1, (n+1))] # SET OF REQUEST LOCATIONS
    #print(N)
    V = [0] + N # SET OF REQUEST LOCATIONS (LOCATIONS + ER LOCATION)
    #print(V)
    A = [(i, j) for i in V for j in V if i != j] # POTENTIAL PATHS
    time_perkm = 1 # VIEHCLE AVERAGE SPEED KM/MINUTE
    daily_min_limit = 10 * 60 # MAX DAILY TIME LIMIT FOR EACH EMPLOYEE
    t_actual_Duration_time = list(actualDurationArray)
    #print(t_actual_Duration_time)
    t_actual_duration_time = dict(zip(N, t_actual_Duration_time)) # LIST OF (Location, ActualDurationMin at this location)
    
    #print(t_actual_duration_time)
    
    # MODEL SETUP
    # x - WHETHER EMPLOYEE PICKED THE PATH FROM I TO J LOCATION
    x = model.addVars(A, vtype=GRB.BINARY, name=['x_'+str(i)+'_'+str(j) for i in V for j in V if i != j])
    #print(len(x))
    #print(x)
    
    # U2 - TOTAL TIME TRAVELED FROM REQUEST LOCATION TO REQUEST LOCATION
    u2 = model.addVars(N, vtype=GRB.CONTINUOUS, name=["Dummy_Time_U2_"+ str(i) for i in N])
    #print(len(u2))
    
    # U3 - TIME TRAVELED FROM THE DEPOT LOCATION TO 1ST REQUEST LOCATION
    u3 = model.addVars(N, vtype=GRB.CONTINUOUS, name=["Dummy_Time_U3_"+ str(i) for i in N])
    
    # U4 - TIME TRAVELED FROM LAST REQUEST LOCATION TO THE DEPOT LOCATION
    u4 = model.addVars(N, vtype=GRB.CONTINUOUS, name=["Dummy_Time_U4_"+ str(i) for i in N])
    
    # Objective 1 (taking customer priority into accounts)
    # model.setObjective(sum(x[i, j]*dist[i, j] for i, j in A) + sum(int(float(customerPriority[i])) * distCoefficient for i in range(len(V))), GRB.MINIMIZE)   # Minimize Distance  
    # Objective 2, just the distance alone, without considering customer priority. 
    model.setObjective(sum(x[i, j]*dist[i, j] for i, j in A))
                       
    # CONSTRAINTS
    # EMPLOYEE HAS TO ENTER EACH REQUEST LOCATION ONCE
    for j in N:
        model.addConstr(sum(x[i,j] for i in V if i!=j) == 1)
    # EMPLOYEE HAS TO EXIT FROM EACH REQUEST LOCATION ONCE
    for i in N:
        model.addConstr(sum(x[i,j] for j in V if j!=i) == 1)
    
    # U2 TIME TRAVELED AMONG REQUEST LOCATIONS UPDATE
    for i, j in A:
        if i != 0 and j != 0:
            model.addConstr((x[i, j] == 1) >> (u2[i]+t_actual_duration_time[j]+(dist[i,j]*time_perkm) == u2[j]))
    
    # U3 TIME TAKEN FROM ER LOCATION TO 1ST REQUEST LOCATION
    for i, j in A:
        if i==0 and j!=0:
            model.addConstr((x[i, j] == 1) >> (dist[0,j]*time_perkm == u3[j]))
            
    # U4 TIME TAKEN FROM LAST REQUEST LOCATION TO ER LOCATION
    for i, j in A:
        if j==0 and i!=0:
            model.addConstr((x[i, j] == 1) >> (dist[0,i]*time_perkm == u4[i]))
       
    # EMPLOYEE current time spent is greater than or equal to TIME SPENT AT EACH REQUEST LOCATION
    # EMPLOYEE TOTAL HOURS SPEND HAS TO BE SMALLER THAN TIME LIMIT - 8 HOURS IN OUR EXAMPLE
    for i in N:
        model.addConstr(u2[i] >= t_actual_duration_time[i])  
        model.addConstr(u2[i]+u3[i]+u4[i] <= daily_min_limit)   
    
    try:
        print("Start Optimization - " + str(count + 1))
        model.optimize()
    
        print("Minimized distance:", round(model.objVal,2))
        print("\nRequired Technician Number and Each Technician's Path:")
        l1=[]
        l2=[]
        
        
        for v in model.getVars():
            if round(v.x,0) == 1:
                l1.append(int(v.varName.split('_')[1]))
                l2.append(int(v.varName.split('_')[2]))
        
        df = pd.DataFrame(list(zip(l1, l2)), columns =['Point1', 'Point2'])
        
        master_list = []
        print("-----------------Summary CYCLE " + str(count) + "-----------------")
        file.write("\n")
        file.write("-----------------Summary CYCLE " + str(count) + "-----------------")
        file.write("\n")
        file.write("Date: " + str(today))
        
        for i in range((list(df["Point1"]).count(0))):
            total_employees += 1
            currentEmployeeTravelDistance = 0
            seq_l=[0]
            t = df["Point2"][i]
            
            j=0
            while(j<len(df)):
                seq_l.append(t) if t not in seq_l else seq_l
                
                if t==df["Point1"][j]:
                    t = df["Point2"][j]
                    j = 0
                    if t==0:
                        break
                else:
                    j = j+1
            
            seq_l.append(0)
            master_list.append(seq_l)

            print("\nTech",i+1,"Path: ", end='')
            file.write("\nTech" + str(i+1) +" Path: ")
            file.write("\n")
            lastLocationId = 0
            
            for k in range(len(seq_l)):
                if k==len(seq_l)-1:
                    print(seq_l[k], end='')
                    file.write(str(seq_l[k]))
                    currentLocationId = seq_l[k]
                    distanceBetweenTwoLocations = dist[lastLocationId, currentLocationId]
                    currentEmployeeTravelDistance += distanceBetweenTwoLocations
                    if (int(seq_l[k]) == 0):
                        continue
                    else:
                        finished_requests.append(seq_l[k])
                elif k == 0:
                    lastLocationId = 0
                    print(seq_l[k],"-> ", end='')
                    file.write(str(seq_l[k]) + "-> ")
                    if (int(seq_l[k]) == 0):
                        continue
                    else:
                        finished_requests.append(seq_l[k])
                else:
                    print(seq_l[k],"-> ", end='')
                    file.write(str(seq_l[k]) + "-> ")
                    currentLocationId = seq_l[k]
                    distanceBetweenTwoLocations = dist[lastLocationId, currentLocationId]
                    currentEmployeeTravelDistance += distanceBetweenTwoLocations
                    lastLocationId = currentLocationId
                    if (int(seq_l[k]) == 0):
                        continue
                    else:
                        finished_requests.append(seq_l[k])
                        caseAges.append(requestAge[int(seq_l[k])])
            #KEEP 2 DECIMAL
            travelDistance.append(round(currentEmployeeTravelDistance, 2))
        
        for request_id in cycle_requests:
            if request_id not in (finished_requests):
                unfinished_requests.append(request_id)
        
        actualWorkingHours = 0
        for duration in actualDurationArray:
            actualWorkingHours += float(duration)
        dailyUtilization = round(actualWorkingHours/(10*60*total_employees), 2)
        
        print("")
        print("ID of all Requests in this cycle: " + str(cycle_requests))
        print("Requests finished in this cycle: " + str(finished_requests))
        print("Requests missed in this cycle: " + str(unfinished_requests))
        print("Number of employees needed in this cycle: " + str(total_employees))
        print("Travel Distance of employees this cycle: " + str(travelDistance))
        print("Technician Utilization (Task Time/Total Working Time): " +  str(dailyUtilization))
        #print("Request Ages for this cycle: " + str(caseAges))
        
        # WRITE INTO LOG FILE
        file.write("\n")
        file.write("ID of all Requests in this cycle: " + str(cycle_requests))
        file.write("\n")
        file.write("Requests finished in this cycle: " + str(finished_requests))
        summary_finished_requests.append(finished_requests)
        file.write("\n")
        file.write("Requests missed in this cycle: " + str(unfinished_requests))
        summary_unfinished_requests.append(summary_unfinished_requests)
        file.write("\n")
        file.write("Number of employees needed in this cycle: " + str(total_employees))
        summary_total_employees.append(total_employees)
        file.write("\n")
        file.write("Travel Distance of employees this cycle: " + str(travelDistance))
        summary_travelDistance.append(travelDistance)
        file.write("\n")
        file.write("Technician Utilization (Task Time/Total Working Time): " + str(dailyUtilization))
        summary_tech_untilization.append(str(dailyUtilization))
        file.write("\n")


        file.write("\n")
        finished_requests = []
        unfinished_requests = []
        caseAges = []
        travelDistance = []
        dailyUtilization = 0
        
        summary_feasibleCount += 1
        count += 1
        today = today + datetime.timedelta(days = 1)
    except:
        print("Met Infeasible Optimization")
        file.write("\n")
        file.write("\n")
        file.write("-----------------Summary CYCLE " + str(count) + "-----------------")
        file.write("\n")
        file.write("Date: " + str(today))
        file.write("\n")
        file.write("Met Infeasible Optimization in Cycle: " + str(count))
        file.write("\n")
        summary_infeasibleCount += 1
        count += 1
        today = today + datetime.timedelta(days = 1)


print("")
print("-----------------Summary ALL -----------------")
print("Total Employees Needed: " + str(summary_total_employees))
print("Requests finished: " + str(summary_finished_requests))
print("Requests missed: " + str(summary_unfinished_requests))
print("Travel Distance of employees this cycle: " + str(summary_travelDistance))
print("Infeasible Cycle Counts: " + str(summary_infeasibleCount))
print("Feasible Cycle Counts: " + str(summary_feasibleCount))


file.write("\n")
file.write("\n")
file.write("-----------------Summary ALL -----------------")
file.write("\n")
file.write("Total Employees Needed: " + str(summary_total_employees))
file.write("\n")
file.write("Requests finished: " + str(summary_finished_requests))
file.write("\n")
file.write("Requests missed: " + str(summary_unfinished_requests))
file.write("\n")
file.write("Travel Distance of employees this cycle: " + str(summary_travelDistance))
file.write("\n")
file.write("Infeasible Cycle Counts: " + str(summary_infeasibleCount))
file.write("\n")
file.write("Feasible Cycle Counts: " + str(summary_feasibleCount))
file.write("\n")
file.write("Technician Utilization (Task Time/Total Working Time): " + str(summary_tech_untilization))
file.write("\n")
file.close()
