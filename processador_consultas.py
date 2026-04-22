import tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison
from sqlparse.tokens import Keyword, DML
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- METADADOS (Baseado na Imagem 01 do PDF) ---
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
        self.colunas = []
        self.condicoes = []
        self.joina_list = []

    def validar_e_parsear(self, sql_query):
        """HU1 - Entrada e Validação da Consulta"""
        parsed = sqlparse.parse(sql_query)
        if not parsed:
            raise ValueError("Consulta SQL inválida.")
        
        stmt = parsed[0]
        self.tabelas = []
        self.colunas = []
        
        # Extração básica de tokens
        from_seen = False
        for token in stmt.tokens:
            if token.ttype is Keyword and token.value.upper() == 'FROM':
                from_seen = True
            if from_seen and isinstance(token, Identifier):
                self.tabelas.append(token.get_real_name().lower())
            elif from_seen and isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    self.tabelas.append(identifier.get_real_name().lower())

        # Validação de Metadados
        for t in self.tabelas:
            if t not in METADADOS:
                raise ValueError(f"Tabela '{t}' não existe no modelo.")
        
        return "Consulta SQL válida e parseada com sucesso."

    def converter_algebra(self):
        """HU2 - Conversão para Álgebra Relacional"""
        # Exemplo simplificado de representação textual
        tab_str = " ⨝ ".join(self.tabelas).upper()
        return f"π (σ ({tab_str}))"

    def gerar_grafo(self, otimizado=False):
        """HU3 e HU4 - Construção e Otimização do Grafo"""
        G = nx.DiGraph()
        
        if not otimizado:
            # Grafo Ingênuo: Tabelas -> Join -> Seleção -> Projeção
            raiz = "π (Projeção Final)"
            G.add_node(raiz)
            sel = "σ (Condições)"
            G.add_edge(sel, raiz)
            
            prev_join = sel
            for i, tab in enumerate(self.tabelas):
                node_tab = f"Tabela: {tab.upper()}"
                G.add_edge(node_tab, prev_join)
        else:
            # HU4 - Otimizado: Filtros aplicados logo após as tabelas (Push-down selection)
            raiz = "π (Projeção Otimizada)"
            G.add_node(raiz)
            join_op = "⨝ (Junção)"
            G.add_edge(join_op, raiz)
            
            for tab in self.tabelas:
                node_tab = f"Tabela: {tab.upper()}"
                node_sel = f"σ (Redução Tuplas {tab.upper()})"
                G.add_edge(node_tab, node_sel)
                G.add_edge(node_sel, join_op)
                
        return G

# --- INTERFACE GRÁFICA (Tkinter) ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("UNIFOR - Processador de Consultas SQL")
        self.root.geometry("1000x800")
        self.proc = ProcessadorConsultas()

        # Input
        tk.Label(root, text="Digite sua consulta SQL:", font=('Arial', 12, 'bold')).pack(pady=5)
        self.txt_sql = scrolledtext.ScrolledText(root, height=5, width=80)
        self.txt_sql.pack(pady=5)
        self.txt_sql.insert(tk.INSERT, "SELECT * FROM cliente JOIN pedido ON cliente.idCliente = pedido.Cliente_idCliente WHERE idCliente = 1")

        # Botões
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Processar e Otimizar", command=self.processar, bg="#4CAF50", fg="black").pack(side=tk.LEFT, padx=5)

        # Output Textual
        self.txt_output = scrolledtext.ScrolledText(root, height=10, width=80, bg="#f0f0f0")
        self.txt_output.pack(pady=5)

        # Container para o Grafo
        self.fig_frame = tk.Frame(root)
        self.fig_frame.pack(fill=tk.BOTH, expand=True)

    def processar(self):
        query = self.txt_sql.get("1.0", tk.END).strip()
        try:
            # HU1
            res = self.proc.validar_e_parsear(query)
            # HU2
            algebra = self.proc.converter_algebra()
            
            # HU5 - Plano de Execução (Texto)
            plano = (
                f"--- RESULTADOS ---\n"
                f"1. Status: {res}\n"
                f"2. Álgebra Relacional: {algebra}\n"
                f"3. Plano de Execução:\n"
                f"   a. Carregar tabelas: {', '.join(self.proc.tabelas)}\n"
                f"   b. Aplicar Heurística: Redução de tuplas (Seleção antecipada)\n"
                f"   c. Executar Junções\n"
                f"   d. Projeção Final dos Atributos\n"
            )
            
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, plano)
            
            self.plot_grafo()
            
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def plot_grafo(self):
        """Exibe o grafo otimizado na interface"""
        for widget in self.fig_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(8, 4))
        G = self.proc.gerar_grafo(otimizado=True)
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=8, font_weight='bold', arrows=True, ax=ax)
        
        canvas = FigureCanvasTkAgg(fig, master=self.fig_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()