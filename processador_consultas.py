import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

METADADOS = {
    "categoria": ["idcategoria", "descricao"],
    "produto": ["idproduto", "nome", "descricao", "preco", "quantestoque", "categoria_idcategoria"],
    "tipocliente": ["idtipocliente", "descricao"],
    "cliente": ["idcliente", "nome", "email", "nascimento", "senha", "tipocliente_idtipocliente", "dataregistro"],
    "tipoendereco": ["idtipoendereco", "descricao"],
    "endereco": ["idendereco", "enderecopadrao", "logradouro", "numero", "complemento", "bairro", "cidade", "uf", "cep", "tipoendereco_idtipoendereco", "cliente_idcliente"],
    "telefone": ["numero", "cliente_idcliente"],
    "status": ["idstatus", "descricao"],
    "pedido": ["idpedido", "status_idstatus", "datapedido", "valortotalpedido", "cliente_idcliente"],
    "pedido_has_produto": ["idpedidoproduto", "pedido_idpedido", "produto_idproduto", "quantidade", "precounitario"]
}

class ProcessadorConsultas:
    def __init__(self):
        self.tabelas = []
        self.colunas_projecao = []
        self.filtros = {} 
        self.algebrista = ""

    def validar_e_parsear(self, sql_query):
        """HU1 - Entrada e Validação Completa"""
        query_limpa = " ".join(sql_query.split()).lower()
        parsed = sqlparse.parse(query_limpa)
        if not parsed: raise ValueError("Erro de sintaxe SQL.")
        
        stmt = parsed[0]
        self.tabelas = []
        self.colunas_projecao = []
        self.filtros = {}

        from_visto = False
        
        for token in stmt.tokens:
            if token.is_whitespace: continue
            
            if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
                from_visto = True
                continue
                
            if not from_visto:
                if isinstance(token, IdentifierList):
                    for iden in token.get_identifiers():
                        self.colunas_projecao.append(iden.get_real_name())
                elif isinstance(token, Identifier):
                    self.colunas_projecao.append(token.get_real_name())
                elif token.value == '*':
                    self.colunas_projecao.append("*")
            else:
                if isinstance(token, Where) or (token.ttype is sqlparse.tokens.Keyword and token.value.upper() in ['WHERE', 'GROUP BY', 'ORDER BY']):
                    break
                
                if isinstance(token, IdentifierList):
                    for iden in token.get_identifiers():
                        self.tabelas.append(iden.get_real_name())
                elif isinstance(token, Identifier):
                    self.tabelas.append(token.get_real_name())

        ignorar = ['join', 'inner', 'left', 'right', 'on']
        self.tabelas = [t for t in self.tabelas if t not in ignorar]

        if not self.tabelas: raise ValueError("Nenhuma tabela encontrada após o FROM.")
        for t in self.tabelas:
            if t not in METADADOS: raise ValueError(f"Tabela '{t}' não existe no dicionário de dados.")

        if "*" not in self.colunas_projecao:
            for col in self.colunas_projecao:
                valida = any(col in cols for cols in METADADOS.values())
                if not valida: raise ValueError(f"Coluna '{col}' não encontrada em nenhuma tabela.")

        where_clause = [t for t in stmt.tokens if isinstance(t, Where)]
        if where_clause:
            for condition in where_clause[0].tokens:
                if isinstance(condition, Comparison):
                    col_filtro = condition.left.value.split('.')[-1]
                    for tab in self.tabelas:
                        if col_filtro in METADADOS[tab]:
                            self.filtros[tab] = condition.value
                            break 
        
        self.gerar_algebra()

    def gerar_algebra(self):
        """HU2 - Conversão para Álgebra Relacional [cite: 28, 34]"""
        corpo = ""
        partes_join = []
        for tab in self.tabelas:
            if tab in self.filtros:
                partes_join.append(f"σ_{{{self.filtros[tab]}}}({tab})")
            else:
                partes_join.append(tab)
        
        corpo = " ⨝ ".join(partes_join)
        proj = ",".join(self.colunas_projecao)
        self.algebrista = f"π_{{{proj}}} ( {corpo} )"

    def construir_grafo(self):
        """HU3 e HU4 - Grafo e Otimização [cite: 35, 46, 58]"""
        G = nx.DiGraph()
        raiz = f"π: {','.join(self.colunas_projecao)}"
        
        no_juncao = "⨝ (Join)" if len(self.tabelas) > 1 else None
        
        if no_juncao:
            G.add_edge(no_juncao, raiz)
        
        for tab in self.tabelas:
            no_tabela = f"Tabela: {tab.upper()}"
            if tab in self.filtros:
                no_sel = f"σ: {self.filtros[tab]}"
                G.add_edge(no_tabela, no_sel)
                if no_juncao: G.add_edge(no_sel, no_juncao)
                else: G.add_edge(no_sel, raiz)
            else:
                if no_juncao: G.add_edge(no_tabela, no_juncao)
                else: G.add_edge(no_tabela, raiz)
        return G

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Processador de Consultas SQL - UNIFOR")
        self.root.geometry("1200x900")
        self.proc = ProcessadorConsultas()
        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TFrame", background="#f5f5f5")
        
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_container, padding=10)
        main_container.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Consulta SQL:", font=("Arial", 11, "bold")).pack(anchor="w")
        self.txt_sql = scrolledtext.ScrolledText(left_frame, height=10, font=("Consolas", 11))
        self.txt_sql.pack(fill=tk.X, pady=5)
        self.txt_sql.insert(tk.END, "SELECT nome, valorTotalPedido FROM cliente JOIN pedido WHERE idCliente = 5")

        ttk.Button(left_frame, text="Processar e Otimizar", command=self.processar).pack(fill=tk.X, pady=10)

        ttk.Label(left_frame, text="Álgebra Relacional (HU2):", font=("Arial", 11, "bold")).pack(anchor="w")
        self.txt_algebra = tk.Text(left_frame, height=4, font=("Times", 14), bg="#e8f0fe")
        self.txt_algebra.pack(fill=tk.X, pady=5)

        ttk.Label(left_frame, text="Plano de Execução (HU5):", font=("Arial", 11, "bold")).pack(anchor="w")
        self.txt_plano = scrolledtext.ScrolledText(left_frame, height=15, bg="#2d2d2d", fg="#88ff88")
        self.txt_plano.pack(fill=tk.BOTH, expand=True, pady=5)

        self.right_frame = ttk.Frame(main_container, padding=10)
        main_container.add(self.right_frame, weight=2)
        ttk.Label(self.right_frame, text="Estratégia de Execução (Grafo):", font=("Arial", 11, "bold")).pack(anchor="w")
        self.canvas_area = ttk.Frame(self.right_frame, relief="ridge", borderwidth=2)
        self.canvas_area.pack(fill=tk.BOTH, expand=True)

    def processar(self):
        sql = self.txt_sql.get("1.0", tk.END).strip()
        try:
            self.proc.validar_e_parsear(sql)
            
            self.txt_algebra.delete("1.0", tk.END)
            self.txt_algebra.insert(tk.END, self.proc.algebrista)

            plano = "--- PLANO DE EXECUÇÃO OTIMIZADO ---\n"
            for i, tab in enumerate(self.proc.tabelas, 1):
                plano += f"{i}. Acessar tabela '{tab.upper()}'\n"
                if tab in self.proc.filtros:
                    plano += f"   -> Aplicar Filtro Redutor (σ): {self.proc.filtros[tab]}\n"
            
            if len(self.proc.tabelas) > 1:
                plano += f"{len(self.proc.tabelas)+1}. Realizar Junção (⨝) dos resultados\n"
            
            plano += f"Final: Projetar colunas (π): {self.proc.colunas_projecao}\n"
            self.txt_plano.delete("1.0", tk.END)
            self.txt_plano.insert(tk.END, plano)

            self.desenhar_grafo()

        except Exception as e:
            messagebox.showerror("Erro de Validação", str(e))

    def desenhar_grafo(self):
        for w in self.canvas_area.winfo_children(): w.destroy()
        
        fig, ax = plt.subplots(figsize=(7, 7))
        G = self.proc.construir_grafo()
        
        pos = nx.spring_layout(G, seed=42)
        nx.draw(G, pos, with_labels=True, node_size=4000, node_color="skyblue", 
                font_size=9, font_weight="bold", arrows=True, ax=ax)
        
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()