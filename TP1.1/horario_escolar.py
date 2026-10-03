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
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex"]
    periodo = range(1,6)
    carga = dict(zip(subjects["disciplina"], subjects["carga_semanal"]))


    model = cp_model.CpModel()
    x = {}
    for _c in classes["turma"]:
        for _s in subjects["disciplina"]:
            for _d in dias:
                for _p in periodo:
                    x[_c,_s,_d,_p] = model.NewBoolVar(f"_{_c}_{_s}_{_d}_{_p}")
    print(len(x))
    return carga, classes, cp_model, dias, mo, model, periodo, subjects, x


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **(R1)** Uma turma não pode ter duas aulas em simultâneo, pelo que:
    """)
    return


@app.cell
def _(classes, dias, model, periodo, subjects, x):
    for _c in classes["turma"]:
        for _d in dias:
            for _p in periodo:
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
def _(carga, classes, dias, model, periodo, subjects, x):
    for _c in classes["turma"]:
        for _s in subjects["disciplina"]:
            model.Add(sum(x[_c, _s, _d, _p] for _d in dias for _p in periodo) == carga[_s])
        
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
def _(classes, dias, model, periodo, subjects, x):
    doubleP = {s: isdouble == "sim" for s, isdouble in zip(subjects["disciplina"], subjects["duplo_periodo"])} #precisamos de uma nocao de disciplina dupla para operar sobre ela
    for _c in classes["turma"]:
        for _s in subjects["disciplina"]:
            if not doubleP[_s]:
                for _d in dias:
                    model.Add(sum(x[_c, _s, _d, _p] for _p in periodo) <= 1)
    return (doubleP,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **(R4)** Disciplinas marcadas `duplo_periodo=sim` só podem ser
      dadas em blocos de 2 tempos consecutivos, no mesmo dia (nunca um
      tempo isolado).
    """)
    return


@app.cell
def _(classes, dias, doubleP, model, periodo, subjects, x):
    for _c in classes["turma"]:
        for _s in subjects["disciplina"]:
            if doubleP[_s]:
                for _d in dias:
                    for _p in periodo:
                        _consecutive = []
                        if _p - 1 in periodo:
                            _consecutive.append(x[_c,_s,_d,_p - 1])
                        if _p + 1 in periodo:
                            _consecutive.append(x[_c,_s,_d,_p + 1])
                        model.Add(x[_c,_s,_d,_p] <= sum(_consecutive))
                
    return


@app.cell
def _(cp_model, model, x):
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    print(solver.StatusName(status))

    horario = {}
    for (_c, _s, _d, _p), var in x.items():
        if solver.Value(var) == 1:
            horario[_c, _d, _p] = _s
    print(horario)
    print(len(horario))
    return


if __name__ == "__main__":
    app.run()
