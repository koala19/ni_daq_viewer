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
        def get_task(sf):
            task = nidaqmx.Task()
            task.ai_channels.add_ai_voltage_chan("cDAQ1Mod1/ai0")
            task.timing.cfg_samp_clk_timing(rate=sf)
            task.ai_channels["cDAQ1Mod1/ai0"].ai_excit_src = nidaqmx.constants.ExcitationSource.INTERNAL
            task.ai_channels[
                "cDAQ1Mod1/ai0"].ai_excit_voltage_or_current = nidaqmx.constants.ExcitationVoltageOrCurrent.USE_CURRENT
            task.ai_channels["cDAQ1Mod1/ai0"].ai_coupling = nidaqmx.constants.Coupling.AC
            task.ai_channels["cDAQ1Mod1/ai0"].ai_excit_val = 0.002
            # task.ai_channels["cDAQ1Mod1/ai0"].ai_accel_sensitivity_units = nidaqmx.constants.AccelSensitivityUnits.M_VOLTS_PER_G
            # task.ai_channels["cDAQ1Mod1/ai0"].ai_accel_sensitivity = 101.3
            return task

        def sensors(i, task, samples, sf):
            #data = task.read(number_of_samples_per_channel=samples)
            x = np.linspace(0, samples * (1 / sf), num=samples)
            data = 0.15*np.sin(2*np.pi*500*x+np.random.random(1))
            self.line.set_ydata(data)
            freq, sp = calc_fft(data, self.sf)
            self.markerline.set_ydata(sp)

            seg = self.stemlines.get_segments()
            for i, x in enumerate(seg):
                x[1][1] = sp[i]
            self.stemlines.set_segments(segments=seg)
            return self.line, self.markerline

        def calc_fft(data, sf):
            #
            data = np.array(data)
            # FFT
            sp = np.fft.rfft(data)
            freq = np.fft.rfftfreq(n=data.shape[-1], d=1 / sf)
            return freq, np.abs(sp.real)

        def entry1_callback():
            self.sf = int(sv.get())
            #self.task = get_task(sf=self.sf)
            return True

        def record_button_callback():
            data = [1, 2, 3, 4, 5]
            t = datetime.datetime.now()
            np.savetxt(t.strftime('%Y%m%d_%H%M%S%f')+".csv", data, delimiter=",")
            return True

        # changing the title of our master widget
        self.master.title("NI-DAQmx Viewer")
        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)
        self.samples = 400
        self.sf = 5000
        # self.task = get_task(sf=self.sf)
        self.task = None
        self.fig = plt.Figure(figsize=(6, 3))
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        self.ax1.set_ylim([-0.16, 0.16])
        self.ax1.set_ylabel('Voltage in V')
        self.ax1.set_xlabel('Time in s')
        self.ax2.set_ylim([-1, 20])
        self.ax2.set_ylabel("Spectrum")
        self.ax2.set_xlabel("Frequency in Hz")
        # data = self.task.read(number_of_samples_per_channel=100)
        data = 0.30*np.random.random(self.samples)-0.15
        t = np.linspace(0, self.samples * (1 / self.sf), num=self.samples)
        self.line, = self.ax1.plot(t, data, color="lime")
        freq, sp = calc_fft(data, self.sf)
        self.markerline, self.stemlines, _ = self.ax2.stem(freq, sp, basefmt=" ", use_line_collection=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().place(relheight=1,relwidth=0.7, relx=0.25, rely=0)
        self.ani = animation.FuncAnimation(self.fig, sensors, interval=10, blit=False,
                                           fargs=(self.task, self.samples, self.sf,))

        # Build Settings List
        sv = StringVar()
        label1 = Label(self, text="Sampling frequency", bg='#3c3f41', fg='#bbbbbb', font=('Helvetica', '15'), anchor=W,
                       justify=LEFT)
        label1.place(relheight=0.05, width=200, relx=0.05, rely=0.1)
        entry1 = Entry(textvariable=sv, validate="focusout", validatecommand=entry1_callback, bg='#4e5254',
                       fg='#bbbbbb', font=('Helvetica', '15'))
        entry1.place(relheight=0.05, width=100, relx=0.05, rely=0.2, anchor=W)
        entry1.delete(0, END)
        entry1.insert(0, 5000)

        label2 = Label(self, text="Sample number", bg='#3c3f41', fg='#bbbbbb', font=('Helvetica', '15'), anchor=W,
                       justify=LEFT)
        label2.place(relheight=0.05, width=150, relx=0.05, rely=0.25)
        entry2 = Entry(bg='#4e5254', fg='#bbbbbb', font=('Helvetica', '15'))
        entry2.place(relheight=0.05, width=100, relx=0.05, rely=0.35, anchor=W)
        entry2.delete(0, END)
        entry2.insert(0, 100)

        label3 = Label(self, text="Module", bg='#3c3f41', fg='#bbbbbb', font=('Helvetica', '15'), anchor=W,
                       justify=LEFT)
        label3.place(relheight=0.05, width=100, relx=0.05, rely=0.4)
        modules = StringVar()
        modules_options = ["cDAQ1Mod1", "cDAQ1Mod2", "cDAQ1Mod3", "cDAQ1Mod4"]
        modules.set(modules_options[0])  # default value
        modules_menu = OptionMenu(self, modules, *modules_options)
        modules_menu["highlightthickness"] = 0
        modules_menu["menu"].config(bg='#4e5254', fg='#bbbbbb', font=('Helvetica', '15'))
        modules_menu.config(bg='#4e5254', fg='#bbbbbb', font=('Helvetica', '15'))
        modules_menu.place(relheight=0.05, width=200, relx=0.05, rely=0.5, anchor=W)

        label4 = Label(self, text="Channel", bg='#3c3f41', fg='#bbbbbb', font=('Helvetica', '15'), anchor=W,
                       justify=LEFT)
        label4.place(relheight=0.05, width=100, relx=0.05, rely=0.55)
        channels = StringVar()
        channel_options = ["ai0", "ai1", "ai2"]
        channels.set(channel_options[0])  # default value
        channels_menu = OptionMenu(self, channels, *channel_options)
        channels_menu["highlightthickness"] = 0
        channels_menu["menu"].config(bg='#4e5254', fg='#bbbbbb', font=('Helvetica', '15'))
        channels_menu.config(bg='#4e5254', fg='#bbbbbb', font=('Helvetica', '15'))
        channels_menu.place(relheight=0.05, relwidth=0.1, relx=0.05, rely=0.65, anchor=W)

        # Create Record button
        record_button = Button(self, command=record_button_callback, text="Record", bg='#4e5254', fg='#bbbbbb',
                               font=('Helvetica', '15'))
        record_button.place(relheight=0.1, relwidth=0.1, relx=0.1, rely=0.75)


root = Tk()
root.iconbitmap('freq.ico')
root.geometry("1000x600")
app = Window(root)
app.configure(background="#3c3f41")
root.mainloop()
