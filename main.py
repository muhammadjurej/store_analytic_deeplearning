from config import default_cfg
from src.store_analytic import StoreAnalytic

import tkinter as tk
import threading
from tkinter import ttk


class App:
    def __init__(self):
        self.config = default_cfg.Config()
        self.WIDTH = self.config.app_width
        self.HEIGHT = self.config.app_height

        self.window = tk.Tk()
        self.window.title("Store Activity Recognition (SAR)")
        self.window.bind('<Escape>', lambda x: self.window.quit())

        self.window.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.window.resizable(False, False)

        self.window.columnconfigure([0], minsize=self.WIDTH)
        self.window.rowconfigure([0,2], minsize=1/6*self.HEIGHT)
        self.window.rowconfigure([1], minsize=4/6*self.HEIGHT)

        # MENUBAR
        self.frm_menu = tk.Frame(master=self.window)
        self.frm_menu.grid(row=0, column=0, sticky="NW")

        self.btn_menuHome = tk.Button(master=self.frm_menu, text="Home", font=("Arial",11), 
                                      command=self.bukaHomePage, height=2, width=15)
        self.btn_menuHome.grid(row=0, column=0, sticky="W")

        self.btn_menuMonitoring = tk.Button(master=self.frm_menu, text="Monitoring", font=("Arial",11),  
                                            command=self.bukaMonitoringPage, height=2, width=15)
        self.btn_menuMonitoring.grid(row=0, column=1, sticky="W")

        self.btn_menuDataHistoris = tk.Button(master=self.frm_menu, text="Data Log", font=("Arial",11),
                                              command=self.bukaDataHistorisPage, height=2, width=15)
        self.btn_menuDataHistoris.grid(row=0, column=2, sticky="W")
        
        # FOOTER
        self.frm_footer = tk.Frame(master=self.window)
        self.frm_footer.grid(row=2, column=0, sticky="S", pady=(0,20))

        lbl_footer = ttk.Label(master=self.frm_footer, text=self.config.footer_text, 
                               font=("Arial",11))
        lbl_footer.grid()

        # FRAME isi di HOMEPAGE
        self.frm_isiHomePage = tk.Frame(master=self.window)
        self.frm_isiHomePage.grid(row=1, column=0, sticky="N")

        lbl_title = ttk.Label(master=self.frm_isiHomePage, text=self.config.title_text, 
                              font=("Arial",18), anchor='center')
        lbl_title.grid(row=0, column=0)

        lbl_desc = ttk.Label(master=self.frm_isiHomePage,text=self.config.desc_text, 
                             anchor='center', font=("Arial",12))
        lbl_desc.grid(row=1, column=0, sticky="N", pady=(34,0))

        lbl_help = ttk.Label(master=self.frm_isiHomePage, text=self.config.help_text, 
                             anchor='center', font=("Arial",12))
        lbl_help.grid(row=2, column=0, sticky="W", pady=(0,0))

        # FRAME isi di MONITORINGPAGE
        self.frm_isiMonitoringPage = tk.Frame(master=self.window)
        self.frm_isiMonitoringPage.columnconfigure(index=0, minsize=int(2/5*self.WIDTH))
        self.frm_isiMonitoringPage.columnconfigure(index=1, minsize=int(3/5*self.WIDTH))

        # Sub-frame source selection
        frm_SourceSelect= tk.Frame(master=self.frm_isiMonitoringPage)
        frm_SourceSelect.grid(row=0, column=0, sticky="NW", padx=(80,0))

        lbl_source = ttk.Label(master=frm_SourceSelect, 
                             text='Source selection', font=("Arial",12))
        lbl_source.grid(row=0, column=0, columnspan=2, pady=5, sticky="NW")

        source_opt = ["video","cam", "webcam"]

        option_width = len(max(source_opt, key=len)) + 15
        self.source_option = tk.StringVar()
        self.source_option.set("Select source")  

        self.dropDown_source = tk.OptionMenu(frm_SourceSelect , self.source_option , *source_opt,
                                             command=self.btn_sourceSelectState)
        self.dropDown_source.config(width=option_width)
        self.dropDown_source.grid(row=1, column=0, sticky="NW")
        
        dict_test = {"In Store":200, 'Spot 1':100, 'Spot 2':250}
        self.btn_sourceStream = tk.Button(master=frm_SourceSelect, text="Start stream", state='disabled', 
                                 font=("Arial",10), command= self.stream_state)
        self.btn_sourceStream.grid(row=1, column=1, sticky="NW", padx=10)

        # Sub-frame person counter
        frm_personCounter = tk.Frame(master=self.frm_isiMonitoringPage)
        frm_personCounter.grid(row=1, column=0, pady=(30,0), sticky="NW", padx=(80,0))

        lbl_counter = ttk.Label(master=frm_personCounter, 
                             text='Person counter', font=("Arial",12))
        lbl_counter.grid(row=0, column=0, pady=5, sticky="NW")

        frm_counterTable = tk.Frame(master=frm_personCounter)
        frm_counterTable.grid(row=1, column=0, sticky="W")

        yscroll = tk.Scrollbar(frm_counterTable)
        yscroll.pack(side="right", fill="y")

        self.tbl_counter = ttk.Treeview(frm_counterTable, yscrollcommand=yscroll.set)
        self.tbl_counter.pack()
        yscroll.config(command=self.tbl_counter.yview)
        
        self.tbl_counter['columns'] = ('spot_id', 'person_count', 'time')
        self.tbl_counter.column('#0', width=0,  stretch=tk.NO)
        self.tbl_counter.column('spot_id' ,anchor=tk.CENTER, width=130)
        self.tbl_counter.column('person_count',anchor=tk.CENTER,width=70)
        self.tbl_counter.column('time',anchor=tk.CENTER,width=70)

        self.tbl_counter.heading('#0',text='',anchor=tk.CENTER)
        self.tbl_counter.heading('spot_id',text="Spot ID",anchor=tk.CENTER)
        self.tbl_counter.heading('person_count',text="Count",anchor=tk.CENTER)
        self.tbl_counter.heading('time',text="Time",anchor=tk.CENTER)

        # Sub-frame monitor plot
        self.frm_monitorPlot = tk.Frame(self.frm_isiMonitoringPage)
        self.frm_monitorPlot.grid(row=0, column=1, rowspan=2)
        self.lbl_monitorPlot = tk.Label(self.frm_monitorPlot)
        self.lbl_monitorPlot.grid()

    def run(self):
        print("APP OPENED")
        self.window.mainloop()
        print("APP CLOSED")


    def bukaHomePage(self):
        self.btn_menuMonitoring['state'] = tk.ACTIVE
        self.btn_menuDataHistoris['state'] = tk.ACTIVE
        if self.btn_menuHome['state'] != tk.DISABLED and self.frm_isiMonitoringPage != None:
            self.btn_menuHome['state'] = tk.DISABLED
            self.frm_isiMonitoringPage.grid_forget()
            self.frm_isiHomePage.grid(row=1,column=0)


    def bukaMonitoringPage(self):
        self.btn_menuHome['state'] = tk.ACTIVE
        self.btn_menuDataHistoris['state'] = tk.ACTIVE
        if self.btn_menuMonitoring['state'] != tk.DISABLED and self.frm_isiHomePage != None:
            self.btn_menuMonitoring['state'] = tk.DISABLED
            self.frm_isiHomePage.grid_forget()
            self.frm_isiMonitoringPage.grid(row=1,column=0)


    def bukaDataHistorisPage(self):
        self.btn_menuHome['state'] = tk.ACTIVE
        self.btn_menuMonitoring['state'] = tk.ACTIVE
        if self.btn_menuDataHistoris['state'] != tk.DISABLED and self.frm_isiHomePage != None:
            self.btn_menuDataHistoris['state'] = tk.DISABLED
            self.frm_isiMonitoringPage.grid_forget()
            self.frm_isiHomePage.grid_forget()


    def btn_sourceSelectState(self, status):
        if status != "Select source":
            self.btn_sourceStream['state'] = 'active'
                

    def stream_state(self):
        if self.btn_sourceStream['text'] == 'Start stream':
            self.dropDown_source.config(state='disable')
            Analytic.inference = True
            Thread_analytic = threading.Thread(target=lambda: Analytic.run(source=self.source_option.get(),
                                                                           container=self.lbl_monitorPlot,
                                                                           table=self.tbl_counter,
                                                                           vis_region=True,
                                                                           oFrame_width=3/5*self.WIDTH, 
                                                                           oFrame_height=4/6*self.HEIGHT))
            Thread_analytic.start()
            print('start STREAM', self.source_option.get())
            self.btn_sourceStream['text'] = 'Stop stream'
        else:
            self.dropDown_source.config(state='active')
            self.btn_sourceStream['text'] = 'Start stream'
            Analytic.inference = False
            for item in self.tbl_counter.get_children():
                self.tbl_counter.delete(item) 


if __name__ == "__main__":
    Analytic = StoreAnalytic()
    App_master = App()
    App_master.run()

    #Analytic.inference = True
    #print('back-end call')
    #Analytic.run(vis_region=False, source='video')
    #print(len(Analytic.imgarray))