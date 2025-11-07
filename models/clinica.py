from __future__ import annotations

from datetime import datetime, date, time, timedelta
from typing import List
import sys
from pathlib import Path

# Tornar o pacote local importável quando este script é executado como
# script standalone. Adicionamos a pasta 'sistema-agenda-clinica' ao
# sys.path para permitir 'from models.xxx import YYY'.
PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / "sistema-agenda-clinica"
if str(MODELS_DIR) not in sys.path:
    sys.path.insert(0, str(MODELS_DIR))
AgendaRepository
from models.paciente import Paciente
from models.medico import Medico
from models.agendamento import Agendamento


class Clinica:
    """
    Camada de ORQUESTRAÇÃO (Pessoa 3).
    Não contém SQL. Depende de um 'GerenciadorBD' injetado no construtor.

    Contrato esperado do GerenciadorBD:
      - buscar_paciente(id_paciente) -> Paciente | None
      - buscar_medico(id_medico) -> Medico | None
      - buscar_todos_pacientes() -> list[Paciente]
      - buscar_todos_medicos() -> list[Medico]
      - buscar_agendamentos_por_paciente(id_paciente) -> list[Agendamento]
      - buscar_agendamentos_por_medico_e_data(id_medico, data_iso: str) -> list[Agendamento]
      - salvar_agendamento(ag: Agendamento) -> int
    """

    def __init__(self, gerenciador_bd):
        self.bd = gerenciador_bd

    # ----------------- API pública -----------------

    def marcar_consulta(self, id_paciente: int, id_medico: int, inicio: datetime, duracao_min: int) -> Agendamento:
        """Valida disponibilidade; cria e persiste um novo Agendamento."""
        paciente = self.bd.buscar_paciente(id_paciente)
        medico = self.bd.buscar_medico(id_medico)
        if not paciente or not medico:
            raise ValueError("Paciente ou Médico inexistente.")

        self._verificar_disponibilidade(medico, inicio, duracao_min, id_medico=id_medico)

        ag = Agendamento(paciente=paciente, medico=medico, data_hora_inicio=inicio, duracao_minutos=duracao_min)
        self.bd.salvar_agendamento(ag)
        return ag

    def consultar_agenda_paciente(self, id_paciente: int):
        return self.bd.buscar_agendamentos_por_paciente(id_paciente)

    def consultar_agenda_medico(self, id_medico: int, d: date):
        return self.bd.buscar_agendamentos_por_medico_e_data(id_medico, d.isoformat())

    def listar_membros_clinica(self) -> None:
        """Demonstra polimorfismo chamando identificar() de cada objeto."""
        for p in self.bd.buscar_todos_pacientes():
            p.identificar()
        for m in self.bd.buscar_todos_medicos():
            m.identificar()

    # ----------------- Núcleo de disponibilidade -----------------

    def _verificar_disponibilidade(self, medico: Medico, inicio: datetime, duracao_min: int, *, id_medico: int) -> None:
        """
        1) Regra de trabalho do médico (dias_semana, hora_inicio, hora_fim, bloqueios)
        2) Conflito com agendamentos existentes
        """
        regras = getattr(medico, "regras_disponibilidade", {}) or {}
        dias_semana = set(regras.get("dias_semana", [0,1,2,3,4]))  # 0=Seg .. 6=Dom
        hora_inicio = _parse_hhmm(regras.get("hora_inicio", "08:00"))
        hora_fim = _parse_hhmm(regras.get("hora_fim", "17:00"))
        bloqueios = set(regras.get("bloqueios", []))

        # 1. bloqueios de data
        if inicio.date().isoformat() in bloqueios:
            raise ValueError("Médico bloqueado nesta data.")

        # 2. dia da semana
        if inicio.weekday() not in dias_semana:
            raise ValueError("Médico não atende neste dia da semana.")

        # 3. janela diária
        fim = inicio + timedelta(minutes=int(duracao_min))
        if not _is_between_time(inicio.time(), hora_inicio, hora_fim):
            raise ValueError("Início fora do horário de atendimento.")
        if not _is_between_time(fim.time(), hora_inicio, hora_fim, inclusive_end=True):
            raise ValueError("Fim extrapola o horário de atendimento.")

        # 4. conflito com existentes (usa o id passado ao método público)
        data_iso = inicio.date().isoformat()
        existentes = self.bd.buscar_agendamentos_por_medico_e_data(id_medico, data_iso)
        for ag in existentes:
            if getattr(ag, "status", None) == "Cancelado":
                continue
            if _overlap(inicio, fim, ag.data_hora_inicio, ag.data_hora_fim):
                raise ValueError("Conflito com outro agendamento no período.")


# ----------------- Helpers -----------------

def _parse_hhmm(s: str) -> time:
    hh, mm = s.split(":")
    return time(int(hh), int(mm))

def _is_between_time(t: time, start: time, end: time, inclusive_end: bool=False) -> bool:
    if inclusive_end:
        return (t >= start) and (t <= end)
    return (t >= start) and (t < end)

def _overlap(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end
