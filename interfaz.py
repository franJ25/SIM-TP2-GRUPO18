import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from aleatorios import *


class RandomGenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de númmeros aleatorios - TP2 SIM - Grupo 18")
        self.geometry("1000x750")

        self.dist_type = tk.StringVar(value="Uniforme")
        self.sample_size_var = tk.StringVar(value="100")
        self.param1_var = tk.StringVar(value="0")
        self.param2_var = tk.StringVar(value="1")
        self.num_bins_var = tk.IntVar(value=10)
        self.generated_data = None

        self.columnconfigure(0, weight=1, minsize=250)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=2)
        self.rowconfigure(3, weight=3)

        self.controls_frame = ttk.Frame(self, padding="10")
        self.controls_frame.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=5, pady=5)

        self.data_display_frame = ttk.Frame(self, padding="5")
        self.data_display_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.table_view_frame = ttk.Frame(self, padding="5")
        self.table_view_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        self.table_view_frame.columnconfigure(0, weight=1)
        self.table_view_frame.rowconfigure(0, weight=1)

        self.plot_frame = ttk.Frame(self, padding="5")
        self.plot_frame.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)

        self._create_control_widgets()
        self._create_display_widgets()
        self._update_parameter_fields()

        style = ttk.Style(self)
        try:
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif 'vista' in available_themes:
                style.theme_use('vista')
            style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
            style.configure("Accent.TButton", font=("Arial", 10, "bold"), padding=5)
            style.configure("Treeview", rowheight=22, font=("Arial", 9))
            style.map("Treeview", background=[('selected', '#0078D7')])
        except Exception as e:
            print(f"No se pudo aplicar el tema TTK: {e}")

    def _create_control_widgets(self):
        frame = self.controls_frame
        row_idx = 0
        ttk.Label(frame, text="Parámetros", font=("Arial", 14, "bold")).grid(row=row_idx, column=0, columnspan=2,
                                                                             pady=(0, 10))
        row_idx += 1
        ttk.Label(frame, text="Distribución:").grid(row=row_idx, column=0, sticky="w", pady=2)
        dist_options = ["Uniforme", "Exponencial", "Normal"]
        dist_combo = ttk.Combobox(frame, textvariable=self.dist_type, values=dist_options, state="readonly", width=15)
        dist_combo.grid(row=row_idx, column=1, sticky="ew", pady=2)
        dist_combo.bind("<<ComboboxSelected>>", self._update_parameter_fields)
        row_idx += 1
        ttk.Label(frame, text="Tamaño Muestra (N):").grid(row=row_idx, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=self.sample_size_var, width=17).grid(row=row_idx, column=1, sticky="ew", pady=2)
        row_idx += 1
        self.param_frame = ttk.Frame(frame)
        self.param_frame.grid(row=row_idx, column=0, columnspan=2, sticky="nsew", pady=5)
        self.param_frame.columnconfigure(1, weight=1)
        self.param1_label = ttk.Label(self.param_frame, text="Parámetro 1:")
        self.param1_entry = ttk.Entry(self.param_frame, textvariable=self.param1_var, width=10)
        self.param2_label = ttk.Label(self.param_frame, text="Parámetro 2:")
        self.param2_entry = ttk.Entry(self.param_frame, textvariable=self.param2_var, width=10)
        row_idx += 1
        ttk.Label(frame, text="Intervalos Histograma:").grid(row=row_idx, column=0, sticky="w", pady=2)
        bin_options = [10, 15, 20, 25]
        bin_combo = ttk.Combobox(frame, textvariable=self.num_bins_var, values=bin_options, state="readonly", width=15)
        bin_combo.grid(row=row_idx, column=1, sticky="ew", pady=2)
        row_idx += 1
        ttk.Button(frame, text="Generar", command=self.generate_and_display, style="Accent.TButton").grid(row=row_idx,
                                                                                                          column=0,
                                                                                                          columnspan=2,
                                                                                                          pady=15)
        row_idx += 1

    def _update_parameter_fields(self, event=None):
        dist = self.dist_type.get()
        for widget in self.param_frame.winfo_children(): widget.grid_forget()
        param_row = 0
        if dist == "Uniforme":
            self.param1_label.config(text="Lím Inferior (a):");
            self.param1_label.grid(row=param_row, column=0, sticky="w", padx=2, pady=2)
            self.param1_entry.grid(row=param_row, column=1, sticky="ew", padx=2, pady=2);
            param_row += 1
            self.param2_label.config(text="Lím Superior (b):");
            self.param2_label.grid(row=param_row, column=0, sticky="w", padx=2, pady=2)
            self.param2_entry.grid(row=param_row, column=1, sticky="ew", padx=2, pady=2)
        elif dist == "Exponencial":
            self.param1_label.config(text="Lambda (λ):");
            self.param1_label.grid(row=param_row, column=0, sticky="w", padx=2, pady=2)
            self.param1_entry.grid(row=param_row, column=1, sticky="ew", padx=2, pady=2)
        elif dist == "Normal":
            self.param1_label.config(text="Media (μ):");
            self.param1_label.grid(row=param_row, column=0, sticky="w", padx=2, pady=2)
            self.param1_entry.grid(row=param_row, column=1, sticky="ew", padx=2, pady=2);
            param_row += 1
            self.param2_label.config(text="Desv. Estándar (σ):");
            self.param2_label.grid(row=param_row, column=0, sticky="w", padx=2, pady=2)
            self.param2_entry.grid(row=param_row, column=1, sticky="ew", padx=2, pady=2)

    def _create_display_widgets(self):
        ttk.Label(self.data_display_frame, text="Serie Numérica Generada:", font=("Arial", 10, "bold")).pack(
            anchor="nw")
        self.data_text = scrolledtext.ScrolledText(self.data_display_frame, height=8, width=60, wrap=tk.WORD,
                                                   state='disabled', font=("Consolas", 9))
        self.data_text.pack(expand=True, fill='both')

        ttk.Label(self.table_view_frame, text="Tabla de Frecuencias:", font=("Arial", 10, "bold")).grid(row=0, column=0,
                                                                                                        sticky="nw",
                                                                                                        columnspan=2)

        columns = ('interval', 'frequency')
        self.frequency_table = ttk.Treeview(self.table_view_frame, columns=columns, show='headings',
                                            selectmode='browse')

        self.frequency_table.heading('interval', text='Intervalo')
        self.frequency_table.heading('frequency', text='Frec. Observada')

        self.frequency_table.column('interval', width=250, anchor=tk.W)
        self.frequency_table.column('frequency', width=150, anchor=tk.E)

        vsb = ttk.Scrollbar(self.table_view_frame, orient="vertical", command=self.frequency_table.yview)
        self.frequency_table.configure(yscrollcommand=vsb.set)

        self.frequency_table.grid(row=1, column=0, sticky='nsew')
        vsb.grid(row=1, column=1, sticky='ns')

        self.table_view_frame.rowconfigure(1, weight=1)
        self.table_view_frame.columnconfigure(0, weight=1)

        self.frequency_table.tag_configure('oddrow', background='#E8E8E8')
        self.frequency_table.tag_configure('evenrow', background='#FFFFFF')
        self.frequency_table.tag_configure('totalrow', background='#C0C0C0', font=('Arial', 9, 'bold'))

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        toolbar.update();
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.ax.set_title("Histograma aparecerá aquí");
        self.ax.set_xlabel("Valores");
        self.ax.set_ylabel("Frecuencia")
        self.canvas.draw()

    def _update_text_widget(self, widget, content):
        widget.config(state='normal');
        widget.delete('1.0', tk.END)
        widget.insert('1.0', content);
        widget.config(state='disabled')

    def _update_frequency_table(self, frecuencias, limites):
        for i in self.frequency_table.get_children():
            self.frequency_table.delete(i)

        num_bins = len(frecuencias)
        for i in range(num_bins):
            lim_inf = limites[i]
            lim_sup = limites[i + 1]
            intervalo_str = f"[{lim_inf: >10.4f}, {lim_sup: >10.4f})" if i < num_bins - 1 else f"[{lim_inf: >10.4f}, {lim_sup: >10.4f}]"
            freq_val = frecuencias[i]

            tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            self.frequency_table.insert('', tk.END, values=(intervalo_str, freq_val), tags=(tag,))

        total_freq = np.sum(frecuencias)
        self.frequency_table.insert('', tk.END, values=("-" * 25, "-" * 15), tags=('totalrow',))
        self.frequency_table.insert('', tk.END, values=("Total", f"{total_freq: >15}"), tags=('totalrow',))

    def generate_and_display(self):
        try:
            dist = self.dist_type.get()
            n = int(self.sample_size_var.get())
            if not (1 <= n <= 1000000): raise ValueError("Tamaño muestra entre 1 y 1,000,000.")
            num_bins = self.num_bins_var.get()
            params = {};
            titulo_dist = ""
            if dist == "Uniforme":
                a = float(self.param1_var.get());
                b = float(self.param2_var.get())
                if a >= b: raise ValueError("'a' debe ser menor que 'b'.")
                params = {'a': a, 'b': b};
                titulo_dist = f"Uniforme (a={a:.4f}, b={b:.4f})"
            elif dist == "Exponencial":
                lambda_val = float(self.param1_var.get())
                if lambda_val <= 0: raise ValueError("'lambda' debe ser positivo.")
                params = {'lambda_val': lambda_val};
                titulo_dist = f"Exponencial (λ={lambda_val:.4f})"
            elif dist == "Normal":
                media = float(self.param1_var.get());
                desv_est = float(self.param2_var.get())
                if desv_est <= 0: raise ValueError("'desv_est' debe ser positivo.")
                params = {'media': media, 'desv_est': desv_est};
                titulo_dist = f"Normal (μ={media:.4f}, σ={desv_est:.4f})"

            print(f"Generando {n} datos para {titulo_dist}...")
            if dist == "Uniforme":
                self.generated_data = generar_uniforme(n, **params)
            elif dist == "Exponencial":
                self.generated_data = generar_exponencial(n, **params)
            elif dist == "Normal":
                self.generated_data = generar_normal(n, **params)
            datos_np = np.array(self.generated_data)

            data_str = "\n".join([f"{x:.4f}" for x in datos_np])
            self._update_text_widget(self.data_text, data_str)

            frecuencias, limites = np.histogram(datos_np, bins=num_bins)

            self._update_frequency_table(frecuencias, limites)

            self.ax.clear()
            ancho_barras = limites[1] - limites[0]
            self.ax.bar(limites[:-1], frecuencias, width=ancho_barras, align='edge', edgecolor='black', alpha=0.75,
                        color='dodgerblue')
            self.ax.set_title(f"Histograma - {titulo_dist}\n(N={n}, {num_bins} intervalos)")
            self.ax.set_xlabel("Intervalos de Clase");
            self.ax.set_ylabel("Frecuencia Observada")
            self.ax.set_xticks(limites);
            self.ax.tick_params(axis='x', rotation=45, labelsize=8)
            self.ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
            self.ax.grid(axis='y', linestyle='--', alpha=0.6);
            self.fig.tight_layout()
            self.canvas.draw()

        except ValueError as ve:
            messagebox.showerror("Error de Entrada", str(ve))
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error: {e}")
            import traceback;
            traceback.print_exc()
