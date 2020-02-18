import io
import math
import os
from hp_chartproperties import Default_Charts
METER_TO_FT = 3.28084  # 1meter = 3.28084ft
#############################
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.gridspec import GridSpec
import matplotlib.animation
#import matplotlib.artist.Artist
from matplotlib.patches import Wedge
import numpy as np
import PIL.Image

from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
styles = getSampleStyleSheet()
############################
def myFirstPage(canvas, doc):
    canvas.saveState()
    canvas.restoreState()

def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.restoreState()

def addPageNumber(canvas, pdf):
    page_num = canvas.getPageNumber()
    text1 = "Page %s" % page_num
    print(text1)
    canvas.drawRightString(375, 10, text1)
##############################################
header_style = ParagraphStyle(  #for header string
                                name='Title',
                                fontName='Times-Roman',
                                fontSize=24,
                                alignment = 1,
                                )
logo = Image("logo.jpg", 
             width=180.0, 
             height=30, 
             kind='direct', 
             mask="auto", 
             lazy=1)
logo.hAlign = 'RIGHT'
#####################################################################################
class DrawCharts(object):
    #------------------------------------------------------------------------ 
    def __init__(self, chart_view, include_page_for_printing):
        self.FIG_WIDTH  = 9.0 #INCHES <- this is final(9,6.5)
        self.FIG_HEIGHT = 6.5
        print("ENTERED DRAWCHARTS INIT CLASS\n")
        self.chart_view = chart_view
        self.include_page_for_printing = include_page_for_printing 
        self.charts = self.initCharts() #initialize an array of the standard charts
        self.use_mp_callout = True
        self.x_limit = self.chart_view.ask_mile
        self.emergency_number = "Harsh Patel"+"\n"+"508-838-9447"
        self.getChartReport()
    
    def imscatter(self, x, y, image, ax=None, zoom=1):#add image to the plot - NOT IN USE
        im = OffsetImage(image, zoom=zoom)
        x, y = np.atleast_1d(x, y)
        artists = []
        for x0, y0 in zip(x, y):
            ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
            artists.append(ax.add_artist(ab))
            ax.update_datalim(np.column_stack([x, y]))
            ax.autoscale()
        return
    def _axhline(self, y, xmin=None, xmax=None, color=None, linewidth=None):
        plt.axhline(y, xmin=xmin, xmax=xmax, color='k', linewidth=linewidth)
        return
    def _text(self, x, y, string, fontsize=None, fontweight=None, 
              horizontalalignment=None, verticalalignment=None):
        plt.text(x, y, string, fontsize=7, fontweight=None,#'bold', 
                 horizontalalignment='center', verticalalignment='bottom')
        return
    def mptext(self, x, top, MP, fontsize=None, fontweight=None,
               horizontalalignment=None, verticalalignment=None):
        plt.text(x, top , MP, fontsize=8, fontweight='bold',
                 horizontalalignment='center', verticalalignment='bottom',
                 bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=0.1'))
        return
    def drawfeatures(self, ax, a, xstart, xend, filter_x, filter_y):
        p = True
        filter_x.append(0)
        for index, value in enumerate(filter_x):
            if index == len(filter_x)-1:
                break
            if p:
                if filter_x[index+1]-value < 0.1:
                    p = False
                if xstart <= value <= xend:
                    ax.annotate(filter_y[index], xy=(value,0.5), fontsize=7, fontweight='bold')
                    ax.errorbar(filter_x[index]-0.02, y=0.5, yerr=0.25, color='k', elinewidth=0.5)
            elif not(p):
                if filter_x[index+1]-value < 0.1:
                    p = True
                if xstart <= value <= xend:
                    ax.annotate(filter_y[index], xy=(value,0.3), fontsize=7, fontweight='bold')
                    ax.errorbar(filter_x[index]-0.02, y=0.5, yerr=0.25, color='k', elinewidth=0.5)
            else:
                p = True
        return
    def _errorbar(self, ax, x, y=None, yerr=None, color=None, elinewidth=None):
        ax.errorbar(x+0.01, y=0.50, yerr=0.0125, color='k', elinewidth=0.5)
        return
    def _annotate(self, ax, string, xytext, xy, angle, arrowprops=None):
        ax.annotate(string, xytext, xy, arrowprops=dict(arrowstyle="-", linewidth=0.6,
                                                   connectionstyle="angle,angleA="+str(angle)+",rad=0.5"))
        return
    #------------------------------------------------------------------------    
    def getChartPage(self, charts_sub_ar, xstart, xend, mps_on_chart):
        print("ENTERED GETCHARTPAGE ONE")
        fig = plt.figure(figsize=(self.FIG_WIDTH,self.FIG_HEIGHT))
        gs = GridSpec(14, 14, figure=fig)
        
        def get_data_for_range(chart_data, xstart, xend):
            x_data = chart_data['x']
            y_data = chart_data['y']
            filter_x, filter_y = [] , []
            print("inside get_data_for_range")
            """
            Maybe if I can just read between xstart and xend.
            """
            filter_x = x_data
            filter_y = y_data
            print(len(filter_x), len(filter_y))
            return filter_x, filter_y
        
        self.page_one_charts, self.page_two_charts = [] , []
        for number, c_name in enumerate(charts_sub_ar):
            if number < 3:
                self.page_one_charts.append(c_name)
            else:
                self.page_two_charts.append(c_name)

#############################################################################################
        for a,chart_name in enumerate(self.page_one_charts):
            print(a,chart_name)
            for prop_obj in self.charts: # 'name' is chart's name
                if prop_obj['name'] == chart_name:
                    chart = prop_obj
                    break
                
            filter_x, filter_y = get_data_for_range(chart['data'], xstart, xend)
            #############################################################
            if a==0:
                ax = fig.add_subplot(gs[0:2, :])
            elif a==1:
                ax = fig.add_subplot(gs[2:12, :])
            elif a==2:
                ax = fig.add_subplot(gs[12:14, :])
            
            ax.set_ylabel(chart['name']+"\n",#+"\n"+"["+chart['units']+"]",
                            horizontalalignment = 'left',
                            verticalalignment='center',
                            rotation = 0,
                            fontweight='bold',
                            fontsize=8)
            ax.get_yaxis().set_label_coords(1.009,0.5)
            #############################################################
            def drawplan(description, odometer, valued, xstart, xend):
                description.append(0)
                description.append(0)
                plans = ["farm-crossing", "switch-point", #"whistle-post-sign" 
                         "yard-limit-sign", "station", "pedestrian-crossing"]
                         #"tunnel-start", "tunnel-end", "road-crossing-start", "road-crossing-end",
                         #"bridge-start", "bridge-end", "overpass-start", "overpass-end"]
                
                updated_odometer, updated_value = [], []
                for index,value in enumerate(description):
                    if index == len(description)-2:
                        break
                    if value == 'tunnel-start':
                        if description[index+1] or description[index+2] == 'tunnel-end':
                            if xstart <= odometer[index] <= xend:
                                updated_odometer.append(odometer[index])
                                updated_value.append("Tunnel")
                    elif value == 'road-crossing-start':
                        if description[index+1] or description[index+2] == 'road-crossing-end':
                            if xstart <= odometer[index] <= xend:
                                updated_odometer.append(odometer[index])
                                updated_value.append("Road Crossing")
                                #image_path = PIL.Image.open("crossing.png")
                                #self.imscatter(odometer[index], 0.5, image_path, zoom=0.01, ax=ax)
                    elif value == 'bridge-start':
                        if description[index+1] or description[index+2] == 'bridge-end':
                            if xstart <= odometer[index] <= xend:
                                updated_odometer.append(odometer[index])
                                updated_value.append("Bridge")
                    elif value == 'overpass-start':
                        if description[index+1] or description[index+2] == 'overpass-end':
                            if xstart <= odometer[index] <= xend:
                                updated_odometer.append(odometer[index])
                                updated_value.append("Overpass")
                    elif value == 'switch-point-facing-left':
                        if xstart <= odometer[index] <= xend:
                            updated_odometer.append(odometer[index])
                            updated_value.append("Switch Point")
                            self._annotate(ax, "", (odometer[index]+0.08, 0.525), (odometer[index], 0.5), 30)
                    elif value == 'switch-point-facing-right':
                        if xstart <= odometer[index] <= xend:
                            updated_odometer.append(odometer[index])
                            updated_value.append("Switch Point")
                            self._annotate(ax, "", (odometer[index]+0.08, 0.475), (odometer[index], 0.5), 330)
                    elif value == 'switch-point-trailing-left':
                        if xstart <= odometer[index] <= xend:
                            updated_odometer.append(odometer[index])
                            updated_value.append("Switch Point")
                            self._annotate(ax, "", (odometer[index]-0.08, 0.525), (odometer[index],0.5), -30)
                    elif value == 'switch-point-trailing-right':
                        if xstart <= odometer[index] <= xend:
                            updated_odometer.append(odometer[index])
                            updated_value.append("Switch Point")
                            self._annotate(ax, "", (odometer[index]-0.08, 0.475), (odometer[index],0.5), 210)
                    elif value == 'note':
                        if xstart <= odometer[index] <= xend:
                            updated_odometer.append(odometer[index])
                            updated_value.append(valued[index])
                    elif (value in plans):
                        if xstart <= odometer[index] <= xend:
                            updated_odometer.append(odometer[index])
                            updated_value.append(value)
                print_top = True
                for index1, value1 in enumerate(updated_odometer):
                    if print_top:
                        print_top = False
                        if xstart <= value1 <= xend:
                            plt.text(value1+0.01, 0.6, "MP "+"{:.2f}".format(value1)+" "+str(updated_value[index1]),
                                        fontsize=6.25, rotation=90, horizontalalignment='center', verticalalignment='bottom')
                            if updated_value[index1] != 'Switch Point':
                                self._errorbar(ax, value1-0.0225)
                    elif not(print_top):
                        print_top = True
                        if xstart <= value1 <= xend:
                            plt.text(value1+0.01, 0.4, str(updated_value[index1])+" "+"MP "+"{:.2f}".format(value1),
                                     fontsize=6.25, rotation=90, horizontalalignment='center', verticalalignment='top')
                            if updated_value[index1] != 'Switch Point':
                                self._errorbar(ax, value1-0.0225)
                    else:
                        print_top = True
                return
#---------------------------------------------------------------------------------------#
            if chart_name == 'Alignment': #Curve, degree of curvature
                #if len(filter_x) == len(filter_y):
                #    print("ploting")
                #    ax.plot(filter_x, filter_y, color='k', linewidth=0.75)
                ax.set_ylim([-1,1])
                self._axhline(y=0, xmin=0, xmax=1,linewidth=0.6)               
                c_list = []
                tsc_obj = {'start':'None',
                            'end':'None',
                            'type':'None'}
                for index1,value1 in enumerate(filter_y):
                    if tsc_obj['type'] == 'None' and index1==0:
                        tsc_obj['type'] = value1
                        tsc_obj['start'] = filter_x[index1]
                    if tsc_obj['type'] != value1:
                        tsc_obj['end'] = filter_x[index1]
                        c_list.append(tsc_obj)
                        if index1 == len(filter_y)-1:
                            tsc_obj['end'] = filter_x[index1]
                            c_list.append(tsc_obj)
                        tsc_obj = {'start':'None',
                                   'end':'None',
                                   'type':'None'}
                        tsc_obj['type'] = value1
                        tsc_obj['start'] = filter_x[index1]
                    if tsc_obj['type'] == value1:
                        if index1 == len(filter_y)-1:
                            tsc_obj['end'] = filter_x[index1]
                            c_list.append(tsc_obj)
                print_top = True
                for index2, value2 in enumerate(c_list):
                    if value2['type'] == 'C':
                        difference = value2['end'] - value2['start']
                        avg_point = difference/2
                        middle_point = value2['start'] + avg_point
                        if print_top:
                            if xstart <= middle_point <= xend:
                                print_top = False
                                self._text(middle_point, avg_point, "{:.2f}".format(avg_point)+"'")
                                e1 = Wedge((middle_point,0), r=avg_point, theta1=0, theta2=180, fc='w', ec='k')
                                ax.add_artist(e1)
                        elif not(print_top):
                            if xstart <= middle_point <= xend:
                                print_top = True
                                ax.text(middle_point, 0-(avg_point), "{:.2f}".format(avg_point)+"'", fontsize=7,
                                           horizontalalignment='center', verticalalignment='top')
                                e2 = Wedge((middle_point,0), r=avg_point, theta1=180, theta2=0, fc='w', ec='k')
                                ax.add_artist(e2)
                """
                -> Current alignment data is fetched from track_feature -> TSC
                -> IN future, we will filter the TSC data then it wont plot a curve 
                    less than 0.25. 
                """
                pg_mp = xstart
                t_mp = xend
                j = 1
                top = ax.get_ylim()[1]
                self.mptext(xstart, top, pg_mp)
                while pg_mp < t_mp:
                    self.mptext(xstart+j, top, pg_mp+1)
                    j += 1
                    pg_mp += 1
#---------------------------------------------------------------------------------------#
            if chart_name == 'Plan':
                #ax.set_facecolor('#E5E4E2')
                ax.set_ylim([0,1])
                ax.set_xlim([xstart,xend])
                self._axhline(y=0.5, xmin=0, xmax=1, linewidth=0.7)
                #self._axhline(y=0.48, xmin=0, xmax=1, linewidth=0.7)
                drawplan(self.chart_view.description, self.chart_view.odometer, self.chart_view.value,
                         xstart, xend)
#---------------------------------------------------------------------------------------#
            if chart_name == 'Grade': #profile, Height above the sea level
                if len(filter_x) == len(filter_y):
                    print("ploting")
                    ax.plot(filter_x, filter_y, color='k', linewidth=0.75)
                mile_y_list = []
                start_mp = xstart
                end_mp = xend
                while start_mp < end_mp:
                    for index3, value3 in enumerate(filter_y):
                        if start_mp <= filter_x[index3] <= start_mp+1:
                            mile_y_list.append(value3)
                    if len(mile_y_list) != 0:
                        first_index = mile_y_list.index(min(mile_y_list))
                        second_index = mile_y_list.index(max(mile_y_list))
                        min_first_mile = min(mile_y_list)
                        max_first_mile = max(mile_y_list)
                        angle = math.degrees(math.atan((max_first_mile - min_first_mile)/len(mile_y_list)))
                        print("min Index:",first_index, "max Index:",second_index, 
                              "min:", "{:.3f}".format(min_first_mile), "max:","{:.3f}".format(max_first_mile), 
                              "length:",len(mile_y_list), "angle:","{:.3f}".format(angle))
                        if first_index < second_index:
                            self._text(start_mp+0.5, max_first_mile, "{:.2f}".format(angle/100))
                        else:
                            self._text(start_mp+0.5, max_first_mile, "- "+"{:.2f}".format(angle/100))
                    mile_y_list.clear()
                    start_mp += 1
                #-- Minor Ticks on top of the plot --#
                ax.minorticks_on()
                ax.tick_params(axis='x', which='minor', direction='in',
                               top=False, bottom=True, length=3)
#---------------------------HIDE CERTAIN THINGS------------------------------------------#
            ax.grid(color='k', linestyle='-', axis='x', linewidth=0.25)#axis X
            ax.grid(True)
            ax.axes.get_yaxis().set_ticks([])
            plt.xlim(xstart, xend)
            print(xstart,xend,"start and end of xaxis start and end\n\n")
            ax.set_xticklabels([])
            if chart_name == 'Plan' or chart_name == 'Alignment':
                ax.spines['top'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
            if chart_name == 'Grade':
                ax.spines['top'].set_visible(False)
#############################################################################################
        plt.subplots_adjust()
        plt.subplots_adjust(hspace = 0.001)
        
        imgdata = io.BytesIO()
        fig.savefig(imgdata,format='PNG', bbox_inches='tight')
        imgdata.seek(0)
        plt.close('all')
        return imgdata
    
    
#--------------------------------------------------------------------------------------------#
        
    
    def getChartPage2(self, charts_sub_ar, xstart, xend, mps_on_chart):
        print("ENTERED GETCHARTPAGE TWO")
        fig = plt.figure(figsize=(self.FIG_WIDTH,self.FIG_HEIGHT))
        gs = GridSpec(6, 6, figure=fig)
        
        def get_data_for_range(chart_data, xstart, xend):
            x_data = chart_data['x']
            y_data = chart_data['y']
            filter_x, filter_y = [] , []
            print("inside get_data_for_range")
            """
            Maybe if I can just read between xstart and xend.
            """
            filter_x = x_data
            filter_y = y_data
            print(len(filter_x), len(filter_y))
            return filter_x, filter_y
        
#############################################################################################
        for a,chart_name in enumerate(self.page_two_charts):
            print(a,chart_name)
            for prop_obj in self.charts: # 'name' is chart's name
                if prop_obj['name'] == chart_name:
                    chart = prop_obj
                    break
                
            filter_x, filter_y = get_data_for_range(chart['data'], xstart, xend)
            #############################################################
            if a==0:
                ax = fig.add_subplot(gs[0:1, :])
            elif a==1:
                ax = fig.add_subplot(gs[1:2, :])
            elif a==2:
                ax = fig.add_subplot(gs[2:3, :])
            elif a==3:
                ax = fig.add_subplot(gs[3:4, :])
            elif a==4:
                ax = fig.add_subplot(gs[4:5, :])
            elif a==5:
                ax = fig.add_subplot(gs[5:6, :])
            
            ax.set_ylabel(chart['name']+"\n",#+"\n"+"["+chart['units']+"]",
                            horizontalalignment = 'left',
                            verticalalignment='center',
                            rotation = 0,
                            fontweight='bold',
                            fontsize=8)
            ax.get_yaxis().set_label_coords(1.009,0.5)
#---------------------------------------------------------------------------------------#
            if chart_name == 'Speed':
                ax.set_ylim([0,1])
                pg_mp = xstart
                t_mp = xend
                j = 1
                top = ax.get_ylim()[1]
                self.mptext(xstart, top, pg_mp)
                while pg_mp < t_mp:
                    self.mptext(xstart+j, top, pg_mp+1)
                    j += 1
                    pg_mp += 1
#---------------------------------------------------------------------------------------#
            if (chart_name == 'Speed' or chart_name == 'Main Track'+'\n'+'Authority' or 
                chart_name == 'Rail' or chart_name == 'Crossties' or chart_name == 'Surface'):
                ax.set_ylim([0,1])
                self._axhline(y=0.5, xmin=0, xmax=1,linewidth=0.4)
                self.drawfeatures(ax, a, xstart, xend, filter_x, filter_y)
#---------------------------------------------------------------------------------------#
            if chart_name == 'Emergency'+'\n'+'Contact':
                ax.set_facecolor('#FFD700')
                self._axhline(y=0.4, xmin=0, xmax=1,linewidth=0.4)
                plt.text(xstart+1, 0.4, self.emergency_number, fontsize=7, fontweight='bold', 
                                       horizontalalignment='center', verticalalignment='bottom')
                plt.text(xend-1, 0.4, self.emergency_number, fontsize=7, fontweight='bold', 
                                       horizontalalignment='center', verticalalignment='bottom')
                #-- Minor Ticks on top of the plot --#
                ax.minorticks_on()
                ax.tick_params(axis='x', which='minor', direction='in',
                               top=False, bottom=True, length=3)
#---------------------------HIDE CERTAIN THINGS------------------------------------------#
            ax.grid(color='k', linestyle='-', axis='x', linewidth=0.25)#axis X
            ax.grid(True)
            ax.axes.get_yaxis().set_ticks([])
            plt.xlim(xstart, xend)
            print(xstart,xend,"start and end of xaxis start and end\n\n")
            ax.set_xticklabels([])
            if (chart_name == 'Rail' or chart_name == 'Crossties' or chart_name == 'Speed' or
                chart_name == 'Surface' or chart_name == 'Main Track'+'\n'+'Authority'):
                ax.spines['top'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
            if chart_name == 'Emergency'+'\n'+'Contact':
                ax.spines['top'].set_visible(False)
#############################################################################################
        plt.subplots_adjust()
        plt.subplots_adjust(hspace = 0.001)
        
        imgdata = io.BytesIO()
        fig.savefig(imgdata,format='PNG', bbox_inches='tight')
        imgdata.seek(0)
        plt.close('all')
        return imgdata
    
    #------------------------------------------------------------------------ 
    def getChartReport(self):
        #Get a full report of charts with all pages and save to a folder.
        print("\nInside getChartReport")
        self.getDataFromDB()
        print("Returning from datafromDB")
        max_charts_per_page = 9
        chart_groups = self.get_chart_groups(max_charts_per_page)
        mile_posts=self.chart_view.mp
        if self.use_mp_callout:
            print("Leaving getChartReport\n")
            self.getChartGroupReportHelper(chart_groups,mile_posts)
            
    #------------------------------------------------------------------------ 
    def getChartGroupReportHelper(self,chart_groups,mile_posts):
        pages_per_group = int(math.ceil((self.chart_view.last_mp-self.chart_view.first_mp)/self.x_limit))
        print("Entering getChartGroupReportHelper")
        for page_name,single_page_of_charts in chart_groups.items():
            print(page_name,"\n") #graph only page with names geometry                
            self.pdf = SimpleDocTemplate("document.pdf", pagesize=landscape(letter), 
                                         topMargin=2, bottomMargin=2, rightMargin=2, leftMargin=1)
            print(landscape(letter))
            cwd = os.getcwd()
            chart_folder_path = cwd
            print(chart_folder_path)
            self.getChartReportUsingOdometerDistance(single_page_of_charts,
                                                     chart_folder_path,mile_posts,pages_per_group)
            print("\nafter coming back from get chartreportusing odometer\n")
            print (self.pdf)
            
    #------------------------------------------------------------------------ 
    def getChartReportUsingOdometerDistance(self,single_page_of_charts,
                            chart_folder_path,mile_posts,pages_per_group):
        #save each new page to that chart group folder
        print("Inside getchartreportusing using odometer distance")
        self.Story = []
        for odo,value in enumerate(mile_posts):
            if odo == len(mile_posts)-1:
                break
            self.start = value
            self.end = value+self.chart_view.ask_mile
            if odo % self.chart_view.ask_mile == 0:
                print("     ---------->",pages_per_group,self.start,self.end,mile_posts, "<----------" ,"\n")
                fig = self.getChartPage(single_page_of_charts, self.start, self.end, mile_posts)
                fig2 = self.getChartPage2(single_page_of_charts, self.start, self.end, mile_posts)
                
                line1 = self.chart_view.group_name
                #----------- PAGE 1 --------------#
                self.Story.append(Paragraph(line1, header_style))
                self.Story.append(logo)
                self.Story.append(Spacer(inch, 0.1*inch))
                pi = Image(fig)
                self.Story.append(KeepTogether(pi))
                #----------- PAGE 2 --------------#
                self.Story.append(Paragraph(line1, header_style))
                self.Story.append(logo)
                self.Story.append(Spacer(inch, 0.1*inch))
                pi2 = Image(fig2)
                self.Story.append(KeepTogether(pi2))
                self.Story.append(PageBreak())
                
        self.pdf.build(self.Story, onFirstPage=addPageNumber, onLaterPages=addPageNumber)
        
    #------------------------------------------------------------------------ 
    def getDataFromDB(self):
        # This will assign x,y data to each line in the array of charts,
        print("\nENTERED GETDATAFROMDB")
        for line in self.charts:#line is deafult chart list
            line['data'] = self.chart_view.list_chart_helper(line['feature'],line['attribute'])

    #------------------------------------------------------------------------ 
    def get_chart_groups(self, max_charts_per_page):
        chart_groups = {} # {'page_name': 'single_page_of_charts'([])} 
        for prop_obj in self.charts: # 'name' is chart's name
            if prop_obj['page_name'] not in chart_groups:
                chart_groups[prop_obj['page_name']] = [prop_obj['name']]
            else: # exists
                chart_groups[prop_obj['page_name']].append(prop_obj['name'])
        return chart_groups
    
    #------------------------------------------------------------------------ 
    def initCharts(self):
        # page_name are : 'Geometry'
        print("ENTERED initCharts") 
        charts_for_printing = []
        for chart_obj in Default_Charts:
            charts_for_printing.append(chart_obj)
        print (charts_for_printing)
        print("LEFT INITCHARTS FUNC\n")
        return charts_for_printing
