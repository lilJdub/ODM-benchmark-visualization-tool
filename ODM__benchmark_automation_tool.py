import os
import tkinter as tk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from openpyxl.drawing.image import Image

#處理多線程
import threading

#testing
import ttkbootstrap

class logHelperApp:
    #initialize root window
    def __init__(self,root):
        style=ttkbootstrap.Style(theme="pulse")
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
        
        #
        self.merged_df=pd.DataFrame()
        self.totalname=""
        submitButton = tk.Button(self.root,text="Select Files",command=self.create_vis_window)
        submitButton.config(padx=80,pady=40,anchor="center")
        submitButton.pack(side="top",pady=40)
        
        finalizeButton = tk.Button(self.root,text="final results",padx=80,pady=40,command=self.finalizeprocess2)#)
        finalizeButton.config(padx=80,pady=40,anchor="center")
        finalizeButton.pack(side="bottom",pady=40)

    #Visualization Windows.
    def create_vis_window(self):
        self.viswindow=tk.Toplevel(root)

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
        submitbutton.pack(side="top",anchor="center",pady=40)

    #Categorize/choose log file types: first loading space of dataframes.
    def categorize_files(self):
        df_pile=[]
        self.chkbox_dict={}
        
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
            df_pile.append(df)

            #get filename only
            file_name = str(os.path.basename(path)).removesuffix(".csv")


            #Generate checkboxes and labels to each file
            label = tk.Label(self.fileWin, text=f"Choose {path} 's file type:")
            label.pack()
            self.checkbox_frame = tk.Frame(self.fileWin)
            
            fileTools=["AIDA64","Furmark", "3DMark","HWInfo64","Prime95"]
            for name in fileTools:
                var=tk.BooleanVar
                checkbox=tk.Checkbutton(self.checkbox_frame, text=name)
                checkbox.pack(side=tk.LEFT, anchor=tk.W)
                print(path,name)
                
                #Check boxes based on df
                if df.columns[2]=="3DMark3DMark" and name =="3DMark" :
                    checkbox.select()
                if df.columns[3]=="AIDA64AIDA64" and name =="AIDA64":
                    checkbox.select()
                if df.columns[4]=="HWINFO64HWINFO64" and name =="HWInfo64":
                    checkbox.select()
                if df.columns[5]=="FurmarkFurmark" and name =="Furmark":
                    checkbox.select()

            # Pack Checkbuttons Frame to the main frames
            self.checkbox_frame.pack()

        def run_cat_files():
            #finds out checkbox
            print(self.chkbox_dict)


        #Submit button for the next step
        submit_category=tk.Button(self.fileWin, text="Submit file", command=run_cat_files)
        submit_category.pack()

        self.fileWin.deiconify()
        self.loadwin.destroy()

    

    #選擇visualizatiion的格式
    def run_vis_window(self):
        f = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])
        self.typeWin = tk.Toplevel(self.viswindow)
        self.typeWin.title("檔案類型選擇")

        format_entries = []  
        selected_formats = {}

        #依不同檔案(這裡以路徑代稱)去選擇格式
        for path in f:
            label = tk.Label(self.typeWin, text=f"選擇 {path} 的格式:")
            label.pack()
            format_entry = ttk.Combobox(self.typeWin, values=["3DMark+Prime95 AC balanced / Burnin AC balanced / Furmark H_L_H AC balanced","other"], state='readonly')
            format_entry.pack()
            format_entries.append(format_entry)
            selected_formats[path] = None

        #更新總共文件黨名
        self.totalname=str(self.projectName.get())+"_"+str(self.phase.get())+"_"+str(self.prodSKU.get())
        
        #依照不同儲存的格式下去套用不同邏輯
        def runtype():
            charts=[]
            
            for i, entry in enumerate(format_entries):
                selected_format = entry.get()
                path = f[i]

                #將data分為上下段(header/footer)
                df=pd.read_csv(path,skipfooter=2,engine="python")
                df2=pd.read_csv(path,encoding="utf-8",engine="python").tail(2)

                file_name = str(os.path.basename(path)).removesuffix(".csv")
                match selected_format:
                    #若選擇furmark邏輯
                    case "3DMark+Prime95 AC balanced / Burnin AC balanced / Furmark H_L_H AC balanced":
                        self.visualize_and_merge_group1(df,df2,file_name,charts)
                        #若選擇burning邏輯
                    case "other":
                        print("")
            
            self.mergecharts(charts,file_name)
            csv_name=self.totalname +"_log_files.csv"
            self.merged_df.to_csv(csv_name, index=False)

            #全merged完記得清
            self.merged_df=pd.DataFrame()

            #實際結束點:
            self.viswindow.destroy()
                        
            
        submitType = tk.Button(self.typeWin, text="finished", command=runtype)
        submitType.config(padx=30,pady=10)
        submitType.pack(pady=20)
               
                
    #分類furmark類的讀取邏輯
    def visualize_and_merge_group1(self,df,df2,file_name,charts):
        #因應列名不同"CPU Package [W]","CPU Package Power [W]"
        cpu_cols=""
        if "CPU Package [W]" in df.columns:
            cpu_cols="CPU Package [W]"
        else:
            cpu_cols="CPU Package Power [W]"
        #需要的欄位
        column_names=[cpu_cols,"GPU Power [W]"]
        for column_name in column_names:
            data=df[column_name]
            dataname=str(file_name)+"_"+str(column_name)
            plt.figure(figsize=(10, 6))  # 設置圖表大小
            plt.plot(data)
            plt.title(dataname)
            plt.xlabel('Index')
            plt.ylabel(column_name)
            chartname=dataname+".png"
            charts.append(chartname)
            plt.savefig(chartname)
        plt.close()

        # 在df的上面添加一行，值为file_name
        new_row = [file_name] * (len(df.columns))
        df.loc[0] = new_row
        df.index = df.index + 1
        df = df.sort_index()
             
        #把footer接上
        whole_df=pd.concat([df, df2], axis=0)
        
        #讀取的df回收利用 用來merge成文件總表
        self.merge_df(df)
    
    #把拿下來的df彙總
    def merge_df(self,df):
        self.coloredrows.append(df.shape[0])
        if self.merged_df.empty:
            self.merged_df=df
        else:
            self.merged_df=pd.concat([self.merged_df, df], axis=1)
        

    def mergecharts(self,charts,file_name):
        workbook = openpyxl.Workbook()
        #圖像化部分
        worksheet = workbook.active
        i=-39
        for chartpath in charts:
            imgpath=str(chartpath)
            img=Image(imgpath)
            i=i+40
            cell="A"+str(i)
            worksheet.add_image(img,cell)
        excel_file_name = self.totalname+'_visualizatiion.xlsx'
        workbook.save(excel_file_name)

        for chartpath in charts:
            imgpath=str(chartpath)
            os.remove(chartpath)

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

    

'''
#疊圖部分:將各個總表抓起來疊圖
    def finalizeprocess(self):
        f = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])
        df_cpu_list=[]
        df_temp=[]
        for path in f :
            df=pd.read_csv(path,header=[0, 1],low_memory=False)
            df_cpu_list.append(df)

        for df in df_cpu_list:
            if "CPU Package [W]" in df.columns.get_level_values(0):
                df_temp.append(df["CPU Package [W]"])
            elif "CPU Package Power [W]" in df.columns.get_level_values(0):
                df_temp.append(df["CPU Package Power [W]"])
        final_chart_cols=["3DMark Prim95 AC", "AIDA64+Furmark", "Burnin AC balanced","Furmark H_L_H AC Balanced"]

        # 創建一個空的DataFrame來存儲所有數據
        for chart in final_chart_cols:
            #plt
            plt.figure(figsize=(10, 6))
            figures=[]
            #找有沒有在各df存在
            
            for df in df_temp:
                if chart in df.columns.values:
                    #圖裡加一條
                    figures.append(np.array(df[chart]))
            # Check if any data was found for the current chart
            if len(figures) > 0:
                # Loop through each array in figures and plot it separately
                for figure in figures:
                    plt.plot(figure)

                # Set the title of the plot
                plt.title(chart)
                # Display the plot
                plt.show()
            else:
                print(f"No data found for the chart: {chart}")
 
'''
    
                        
#主執行檔
if __name__ == "__main__":
    root = tk.Tk()
    app = logHelperApp(root)
    root.mainloop()