from models.pessoa import Pessoa

class Medico(Pessoa):
    """
    CLASSE CONCRETA (FILHA)
    
    Representa um Médico.
    Também aplica o pilar da HERANÇA (herda de Pessoa).
    """

    def __init__(self, nome: str, cpf: str, telefone: str, crm: str, especialidade: str, regras_disponibilidade: dict):
        
        # 1. Chama o construtor da classe Mãe (Pessoa).
        super().__init__(id, nome, cpf,)

        # 2. Inicializa os atributos específicos do Médico.
        self._crm = crm
        self._especialidade = especialidade
        self._regras_disponibilidade = regras_disponibilidade

    # --- Getters Específicos do Médico ---
    
    @property
    def crm(self):
        return self._crm
        
    @property
    def especialidade(self):
        return self._especialidade

    @property
    def regras_disponibilidade(self):
        """
        Este getter é MUITO IMPORTANTE para a Pessoa 3 (Lógica).
        É lendo esta propriedade que a classe Clinica saberá
        o horário de trabalho do médico e poderá agendar consultas corretamente.
        
        A Pessoa 1 (BD) também precisará ler isso para salvar no banco.
        """
        return self._regras_disponibilidade

    def identificar(self):
        """
        IMPLEMENTAÇÃO DO POLIMORFISMO

        Esta é a versão do 'identificar' específica para o Médico.
        Note que é diferente da implementação do Paciente.
        """
        print("--- Identificação do Médico ---")
        print(f"Nome: Dr. {self.nome}")
        print(f"CRM: {self._crm} (Especialidade: {self._especialidade})")