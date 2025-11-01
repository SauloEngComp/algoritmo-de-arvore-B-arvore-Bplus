import gradio as gr
import sys
import tempfile
import networkx as nx
import matplotlib.pyplot as plt

# ===================================================================
# ESTRUTURA DA ÁRVORE B (t=3) - AGORA COM REMOÇÃO
# ===================================================================

class NoB:
    """Classe para um Nó da Árvore B."""
    def __init__(self, t, arvore_b, folha=True):
        self.t = t
        self.folha = folha
        self.chaves = []
        self.filhos = []
        self.id = arvore_b.get_next_id()

class ArvoreB:
    """Classe para a Árvore B com grau mínimo t."""
    def __init__(self, t=3): 
        if t < 2: raise ValueError("O grau mínimo 't' da Árvore B deve ser pelo menos 2.")
        self.t = t
        self.log = []
        self.id_counter = 0
        self.raiz = NoB(t, self)

    def get_next_id(self):
        self.id_counter += 1
        return self.id_counter

    def buscar(self, k):
        self.log.clear()
        no_atual = self.raiz
        caminho = []
        while True:
            i = 0
            while i < len(no_atual.chaves) and k > no_atual.chaves[i]: i += 1
            caminho.append((no_atual, i))
            if i < len(no_atual.chaves) and k == no_atual.chaves[i]:
                self.log.append(f"Chave {k} encontrada no nó {no_atual.id}.")
                return (True, caminho)
            if no_atual.folha:
                self.log.append(f"Chegou à folha {no_atual.id}, chave {k} não encontrada.")
                return (False, caminho)
            self.log.append(f"Nó {no_atual.id}, descendo para o filho {i}.")
            no_atual = no_atual.filhos[i]

    # --- INSERÇÃO (Sem alterações) ---
    def inserir(self, k):
        try: k_int = int(k)
        except (ValueError, TypeError): return False, "❌ Erro: Chave deve ser um número inteiro."
        self.log.clear()
        encontrado, _ = self.buscar(k_int)
        if encontrado: return False, f"❌ Erro: Chave {k_int} já existe na árvore."
        raiz = self.raiz
        if len(raiz.chaves) == (2 * self.t - 1):
            self.log.append(f"Raiz {raiz.id} está cheia. Dividindo a raiz.")
            nova_raiz = NoB(self.t, self, folha=False)
            self.raiz = nova_raiz
            nova_raiz.filhos.append(raiz)
            self._dividir_filho(nova_raiz, 0)
            self._inserir_nao_cheio(nova_raiz, k_int)
        else:
            self._inserir_nao_cheio(raiz, k_int)
        return True, f"✅ Chave {k_int} inserida.\n" + "\n".join(self.log)

    def _inserir_nao_cheio(self, no, k):
        i = len(no.chaves) - 1
        if no.folha:
            self.log.append(f"Inserindo chave {k} no nó folha {no.id}.")
            no.chaves.append(None)
            while i >= 0 and k < no.chaves[i]: no.chaves[i+1] = no.chaves[i]; i -= 1
            no.chaves[i+1] = k
        else:
            while i >= 0 and k < no.chaves[i]: i -= 1
            i += 1
            self.log.append(f"Descendo para o filho {i} do nó {no.id}.")
            if len(no.filhos[i].chaves) == (2 * self.t - 1):
                self.log.append(f"Filho {no.filhos[i].id} está cheio. Dividindo...")
                self._dividir_filho(no, i)
                if k > no.chaves[i]:
                    i += 1
                    self.log.append(f"Chave {k} > mediana {no.chaves[i-1]}, descendo para novo filho {i}.")
                else:
                    self.log.append(f"Chave {k} <= mediana {no.chaves[i]}, continuando no filho {i}.")
            self._inserir_nao_cheio(no.filhos[i], k)

    def _dividir_filho(self, pai, i):
        t = self.t; filho_cheio = pai.filhos[i]
        novo_irmao = NoB(t, self, folha=filho_cheio.folha)
        novo_irmao.chaves = filho_cheio.chaves[t:]
        chave_mediana = filho_cheio.chaves[t-1]
        filho_cheio.chaves = filho_cheio.chaves[:t-1]
        if not filho_cheio.folha:
            novo_irmao.filhos = filho_cheio.filhos[t:]
            filho_cheio.filhos = filho_cheio.filhos[:t]
        pai.filhos.insert(i + 1, novo_irmao)
        pai.chaves.insert(i, chave_mediana)
        self.log.append(f"Divisão: Nó {filho_cheio.id} dividido. Chave {chave_mediana} promovida para {pai.id}. Novo nó {novo_irmao.id} criado.")
        
    # --- REMOÇÃO (Nova Implementação para Árvore B) ---
    def remover(self, k):
        try: k_int = int(k)
        except (ValueError, TypeError): return False, "❌ Erro: Chave deve ser um número inteiro."
        
        self.log.clear()
        encontrado, _ = self.buscar(k_int)
        if not encontrado:
            return False, f"❌ Erro: Chave {k_int} não encontrada na árvore."
        
        self.log.clear() # Limpa o log da busca
        self.log.append(f"Iniciando remoção da chave {k_int}...")
        self._remover(self.raiz, k_int)

        # Se a raiz ficar vazia, seu único filho se torna a nova raiz
        if len(self.raiz.chaves) == 0 and not self.raiz.folha and self.raiz.filhos:
            self.log.append(f"Raiz {self.raiz.id} ficou vazia. Nova raiz é {self.raiz.filhos[0].id}.")
            self.raiz = self.raiz.filhos[0]
            
        return True, f"✅ Chave {k_int} removida.\n" + "\n".join(self.log)

    def _remover(self, no, k):
        i = 0
        while i < len(no.chaves) and k > no.chaves[i]:
            i += 1

        if i < len(no.chaves) and no.chaves[i] == k:
            # Caso 1: 'k' está em 'no' (folha ou interno)
            if no.folha:
                self._remover_de_folha(no, i)
            else:
                self._remover_de_interno(no, i)
        else:
            # Caso 2: 'k' está na subárvore de 'no.filhos[i]'
            if no.folha:
                # Chave não encontrada (já tratado, mas por segurança)
                return
            
            filho = no.filhos[i]
            # Flag para saber se descemos para o último filho
            ultimo_filho = (i == len(no.chaves))
            
            # --- Ponto-chave da remoção B-Tree: GARANTIA TOP-DOWN ---
            # Garante que o filho para onde vamos descer tenha pelo menos 't' chaves
            if len(filho.chaves) < self.t:
                self._preencher_filho(no, i)
            
            # Se 'preencher' fundiu 'filho' com o anterior,
            # precisamos descer para o nó fundido, que agora está em 'i-1'.
            if ultimo_filho and i > len(no.chaves):
                 self._remover(no.filhos[i-1], k)
            else:
                 self._remover(no.filhos[i], k)
                 
    def _remover_de_folha(self, no, i):
        no.chaves.pop(i)
        self.log.append(f"Removida chave do nó folha {no.id}.")

    def _remover_de_interno(self, no, i):
        k = no.chaves[i]
        filho_esq = no.filhos[i]
        filho_dir = no.filhos[i+1]
        
        if len(filho_esq.chaves) >= self.t:
            # Caso A: Filho esquerdo tem chaves suficientes
            pred = self._get_predecessor(filho_esq)
            self.log.append(f"Substituindo {k} pelo predecessor {pred}.")
            no.chaves[i] = pred
            self._remover(filho_esq, pred)
        elif len(filho_dir.chaves) >= self.t:
            # Caso B: Filho direito tem chaves suficientes
            succ = self._get_sucessor(filho_dir)
            self.log.append(f"Substituindo {k} pelo sucessor {succ}.")
            no.chaves[i] = succ
            self._remover(filho_dir, succ)
        else:
            # Caso C: Ambos os filhos têm t-1 chaves. Fundir!
            self.log.append(f"Filhos de {k} têm apenas {self.t-1} chaves. Fundindo...")
            self._fundir(no, i)
            # 'k' foi movido para o filho esquerdo. Remove 'k' de lá.
            self._remover(filho_esq, k)

    def _preencher_filho(self, no_pai, i):
        """Garante que o filho 'i' de 'no_pai' tenha pelo menos 't' chaves."""
        self.log.append(f"Nó {no_pai.filhos[i].id} tem < {self.t} chaves. Tentando enriquecer...")
        
        if i != 0 and len(no_pai.filhos[i-1].chaves) >= self.t:
            self._emprestar_do_anterior(no_pai, i)
        elif i != len(no_pai.chaves) and len(no_pai.filhos[i+1].chaves) >= self.t:
            self._emprestar_do_proximo(no_pai, i)
        else:
            if i != len(no_pai.chaves):
                self._fundir(no_pai, i) # Funde com o irmão direito
            else:
                self._fundir(no_pai, i-1) # Funde com o irmão esquerdo

    def _emprestar_do_anterior(self, pai, i):
        filho = pai.filhos[i]
        irmao = pai.filhos[i-1]
        
        filho.chaves.insert(0, pai.chaves[i-1])
        pai.chaves[i-1] = irmao.chaves.pop()
        
        if not filho.folha:
            filho.filhos.insert(0, irmao.filhos.pop())
            
        self.log.append(f"-> Empréstimo (Rotação) do irmão esquerdo {irmao.id} para {filho.id}.")

    def _emprestar_do_proximo(self, pai, i):
        filho = pai.filhos[i]
        irmao = pai.filhos[i+1]
        
        filho.chaves.append(pai.chaves[i])
        pai.chaves[i] = irmao.chaves.pop(0)
        
        if not filho.folha:
            filho.filhos.append(irmao.filhos.pop(0))
        
        self.log.append(f"-> Empréstimo (Rotação) do irmão direito {irmao.id} para {filho.id}.")

    def _fundir(self, pai, i):
        filho = pai.filhos[i]
        irmao = pai.filhos[i+1]
        chave_pai = pai.chaves.pop(i)
        
        filho.chaves.append(chave_pai)
        filho.chaves.extend(irmao.chaves)
        
        if not filho.folha:
            filho.filhos.extend(irmao.filhos)
            
        pai.filhos.pop(i+1) # Remove o ponteiro para o antigo irmão
        
        self.log.append(f"-> Fusão (Merge) do nó {filho.id} com {irmao.id}. Chave {chave_pai} desceu de {pai.id}.")
        
    def _get_predecessor(self, no):
        atual = no
        while not atual.folha:
            atual = atual.filhos[-1]
        return atual.chaves[-1]

    def _get_sucessor(self, no):
        atual = no
        while not atual.folha:
            atual = atual.filhos[0]
        return atual.chaves[0]
        
# ===================================================================
# ESTRUTURA DA ÁRVORE B+ (t=3) - COM REMOÇÃO
# ===================================================================

class NoBPlus:
    def __init__(self, t, arvore_bplus, folha=True):
        self.t = t
        self.arvore = arvore_bplus
        self.folha = folha
        self.chaves = []
        self.filhos = []
        self.proximo = None 
        self.id = arvore_bplus.get_next_id()
        self.pai = None 

    def esta_em_underflow(self):
        if self.id == self.arvore.raiz.id:
            return False
        return len(self.chaves) < (self.t - 1)

class ArvoreBPlus:
    def __init__(self, t=3):
        if t < 2: raise ValueError("O grau mínimo 't' da Árvore B+ deve ser pelo menos 2.")
        self.t = t
        self.log = []
        self.id_counter = 0
        self.raiz = NoBPlus(t, self)

    def get_next_id(self):
        self.id_counter += 1
        return self.id_counter

    def buscar(self, k):
        self.log.clear()
        no_atual = self.raiz
        caminho = []
        while not no_atual.folha:
            i = 0
            while i < len(no_atual.chaves) and k > no_atual.chaves[i]:
                i += 1
            caminho.append((no_atual, i))
            self.log.append(f"Nó interno {no_atual.id}, descendo para o filho {i}.")
            no_atual = no_atual.filhos[i]
        caminho.append((no_atual, 0))
        i = 0
        while i < len(no_atual.chaves) and k > no_atual.chaves[i]:
            i += 1
        if i < len(no_atual.chaves) and k == no_atual.chaves[i]:
            self.log.append(f"Chave {k} encontrada no nó folha {no_atual.id}.")
            return (True, caminho, no_atual)
        else:
            self.log.append(f"Chegou à folha {no_atual.id}, chave {k} não encontrada.")
            return (False, caminho, None)

    def inserir(self, k):
        try: k_int = int(k)
        except (ValueError, TypeError): return False, "❌ Erro: Chave deve ser um número inteiro."
        self.log.clear()
        encontrado, _, _ = self.buscar(k_int)
        if encontrado: return False, f"❌ Erro: Chave {k_int} já existe na árvore."
        
        self.log.clear()
        raiz = self.raiz
        if len(raiz.chaves) == (2 * self.t - 1):
            self.log.append(f"Raiz {raiz.id} está cheia. Dividindo a raiz.")
            nova_raiz = NoBPlus(self.t, self, folha=False)
            self.raiz = nova_raiz
            nova_raiz.filhos.append(raiz)
            raiz.pai = nova_raiz
            self._dividir_filho(nova_raiz, 0)
            self._inserir_nao_cheio(nova_raiz, k_int)
        else:
            self._inserir_nao_cheio(raiz, k_int)
        return True, f"✅ Chave {k_int} inserida.\n" + "\n".join(self.log)

    def _inserir_nao_cheio(self, no, k):
        if no.folha:
            i = 0
            while i < len(no.chaves) and k > no.chaves[i]: i += 1
            no.chaves.insert(i, k)
            self.log.append(f"Inserindo chave {k} no nó folha {no.id}.")
        else:
            i = 0
            while i < len(no.chaves) and k > no.chaves[i]: i += 1
            self.log.append(f"Descendo do nó {no.id} para o filho {i}.")
            filho = no.filhos[i]
            if len(filho.chaves) == (2 * self.t - 1):
                self.log.append(f"Filho {filho.id} está cheio. Dividindo...")
                self._dividir_filho(no, i)
                if k > no.chaves[i]:
                    i += 1
            no.filhos[i].pai = no
            self._inserir_nao_cheio(no.filhos[i], k)

    def _dividir_filho(self, pai, i):
        t = self.t
        filho_cheio = pai.filhos[i]
        novo_irmao = NoBPlus(t, self, folha=filho_cheio.folha)
        novo_irmao.pai = pai
        
        if filho_cheio.folha:
            idx_mediano = self.t - 1
            chave_mediana_copiada = filho_cheio.chaves[idx_mediano]
            novo_irmao.chaves = filho_cheio.chaves[idx_mediano:]
            filho_cheio.chaves = filho_cheio.chaves[:idx_mediano]
            novo_irmao.proximo = filho_cheio.proximo
            filho_cheio.proximo = novo_irmao
            pai.chaves.insert(i, chave_mediana_copiada)
            pai.filhos.insert(i + 1, novo_irmao)
            self.log.append(f"Divisão (Folha): Nó {filho_cheio.id} dividido. Chave {chave_mediana_copiada} COPIADA para {pai.id}. Novo nó folha {novo_irmao.id} criado.")
        else:
            idx_mediano = t - 1
            chave_mediana_movida = filho_cheio.chaves.pop(idx_mediano)
            novo_irmao.chaves = filho_cheio.chaves[idx_mediano:]
            filho_cheio.chaves = filho_cheio.chaves[:idx_mediano]
            novo_irmao.filhos = filho_cheio.filhos[t:]
            filho_cheio.filhos = filho_cheio.filhos[:t]
            for filho in novo_irmao.filhos: filho.pai = novo_irmao
            pai.chaves.insert(i, chave_mediana_movida)
            pai.filhos.insert(i + 1, novo_irmao)
            self.log.append(f"Divisão (Interno): Nó {filho_cheio.id} dividido. Chave {chave_mediana_movida} MOVIDA para {pai.id}. Novo nó {novo_irmao.id} criado.")

    def remover(self, k):
        try: k_int = int(k)
        except (ValueError, TypeError): return False, "❌ Erro: Chave deve ser um número inteiro."
        
        self.log.clear()
        encontrado, _, no_folha = self.buscar(k_int)
        
        if not encontrado:
            return False, f"❌ Erro: Chave {k_int} não encontrada na árvore."
        
        self.log.clear()
        self.log.append(f"Iniciando remoção da chave {k_int}...")
        
        self._remover_recursivo(no_folha, k_int)
        
        # Se a raiz ficar vazia, seu único filho se torna a nova raiz
        if len(self.raiz.chaves) == 0 and not self.raiz.folha and self.raiz.filhos:
            self.log.append(f"Raiz {self.raiz.id} ficou vazia. Nova raiz é {self.raiz.filhos[0].id}.")
            self.raiz = self.raiz.filhos[0]
            self.raiz.pai = None
            
        return True, f"✅ Chave {k_int} removida.\n" + "\n".join(self.log)

    def _remover_recursivo(self, no, k):
        # 1. Remove a chave (só acontece na folha na primeira chamada)
        if k in no.chaves:
            no.chaves.remove(k)
            self.log.append(f"Chave {k} removida do nó {no.id}.")
        
        # 2. Verifica Underflow
        if no.esta_em_underflow():
            self.log.append(f"Nó {no.id} está em underflow. Balanceando...")
            pai = no.pai
            i = pai.filhos.index(no)
            
            # Tenta emprestar do irmão esquerdo
            if i > 0 and len(pai.filhos[i-1].chaves) > (self.t - 1):
                self._emprestar(no, pai.filhos[i-1], pai, i-1, 'esq')
            # Tenta emprestar do irmão direito
            elif i < len(pai.filhos) - 1 and len(pai.filhos[i+1].chaves) > (self.t - 1):
                self._emprestar(no, pai.filhos[i+1], pai, i, 'dir')
            # Precisa fundir
            else:
                if i > 0:
                    self._fundir(pai.filhos[i-1], no, pai, i-1)
                else:
                    self._fundir(no, pai.filhos[i+1], pai, i)
        
        # 3. Atualiza Chave do Pai
        # Esta é a parte crucial: Se a menor chave de um nó muda,
        # a chave-guia no pai deve ser atualizada.
        if no.pai:
            self._atualizar_chaves_pais(no)

    def _emprestar(self, no_vazio, irmao, pai, idx_chave_pai, direcao):
        if direcao == 'esq':
            if no_vazio.folha:
                irmao_chave = irmao.chaves.pop()
                no_vazio.chaves.insert(0, irmao_chave)
                pai.chaves[idx_chave_pai] = no_vazio.chaves[0]
            else:
                irmao_filho = irmao.filhos.pop()
                irmao_filho.pai = no_vazio
                no_vazio.filhos.insert(0, irmao_filho)
                pai_chave = pai.chaves[idx_chave_pai]
                irmao_chave = irmao.chaves.pop()
                no_vazio.chaves.insert(0, pai_chave)
                pai.chaves[idx_chave_pai] = irmao_chave
            self.log.append(f"-> Empréstimo (Rotação) do irmão esquerdo {irmao.id} para {no_vazio.id}.")
                
        elif direcao == 'dir':
            if no_vazio.folha:
                irmao_chave = irmao.chaves.pop(0)
                no_vazio.chaves.append(irmao_chave)
                pai.chaves[idx_chave_pai] = irmao.chaves[0]
            else:
                irmao_filho = irmao.filhos.pop(0)
                irmao_filho.pai = no_vazio
                no_vazio.filhos.append(irmao_filho)
                pai_chave = pai.chaves[idx_chave_pai]
                irmao_chave = irmao.chaves.pop(0)
                no_vazio.chaves.append(pai_chave)
                pai.chaves[idx_chave_pai] = irmao_chave
            self.log.append(f"-> Empréstimo (Rotação) do irmão direito {irmao.id} para {no_vazio.id}.")

    def _fundir(self, no_esq, no_dir, pai, idx_chave_pai):
        self.log.append(f"-> Fusão (Merge) do nó {no_dir.id} no nó {no_esq.id}.")
        
        if no_esq.folha:
            no_esq.chaves.extend(no_dir.chaves)
            no_esq.proximo = no_dir.proximo
            pai.chaves.pop(idx_chave_pai)
            pai.filhos.pop(idx_chave_pai + 1)
        else:
            chave_pai_desce = pai.chaves.pop(idx_chave_pai)
            no_esq.chaves.append(chave_pai_desce)
            no_esq.chaves.extend(no_dir.chaves)
            for filho in no_dir.filhos:
                filho.pai = no_esq
                no_esq.filhos.append(filho)
            pai.filhos.pop(idx_chave_pai + 1)
            
        if pai.esta_em_underflow():
            self._balancear(pai)
            
    def _atualizar_chaves_pais(self, no):
        """Sobe na árvore recursivamente e atualiza as chaves-guia."""
        pai = no.pai
        if not pai:
            return

        i = pai.filhos.index(no)
        # Se 'no' não for o primeiro filho, a chave-guia
        # no pai é a chave no índice i-1
        if i > 0:
            nova_chave_guia = no.chaves[0] if no.chaves else None
            # Se a chave guia do pai for diferente da menor chave atual do filho
            # E a chave guia *antiga* ainda estiver no filho (significa que não era a chave removida)
            if nova_chave_guia is not None and pai.chaves[i-1] != nova_chave_guia:
                 # Checa se a chave antiga (a guia) ainda está na árvore
                 if pai.chaves[i-1] in no.chaves:
                    self.log.append(f"Atualizando guia no pai {pai.id}: {pai.chaves[i-1]} -> {nova_chave_guia}")
                    pai.chaves[i-1] = nova_chave_guia
                    self._atualizar_chaves_pais(pai) # Propaga a mudança para cima
        
        # Propaga a verificação para cima
        if pai.pai:
            self._atualizar_chaves_pais(pai)


# ===================================================================
# FUNÇÕES DE VISUALIZAÇÃO (NetworkX + Matplotlib)
# ===================================================================

def hierarchical_layout(G, root=None):
    if root is None:
        roots = [n for n, d in G.in_degree() if d == 0]
        if not roots: return {}
        root = roots[0]
    pos = {}; levels = {root: 0}; queue = [root]; visited = {root}; level_nodes = [[root]]
    while queue:
        parent = queue.pop(0)
        children = [child for child in G.neighbors(parent) if child not in visited]
        if not children: continue
        level = levels[parent] + 1
        if len(level_nodes) <= level: level_nodes.append([])
        for child in children:
            if child not in visited: visited.add(child); levels[child] = level; level_nodes[level].append(child); queue.append(child)
    for i, level in enumerate(level_nodes):
        level_width = len(level)
        for j, node in enumerate(level): pos[node] = ((j - level_width / 2.0 + 0.5) * 2.5, -i * 1.5)
    return pos

def renderizar_com_matplotlib(G, labels, node_colors, edge_labels=None, leaf_edges=None, pos=None):
    if not G.nodes: return None
    plt.figure(figsize=(12, 8))
    ax = plt.gca(); ax.set_axis_off()
    
    if pos is None:
        pos = hierarchical_layout(G)
    
    if G.number_of_nodes() == 1:
        ax.set_ylim(-1.5, 1.5); ax.set_xlim(-2.5, 2.5)

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', width=1.5, alpha=0.9)
    
    if leaf_edges:
        nx.draw_networkx_edges(G, pos, edgelist=leaf_edges, ax=ax, 
                               edge_color='#00FFFF', style='dashed', width=2.0,
                               connectionstyle='arc3,rad=0.1') 

    for node in G.nodes():
        x, y = pos[node]
        label = labels.get(node, '')
        color = node_colors.get(node, '#FFFFFF')
        ax.text(x, y, label, ha='center', va='center',
                size=9, weight='bold', color='black',
                bbox=dict(facecolor=color, edgecolor='none', boxstyle='round,pad=1.0', alpha=0.9))
    
    if edge_labels: 
        nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=edge_labels, font_color='red')
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
            plt.savefig(tmpfile.name, format='png', bbox_inches='tight'); plt.close(); return tmpfile.name
    except Exception as e:
        print(f"Erro ao salvar a imagem: {e}"); plt.close(); return None

def formatar_b_para_exibicao(arvore, caminho_destacado=None):
    if not arvore.raiz or (not arvore.raiz.chaves and arvore.raiz.folha): return None
    G = nx.DiGraph(); labels = {}; node_colors = {}
    highlight_nodes = {no.id for no, _ in caminho_destacado} if caminho_destacado else set()
    
    def construir_grafo(no):
        if not no: return
        label = " | ".join(map(str, no.chaves)) if no.chaves else "[]"
        label = f"<{label}>"
        G.add_node(no.id); labels[no.id] = label
        cor = '#f1c40f' if no.id in highlight_nodes else '#e74c3c'
        if len(no.chaves) == (2 * arvore.t - 1): cor = '#d35400'
        if len(no.chaves) < (arvore.t-1) and no.id != arvore.raiz.id: cor = '#F08080' # Underflow
        node_colors[no.id] = cor
        if not no.folha:
            for filho in no.filhos: G.add_edge(no.id, filho.id); construir_grafo(filho)
                
    construir_grafo(arvore.raiz)
    return renderizar_com_matplotlib(G, labels, node_colors)

def formatar_bplus_para_exibicao(arvore, caminho_destacado=None):
    if not arvore.raiz or (not arvore.raiz.chaves and arvore.raiz.folha): return None
    G = nx.DiGraph(); labels = {}; node_colors = {}
    leaf_nodes = [] 
    highlight_nodes = {no.id for no, _ in caminho_destacado} if caminho_destacado else set()

    def construir_grafo(no):
        if not no: return
        label = " | ".join(map(str, no.chaves)) if no.chaves else "[]"
        label = f"<{label}>"
        G.add_node(no.id); labels[no.id] = label
        
        if no.folha:
            cor = '#f1c40f' if no.id in highlight_nodes else '#2ecc71' 
            if len(no.chaves) == (2 * arvore.t - 1): cor = '#27ae60' 
            if no.esta_em_underflow(): cor = '#F08080'
            leaf_nodes.append(no)
        else:
            cor = '#f1c40f' if no.id in highlight_nodes else '#3498db' 
            if len(no.chaves) == (2 * arvore.t - 1): cor = '#2980b9' 
            if no.esta_em_underflow(): cor = '#F08080'
        
        node_colors[no.id] = cor
        if not no.folha:
            for filho in no.filhos: 
                G.add_edge(no.id, filho.id); 
                construir_grafo(filho)
                
    construir_grafo(arvore.raiz)
    
    pos = hierarchical_layout(G)
    folhas_ordenadas = sorted([no for no in leaf_nodes if no.id in pos], key=lambda n: pos[n.id][0])
    leaf_edges = []
    
    for i in range(len(folhas_ordenadas) - 1):
        no_atual = folhas_ordenadas[i]
        proximo_no = folhas_ordenadas[i+1]
        if no_atual.proximo and no_atual.proximo.id == proximo_no.id:
             leaf_edges.append((no_atual.id, proximo_no.id))

    return renderizar_com_matplotlib(G, labels, node_colors, leaf_edges=leaf_edges, pos=pos)


# ===================================================================
# FUNÇÕES DE INTERFACE (GRADIO)
# ===================================================================

def inserir_b(arv, val):
    if not val: return arv, gr.update(), "❌ Erro: Forneça um valor."
    sucesso, msg = arv.inserir(val); imagem = formatar_b_para_exibicao(arv)
    return arv, gr.update(value=imagem), msg
def remover_b(arv, val):
    if not val: return arv, gr.update(), "❌ Erro: Forneça um valor."
    sucesso, msg = arv.remover(val); imagem = formatar_b_para_exibicao(arv)
    return arv, gr.update(value=imagem), msg
def buscar_b(arv, val):
    if not val: return gr.update(), "Forneça um valor para buscar."
    try: k_int = int(val)
    except (ValueError, TypeError): return gr.update(), "❌ Erro: Chave deve ser um número inteiro."
    encontrado, caminho = arv.buscar(k_int)
    caminho_formatado = []
    for no, idx_filho in caminho:
        chaves_str = ",".join(map(str, no.chaves)) if no.chaves else "[]"
        caminho_formatado.append(f"Nó {no.id} [{chaves_str}] -> descendo p/ filho {idx_filho}")
    if encontrado: msg = f"✅ Chave {val} encontrada!\n\nHistórico do Caminho:\n" + "\n".join(caminho_formatado)
    else: msg = f"❌ Chave {val} não encontrada.\n\nHistórico do Caminho:\n" + "\n".join(caminho_formatado)
    imagem = formatar_b_para_exibicao(arv, caminho)
    return gr.update(value=imagem), msg

def inserir_bplus(arv, val):
    if not val: return arv, gr.update(), "❌ Erro: Forneça um valor."
    sucesso, msg = arv.inserir(val)
    imagem = formatar_bplus_para_exibicao(arv)
    return arv, gr.update(value=imagem), msg
def remover_bplus(arv, val):
    if not val: return arv, gr.update(), "❌ Erro: Forneça um valor."
    sucesso, msg = arv.remover(val)
    imagem = formatar_bplus_para_exibicao(arv)
    return arv, gr.update(value=imagem), msg
def buscar_bplus(arv, val):
    if not val: return gr.update(), "Forneça um valor para buscar."
    try: k_int = int(val)
    except (ValueError, TypeError): return gr.update(), "❌ Erro: Chave deve ser um número inteiro."
    encontrado, caminho, _ = arv.buscar(k_int)
    caminho_formatado = []
    for no, idx_filho in caminho:
        chaves_str = ",".join(map(str, no.chaves)) if no.chaves else "[]"
        tipo = "Folha" if no.folha else "Interno"
        caminho_formatado.append(f"Nó {tipo} {no.id} [{chaves_str}]")
    if encontrado: 
        msg = f"✅ Chave {val} encontrada!\n\nHistórico do Caminho:\n" + "\n".join(caminho_formatado)
    else: 
        msg = f"❌ Chave {val} não encontrada.\n\nHistórico do Caminho:\n" + "\n".join(caminho_formatado)
    imagem = formatar_bplus_para_exibicao(arv, caminho)
    return gr.update(value=imagem), msg

# ===================================================================
# CONSTRUÇÃO DA INTERFACE (GRADIO)
# ===================================================================
with gr.Blocks(theme=gr.themes.Soft(), css="footer {display: none !important}") as demo:
    
    estado_b = gr.State(lambda: ArvoreB(t=3)) 
    estado_bplus = gr.State(lambda: ArvoreBPlus(t=3))

    gr.Markdown("# 🌳 Interface para Árvores B e B+")
    gr.Markdown("Selecione a aba correspondente à árvore que deseja manipular.")

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.TabItem("Árvore B"):
                    gr.Markdown("Árvore com grau mínimo **t=3**.\n- Mínimo de chaves: t-1 = **2**\n- Máximo de chaves: 2t-1 = **5**")
                    gr.Markdown("### Inserir / Remover / Buscar"); input_b_valor = gr.Textbox(label="Valor da Chave (inteiro)")
                    with gr.Row():
                        btn_b_inserir = gr.Button("Inserir", variant="primary")
                        btn_b_remover = gr.Button("Remover", variant="stop")
                    btn_b_buscar = gr.Button("Buscar")
                    gr.Markdown("*(Remoção da B-Tree implementada!)*") # ATUALIZADO
                
                with gr.TabItem("Árvore B+"):
                    gr.Markdown("Árvore com grau mínimo **t=3**.\n- Mínimo de chaves: t-1 = **2**\n- Máximo de chaves: 2t-1 = **5**")
                    gr.Markdown("Nós internos são guias (azuis). Dados reais estão nas folhas (verdes).")
                    gr.Markdown("### Inserir / Remover / Buscar"); input_bplus_valor = gr.Textbox(label="Valor da Chave (inteiro)")
                    with gr.Row():
                        btn_bplus_inserir = gr.Button("Inserir", variant="primary")
                        btn_bplus_remover = gr.Button("Remover", variant="stop")
                    btn_bplus_buscar = gr.Button("Buscar")
                    gr.Markdown("*(Remoção da B+ implementada!)*")

            gr.Markdown("### Status da Ação")
            output_status = gr.Textbox(label="Resultado", interactive=False, lines=10)

        with gr.Column(scale=2):
            gr.Markdown("### Visualização da Árvore")
            output_visualizacao = gr.Image(label="Estrutura Atual", height=600, interactive=False)

    # Conexões da Árvore B
    btn_b_inserir.click(fn=inserir_b, inputs=[estado_b, input_b_valor], outputs=[estado_b, output_visualizacao, output_status])
    btn_b_remover.click(fn=remover_b, inputs=[estado_b, input_b_valor], outputs=[estado_b, output_visualizacao, output_status])
    btn_b_buscar.click(fn=buscar_b, inputs=[estado_b, input_b_valor], outputs=[output_visualizacao, output_status])
    
    # Conexões da Árvore B+
    btn_bplus_inserir.click(fn=inserir_bplus, inputs=[estado_bplus, input_bplus_valor], outputs=[estado_bplus, output_visualizacao, output_status])
    btn_bplus_remover.click(fn=remover_bplus, inputs=[estado_bplus, input_bplus_valor], outputs=[estado_bplus, output_visualizacao, output_status])
    btn_bplus_buscar.click(fn=buscar_bplus, inputs=[estado_bplus, input_bplus_valor], outputs=[output_visualizacao, output_status])

demo.launch()