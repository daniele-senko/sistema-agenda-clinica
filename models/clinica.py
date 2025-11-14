from datetime import datetime, timedelta, date
from typing import List
from models.agendamento import Agendamento
from models.medico import Medico
from models.paciente import Paciente
from persistencia import AgendaRepository 


class Clinica:
    """Classe que gerencia as regras de negócio da clínica."""

    def __init__(self, repo: AgendaRepository):
        """
        Inicializa a clínica com um repositório de dados.
        """
        self.repo = repo

    # --- NOVO ---
    def cadastrar_paciente(self, paciente: Paciente) -> int:
        """Cadastra um novo paciente, validando regras de negócio."""
        
        # REGRA: Não permitir CPF duplicado (em pacientes ou médicos)
        if self.repo.buscar_paciente_por_cpf(paciente.cpf) or self.repo.buscar_medico_por_cpf(paciente.cpf):
            raise ValueError(f"Já existe um usuário (paciente ou médico) cadastrado com o CPF {paciente.cpf}.")
        
        # REGRA: (Exemplo) Plano de saúde não pode estar vazio
        if not paciente.plano_saude or not paciente.plano_saude.strip():
             raise ValueError("O plano de saúde é obrigatório.")

        paciente_id = self.repo.salvar_paciente(paciente)
        paciente.id = paciente_id
        return paciente.id

    # --- NOVO ---
    def cadastrar_medico(self, medico: Medico) -> int:
        """Cadastra um novo médico, validando regras de negócio."""
        
        # REGRA: Não permitir CPF duplicado (em pacientes ou médicos)
        if self.repo.buscar_paciente_por_cpf(medico.cpf) or self.repo.buscar_medico_por_cpf(medico.cpf):
            raise ValueError(f"Este CPF já está em uso por outro usuário (paciente ou médico).")

        # REGRA: Não permitir CRM duplicado
        if self.repo.buscar_medico_por_crm(medico.crm):
            raise ValueError(f"O CRM {medico.crm} já está cadastrado.")

        medico_id = self.repo.salvar_medico(medico)
        medico.id = medico_id
        return medico.id

    def marcar_consulta(self, id_paciente: int, id_medico: int, inicio: datetime, duracao_min: int) -> Agendamento:
        """
        Marca uma consulta validando regras de negócio.
        ...
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
            duracao_minutos=duracao_min
        )
        agendamento.status = "agendado" # O status é setado aqui


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
        
        agendamentos = self.repo.buscar_agendamentos_por_medico_e_data(id_medico, inicio.date().isoformat())

        for ag in agendamentos:
            if ag.status == 'Cancelado':
                continue
            
            ag_fim = ag.data_hora_inicio + timedelta(minutes=ag.duracao_minutos)
            if (inicio < ag_fim and fim > ag.data_hora_inicio):
                return True

        return False

    def consultar_agenda_paciente(self, id_paciente: int) -> List[Agendamento]:
        """
        Retorna todas as consultas de um paciente.
        """
        return self.repo.buscar_agendamentos_por_paciente(id_paciente)

    def consultar_agenda_medico(self, id_medico: int, data: date) -> List[Agendamento]:
        """
        Retorna todas as consultas de um médico em uma data específica.
        """
        return self.repo.buscar_agendamentos_por_medico_e_data(id_medico, data.isoformat())

    def cancelar_consulta(self, id_agendamento: int) -> None:
        """
        Cancela uma consulta.
        """
        agendamento = self.repo.buscar_agendamento(id_agendamento)
        if not agendamento:
            raise ValueError(f"Agendamento com ID {id_agendamento} não encontrado.")

        agendamento.cancelar()
        
        self.repo.atualizar_agendamento(agendamento)
            
    def listar_todos_pacientes(self) -> List[Paciente]:
        """Retorna uma lista de todos os pacientes cadastrados."""
        return self.repo.buscar_todos_pacientes()
        
    def listar_todos_medicos(self) -> List[Medico]:
        """Retorna uma lista de todos os médicos cadastrados."""
        return self.repo.buscar_todos_medicos()

    # --- NOVO ---
    def atualizar_dados_paciente(self, id_paciente: int, novo_telefone: str, novo_plano: str) -> Paciente:
        """
A-        Atualiza os dados de um paciente, validando regras.
        """
        # REGRA: Valida se o paciente existe
        paciente = self.repo.buscar_paciente(id_paciente)
        if not paciente:
            raise ValueError(f"Paciente com ID {id_paciente} não encontrado.")
        
        # REGRA: (Exemplo) Valida se os dados não estão vazios
        if not novo_telefone.strip() or not novo_plano.strip():
            raise ValueError("Telefone e Plano de Saúde não podem ser vazios.")
            
        self.repo.atualizar_paciente(id_paciente, novo_telefone, novo_plano)
        
        # Retorna o objeto paciente ATUALIZADO, lendo do banco
        # Isso garante que estamos retornando os dados corretos
        # e respeitando o encapsulamento dos models (que não têm setters)
        return self.repo.buscar_paciente(id_paciente)