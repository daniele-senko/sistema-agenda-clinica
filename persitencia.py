import os.path
import sqlite3
from sqlite3 import Error
from typing import List, Tuple, Optional
from datetime import datetime, date, timedelta
from models.paciente import Paciente
from models.medico import Medico
from models.agendamento import Agendamento

DB_FILE = "sistema_agenda_clinica.db"

class AgendaRepository:
    """
    Camada de PERSITÊNCIA
    Responsável por todas as operações de banco de dados.
    Usa SQLite via sqlite3, que é parte da biblioteca padrão do Python.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._criar_tabelas()

    def _get_conexao(self):
        """Cria e retorna uma conexão com o banco de dados SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON;")  # Habilita suporte a chaves estrangeiras
            return conn
        except Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def _criar_tabelas(self):
        """Cria as tabelas necessárias no banco de dados, se não existirem."""
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                telefone TEXT NOT NULL
            );
            """)
            cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS medicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                telefone TEXT NOT NULL,
                especialidade TEXT NOT NULL
            );
            """)
            cursor.execute(
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
            """)
        conn.commit()
        conn.close()

def salvar_paciente(self, paciente: Paciente) -> int:
        """Salva um novo Paciente no banco de dados e retorna seu ID."""
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO pacientes (nome, cpf, telefone)
                    VALUES (?, ?, ?);
                    """,
                    (paciente.nome, paciente.cpf, paciente.telefone)
                )
                conn.commit()
                print("Paciente salvo com sucesso.")
                return cursor.lastrowid
            except sqlite3.IntegrityError as e:
                print(f"Erro ao salvar paciente: {e}")
                raise

def buscar_paciente(self, id_paciente: int) -> Optional[Paciente]:
        """Busca um Paciente pelo ID. Retorna None se não encontrado."""
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT nome, cpf, telefone
                FROM pacientes
                WHERE id = ?;
                """,
                (id_paciente,)
            )
            row = cursor.fetchone()
            if row:
                nome, cpf, telefone = row
                return Paciente(nome=nome, cpf=cpf, telefone=telefone, plano_saude="Desconhecido")
            return None

def buscar_todos_pacientes(self) -> List[Paciente]:
        """Retorna uma lista de todos os Pacientes no banco de dados."""
        pacientes = []
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT nome, cpf, telefone
                FROM pacientes;
                """
            )
            rows = cursor.fetchall()
            for row in rows:
                nome, cpf, telefone = row
                pacientes.append(Paciente(nome=nome, cpf=cpf, telefone=telefone, plano_saude="Desconhecido"))
        return pacientes

def salvar_medico(self, medico: Medico) -> int:
        """Salva um novo Médico no banco de dados e retorna seu ID."""
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO medicos (nome, cpf, telefone, especialidade)
                    VALUES (?, ?, ?, ?);
                    """,
                    (medico.nome, medico.cpf, medico.telefone, medico.especialidade)
                )
                conn.commit()
                print("Médico salvo com sucesso.")
                return cursor.lastrowid
            except sqlite3.IntegrityError as e:
                print(f"Erro ao salvar médico: {e}")
                raise

def buscar_medico(self, id_medico: int) -> Optional[Medico]:
        """Busca um Médico pelo ID. Retorna None se não encontrado."""
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT nome, cpf, telefone, especialidade
                FROM medicos
                WHERE id = ?;
                """,
                (id_medico,)
            )
            row = cursor.fetchone()
            if row:
                nome, cpf, telefone, especialidade = row
                return Medico(nome=nome, cpf=cpf, telefone=telefone, crm="Desconhecido", especialidade=especialidade, regras_disponibilidade={})
            return None

def buscar_todos_medicos(self) -> List[Medico]:
        """Retorna uma lista de todos os Médicos no banco de dados."""
        medicos = []
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT nome, cpf, telefone, especialidade
                FROM medicos;
                """
            )
            rows = cursor.fetchall()
            for row in rows:
                nome, cpf, telefone, especialidade = row
                medicos.append(Medico(nome=nome, cpf=cpf, telefone=telefone, crm="Desconhecido", especialidade=especialidade, regras_disponibilidade={}))
        return medicos

def salvar_agendamento(self, ag: Agendamento) -> int:
        """Salva um novo Agendamento no banco de dados e retorna seu ID."""
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO agendamentos (id_paciente, id_medico, data_hora_inicio, duracao_minutos, status)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (
                        ag.paciente.id,
                        ag.medico.id,
                        ag.data_hora_inicio.isoformat(),
                        ag.duracao_minutos,
                        ag.status
                    )
                )
                conn.commit()
                print("Agendamento salvo com sucesso.")
                return cursor.lastrowid
            except sqlite3.IntegrityError as e:
                print(f"Erro ao salvar agendamento: {e}")
                raise

def buscar_agendamentos_por_paciente(self, id_paciente: int) -> List[Agendamento]:
        """Retorna uma lista de Agendamentos para um dado Paciente."""
        agendamentos = []
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id_medico, data_hora_inicio, duracao_minutos, status
                FROM agendamentos
                WHERE id_paciente = ?;
                """,
                (id_paciente,)
            )
            rows = cursor.fetchall()
            for row in rows:
                id_medico, data_hora_inicio, duracao_minutos, status = row
                medico = self.buscar_medico(id_medico)
                paciente = self.buscar_paciente(id_paciente)
                if medico and paciente:
                    agendamentos.append(
                        Agendamento(
                            paciente=paciente,
                            medico=medico,
                            data_hora_inicio=datetime.fromisoformat(data_hora_inicio),
                            duracao_minutos=duracao_minutos
                        )
                    )
        return agendamentos

def buscar_agendamentos_por_medico_e_data(self, id_medico: int, data_iso: str) -> List[Agendamento]:
        """Retorna uma lista de Agendamentos para um dado Médico em uma data específica."""
        agendamentos = []
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id_paciente, data_hora_inicio, duracao_minutos, status
                FROM agendamentos
                WHERE id_medico = ? AND date(data_hora_inicio) = date(?);
                """,
                (id_medico, data_iso)
            )
            rows = cursor.fetchall()
            for row in rows:
                id_paciente, data_hora_inicio, duracao_minutos, status = row
                medico = self.buscar_medico(id_medico)
                paciente = self.buscar_paciente(id_paciente)
                if medico and paciente:
                    agendamentos.append(
                        Agendamento(
                            paciente=paciente,
                            medico=medico,
                            data_hora_inicio=datetime.fromisoformat(data_hora_inicio),
                            duracao_minutos=duracao_minutos
                        )
                    )
        return agendamentos
