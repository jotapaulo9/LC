# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.24.2",
#     "ortools>=9.15",
# ]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo


    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Trabalho Prático: Sudoku Genérico como CSP


    ## Contexto


    O Sudoku clássico — uma grelha $n^2 \times n^2$ onde cada linha,
    cada coluna e cada bloco $n \times n$ tem de conter todos os
    valores de $1$ a $n^2$ sem repetições — é um exemplo canónico de
    **problema de satisfação de restrições (CSP)**: a "regra" é sempre
    a mesma (um conjunto de células tem de ter valores todos
    diferentes), o que muda de linha para linha, de coluna para
    coluna e de bloco para bloco é apenas **que células pertencem a
    esse conjunto**.


    Isso sugere uma abstração única — um grupo de células com a
    restrição "todos diferentes", opcionalmente com algumas células já
    fixas a um valor — a partir da qual linhas, colunas, blocos e
    ainda outras variantes de Sudoku (diagonais, regiões irregulares,
    grelhas sobrepostas, etc.) podem ser todas construídas sem
    duplicar lógica de restrição nenhuma.


    Este é um problema de **modelação e resolução de CSP**. Cabe-te a
    ti escolher a técnica de resolução e justificá-la — o enunciado
    não fornece código de modelação nem de apresentação de resultados,
    apenas a interface que o teu notebook tem de expor (secção
    seguinte) para poder ser testado automaticamente.


    ## Objetivo


    Construir, num notebook Marimo, um gerador/resolvedor de Sudoku
    $n^2 \times n^2$ (com $n$ parametrizável, tipicamente $n=3$) que:


    1. representa qualquer **grupo de células com restrição "todos
       diferentes"** através de uma classe genérica (secção
       "`box` — grupo genérico de células"),
    2. constrói **linhas, colunas e blocos** como casos particulares
       dessa classe genérica — os blocos através de uma especialização
       dedicada a blocos $n \times n$, as linhas e colunas através de
       uma especialização dedicada a sequências retas de células
       (secção "`cube` e `path`"),
    3. gera **aleatoriamente** um subconjunto de células já
       preenchidas (as "pistas" iniciais do puzzle), usando a mesma
       abstração genérica (secção "Geração aleatória de pistas"),
    4. monta o modelo completo (linhas + colunas + blocos + pistas) e
       o resolve como CSP, devolvendo a grelha preenchida ou sinalizando
       que não há solução (secção "Resolução").
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Requisitos obrigatórios


    O teu notebook tem de expor, com este comportamento, os seguintes
    elementos (os nomes propostos abaixo são sugestões que facilitam a
    correção automática — podes usar outros, desde que documentes a
    correspondência):


    ### `box` — grupo genérico de células (R1)


    Uma classe que representa **qualquer** conjunto de células da
    grelha às quais se aplica a restrição "todos os valores
    diferentes", com algumas delas possivelmente já fixas:


    - guarda internamente uma associação `(linha, coluna) → valor ou
      None` (`None` = célula livre; um inteiro = célula fixa/pinada a
      esse valor);
    - um construtor que aceita opcionalmente esse conjunto inicial de
      células (vazio por omissão);
    - um método `add(i, j, val=None)` que acrescenta a célula `(i,
      j)` ao grupo, opcionalmente fixando-a a `val`, e que **rejeita**
      (levanta exceção) coordenadas fora da grelha ou valores fora do
      intervalo $[1, n^2]$;
    - uma forma de obter a representação do grupo como matriz $n^2
      \times n^2$, com zeros nas células não pertencentes ao grupo ou
      não fixas, e o valor fixo nas restantes.


    Esta classe **não deve saber nada** sobre linhas, colunas, blocos
    ou Sudoku — só sabe lidar com "um conjunto de células, algumas
    fixas". Essa generalidade é o que te vai permitir, mais tarde,
    tratar da mesma forma linhas, colunas, blocos, pistas aleatórias
    e (nas extensões opcionais) diagonais ou regiões irregulares.


    ### `cube` e `path` — duas formas concretas de grupo (R2, R3)


    A partir da classe genérica, define duas especializações:


    - **R2.** Um grupo que representa o **bloco $n \times n$** cujo
      canto superior esquerdo é a célula $(i \cdot n,\ j \cdot n)$,
      parametrizado pelos índices de bloco $(i, j)$ com $0 \le i, j <
      n$.
    - **R3.** Um grupo que representa o **troço reto** (horizontal ou
      vertical) de células entre duas coordenadas `inicio` e `fim`,
      inclusive — tem de funcionar tanto para `fim` "depois" de
      `inicio` como "antes" (ou seja, percorrer a sequência em
      qualquer sentido).


    ### Geração aleatória de pistas (R4)


    Uma função que devolve um grupo (`box`) com $k$ células escolhidas
    aleatoriamente na grelha, cada uma fixa a um valor também escolhido
    aleatoriamente em $[1, n^2]$ ($k$ deve ter um valor por omissão
    razoável, por exemplo da ordem de $n$). Repara que esta função
    **não precisa de nenhuma classe nova** — o resultado é, de novo,
    apenas um `box`.


    ### Modelo e resolução (R5, R6)


    - **R5.** Um modelo de CSP para a grelha $n^2 \times n^2$, com uma
      variável inteira por célula, cada uma no intervalo $[1, n^2]$;
      um método que recebe **um número arbitrário de grupos**
      (`box`, `cube`, `path`, ou pistas aleatórias — o modelo não deve
      distinguir a sua origem) e, para cada um, impõe que as suas
      células sejam todas diferentes e fixa as que tiverem valor
      atribuído; e um método de resolução que devolve a grelha
      preenchida ou sinaliza, de forma distinguível, que o puzzle não
      tem solução.
    - **R6.** Um Sudoku $n^2 \times n^2$ completo é montado juntando:
      todas as linhas, todas as colunas, todos os blocos $n \times n$
      e (pelo menos) um grupo de pistas aleatórias — e resolvido.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Como testar/validar


    O teu notebook (ou um ficheiro de testes à parte) tem de verificar
    automaticamente, para uma grelha resolvida:


    - que cada linha, cada coluna e cada bloco $n \times n$ contém
      exatamente os valores $1 \ldots n^2$, sem repetições;
    - que as células fixadas pelas pistas aleatórias mantêm, na
      solução, o valor com que foram fixadas;
    - que `add` (ou equivalente) rejeita coordenadas fora da grelha e
      valores fora de $[1, n^2]$.


    Corre o fluxo completo (gerar pistas aleatórias → montar linhas +
    colunas + blocos + pistas → resolver → validar) pelo menos uma vez
    com $n=3$ (Sudoku clássico $9\times9$) e confirma que também
    funciona com outro valor de $n$ (ex.: $n=2$, grelha $4\times4$),
    para garantires que nada está fixo a $9\times9$ no teu código.


    ## O que é deixado ao teu critério


    O enunciado define **que abstrações** o notebook tem de expor e
    **que comportamento** têm de ter, não **como** as deves
    implementar. Ficam ao teu critério, desde que justificadas no
    notebook:


    - a técnica e biblioteca de resolução do CSP (CP-SAT do OR-Tools
      é a sugestão da disciplina, mas és livre de escolher outra
      abordagem de Lógica Computacional, justificando a escolha);
    - a estrutura de dados interna do grupo genérico (dicionário,
      matriz esparsa, etc.);
    - a forma de apresentar a grelha resultante (texto, tabela,
      `mo.ui`, gráfico — o que achares mais claro);
    - o comportamento exato quando o puzzle gerado aleatoriamente não
      tem solução (podes, por exemplo, tentar novas pistas aleatórias
      até obteres um puzzle solúvel, ou simplesmente reportar o
      insucesso — justifica a escolha).






    ## Extensões opcionais (bónus)


    A generalidade do `box` é o que torna estas extensões possíveis
    sem tocar no modelo CSP em si — cada uma acrescenta apenas **novos
    grupos** de células:


    - **Sudoku diagonal (X-Sudoku)**: acrescenta um grupo (`box`, sem
      precisar de nova subclasse) para cada uma das duas diagonais
      principais, também elas restritas a "todos diferentes".
    - **Sudoku irregular (jigsaw)**: substitui os blocos $n \times n$
      regulares por regiões de forma arbitrária mas do mesmo tamanho,
      cada uma representada como um `box` construído célula a célula
      em vez de por `cube`.
    - **Hyper-Sudoku / Windoku**: acrescenta 4 blocos extra (também
      `box`, de forma semelhante a `cube` mas sem estarem alinhados
      com a grelha $n \times n$ de blocos) sobrepostos aos existentes.
    - **Escala**: mostra que o teu código funciona (talvez mais devagar)
      para $n=6$ (grelha $36\times36$) sem alterações, e discute os
      limites de desempenho que encontraste.
    - **Sudoku tridimensional** define a estrutura de "boxes" numa grelha $n^2\times n^2\times n^2$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Resolução

    ## Organização do notebook

    O notebook segue a ordem dos requisitos: primeiro a classe genérica (R1), depois as
    especializações (R2, R3), a geração de pistas (R4), o modelo CSP (R5) e a montagem do
    Sudoku completo (R6). No fim, estão a apresentação da grelha e os testes de validação.

    Correspondência de nomes com o enunciado:

    | Enunciado | Notebook |
    |---|---|
    | `box`, `add` | `box`, `box.add` |
    | representação como matriz | `box.matrix()` |
    | `cube`, `path` | `cube`, `path` |
    | geração aleatória de pistas | `pistas_aleatorias(k, n)` |
    | modelo CSP e resolução | classe `Modelo`, métodos `add` e `solve` |
    | Sudoku completo | `resolver_sudoku(n, k)` |
    | validação | `validar` e `verificar_add` |

    ## Parâmetro n

    `N` define o tamanho dos blocos; a grelha tem N^2 * N^2 células. Todas as classes
    e funções recebem `n` como parâmetro, com `N` como valor por omissão. Assim é possível
    criar grelhas de outros tamanhos (por exemplo n=2 nos testes) sem alterar o código.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## R1 — `box`: grupo genérico de células

    Um `box` representa qualquer conjunto de células cujos valores têm de ser todos
    diferentes. Algumas dessas células podem já estar fixas a um valor.

    **Estrutura de dados:** um dicionário `cells` que associa cada célula `(linha, coluna)`
    ao seu valor fixo, ou a `None` se a célula estiver livre. Escolhemos um dicionário porque
    corresponde diretamente à associação pedida no enunciado, só guarda as células que
    pertencem ao grupo, e permite saber rapidamente se uma célula está no grupo.

    - O **construtor** aceita opcionalmente um dicionário inicial. Cada célula desse
      dicionário passa pelo `add`, por isso também é validada.
    - O método **`add(i, j, val)`** acrescenta uma célula e levanta `ValueError` se as
      coordenadas estiverem fora da grelha ou se o valor estiver fora de [1, n^2].
    - O método **`matrix()`** devolve a matriz n^2 * n^2 pedida: o valor fixo nas
      células fixas e 0 em todas as outras.

    A classe não sabe nada sobre linhas, colunas, blocos ou Sudoku. A única coisa que
    conhece é o tamanho da grelha, necessário para validar as coordenadas e os valores.
    """)
    return


@app.cell
def _():
    N = 3
    return (N,)


@app.cell
def _(N):
    class box:
        """Grupo genérico de células com a restrição 'todos diferentes'.

        Guarda um dicionário (linha, coluna) -> valor ou None.
        None = célula livre; inteiro = célula fixa a esse valor.
        """

        def __init__(self, cells=None, n=N):
            self.n = n
            self.size = n * n          # lado da grelha (n^2)
            self.cells = {}
            if cells:
                for (i, j), val in cells.items():
                    self.add(i, j, val)   # assim também é validado

        def add(self, i, j, val=None):
            if not (0 <= i < self.size and 0 <= j < self.size):
                raise ValueError(f"Célula ({i}, {j}) fora da grelha")
            if val is not None and not (1 <= val <= self.size):
                raise ValueError(f"Valor {val} fora do intervalo [1, {self.size}]")
            self.cells[(i, j)] = val

        def matrix(self):
            """Matriz n^2*n^2: valor fixo nas células fixas, 0 no resto."""
            m = [[0] * self.size for _ in range(self.size)]
            for (i, j), val in self.cells.items():
                if val is not None:
                    m[i][j] = val
            return m

    return (box,)


@app.cell
def _(box):
    _b = box()
    _b.add(0, 0, 5)
    _b.add(4, 7)        # celula livre
    for _linha in _b.matrix():
        print(_linha)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## R2 — `cube`: bloco n * n

    `cube` é uma subclasse de `box`: herda o dicionário, o `add` e o `matrix`. O construtor
    recebe os índices do bloco $(i, j)$ e acrescenta as n * n células desse bloco,
    das linhas $i \cdot n$ a $i \cdot n + n - 1$ e das colunas $j \cdot n$ a $j \cdot n + n - 1$.

    Não é preciso validar $i$ e $j$ à parte: se forem inválidos, as células calculadas
    ficam fora da grelha e o `add` rejeita-as.
    """)
    return


@app.cell
def _(N, box):
    class cube(box):
        """Bloco n*n número (i, j). O canto superior esquerdo é a célula (i*n, j*n)."""

        def __init__(self, i, j, n=N):
            super().__init__(n=n)      # cria um box vazio
            for linha in range(i * n, i * n + n):
                for coluna in range(j * n, j * n + n):
                    self.add(linha, coluna)

    return (cube,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## R3 — `path`: troço reto de células

    `path` é outra subclasse de `box`. Recebe duas células, `inicio` e `fim`:

    - se estão na **mesma linha**, o troço é horizontal;
    - se estão na **mesma coluna**, o troço é vertical;
    - caso contrário, não há troço reto e é levantado um `ValueError`.

    Para funcionar em qualquer sentido, percorremos sempre do menor índice para o maior
    (`min` e `max`). Assim, `path((0, 2), (0, 6))` e `path((0, 6), (0, 2))` dão exatamente
    as mesmas células. A ordem não importa, porque a restrição "todos diferentes" só
    depende de quais células estão no grupo.

    As linhas e colunas do Sudoku são `path`s que vão de uma ponta à outra da grelha.
    """)
    return


@app.cell
def _(N, box):
    class path(box):
        """Troço reto (horizontal ou vertical) entre inicio e fim, inclusive."""

        def __init__(self, inicio, fim, n=N):
            super().__init__(n=n)
            i1, j1 = inicio
            i2, j2 = fim
            if i1 == i2:                       # mesma linha -> horizontal
                for coluna in range(min(j1, j2), max(j1, j2) + 1):
                    self.add(i1, coluna)
            elif j1 == j2:                     # mesma coluna -> vertical
                for linha in range(min(i1, i2), max(i1, i2) + 1):
                    self.add(linha, j1)
            else:
                raise ValueError("inicio e fim têm de estar na mesma linha ou coluna")

    return (path,)


@app.cell
def _(cube, path):
    print("cube(1, 2):", list(cube(1, 2).cells))
    print("path -> :", list(path((0, 2), (0, 6)).cells))
    print("path <- :", list(path((0, 6), (0, 2)).cells))
    print("vertical:", list(path((8, 4), (5, 4)).cells))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## R4 — Geração aleatória de pistas

    A função `pistas_aleatorias(k, n)` devolve um `box` normal, sem nenhuma classe nova,
    com k células escolhidas ao acaso, cada uma fixa a um valor aleatório em [1, n^2].
    Por omissão, k = n.

    Usamos `random.sample`, que escolhe elementos diferentes, tanto para as células como
    para os valores.

    **Porquê valores diferentes?** O modelo (R5) trata todos os grupos da mesma forma e
    impõe "todos diferentes" em cada um, incluindo o grupo das pistas. Se duas pistas
    tivessem o mesmo valor, o próprio grupo das pistas seria impossível de satisfazer,
    mesmo que essas duas células não estivessem em conflito num Sudoku normal.
    """)
    return


@app.cell
def _(N, box):
    import random

    def pistas_aleatorias(k=N, n=N):
        """Devolve um box com k células aleatórias, cada uma fixa a um valor aleatório.

        Os valores são todos diferentes porque o modelo impõe 'todos diferentes'
        também neste grupo (trata todos os grupos da mesma forma).
        """
        tamanho = n * n
        todas = [(i, j) for i in range(tamanho) for j in range(tamanho)]
        celulas = random.sample(todas, k)                    # k células diferentes
        valores = random.sample(range(1, tamanho + 1), k)    # k valores diferentes
        pistas = box(n=n)
        for (i, j), val in zip(celulas, valores):
            pistas.add(i, j, val)
        return pistas

    return pistas_aleatorias, random


@app.cell
def _(pistas_aleatorias):


    _p = pistas_aleatorias()
    print(_p.cells)
    for _linha in _p.matrix():
        print(_linha)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## R5 — Modelo CSP e resolução

    **Técnica escolhida:** CP-SAT do OR-Tools, a sugestão da disciplina. É adequado a este
    problema porque tem a restrição global `AllDifferent`, que corresponde exatamente ao
    conceito de `box`: cada grupo dá origem a uma restrição `AllDifferent`, sem ser preciso
    escrever restrições célula a célula. O resolvedor usa essa estrutura para eliminar
    valores impossíveis muito mais depressa do que uma pesquisa exaustiva.

    O modelo tem:

    - **uma variável inteira por célula**, com domínio [1, n^2];
    - o método **`add(*grupos)`**, que aceita um número qualquer de grupos. Para cada
      grupo, impõe `AllDifferent` sobre as suas células e fixa as células com valor. O
      método só usa o dicionário `cells`, por isso não distingue se o grupo é um `box`, um
      `cube`, um `path` ou um grupo de pistas;
    - o método **`solve()`**, que devolve a grelha preenchida (lista de listas) ou `None`
      quando não há solução.

    **Semente aleatória:** o CP-SAT é determinista e, com poucas pistas, encontraria quase
    sempre a mesma solução. Damos-lhe uma semente aleatória para que cada execução possa
    encontrar uma solução diferente. Isto não afeta a correção: a solução continua a
    cumprir todas as restrições.
    """)
    return


@app.cell
def _(N, random):
    from ortools.sat.python import cp_model

    class Modelo:
        """Modelo CSP de uma grelha n^2 * n^2: uma variável inteira por célula, com valor em [1, n^2]."""

        def __init__(self, n=N):
            self.n = n
            self.size = n * n
            self.modelo = cp_model.CpModel()
            self.x = {}                          # (linha, coluna) -> variável
            for i in range(self.size):
                for j in range(self.size):
                    self.x[(i, j)] = self.modelo.new_int_var(1, self.size, f"x_{i}_{j}")

        def add(self, *grupos):
            """Recebe quantos grupos quisermos (box, cube, path, pistas): todos tratados igual."""
            for g in grupos:
                if g.n != self.n:
                    raise ValueError("O grupo não é do mesmo tamanho que a grelha")
                # 1) as células do grupo têm valores todos diferentes
                variaveis = [self.x[c] for c in g.cells]
                self.modelo.add_all_different(variaveis)
                # 2) as células fixas ficam com o seu valor
                for (i, j), val in g.cells.items():
                    if val is not None:
                        self.modelo.add(self.x[(i, j)] == val)

        def solve(self):
            """Devolve a grelha resolvida (lista de listas) ou None se não houver solução."""
            solver = cp_model.CpSolver()
            # semente aleatória: cada execução pode encontrar uma solução diferente
            solver.parameters.random_seed = random.randint(0, 1000000)
            solver.parameters.randomize_search = True
            estado = solver.solve(self.modelo)
            if estado == cp_model.OPTIMAL or estado == cp_model.FEASIBLE:
                return [[solver.value(self.x[(i, j)]) for j in range(self.size)]
                        for i in range(self.size)]
            return None

    return (Modelo,)


@app.cell
def _(Modelo, N, box, cube, path):
    _m = Modelo()
    for _i in range(N * N):
        _m.add(path((_i, 0), (_i, N * N - 1)))    # linha _i
        _m.add(path((0, _i), (N * N - 1, _i)))    # coluna _i
    for _a in range(N):
        for _b in range(N):
            _m.add(cube(_a, _b))                  # bloco (_a, _b)

    for _linha in _m.solve():
        print(_linha)

    # caso impossível: duas células do mesmo grupo fixas ao mesmo valor
    _imp = Modelo()
    _imp.add(box({(0, 0): 5, (0, 1): 5}))
    print("Impossível →", _imp.solve())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## R6 — Sudoku completo

    `resolver_sudoku(n, k)` monta o Sudoku juntando no modelo:

    - as n^2 linhas: `path((i, 0), (i, n^2 -1))`;
    - as n^2 colunas: `path((0, j), (n^2 -1, j))`;
    - os n^2 blocos: `cube(i, j)`;
    - um grupo de pistas aleatórias.

    **Quando o puzzle não tem solução:** gera novas pistas e tenta de novo, até 100
    tentativas. Escolhemos esta opção porque o objetivo é produzir um Sudoku resolvido, e
    pistas impossíveis são apenas azar na geração aleatória. Em cada tentativa é criado um
    modelo novo, para que as restrições das pistas anteriores não fiquem no modelo. Se
    todas as tentativas falharem, a função devolve `None`, e isso é reportado.

    Na prática, como as pistas têm valores diferentes e são poucas, o puzzle é quase
    sempre resolúvel à primeira tentativa.
    """)
    return


@app.cell
def _(Modelo, N, cube, path, pistas_aleatorias):
    def resolver_sudoku(n=N, k=N, max_tentativas=100):
        """Monta linhas + colunas + blocos + pistas aleatórias e resolve.

        Se as pistas não tiverem solução, gera pistas novas (até max_tentativas).
        Devolve (grelha, pistas, nº de tentativas); grelha = None se falhar sempre.
        """
        tamanho = n * n
        linhas = [path((i, 0), (i, tamanho - 1), n=n) for i in range(tamanho)]
        colunas = [path((0, j), (tamanho - 1, j), n=n) for j in range(tamanho)]
        blocos = [cube(i, j, n=n) for i in range(n) for j in range(n)]

        for tentativa in range(1, max_tentativas + 1):
            pistas = pistas_aleatorias(k, n)
            modelo = Modelo(n)
            modelo.add(*linhas, *colunas, *blocos, pistas)
            grelha = modelo.solve()
            if grelha is not None:
                return grelha, pistas, tentativa
        return None, None, max_tentativas

    return (resolver_sudoku,)


@app.cell
def _(resolver_sudoku):
    grelha, pistas, tentativas = resolver_sudoku()
    print("Tentativas:", tentativas)
    print("Pistas:", pistas.cells)
    for _linha in grelha:
        print(_linha)
    return grelha, pistas


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Apresentação da grelha

    A grelha é mostrada como uma tabela HTML. As linhas grossas separam os blocos
    n * n e são calculadas a partir de n, por isso funcionam para qualquer tamanho.

    As pistas aparecem em negrito com fundo sombreado, e os valores encontrados pelo
    resolvedor aparecem a cinzento. Assim distingue-se o que foi dado à partida do que foi
    deduzido, como num Sudoku em papel.
    """)
    return


@app.cell
def _(N, mo):
    def mostrar_grelha(grelha, pistas=None, n=N):
        """Mostra a grelha como tabela HTML: blocos separados por linhas grossas,
        pistas em destaque (negrito e fundo sombreado), restantes valores a cinzento."""
        if grelha is None:
            return mo.md("**Sem solução.**")

        tamanho = n * n
        fixas = pistas.cells if pistas is not None else {}

        html = "<table style='border-collapse: collapse; font-family: monospace; font-size: 18px;'>"
        for i in range(tamanho):
            html += "<tr>"
            for j in range(tamanho):
                cima = "3px" if i % n == 0 else "1px"
                esquerda = "3px" if j % n == 0 else "1px"
                baixo = "3px" if i == tamanho - 1 else "1px"
                direita = "3px" if j == tamanho - 1 else "1px"
                estilo_celula = (f"border-top: {cima} solid; border-left: {esquerda} solid; "
                                 f"border-bottom: {baixo} solid; border-right: {direita} solid; "
                                 "width: 32px; height: 32px; text-align: center;")
                if (i, j) in fixas:
                    estilo_celula += " background: rgba(128, 128, 128, 0.3);"
                    estilo_numero = "font-weight: bold;"
                else:
                    estilo_numero = "color: #8a8a8a;"
                html += (f"<td style='{estilo_celula}'>"
                         f"<span style='{estilo_numero}'>{grelha[i][j]}</span></td>")
            html += "</tr>"
        html += "</table>"
        return mo.Html(html)

    return (mostrar_grelha,)


@app.cell
def _(grelha, mostrar_grelha, pistas):
    mostrar_grelha(grelha, pistas)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Testes de validação

    - **`validar(grelha, pistas, n)`** verifica que cada linha, coluna e bloco contém
      exatamente os valores 1 ... n^2, e que cada pista mantém o seu valor. Para cada
      linha, coluna ou bloco, comparamos o conjunto dos seus valores com
      {1, ..., n^2}. Como há n^2 posições, conjuntos iguais significam que todos
      os valores aparecem e nenhum se repete.
    - **`validar_add(n)`** verifica que o `add` rejeita coordenadas negativas, coordenadas
      acima do limite, e valores fora de [1, n^2].

    A célula de testes corre o fluxo completo 10 vezes para n=2 (grelha 4 * 4) e
    10 vezes para n=3 (grelha 9 * 9), o que confirma que nada está fixo a
    9 * 9. No fim, estraga de propósito uma grelha válida, para confirmar que os
    testes detetam mesmo os erros.
    """)
    return


@app.cell
def _(N):
    def validar(grelha, pistas, n=N):
        """Verifica linhas, colunas, blocos e pistas. Lança AssertionError se algo falhar."""
        tamanho = n * n
        certos = set(range(1, tamanho + 1))      # {1, 2, ..., n^2}

        for i in range(tamanho):
            assert set(grelha[i]) == certos, f"Linha {i} inválida"
            coluna = [grelha[r][i] for r in range(tamanho)]
            assert set(coluna) == certos, f"Coluna {i} inválida"

        for a in range(n):
            for b in range(n):
                bloco = [grelha[r][c] for r in range(a * n, a * n + n)
                                      for c in range(b * n, b * n + n)]
                assert set(bloco) == certos, f"Bloco ({a}, {b}) inválido"

        for (i, j), val in pistas.cells.items():
            assert grelha[i][j] == val, f"Pista ({i}, {j}) = {val} não foi respeitada"

        return True

    return (validar,)


@app.cell
def _(N, box):
    def verificar_add(n=N):
        """Verifica que o add rejeita coordenadas fora da grelha e valores fora de [1, n^2]."""
        tamanho = n * n
        invalidos = [(-1, 0, None),          # linha negativa
                     (tamanho, 0, None),     # linha a mais
                     (0, tamanho, None),     # coluna a mais
                     (0, 0, 0),              # valor abaixo de 1
                     (0, 0, tamanho + 1)]    # valor acima de n^2
        for i, j, val in invalidos:
            rejeitado = False
            try:
                box(n=n).add(i, j, val)
            except ValueError:
                rejeitado = True
            assert rejeitado, f"add({i}, {j}, {val}) devia ter sido rejeitado"
        return True

    return (verificar_add,)


@app.cell
def _(grelha, pistas, resolver_sudoku, validar, verificar_add):
    # 1) a grelha que está a ser mostrada
    validar(grelha, pistas)

    # 2) fluxo completo várias vezes, para n=2 (4*4) e n=3 (9*9)
    for _n in [2, 3]:
        for _vez in range(10):
            _g, _p, _t = resolver_sudoku(n=_n, k=_n)
            assert _g is not None, f"n={_n}: não encontrou solução"
            validar(_g, _p, n=_n)
        verificar_add(_n)
        print(f"n={_n}: 10 Sudokus válidos, pistas respeitadas, add rejeita inválidos")

    # 3) os testes apanham mesmo erros? Estragamos uma grelha de propósito
    _errada = [_linha[:] for _linha in grelha]
    _errada[0][0], _errada[0][1] = _errada[0][1], _errada[0][0]   # troca duas células
    _apanhou = False
    try:
        validar(_errada, pistas)
    except AssertionError as _erro:
        _apanhou = True
        print("Grelha estragada de propósito ->", _erro)
    assert _apanhou, "validar devia ter detetado a grelha estragada"
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Utilização de LMM

    Neste trabalho foi usado um modelo de linguagem llm como apoio.
    Foi usado para:

    - explicar conceitos (CSP, CP-SAT, Python e Marimo);
    - sugerir e rever o código de cada requisito;
    - verificar que o notebook corre e cumpre o enunciado;
    - ajudar a compreender e a explicar cada parte do código.

    Todo o código foi lido, testado e compreendido pelo grupo antes de ser entregue.

    https://share.gemini.google/msahl6WOkk9a
    """)
    return


if __name__ == "__main__":
    app.run()
