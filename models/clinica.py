from datetime import datetime, timedelta
from typing import List
from models.agendamento import Agendamento
from models.medico import Medico
from models.paciente import Paciente


class Clinica:
    """Classe que gerencia as regras de negócio da clínica."""

    def __init__(self, repo):
        """
        Inicializa a clínica com um repositório de dados.

        Args:
            repo: Instância de AgendaRepository para persistência de dados.
        """
        self.repo = repo

    def marcar_consulta(self, id_paciente: int, id_medico: int, inicio: datetime, duracao_min: int) -> Agendamento:
        """
        Marca uma consulta validando regras de negócio.

        Args:
            id_paciente: ID do paciente.
            id_medico: ID do médico.
            inicio: Data e hora de início da consulta.
            duracao_min: Duração da consulta em minutos.

        Returns:
            Agendamento criado.

        Raises:
            ValueError: Se houver conflito de horário ou regras violadas.
        """
        # Busca paciente e médico
        paciente = self.repo.buscar_paciente(id_paciente)
        if not paciente:
            raise ValueError(f"Paciente com ID {id_paciente} não encontrado.")

        medico = self.repo.buscar_medico(id_medico)
        if not medico:
            raise ValueError(f"Médico com ID {id_medico} não encontrado.")

        # Verifica disponibilidade do médico
        if not self._verificar_disponibilidade_medico(medico, inicio, duracao_min):
            raise ValueError("Médico não está disponível neste horário.")

        # Verifica conflitos de horário
        if self._verificar_conflito_horario(id_medico, inicio, duracao_min):
            raise ValueError("Já existe uma consulta agendada neste horário.")

        # Cria e salva o agendamento
        agendamento = Agendamento(
            paciente=paciente,
            medico=medico,
            data_hora_inicio=inicio,
            duracao_minutos=duracao_min,
            status="agendado"
        )

        agendamento_id = self.repo.salvar_agendamento(agendamento)
        agendamento.id = agendamento_id

        return agendamento

    def _verificar_disponibilidade_medico(self, medico: Medico, inicio: datetime, duracao_min: int) -> bool:
        """Verifica se o médico está disponível no horário solicitado."""
        dias_semana = {
            0: "segunda",
            1: "terca",
            2: "quarta",
            3: "quinta",
            4: "sexta",
            5: "sabado",
            6: "domingo"
        }

        dia = dias_semana[inicio.weekday()]
        if dia not in medico.regras_disponibilidade:
            return False

        horario_inicio = inicio.strftime("%H:%M")
        horario_fim = (inicio + timedelta(minutes=duracao_min)).strftime("%H:%M")

        for intervalo in medico.regras_disponibilidade[dia]:
            inicio_intervalo, fim_intervalo = intervalo.split("-")
            if inicio_intervalo <= horario_inicio < fim_intervalo and horario_fim <= fim_intervalo:
                return True

        return False

    def _verificar_conflito_horario(self, id_medico: int, inicio: datetime, duracao_min: int) -> bool:
        """Verifica se há conflito de horário com outras consultas do médico."""
        fim = inicio + timedelta(minutes=duracao_min)
        agendamentos = self.repo.buscar_agendamentos_medico(id_medico, inicio.date())

        for ag in agendamentos:
            ag_fim = ag.data_hora_inicio + timedelta(minutes=ag.duracao_minutos)
            if (inicio < ag_fim and fim > ag.data_hora_inicio):
                return True

        return False

    def consultar_agenda_paciente(self, id_paciente: int) -> List[Agendamento]:
        """
        Retorna todas as consultas de um paciente.

        Args:
            id_paciente: ID do paciente.

        Returns:
            Lista de agendamentos do paciente.
        """
        return self.repo.buscar_agendamentos_paciente(id_paciente)

    def consultar_agenda_medico(self, id_medico: int, data: datetime.date) -> List[Agendamento]:
        """
        Retorna todas as consultas de um médico em uma data específica.

        Args:
            id_medico: ID do médico.
            data: Data para consulta.

        Returns:
            Lista de agendamentos do médico na data especificada.
        """
        return self.repo.buscar_agendamentos_medico(id_medico, data)

    def cancelar_consulta(self, id_agendamento: int) -> None:
        """
        Cancela uma consulta.

        Args:
            id_agendamento: ID do agendamento a ser cancelado.
        """
        agendamento = self.repo.buscar_agendamento(id_agendamento)
        if not agendamento:
            raise ValueError(f"Agendamento com ID {id_agendamento} não encontrado.")

        agendamento.status = "cancelado"
        self.repo.atualizar_agendamento(agendamento)