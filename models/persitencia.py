import sqlite3
from sqlite3 import Error
from typing import List, Tuple, Optional
from models.pessoa import Pessoa
from models.paciente import Paciente
from models.medico import Medico
from models.agendamento import Agendamento

DB_FILE = "sistema_agenda_clinica.db"

class GerenciadorBD:
    """
    Camada de PERSITÊNCIA
    Responsável por todas as operações de banco de dados.
    Usa SQLite via sqlite3, que é parte da biblioteca padrão do Python.
    """

    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self._criar_tabelas()

    def _criar_tabelas(self):
        """Cria as tabelas necessárias no banco de dados, se não existirem."""
        comandos_sql = [
            """
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                telefone TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS medicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                telefone TEXT NOT NULL,
                especialidade TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_paciente INTEGER NOT NULL,
                id_medico INTEGER NOT NULL,
                data_hora_inicio TEXT NOT NULL,
                duracao_minutos INTEGER NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (id_paciente) REFERENCES pacientes (id),
                FOREIGN KEY (id_medico) REFERENCES medicos (id)
            );
            """
        ]
        conn = self._conectar()
        cursor = conn.cursor()
        for comando in comandos_sql:
            cursor.execute(comando)
        conn.commit()
        conn.close()