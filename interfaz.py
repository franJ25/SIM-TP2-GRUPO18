import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from chi2 import * # Asumo que chi2.py existe y es correcto
import aleatorios # Asumo que aleatorios.py existe y es correcto


class RandomGenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de números aleatorios - TP2 SIM")
        self.geometry("1000x750")

        self.dist_type = tk.StringVar(value="Uniforme")
        self.sample_size_var = tk.StringVar(value="100")
        self.param1_var = tk.StringVar(value="0")
        self.param2_var = tk.StringVar(value="1")
        self.num_bins_var = tk.IntVar(value=10)

        self.generated_data = None
        self.current_frecuencias_obs = None
        self.current_limites_intervalos = None
        self.current_n_total = 0
        self.current_dist_params = {}  # Parámetros usados para la generación

        self.columnconfigure(0, weight=1, minsize=280)
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
        self.table_view_frame.rowconfigure(1, weight=1)

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

        ttk.Label(frame, text="Parámetros de Generación", font=("Arial", 14, "bold")).grid(
            row=row_idx, column=0, columnspan=2, pady=(0, 15))
        row_idx += 1

        ttk.Label(frame, text="Distribución:").grid(row=row_idx, column=0, sticky="w", pady=2)
        dist_options = ["Uniforme", "Exponencial", "Normal"]
        dist_combo = ttk.Combobox(frame, textvariable=self.dist_type, values=dist_options, state="readonly", width=20)
        dist_combo.grid(row=row_idx, column=1, sticky="ew", pady=2)
        dist_combo.bind("<<ComboboxSelected>>", self._update_parameter_fields)
        row_idx += 1

        ttk.Label(frame, text="Tamaño Muestra (N):").grid(row=row_idx, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=self.sample_size_var, width=22).grid(row=row_idx, column=1, sticky="ew", pady=2)
        row_idx += 1

        self.param_frame = ttk.Frame(frame)
        self.param_frame.grid(row=row_idx, column=0, columnspan=2, sticky="nsew", pady=5)
        self.param_frame.columnconfigure(1, weight=1)

        self.param1_label = ttk.Label(self.param_frame, text="Parámetro 1:")
        self.param1_entry = ttk.Entry(self.param_frame, textvariable=self.param1_var, width=15)
        self.param2_label = ttk.Label(self.param_frame, text="Parámetro 2:")
        self.param2_entry = ttk.Entry(self.param_frame, textvariable=self.param2_var, width=15)
        row_idx += 1

        ttk.Label(frame, text="Intervalos Histograma (k):").grid(row=row_idx, column=0, sticky="w", pady=2)
        # Punto 2: Solo deje escoger entre 10, 15, 20 o 25 intervalos.
        bin_options = [10, 15, 20, 25]
        bin_combo = ttk.Combobox(frame, textvariable=self.num_bins_var, values=bin_options, state="readonly", width=20)
        bin_combo.grid(row=row_idx, column=1, sticky="ew", pady=2)
        self.num_bins_var.set(10) # El default es 10, que está en la lista
        row_idx += 1

        ttk.Button(frame, text="Generar Datos", command=self.generate_and_display, style="Accent.TButton").grid(
            row=row_idx, column=0, columnspan=2, pady=15, sticky="ew")
        row_idx += 1

        self.chi_square_button = ttk.Button(frame, text="Prueba Chi Cuadrado",
                                            command=self._open_chi_square_test_window, style="Accent.TButton")
        self.chi_square_button.grid(row=row_idx, column=0, columnspan=2, pady=10, sticky="ew")
        self.chi_square_button.config(state="disabled")
        row_idx += 1

    def _update_parameter_fields(self, event=None):
        dist = self.dist_type.get()

        self.param1_label.grid_forget()
        self.param1_entry.grid_forget()
        self.param2_label.grid_forget()
        self.param2_entry.grid_forget()

        param_row = 0
        if dist == "Uniforme":
            self.param1_label.config(text="Lím Inferior (a):")
            self.param1_label.grid(row=param_row, column=0, sticky="w", padx=2, pady=2)
            self.param1_entry.grid(row=param_row, column=1, sticky="ew", padx=2, pady=2)
            param_row += 1
            self.param2_label.config(text="Lím Superior (b):")
            self.param2_label.grid(row=param_row, column=0, sticky="w", padx=2, pady=2)
            self.param2_entry.grid(row=param_row, column=1, sticky="ew", padx=2, pady=2)
        elif dist == "Exponencial":
            self.param1_label.config(text="Lambda (λ):")
            self.param1_label.grid(row=param_row, column=0, sticky="w", padx=2, pady=2)
            self.param1_entry.grid(row=param_row, column=1, sticky="ew", padx=2, pady=2)
        elif dist == "Normal":
            self.param1_label.config(text="Media (μ):")
            self.param1_label.grid(row=param_row, column=0, sticky="w", padx=2, pady=2)
            self.param1_entry.grid(row=param_row, column=1, sticky="ew", padx=2, pady=2)
            param_row += 1
            self.param2_label.config(text="Desv. Estándar (σ):")
            self.param2_label.grid(row=param_row, column=0, sticky="w", padx=2, pady=2)
            self.param2_entry.grid(row=param_row, column=1, sticky="ew", padx=2, pady=2)

    def _create_display_widgets(self):
        ttk.Label(self.data_display_frame, text="Serie Numérica Generada:", font=("Arial", 10, "bold")).pack(
            anchor="nw")
        self.data_text = scrolledtext.ScrolledText(self.data_display_frame, height=8, width=60, wrap=tk.WORD,
                                                   state='disabled', font=("Consolas", 9))
        self.data_text.pack(expand=True, fill='both')

        ttk.Label(self.table_view_frame, text="Tabla de Frecuencias:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="nw", columnspan=2)

        columns = ('intervalo', 'frec_obs')
        self.frequency_table = ttk.Treeview(self.table_view_frame, columns=columns, show='headings',
                                            selectmode='browse')
        self.frequency_table.heading('intervalo', text='Intervalo')
        self.frequency_table.heading('frec_obs', text='Frec. Observada')
        self.frequency_table.column('intervalo', width=250, anchor=tk.W)
        self.frequency_table.column('frec_obs', width=150, anchor=tk.CENTER)  # Centrado

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

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.ax.set_title("Histograma aparecerá aquí")
        self.ax.set_xlabel("Valores")
        self.ax.set_ylabel("Frecuencia")
        self.fig.tight_layout()
        self.canvas.draw()

    def _update_text_widget(self, widget, content):
        widget.config(state='normal')
        widget.delete('1.0', tk.END)
        widget.insert('1.0', content)
        widget.config(state='disabled')

    def _update_frequency_table(self, frecuencias, limites):
        for i in self.frequency_table.get_children():
            self.frequency_table.delete(i)

        num_bins_actual = len(frecuencias)
        for i in range(num_bins_actual):
            lim_inf = limites[i]
            lim_sup = limites[i + 1]
            intervalo_str = f"[{lim_inf: >9.4f}, {lim_sup: >9.4f})" if i < num_bins_actual - 1 else f"[{lim_inf: >9.4f}, {lim_sup: >9.4f}]"
            freq_val = frecuencias[i]
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.frequency_table.insert('', tk.END, values=(intervalo_str, freq_val), tags=(tag,))

        total_freq = np.sum(frecuencias)
        self.frequency_table.insert('', tk.END, values=("-" * 30, "-" * 18), tags=('totalrow',))  # Ajustar guiones
        self.frequency_table.insert('', tk.END, values=("Total", f"{total_freq: >18}"), tags=('totalrow',))

    def generate_and_display(self):
        try:
            dist = self.dist_type.get()
            n = int(self.sample_size_var.get())
            if not (1 <= n <= 1000000): raise ValueError("Tamaño muestra debe estar entre 1 y 1,000,000.")
            self.current_n_total = n # Guardar n para uso posterior

            num_bins = self.num_bins_var.get()
            # Validación N vs k para Chi2 (importante para g.l. > 0)
            # Para Normal se restan 2 parámetros, para Exponencial 1.
            # g.l. = k - 1 - p
            # k - 1 - p > 0  => k > p + 1
            min_k_needed = 0
            if dist == "Normal":
                min_k_needed = 2 + 1  # p=2
            elif dist == "Exponencial":
                min_k_needed = 1 + 1  # p=1
            elif dist == "Uniforme":
                min_k_needed = 0 + 1  # p=0

            if num_bins <= min_k_needed:
                messagebox.showwarning("Advertencia de Intervalos",
                                       f"Para la distribución {dist} y la prueba Chi-cuadrado, se necesitan al menos {min_k_needed + 1} intervalos (k).\n"
                                       f"Actualmente tiene {num_bins}. Los grados de libertad podrían ser no positivos.",
                                       parent=self)
                # No impedir, pero advertir. La prueba Chi2 en sí mostrará el error de g.l.

            if n < num_bins * 5:  # Regla de Cochran (FE >= 5)
                messagebox.showinfo("Sugerencia de Intervalos",
                                    f"Con N={n} y k={num_bins} intervalos, algunas frecuencias esperadas podrían ser < 5.\n"
                                    "Esto puede afectar la validez de la prueba Chi-cuadrado.\n"
                                    "Considere aumentar N o disminuir k.", parent=self)

            self.current_dist_params = {}
            titulo_dist = ""

            if dist == "Uniforme":
                a = float(self.param1_var.get())
                b = float(self.param2_var.get())
                if a >= b: raise ValueError("Para Uniforme, 'a' (Lím Inferior) debe ser menor que 'b' (Lím Superior).")
                self.current_dist_params = {'a': a, 'b': b}
                titulo_dist = f"Uniforme (a={a:.4f}, b={b:.4f})"
                self.generated_data = aleatorios.generar_uniforme(n, **self.current_dist_params)
            elif dist == "Exponencial":
                lambda_val = float(self.param1_var.get())
                if lambda_val <= 0: raise ValueError("Para Exponencial, 'lambda' debe ser positivo.")
                self.current_dist_params = {'lambda_val': lambda_val}
                titulo_dist = f"Exponencial (λ={lambda_val:.4f})"
                self.generated_data = aleatorios.generar_exponencial(n, **self.current_dist_params)
            elif dist == "Normal":
                media = float(self.param1_var.get())
                desv_est = float(self.param2_var.get())
                if desv_est <= 0: raise ValueError("Para Normal, 'Desv. Estándar' debe ser positivo.")
                self.current_dist_params = {'media': media, 'desv_est': desv_est}
                titulo_dist = f"Normal (μ={media:.4f}, σ={desv_est:.4f})"
                self.generated_data = aleatorios.generar_normal(n, **self.current_dist_params)

            datos_np = np.array(self.generated_data)

            # CAMBIO SOLICITADO: Mostrar siempre la serie completa
            data_str = "\n".join([f"{x:.4f}" for x in datos_np])
            self._update_text_widget(self.data_text, data_str)

            self.current_frecuencias_obs, self.current_limites_intervalos = np.histogram(datos_np, bins=num_bins)
            # self.current_n_total = n # Ya se asignó arriba

            self._update_frequency_table(self.current_frecuencias_obs, self.current_limites_intervalos)

            self.ax.clear()
            self.ax.hist(datos_np, bins=self.current_limites_intervalos, edgecolor='black', alpha=0.75,
                         color='dodgerblue')

            self.ax.set_title(f"Histograma - {titulo_dist}\n(N={n}, {len(self.current_frecuencias_obs)} intervalos)")
            self.ax.set_xlabel("Intervalos de Clase")
            self.ax.set_ylabel("Frecuencia Observada")

            self.ax.set_xticks(self.current_limites_intervalos)
            self.ax.tick_params(axis='x', rotation=45, labelsize=8)
            # Punto 1: En el histograma muestre los límites con 4 decimales.
            self.ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.4f')) # CAMBIO AQUÍ

            self.ax.grid(axis='y', linestyle='--', alpha=0.6)
            self.fig.tight_layout()
            self.canvas.draw()
            self.toolbar.update()  # Asegurar que la toolbar se refresque

            # Punto 3: Solo ejecute la prueba de chi cuadrado cuando n >= 30.
            if n >= 30:
                self.chi_square_button.config(state="normal")
            else:
                self.chi_square_button.config(state="disabled")
                messagebox.showinfo("Prueba Chi-Cuadrado",
                                    f"La prueba Chi-Cuadrado está deshabilitada porque N ({n}) es menor que 30.",
                                    parent=self)

        except ValueError as ve:
            messagebox.showerror("Error de Entrada", str(ve))
            self.chi_square_button.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error: {e}")
            import traceback
            traceback.print_exc()
            self.chi_square_button.config(state="disabled")

    def _open_chi_square_test_window(self):
        # Punto 3: Solo ejecute la prueba de chi cuadrado cuando n >= 30 (segunda verificación).
        if self.current_n_total < 30:
            messagebox.showwarning("Prueba Chi-Cuadrado no disponible",
                                   "La prueba de Chi-Cuadrado solo está disponible para N >= 30.",
                                   parent=self)
            return

        if self.generated_data is None or self.current_frecuencias_obs is None:
            messagebox.showwarning("Sin Datos", "Primero debe generar datos para realizar la prueba de Chi-Cuadrado.",
                                   parent=self)
            return

        app_data_for_chi2 = {
            'dist_type': self.dist_type.get(),
            'n_total': self.current_n_total,
            'params_generacion': self.current_dist_params.copy(),
            'frecuencias_obs': self.current_frecuencias_obs.tolist(),
            'limites_intervalos': self.current_limites_intervalos.tolist(),
            'raw_data': self.generated_data
        }
        ChiInterfaz(self, app_data_for_chi2)


class ChiInterfaz(tk.Toplevel):
    def __init__(self, master, app_data):
        super().__init__(master)
        self.title("Prueba de Bondad de Ajuste Chi-Cuadrado (Parámetros Estimados)")
        self.geometry("700x550")
        self.transient(master)
        self.grab_set()

        self.app_data = app_data
        self.alpha_var = tk.StringVar(value="0.05")

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill="both")

        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill="x", pady=5)

        ttk.Label(controls_frame, text="Nivel de significancia (α):").grid(row=0, column=0, padx=5, sticky="w")
        alpha_entry = ttk.Entry(controls_frame, textvariable=self.alpha_var, width=10)
        alpha_entry.grid(row=0, column=1, padx=5, sticky="w")

        try:
            run_button = ttk.Button(controls_frame, text="Realizar Prueba", command=self.run_test,
                                    style="Accent.TButton")
        except tk.TclError:
            run_button = ttk.Button(controls_frame, text="Realizar Prueba", command=self.run_test)
        run_button.grid(row=0, column=2, padx=10)

        results_frame = ttk.LabelFrame(main_frame, text="Resultados de la Prueba", padding="10")
        results_frame.pack(expand=True, fill="both", pady=10)

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15, font=("Consolas", 9))
        self.results_text.pack(expand=True, fill="both")
        self.results_text.insert(tk.END, "Ingrese alfa y presione 'Realizar Prueba'.\n"
                                         "La prueba utilizará parámetros (ej: media, lambda) estimados a partir de los datos generados.\n"
                                         "La hipótesis nula (H0) es que los datos siguen la distribución especificada.\n"
                                         "La hipótesis alternativa (H1) es que los datos no siguen dicha distribución.\n")
        self.results_text.config(state='disabled')

    def _update_results_text(self, content):
        self.results_text.config(state='normal')
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert('1.0', content)
        self.results_text.config(state='disabled')

    def run_test(self):
        try:
            alpha = float(self.alpha_var.get())
            if not (0 < alpha < 1):
                raise ValueError("Alfa debe estar entre 0 y 1 (excluyentes).")
        except ValueError as e:
            messagebox.showerror("Error de Entrada", f"Valor de alfa inválido: {e}", parent=self)
            return

        if not self.app_data or not self.app_data.get('frecuencias_obs') or not self.app_data.get('raw_data'):
            messagebox.showerror("Error de Datos", "No hay datos crudos o procesados para la prueba.", parent=self)
            return

        dist_type = self.app_data['dist_type']
        n_total = self.app_data['n_total']
        frecuencias_obs = self.app_data['frecuencias_obs']
        limites_intervalos = self.app_data['limites_intervalos']
        raw_data_np = np.array(self.app_data['raw_data'])

        resultados_str = f"Distribución probada: {dist_type}\n"
        params_estimados_info = ""

        if dist_type == "Uniforme":
            a_est = limites_intervalos[0]
            b_est = limites_intervalos[-1]
            params_estimados_info = f"Se asume uniformidad sobre el rango de los datos observados [{a_est:.4f}, {b_est:.4f}]."
            res_str_details = chi2_uniforme(frecuencias_obs, limites_intervalos, n_total, alpha)

        elif dist_type == "Exponencial":
            if len(raw_data_np) == 0:
                messagebox.showerror("Error", "No hay datos para estimar Lambda.", parent=self)
                return
            media_muestral = np.mean(raw_data_np)
            if media_muestral == 0:
                messagebox.showerror("Error de Estimación",
                                     "La media muestral es cero, no se puede estimar Lambda para Exponencial.",
                                     parent=self)
                return
            lambda_estimada = 1.0 / media_muestral
            params_estimados_info = f"Lambda (λ) estimada de los datos: {lambda_estimada:.4f}"
            res_str_details = chi2_exponencial(frecuencias_obs, limites_intervalos, n_total, lambda_estimada, alpha)

        elif dist_type == "Normal":
            if len(raw_data_np) < 2:
                messagebox.showerror("Error", "No hay suficientes datos para estimar Media y Desv. Estándar.",
                                     parent=self)
                return
            media_estimada = np.mean(raw_data_np)
            desv_est_estimada = np.std(raw_data_np, ddof=1)
            if desv_est_estimada == 0:
                messagebox.showerror("Error de Estimación",
                                     "La desviación estándar muestral es cero. Verifique los datos.", parent=self)
                return
            params_estimados_info = (f"Media (μ) estimada: {media_estimada:.4f}\n"
                                     f"Desv. Estándar (σ) estimada: {desv_est_estimada:.4f}")
            res_str_details = chi2_normal(frecuencias_obs, limites_intervalos, n_total, media_estimada,
                                          desv_est_estimada, alpha)
        else:
            messagebox.showerror("Error", f"Distribución desconocida: {dist_type}", parent=self)
            return

        resultados_str += params_estimados_info + "\n" + "-" * 30 + "\n"
        resultados_str += res_str_details
        self._update_results_text(resultados_str)
