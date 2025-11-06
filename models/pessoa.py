# ABC (Abstract Base Classes) é o módulo do Python que usamos
# para criar classes abstratas, como aprendemos.
from abc import ABC, abstractmethod

class Pessoa(ABC):
    """
    CLASSE ABSTRATA (BASE)
    
    Define o "molde" para qualquer pessoa dentro do sistema (Médico ou Paciente).
    Ninguém pode criar um objeto "Pessoa" diretamente.
    
    Esta classe aplica o pilar da ABSTRAÇÃO.
    """
    
    def __init__(self, nome: str, cpf: str, telefone: str):
        """
        Construtor da classe base.
        
        Usamos um underscore '_' (ex: self._nome) para indicar que 
        esses atributos são "protegidos". Isso é parte do ENCAPSULAMENTO.
        """
        self._id = None
        self._nome = nome
        self._cpf = cpf
        self._telefone = telefone

    # --- Getters (Propriedades) ---
    # Usamos @property para criar "getters" no estilo Python.
    # Isso permite que a Pessoa 1 (BD) e a Pessoa 3 (Lógica)
    # leiam os dados (ex: pessoa.nome) sem poderem modificá-los
    # diretamente (ex: pessoa._nome = "novo").
    
    @property
    def nome(self):
        return self._nome
    
    @property
    def cpf(self):
        return self._cpf

    @property
    def telefone(self):
        return self._telefone

    # --- Método Abstrato ---
    
    @abstractmethod
    def identificar(self):
        """
        Este é um método abstrato, o que força as classes filhas
        (Paciente e Medico) a implementarem sua própria versão.
        
        Isso garante o nosso POLIMORFISMO.
        """
        pass