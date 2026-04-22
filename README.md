# Processador de Consultas SQL (Otimizador de Álgebra Relacional)

Este projeto foi desenvolvido como requisito para a disciplina de **Banco de Dados**. O objetivo é implementar um motor de processamento que recebe consultas SQL, valida os metadados, converte-os para Álgebra Relacional e aplica heurísticas de otimização através de um grafo de operadores.

---

## Contexto 

O projeto foi estruturado seguindo metodologias ágeis, dividindo os requisitos em **Histórias de Usuário (HUs)**:

* **HU1 - Entrada e Validação:** Interface para entrada da query e validação sintática/semântica contra o dicionário de dados.
* **HU2 - Conversão para Álgebra Relacional:** Tradução do SQL para notação matemática ($\sigma$, $\pi$, $\Join$).
* **HU3 e HU4 - Grafo de Operadores e Otimização:** Geração de um grafo visual utilizando a heurística de **Push-down Selection** (antecipação de seleções para redução de tuplas).
* **HU5 - Plano de Execução:** Detalhamento passo a passo da ordem de execução das operações no banco de dados.

---

## Tecnologias e Bibliotecas

O projeto foi desenvolvido em **Python 3**, utilizando:

* **Tkinter:** Interface gráfica (GUI).
* **sqlparse:** Motor de parsing para decomposição de comandos SQL.
* **NetworkX:** Criação e manipulação de estruturas de grafos.
* **Matplotlib:** Renderização visual do grafo de operadores dentro da interface.

---

## Como Executar no macOS

1.  **Clonar o repositório:**
    ```bash
    git clone [https://github.com/seu-utilizador/nome-do-repositorio.git](https://github.com/seu-utilizador/nome-do-repositorio.git)
    cd nome-do-repositorio
    ```

2.  **Instalar as dependências:**
    ```bash
    pip install sqlparse networkx matplotlib
    ```

3.  **Executar a aplicação:**
    ```bash
    python3 processador_consultas.py
    ```


---

## Dicionário de Dados (Metadados)

O sistema valida consultas com base no esquema de e-commerce fornecido, incluindo tabelas como:
- `cliente`, `pedido`, `produto`, `categoria`, `endereco`, `telefone`, entre outras.

## Heurísticas de Otimização Implementadas

O motor de otimização aplica as seguintes regras:
1.  **Seleção Antecipada:** Filtros (`WHERE`) são empurrados para as folhas do grafo para minimizar o processamento nas junções.
2.  **Eliminação de Produto Cartesiano:** As junções são tratadas preferencialmente via chaves primárias e estrangeiras definidas nos metadados.

---

**Equipe:** Diego Benevides, Mario Eduardo, Caua Bilhar