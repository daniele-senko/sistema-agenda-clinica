from datetime import datetime, timedelta
# Importamos as classes Paciente e Medico para usá-las na Composição.
from models.paciente import Paciente
from models.medico import Medico

class Agendamento:
    """
    CLASSE DE COMPOSIÇÃO E ENCAPSULAMENTO

    Esta classe "contém" um Paciente e um Médico (COMPOSIÇÃO).
    Ela também protege seus dados internos (ENCAPSULAMENTO).
    """

    def __init__(self, paciente: Paciente, medico: Medico, data_hora_inicio: datetime, duracao_minutos: int):
        
        # --- COMPOSIÇÃO ---
        # O Agendamento "tem um" Paciente e "tem um" Médico.
        # Armazenamos os objetos inteiros.
        self._paciente = paciente
        self._medico = medico
        
        # --- ENCAPSULAMENTO ---
        # Estes atributos controlam o estado do Agendamento.
        # São protegidos para que só possam ser lidos (via getters)
        # ou alterados pelos métodos desta classe (cancelar(), etc.).
        self._data_hora_inicio = data_hora_inicio
        self._duracao_minutos = duracao_minutos
        self._status = "Agendado" # Status inicial padrão

    # --- Propriedades (Getters) ---
    
    @property
    def data_hora_fim(self) -> datetime:
        """
        Esta é uma "Propriedade Calculada", como pedido no requisito.
        Ela não armazena um valor, mas o calcula toda vez que é acessada.
        """
        return self._data_hora_inicio + timedelta(minutes=self._duracao_minutos)

    # Getters para a Pessoa 1 (BD) e Pessoa 3 (Lógica) poderem
    # ler os dados do agendamento.
    
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

    # --- Métodos de Encapsulamento ---
    
    def cancelar(self):
        """
        Este método ENCAPSULA a lógica de cancelamento.
        Em vez de a Pessoa 3 (Lógica) fazer "agendamento.status = 'Cancelado'",
        ela deve chamar "agendamento.cancelar()".
        
        Isso é bom porque, se no futuro tiver uma regra (ex: "não pode
        cancelar 1h antes"), a regra é adicionada AQUI, e o resto do
        sistema não precisa mudar.
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