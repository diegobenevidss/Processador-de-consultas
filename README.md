# Processador de Consultas SQL (Otimizador de Álgebra Relacional)

Este projeto consiste na implementação de um **Processador de Consultas**, desenvolvido para a disciplina de Banco de Dados. O sistema simula o comportamento de um SGBD ao receber, validar, otimizar e planejar a execução de uma consulta SQL baseada em um modelo de dados de e-commerce.

---

## Funcionalidades (Histórias de Usuário)

O desenvolvimento foi guiado pelas seguintes Histórias de Usuário (HUs), conforme os requisitos do projeto:

* **HU1 - Entrada e Validação:** Interface gráfica que valida comandos `SELECT`, `FROM`, `WHERE` e `JOIN`. O sistema verifica a existência de tabelas e atributos no dicionário de dados, ignorando diferenças entre maiúsculas/minúsculas e espaços extras.
* **HU2 - Conversão para Álgebra Relacional:** Tradução automática da query para a representação teórica utilizando os operadores de seleção ($\sigma$), projeção ($\pi$) e junção ($\Join$).
* **HU3 - Construção do Grafo de Operadores:** Geração de um grafo em memória onde as folhas são as tabelas e a raiz é a projeção final.
* **HU4 - Otimização de Consulta:** Aplicação de heurísticas para reduzir o custo de execução:
    * **Redução de Tuplas (Push-down Selection):** Antecipação de seleções (filtros) para a base da árvore.
    * **Redução de Atributos:** Projeções aplicadas para minimizar o tráfego de dados.
    * **Evita Produto Cartesiano:** Priorização de junções restritivas através de chaves.
* **HU5 - Plano de Execução:** Exibição detalhada da ordem lógica de operações que o motor de busca executará no "disco".

---

## Tecnologias e Bibliotecas

* **Python**
* **Tkinter:** Interface Gráfica Funcional (GUI).
* **sqlparse:** Motor de parsing para decomposição e validação de comandos SQL.
* **NetworkX:** Criação e manipulação da estrutura de dados do grafo.
* **Matplotlib:** Renderização visual do Grafo de Operadores Otimizado.

---

## Dicionário de Dados (Metadados)

O sistema é alimentado por um esquema de e-commerce robusto. As tabelas validadas incluem:
- `cliente`, `pedido`, `produto`, `categoria`, `endereco`, `telefone`, `status`, `tipoendereco`, `tipocliente` e `pedido_has_produto`.

---

## Como Executar

### Pré-requisitos
Certifique-se de ter o Python instalado em sua máquina (macOS, Windows ou Linux).

### Instalação
1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/diegobenevidss/Processador-de-consultas.git
   cd "Projeto Banco Dados 2"