from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename

from GenerateFs import generate_fs

def main():
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
        #window.geometry("500x300")
        
        return window
    
    def generate_fs_window():
        window = Toplevel(root)
        window.title("Generate frequency spectrum")
        
        frm = Frame(window)
        frm_sample_size = Frame(frm)
        pop_ids = []
        sample_size_entries = []
        
        def select_vcf_file():
            file_name = askopenfilename(
                parent=window,
                filetypes=[("GZcompressed VCF Files", "*.vcf.gz"), ("VCF Files", "*.vcf"), ("All Files", "*.*")]
            )
            if not file_name:
                return
            
            lbl_vcf['text'] = file_name
            
            return file_name
        
        def select_pop_info():
            file_name = askopenfilename(
                parent=window,
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if not file_name:
                return
            
            lbl_pop_info['text'] = file_name
            
            pops = {}
            f = open(file_name, 'r')
            for line in f:
                elm = line.rstrip().split()
                pops[elm[1]] = 1
            f.close()
            i = 0
            for p in pops:
                pop_ids.append(p)
                lbl = Label(frm_sample_size, text=p)
                ent = Entry(frm_sample_size, width=10)
                i += 1
                lbl.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
                i += 1
                ent.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
                sample_size_entries.append(ent)
            
            return file_name
        
        def output_file():
            file_name = asksaveasfilename(
                parent=window,
                defaultextension="fs",
                filetypes=[("Frequency Spectrum Files", "*.fs"), ("All Files", "*.*")],
            )
            if not file_name:
                return
            
            lbl_output['text'] = file_name
            return file_name
        
        def run_generate_fs():
            if is_unfolded.get() == 1: is_polarized = True
            else: is_polarized = False
            sample_sizes = []
            for e in sample_size_entries:
                sample_sizes.append(int(e.get()))
                
            generate_fs(
                vcf=lbl_vcf['text'], 
                output=lbl_output['text'], 
                pop_ids=pop_ids, 
                pop_info=lbl_pop_info['text'], 
                projections=sample_sizes, 
                polarized=is_polarized, 
                bootstrap=None, chunk_size=0)
        
        btn_select_vcf = Button(frm, text="Select a VCF file", command=select_vcf_file)
        btn_select_pop_info = Button(frm, text="Select a Pop Info file", command=select_pop_info)
        btn_select_output = Button(frm, text="Save as", command=output_file)
        btn_generate = Button(frm, text="Generate", command=run_generate_fs)
        
        lbl_vcf = Label(frm, text="No VCF file selected")
        lbl_pop_info = Label(frm, text="No Pop Info file selected")
        lbl_output = Label(frm, text="No output file")
        lbl_projections = Label(frm, text="Sample sizes (chromosomes)")
        
        is_unfolded = IntVar()
        cbt_unfolded = Checkbutton(frm, text="Unfolded", variable=is_unfolded)
        
        btn_select_vcf.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_select_pop_info.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        btn_select_output.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        btn_generate.grid(row=5, column=2, sticky="ew", padx=5, pady=5)
        
        lbl_vcf.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        lbl_pop_info.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        lbl_output.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        lbl_projections.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        
        cbt_unfolded.grid(row=3, column=0, sticky="n", padx=5, pady=5)
        
        frm_sample_size.grid(row=4, column=1, sticky="ns")
        frm.grid(row=0, column=0, sticky="ns")
    
    def infer_dm_window():
        window = create_new_window("Infer demographic models")

    def generate_cache_window():
        window = create_new_window("Generate cache for DFE inference")

    def infer_dfe_window():
        window = create_new_window("Infer DFEs")

    def analyze_uncerts_window():
        window = create_new_window("Analyze uncertainty")

    def make_plots_window():
        window = create_new_window("Make plots")

    # create a menu for analysis
    menu_analysis = Menu(menubar)
    menu_analysis.add_command(label="Generate frequency spectrum", command=generate_fs_window)
    menu_analysis.add_command(label="Infer demographic models", command=infer_dm_window)
    menu_analysis.add_command(label="Generate cache for DFE inference", command=generate_cache_window)
    menu_analysis.add_command(label="Infer DFEs", command=infer_dfe_window)
    menu_analysis.add_command(label="Analyze uncertainty", command=analyze_uncerts_window)
    menu_analysis.add_command(label="Make plots", command=make_plots_window)
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