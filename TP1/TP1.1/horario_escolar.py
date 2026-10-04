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


    model = cp_model.CpModel()
    x = {} #declaracao de x
    for _c in classes["turma"]:
        for _s in subjects["disciplina"]:
            for _d in days:
                for _p in period:
                    x[_c,_s,_d,_p] = model.NewBoolVar(f"_{_c}_{_s}_{_d}_{_p}")
    print(len(x))
    return (
        availability,
        classes,
        cp_model,
        crooms,
        days,
        mo,
        model,
        pd,
        period,
        subjects,
        workload,
        x,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **(R1)** Uma turma não pode ter duas aulas em simultâneo, pelo que:
    """)
    return


@app.cell
def _(classes, days, model, period, subjects, x):
    for _c in classes["turma"]:
        for _d in days:
            for _p in period:
                model.Add(sum(x[_c,_s,_d,_p] for _s in subjects["disciplina"]) <= 1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **(R2)** Cada disciplina cumpre *exatamente* a carga semanal
    """)
    return


@app.cell
def _(classes, days, model, period, subjects, workload, x):
    for _c in classes["turma"]:
        for _s in subjects["disciplina"]:
            model.Add(sum(x[_c, _s, _d, _p] for _d in days for _p in period) == workload[_s])
        
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **(R3)** No máximo uma aula da mesma disciplina por dia, por
    turma — exceto disciplinas de duplo período (ver R4), em que o
    bloco de 2 tempos conta como uma só ocorrência nesse dia.
    """)
    return


@app.cell
def _(classes, days, model, period, subjects, x):
    doubleP = {s: isdouble == "sim" for s, isdouble in zip(subjects["disciplina"], subjects["duplo_periodo"])} #precisamos de uma nocao de disciplina dupla para operar sobre elas
    for _c in classes["turma"]:
        for _s in subjects["disciplina"]:
            if not doubleP[_s]:
                for _d in days:
                    model.Add(sum(x[_c, _s, _d, _p] for _p in period) <= 1)
    return (doubleP,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **(R4)** Disciplinas marcadas `duplo_period=sim` só podem ser
      dadas em blocos de 2 tempos consecutivos, no mesmo dia (nunca um
      tempo isolado).
    """)
    return


@app.cell
def _(classes, days, doubleP, model, period, subjects, x):
    for _c in classes["turma"]:
        for _s in subjects["disciplina"]:
            if doubleP[_s]:
                for _d in days:
                    model.Add(sum(x[_c,_s,_d,_p] for _p in period) <= 2) # vamos restringir 2 blocos de EF por dia 
                    for _p in period:
                        _consecutive = []
                        if _p - 1 in period:
                            _consecutive.append(x[_c,_s,_d,_p - 1]) 
                        if _p + 1 in period:
                            _consecutive.append(x[_c,_s,_d,_p + 1])
                        model.Add(x[_c,_s,_d,_p] <= sum(_consecutive)) # EF so pode ser colocada no horario sse tiver um bloco antes de _p ou depois 
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **(R5)** Um professor não pode dar duas aulas em simultâneo, mesmo
      que sejam a turmas ou disciplinas diferentes.
    """)
    return


@app.cell
def _(classes, days, model, period, subjects, x):
    teachers = dict(zip(subjects["disciplina"], subjects["professor"]))
    teachersList = subjects["professor"].unique()
    for _t in teachersList:
        for _d in days:
            for _p in period:
                model.Add(sum(x[_c,_s,_d,_p] for _c in classes["turma"] for _s in subjects["disciplina"] if _t == teachers[_s]) <= 1)
    return teachers, teachersList


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **(R6)** Um professor só pode dar aulas nos tempos em que está
      disponível (`disponibilidade_excecoes.csv`).
    """)
    return


@app.cell
def _(availability, classes, days, model, period, subjects, teachers, x):
    unavailable = set(zip(availability["professor"], availability["dia"], availability["periodo"])) #definimos unavailable pois esta restricao so corre se o professor for colocado num bloco onde nao tem disponibilidade
    for _c in classes["turma"]:
        for _s in subjects["disciplina"]:
            for _d in days:
                for _p in period:
                    if (teachers[_s], _d, _p) in unavailable:
                        model.Add(x[_c,_s,_d,_p] == 0)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **(R7)** Cada aula ocupa uma sala. Disciplinas com `sala_especial`
      só podem usar salas desse tipo; as restantes usam salas normais
    """)
    return


@app.cell
def _(classes, crooms, days, model, pd, period, subjects, x):
    capacity = {s: int(q) for s, q in zip(crooms["sala"], crooms["quantidade"])}
    normal = crooms.loc[crooms["tipo"] == "normal", "sala"].iloc[0] #definicao de sala normal
    typo = {}
    for _s, _e in zip(subjects["disciplina"], subjects["sala_especial"]): #declaracao do tipo de sala 
        if pd.isna(_e):
            typo[_s] = normal
        else:
            typo[_s] = _e

    for _r in crooms["sala"]:
        for _d in days:
            for _p in period:
                 model.Add(sum(x[_c,_s,_d,_p] for _c in classes["turma"] for _s in subjects["disciplina"] if typo[_s] == _r) <= capacity[_r]) 


    return (typo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    **(O1)** Minimizar o número total de "buracos" no horário de cada professor — um buraco é um tempo livre, no meio do dia, entre a primeira e a última aula desse professor nesse dia.
    """)
    return


@app.cell
def _(classes, days, model, period, subjects, teachers, teachersList, x):
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


    for _t in teachersList: 
        for _d in days:
            for _p in period:
                model.Add(first[_t,_d] <= _p).OnlyEnforceIf(w[_t,_d,_p]) #enquadramento de aula entre os limites de períodos
                model.Add(last[_t,_d] >= _p).OnlyEnforceIf(w[_t,_d,_p])
            model.Add(holes[_t,_d] >= last[_t,_d] - first[_t,_d] + 1 - sum(w[_t,_d,_p] for _p in period)) #os buracos sao calculados pelo last e first e também com w (número de aulas por dia para um dado professor. é incrementado para cada período dando 1 ou 0 se tiver aula ou não respetivamente)
    model.Minimize(sum(holes[_t,_d] for _t in teachersList for _d in days))


    for _t in teachersList:
        for _d in days:
            for _p in period:
                model.Add(sum(x[_c,_s,_d,_p] for _c in classes["turma"] for _s in subjects["disciplina"] if teachers[_s] == _t) == w[_t,_d,_p])

    return


@app.cell
def _(cp_model, days, mo, model, pd, period, teachers, typo, x):
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    print(solver.StatusName(status))

    horario = {}
    for (_c, _s, _d, _p), var in x.items():
        if solver.Value(var) == 1:
            horario[_c, _d, _p] = _s
    print(len(horario))


    def show(solver, x, days, periods, teachers, typo):
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

    show(solver, x, days, period, teachers, typo)
    return


if __name__ == "__main__":
    app.run()
