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
    Para a leitura dos dados .csv:
    """)
    return


@app.cell
def _():
    import marimo as mo
    from pathlib import Path
    import pandas as pd
    from ortools.sat.python import cp_model

    pathway = Path("dados")
    classes = pd.read_csv(pathway/"turmas.csv")
    croooms = pd.read_csv(pathway/"salas.csv")
    availability = pd.read_csv(pathway/"disponibilidade_excecoes.csv")
    subjects = pd.read_csv(pathway/"disciplinas.csv")
    days = ["Seg", "Ter", "Qua", "Qui", "Sex"]
    period = range(1,6)
    workload = dict(zip(subjects["disciplina"], subjects["carga_semanal"]))


    model = cp_model.CpModel()
    x = {}
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
    return (teachers,)


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
    unavailable = set(zip(availability["professor"], availability["dia"], availability["periodo"]))
    for _c in classes["turma"]:
        for _s in subjects["disciplina"]:
            for _d in days:
                for _p in period:
                    if (teachers[_s], _d, _p) in unavailable:
                        model.Add(x[_c,_s,_d,_p] == 0)
    return


@app.cell
def _(cp_model, days, mo, model, pd, period, teachers, x):
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    print(solver.StatusName(status))

    horario = {}
    for (_c, _s, _d, _p), var in x.items():
        if solver.Value(var) == 1:
            horario[_c, _d, _p] = _s
    print(len(horario))


    def show(solver, x, days, periods, teachers): ## feito pelo Claude
        turmas = list(dict.fromkeys(k[0] for k in x))
        blocos = []
        for turma in turmas:
            tab = pd.DataFrame("", index=list(periods), columns=days)
            for (t, disc, dia, p), var in x.items():
                if t == turma and solver.Value(var) == 1:
                    texto = f"{disc} ({teachers[disc]})"
                    atual = tab.loc[p, dia]
                    tab.loc[p, dia] = texto if atual == "" else f"{atual} + {texto}"
            blocos += [mo.md(f"### {turma}"), tab]
        return mo.vstack(blocos)

    show(solver, x, days, period, teachers)
    return


if __name__ == "__main__":
    app.run()
