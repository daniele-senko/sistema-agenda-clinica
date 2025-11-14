from datetime import datetime, timedelta
# Importamos as classes Paciente e Medico para usá-las na Composição.
from .paciente import Paciente
from .medico import Medico

class Agendamento:
    """
    CLASSE DE COMPOSIÇÃO E ENCAPSULAMENTO

    Esta classe "contém" um Paciente e um Médico (COMPOSIÇÃO).
    Ela também protege seus dados internos (ENCAPSULAMENTO).
    """

    def __init__(self, paciente: Paciente, medico: Medico, data_hora_inicio: datetime, duracao_minutos: int):
        
        # --- COMPOSIÇÃO ---
        self._paciente = paciente
        self._medico = medico
        
        # --- ENCAPSULAMENTO ---
        self._data_hora_inicio = data_hora_inicio
        self._duracao_minutos = duracao_minutos
        self._id = None # Para ser setado pela persistência
        
        # O status não é mais "Agendado" por padrão
        # --- COMENTÁRIO IMPORTANTE (MUDANÇA PÓS-VÍDEO) ---
        # NO VÍDEO, O STATUS ERA DEFINIDO COMO "Agendado" AQUI DENTRO.
        # MUDAMOS ISSO PORQUE O STATUS CORRETO DEVE SER CONTROLADO
        # PELA CAMADA DE LÓGICA (CLINICA) OU DE PERSISTÊNCIA (AO LER DO BANCO).
        # POR ISSO, O STATUS COMEÇA COMO 'None'.
        self._status = None 

    # --- Propriedades (Getters) ---
    
    @property
    def data_hora_fim(self) -> datetime:
        """
        Esta é uma "Propriedade Calculada", como pedido no requisito.
        Ela não armazena um valor, mas o calcula toda vez que é acessada.
        """
        return self._data_hora_inicio + timedelta(minutes=self._duracao_minutos)
    
    @property
    def paciente(self):
        return self._paciente

    @property
    def medico(self):
        return self._medico

    @property
    def data_hora_inicio(self):
        return self._data_hora_inicio
        
    @property
    def duracao_minutos(self):
        return self._duracao_minutos

    @property
    def status(self):
        return self._status

    @property
    def id(self):
        return self._id

    # --- Setters (Usados pela Lógica e Persistência) ---

    @id.setter
    def id(self, value: int):
        """Usado pela persistência para setar o ID do banco."""
        self._id = value

    @status.setter
    def status(self, value: str):
        """
        --- COMENTÁRIO IMPORTANTE (MUDANÇA PÓS-VÍDEO) ---
        ESTE MÉTODO FOI A CORREÇÃO PRINCIPAL.
        O VÍDEO TINHA O ERRO "property 'status' has no setter".
        
        ADICIONAMOS ESTE 'SETTER' PARA PERMITIR QUE A CLASSE 'Clinica'
        (Ex: agendamento.status = "agendado") E O 'AgendaRepository'
        (ao ler do banco) POSSAM DEFINIR O STATUS.
        """
        """Usado pela Clinica ou Repositório para definir o status."""
        self._status = value
    
    def cancelar(self):
        """
        Este método ENCAPSULA a lógica de cancelamento.
        """
        print(f"Agendamento em {self._data_hora_inicio} cancelado.")
        self._status = "Cancelado"

    def confirmar_realizacao(self):
        """
        Mesma lógica do cancelar(), mas para confirmar a realização.
        Encapsula a mudança de status.
        """
        print(f"Agendamento em {self._data_hora_inicio} realizado.")
        self._status = "Realizado"