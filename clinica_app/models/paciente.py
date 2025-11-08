# A importação com "." (from .pessoa...) significa "do mesmo pacote,
# pegue o arquivo pessoa e importe a classe Pessoa".
from .pessoa import Pessoa

class Paciente(Pessoa):
    """
    CLASSE CONCRETA (FILHA)
    
    Representa um Paciente.
    Aplica o pilar da HERANÇA, pois herda de Pessoa.
    """

    def __init__(self, nome: str, cpf: str, telefone: str, plano_saude: str):
        
        # 1. super().__init__(...) chama o construtor da classe Mãe (Pessoa)
        #    para inicializar os atributos comuns (nome, cpf, telefone).
        super().__init__(nome, cpf, telefone)
        
        # 2. Adiciona o atributo que é específico APENAS do Paciente.
        self._plano_saude = plano_saude

    @property
    def plano_saude(self):
        """ Getter para o atributo específico de Paciente. """
        return self._plano_saude

    def identificar(self):
        """
        IMPLEMENTAÇÃO DO POLIMORFISMO
        
        Esta é a implementação concreta do método abstrato 'identificar'
        definido em Pessoa. Ela é específica para o Paciente.
        """
        print("--- Identificação do Paciente ---")
        print(f"Nome: {self.nome}")
        print(f"CPF: {self.cpf}")
        print(f"Plano de Saúde: {self._plano_saude}")