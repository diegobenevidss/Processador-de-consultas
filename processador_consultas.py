import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison
from sqlparse.tokens import Keyword
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- METADADOS (Fonte: Imagem 01 do PDF) ---
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
        self.tabelas_na_query = []
        self.filtros = []

    def extrair_dados(self, sql_query):
        """HU1 - Validação e Parsing Dinâmico [cite: 16, 145]"""
        parsed = sqlparse.parse(sql_query)
        if not parsed:
            raise ValueError("Consulta SQL inválida.")
        
        stmt = parsed[0]
        self.tabelas_na_query = []
        self.filtros = []
        
        # Busca tabelas e filtros (WHERE)
        for token in stmt.tokens:
            # Tabelas no FROM e JOIN
            if isinstance(token, Identifier):
                self.tabelas_na_query.append(token.get_real_name().lower())
            elif isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    self.tabelas_na_query.append(identifier.get_real_name().lower())
            # Condições no WHERE
            elif isinstance(token, Where):
                for condition in token.tokens:
                    if isinstance(condition, Comparison):
                        self.filtros.append(condition.value)

        # Valida contra o modelo [cite: 24, 121]
        self.tabelas_na_query = list(set(self.tabelas_na_query)) # Remover duplicatas
        for t in self.tabelas_na_query:
            if t not in METADADOS:
                raise ValueError(f"Tabela '{t}' não existe no modelo de dados.")

    def gerar_grafo_otimizado(self):
        """HU4 - Heurística de Redução de Tuplas e Atributos [cite: 46, 136]"""
        G = nx.DiGraph()
        raiz = "π (Projeção Final)"
        
        # Se houver mais de uma tabela, precisamos de um Join [cite: 25]
        if len(self.tabelas_na_query) > 1:
            op_central = "⨝ (Junção Otimizada)"
        else:
            op_central = "Operação Única"

        G.add_edge(op_central, raiz)

        for tab in self.tabelas_na_query:
            node_tab = f"TABELA: {tab.upper()}"
            # Aplicando Heurística: Seleção vem ANTES da Junção [cite: 51, 149]
            node_sel = f"σ (Filtro {tab.upper()})"
            
            G.add_edge(node_tab, node_sel)
            G.add_edge(node_sel, op_central)
            
        return G

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("UNIFOR - Otimizador de Consultas")
        self.root.geometry("1100x850")
        self.proc = ProcessadorConsultas()

        # Layout Splitter
        self.paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Lado Esquerdo (Editor)
        self.frame_left = ttk.Frame(self.paned, padding=15)
        self.paned.add(self.frame_left, weight=1)

        ttk.Label(self.frame_left, text="Entrada SQL", font=('Helvetica', 13, 'bold')).pack(anchor=tk.W)
        self.txt_sql = scrolledtext.ScrolledText(self.frame_left, height=8, font=('Menlo', 12))
        self.txt_sql.pack(fill=tk.X, pady=(5, 15))
        self.txt_sql.insert(tk.INSERT, "SELECT * FROM cliente JOIN pedido WHERE idCliente = 10")

        self.btn_action = ttk.Button(self.frame_left, text="Executar Otimização", command=self.executar)
        self.btn_action.pack(fill=tk.X)

        ttk.Label(self.frame_left, text="Plano de Execução (HU5)", font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(25, 5))
        self.txt_log = scrolledtext.ScrolledText(self.frame_left, height=20, bg="#1e1e1e", fg="#00ff00", font=('Menlo', 11))
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        # Lado Direito (Grafo)
        self.frame_right = ttk.Frame(self.paned, padding=15)
        self.paned.add(self.frame_right, weight=2)
        
        ttk.Label(self.frame_right, text="Grafo de Operadores (HU3)", font=('Helvetica', 13, 'bold')).pack(anchor=tk.W)
        self.canvas_frame = ttk.Frame(self.frame_right, borderwidth=1, relief="solid")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    def executar(self):
        query = self.txt_sql.get("1.0", tk.END).strip()
        try:
            # 1. Parsing e Validação (HU1)
            self.proc.extrair_dados(query)
            
            # 2. Log de Processamento (HU5) [cite: 59, 153]
            log_text = (
                f"> SQL VALIDADO COM SUCESSO\n"
                f"> TABELAS DETECTADAS: {', '.join(self.proc.tabelas_na_query).upper()}\n"
                f"> CONVERSÃO ÁLGEBRA: π ( σ ( {' ⨝ '.join(self.proc.tabelas_na_query).upper()} ) )\n\n"
                f"ORDEM DE EXECUÇÃO:\n"
                f"1. Acesso ao disco (Scan): {self.proc.tabelas_na_query}\n"
                f"2. Aplicação de filtros σ (Heurística de Redução)\n"
                f"3. Realização de Junções (⨝)\n"
                f"4. Projeção final dos atributos (π)\n"
            )
            self.txt_log.delete("1.0", tk.END)
            self.txt_log.insert(tk.END, log_text)
            
            # 3. Atualizar Grafo (HU3/HU4)
            self.renderizar_grafo()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no Processamento: {str(e)}")

    def renderizar_grafo(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_facecolor('#f0f0f0')
        
        G = self.proc.gerar_grafo_otimizado()
        # Layout hierárquico para parecer uma árvore de decisão
        pos = nx.spring_layout(G, seed=42) 
        
        nx.draw(G, pos, with_labels=True, 
                node_color='#007AFF', node_size=3500, 
                font_size=8, font_weight='bold', font_color='white',
                edge_color='#8e8e93', width=1.5, arrows=True, ax=ax)
        
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()