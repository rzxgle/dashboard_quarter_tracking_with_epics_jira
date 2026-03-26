DONE_STATUS = [
    "Pronto para Prod",
    "Prod",
    "Done",
    "Deploy em PROD",
    "PRONTO PARA ATIVAÇÃO DE VALOR",
    "Pronto p/ Deploy STG",
    "Ativação de valor",
    "PRONTO PARA MEDIÇÃO",
    "Concluído"
]

IN_PROGRESS_STATUS = [
    "Fazendo",
    "Desenvolvimento",
    "EM ANDAMENTO",
    "Code Review",
    "Pronto para Testes",
    "Em QA",
    "Beta"
]

IN_APPROVAL_STATUS = [
    "Em Homologação",
    "Pronto para Staging",
    "Aprovação Comitê",
    "Staging"
]

IGNORED_STATUS = [
    "Inválido",
    "Cancelado"
]

def normalize(status):
    return status.strip().upper()

def is_done(status):
    return normalize(status) in [s.upper() for s in DONE_STATUS]

def is_in_approval(status):
    return normalize(status) in [s.upper() for s in IN_APPROVAL_STATUS]

def is_in_progress(status):
    return normalize(status) in [s.upper() for s in IN_PROGRESS_STATUS]

def is_ignored(status):
    return normalize(status) in [s.upper() for s in IGNORED_STATUS]

def get_priority(status, done, flagged):
    if flagged:
        return 1  # 🚧 bloqueado
    elif is_ignored(status):
        return 6  # ❌ cancelado
    elif done:
        return 5  # ✅ concluído
    elif is_in_approval(status):
        return 4  # 🟣 aprovação
    elif is_in_progress(status):
        return 3  # 🔵 em andamento
    else:
        return 2  # ⚪ to do