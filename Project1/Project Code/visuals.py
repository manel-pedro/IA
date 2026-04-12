import tkinter as tk
from tkinter import ttk, messagebox
import os
import glob

def distance(a, b, x, y):
    return abs(a - x) + abs(b - y)

class VisualizadorHashcode:
    def __init__(self, R, C, F, T_MAX, B, rides, func_greedy, func_smart, func_randomized, func_hill_climbing, func_simulated_annealing, func_genetic, func_read_file):
        self.R = R
        self.C = C
        self.F = F
        self.T_MAX = T_MAX
        self.rides = rides
        self.B = B
        
        self.func_greedy = func_greedy
        self.func_smart = func_smart
        self.func_randomized = func_randomized
        self.func_hill_climbing = func_hill_climbing
        self.func_simulated_annealing = func_simulated_annealing
        self.func_genetic = func_genetic 
        self.func_read_file = func_read_file

        self.algoritmo_ativo = 2 

        # Valores base de fallback, o Canvas vai adaptar-se ao tamanho real
        self.current_canvas_width = 1180
        self.current_canvas_height = 680
        
        # Paleta de Cores Moderna (Dark Theme)
        self.colors = {
            "bg_main": "#0f172a",        # Fundo principal (Slate 900)
            "bg_card": "#1e293b",        # Fundo dos painéis (Slate 800)
            "bg_canvas": "#0B1120",      # Fundo do mapa (Ainda mais escuro)
            "text_primary": "#f8fafc",   # Texto principal (Slate 50)
            "text_secondary": "#94a3b8", # Texto secundário (Slate 400)
            "accent": "#3b82f6",         # Cor de destaque (Azul)
            "grid_lines": "#334155",     # Linhas da grelha
            "car_empty": "#3b82f6",      # Azul brilhante
            "car_wait": "#f59e0b",       # Amarelo/Laranja
            "car_full": "#10b981",       # Verde esmeralda
            "car_done": "#475569",       # Cinzento neutro
            "ride_start": "#10b981",     # Verde para início da viagem
            "ride_end": "#ef4444"        # Vermelho para fim da viagem
        }

        self.cars_schedule, self.pontuacao_final_calculada = self.func_smart(self.F, self.B, self.rides)
        
        self.passo_atual = 0
        self.em_execucao = False
        self.score_atual = 0
        
        self.tam_celula = 20 # Calculado dinamicamente no redraw
        
        self.carros_sim = []
        self.reset_carros()

        self.root = tk.Tk()
        self.root.title("Simulador Hash Code - Otimização de Frotas")
        self.root.geometry("1280x900")
        self.root.minsize(1100, 750)
        self.root.configure(bg=self.colors["bg_main"])
        
        self.setup_ui()
        
        # Força uma atualização inicial para o Canvas calcular a sua largura real
        self.root.update_idletasks() 
        self.desenhar()

    def _obter_ficheiros_validos(self):
        """Lê os cabeçalhos de todos os ficheiros e retorna apenas os <= 30x30"""
        ficheiros_validos = []
        if os.path.exists("input"):
            todos_ficheiros = glob.glob("input/*.txt") + glob.glob("input/*.in")
            todos_ficheiros.sort()
            
            for caminho in todos_ficheiros:
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        primeira_linha = f.readline().strip()
                        if primeira_linha:
                            partes = primeira_linha.split()
                            if len(partes) >= 2:
                                r_file = int(partes[0])
                                c_file = int(partes[1])
                                if r_file <= 30 and c_file <= 30:
                                    ficheiros_validos.append(os.path.basename(caminho))
                except Exception:
                    pass
                    
        if not ficheiros_validos:
            ficheiros_validos = ["Nenhum dataset <= 30x30 encontrado"]
            
        return ficheiros_validos

    def _calcular_tamanho_celula(self):
        if self.R <= 0 or self.C <= 0:
            return 20
        # Subtrai-se 60 para dar uma margem segura nas bordas
        fit_width = max(1, (self.current_canvas_width - 60) // self.C)
        fit_height = max(1, (self.current_canvas_height - 60) // self.R)
        return max(2, min(35, fit_width, fit_height))

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
        
        nomes = {
            1: "Greedy Simples",
            2: "Smart Greedy",
            3: "Randomized Greedy",
            4: "Hill Climbing",
            5: "Simulated Annealing",
            6: "Algoritmo Genético"
        }
        
        funcs = {
            1: self.func_greedy,
            2: self.func_smart,
            3: self.func_randomized,
            4: self.func_hill_climbing,
            5: self.func_simulated_annealing,
            6: self.func_genetic
        }
        
        self.lbl_algo_ativo.config(text=f"A calcular {nomes[tipo]}...")
        self.root.update()
        
        self.cars_schedule, self.pontuacao_final_calculada = funcs[tipo](self.F, self.B, self.rides)
        self.lbl_algo_ativo.config(text=nomes[tipo])
            
        self.restart()

    def carregar_ficheiro(self, event=None):
        ficheiro_selecionado = self.combo_ficheiros.get()
        if not ficheiro_selecionado or ficheiro_selecionado == "Nenhum dataset <= 30x30 encontrado": return
        
        self.lbl_algo_ativo.config(text="A carregar ficheiro...")
        self.root.update()
        
        caminho_completo = os.path.join("input", ficheiro_selecionado)
        self.em_execucao = False
        self.R, self.C, self.F, N, self.B, self.T_MAX, self.rides = self.func_read_file(caminho_completo)
        
        self.lbl_rides.config(text=f"Viagens Totais: {len(self.rides)}")
        self.desenhar() # Vai recalcular o tamanho da célula automaticamente
        self.mudar_algoritmo(self.algoritmo_ativo)

    def on_canvas_resize(self, event):
        """Dispara sempre que a janela for redimensionada para recentrar o mapa"""
        if event.widget == self.canvas:
            new_width = event.width
            new_height = event.height
            # Evita redraws contínuos e desnecessários com pequenas flutuações
            if abs(new_width - self.current_canvas_width) > 10 or abs(new_height - self.current_canvas_height) > 10:
                self.current_canvas_width = new_width
                self.current_canvas_height = new_height
                # Se não estiver a executar, redesenha o frame para centrar
                if not self.em_execucao:
                    self.desenhar()

    def setup_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        font_title = ("Segoe UI", 16, "bold")
        font_main = ("Segoe UI", 11)
        font_small = ("Segoe UI", 9)

        style.configure("App.TFrame", background=self.colors["bg_main"])
        style.configure("Card.TFrame", background=self.colors["bg_card"])
        
        style.configure("Title.TLabel", background=self.colors["bg_card"], foreground=self.colors["text_primary"], font=font_title)
        style.configure("Subtitle.TLabel", background=self.colors["bg_card"], foreground=self.colors["text_secondary"], font=font_small)
        style.configure("Data.TLabel", background=self.colors["bg_card"], foreground=self.colors["accent"], font=("Segoe UI", 12, "bold"))
        style.configure("Standard.TLabel", background=self.colors["bg_card"], foreground=self.colors["text_primary"], font=font_main)

        style.configure("Modern.TButton", 
                        font=("Segoe UI", 10), 
                        padding=6, 
                        background="#334155", 
                        foreground="white",
                        borderwidth=0)
        style.map("Modern.TButton",
                  background=[('active', self.colors["accent"])],
                  foreground=[('active', 'white')])

        style.configure("Action.TButton", 
                        font=("Segoe UI", 10, "bold"), 
                        padding=8, 
                        background=self.colors["accent"], 
                        foreground="white",
                        borderwidth=0)
        style.map("Action.TButton",
                  background=[('active', '#2563eb')])

        container = ttk.Frame(self.root, style="App.TFrame")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        # --- CABEÇALHO ---
        header = ttk.Frame(container, style="Card.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header.columnconfigure(2, weight=1)

        title_box = tk.Frame(header, bg=self.colors["bg_card"], padx=15, pady=10)
        title_box.grid(row=0, column=0, sticky="w")
        ttk.Label(title_box, text="Simulador Hash Code", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_box, text="Ride Scheduling AI Visualizer", style="Subtitle.TLabel").pack(anchor="w")

        file_box = tk.Frame(header, bg=self.colors["bg_card"], padx=15, pady=10)
        file_box.grid(row=0, column=1, sticky="w")
        ttk.Label(file_box, text="Dataset Visual (<= 30x30):", style="Subtitle.TLabel").pack(anchor="w")
        
        ficheiros_input = self._obter_ficheiros_validos()

        self.combo_ficheiros = ttk.Combobox(file_box, values=ficheiros_input, state="readonly", width=30, font=font_main)
        if ficheiros_input:
            ficheiro_atual = "a_example.in" if not self.rides else "a_example.in" 
            encontrado = False
            for f in ficheiros_input:
                if self.R <= 30 and self.C <= 30:
                     self.combo_ficheiros.set(f)
                     encontrado = True
                     break
            if not encontrado:
                self.combo_ficheiros.set(ficheiros_input[0])
                
        self.combo_ficheiros.pack(side=tk.LEFT, pady=(4, 0))
        self.combo_ficheiros.bind("<<ComboboxSelected>>", self.carregar_ficheiro)

        algo_box = tk.Frame(header, bg=self.colors["bg_card"], padx=15, pady=10)
        algo_box.grid(row=0, column=2, sticky="e")
        ttk.Label(algo_box, text="Algoritmo Selecionado", style="Subtitle.TLabel").pack(anchor="e")
        self.lbl_algo_ativo = ttk.Label(algo_box, text="Smart Greedy", style="Data.TLabel")
        self.lbl_algo_ativo.pack(anchor="e")

        # --- PAINEL DE CONTROLO ---
        control_panel = ttk.Frame(container, style="Card.TFrame", padding=15)
        control_panel.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        control_panel.columnconfigure(0, weight=1)

        row1 = tk.Frame(control_panel, bg=self.colors["bg_card"])
        row1.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        row1.columnconfigure(1, weight=1)

        algo_btns = tk.Frame(row1, bg=self.colors["bg_card"])
        algo_btns.grid(row=0, column=0, sticky="w")
        
        ttk.Button(algo_btns, text="Greedy Simples", style="Modern.TButton", command=lambda: self.mudar_algoritmo(1)).pack(side=tk.LEFT, padx=3)
        ttk.Button(algo_btns, text="Smart Greedy", style="Modern.TButton", command=lambda: self.mudar_algoritmo(2)).pack(side=tk.LEFT, padx=3)
        ttk.Button(algo_btns, text="Randomized Greedy", style="Modern.TButton", command=lambda: self.mudar_algoritmo(3)).pack(side=tk.LEFT, padx=3)
        ttk.Button(algo_btns, text="Hill Climbing", style="Modern.TButton", command=lambda: self.mudar_algoritmo(4)).pack(side=tk.LEFT, padx=3)
        ttk.Button(algo_btns, text="Simulated Annealing", style="Modern.TButton", command=lambda: self.mudar_algoritmo(5)).pack(side=tk.LEFT, padx=3)
        ttk.Button(algo_btns, text="Genético", style="Modern.TButton", command=lambda: self.mudar_algoritmo(6)).pack(side=tk.LEFT, padx=3)

        stats_box = tk.Frame(row1, bg=self.colors["bg_card"])
        stats_box.grid(row=0, column=1, sticky="e")
        
        self.lbl_passo = ttk.Label(stats_box, text="Passo: 0", style="Standard.TLabel")
        self.lbl_passo.pack(side=tk.LEFT, padx=15)
        
        self.lbl_rides = ttk.Label(stats_box, text=f"Viagens: {len(self.rides)}", style="Standard.TLabel")
        self.lbl_rides.pack(side=tk.LEFT, padx=15)

        self.lbl_score = ttk.Label(stats_box, text=f"Score Atual: 0 | Final: {self.pontuacao_final_calculada}", style="Data.TLabel", foreground=self.colors["car_full"])
        self.lbl_score.pack(side=tk.LEFT, padx=15)

        ttk.Separator(control_panel, orient='horizontal').grid(row=1, column=0, sticky="ew", pady=10)

        sim_btns = tk.Frame(control_panel, bg=self.colors["bg_card"])
        sim_btns.grid(row=2, column=0) 
        
        ttk.Button(sim_btns, text="Play", style="Action.TButton", width=12, command=self.play).pack(side=tk.LEFT, padx=5)
        ttk.Button(sim_btns, text="Pause", style="Modern.TButton", width=12, command=self.pause).pack(side=tk.LEFT, padx=5)
        ttk.Button(sim_btns, text="+1 Passo", style="Modern.TButton", width=12, command=self.proximo_passo).pack(side=tk.LEFT, padx=5)
        ttk.Button(sim_btns, text="Saltar p/ Fim", style="Modern.TButton", width=15, command=self.saltar_para_fim).pack(side=tk.LEFT, padx=5)
        ttk.Button(sim_btns, text="Reset", style="Modern.TButton", width=12, command=self.restart).pack(side=tk.LEFT, padx=5)

        # --- ÁREA DO MAPA (CANVAS) ---
        canvas_frame = tk.Frame(container, bg=self.colors["bg_card"], bd=1, relief=tk.FLAT)
        canvas_frame.grid(row=2, column=0, sticky="nsew")
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.current_canvas_width,
            height=self.current_canvas_height,
            bg=self.colors["bg_canvas"],
            highlightthickness=0,
        )
        
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        x_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        y_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        # --- LEGENDA VISUAL ---
        legenda = tk.Frame(container, bg=self.colors["bg_main"], pady=5)
        legenda.grid(row=3, column=0, sticky="w")
        
        # Legenda dos Carros (Quadrados)
        ttk.Label(legenda, text="■ Livre  ", foreground=self.colors["car_empty"], font=font_small, background=self.colors["bg_main"]).pack(side=tk.LEFT)
        ttk.Label(legenda, text="■ Em Espera  ", foreground=self.colors["car_wait"], font=font_small, background=self.colors["bg_main"]).pack(side=tk.LEFT)
        ttk.Label(legenda, text="■ Com Passageiro  ", foreground=self.colors["car_full"], font=font_small, background=self.colors["bg_main"]).pack(side=tk.LEFT)
        ttk.Label(legenda, text="■ Concluído", foreground=self.colors["car_done"], font=font_small, background=self.colors["bg_main"]).pack(side=tk.LEFT)
        
        # Separador
        ttk.Label(legenda, text="   |   ", foreground=self.colors["text_secondary"], font=font_small, background=self.colors["bg_main"]).pack(side=tk.LEFT)
        
        # Legenda das Viagens (Círculos)
        ttk.Label(legenda, text="● Partida (Viagem)  ", foreground=self.colors["ride_start"], font=font_small, background=self.colors["bg_main"]).pack(side=tk.LEFT)
        ttk.Label(legenda, text="● Chegada (Viagem)", foreground=self.colors["ride_end"], font=font_small, background=self.colors["bg_main"]).pack(side=tk.LEFT)

    def mover_para(self, r_atual, c_atual, r_dest, c_dest):
        if r_atual < r_dest: r_atual += 1
        elif r_atual > r_dest: r_atual -= 1
        elif c_atual < c_dest: c_atual += 1
        elif c_atual > c_dest: c_atual -= 1
        return r_atual, c_atual

    def logica_carros(self):
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

    def proximo_passo(self):
        if self.passo_atual >= self.T_MAX:
            self.em_execucao = False
            return

        self.logica_carros()
        self.passo_atual += 1
        self.desenhar()
        
        if self.em_execucao:
            delay = 10 if self.T_MAX > 5000 else 100
            self.root.after(delay, self.proximo_passo)

    def saltar_para_fim(self):
        self.em_execucao = False
        while self.passo_atual < self.T_MAX:
            self.logica_carros()
            self.passo_atual += 1
        self.desenhar()

        messagebox.showinfo(
            "Simulação Concluída", 
            f"Tempo limite atingido (Passo {self.T_MAX}).\n\n"
            f"Score Obtido: {self.score_atual}"
        )

    def desenhar(self):
        self.tam_celula = self._calcular_tamanho_celula()
        
        self.canvas.delete("all")
        self.lbl_passo.config(text=f"Passo: {self.passo_atual} / {self.T_MAX}")
        self.lbl_score.config(text=f"Score Atual: {self.score_atual} | Final: {self.pontuacao_final_calculada}")
        
        grid_w = self.C * self.tam_celula
        grid_h = self.R * self.tam_celula
        
        offset_x = max(0, (self.current_canvas_width - grid_w) // 2)
        offset_y = max(0, (self.current_canvas_height - grid_h) // 2)

        for i in range(self.R + 1):
            y = offset_y + i * self.tam_celula
            self.canvas.create_line(offset_x, y, offset_x + grid_w, y, fill=self.colors["grid_lines"], width=1)
        for j in range(self.C + 1):
            x = offset_x + j * self.tam_celula
            self.canvas.create_line(x, offset_y, x, offset_y + grid_h, fill=self.colors["grid_lines"], width=1)
                
        for carro in self.carros_sim:
            if carro["estado"] != 'CONCLUIDO':
                id_v = carro["viagens_atribuidas"][carro["idx_viagem_atual"]]
                a, b, x, y, _, _ = self.rides[id_v]
                marker_size = max(4, min(10, self.tam_celula // 2.5))
                
                start_x = offset_x + b * self.tam_celula + (self.tam_celula // 2)
                start_y = offset_y + a * self.tam_celula + (self.tam_celula // 2)
                
                end_x = offset_x + y * self.tam_celula + (self.tam_celula // 2)
                end_y = offset_y + x * self.tam_celula + (self.tam_celula // 2)
                
                self.canvas.create_oval(
                    start_x - marker_size, start_y - marker_size, 
                    start_x + marker_size, start_y + marker_size, 
                    fill=self.colors["ride_start"], outline=""
                )
                self.canvas.create_oval(
                    end_x - marker_size, end_y - marker_size, 
                    end_x + marker_size, end_y + marker_size, 
                    fill=self.colors["ride_end"], outline=""
                )
                
        for carro in self.carros_sim:
            cx = offset_x + carro["c"] * self.tam_celula + (self.tam_celula//2)
            cy = offset_y + carro["r"] * self.tam_celula + (self.tam_celula//2)
            
            if carro["estado"] == 'A_CAMINHO_PARTIDA': cor = self.colors["car_empty"]
            elif carro["estado"] == 'ESPERA': cor = self.colors["car_wait"]
            elif carro["estado"] == 'COM_PASSAGEIRO': cor = self.colors["car_full"]
            else: cor = self.colors["car_done"]
                
            car_size = max(6, min(14, self.tam_celula // 1.8))
            
            self.canvas.create_rectangle(
                cx - car_size, cy - car_size, 
                cx + car_size, cy + car_size, 
                fill=cor, outline=self.colors["bg_canvas"], width=2, tags="carro"
            )
            
            if self.tam_celula >= 20:
                self.canvas.create_text(cx, cy, text=str(carro["id"]), fill="white", font=("Segoe UI", 8, "bold"))

        self.canvas.configure(scrollregion=(0, 0, max(self.current_canvas_width, grid_w + 20), max(self.current_canvas_height, grid_h + 20)))

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