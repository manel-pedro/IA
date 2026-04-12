import tkinter as tk
from tkinter import ttk
import os
import glob

def distance(a, b, x, y):
    return abs(a - x) + abs(b - y)

class VisualizadorHashcode:
    # Adicionamos 'func_read_file' para o visualizador conseguir carregar novos ficheiros
    def __init__(self, R, C, F, T_MAX, B, rides, func_greedy, func_smart, func_hill_climbing, func_simulated_annealing, func_genetic, func_read_file):
        self.R = R
        self.C = C
        self.F = F
        self.T_MAX = T_MAX
        self.rides = rides
        self.B = B
        
        self.func_greedy = func_greedy
        self.func_smart = func_smart
        self.func_hill_climbing = func_hill_climbing
        self.func_simulated_annealing = func_simulated_annealing
        self.func_genetic = func_genetic 
        self.func_read_file = func_read_file # <--- Nova função recebida

        # Variável para rastrear qual é o algoritmo ativo (1 a 5). Começa no 2 (Smart Greedy)
        self.algoritmo_ativo = 2 

        self.max_canvas_width = 1180
        self.max_canvas_height = 720
        
        # Correr o Smart Greedy por defeito ao abrir
        self.cars_schedule, self.pontuacao_final_calculada = self.func_smart(self.F, self.B, self.rides)
        
        self.passo_atual = 0
        self.em_execucao = False
        self.score_atual = 0
        
        self.tam_celula = self._calcular_tamanho_celula()
        
        self.carros_sim = []
        self.reset_carros()

        self.root = tk.Tk()
        self.root.title("Simulador Hash Code")
        self.root.geometry("1280x900")
        self.root.minsize(1000, 720)
        self.root.configure(bg="#0f172a")
        
        self.setup_ui()
        self.desenhar()

    def _calcular_tamanho_celula(self):
        if self.R <= 0 or self.C <= 0:
            return 20

        fit_width = max(1, self.max_canvas_width // self.C)
        fit_height = max(1, self.max_canvas_height // self.R)
        return max(1, min(24, fit_width, fit_height))

    def reset_carros(self):
        self.carros_sim = []
        for i, car_data in enumerate(self.cars_schedule):
            self.carros_sim.append({
                "id": i,
                "r": 0, "c": 0,
                "viagens_atribuidas": car_data["rides"],
                "idx_viagem_atual": 0,
                "estado": 'A_CAMINHO_PARTIDA' if len(car_data["rides"]) > 0 else 'CONCLUIDO'
            })

    def mudar_algoritmo(self, tipo):
        self.em_execucao = False
        self.algoritmo_ativo = tipo
        
        # Recalcular as rotas com o algoritmo escolhido
        if tipo == 1:
            self.cars_schedule, self.pontuacao_final_calculada = self.func_greedy(self.F, self.B, self.rides)
            self.lbl_algo_ativo.config(text="Ativo: Greedy Simples")
        elif tipo == 2:
            self.cars_schedule, self.pontuacao_final_calculada = self.func_smart(self.F, self.B, self.rides)
            self.lbl_algo_ativo.config(text="Ativo: Smart Greedy")
        elif tipo == 3:
            self.cars_schedule, self.pontuacao_final_calculada = self.func_hill_climbing(self.F, self.B, self.rides)
            self.lbl_algo_ativo.config(text="Ativo: Hill Climbing")
        elif tipo == 4:
            self.cars_schedule, self.pontuacao_final_calculada = self.func_simulated_annealing(self.F, self.B, self.rides)
            self.lbl_algo_ativo.config(text="Ativo: Simulated Annealing")
        elif tipo == 5:
            self.cars_schedule, self.pontuacao_final_calculada = self.func_genetic(self.F, self.B, self.rides)
            self.lbl_algo_ativo.config(text="Ativo: Algoritmo Genético")
            
        self.restart()

    def carregar_ficheiro(self, event=None):
        """Carrega um novo ficheiro de input e repõe o visualizador"""
        ficheiro_selecionado = self.combo_ficheiros.get()
        if not ficheiro_selecionado: return
        
        caminho_completo = os.path.join("input", ficheiro_selecionado)
        
        # Parar simulação atual
        self.em_execucao = False
        
        # Ler novos dados usando a função do main.py
        self.R, self.C, self.F, N, self.B, self.T_MAX, self.rides = self.func_read_file(caminho_completo)
        
        # Atualizar Labels
        self.lbl_rides.config(text=f"Viagens: {len(self.rides)}")
        self.tam_celula = self._calcular_tamanho_celula()
        
        # Recalcular usando o algoritmo que estava selecionado
        self.mudar_algoritmo(self.algoritmo_ativo)

    def setup_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background="#0f172a")
        style.configure("Header.TFrame", background="#111827")
        style.configure("Card.TFrame", background="#111827")
        style.configure("Title.TLabel", background="#111827", foreground="white", font=("Helvetica", 16, "bold"))
        style.configure("Meta.TLabel", background="#111827", foreground="#cbd5e1", font=("Helvetica", 10))
        style.configure("Dark.TLabel", background="#111827", foreground="white", font=("Helvetica", 10))
        style.configure("Dark.TButton", padding=(10, 6))

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        container = ttk.Frame(self.root, style="App.TFrame", padding=16)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        header = ttk.Frame(container, style="Header.TFrame", padding=(16, 14))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        title_block = ttk.Frame(header, style="Header.TFrame")
        title_block.grid(row=0, column=0, sticky="w")
        ttk.Label(title_block, text="Simulador Hash Code", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_block, text="Local search and greedy solvers on the ride scheduling problem", style="Meta.TLabel").pack(anchor="w", pady=(2, 0))

        # --- NOVO SELECTOR DE FICHEIROS NO CABEÇALHO ---
        file_frame = ttk.Frame(header, style="Header.TFrame")
        file_frame.grid(row=0, column=1, sticky="e", padx=(16, 16))
        ttk.Label(file_frame, text="Dataset:", style="Meta.TLabel").pack(side=tk.LEFT, padx=5)
        
        # Procurar ficheiros na pasta input/
        if os.path.exists("input"):
            ficheiros_input = [os.path.basename(f) for f in glob.glob("input/*.txt") + glob.glob("input/*.in")]
        else:
            ficheiros_input = ["Nenhuma pasta 'input' encontrada"]

        self.combo_ficheiros = ttk.Combobox(file_frame, values=ficheiros_input, state="readonly", width=25)
        if ficheiros_input:
            self.combo_ficheiros.set(ficheiros_input[0]) # Selecionar o primeiro por defeito
        self.combo_ficheiros.pack(side=tk.LEFT)
        self.combo_ficheiros.bind("<<ComboboxSelected>>", self.carregar_ficheiro)


        info_frame = ttk.Frame(header, style="Header.TFrame")
        info_frame.grid(row=0, column=2, sticky="e")
        ttk.Label(info_frame, text="Algoritmo ativo:", style="Meta.TLabel").pack(side=tk.LEFT, padx=5)
        self.lbl_algo_ativo = ttk.Label(info_frame, text="Smart Greedy", style="Title.TLabel")
        self.lbl_algo_ativo.pack(side=tk.LEFT)

        controls = ttk.Frame(container, style="Card.TFrame", padding=12)
        controls.grid(row=1, column=0, sticky="ew", pady=(12, 12))
        controls.columnconfigure(0, weight=1)

        buttons = ttk.Frame(controls, style="Card.TFrame")
        buttons.grid(row=0, column=0, sticky="w")

        ttk.Label(buttons, text="Escolher algoritmo", style="Dark.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons, text="Greedy Simples", style="Dark.TButton", command=lambda: self.mudar_algoritmo(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Smart Greedy", style="Dark.TButton", command=lambda: self.mudar_algoritmo(2)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Hill Climbing", style="Dark.TButton", command=lambda: self.mudar_algoritmo(3)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Simulated Annealing", style="Dark.TButton", command=lambda: self.mudar_algoritmo(4)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Genético", style="Dark.TButton", command=lambda: self.mudar_algoritmo(5)).pack(side=tk.LEFT, padx=5)

        stats = ttk.Frame(controls, style="Card.TFrame")
        stats.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        stats.columnconfigure(0, weight=1)
        stats.columnconfigure(1, weight=1)
        stats.columnconfigure(2, weight=1)
        stats.columnconfigure(3, weight=1)

        self.lbl_passo = ttk.Label(stats, text="Passo: 0", style="Dark.TLabel")
        self.lbl_passo.grid(row=0, column=0, sticky="w")

        self.lbl_score = ttk.Label(stats, text="Score: 0", style="Dark.TLabel")
        self.lbl_score.grid(row=0, column=1, sticky="w")

        self.lbl_rides = ttk.Label(stats, text=f"Viagens: {len(self.rides)}", style="Dark.TLabel")
        self.lbl_rides.grid(row=0, column=2, sticky="w")

        self.lbl_target = ttk.Label(stats, text=f"Alvo: {self.pontuacao_final_calculada}", style="Dark.TLabel")
        self.lbl_target.grid(row=0, column=3, sticky="w")

        actions = ttk.Frame(controls, style="Card.TFrame")
        actions.grid(row=2, column=0, sticky="w", pady=(12, 0))
        ttk.Button(actions, text="Play", command=self.play).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(actions, text="Pause", command=self.pause).pack(side=tk.LEFT, padx=6)
        ttk.Button(actions, text="+1 Passo", command=self.proximo_passo).pack(side=tk.LEFT, padx=6)
        ttk.Button(actions, text="Restart", command=self.restart).pack(side=tk.LEFT, padx=6)

        canvas_shell = ttk.Frame(container, style="App.TFrame")
        canvas_shell.grid(row=2, column=0, sticky="nsew")
        canvas_shell.rowconfigure(0, weight=1)
        canvas_shell.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_shell,
            width=self.max_canvas_width,
            height=self.max_canvas_height,
            bg="white",
            highlightthickness=0,
        )
        x_scroll = ttk.Scrollbar(canvas_shell, orient="horizontal", command=self.canvas.xview)
        y_scroll = ttk.Scrollbar(canvas_shell, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        canvas_shell.rowconfigure(0, weight=1)
        canvas_shell.columnconfigure(0, weight=1)

    def mover_para(self, r_atual, c_atual, r_dest, c_dest):
        if r_atual < r_dest: r_atual += 1
        elif r_atual > r_dest: r_atual -= 1
        elif c_atual < c_dest: c_atual += 1
        elif c_atual > c_dest: c_atual -= 1
        return r_atual, c_atual

    def proximo_passo(self):
        if self.passo_atual >= self.T_MAX:
            self.em_execucao = False
            return

        for carro in self.carros_sim:
            if carro["estado"] == 'CONCLUIDO': continue
            
            id_viagem = carro["viagens_atribuidas"][carro["idx_viagem_atual"]]
            a, b, x, y, s, _ = self.rides[id_viagem]
            
            if carro["estado"] == 'A_CAMINHO_PARTIDA':
                if (carro["r"], carro["c"]) == (a, b):
                    if self.passo_atual < s:
                        carro["estado"] = 'ESPERA'
                    else:
                        carro["estado"] = 'COM_PASSAGEIRO'
                        if self.passo_atual == s: self.score_atual += self.B 
                else:
                    carro["r"], carro["c"] = self.mover_para(carro["r"], carro["c"], a, b)
                    if (carro["r"], carro["c"]) == (a, b) and self.passo_atual < s:
                        carro["estado"] = 'ESPERA'
                    elif (carro["r"], carro["c"]) == (a, b):
                        carro["estado"] = 'COM_PASSAGEIRO'
                        if self.passo_atual == s: self.score_atual += self.B
                        
            elif carro["estado"] == 'ESPERA':
                if self.passo_atual >= s:
                    carro["estado"] = 'COM_PASSAGEIRO'
                    self.score_atual += self.B 
                    
            elif carro["estado"] == 'COM_PASSAGEIRO':
                carro["r"], carro["c"] = self.mover_para(carro["r"], carro["c"], x, y)
                if (carro["r"], carro["c"]) == (x, y):
                    self.score_atual += distance(a, b, x, y)
                    carro["idx_viagem_atual"] += 1
                    if carro["idx_viagem_atual"] >= len(carro["viagens_atribuidas"]):
                        carro["estado"] = 'CONCLUIDO'
                    else:
                        carro["estado"] = 'A_CAMINHO_PARTIDA'

        self.passo_atual += 1
        self.desenhar()
        
        if self.em_execucao:
            self.root.after(300, self.proximo_passo)

    def desenhar(self):
        self.canvas.delete("all")
        self.lbl_passo.config(text=f"Passo: {self.passo_atual} / {self.T_MAX}")
        self.lbl_score.config(text=f"Score: {self.score_atual} (Alvo: {self.pontuacao_final_calculada})")
        self.lbl_target.config(text=f"Alvo: {self.pontuacao_final_calculada}")
        
        if max(self.R, self.C) < 100:
            for i in range(self.R + 1):
                self.canvas.create_line(0, i*self.tam_celula, self.C*self.tam_celula, i*self.tam_celula, fill="#eee")
            for j in range(self.C + 1):
                self.canvas.create_line(j*self.tam_celula, 0, j*self.tam_celula, self.R*self.tam_celula, fill="#eee")
                
        for carro in self.carros_sim:
            if carro["estado"] != 'CONCLUIDO':
                id_v = carro["viagens_atribuidas"][carro["idx_viagem_atual"]]
                a, b, x, y, _, _ = self.rides[id_v]
                marker = max(4, min(10, self.tam_celula // 2))
                self.canvas.create_oval(b*self.tam_celula+4, a*self.tam_celula+4, b*self.tam_celula+4+marker, a*self.tam_celula+4+marker, fill="#22c55e", outline="")
                self.canvas.create_oval(y*self.tam_celula+4, x*self.tam_celula+4, y*self.tam_celula+4+marker, x*self.tam_celula+4+marker, fill="#ef4444", outline="")
                
        cores = ["blue", "purple", "orange", "black"]
        for carro in self.carros_sim:
            cy = carro["r"] * self.tam_celula + (self.tam_celula//2)
            cx = carro["c"] * self.tam_celula + (self.tam_celula//2)
            cor = "gray" if carro["estado"] == 'CONCLUIDO' else cores[carro["id"] % len(cores)]
            half = max(4, min(12, self.tam_celula // 2))
            self.canvas.create_rectangle(cx-half, cy-half, cx+half, cy+half, fill=cor, outline="")
            self.canvas.create_text(cx, cy, text=str(carro["id"]), fill="white", font=("Helvetica", 8, "bold"))

        self.canvas.configure(scrollregion=(0, 0, self.C * self.tam_celula, self.R * self.tam_celula))

    def play(self):
        if not self.em_execucao:
            self.em_execucao = True
            self.proximo_passo()

    def pause(self):
        self.em_execucao = False
        
    def restart(self):
        self.em_execucao = False
        self.passo_atual = 0
        self.score_atual = 0
        self.reset_carros()
        self.desenhar()

    def iniciar(self):
        self.root.mainloop()