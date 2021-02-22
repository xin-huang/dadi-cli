from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
from PIL import Image, ImageTk

from GenerateFs import generate_fs
from Models import get_dadi_model_params

import subprocess
import threading

class analysis_window:
    # window template for different analysis
    def __init__(self, master, title):
        self.window = Toplevel(master)
        self.window.title(title)

class generate_fs_window(analysis_window):
    def __init__(self, master):
        analysis_window.__init__(self, master, "Generate frequency spectrum")
        
        self.frm = Frame(self.window)
        self.frm_sample_size = Frame(self.frm)
        self.params_labels = []
        self.params_entries = []
        self.pop_ids = []
        
        def select_vcf_file():
            file_name = askopenfilename(
                parent=self.window,
                filetypes=[("GZcompressed VCF Files", "*.vcf.gz"), ("VCF Files", "*.vcf"), ("All Files", "*.*")]
            )
            if not file_name: return
            
            self.lbl_vcf['text'] = file_name
        
        def select_pop_info():       
            self.pop_ids = []
            for lbl in self.params_labels: lbl.destroy()
            for ent in self.params_entries: ent.destroy()
            
            file_name = askopenfilename(
                parent=self.window,
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if not file_name: return
            
            self.lbl_pop_info['text'] = file_name
            
            pops = {}
            f = open(file_name, 'r')
            for line in f:
                elm = line.rstrip().split()
                pops[elm[1]] = 1
            f.close()
            i = 0
            for p in pops:
                self.pop_ids.append(p)
                lbl = Label(self.frm_sample_size, text=p)
                ent = Entry(self.frm_sample_size, width=10)
                
                self.params_labels.append(lbl)
                self.params_entries.append(ent)

                lbl.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
                i += 1
                ent.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
                i += 1
        
        def output_file():
            file_name = asksaveasfilename(
                parent=self.window,
                defaultextension="fs",
                filetypes=[("Frequency Spectrum Files", "*.fs"), ("All Files", "*.*")],
            )
            if not file_name: return
            
            self.lbl_output['text'] = file_name
        
        def run_generate_fs():
            if self.is_unfolded.get() == 1: is_polarized = True
            else: is_polarized = False
            sample_sizes = []
            for e in self.params_entries:
                sample_sizes.append(int(e.get()))
                
            #generate_fs(
            #    vcf=self.lbl_vcf['text'], 
            #    output=self.lbl_output['text'], 
            #    pop_ids=self.pop_ids, 
            #    pop_info=self.lbl_pop_info['text'], 
            #    projections=sample_sizes, 
            #    polarized=is_polarized, 
            #    bootstrap=None, chunk_size=0)
            t = threading.Thread(target=generate_fs, args=(self.lbl_vcf['text'], self.lbl_output['text'], self.pop_ids, self.lbl_pop_info['text'], sample_sizes, is_polarized, None, 0))
            t.start()
        
        self.btn_select_vcf = Button(self.frm, text="Select a VCF file", command=select_vcf_file)
        self.btn_select_pop_info = Button(self.frm, text="Select a Pop Info file", command=select_pop_info)
        self.btn_select_output = Button(self.frm, text="Save as", command=output_file)
        self.btn_generate = Button(self.frm, width=10, text="Submit", command=run_generate_fs)
        
        self.lbl_vcf = Label(self.frm, text="No VCF file selected")
        self.lbl_pop_info = Label(self.frm, text="No Pop Info file selected")
        self.lbl_output = Label(self.frm, text="No output file selected")
        self.lbl_projections = Label(self.frm, text="Sample sizes (chromosomes)")
        
        self.is_unfolded = IntVar()
        self.cbt_unfolded = Checkbutton(self.frm, text="Unfolded", variable=self.is_unfolded)
        
        self.btn_select_vcf.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_select_pop_info.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.btn_select_output.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.btn_generate.grid(row=5, column=2, sticky="ew", padx=5, pady=5)
        
        self.lbl_vcf.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.lbl_pop_info.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.lbl_output.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.lbl_projections.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        
        self.cbt_unfolded.grid(row=3, column=0, sticky="n", padx=5, pady=5)
        
        self.frm_sample_size.grid(row=4, column=1, sticky="ns")
        self.frm.grid(row=0, column=0, sticky="ns")

class infer_dm_window(analysis_window):
    def __init__(self, master):
        analysis_window.__init__(self, master, "Infer demographic models")
        
        self.frm = Frame(self.window)
        self.frm_initial_values = Frame(self.frm)
        self.frm_upper_bounds = Frame(self.frm)
        self.frm_lower_bounds = Frame(self.frm)
        self.frm_fixed_params = Frame(self.frm)
        self.params_labels = []
        self.params_entries = []
        self.params_checkboxes = []
        
        def select_fs_file():
            file_name = askopenfilename(
                parent=self.window,
                filetypes=[("Frequency Spectrum Files", "*.fs"), ("All Files", "*.*")]
            )
            if not file_name: return
            
            self.lbl_fs['text'] = file_name
        
        def select_output_dir():
            file_dir = askdirectory(parent=self.window)
            
            if not file_dir: return
            
            self.lbl_output_dir['text'] = file_dir
        
        def run_infer_dm():
            return
        
        self.btn_select_fs = Button(self.frm, text="Select a frequency spectrum file", command=select_fs_file)
        self.lbl_fs = Label(self.frm, text="No frequency spectrum file selected")   
        self.btn_select_fs.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_fs.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        self.btn_select_output_dir = Button(self.frm, text="Select a output directory", command=select_output_dir)
        self.lbl_output_dir = Label(self.frm, text="No output directory selected")
        self.btn_select_output_dir.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_output_dir.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        self.lbl_output_file_prefix = Label(self.frm, text="Output file prefix")
        self.ent_output_file = Entry(self.frm, width=50)
        self.lbl_output_file_prefix.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.ent_output_file.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        self.lbl_model = Label(self.frm, text="Select a demographic model")
        self.cbb_models = ttk.Combobox(self.frm)
        self.cbb_models['values'] = (
            'bottlegrowth_1d',
            'growth_1d',
            'snm_1d',
            'three_epoch_1d',
            'two_epoch_1d',
            'bottlegrowth_2d',
            'bottlegrowth_split',
            'bottlegrowth_split_mig',
            'IM',
            'IM_pre',
            'split_mig',
            'split_asym_mig',
            'snm_2d'
        )
        self.cbb_models.state(["readonly"])
        
        def select_models(event):
            
            for lbl in self.params_labels: lbl.destroy()
            for ent in self.params_entries: ent.destroy()
            for cbt in self.params_checkboxes: cbt.destroy()
            
            params = get_dadi_model_params(self.cbb_models.get())
            i = 0
            for p in params:
                lbl1 = Label(self.frm_initial_values, text=p)
                lbl2 = Label(self.frm_upper_bounds, text=p)
                lbl3 = Label(self.frm_lower_bounds, text=p)
                self.params_labels.append(lbl1)
                self.params_labels.append(lbl2)
                self.params_labels.append(lbl3)
                
                ent1 = Entry(self.frm_initial_values, width=10)
                ent2 = Entry(self.frm_upper_bounds, width=10)
                ent3 = Entry(self.frm_lower_bounds, width=10)
                self.params_entries.append(ent1)
                self.params_entries.append(ent2)
                self.params_entries.append(ent3)
                
                cbt = Checkbutton(self.frm_fixed_params, text=p)
                self.params_checkboxes.append(cbt)
                
                lbl1.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
                lbl2.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
                lbl3.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
                cbt.grid(row=0, column=i, sticky="n", padx=5, pady=5)
                i += 1
                ent1.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
                ent2.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
                ent3.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
                i += 1
            
        self.cbb_models.bind('<<ComboboxSelected>>', select_models)
        
        self.lbl_model.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.cbb_models.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        self.cbt_misid = Checkbutton(self.frm, text="Add misidentification")
        self.cbt_misid.grid(row=4, column=0, sticky="n", padx=5, pady=5)
        
        self.lbl_initial_values = Label(self.frm, text="Initial values")
        self.lbl_upper_bounds = Label(self.frm, text="Upper bounds")
        self.lbl_lower_bounds = Label(self.frm, text="Lower bounds")
        self.lbl_fixed_params = Label(self.frm, text="Fixed parameters")
        self.lbl_parallel_jobs = Label(self.frm, text="Parallel jobs")
        self.lbl_initial_values.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_upper_bounds.grid(row=6, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_lower_bounds.grid(row=7, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_fixed_params.grid(row=8, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_parallel_jobs.grid(row=9, column=0, sticky="ew", padx=5, pady=5)
        
        self.ent_parallel_jobs = Entry(self.frm, width=20)
        self.ent_parallel_jobs.grid(row=9, column=1, sticky="ew", padx=5, pady=5)
        
        self.btn_infer = Button(self.frm, width=10, text="Submit", command=run_infer_dm)
        self.btn_infer.grid(row=10, column=2, sticky="ew", padx=5, pady=5)
        
        self.frm_initial_values.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        self.frm_upper_bounds.grid(row=6, column=1, sticky="ew", padx=5, pady=5)
        self.frm_lower_bounds.grid(row=7, column=1, sticky="ew", padx=5, pady=5)
        self.frm_fixed_params.grid(row=8, column=1, sticky="ew", padx=5, pady=5)
        self.frm.grid(row=0, column=0, sticky="ns")

class plot_a_frequency_spectrum_window(analysis_window):
    def __init__(self, master):
        analysis_window.__init__(self, master, "Make plots")
        self.set_window_title("Make plot - Plot a frequency spectrum")
        
        self.frm = Frame(self.window)
        
        self.lbl_fs = Label(self.frm, text="No frequency spectrum file selected")
        self.btn_select_fs = Button(self.frm, text="Select a frequency spectrum file", command=self.select_fs_file)
        self.btn_select_fs.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_fs.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        self.lbl_output = Label(self.frm, text="No output file selected")
        self.btn_select_output = Button(self.frm, text="Save as", command=self.output_file)
        self.btn_select_output.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_output.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        self.btn_plot = Button(self.frm, width=10, text="Plot", command=self.run_make_plots)
        self.btn_plot.grid(row=100, column=2, sticky="ew", padx=5, pady=5)
        
        self.frm.grid(row=0, column=0, sticky="ns")
        
    def set_window_title(self, title):
        self.window.title(title)
        
    def select_fs_file(self):
        file_name = askopenfilename(
            parent=self.window,
            filetypes=[("Frequency Spectrum Files", "*.fs"), ("All Files", "*.*")]
        )
        if not file_name: return
            
        self.lbl_fs['text'] = file_name
        
    def output_file(self):
        file_name = asksaveasfilename(
            parent=self.window,
            defaultextension="pdf",
            filetypes=[("Portable Network Graphics", "*.png"), ("Portable Document Format", "*.pdf"), ("All Files", "*.*")],
        )
        if not file_name: return
            
        self.lbl_output['text'] = file_name
        
    def run_make_plots(self):
        self.run_dadi_cli_command()
            
        load = Image.open(self.lbl_output['text'])
        render = ImageTk.PhotoImage(load)
        img = Label(self.frm, image=render)
        img.image = render
        img.grid(row=99, column=1)
        
    def run_dadi_cli_command(self):
        subprocess.run(["dadi-cli", "Plot", "--fs", self.lbl_fs['text'], "--output", self.lbl_output['text']])
        
class compare_two_frequency_spectra_window(plot_a_frequency_spectrum_window):
    def __init__(self, master):
        plot_a_frequency_spectrum_window.__init__(self, master)
        self.set_window_title("Make plot - Compare two frequency spectra")

        self.lbl_ant_fs = Label(self.frm, text="No frequency spectrum file selected")   
        self.btn_select_ant_fs = Button(self.frm, text="Select another frequency spectrum file", command=self.select_ant_fs_file)
        self.btn_select_ant_fs.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_ant_fs.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
    def select_ant_fs_file(self):
        file_name = askopenfilename(
            parent=self.window,
            filetypes=[("Frequency Spectrum Files", "*.fs"), ("All Files", "*.*")]
        )
        if not file_name: return
            
        self.lbl_ant_fs['text'] = file_name
        
    def run_dadi_cli_command(self):
        subprocess.run(["dadi-cli", "Plot", "--fs", self.lbl_fs['text'], "--fs2", self.lbl_ant_fs['text'], "--output", self.lbl_output['text']])

class compare_frequency_with_dm_window(plot_a_frequency_spectrum_window):
    def __init__(self, master):
        plot_a_frequency_spectrum_window.__init__(self, master)
        self.set_window_title("Make plot - Compare a frequency spectrum with a demographic model")
        
        self.params_labels = []
        self.params_entries = []
        
        self.lbl_model = Label(self.frm, text="Select a demographic model")
        self.cbb_models = ttk.Combobox(self.frm)
        self.cbb_models['values'] = (
            'bottlegrowth_1d',
            'growth_1d',
            'snm_1d',
            'three_epoch_1d',
            'two_epoch_1d',
            'bottlegrowth_2d',
            'bottlegrowth_split',
            'bottlegrowth_split_mig',
            'IM',
            'IM_pre',
            'split_mig',
            'split_asym_mig',
            'snm_2d'
        )
        self.cbb_models.state(["readonly"])
        self.cbb_models.bind('<<ComboboxSelected>>', self.select_models)
        
        self.lbl_model.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        self.cbb_models.grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        self.demo_params = Label(self.frm, text="Demographic model parameters")
        self.frm_demo_params = Frame(self.frm)
        
        self.demo_params.grid(row=6, column=0, sticky="ew", padx=5, pady=5)
        self.frm_demo_params.grid(row=6, column=1, sticky="ew", padx=5, pady=5)
                
        self.cbt_misid = Checkbutton(self.frm, text="Add misidentification")
        self.cbt_misid.grid(row=7, column=0, sticky="n", padx=5, pady=5)
        
    def select_models(self, event):
            
        for lbl in self.params_labels: lbl.destroy()
        for ent in self.params_entries: ent.destroy()
            
        params = get_dadi_model_params(self.cbb_models.get())
        params.append('theta')
        i = 0
        for p in params:
            lbl = Label(self.frm_demo_params, text=p)
            self.params_labels.append(lbl)
                
            ent = Entry(self.frm_demo_params, width=10)
            self.params_entries.append(lbl)
                
            lbl.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
            i += 1
            ent.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
            i += 1
        
class compare_frequency_with_dfe_window(compare_frequency_with_dm_window):
    def __init__(self, master):
        compare_frequency_with_dm_window.__init__(self, master)
        self.set_window_title("Make plot - Compare a frequency spectrum with a DFE model")
        
        self.lbl_cache = Label(self.frm, text="No cache file selected")   
        self.btn_select_cache = Button(self.frm, text="Select a 1D/2D cache file", command=self.select_cache_file)
        self.btn_select_cache.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_cache.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        self.lbl_pdfs = Label(self.frm, text="Select a DFE distribution")
        self.cbb_pdfs = ttk.Combobox(self.frm)
        self.cbb_pdfs['values'] = (
            'beta',
            'biv_ind_gamma',
            'biv_lognormal',
            'exponential',
            'gamma',
            'lognormal',
            'normal'
        )
        self.cbb_pdfs.state(["readonly"])
        self.cbb_pdfs.bind('<<ComboboxSelected>>', self.select_pdfs)
        
        self.lbl_pdfs.grid(row=8, column=0, sticky="ew", padx=5, pady=5)
        self.cbb_pdfs.grid(row=8, column=1, sticky="ew", padx=5, pady=5)
        
    def select_cache_file(self):
        return
    
    def select_pdfs(self, event):
        return
        
class compare_frequency_with_joint_dfe_window(compare_frequency_with_dfe_window):
    def __init__(self, master):
        compare_frequency_with_dfe_window.__init__(self, master)
        self.set_window_title("Make plot - Compare a frequency spectrum with a joint DFE model")
        
        self.lbl_cache['text'] = "No 1D cache file selected"
        self.btn_select_cache['text'] = "Select a 1D cache file"
        
        self.lbl_ant_cache = Label(self.frm, text="No 2D cache file selected")   
        self.btn_select_ant_cache = Button(self.frm, text="Select a 2D cache file", command=self.select_ant_cache_file)
        self.btn_select_ant_cache.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_ant_cache.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        self.lbl_pdfs['text'] = "Select a 1D DFE distribution"
        self.cbb_pdfs['values'] = (
            'gamma',
            'lognormal'
        )
        
        self.lbl_2d_pdfs = Label(self.frm, text="Select a 2D DFE distribution")
        self.cbb_2d_pdfs = ttk.Combobox(self.frm)
        self.cbb_2d_pdfs['values'] = (
            'biv_ind_gamma',
            'biv_lognormal',
        )
        self.cbb_2d_pdfs.state(["readonly"])
        self.cbb_2d_pdfs.bind('<<ComboboxSelected>>', self.select_2d_pdfs)
        
        self.lbl_2d_pdfs.grid(row=9, column=0, sticky="ew", padx=5, pady=5)
        self.cbb_2d_pdfs.grid(row=9, column=1, sticky="ew", padx=5, pady=5)

    def select_ant_cache_file(self):
        return
    
    def select_2d_pdfs(self, event):
        return
        
def main():
    # create the root window
    root = Tk()
    root.title("Diffusion Approximation for Demographic Inference")
    root.geometry("500x250")
    root.rowconfigure(0, minsize=800, weight=1)
    root.columnconfigure(1, minsize=800, weight=1)
    root.resizable(width=True, height=True)
    root.option_add('*tearOff', False)

    # create a menubar
    menubar = Menu(root)
    
    # create commands for different analysis
    def create_new_window(title):
        window = Toplevel(root)
        window.title(title)
        
        return window
    
    def create_generate_fs_window():
        generate_fs_window(root)
        
    def create_infer_dm_window():
        infer_dm_window(root)

    def generate_cache_window():
        window = create_new_window("Generate cache for DFE inference")

    def infer_dfe_window():
        window = create_new_window("Infer DFEs")

    def analyze_uncerts_window():
        window = create_new_window("Analyze uncertainty")

    def create_plot_a_frequency_spectrum_window():
        plot_a_frequency_spectrum_window(root)
        
    def create_compare_two_frequency_spectra_window():
        compare_two_frequency_spectra_window(root)
        
    def create_compare_frequency_with_dm_window():
        compare_frequency_with_dm_window(root)
        
    def create_compare_frequency_with_dfe_window():
        compare_frequency_with_dfe_window(root)
        
    def create_compare_frequency_with_joint_dfe_window():
        compare_frequency_with_joint_dfe_window(root)

    # create a menu for analysis
    menu_analysis = Menu(menubar)
    menu_make_plots = Menu(menubar)
    
    menu_analysis.add_command(label="Generate frequency spectrum", command=create_generate_fs_window)
    menu_analysis.add_command(label="Infer demographic models", command=create_infer_dm_window)
    menu_analysis.add_command(label="Generate cache for DFE inference", command=generate_cache_window)
    menu_analysis.add_command(label="Infer DFEs", command=infer_dfe_window)
    menu_analysis.add_command(label="Analyze uncertainty", command=analyze_uncerts_window)
    menu_analysis.add_cascade(label="Make plots", menu=menu_make_plots)
    
    menu_make_plots.add_command(label="Plot a frequency spectrum", command=create_plot_a_frequency_spectrum_window)
    menu_make_plots.add_command(label="Compare two frequency spectra", command=create_compare_two_frequency_spectra_window)
    menu_make_plots.add_command(label="Compare a frequency spectrum with a demographic model", command=create_compare_frequency_with_dm_window)
    menu_make_plots.add_command(label="Compare a frequency spectrum with a DFE model", command=create_compare_frequency_with_dfe_window)
    menu_make_plots.add_command(label="Compare a frequency spectrum with a joint DFE model", command=create_compare_frequency_with_joint_dfe_window)
    
    menubar.add_cascade(menu=menu_analysis, label='Analysis')

    # create a menu for help
    menu_help = Menu(menubar)
    
    menu_help.add_command(label="Manual")
    menu_help.add_command(label="Google group")
    menu_help.add_command(label="About")
    menubar.add_cascade(menu=menu_help, label='Help')

    root['menu'] = menubar

    root.mainloop()
    
if __name__ == '__main__':
    main()