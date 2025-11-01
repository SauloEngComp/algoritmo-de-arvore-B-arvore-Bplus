# algoritmo-de-arvore-B-arvore-Bplus
Visualizador Interativo de Estruturas de Dados em Árvore. Um projeto educacional em Python que usa Gradio para demonstrar o funcionamento de Árvores B e B+
# 🌳 Visualizador Interativo de Árvores B e B+

Este é um projeto educacional em Python que fornece uma interface web interativa para visualizar e entender o funcionamento das estruturas de dados Árvore B e Árvore B+.

O objetivo é permitir ao usuário inserir, remover e buscar chaves, observando visualmente como a árvore se transforma. A interface exibe um log detalhado de todas as operações complexas, como divisões (split), empréstimos (rotações) e fusões (merge), facilitando o aprendizado.

Este projeto usa **Gradio** para a interface web e **NetworkX** com **Matplotlib** para a renderização dos grafos, eliminando a necessidade de dependências externas.

---

## 🚀 Como Executar

1.  **Clone o repositório:**
    ```bash
    git clone [https://seu-link-para-o-repo.git](https://seu-link-para-o-repo.git)
    cd nome-do-diretorio
    ```

2.  **Instale as dependências:**
    ```bash
    pip install gradio networkx matplotlib
    ```

3.  **Execute o script:**
    ```bash
    python nome_do_seu_arquivo.py
    ```
    Abra o link local (ex: `http://127.0.0.1:7860`) no seu navegador.

---

## ✨ Estruturas Implementadas

O projeto está focado em duas variantes de Árvores-B, ambas usando um **grau mínimo t=3**:
* **Mínimo de chaves:** `t-1 = 2`
* **Máximo de chaves:** `2t-1 = 5`

### 1. Árvore B

A implementação clássica da Árvore B, onde chaves e dados podem residir em qualquer nó.

* **Inserir:** Executa a divisão (split) "1-para-2" quando um nó atinge 5 chaves, promovendo a chave mediana.
* **Remover:** Implementa a lógica completa de remoção *top-down* (preventiva), realizando "empréstimos" (rotação) ou "fusões" (merge) para garantir que nenhum nó visitado fique abaixo do mínimo de chaves.
* **Buscar:** Mostra o caminho percorrido de nó em nó.
* **Histórico:** Detalha todas as operações de divisão, empréstimo e fusão.

### 2. Árvore B+ (B-Plus)

A variante moderna usada pela maioria dos bancos de dados e sistemas de arquivos para indexação.

* **Visualização Diferenciada:**
    * Nós internos (guias) são mostrados em **azul**.
    * Nós folha (onde os dados residem) são mostrados em **verde**.
* **Lista Encadeada:** A visualização desenha as conexões da lista encadeada (em azul-claro) que liga todos os nós folha, permitindo buscas por intervalo.
* **Inserir:** Demonstra a lógica de divisão onde chaves são *copiadas* de folhas para pais, mas *movidas* de nós internos para pais.
* **Remover:** Implementa a lógica de remoção *post-order* (corretiva), balanceando a árvore de baixo para cima (com empréstimos e fusões) após a remoção na folha.

---

## ⚖️ Licença

Este projeto é licenciado sob a [Licença MIT](LICENSE).
