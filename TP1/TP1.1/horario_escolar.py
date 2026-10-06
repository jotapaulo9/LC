# /// script
# dependencies = ["marimo"]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #TP1.1

    ##Grupo 19
    João Pontes, A111657

    João Paulo, A110393

    Objetivo: Criar um horário escolar semanal cumpridor de determinadas restrições (consultar horario_escolar_enunciado.py).

    ---

    **Importação de Bibliotecas e Inicialização de Dados**

    Nesta primeira célula, procedemos à importação das ferramentas necessárias para a resolução do problema. Utilizamos o `pandas` para a leitura e manipulação eficiente dos ficheiros `.csv` fornecidos, e a biblioteca `ortools.sat.python` (especificamente o módulo `cp_model`), que nos permite modelar o problema de alocação de horários.
    Aqui, definimos também as estruturas de dados nevrálgicas, tais como os dias da semana, os períodos letivos diários e um dicionário que mapeia cada disciplina à sua respetiva carga horária semanal.
    """)
    return


@app.cell
def _():
    import marimo as mo
    from pathlib import Path
    import pandas as pd #escolhemos utilizar o pandas para ler .csv
    from ortools.sat.python import cp_model

    pathway = Path("dados") #leitura de dados
    classes = pd.read_csv(pathway/"turmas.csv")
    crooms = pd.read_csv(pathway/"salas.csv")
    availability = pd.read_csv(pathway/"disponibilidade_excecoes.csv")
    subjects = pd.read_csv(pathway/"disciplinas.csv")
    days = ["Seg", "Ter", "Qua", "Qui", "Sex"]
    period = range(1,6)
    workload = dict(zip(subjects["disciplina"], subjects["carga_semanal"]))

    return (
        Path,
        availability,
        classes,
        cp_model,
        crooms,
        days,
        mo,
        pd,
        period,
        subjects,
        workload,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    **Processamento e Estruturação das Restrições Específicas**

    - `doubleP`: Identifica através de um valor booleano quais as disciplinas que exigem a marcação de blocos de aulas duplos.
    - `teachers` e `teachersList`: Mapeiam a correspondência entre cada disciplina e o professor responsável, bem como a lista de todos os docentes únicos.
    - `unavailable`: Cria um conjunto (`set`) de tuplos contendo as indisponibilidades predefinidas dos professores, cruzando docente, dia e período, de modo a acelerar a verificação de conflitos durante a geração do horário.
    - `capacity` e `typo`: Definem a lotação máxima de cada sala e associam as necessidades específicas de cada disciplina ao tipo de sala exigido (por exemplo, a necessidade de um laboratório em vez de uma sala normal).
    """)
    return


@app.cell
def _(subjects):
    doubleP = {s: isdouble == "sim" for s, isdouble in zip(subjects["disciplina"], subjects["duplo_periodo"])} #precisamos de uma nocao de disciplina dupla para operar sobre elas
    return (doubleP,)


@app.cell
def _(subjects):
    teachers = dict(zip(subjects["disciplina"], subjects["professor"]))
    teachersList = subjects["professor"].unique()
    return teachers, teachersList


@app.cell
def _(availability):
    unavailable = set(zip(availability["professor"], availability["dia"], availability["periodo"])) #definimos unavailable pois esta restricao so corre se o professor for colocado num bloco onde nao tem disponibilidade
    return (unavailable,)


@app.cell
def _(crooms, pd, subjects):
    capacity = {s: int(q) for s, q in zip(crooms["sala"], crooms["quantidade"])}
    normal = crooms.loc[crooms["tipo"] == "normal", "sala"].iloc[0] #definicao de sala normal
    typo = {}
    for _s, _e in zip(subjects["disciplina"], subjects["sala_especial"]): #declaracao do tipo de sala 
        if pd.isna(_e):
            typo[_s] = normal
        else:
            typo[_s] = _e
    return capacity, typo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    **(O1)** Minimizar o número total de "buracos" no horário de cada professor — um buraco é um tempo livre, no meio do dia, entre a primeira e a última aula desse professor nesse dia.

    ---

    **Função de Otimização: Minimização de "Buracos" (`manageHoles`)**

    O intuito é garantir a melhor qualidade de horário possível para os docentes, minimizando os chamados "buracos" (tempos livres intercalados entre aulas no meio do mesmo dia).

    Para o conseguir, o algoritmo cria variáveis inteiras para identificar dinamicamente o período da primeira (`first`) e da última (`last`) aula de cada professor em cada dia útil.
    Em seguida, contabiliza o intervalo de tempo entre estes dois limites, subtraindo o número real de aulas dadas nesse dia. O objetivo do modelo (`model.Minimize`) é, assim, reduzir a soma total destes tempos mortos em toda a escola.
    """)
    return


@app.cell
def _(classes, days, period, subjects, teachers, teachersList):
    def manageHoles(model, x):

    #para tentar minimizar o numero de buracos para um determinado professor temos de, primeiramente, ter uma noção do período em que um professor não tem aulas
        first = {} #primeira aula lecionada num determinado dia para um dado professor
        for _t in teachersList:
            for _d in days:
                first[_t,_d] = model.NewIntVar(min(period), max(period), f"first_{_t}_{_d}")
    
        last = {} #ultima
        for _t in teachersList:
            for _d in days:
                last[_t,_d] = model.NewIntVar(min(period), max(period), f"last_{_t}_{_d}")

        holes = {} #intervao entre aulas (buraco)
        for _t in teachersList:
            for _d in days:
                holes[_t,_d] = model.NewIntVar(0,len(period), f"holes_{_t}_{_d}") #não vou colocar limite fixo, len(period) fica mais versátil

        w = {} #bool var para verificacao da disponibilidade do professor 
        for _t in teachersList:
            for _d in days:
                for _p in period:
                    w[_t,_d,_p] = model.NewBoolVar(f"_{_t},_{_d}, _{_p}")

        model.Minimize(sum(holes[_t,_d] for _t in teachersList for _d in days))



        for _t in teachersList: 
            for _d in days:
                for _p in period:
                    model.Add(first[_t,_d] <= _p).OnlyEnforceIf(w[_t,_d,_p]) #enquadramento de aula entre os limites de períodos
                    model.Add(last[_t,_d] >= _p).OnlyEnforceIf(w[_t,_d,_p])
                model.Add(holes[_t,_d] >= last[_t,_d] - first[_t,_d] + 1 - sum(w[_t,_d,_p] for _p in period)) #os buracos sao calculados pelo last e first e também com w (número de aulas por dia para um dado professor. é incrementado para cada período dando 1 ou 0 se tiver aula ou não respetivamente)


        for _t in teachersList:
            for _d in days:
                for _p in period:
                    model.Add(sum(x[_c,_s,_d,_p] for _c in classes["turma"] for _s in subjects["disciplina"] if teachers[_s] == _t) == w[_t,_d,_p])

    return (manageHoles,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **(R9)**
    1. Gerar um horário válido `H0` a partir de um conjunto de
           dados inicial (`dados/`).
    2. Dada uma pequena alteração aos recursos — por exemplo, a
           que está em `dados_v2/` (o Prof. Eduardo continua limitado
           às tardes, mas a Prof. Ana passa a estar indisponível às
           sextas-feiras nos 2 últimos tempos) — gerar um novo horário
           válido `H1` que respeite R1–R8 com os novos dados.
    3. `H1` deve ser produzido **de forma eficiente** (mais rápido
           do que resolver `H1` do zero, sem usar `H0`) e **minimizando
           o número de aulas que mudam de tempo/sala** entre `H0` e
           `H1` — `H1` não precisa de ser ótimo em relação a O1.
    """)
    return


@app.cell
def _(H0, Path, pd, teachers, unavailable):
    pathway2 = Path("dados_v2")
    availability2 = pd.read_csv(pathway2/"disponibilidade_excecoes.csv")
    unavailable2 = set(zip(availability2["professor"], availability2["dia"], availability2["periodo"])) 

    affected = []
    for(_c,_d,_p), _s in H0.items(): #vamos encontrar as aulas afetadas pelas novas indisponibilidades
        if (teachers[_s], _d, _p)  in unavailable2:
            affected.append((_c,_s,_d,_p)) 

    print(len(affected))
    print(len(unavailable2))
    print(len(unavailable))
    return (unavailable2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Função Base de Construção do Modelo (`.build()`)**

        Esta célula encapsula a lógica principal de criação do horário na função `build(unavailable)`.
        Adicionamos rigorosamente todas as restrições estruturais imperativas ao modelo (R1-R7):
    1. Impedir a sobreposição de aulas: cada turma tem, no máximo, uma aula por cada período;
    2. Garantir o cumprimento exato da carga horária semanal definida para cada disciplina;
    3. Assegurar a correta distribuição das aulas ao longo da semana, impondo também que as aulas de período duplo ocorrem obrigatoriamente em tempos consecutivos no mesmo dia;
    4. Prevenir sobreposições para os docentes (não podem lecionar a turmas distintas no mesmo instante) e impor os seus períodos de indisponibilidade;
    5. Respeitar a capacidade limite das salas face à lotação necessária e garantir que as disciplinas ocupam apenas os tipos de sala apropriados.
    """)
    return


@app.cell
def _(
    capacity,
    classes,
    cp_model,
    crooms,
    days,
    doubleP,
    period,
    subjects,
    teachers,
    teachersList,
    typo,
    workload,
):
    def build(unavailable):

        model = cp_model.CpModel()
        x = {} #declaracao de x
        for _c in classes["turma"]:
            for _s in subjects["disciplina"]:
                for _d in days:
                    for _p in period:
                        x[_c,_s,_d,_p] = model.NewBoolVar(f"_{_c}_{_s}_{_d}_{_p}")

        for _c in classes["turma"]:
            for _d in days:
                for _p in period:
                    model.Add(sum(x[_c,_s,_d,_p] for _s in subjects["disciplina"]) <= 1)
    
        for _c in classes["turma"]:
            for _s in subjects["disciplina"]:
                model.Add(sum(x[_c, _s, _d, _p] for _d in days for _p in period) == workload[_s])


        for _c in classes["turma"]:
            for _s in subjects["disciplina"]:
                if not doubleP[_s]:
                    for _d in days:
                        model.Add(sum(x[_c, _s, _d, _p] for _p in period) <= 1)

    
        for _c in classes["turma"]:
            for _s in subjects["disciplina"]:
                if doubleP[_s]:
                    for _d in days:
                        model.Add(sum(x[_c,_s,_d,_p] for _p in period) <= 2)
                        for _p in period:
                            _consecutive = []
                            if _p - 1 in period:
                                _consecutive.append(x[_c,_s,_d,_p - 1])
                            if _p + 1 in period:
                                _consecutive.append(x[_c,_s,_d,_p + 1])
                            model.Add(x[_c,_s,_d,_p] <= sum(_consecutive))


        for _t in teachersList:
            for _d in days:
                for _p in period:
                    model.Add(sum(x[_c,_s,_d,_p] for _c in classes["turma"] for _s in subjects["disciplina"] if _t == teachers[_s]) <= 1)

        for _c in classes["turma"]:
            for _s in subjects["disciplina"]:
                for _d in days:
                    for _p in period:
                        if (teachers[_s], _d, _p) in unavailable:
                            model.Add(x[_c,_s,_d,_p] == 0)

        for _r in crooms["sala"]:
            for _d in days:
                for _p in period:
                     model.Add(sum(x[_c,_s,_d,_p] for _c in classes["turma"] for _s in subjects["disciplina"] if typo[_s] == _r) <= capacity[_r]) 
    
        return model, x


    return (build,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Instanciação de (H0)**

    Nesta etapa, invocamos a função `build` utilizando os dados de indisponibilidade originais. A este modelo aplicamos a função de otimização `manageHoles`, preparando o solver para gerar a primeira solução ótima para o horário escolar, partindo completamente do zero.
    """)
    return


@app.cell
def _(build, manageHoles, unavailable):
    model, x = build(unavailable)
    manageHoles(model, x)
    return model, x


@app.cell
def _(cp_model, model, x):
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    print(solver.StatusName(status))

    horario = {}
    for (_c, _s, _d, _p), var in x.items():
        if solver.Value(var) == 1:
            horario[_c, _d, _p] = _s
    H0 = dict(horario)
    print(len(horario))

    return H0, solver


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    **Instanciação de (H1)** - condicionado por dados_v2

    Aqui construímos um novo modelo que já incorpora as indisponibilidades atualizadas (versão 2). Contudo, em vez de procurarmos do zero um novo horário ótimo que minimize os buracos, o nosso objetivo primordial (`Maximize(sum(kept))`) passa a ser **maximizar o número de aulas que se mantêm estritamente no mesmo dia e período** face à solução inicial `H0`.
    Este processo assegura uma transição suave, permitindo ajustar o horário de forma muito mais eficiente em termos computacionais e provocando a mínima disrupção na rotina já estabelecida de alunos e professores.
    """)
    return


@app.cell
def _(H0, build, unavailable2):
    model1, x1 = build(unavailable2) #apenas o model1 é inicializado com o kept
    kept = []
    for (_c, _d, _p), _s in H0.items():
        kept.append(x1[_c, _s, _d, _p])

    model1.Maximize(sum(kept))
    return model1, x1


@app.cell
def _(H0, cp_model, model1, x1):
    solver1 = cp_model.CpSolver()
    status1 = solver1.Solve(model1)
    print(solver1.StatusName(status1), solver1.ObjectiveValue(), solver1.WallTime())

    horario1 = {}
    for (_c,_s,_d,_p), var1 in x1.items():
        if solver1.Value(var1) == 1:
            horario1[_c,_d,_p] = _s
    H1 = dict(horario1)
    print(len(horario1))
    changes = set(H0.items()) - set(H1.items())
    print(len(changes))
    print(changes)
    return (solver1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    **Instanciação de (H2)**

    Criamos um terceiro modelo, igualmente suportado nos novos dados de disponibilidade, mas regressando à função objetivo original (`manageHoles`). O propósito deste passo é puramente comparativo: permite-nos avaliar e contrastar o tempo de execução e o volume de alterações estruturais resultantes de um reajuste minimalista (`H1`), por oposição a um cálculo de um novo horário feito inteiramente de raiz.
    """)
    return


@app.cell
def _(build, manageHoles, unavailable2):
    model2, x2 = build(unavailable2)
    manageHoles(model2, x2)
    return model2, x2


@app.cell
def _(H0, cp_model, model2, x2):
    solver2 = cp_model.CpSolver()
    status2 = solver2.Solve(model2)
    print(solver2.StatusName(status2), solver2.ObjectiveValue(), solver2.WallTime())

    horario2 = {}
    for (_c,_s,_d,_p), var2 in x2.items():
        if solver2.Value(var2) == 1:
            horario2[_c,_d,_p] = _s
    H2 = dict(horario2)
    print(len(horario2))
    print(len(set(H0.items()) - set(H2.items())))
    return (solver2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    **Instanciação de (H3)**

    Criamos um ultimo modelo, com novas indsiponibilidades, mas regressando à função objetivo original (`manageHoles`). A criação deste modelo permito-nos testar a versatilidade do código.

    As novas indisponibilidades são do professor Bruno.
    """)
    return


@app.cell
def _(Path, pd):
    pathway3 = Path("dados_v3")
    availability3 = pd.read_csv(pathway3/"disponibilidade_excecoes.csv")
    unavailable3 = set(zip(availability3["professor"], availability3["dia"], availability3["periodo"]))
    return (unavailable3,)


@app.cell
def _(build, manageHoles, unavailable3):
    model3, x3 = build(unavailable3)
    manageHoles(model3,x3)
    print(len(unavailable3))
    return model3, x3


@app.cell
def _(H0, cp_model, model3, solver2, x3):
    solver3 = cp_model.CpSolver()
    status3 = solver3.Solve(model3)
    print(solver3.StatusName(status3), solver3.ObjectiveValue(), solver3.WallTime())


    horario3 = {}
    for (_c,_s,_d,_p), var3 in x3.items():
        if solver2.Value(var3) == 1:
            horario3[_c,_d,_p] = _s
    H3 = dict(horario3)
    print(len(horario3))
    print(len(set(H0.items()) - set(H3.items())))
    return H3, solver3


@app.cell
def _(H3, teachers, unavailable3):
    affectedv3 = []
    for(_c,_d,_p), _s in H3.items(): #vamos, novamente, encontrar as aulas afetadas pelas novas indisponibilidades(dados_v3)
        if (teachers[_s], _d, _p)  in unavailable3:
            affectedv3.append((_c,_s,_d,_p)) 
    print(len(affectedv3)) # 3 aulas afetadas por dados_v3
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Método `.show()`**

    Na célula final, focamo-nos na apresentação gráfica dos resultados. Definimos a função `show`, cujo propósito é percorrer as variáveis de decisão validadas pelo algoritmo e transformar esses dados em tabelas estruturadas (através de `pd.DataFrame`).
    Estes dados são seguidamente convertidos para formato HTML e integrados na interface da plataforma Marimo recorrendo à função `mo.Html`. Este procedimento permite-nos apresentar o produto final — o horário detalhado de cada turma — de uma forma visualmente apelativa e de fácil leitura.
    """)
    return


@app.cell
def _(mo, pd):

    def show(solver, x, days, periods, teachers, typo): #feito pelo Claude
        turmas = list(dict.fromkeys(k[0] for k in x))
        blocos = []
        for turma in turmas:
            tab = pd.DataFrame("", index=list(periods), columns=days)
            for (t, disc, dia, p), var in x.items():
                if t == turma and solver.Value(var) == 1:
                    texto = f"{disc} ({teachers[disc]})<br><i>{typo[disc]}</i>"
                    atual = tab.loc[p, dia]
                    tab.loc[p, dia] = texto if atual == "" else f"{atual}<br>+ {texto}"
            blocos += [mo.md(f"### {turma}"), mo.Html(tab.to_html(escape=False))]
        return mo.vstack(blocos)



    return (show,)


@app.cell
def _(days, period, show, solver, teachers, typo, x):
    show(solver, x, days, period, teachers, typo) #H0
    return


@app.cell
def _(days, period, show, solver1, teachers, typo, x):
    show(solver1, x, days, period, teachers, typo) #H1
    return


@app.cell
def _(days, period, show, solver3, teachers, typo, x3):
    show(solver3, x3, days, period, teachers, typo) #Horário com dados_v3
    return


if __name__ == "__main__":
    app.run()
