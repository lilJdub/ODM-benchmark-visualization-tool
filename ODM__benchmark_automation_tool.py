import os
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
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
        top_frame = tk.Frame(self.root, bd=5, relief=tk.GROOVE)
        top_frame.pack(side="top", fill="both", expand=True)
        submitlabel=tk.Label(top_frame,text="Visualize Files\n視覺化檔案")
        submitlabel.pack(side="top", pady=20)
        submitButton = tk.Button(top_frame,text="Select Files",command=self.create_vis_window)
        submitButton.config(padx=80,pady=40,anchor="center")
        submitButton.pack(side="top",pady=40)
        
        # 創建下半部的框架
        bottom_frame = tk.Frame(self.root, bd=5, relief=tk.GROOVE)
        bottom_frame.pack(side="top", fill="both", expand=True)
        finalizelabel=tk.Label(bottom_frame,text="Stacking analysis\n疊圖分析")
        finalizelabel.pack(side="top", pady=20)
        finalizeButton = tk.Button(bottom_frame,text="Select files",command=self.finalizeprocess2)
        finalizeButton.config(padx=80,pady=40,anchor="center")
        finalizeButton.pack(side="top",pady=40)

    #Visualization Windows.
    def create_vis_window(self):
        #disable interactions w/root
        self.root.attributes('-disabled', True)

        self.viswindow=tk.Toplevel(root)
        self.viswindow.geometry(self.root.geometry())

        def on_close():
            # Enable interactions with the root window when the viswindow is closed
            self.root.attributes('-disabled', False)
            self.viswindow.destroy()
        
        self.viswindow.protocol("WM_DELETE_WINDOW", on_close)
        self.viswindow.bind("<Destroy>", lambda e: on_close())

        self.viswindow.title("檔案類型選擇")
        self.viswindow.resizable(False,False)

        projectLabel = tk.Label(self.viswindow,text="Enter Project Name")
        projectLabel.pack(side="top",anchor="center",pady=10,fill="both", expand=True)
        self.projectName = tk.Entry(self.viswindow, justify="center")
        self.projectName.pack(side="top",anchor="center",padx=10,pady=10,fill="both", expand=True)    

        phaseLabel = tk.Label(self.viswindow,text="Choose Phase Name")
        phaseLabel.pack(side="top",anchor="center",pady=10,fill="both", expand=True)
        self.phase=ttk.Combobox(self.viswindow,values=["DB","SI","PV","MV"],state="readonly", justify="center")
        self.phase.pack(side="top",anchor="center",padx=10,pady=10,fill="both", expand=True)

        skuLabel = tk.Label(self.viswindow,text="Product SKU")
        skuLabel.pack(side="top",anchor="center",pady=10,fill="both", expand=True)
        self.prodSKU = tk.Entry(self.viswindow, justify="center")
        self.prodSKU.pack(side="top",anchor="center",padx=10,pady=10,fill="both", expand=True)

        submitbutton = tk.Button(self.viswindow,text="Select Files",command=self.categorize_files)
        submitbutton.config(padx=20, pady=20)
        submitbutton.pack(side="top",anchor="center",pady=20 , padx=5,fill="both", expand=True)

        # Set grab_set to make the viswindow modal
        self.viswindow.grab_set()
        self.viswindow.wait_window(self.viswindow)

    #Categorize/choose log file types: first loading space of dataframes.
    def categorize_files(self):
        
        #紀錄project name
        project_name = self.projectName.get()
        phase_name = self.phase.get()
        prod_sku = self.prodSKU.get()
        self.totalname=str(project_name)+"_"+str(phase_name)+"_"+str(prod_sku)
        
        #check if all needed columns is entered.
        if not project_name or not prod_sku:
            messagebox.showerror("Error", "Please enter Project Name and Product SKU.")
            return

        #暫存
        self.dfPile={}
        checkbox_file_association = []

        #Choose files for using
        f=filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])
        #check if f is emnpty
        if len(f)<1:
            messagebox.showerror("Error", "No files selected. Please choose at least one CSV file.")
            return
    
        #checkbox windows
        self.fileWin=tk.Toplevel(self.viswindow)
        self.fileWin.title("File Type")
        self.fileWin.withdraw()

        #loading win
        self.check_load_win=tk.Toplevel(self.fileWin)
        self.check_load_win.geometry("400x100")
        self.check_load_win.title("Loading")
        check_label=tk.Label(self.check_load_win,text="checking data type, please wait.....")
        check_label.pack(side="top", fill="both", expand=True)
        check_load_win_label=tk.Label(self.check_load_win,text="Now loading file : 0/"+str(len(f)))
        check_load_win_label.pack(side="top", fill="both", expand=True)
        clw_counter=0
        
        #update UI
        self.fileWin.update()
        
        #each file type
        for path in f:
                
            #update loading window information
            clw_counter+=1
            check_load_win_label.config(text="Now loading file :"+str(clw_counter)+"/"+str(len(f)))
            
            self.check_load_win.minsize(self.check_load_win.winfo_reqwidth(), self.check_load_win.winfo_reqheight())
            self.check_load_win.update()

            #load and save df
            df=pd.read_csv(path,skipfooter=2,engine="python",encoding="ANSI", on_bad_lines='skip', index_col=False)

            fn = str(os.path.basename(path)).removesuffix(".csv")
            #save dict into dictionary
            self.dfPile[fn]=df

            #Generate checkboxes and labels to each file
            label = tk.Label(self.fileWin, text=f"Choose {path} 's file type:")
            label.pack()
            self.checkbox_frame = tk.Frame(self.fileWin, bd=5, relief=tk.GROOVE)
            
            fileTools=["Furmark","HWInfo64"]
            file_checkboxes = []
            for name in fileTools:
                var=tk.IntVar()
                checkbox=tk.Checkbutton(self.checkbox_frame, text=name,variable=var,pady=5)
                checkbox.var=var
                checkbox.pack(side=tk.LEFT, anchor=tk.W)
                file_checkboxes.append(checkbox)

                #Check boxes based on df
                if df.columns[0]=="Date" and name =="HWInfo64":
                    checkbox.select()
                if df.columns[0]=="Renderer" and name =="Furmark":
                    checkbox.select()

            # Store the association between checkboxes and the current file
            checkbox_file_association.append((path, file_checkboxes))

            # Pack Checkbuttons Frame to the main frames
            self.checkbox_frame.pack()

        def run_cat_files():
            #loading window
            self.loadwin=tk.Toplevel(self.fileWin)
            self.loadwin.geometry("300x100")
            self.loadwin.title("Loading")
            load_label=tk.Label(self.loadwin,text="Loading file data, please wait.....")
            load_label.pack(side="top", fill="both", expand=True)

            #update UI
            self.fileWin.update()
        
            #get an dictionary
            d=defaultdict(dict)
            
            #checking each individual files for usage
            for file_path, file_checkboxes in checkbox_file_association:
                file_name = str(os.path.basename(file_path)).removesuffix(".csv")
                for cb in file_checkboxes:
                    chkboxtext=cb.cget("text")
                    #d: filename in first layer, then a dictionary of checkbox-state in value set
                    d[file_name][chkboxtext]=cb.var.get()
            
            #Working on here:            
            try:
                self.visualize_and_merge_files(self.dfPile,d)
            except Exception as e:
                self.loadwin.destroy()
                messagebox.showerror("Something occured", "Most likely youve chosen the wrong format. Please choose a correct format. "+ str(e))
                self.fileWin.destroy()
                return
            
            #d: 3DMark Prim95 AC': {'AIDA64': 0, 'Furmark': 1, '3DMark': 0, 'HWInfo64': 0, 'Prime95': 0}, 'AIDA64+Furmark': {'AIDA64': 0, 'Furmark': 1, '3DMark': 0, 'HWInfo64': 0, 'Prime95': 0}, 'Burnin AC balanced': {'AIDA64': 0, 'Furmark': 1, '3DMark': 0, 'HWInfo64': 0, 'Prime95': 0}, 'Furmark H_L_H AC Balanced': {'AIDA64': 0, 'Furmark': 1, '3DMark': 0, 'HWInfo64': 0, 'Prime95': 0}})
            self.loadwin.destroy()
            

        #Submit button for the next step
        submit_category=tk.Button(self.fileWin, text="Submit file", command=run_cat_files, padx=10,pady=10)
        submit_category.pack(pady=10)

        self.fileWin.deiconify()
        self.check_load_win.destroy()

        self.fileWin.grab_set()

    #main hub for visualization and merging
    def visualize_and_merge_files(self,dfPile,d):
        self.merged_df=pd.DataFrame()
        self.charts=[]

        #all the file names
        for file_name,val in d.items():
            #The column in df (without duplicates)
            column_sets=set()
            
            #switch based on val: add the criteria that needs to be visualized
            for k,v in val.items():
                if v==1:
                    match k:
                        case "Furmark":
                            column_sets.add("gpu_power")
                        case "HWInfo64":
                            column_sets.add("CPU Package Power [W]")
                            column_sets.add("CPU Package [W]")
                            column_sets.add("IA Cores Power [W]")
                            column_sets.add("GT Cores Power [W]")
                            column_sets.add("GPU Power [W]")
                            column_sets.add("System Agent Power [W]")
                            column_sets.add("Total Graphics Power")

            #visualize key(chart name),col_sets(the columns that needed to be visualized)
            self.visualize_merge_docs(file_name,column_sets,dfPile[file_name])

        #merge the whole chart into a single document
        self.mergecharts(self.charts, 1)
        
        #wrap up
        csv_name=self.totalname +"_log_files.csv"
        self.merged_df.to_csv(csv_name, index=False)

        #全merged完記得清
        self.merged_df=pd.DataFrame()

        """
        the actual finishing point
        """
        if len(self.charts)!=0:
            tk.messagebox.showwarning(title="Document generation done", message="Finished generating documents. Please check file folder.")

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
                errmsg="the column: "+col +" is not in the data."
                er=tk.Label(self.loadwin,text=errmsg)
                er.pack(side="top", fill="both", expand=True)
                self.loadwin.update()
            plt.close()

        # Foolproof: if theres no charts then stop rest of the program
        if len(self.charts)==0:
            tk.messagebox.showwarning(title="Wrong data", message="No available charts for "+file_name+", please check if the data has the correct format.")
            return
        
        else:
            # add df name to chart header : preparation for merging documentation 
            new_row = [file_name] * (len(df.columns))
            df.loc[0] = new_row
            df.index = df.index + 1
            df = df.sort_index()

            # merge into final document
            self.merge_df(df)

    #place the charts into a single file
    def mergecharts(self,charts,gate):
            
            if len(charts)==0:
                tk.messagebox.showwarning(title="No data", message="There's no available charts for the whole project, no need for visualization")
                return
            
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
            except Exception as e:
                tk.messagebox.showwarning(title="Exception happened", message=str(e))
                
            #separate visualization names for log/img stacking
            if gate==1:
                excel_file_name = self.totalname+'_visualization.xlsx'
            elif gate==2:
                excel_file_name = "final_viz.xlsx"
                
            workbook.save(excel_file_name)

            for chartpath in charts:
                imgpath=str(chartpath)
                os.remove(chartpath)
            

    #Bassic logics of loading the chart.
    def merge_df(self,df):
        if self.merged_df.empty:
            self.merged_df=df
        else:
            self.merged_df=pd.concat([self.merged_df, df], axis=1)
    
    """
    Second function of the tool
    """
    def finalizeprocess2(self):
        tk.messagebox.showwarning(title="Under construction", message="Not available in this vession yet.")
        
    def finalizeprocess(self):
        
        # Now Loading pop-up-window
        self.fin_loading_window = tk.Toplevel(self.root)
        self.fin_loading_window.geometry("300x100")
        fin_loading_label = tk.Label(self.fin_loading_window, text="Now Loading...")
        fin_loading_label.pack(side="top", fill="both", expand=True)
        

        self.dict_path_df={}

        f = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])

        #loading window to the top of all windows
        self.fin_loading_window.lift()

        #no need for later if f==none
        if not f:
            return
        for path in f:
            self.dict_path_df[path]=pd.read_csv(path,header=[0, 1],low_memory=False)

        #the window for checkboxes
        self.final_checkwin=tk.Toplevel(root)
        self.final_checkwin.geometry(self.root.geometry())
        fin_label_frame=tk.Frame(self.final_checkwin, bd=5, relief=tk.GROOVE)
        fin_label_frame.pack()
        
        fin_label1=tk.Label(fin_label_frame, text="Files chosen are: ")
        fin_label1.pack()

        #saving path into an array
        
        #finding out path
        for path, df in self.dict_path_df.items():
            fin_check_label=tk.Label(fin_label_frame, text=path ,padx=10)
            fin_check_label.pack(pady=(10,0))

        #frame below for checkboxes
        fin_check_frame= tk.Frame(self.final_checkwin, bd=5, relief=tk.GROOVE)
        fin_check_frame.pack(fill="x",expand=True)

        #choosing and setting the criteria of each df
        fin_label2=tk.Label(fin_check_frame, text="Choose the criteria.")
        fin_label2.pack()

        #Saving states of checkboxes
        self.checkbox_states = {
            'aida64': [tk.BooleanVar(), tk.BooleanVar()],
            'furmark': [tk.BooleanVar(), tk.BooleanVar()],
            '3dmark': [tk.BooleanVar(), tk.BooleanVar()],
            'hwinfo64': [tk.BooleanVar(), tk.BooleanVar()],
            'prime95': [tk.BooleanVar(), tk.BooleanVar()]
        }

        self.testerstates={
            'aida64': ["a64","a642"],
            'furmark': ["fm","fm2"],
            '3dmark': ["3dm","3dm2"],
            'hwinfo64': ["hw64","hw642"],
            'prime95': ["p95","p952"]
        }

        #AIDA64 checkboxes
        aida_label = tk.Label(fin_check_frame, text="AIDA64")
        aida_label.pack(pady=(5,0))
        aidachkframe=tk.Frame(fin_check_frame, bd=5, relief=tk.GROOVE)
        aidachkframe.pack()
        chk=self.testerstates["aida64"]
        for index, c in enumerate(chk):            
            cb=tk.Checkbutton(aidachkframe, text=c,pady=5,variable=self.checkbox_states['aida64'][index])
            cb.pack(side=tk.LEFT, anchor=tk.W)

        #Furmark checkboxes
        furmark_label = tk.Label(fin_check_frame, text="Furmark")
        furmark_label.pack(pady=(5,0))
        fmchkframe=tk.Frame(fin_check_frame, bd=5, relief=tk.GROOVE)
        fmchkframe.pack()
        chk=self.testerstates["furmark"]
        for index, c in enumerate(chk):            
            cb=tk.Checkbutton(fmchkframe, text=c,pady=5,variable=self.checkbox_states['furmark'][index])
            cb.pack(side=tk.LEFT, anchor=tk.W)

        #3Dmark checkboxes
        threedmark_label = tk.Label(fin_check_frame, text="3DMark")
        threedmark_label.pack(pady=(5,0))
        threechkframe=tk.Frame(fin_check_frame, bd=5, relief=tk.GROOVE)
        threechkframe.pack()
        chk=self.testerstates["3dmark"]
        for index, c in enumerate(chk):            
            cb=tk.Checkbutton(threechkframe, text=c,pady=5,variable=self.checkbox_states['3dmark'][index])
            cb.pack(side=tk.LEFT, anchor=tk.W)
        
        
        #hwinfo64 checkboxes
        hwinfo64_label = tk.Label(fin_check_frame, text="HWinfo 64")
        hwinfo64_label.pack(pady=(5,0))
        hw64chkframe=tk.Frame(fin_check_frame, bd=5, relief=tk.GROOVE)
        hw64chkframe.pack()
        chk=self.testerstates["hwinfo64"]
        for index, c in enumerate(chk):            
            cb=tk.Checkbutton(hw64chkframe, text=c,pady=5,variable=self.checkbox_states['hwinfo64'][index])
            cb.pack(side=tk.LEFT, anchor=tk.W)
        
        #prime95 checkboxes
        prime95_label = tk.Label(fin_check_frame, text="Prime95")
        prime95_label.pack(pady=(10,0))
        p95frame=tk.Frame(fin_check_frame, bd=5, relief=tk.GROOVE)
        p95frame.pack()
        chk=self.testerstates["prime95"]
        for index, c in enumerate(chk):            
            cb=tk.Checkbutton(p95frame, text=c,pady=5,variable=self.checkbox_states['prime95'][index])
            cb.pack(side=tk.LEFT, anchor=tk.W)

        self.fin_loading_window.destroy()
        def run_analysis():
        #getting parameters
            params=[]
            for key, vars_list in self.checkbox_states.items():
                 for index, var in enumerate(vars_list):
                    if var.get():
                        #saving checkboxes checked.
                        params.append(self.testerstates[key][index])
            self.img_stack_analysis(params)

        final_analyze_btn=tk.Button(self.final_checkwin, text="Image stacking analysis.", command=run_analysis, pady=10)
        final_analyze_btn.pack(fill="x", pady=10, padx=5)

        #resizing window for oversizing
        self.final_checkwin.update()
        self.final_checkwin.minsize(self.final_checkwin.winfo_reqwidth(), self.final_checkwin.winfo_reqheight())
        

    #analysis
    def img_stack_analysis(self, params):
        f_charts=[]
        for p in params:
            #see if everything is in place
            for path, df in self.dict_path_df.items():
                if p in df.columns:
                    plt.plot(df[p], label=p+"")
                else:
                    print(p+" not available in data provided.")

            plt.title(path+p)
            plt.legend()

            #saving charts stacked into a file.
            analysis_chartname=path+"_"+p+".png"
            plt.savefig(analysis_chartname)
            f_charts.append(analysis_chartname)
            plt.close()
        
        self.mergecharts(f_charts, 2)
        tk.messagebox.showwarning(title="Document generation done", message="Finished generating documents. Please check file folder.")
        self.final_checkwin.destroy()

#主執行檔
if __name__ == "__main__":
    root = tk.Tk()
    app = logHelperApp(root)
    root.mainloop()