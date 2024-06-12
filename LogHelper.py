import os
import sys
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import Entry
from openpyxl.drawing.image import Image
from collections import defaultdict
from matplotlib.widgets import SpanSelector


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
        self.root.resizable(False, False)
        
        #Windows
        self.viswindow=None
        self.fileWin=None
        self.typeWin=None
        
        self.merged_df=pd.DataFrame()
        self.full_project_name=""

        #Variable_testing
        self.cpu_tster=None
        self.gpu_tster=None
        self.tpp_tster=None
        self.thresh_tster=None

        #Button & Frame
        # 創建上半部的框架
        top_frame = tk.Frame(self.root, bd=5, relief=tk.GROOVE)
        top_frame.pack(side="top", fill="both", expand=True)
        submitlabel=tk.Label(top_frame,text="Visualize & concat Files\n\n視覺化檔案並產出總檔")
        submitlabel.pack(side="top", pady=10)


        submitButton = tk.Button(top_frame,text="Select Files",command=self.create_vis_window)
        submitButton.config(padx=80,pady=40,anchor="center")
        submitButton.pack(side="top",pady=20)
        #上半部criteria 部分
        criteria_frame=tk.Frame(top_frame, bd=5, relief=tk.GROOVE)
        CPU_label=tk.Label(criteria_frame,text="CPU :")
        self.CPU_entry=tk.Entry(criteria_frame,validate="key", validatecommand=(self.root.register(self.validate_number), "%P"), justify="center")
        GPU_Label=tk.Label(criteria_frame,text="GPU :")
        self.GPU_entry=tk.Entry(criteria_frame,validate="key", validatecommand=(self.root.register(self.validate_number), "%P"), justify="center")
        TPP_label=tk.Label(criteria_frame,text="TPP :")
        self.TPP_entry=tk.Entry(criteria_frame,validate="key", validatecommand=(self.root.register(self.validate_number), "%P"), justify="center")
        threshold_label=tk.Label(criteria_frame,text="threshold (NOTE : %) :")
        self.threshold_entry=tk.Entry(criteria_frame,validate="key", validatecommand=(self.root.register(self.validate_number), "%P"), justify="center")
        criteria_frame.pack(side="top", fill="both", expand=True)
        CPU_label.grid(row=0,column=0)
        self.CPU_entry.grid(row=1,column=0)
        GPU_Label.grid(row=0,column=1)
        self.GPU_entry.grid(row=1,column=1)
        TPP_label.grid(row=0,column=2)
        self.TPP_entry.grid(row=1,column=2)
        threshold_label.grid(row=0,column=3)
        self.threshold_entry.grid(row=1,column=3)
        
     # validate if input is numbe
    def validate_number(self, value):
        if value.isdigit():
            return True
        elif value == "":
            return True
        else:
            return False

    #Visualization Windows.
    def create_vis_window(self):
        self.cpu_tster = float(self.CPU_entry.get()) if self.CPU_entry.get().strip() else None
        self.gpu_tster = float(self.GPU_entry.get()) if self.GPU_entry.get().strip() else None
        self.tpp_tster = float(self.TPP_entry.get()) if self.TPP_entry.get().strip() else None
        self.thresh_tster = float(self.threshold_entry.get()) if self.threshold_entry.get().strip() else None

        print(self.cpu_tster, self.gpu_tster, self.tpp_tster, self.thresh_tster)

        #show root window if the current one is accidently closed
        def on_close():
            self.root.deiconify()
            self.viswindow.destroy()

        #disable interactions w/root
        #self.root.attributes('-disabled', True)
        self.root.withdraw()

        self.viswindow=tk.Toplevel(root)
        self.viswindow.geometry(f"600x200+{root.winfo_x()}+{root.winfo_y()}")
        
        self.viswindow.protocol("WM_DELETE_WINDOW", on_close)
        self.viswindow.bind("<Destroy>", lambda e: on_close())

        self.viswindow.title("檔案類型選擇")
        self.viswindow.resizable(False,False)

        projectLabel = tk.Label(self.viswindow,text="Enter File Name for visiualized logs")
        projectLabel.pack(side="top",anchor="center",pady=10,fill="both", expand=True)
        self.projectName = tk.Entry(self.viswindow, justify="center")
        self.projectName.pack(side="top",anchor="center",padx=10,pady=10,fill="both", expand=True)    

        submitbutton = tk.Button(self.viswindow,text="Select Logs",command=self.categorize_files)
        submitbutton.config(padx=20, pady=20)
        submitbutton.pack(side="top",anchor="center",pady=20 , padx=5,fill="both", expand=True)

        # Set grab_set to make the viswindow modal
        self.viswindow.grab_set()
        self.viswindow.wait_window(self.viswindow)

    #Categorize/choose log file types: first loading space of dataframes.
    def categorize_files(self):
        
        #show root window if the current one is accidently closed
        def on_close():
            self.root.deiconify()
            self.viswindow.destroy()

        #disable interactions w/root
        #self.root.attributes('-disabled', True)
        self.root.withdraw()

        self.viswindow=tk.Toplevel(root)
        self.viswindow.geometry(f"600x400+{root.winfo_x()}+{root.winfo_y()}")
        
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

        submitbutton = tk.Button(self.viswindow,text="Select Logs",command=self.categorize_files)
        submitbutton.config(padx=20, pady=20)
        submitbutton.pack(side="top",anchor="center",pady=20 , padx=5,fill="both", expand=True)

        # Set grab_set to make the viswindow modal
        self.viswindow.grab_set()
        self.viswindow.wait_window(self.viswindow)

    #Categorize/choose log file types: first loading space of dataframes.
    def categorize_files(self):
        def on_close():
            self.viswindow.deiconify()
            self.fileWin.destroy()
        
        #紀錄project name
        self.full_project_name = self.projectName.get()
        
        #check if all needed columns is entered.
        if not self.full_project_name:
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
        self.fileWin.geometry(f"+{root.winfo_x()}+{root.winfo_y()}")
        self.fileWin.protocol("WM_DELETE_WINDOW", on_close)
        self.fileWin.bind("<Destroy>", lambda e: on_close())
        self.fileWin.title("File Type")
        self.fileWin.withdraw()
        #close last window
        self.viswindow.withdraw()


        #loading win
        self.check_load_win=tk.Toplevel(self.fileWin)
        self.check_load_win.geometry(f"400x100+{root.winfo_x()}+{root.winfo_y()}")
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
            try:
                df=pd.read_csv(path,skipfooter=2,engine="python",encoding="ANSI", on_bad_lines='skip', index_col=False)
            except UnicodeDecodeError:
                messagebox.showwarning("Error", "UnicodeDecodeError occurred. Please check the file encoding.")
                return

            fn = str(os.path.basename(path)).removesuffix(".csv")
            #save dict into dictionary
            self.dfPile[fn]=df

            #Generate checkboxes and labels to each file
            label = tk.Label(self.fileWin, text=f"Choose {path} 's file type:")
            label.pack()
            self.checkbox_frame = tk.Frame(self.fileWin, bd=5, relief=tk.GROOVE)            
            self.file_checkboxes = []

            """
            #HWINFO checkbox:
            hw_var=tk.IntVar()
            hw_checkbox=tk.Checkbutton(self.checkbox_frame, text="HWInfo64",variable=hw_var,pady=5)
            hw_checkbox.var=hw_var
            hw_checkbox.pack(side=tk.LEFT, anchor=tk.W)
            self.file_checkboxes.append(hw_checkbox)

            把hwinfo64拆開
            column_sets.add("CPU Package Power [W]")
            column_sets.add("CPU Package [W]")
            column_sets.add("IA Cores Power [W]")
            column_sets.add("GT Cores Power [W]")
            column_sets.add("GPU Power [W]")
            column_sets.add("System Agent Power [W]")
            column_sets.add("Total Graphics Power")
            """

            cpu_var=tk.IntVar()
            cpu_checkbox=tk.Checkbutton(self.checkbox_frame, text="CPU Power",variable=cpu_var,pady=5)
            cpu_checkbox.var=cpu_var
            cpu_checkbox.pack(side=tk.LEFT, anchor=tk.W)
            self.file_checkboxes.append(cpu_checkbox)

            gpu_var=tk.IntVar()
            gpu_checkbox=tk.Checkbutton(self.checkbox_frame, text="GPU Power",variable=gpu_var,pady=5)
            gpu_checkbox.var=gpu_var
            gpu_checkbox.pack(side=tk.LEFT, anchor=tk.W)
            self.file_checkboxes.append(gpu_checkbox)

            ia_var=tk.IntVar()
            ia_checkbox=tk.Checkbutton(self.checkbox_frame, text="IA Cores Power",variable=ia_var,pady=5)
            ia_checkbox.var=ia_var
            ia_checkbox.pack(side=tk.LEFT, anchor=tk.W)
            self.file_checkboxes.append(ia_checkbox)

            gt_var=tk.IntVar()
            gt_checkbox=tk.Checkbutton(self.checkbox_frame, text="GT Cores Power",variable=gt_var,pady=5)
            gt_checkbox.var=gt_var
            gt_checkbox.pack(side=tk.LEFT, anchor=tk.W)
            self.file_checkboxes.append(gt_checkbox)

            sa_var=tk.IntVar()
            sa_checkbox=tk.Checkbutton(self.checkbox_frame, text="System Agent Power",variable=sa_var,pady=5)
            sa_checkbox.var=sa_var
            sa_checkbox.pack(side=tk.LEFT, anchor=tk.W)
            self.file_checkboxes.append(sa_checkbox)


            #TPP:
            tp_var=tk.IntVar()
            self.tpp_checkbox=tk.Checkbutton(self.checkbox_frame, text="TPP (Optional)",variable=tp_var,pady=5)
            self.tpp_checkbox.var=tp_var
            self.file_checkboxes.append(self.tpp_checkbox)
            self.tpp_checkbox.pack(side=tk.LEFT, anchor=tk.W)

            """
            if df.columns[0]=="Date":
                hw_checkbox.select()
                self.add_tpp_check()

            """
            
            # Store the association between checkboxes and the current file
            checkbox_file_association.append((path, self.file_checkboxes))

            # Pack Checkbuttons Frame to the main frames
            self.checkbox_frame.pack()

        def run_cat_files():
            #loading window
            self.loadwin=tk.Toplevel(self.fileWin)
            self.loadwin.geometry(f"300x100+{root.winfo_x()}+{root.winfo_y()}")
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
            
            #process format
            try:
                self.visualize_and_merge_files(self.dfPile,d)
            except Exception as e:
                self.loadwin.destroy()
                messagebox.showerror("Something occured", "Most likely youve chosen the wrong format. Please choose a correct format. "+ str(e))
                self.fileWin.destroy()
                return
            
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
                        #case "Furmark":
                            #column_sets.add("gpu_power")
                        case "CPU Power":
                            column_sets.add("CPU Package Power [W]")
                            column_sets.add("CPU Package [W]")
                        case "GPU Power":
                            column_sets.add("GPU Power [W]")
                            column_sets.add("Total Graphics Power")
                        case "IA Cores Power":
                            column_sets.add("IA Cores Power [W]")
                        case "GT Cores Power":
                            column_sets.add("GT Cores Power [W]")
                        case "System Agent Power":
                            column_sets.add("System Agent Power [W]")
                        case "TPP (Optional)":
                            column_sets.add("TPP")

            #visualize key(chart name),col_sets(the columns that needed to be visualized)
            self.visualize_merge_docs(file_name,column_sets,dfPile[file_name])

        #merge the whole chart into a single document
        self.mergecharts(self.charts)
        
        #wrap up
        csv_name=self.full_project_name +"_log_files.csv"
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
                #switch cases
                if (col=="CPU Package Power [W]" or col=="CPU Package [W]") and self.cpu_tster!=None and self.thresh_tster!=None:
                    plt.axhspan(self.cpu_tster*(1-(0.01*self.thresh_tster)), self.cpu_tster, color="red", alpha=0.5)
                elif (col=="GPU Power [W]" or col=="Total Graphics Power") and self.gpu_tster!=None and self.thresh_tster!=None:
                    plt.axhspan(self.gpu_tster*(1-(0.01*self.thresh_tster)), self.gpu_tster, color="red", alpha=0.5)
                plt.title(dataname)
                plt.xlabel('Index')
                plt.ylabel(col)
                chartname=dataname+".png"
                #place all chart names in a array.
                self.charts.append(chartname)
                #save charts in the same folder
                plt.savefig(chartname)
                plt.close()

                #show images for data
                self.twographs(data,dataname)

            #TPP needs special calculations for the hub
            elif col=="TPP":
                #take care of multiple column names
                if "CPU Package Power [W]" in df.columns:
                    cpu=df["CPU Package Power [W]"]
                elif "CPU Package [W]" in df.columns:
                    cpu=df["CPU Package [W]"]
                else: cpu=None
                if "GPU Power [W]" in df.columns:
                    gpu=df["GPU Power [W]"]
                elif "Total Graphics Power" in df.columns:
                    gpu=df["Total Graphics Power"]
                else: gpu=None
                #calculations for tpp:
                df["TPP"]=cpu.add(gpu)
                data=df["TPP"]
                dataname=str(file_name)+"_TPP"
                plt.plot(df.index,data)
                if col=="TPP" and self.tpp_tster!=None and self.thresh_tster!=None:
                    plt.axhspan(self.tpp_tster*(1-(0.01*self.thresh_tster)),self.tpp_tster,color="red", alpha=0.5)
                #plt.fill_between
                plt.title(dataname)
                plt.xlabel('Index')
                plt.ylabel("TPP")
                chartname=dataname+".png"
                self.charts.append(chartname)
                plt.savefig(chartname)
                plt.close()
                
                #showing images
                self.twographs(data,dataname)

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

    def twographs(self,basedata,dataname):
        fig, (ax1, ax2) = plt.subplots(2, figsize=(8, 6))
        plt.subplots_adjust(hspace=0.5)

        #add reference lines over here
        if dataname.endswith(("CPU Package Power [W]","CPU Package [W]")) and self.cpu_tster!=None and self.thresh_tster!=None:
            ax1.axhspan(self.cpu_tster*(1-(0.01*self.thresh_tster)), self.cpu_tster, color="red", alpha=0.5)
            ax2.axhspan(self.cpu_tster*(1-(0.01*self.thresh_tster)), self.cpu_tster, color="red", alpha=0.5)
        elif dataname.endswith(("GPU Power [W]","Total Graphics Power")) and self.gpu_tster!=None and self.thresh_tster!=None:
            ax1.axhspan(self.gpu_tster*(1-(0.01*self.thresh_tster)), self.gpu_tster, color="red", alpha=0.5)
            ax2.axhspan(self.gpu_tster*(1-(0.01*self.thresh_tster)), self.gpu_tster, color="red", alpha=0.5)
        elif dataname.endswith("TPP") and self.tpp_tster!=None and self.thresh_tster!=None:
            ax1.axhspan(self.tpp_tster*(1-(0.01*self.thresh_tster)),self.tpp_tster,color="red", alpha=0.5)
            ax2.axhspan(self.tpp_tster*(1-(0.01*self.thresh_tster)),self.tpp_tster,color="red", alpha=0.5)

        x = np.arange(0.0, len(basedata), 1)  # Assuming x values are simply indices
        y = basedata.values  # Assuming y values come from the specified column

        ax1.plot(x, y)
        ax1.set_title(str(dataname)+"_inspection")

        line2, = ax2.plot([], [])
        def onselect(xmin, xmax):
            indmin, indmax = np.searchsorted(x, (xmin, xmax))
            indmax = min(len(x) - 1, indmax)

            region_x = x[indmin:indmax]
            region_y = y[indmin:indmax]

            if len(region_x) >= 2:
                line2.set_data(region_x, region_y)
                ax2.set_xlim(region_x[0], region_x[-1])
                ax2.set_ylim(region_y.min(), region_y.max())

                # Marking highest and lowest values
                highest_idx = np.argmax(region_y)
                lowest_idx = np.argmin(region_y)
                ax2.plot(region_x[highest_idx], region_y[highest_idx], 'ro', label='Highest')
                ax2.plot(region_x[lowest_idx], region_y[lowest_idx], 'bo', label='Lowest')

                # Annotating highest and lowest valuesm
                ax2.annotate(f'{region_y[highest_idx]:.2f}', xy=(region_x[highest_idx], region_y[highest_idx]), xytext=(-20, 10), textcoords='offset points', arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5', color='red'))
                ax2.annotate(f'{region_y[lowest_idx]:.2f}', xy=(region_x[lowest_idx], region_y[lowest_idx]), xytext=(-20, 10), textcoords='offset points', arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5', color='blue'))

                fig.canvas.draw_idle()
                
        span = SpanSelector(
            ax1,
            onselect,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True
        )
        # Set useblit=True on most backends for enhanced performance.
        plt.show()

    #place the charts into a single file
    def mergecharts(self,charts):
        workbook = openpyxl.Workbook()
        exe_file_path =  os.path.dirname(os.path.abspath(sys.argv[0]))
        extra_images=[]
            
        if len(charts)==0:
            tk.messagebox.showwarning(title="No data", message="There's no available charts for the whole project, no need for visualization")
            return

        #Visualization
        worksheet = workbook.active
        i=-39
        try:
            for chartpath in charts:
                imgpath=str(chartpath)
                img=Image(imgpath)
                i=i+40
                cell="A"+str(i)
                worksheet.add_image(img,cell)

            #find other saved jpeg files in the folder
            for filename in os.listdir(exe_file_path):
                # user jpeg format
                if filename.lower().endswith(".jpeg") and filename not in charts:
                    img = Image(filename)
                    i += 40
                    cell = "A" + str(i)
                    worksheet.add_image(img, cell)
                    extra_images.append(filename)
                # user saveed png format
                if filename.lower().endswith(".png") and filename not in charts:
                    img = Image(filename)
                    i += 40
                    cell = "A" + str(i)
                    worksheet.add_image(img, cell)
                    extra_images.append(filename)
            
        except Exception as e:
            tk.messagebox.showwarning(title="Exception happened", message=str(e))
            
        #separate visualization names for log/img stacking
        excel_file_name = self.full_project_name+'_visualization.xlsx'
        workbook.save(excel_file_name)

        for chartpath in charts:
            imgpath=str(chartpath)
            os.remove(chartpath)
        for e in extra_images:
            e_imgpath=str(e)
            os.remove(e_imgpath)

    #Bassic logics of loading the chart.
    def merge_df(self,df):
        if self.merged_df.empty:
            self.merged_df=df
        else:
            self.merged_df=pd.concat([self.merged_df, df], axis=1)
    

#主執行檔
if __name__ == "__main__":#
    root = tk.Tk()
    app = logHelperApp(root)
    root.mainloop()