import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import json
import os

ARQUIVO_TAREFAS = "tarefas.json"

# ------------------------ Funcoes de Persistencia ------------------------ #
def carregar_tarefas():
    if os.path.exists(ARQUIVO_TAREFAS):
        with open(ARQUIVO_TAREFAS, "r") as f:
            return json.load(f)
    return []

def salvar_tarefas(tarefas):
    with open(ARQUIVO_TAREFAS, "w") as f:
        json.dump(tarefas, f, indent=4)

# ------------------------ Lógica de Cálculo ------------------------ #
def calcular_status(tarefa):
    try:
        progresso_atual = float(tarefa['progresso_atual'])
        progresso_total = float(tarefa['progresso_total'])
        data_inicio = datetime.strptime(tarefa['data_inicio'], "%d/%m/%Y")
        data_fim = datetime.strptime(tarefa['data_fim'], "%d/%m/%Y")
        agora = datetime.now()

        progresso_percentual = round((progresso_atual / progresso_total) * 100, 2) if progresso_total != 0 else 0
        tempo_total = (data_fim - data_inicio).total_seconds()
        tempo_passado = (agora - data_inicio).total_seconds()
        tempo_percentual = round((tempo_passado / tempo_total) * 100, 2) if tempo_total != 0 else 0

        if progresso_percentual >= tempo_percentual:
            status = "✅ No prazo"
        else:
            status = "⚠️ Atrasado"

        return progresso_percentual, tempo_percentual, status
    except:
        return 0, 0, "Erro nos dados"

# ------------------------ Interface Gráfica ------------------------ #
def adicionar_tarefa():
    nome = entry_nome.get()
    atual = entry_atual.get()
    total = entry_total.get()
    inicio = entry_inicio.get()
    fim = entry_fim.get()

    if not nome or not atual or not total or not inicio or not fim:
        messagebox.showerror("Erro", "Preencha todos os campos.")
        return

    nova = {
        "nome": nome,
        "progresso_atual": atual,
        "progresso_total": total,
        "data_inicio": inicio,
        "data_fim": fim
    }

    tarefas.append(nova)
    salvar_tarefas(tarefas)
    atualizar_lista()
    limpar_campos()

def limpar_campos():
    entry_nome.delete(0, tk.END)
    entry_atual.delete(0, tk.END)
    entry_total.delete(0, tk.END)
    entry_inicio.delete(0, tk.END)
    entry_fim.delete(0, tk.END)

def atualizar_tarefa(index, frame):
    def salvar_edicao():
        try:
            tarefas[index]['nome'] = entry_nome_edit.get()
            tarefas[index]['progresso_atual'] = entry_atual_edit.get()
            tarefas[index]['progresso_total'] = entry_total_edit.get()
            tarefas[index]['data_inicio'] = entry_inicio_edit.get()
            tarefas[index]['data_fim'] = entry_fim_edit.get()
            salvar_tarefas(tarefas)
            atualizar_lista()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar tarefa: {e}")

    for widget in frame.winfo_children():
        widget.destroy()

    tk.Label(frame, text="Editar tarefa:").pack(anchor="w")

    tk.Label(frame, text="Nome da tarefa:").pack(anchor="w")
    entry_nome_edit = tk.Entry(frame)
    entry_nome_edit.insert(0, tarefas[index]['nome'])
    entry_nome_edit.pack(fill="x")

    tk.Label(frame, text="Progresso atual:").pack(anchor="w")
    entry_atual_edit = tk.Entry(frame)
    entry_atual_edit.insert(0, tarefas[index]['progresso_atual'])
    entry_atual_edit.pack(fill="x")

    tk.Label(frame, text="Progresso total:").pack(anchor="w")
    entry_total_edit = tk.Entry(frame)
    entry_total_edit.insert(0, tarefas[index]['progresso_total'])
    entry_total_edit.pack(fill="x")

    tk.Label(frame, text="Data de início (DD/MM/AAAA):").pack(anchor="w")
    entry_inicio_edit = tk.Entry(frame)
    entry_inicio_edit.insert(0, tarefas[index]['data_inicio'])
    entry_inicio_edit.pack(fill="x")

    tk.Label(frame, text="Data final (DD/MM/AAAA):").pack(anchor="w")
    entry_fim_edit = tk.Entry(frame)
    entry_fim_edit.insert(0, tarefas[index]['data_fim'])
    entry_fim_edit.pack(fill="x")

    tk.Button(frame, text="Salvar", command=salvar_edicao).pack(pady=2)

def deletar_tarefa(index):
    if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta tarefa?"):
        tarefas.pop(index)
        salvar_tarefas(tarefas)
        atualizar_lista()

def atualizar_lista():
    for widget in frame_tarefas.winfo_children():
        widget.destroy()

    for i, tarefa in enumerate(tarefas):
        prog, tempo, status = calcular_status(tarefa)
        bloco = tk.Frame(frame_tarefas, bd=1, relief=tk.SOLID, padx=5, pady=5)
        bloco.grid_columnconfigure(1, weight=1)

        tk.Label(bloco, text=f"📌 {tarefa['nome']}", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", columnspan=2)
        tk.Label(bloco, text=f"📅 Início: {tarefa['data_inicio']} | Fim: {tarefa['data_fim']}").grid(row=1, column=0, sticky="w", columnspan=2)

        ttk.Progressbar(bloco, value=prog, maximum=100, length=200).grid(row=2, column=0, sticky="w", columnspan=2, pady=(2, 2))
        tempo_barra = ttk.Progressbar(bloco, value=tempo, maximum=100, length=200)
        tempo_barra.grid(row=3, column=0, sticky="w", columnspan=2, pady=(0, 2))
        tempo_barra.configure(style="Red.Horizontal.TProgressbar")

        tk.Label(bloco, text=f"📊 {prog}% | ⏳ {tempo}%").grid(row=4, column=0, sticky="w")
        tk.Label(bloco, text=status, fg="green" if "✅" in status else "red").grid(row=5, column=0, sticky="w")

        botoes = tk.Frame(bloco)
        tk.Button(botoes, text="Editar", command=lambda idx=i, fr=bloco: atualizar_tarefa(idx, fr)).pack(side="left")
        tk.Button(botoes, text="Excluir", command=lambda idx=i: deletar_tarefa(idx)).pack(side="left")
        botoes.grid(row=4, column=1, rowspan=2, padx=5)

        bloco.pack(fill="x", pady=5)

# ------------------------ Janela Principal ------------------------ #
janela = tk.Tk()
janela.title("Gerenciador de Tarefas com Progresso")
janela.geometry("520x720")

# Estilo para barra vermelha
style = ttk.Style()
style.theme_use('default')
style.configure("Red.Horizontal.TProgressbar", troughcolor='white', background='red')

# Campos de entrada
tk.Label(janela, text="Nome da tarefa:").pack()
entry_nome = tk.Entry(janela)
entry_nome.pack(fill="x")

tk.Label(janela, text="Progresso atual:").pack()
entry_atual = tk.Entry(janela)
entry_atual.pack(fill="x")

tk.Label(janela, text="Progresso total:").pack()
entry_total = tk.Entry(janela)
entry_total.pack(fill="x")

tk.Label(janela, text="Data de início (DD/MM/AAAA):").pack()
entry_inicio = tk.Entry(janela)
entry_inicio.pack(fill="x")

tk.Label(janela, text="Data final (DD/MM/AAAA):").pack()
entry_fim = tk.Entry(janela)
entry_fim.pack(fill="x")

tk.Button(janela, text="Adicionar tarefa", command=adicionar_tarefa).pack(pady=10)

# Lista de tarefas
frame_tarefas = tk.Frame(janela)
frame_tarefas.pack(fill="both", expand=True)

# Carregar tarefas ao iniciar
tarefas = carregar_tarefas()
atualizar_lista()

janela.mainloop()
