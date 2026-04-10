import tkinter as tk

def distance(a, b, x, y):
    return abs(a - x) + abs(b - y)

class VisualizadorHashcode:
    # Nota que agora recebemos as funções func_greedy e func_smart
    def __init__(self, R, C, F, T_MAX, B, rides, func_greedy, func_smart):
        self.R = R
        self.C = C
        self.F = F
        self.T_MAX = T_MAX
        self.rides = rides
        self.B = B
        
        # Guardar as funções passadas pelo main.py
        self.func_greedy = func_greedy
        self.func_smart = func_smart
        
        # Correr o Smart Greedy por defeito ao abrir
        self.cars_schedule, self.pontuacao_final_calculada = self.func_smart(self.F, self.B, self.rides)
        
        self.passo_atual = 0
        self.em_execucao = False
        self.score_atual = 0
        
        self.tam_celula = min(50, 800 // max(R, C)) if max(R,C) > 0 else 50
        
        self.carros_sim = []
        self.reset_carros()

        self.root = tk.Tk()
        self.root.title("Simulador Hash Code")
        
        self.setup_ui()
        self.desenhar()

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
        
        # Recalcular as rotas com o algoritmo escolhido
        if tipo == 1:
            self.cars_schedule, self.pontuacao_final_calculada = self.func_greedy(self.F, self.B, self.rides)
            self.lbl_algo_ativo.config(text="Ativo: Greedy Simples")
        else:
            self.cars_schedule, self.pontuacao_final_calculada = self.func_smart(self.F, self.B, self.rides)
            self.lbl_algo_ativo.config(text="Ativo: Smart Greedy")
            
        # Repor a simulação do zero
        self.restart()

    def setup_ui(self):
        # --- PAINEL DOS ALGORITMOS (NOVO) ---
        painel_algos = tk.Frame(self.root)
        painel_algos.pack(pady=10)
        
        tk.Label(painel_algos, text="Escolher Algoritmo:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        btn_greedy = tk.Button(painel_algos, text="Greedy Simples", command=lambda: self.mudar_algoritmo(1))
        btn_greedy.pack(side=tk.LEFT, padx=5)
        
        btn_smart = tk.Button(painel_algos, text="Smart Greedy", command=lambda: self.mudar_algoritmo(2))
        btn_smart.pack(side=tk.LEFT, padx=5)
        
        self.lbl_algo_ativo = tk.Label(painel_algos, text="Ativo: Smart Greedy", fg="blue", font=("Arial", 10, "italic"))
        self.lbl_algo_ativo.pack(side=tk.LEFT, padx=15)

        # --- PAINEL DE CONTROLO DO TEMPO ---
        painel_topo = tk.Frame(self.root)
        painel_topo.pack(pady=5)
        
        self.lbl_passo = tk.Label(painel_topo, text="Passo: 0", font=("Arial", 12))
        self.lbl_passo.pack(side=tk.LEFT, padx=10)
        
        self.lbl_score = tk.Label(painel_topo, text="Score: 0", font=("Arial", 12, "bold"), fg="green")
        self.lbl_score.pack(side=tk.LEFT, padx=10)
        
        tk.Button(painel_topo, text="Play", command=self.play, bg="lightgreen").pack(side=tk.LEFT, padx=5)
        tk.Button(painel_topo, text="Pause", command=self.pause, bg="salmon").pack(side=tk.LEFT, padx=5)
        tk.Button(painel_topo, text="+1 Passo", command=self.proximo_passo).pack(side=tk.LEFT, padx=5)
        tk.Button(painel_topo, text="Restart", command=self.restart, bg="lightblue").pack(side=tk.LEFT, padx=5)
        
        largura = self.C * self.tam_celula
        altura = self.R * self.tam_celula
        self.canvas = tk.Canvas(self.root, width=largura, height=altura, bg="white")
        self.canvas.pack(padx=20, pady=20)

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
            a, b, x, y, s, f = self.rides[id_viagem]
            
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
        
        if max(self.R, self.C) < 100:
            for i in range(self.R + 1):
                self.canvas.create_line(0, i*self.tam_celula, self.C*self.tam_celula, i*self.tam_celula, fill="#eee")
            for j in range(self.C + 1):
                self.canvas.create_line(j*self.tam_celula, 0, j*self.tam_celula, self.R*self.tam_celula, fill="#eee")
                
        for carro in self.carros_sim:
            if carro["estado"] != 'CONCLUIDO':
                id_v = carro["viagens_atribuidas"][carro["idx_viagem_atual"]]
                a, b, x, y, s, f = self.rides[id_v]
                self.canvas.create_oval(b*self.tam_celula+5, a*self.tam_celula+5, b*self.tam_celula+15, a*self.tam_celula+15, fill="green", outline="")
                self.canvas.create_oval(y*self.tam_celula+5, x*self.tam_celula+5, y*self.tam_celula+15, x*self.tam_celula+15, fill="red", outline="")
                
        cores = ["blue", "purple", "orange", "black"]
        for carro in self.carros_sim:
            cy = carro["r"] * self.tam_celula + (self.tam_celula//2)
            cx = carro["c"] * self.tam_celula + (self.tam_celula//2)
            cor = "gray" if carro["estado"] == 'CONCLUIDO' else cores[carro["id"] % len(cores)]
            self.canvas.create_rectangle(cx-10, cy-10, cx+10, cy+10, fill=cor)
            self.canvas.create_text(cx, cy, text=str(carro["id"]), fill="white")

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