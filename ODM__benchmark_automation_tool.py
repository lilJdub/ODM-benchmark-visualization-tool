import os
import tkinter as tk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import Frame
from openpyxl.drawing.image import Image
from collections import defaultdict

#testing
import ttkbootstrap

class logHelperApp:
    #initialize root window
    def __init__(self,root):
        style=ttkbootstrap.Style(theme="flatly")
        TOP6=style.master

        #Placing and initiation of the objects and windows.
        self.root = root
        self.root.title("LogHelper Widget")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        #Windows
        self.viswindow=None
        self.fileWin=None
        self.typeWin=None
        
        
        self.merged_df=pd.DataFrame()
        self.totalname=""

        #Button & Frame
        # 創建上半部的框架
        top_frame = tk.Frame(self.root, bd=2, relief=tk.GROOVE)
        top_frame.pack(side="top", fill="both", expand=True)
        submitlabel=tk.Label(top_frame,text="Select Files")
        submitlabel.pack(side="top", pady=20)
        submitButton = tk.Button(top_frame,text="Select Files",command=self.create_vis_window)
        submitButton.config(padx=80,pady=40,anchor="center")
        submitButton.pack(side="top",pady=40)
        
        # 創建下半部的框架
        bottom_frame = tk.Frame(self.root, bd=2, relief=tk.GROOVE)
        bottom_frame.pack(side="top", fill="both", expand=True)
        finalizelabel=tk.Label(bottom_frame,text="final results")
        finalizelabel.pack(side="top", pady=20)
        finalizeButton = tk.Button(bottom_frame,text="final results",command=self.finalizeprocess2)
        finalizeButton.config(padx=80,pady=40,anchor="center")
        finalizeButton.pack(side="top",pady=40)

    #Visualization Windows.
    def create_vis_window(self):
        #disable interactions w/root
        self.root.attributes('-disabled', True)

        self.viswindow=tk.Toplevel(root)

        def on_close():
            # Enable interactions with the root window when the viswindow is closed
            self.root.attributes('-disabled', False)
            self.viswindow.destroy()
        
        self.viswindow.protocol("WM_DELETE_WINDOW", on_close)

        self.viswindow.title("檔案類型選擇")
        self.viswindow.geometry("400x600")
        self.viswindow.resizable(False,False)

        projectLabel = tk.Label(self.viswindow,text="Enter Project Name")
        projectLabel.pack(side="top",anchor="center",pady=10)
        self.projectName = tk.Entry(self.viswindow)
        self.projectName.pack(side="top",anchor="center",pady=10)    

        phaseLabel = tk.Label(self.viswindow,text="Enter Phase Name")
        phaseLabel.pack(side="top",anchor="center",pady=10)
        self.phase=ttk.Combobox(self.viswindow,values=["DB","SI","PV","MV"],state="readonly")
        self.phase.pack(side="top",anchor="center",pady=10)

        skuLabel = tk.Label(self.viswindow,text="Product SKU")
        skuLabel.pack(side="top",anchor="center",pady=10)
        self.prodSKU = tk.Entry(self.viswindow)
        self.prodSKU.pack(side="top",anchor="center",pady=10)

        submitbutton = tk.Button(self.viswindow,text="Select Files",command=self.categorize_files)
        submitbutton.config(padx=20, pady=20)
        submitbutton.pack(side="top",anchor="center",pady=40)

        # Set grab_set to make the viswindow modal
        self.viswindow.grab_set()
        self.viswindow.wait_window(self.viswindow)

    #Categorize/choose log file types: first loading space of dataframes.
    def categorize_files(self):
        #紀錄project name
        self.totalname=str(self.projectName.get())+"_"+str(self.phase.get())+"_"+str(self.prodSKU.get())

        #暫存
        self.dfPile={}
        checkbox_file_association = []


        #Choose files for using
        f=filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])
        #check if f is emnpty
        if len(f)<1:
            messagebox.showerror("Error", "No files selected. Please choose at least one CSV file.")
            return
    
        #視窗
        self.fileWin=tk.Toplevel(self.viswindow)
        self.fileWin.title("File Type")
        self.fileWin.withdraw()

        self.loadwin=tk.Toplevel(self.fileWin)
        self.loadwin.geometry("300x100")
        self.loadwin.title("Loading")
        load_label=tk.Label(self.loadwin,text="Loading file data, please wait.....")
        load_label.pack()
        
        #update UI
        self.fileWin.update()
        
        #each file type
        for path in f:    
            #load and save df
            df=pd.read_csv(path,skipfooter=2,engine="python")
            fn = str(os.path.basename(path)).removesuffix(".csv")
            #save dict into dictionary
            self.dfPile[fn]=df


            #Generate checkboxes and labels to each file
            label = tk.Label(self.fileWin, text=f"Choose {path} 's file type:")
            label.pack()
            self.checkbox_frame = tk.Frame(self.fileWin)
            
            fileTools=["AIDA64","Furmark", "3DMark","HWInfo64","Prime95"]
            file_checkboxes = []
            for name in fileTools:
                var=tk.IntVar()
                checkbox=tk.Checkbutton(self.checkbox_frame, text=name,variable=var)
                checkbox.var=var
                checkbox.pack(side=tk.LEFT, anchor=tk.W)
                file_checkboxes.append(checkbox)

                
                #Check boxes based on df
                if df.columns[2]=="3DMark3DMark" and name =="3DMark" :
                    checkbox.select()
                if df.columns[3]=="AIDA64AIDA64" and name =="AIDA64":
                    checkbox.select()
                if df.columns[4]=="HWINFO64HWINFO64" and name =="HWInfo64":
                    checkbox.select()
                if df.columns[5]=="FurmarkFurmark" and name =="Furmark":
                    checkbox.select()
                if df.columns[6]=="P95P95" and name =="Prime95":
                    checkbox.select()

            # Store the association between checkboxes and the current file
            checkbox_file_association.append((path, file_checkboxes))

            # Pack Checkbuttons Frame to the main frames
            self.checkbox_frame.pack()

        def run_cat_files():
            d=defaultdict(dict)
            for file_path, file_checkboxes in checkbox_file_association:
                file_name = str(os.path.basename(file_path)).removesuffix(".csv")
                for cb in file_checkboxes:
                    chkboxtext=cb.cget("text")
                    #d: filename in first layer, then a dictionary of checkbox-state in value set
                    d[file_name][chkboxtext]=cb.var.get()
            self.visualize_and_merge_files(self.dfPile,d)
            #d: 3DMark Prim95 AC': {'AIDA64': 0, 'Furmark': 1, '3DMark': 0, 'HWInfo64': 0, 'Prime95': 0}, 'AIDA64+Furmark': {'AIDA64': 0, 'Furmark': 1, '3DMark': 0, 'HWInfo64': 0, 'Prime95': 0}, 'Burnin AC balanced': {'AIDA64': 0, 'Furmark': 1, '3DMark': 0, 'HWInfo64': 0, 'Prime95': 0}, 'Furmark H_L_H AC Balanced': {'AIDA64': 0, 'Furmark': 1, '3DMark': 0, 'HWInfo64': 0, 'Prime95': 0}})
            

        #Submit button for the next step
        submit_category=tk.Button(self.fileWin, text="Submit file", command=run_cat_files)
        submit_category.pack()

        self.fileWin.deiconify()
        self.loadwin.destroy()

    #main hub for visualization and merging
    def visualize_and_merge_files(self,dfPile,d):
        self.merged_df=pd.DataFrame()
        self.charts=[]

        #all the file names
        for file_name,val in d.items():
            #The column in df (without duplicates)
            column_sets=set()
            
            #switch based on val
            for k,v in val.items():
                if v==1:
                    match k:
                        case "AIDA64":
                            column_sets.add("a64")
                            column_sets.add("a642")
                        case "Furmark":
                            column_sets.add("fm")
                            column_sets.add("fm2")
                        case "3DMark":
                            column_sets.add("3dm")
                            column_sets.add("3dm2")
                        case "HWInfo64":
                            column_sets.add("hw64")
                            column_sets.add("hw642")
                        case "Prime95":
                            column_sets.add("p95")
                            column_sets.add("p952")

            #visualize key(chart name),col_sets(the columns that needed to be visualized)
            self.visualize_merge_docs(file_name,column_sets,dfPile[file_name])

        #merge the whole chart into a single document
        self.mergecharts(self.charts)
        
        #wrap up
        csv_name=self.totalname +"_log_files.csv"
        self.merged_df.to_csv(csv_name, index=False)

        #全merged完記得清
        self.merged_df=pd.DataFrame()

        """
        the actual finishing point
        """
        self.viswindow.destroy()


    def visualize_merge_docs(self,file_name,column_sets,df):
        #Visualize docs using the columns mentioned
        #place the df's chart in this array (one dataframe at a time)
        #for each column:
        for col in column_sets:
            # if col in df columns :visualize data
            if col in df.columns:
                data=df[col]
                #data name+column name
                dataname=str(file_name)+"_"+str(col)
                #configure plot sizes
                plt.figure(figsize=(10, 6))
                plt.plot(data)
                plt.title(dataname)
                plt.xlabel('Index')
                plt.ylabel(col)
                chartname=dataname+".png"
                #place all chart names in a array.
                self.charts.append(chartname)
                #save charts in the asame folder
                plt.savefig(chartname)                               
            # if col inot in df[col]: print error message
            else:
                print("the column: "+col +" is not in the data.")
            
            plt.close()
        
        # add df name to chart header : preparation for merging documentation 
        new_row = [file_name] * (len(df.columns))
        df.loc[0] = new_row
        df.index = df.index + 1
        df = df.sort_index()

        # merge into final document
        self.merge_df(df)

    #place the charts into a single file
    def mergecharts(self,charts):
            workbook = openpyxl.Workbook()
            #圖像化部分
            worksheet = workbook.active
            i=-39
            try:
                for chartpath in charts:
                    imgpath=str(chartpath)
                    img=Image(imgpath)
                    i=i+40
                    cell="A"+str(i)
                    worksheet.add_image(img,cell)
                excel_file_name = self.totalname+'_visualization.xlsx'
                workbook.save(excel_file_name)

                for chartpath in charts:
                    imgpath=str(chartpath)
                    os.remove(chartpath)
            except Exception as e:
                print(e)

    #Bassic logics of loading the chart.
    def merge_df(self,df):
        if self.merged_df.empty:
            self.merged_df=df
        else:
            self.merged_df=pd.concat([self.merged_df, df], axis=1)


    
    """
    這裡是下半段的東西
    """
    def finalizeprocess2(self):
        dict_path_df={}
        viz_sku_df=[]

        used_criteria=["CPU Package [W]","CPU Package Power [W]", "GPU Power [W]" ]

        f = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])
        for path in f:
            dict_path_df[path]=pd.read_csv(path,header=[0, 1],low_memory=False)
        #篩剩下需要的列
        for path, df in dict_path_df.items():
            col_intersection=list(set(used_criteria).intersection(df.columns.get_level_values(0)))
            if col_intersection:
                df_loc=df.loc[:, col_intersection]
                viz_sku_df.append(df_loc)
            else:
                print("no cols in df")
        #將各表統合
        print(viz_sku_df)
    
                        
#主執行檔
if __name__ == "__main__":
    root = tk.Tk()
    app = logHelperApp(root)
    root.mainloop()