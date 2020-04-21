from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime
import nidaqmx

plt.rcParams['axes.facecolor'] = '#2b2b2b'
plt.rcParams['figure.facecolor'] = '#3c3f41'

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    # Creation of init_window
    def init_window(self):
        # Changing the title of the master widget
        self.master.title("NI-DAQmx Viewer")
        # Allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # Define sample rate and n samples
        self.samples = 1000
        self.sf = 10000

        # Define modules
        self.module_options = []
        self.get_modules()
        self.active_module = self.module_options[0]

        # Define channels
        self.channel_options = ["ai0", "ai1", "ai2", "ai3"]
        self.active_channel = self.channel_options[0]

        # Define task
        self.task = self.get_task()
        #self.task = None
        self.fig = plt.Figure(figsize=(6, 3))
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)

        self.update_fig()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().place(relheight=1, relwidth=0.7, relx=0.25, rely=0)
        self.ani = animation.FuncAnimation(self.fig, self.sensors, interval=1, blit=False)

        # Build Settings List
        self.sv1 = StringVar()
        label1 = Label(self, text="Sampling frequency", bg='#3c3f41', fg='#bbbbbb', font=('Helvetica', '15'), anchor=W,
                       justify=LEFT)
        label1.place(relheight=0.05, width=200, relx=0.05, rely=0.1)
        entry1 = Entry(textvariable=self.sv1, validate="focusout", validatecommand=self.entry1_callback, bg='#4e5254',
                       fg='#bbbbbb', font=('Helvetica', '15'))
        entry1.place(relheight=0.05, width=100, relx=0.05, rely=0.2, anchor=W)
        entry1.delete(0, END)
        entry1.insert(0, self.sf)

        self.sv2 = StringVar()
        label2 = Label(self, text="Sample number", bg='#3c3f41', fg='#bbbbbb', font=('Helvetica', '15'), anchor=W,
                       justify=LEFT)
        label2.place(relheight=0.05, width=150, relx=0.05, rely=0.25)
        entry2 = Entry(textvariable=self.sv2, validate="focusout", validatecommand=self.entry2_callback, bg='#4e5254',
                       fg='#bbbbbb', font=('Helvetica', '15'))
        entry2.place(relheight=0.05, width=100, relx=0.05, rely=0.35, anchor=W)
        entry2.delete(0, END)
        entry2.insert(0, self.samples)

        label3 = Label(self, text="Module", bg='#3c3f41', fg='#bbbbbb', font=('Helvetica', '15'), anchor=W,
                       justify=LEFT)
        label3.place(relheight=0.05, width=100, relx=0.05, rely=0.4)
        modules = StringVar()
        # Dropdown for modules
        modules.set(self.active_module)  # default value
        modules_menu = OptionMenu(self, modules, *self.module_options, command=self.module_menu_callback)
        modules_menu["highlightthickness"] = 0
        modules_menu["menu"].config(bg='#4e5254', fg='#bbbbbb', font=('Helvetica', '15'))
        modules_menu.config(bg='#4e5254', fg='#bbbbbb', font=('Helvetica', '15'))
        modules_menu.place(relheight=0.05, width=200, relx=0.05, rely=0.5, anchor=W)

        label4 = Label(self, text="Channel", bg='#3c3f41', fg='#bbbbbb', font=('Helvetica', '15'), anchor=W,
                       justify=LEFT)
        label4.place(relheight=0.05, width=100, relx=0.05, rely=0.55)
        # Dropdown for channels
        channels = StringVar()
        channels.set(self.active_channel)  # default value
        channels_menu = OptionMenu(self, channels, *self.channel_options, command=self.channel_menu_callback)
        channels_menu["highlightthickness"] = 0
        channels_menu["menu"].config(bg='#4e5254', fg='#bbbbbb', font=('Helvetica', '15'))
        channels_menu.config(bg='#4e5254', fg='#bbbbbb', font=('Helvetica', '15'))
        channels_menu.place(relheight=0.05, relwidth=0.1, relx=0.05, rely=0.65, anchor=W)

        # Create Record button
        record_button = Button(self, command=self.record_button_callback, text="Record", bg='#4e5254', fg='#bbbbbb',
                               font=('Helvetica', '15'))
        record_button.place(relheight=0.1, relwidth=0.1, relx=0.1, rely=0.75)

    def get_task(self):
        name = self.active_module+"/"+self.active_channel
        print(name)
        task = nidaqmx.Task()
        task.ai_channels.add_ai_voltage_chan(name)
        task.timing.cfg_samp_clk_timing(rate=self.sf)
        task.ai_channels[name].ai_excit_src = nidaqmx.constants.ExcitationSource.INTERNAL
        task.ai_channels[
            name].ai_excit_voltage_or_current = nidaqmx.constants.ExcitationVoltageOrCurrent.USE_CURRENT
        task.ai_channels[name].ai_coupling = nidaqmx.constants.Coupling.AC
        task.ai_channels[name].ai_excit_val = 0.002
        # task.ai_channels["cDAQ1Mod1/ai0"].ai_accel_sensitivity_units = nidaqmx.constants.AccelSensitivityUnits.M_VOLTS_PER_G
        # task.ai_channels["cDAQ1Mod1/ai0"].ai_accel_sensitivity = 101.3
        return task

    def get_modules(self):
        system = nidaqmx.system.System.local()
        modules = []
        for device in system.devices:
            modules.append(device.name)
        self.module_options = modules[1:]
        return True


    def calc_fft(self, data):
        data = np.array(data)
        # FFT
        sp = np.fft.rfft(data, n=data.shape[-1])
        freq = np.fft.rfftfreq(n=data.shape[-1], d=1/self.sf)
        return freq, np.abs(sp.real)/self.samples

    def sensors(self, i):
        data = self.task.read(number_of_samples_per_channel=self.samples)
        # x = np.linspace(0, samples * (1 / sf), num=samples)
        # data = 0.15*np.sin(2*np.pi*500*x+np.random.random(1))
        self.line.set_ydata(data)
        freq, sp = self.calc_fft(data)
        self.markerline.set_ydata(sp)
        seg = self.stemlines.get_segments()
        for i, x in enumerate(seg):
            x[1][1] = sp[i]
        self.stemlines.set_segments(segments=seg)
        return self.line, self.markerline

    def entry1_callback(self):
        # Update sampling frequency
        self.sf = int(self.sv1.get())
        # Refresh task
        self.task.close()
        self.task = self.get_task()
        # Refresh axes
        self.update_fig()
        return True

    def entry2_callback(self):
        # Update sample number
        self.samples = int(self.sv2.get())
        # Refresh task
        self.task.close()
        self.task = self.get_task()
        # Refresh axes
        self.update_fig()
        return True

    def module_menu_callback(self, module):
        self.task.close()
        self.active_module = module
        self.task = self.get_task()
        return True

    def channel_menu_callback(self, channel):
        self.task.close()
        self.active_channel = channel
        self.task = self.get_task()
        return True

    def update_fig(self):
        # Clear axes
        self.ax1.clear()
        self.ax2.clear()
        # Refresh time axes
        t = np.linspace(0, self.samples * (1 / self.sf), num=self.samples)
        data = self.task.read(number_of_samples_per_channel=self.samples)
        self.line, = self.ax1.plot(t, data, color="lime")
        # Refresh freq axes
        freq, sp = self.calc_fft(data)
        self.markerline, self.stemlines, _ = self.ax2.stem(freq, sp, basefmt=" ", use_line_collection=True)
        self.ax1.set_ylim([-0.16, 0.16])
        self.ax1.set_ylabel('Voltage in V')
        self.ax1.set_xlabel('Time in s')
        self.ax2.set_ylim([-0.01, 0.16])
        self.ax2.set_ylabel("Spectrum")
        self.ax2.set_xlabel("Frequency in Hz")

    def record_button_callback(self):
        data = [1, 2, 3, 4, 5]
        t = datetime.datetime.now()
        np.savetxt(t.strftime('%Y%m%d_%H%M%S%f') + ".csv", data, delimiter=",")
        return True

    def on_closing(self):
        # Close task to avoid error
        self.task.close()
        # Destroy window
        root.destroy()



root = Tk()
root.iconbitmap("freq.ico")
root.geometry("1000x600")
app = Window(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
app.configure(background="#3c3f41")
root.mainloop()
