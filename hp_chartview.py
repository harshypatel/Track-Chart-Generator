import csv
import math
from hp_drawchart import DrawCharts
from datetime import date

METER_TO_FT = 3.28084  # 1m = 3.28084ft
#Miles = feet * 0.00018939

class ChartView(object):
     
    def __init__(self, group_name):
        today = date.today()
        print(today)
        self.group_name = group_name
        self.ask_mile = int(input("How many Miles per page (5 Recommended): "))
    ################################################
    def generate_charts(self, include_page_for_printing):
        print("GENERATE_CHARTS\n")
        DrawCharts(self, include_page_for_printing)
    ################################################    
    def getmilepost(self, first_mp, last_mp):
        mp = []
        while first_mp <= last_mp:
            mp.append(first_mp)
            first_mp += 1
        return mp
    ################################################
    def getodometer(self, distance, feet):
        odometer , mps = [] , []
        for index, value in enumerate(feet):
                t = value*0.00018939
                odometer.append(t)
        for index1, value1 in enumerate(odometer):
            if index1 == len(odometer):
                break
            b = distance[index1]+value1
            mps.append(float(b))
        return mps
    ################################################
    def getvalues(self, description, distance, valued, namecheck):
        temp, mps, name = [] , [] , []
        for index,value in enumerate(description):
            if value == namecheck:
                temp.append(index)
        for index, value in enumerate(self.odometer):
            for index1, value1 in enumerate(temp):
                if index == value1:
                    mps.append(float(value))
                    mps.sort()
        for index, value in enumerate(valued):
            for index1, value1 in enumerate(temp):
                if index == value1:
                    name.append(value)
        return mps, name
    ################################################
    def get_downsampled(self, mylist, size):
        data_length = len(mylist)
        nth = round(data_length/ size)
        downsampled = mylist
        if nth > 1:
            downsampled = downsampled[::nth]
        return downsampled
    ################################################
    def list_chart_helper(self, feature, attribute):
        description, distance, feet, valued, tsc= [] , [] , [] , [] , []
        alignment1, degree_distance, degree_ffm = [] , [] , []
        height, geoid_height, grade = [] , [] , []
        
        print("\nENTERED LIST_CHART_HELPER")#1503 -> data <- comes from
        with open ('track_feature_data.csv', mode = 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)
            for row in reader:
                description.append(row[1])
                distance.append(float(row[2]))
                feet.append(float(row[3]))
                valued.append(row[4])
                tsc.append(row[6])
        with open ('degree_of_curvature_1503.csv', mode = 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)
            for row in reader:
                #alignment1.append(float(row[2]))
                degree_distance.append(float(row[7]))
                degree_ffm.append(float(row[8]))
        with open ('profile_grade_1503.csv', mode = 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)
            for row in reader:
                height.append(float(row[0]))
                geoid_height.append(float(row[1]))
            
        
        #new_alignment = self.get_downsampled(alignment1, 500) #234,972 -> 500
        new_degree_distance = self.get_downsampled(degree_distance, 500)#234,972 -> 500
        new_degree_ffm = self.get_downsampled(degree_ffm, 500) #234,972 -> 500
        #self.alignment_odometer = self.getodometer(new_degree_distance, new_degree_ffm)#500
        
        small_height = self.get_downsampled(height, 500)#262940 -> 500
        small_geoid_height = self.get_downsampled(geoid_height, 500) #262940 -> 500
        for index, value in enumerate(small_height):
            temp = value - small_geoid_height[index]
            grade.append(temp)
        self.grade_odometer = self.getodometer(new_degree_distance, new_degree_ffm)#500
        
        self.description = description
        self.value = valued
        self.odometer = self.getodometer(distance, feet)
        for index, value in enumerate(self.odometer):
            if index == 0:
                self.first_mp = math.floor(value)
            if index == len(self.odometer)-1:
                self.last_mp = math.ceil(value)
        
        
        self.mp = self.getmilepost(self.first_mp, self.last_mp)
        
        mta = self.getvalues(description, distance, valued, 'main-track-authority')
        self.mta , self.mtaname = mta[0] , mta[1]
        
        speed = self.getvalues(description, distance, valued, 'posted-speed')
        self.speed , self.speedvalue = speed[0] , speed[1]
        
        rail = self.getvalues(description, distance, valued, 'rail-size')
        self.rail , self.raildate = rail[0] , rail[1]
        
        crossties = self.getvalues(description, distance, valued, 'crossties')
        self.crossties , self.crosstiesdate = crossties[0] , crossties[1]
        
        surface = self.getvalues(description, distance, valued, 'surface')
        self.surface , self.surfacedate = surface[0] , surface[1]
        
        ec = self.getvalues(description, distance, valued, 'emergency-contanct')
        self.ec , self.ecname = ec[0] , ec[1]
        
        print(len(description), len(valued), len(feet), len(self.odometer), "description, valued, feet, odometer")
        print(self.mta, self.mtaname, self.speed, self.speedvalue, "mta, mtaname, speed, speedvalue\n")
        print(self.rail, self.raildate, self.crossties, self.crosstiesdate, "rail-size, raildate, crossties, crosstiesdate\n")
        print(self.surface, self.surfacedate, self.ec, self.ecname, "surface, surfacedate, ec, ecname\n")
        print("LEAVING LIST_CHART_HELPER\n")
        
        if feature == 'alignment':#degree of curvature, curves
            return {"x":self.odometer, "x_ft":[], "y":tsc}
        if feature == 'plan':
            return {"x":self.odometer, "x_ft":[], "y":self.description}
        if feature == 'profile':#grade, height above the sea level
            return {"x":self.grade_odometer, "x_ft":[], "y":grade}
        if feature == 'speed':
            return {"x":self.speed, "x_ft":[], "y":self.speedvalue}
        if feature == 'mta':
            return {"x":self.mta, "x_ft":[], "y":self.mtaname}
        if feature == 'rail':
            return {"x":self.rail, "x_ft":[], "y":self.raildate}
        if feature == 'crossties':
            return {"x":self.crossties, "x_ft":[], "y":self.crosstiesdate}
        if feature == 'surface':
            return {"x":self.surface, "x_ft":[], "y":self.surfacedate}
        if feature == 'ec':
            return {"x":self.ec, "x_ft":[], "y":self.ecname}

if __name__ == '__main__':
    chart_view = ChartView('Track Chart Sample')
    chart_view.generate_charts('geometry')
    