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
    # TP1

    ## Grupo
    João Pontes, A111657

    João Paulo, A110393

    Objetivo: Criar um horário escolar semanal cumpridor de determinadas restrições (consultar horario_escolar_enunciado.py).


    ---
    **(R8)** Para a leitura dos dados .csv:
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
    Declaração do dicionário das disciplinas que ocupam períodos/blocos duplos, variáveis professor e lista de professores, set para professores indisponíveis, capacidade e tipo de sala.
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

    ## falta apenas colocar a restrição em prática. se estiver em affected, obrigamos a mudar
    print(len(affected))
    print(("Prof. Ana", "Sex", 4) in unavailable2)
    print(len(unavailable2))
    print(len(unavailable))
    return (unavailable2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Método .build() ##

    Neste método estão contidos os algoritmos de cada restrição
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


@app.cell
def _(build, manageHoles, unavailable):
    model, x = build(unavailable)
    manageHoles(model, x)
    return model, x


@app.cell
def _(H0, build, unavailable2):
    model1, x1 = build(unavailable2)
    kept = []
    for (_c, _d, _p), _s in H0.items():
        kept.append(x1[_c, _s, _d, _p])

    model1.Maximize(sum(kept))
    return model1, x1


@app.cell
def _(build, manageHoles, unavailable2):
    model2, x2 = build(unavailable2)
    manageHoles(model2, x2)
    return model2, x2


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

    return (H0,)


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
    return


@app.cell
def _(days, mo, pd, period, solver1, teachers, typo, x1):

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

    show(solver1, x1, days, period, teachers, typo)

    return


if __name__ == "__main__":
    app.run()
