import json
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
                telefone TEXT NOT NULL,
                plano_saude TEXT NOT NULL
            );
            """)
            cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS medicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                telefone TEXT NOT NULL,
                crm TEXT,
                especialidade TEXT,
                regras_disponibilidade TEXT
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

    def salvar_paciente(self, paciente: Paciente) -> int:
            """Salva um novo Paciente no banco de dados e retorna seu ID."""
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        INSERT INTO pacientes (nome, cpf, telefone, plano_saude)
                        VALUES (?, ?, ?, ?);
                        """,
                        (paciente.nome, paciente.cpf, paciente.telefone, paciente.plano_saude)
                    )
                    conn.commit()
                    paciente.id = cursor.lastrowid
                    return paciente.id
                except sqlite3.IntegrityError as e:
                    raise

    def buscar_paciente(self, id_paciente: int) -> Optional[Paciente]:
            """Busca um Paciente pelo ID. Retorna None se não encontrado."""
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT id, nome, cpf, telefone, plano_saude
                        FROM pacientes
                        WHERE id = ?;
                        """,
                        (id_paciente,)
                    )
                    row = cursor.fetchone()
                    if row:
                        pid, nome, cpf, telefone, plano = row
                        p = Paciente(nome=nome, cpf=cpf, telefone=telefone, plano_saude=plano)
                        p.id = pid
                        return p
                    return None
                except sqlite3.Error as e:
                    raise

    def buscar_todos_pacientes(self) -> List[Paciente]:
            """Retorna uma lista de todos os Pacientes no banco de dados."""
            pacientes = []
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT id, nome, cpf, telefone, plano_saude
                        FROM pacientes;
                        """
                    )
                    rows = cursor.fetchall()
                    for row in rows:
                        pid, nome, cpf, telefone, plano = row
                        p = Paciente(nome=nome, cpf=cpf, telefone=telefone, plano_saude=plano)
                        p.id = pid
                        pacientes.append(p)
                    return pacientes
                except sqlite3.Error as e:
                    print(f"Erro ao buscar pacientes: {e}")
                    raise

    def deletar_paciente(self, id_paciente: int) -> None:
            """Deleta um Paciente pelo ID."""
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        DELETE FROM pacientes
                        WHERE id = ?;
                        """,
                        (id_paciente,)
                    )
                    conn.commit()
                except sqlite3.Error as e:
                    raise

    def buscar_paciente_por_cpf(self, cpf: str) -> Optional[Paciente]:
            """Busca um Paciente pelo CPF. Retorna None se não encontrado."""
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT id, nome, cpf, telefone, plano_saude
                        FROM pacientes
                        WHERE cpf = ?;
                        """,
                        (cpf,)
                    )
                    row = cursor.fetchone()
                    if row:
                        pid, nome, cpf_row, telefone, plano = row
                        p = Paciente(nome=nome, cpf=cpf_row, telefone=telefone, plano_saude=plano)
                        p.id = pid
                        return p
                    return None
                except sqlite3.Error as e:
                    raise


    def salvar_medico(self, medico: Medico) -> int:
            """Salva um novo Médico no banco de dados e retorna seu ID."""
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    # Serializar regras_disponibilidade como JSON
                    regras_json = json.dumps(medico.regras_disponibilidade) if medico.regras_disponibilidade else "{}"
                    cursor.execute(
                        """
                        INSERT INTO medicos (nome, cpf, telefone, especialidade, crm, regras_disponibilidade)
                        VALUES (?, ?, ?, ?, ?, ?);
                        """,
                        (
                            medico.nome,
                            medico.cpf,
                            medico.telefone,
                            medico.especialidade,
                            medico.crm,
                            regras_json
                        )
                    )
                    conn.commit()
                    medico.id = cursor.lastrowid
                    return medico.id
                except sqlite3.IntegrityError as e:
                    raise

    def buscar_medico(self, id_medico: int) -> Optional[Medico]:
            """Busca um Médico pelo ID. Retorna None se não encontrado."""
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT id, nome, cpf, telefone, crm, especialidade, regras_disponibilidade
                        FROM medicos
                        WHERE id = ?;
                        """,
                        (id_medico,)
                    )
                    row = cursor.fetchone()
                    if row:
                        mid, nome, cpf, telefone, crm, especialidade, regras_json = row
                        regras = json.loads(regras_json) if regras_json else {}
                        m = Medico(nome=nome, cpf=cpf, telefone=telefone, crm=crm, especialidade=especialidade, regras_disponibilidade=regras)
                        m.id = mid
                        return m
                    return None
                except sqlite3.Error as e:
                    raise

    def buscar_medico_por_crm(self, crm: str) -> Optional[Medico]:
            """Busca um Médico pelo CRM. Retorna None se não encontrado."""
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT id, nome, cpf, telefone, crm, especialidade, regras_disponibilidade
                        FROM medicos
                        WHERE crm = ?;
                        """,
                        (crm,)
                    )
                    row = cursor.fetchone()
                    if row:
                        mid, nome, cpf, telefone, crm_row, especialidade, regras_json = row
                        regras = json.loads(regras_json) if regras_json else {}
                        m = Medico(nome=nome, cpf=cpf, telefone=telefone, crm=crm_row, especialidade=especialidade, regras_disponibilidade=regras)
                        m.id = mid
                        return m
                    return None
                except sqlite3.Error as e:
                    raise

    # --- NOVO ---
    def buscar_medico_por_cpf(self, cpf: str) -> Optional[Medico]:
            """Busca um Médico pelo CPF. Retorna None se não encontrado."""
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT id, nome, cpf, telefone, crm, especialidade, regras_disponibilidade
                        FROM medicos
                        WHERE cpf = ?;
                        """,
                        (cpf,)
                    )
                    row = cursor.fetchone()
                    if row:
                        mid, nome, cpf_row, telefone, crm, especialidade, regras_json = row
                        regras = json.loads(regras_json) if regras_json else {}
                        m = Medico(nome=nome, cpf=cpf_row, telefone=telefone, crm=crm, especialidade=especialidade, regras_disponibilidade=regras)
                        m.id = mid
                        return m
                    return None
                except sqlite3.Error as e:
                    raise

    def buscar_todos_medicos(self) -> List[Medico]:
            """Retorna uma lista de todos os Médicos no banco de dados."""
            medicos = []
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT id, nome, cpf, telefone, crm, especialidade, regras_disponibilidade
                        FROM medicos;
                        """
                    )
                    rows = cursor.fetchall()
                    for row in rows:
                        mid, nome, cpf, telefone, crm, especialidade, regras_json = row
                        regras = json.loads(regras_json) if regras_json else {}
                        m = Medico(nome=nome, cpf=cpf, telefone=telefone, crm=crm, especialidade=especialidade, regras_disponibilidade=regras)
                        m.id = mid
                        medicos.append(m)
                    return medicos
                except sqlite3.Error as e:
                    raise

    def deletar_medico(self, id_medico: int) -> None:
            """Deleta um Médico pelo ID."""
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        DELETE FROM medicos
                        WHERE id = ?;
                        """,
                        (id_medico,)
                    )
                    conn.commit()
                except sqlite3.Error as e:
                    raise

    def salvar_agendamento(self, ag: Agendamento) -> int:
            """Salva um novo Agendamento no banco de dados e retorna seu ID."""
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    # O ID do paciente já deve vir setado pela Clinica
                    if not ag.paciente.id:
                        raise ValueError("Paciente sem ID não pode agendar.")
                    
                    # O ID do médico já deve vir setado pela Clinica
                    if not ag.medico.id:
                        raise ValueError("Médico sem ID não pode agendar.")

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
                    return cursor.lastrowid
                except sqlite3.IntegrityError as e:
                    raise

    def buscar_agendamentos_por_paciente(self, id_paciente: int) -> List[Agendamento]:
            """Retorna uma lista de Agendamentos para um dado Paciente."""
            agendamentos = []
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT id, id_medico, data_hora_inicio, duracao_minutos, status
                        FROM agendamentos
                        WHERE id_paciente = ?;
                        """,
                        (id_paciente,)
                    )
                    rows = cursor.fetchall()
                    for row in rows:
                        aid, id_medico, data_hora_inicio, duracao_minutos, status = row
                        medico = self.buscar_medico(id_medico)
                        paciente = self.buscar_paciente(id_paciente)
                        if medico and paciente:
                            ag = Agendamento(
                                paciente=paciente,
                                medico=medico,
                                data_hora_inicio=datetime.fromisoformat(data_hora_inicio),
                                duracao_minutos=duracao_minutos
                            )
                            ag.id = aid
                            ag.status = status
                            agendamentos.append(ag)
                    return agendamentos
                except sqlite3.Error as e:
                    raise

    def buscar_agendamentos_por_medico_e_data(self, id_medico: int, data_iso: str) -> List[Agendamento]:
            """Retorna uma lista de Agendamentos para um dado Médico em uma data específica."""
            agendamentos = []
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT id, id_paciente, data_hora_inicio, duracao_minutos, status
                        FROM agendamentos
                        WHERE id_medico = ? AND date(data_hora_inicio) = date(?);
                        """,
                        (id_medico, data_iso)
                    )
                    rows = cursor.fetchall()
                    for row in rows:
                        aid, id_paciente, data_hora_inicio, duracao_minutos, status = row
                        medico = self.buscar_medico(id_medico)
                        paciente = self.buscar_paciente(id_paciente)
                        if medico and paciente:
                            ag = Agendamento(
                                paciente=paciente,
                                medico=medico,
                                data_hora_inicio=datetime.fromisoformat(data_hora_inicio),
                                duracao_minutos=duracao_minutos
                            )
                            ag.id = aid
                            ag.status = status
                            agendamentos.append(ag)
                    return agendamentos
                except sqlite3.Error as e:
                    raise

    def deletar_agendamento(self, id_agendamento: int) -> None:
            """Deleta um Agendamento pelo ID."""
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        DELETE FROM agendamentos
                        WHERE id = ?;
                        """,
                        (id_agendamento,)
                    )
                    conn.commit()
                except sqlite3.Error as e:
                    print(f"Erro ao deletar agendamento: {e}")
                    raise

    @staticmethod
    def initdb(db_path: str):
        """Inicializa o banco de dados criando as tabelas necessárias."""
        if not os.path.exists(db_path):
            repo = AgendaRepository(db_path)
            print("Banco de dados inicializado.")
        else:
            print("Banco de dados já existe.")

    def buscar_agendamento(self, id_agendamento: int) -> Optional[Agendamento]:
            """Busca um Agendamento pelo ID. Retorna None se não encontrado."""
            with self._get_conexao() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT id, id_paciente, id_medico, data_hora_inicio, duracao_minutos, status
                        FROM agendamentos
                        WHERE id = ?;
                        """,
                        (id_agendamento,)
                    )
                    row = cursor.fetchone()
                    if row:
                        aid, id_paciente, id_medico, data_hora_inicio, duracao, status = row
                        
                        paciente = self.buscar_paciente(id_paciente)
                        medico = self.buscar_medico(id_medico)
                        
                        if not paciente or not medico:
                            return None # Ou lançar um erro, caso de dados órfãos

                        ag = Agendamento(
                            paciente=paciente,
                            medico=medico,
                            data_hora_inicio=datetime.fromisoformat(data_hora_inicio),
                            duracao_minutos=duracao
                        )
                        ag.id = aid
                        ag.status = status # Seta o status vindo do banco
                        return ag
                    return None
                except sqlite3.Error as e:
                    raise
                    
    def atualizar_agendamento(self, ag: Agendamento) -> None:
        """Atualiza um agendamento existente no banco (ex: status)."""
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    UPDATE agendamentos
                    SET status = ?
                    WHERE id = ?;
                    """,
                    (ag.status, ag.id)
                )
                conn.commit()
            except sqlite3.Error as e:
                raise

    # --- NOVO ---
    def atualizar_paciente(self, id_paciente: int, telefone: str, plano_saude: str) -> None:
        """Atualiza o telefone e o plano de saúde de um paciente existente."""
        with self._get_conexao() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    UPDATE pacientes
                    SET telefone = ?, plano_saude = ?
                    WHERE id = ?;
                    """,
                    (telefone, plano_saude, id_paciente)
                )
                conn.commit()
                if cursor.rowcount == 0:
                    # Isso garante que não tentamos atualizar um ID que não existe
                    raise ValueError(f"Paciente com ID {id_paciente} não encontrado para atualização.")
            except sqlite3.Error as e:
                print(f"Erro ao atualizar paciente: {e}")
                raise