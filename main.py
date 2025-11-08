import json
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from persistencia import AgendaRepository
from models.medico import Medico
from models.paciente import Paciente
from models.clinica import Clinica

# Define o caminho do banco de dados
db_path = os.path.join(os.path.dirname(__file__), "clinica.db")


def obter_regras_interativas() -> dict:
    """
    Cria um menu interativo para definir os horários de trabalho
    e retorna um dicionário de regras.
    """
    regras = {}
    dias_semana = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
    print("\n--- Definir Regras de Disponibilidade ---")

    for dia in dias_semana:
        resposta = input(f"Trabalha na {dia.capitalize()}? (s/n): ").strip().lower()

        if resposta == "s":
            print(f"  Digite os intervalos para {dia.capitalize()}.")
            print("  (Ex: 08:00-12:00, 14:00-18:00) Pressione Enter para pular.")
            intervalos_str = input("  Intervalos: ").strip()

            if intervalos_str:
                lista_intervalos = [
                    intervalo.strip() for intervalo in intervalos_str.split(",")
                ]
                regras[dia] = lista_intervalos
            else:
                print(f"  Nenhum horário definido para {dia.capitalize()}.")

    print("\nRegras de disponibilidade definidas:")
    print(json.dumps(regras, indent=2) if regras else "Nenhuma regra definida.")
    return regras


def cadastrar_medico(clinica: Clinica):
    """Cadastra um novo médico no sistema."""
    print("\n=== Cadastro de Médico ===")
    nome = input("Nome do médico: ")
    cpf = input("CPF do médico: ")
    telefone = input("Telefone do médico: ")
    crm = input("CRM do médico: ")
    especialidade = input("Especialidade do médico: ")
    regras_dict = obter_regras_interativas()

    try:
        medico = Medico(
            nome=nome,
            cpf=cpf,
            telefone=telefone,
            crm=crm,
            especialidade=especialidade,
            regras_disponibilidade=regras_dict,
        )

        medico_id = clinica.cadastrar_medico(medico)
        print(f"\nMédico cadastrado com sucesso! ID: {medico_id}")

    # Captura os erros de negócio (ex: CPF duplicado)
    except ValueError as e:
        print(f"\n[ERRO DE NEGÓCIO] Não foi possível cadastrar: {e}")
    except Exception as e:
        print(f"Erro inesperado ao cadastrar médico: {e}")

def cadastrar_paciente(clinica: Clinica):
    """Cadastra um novo paciente no sistema."""
    print("\n=== Cadastro de Paciente ===")
    nome = input("Nome do paciente: ")
    cpf = input("CPF do paciente: ")
    telefone = input("Telefone do paciente: ")
    plano_saude = input("Plano de saúde do paciente: ")

    try:
        paciente = Paciente(
            nome=nome, cpf=cpf, telefone=telefone, plano_saude=plano_saude
        )
        # Chama a camada de lógica (clinica) que fará a validação
        paciente_id = clinica.cadastrar_paciente(paciente)
        print(f"Paciente cadastrado com sucesso! ID: {paciente_id}")

    # Captura os erros de negócio (ex: CPF duplicado)
    except ValueError as e:
        print(f"\n[ERRO DE NEGÓCIO] Não foi possível cadastrar: {e}")
    except Exception as e:
        print(f"Erro ao cadastrar paciente: {e}")


def marcar_consulta(clinica):
    """Marca uma consulta no sistema."""
    print("\n=== Marcar Consulta ===")
    try:
        id_paciente = int(input("ID do paciente: "))
        id_medico = int(input("ID do médico: "))
        inicio_str = input("Data e hora da consulta (YYYY-MM-DD HH:MM): ")
        duracao_min = int(input("Duração da consulta (em minutos): "))

        inicio_dt = datetime.strptime(inicio_str, "%Y-%m-%d %H:%M")

        agendamento = clinica.marcar_consulta(
            id_paciente=id_paciente,
            id_medico=id_medico,
            inicio=inicio_dt,
            duracao_min=duracao_min,
        )
        print("\nConsulta marcada com sucesso!")
        print(
            json.dumps(
                {
                    "id_agendamento": agendamento.id,
                    "data_hora_inicio": agendamento.data_hora_inicio.isoformat(),
                    "duracao_minutos": agendamento.duracao_minutos,
                    "status": agendamento.status,
                },
                indent=4,
                ensure_ascii=False,
            )
        )

    except ValueError as e:
        # Captura erros de digitação (ex: data inválida) ou de negócio (ex: horário)
        print(f"\n[ERRO] Não foi possível marcar consulta: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


def listar_consultas(clinica):
    """Lista as consultas de um paciente."""
    print("\n=== Listar Consultas ===")
    try:
        id_paciente = int(input("ID do paciente: "))
        consultas = clinica.consultar_agenda_paciente(id_paciente)

        if not consultas:
            print("Nenhuma consulta encontrada para este paciente.")
            return

        print(f"\nConsultas do paciente (ID: {id_paciente}):")
        for consulta in consultas:
            print(
                f"- ID: {consulta.id} | {consulta.data_hora_inicio} | "
                f"Médico: {consulta.medico.nome} | Status: {consulta.status}"
            )
    except ValueError as e:
        print(f"Erro: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


def listar_pacientes(clinica):
    """Lista todos os pacientes cadastrados."""
    print("\n=== Lista de Pacientes Cadastrados ===")
    try:
        pacientes = clinica.listar_todos_pacientes()
        if not pacientes:
            print("Nenhum paciente cadastrado.")
            return

        print("-" * 40)
        for p in pacientes:
            print(
                f"ID: {p.id} | Nome: {p.nome} | CPF: {p.cpf} | Plano: {p.plano_saude}"
            )
        print("-" * 40)

    except Exception as e:
        print(f"Erro ao listar pacientes: {e}")


def listar_medicos(clinica):
    """Lista todos os médicos cadastrados."""
    print("\n=== Lista de Médicos Cadastrados ===")
    try:
        medicos = clinica.listar_todos_medicos()
        if not medicos:
            print("Nenhum médico cadastrado.")
            return

        print("-" * 40)
        for m in medicos:
            print(
                f"ID: {m.id} | Nome: Dr(a). {m.nome} | CRM: {m.crm} | Espec: {m.especialidade}"
            )
        print("-" * 40)

    except Exception as e:
        print(f"Erro ao listar médicos: {e}")


def cancelar_consulta(clinica):
    """Cancela uma consulta existente."""
    print("\n=== Cancelar Consulta ===")
    try:
        id_agendamento = int(input("Digite o ID do agendamento a ser cancelado: "))

        clinica.cancelar_consulta(id_agendamento)

        print(f"Agendamento ID {id_agendamento} cancelado com sucesso.")

    except ValueError as e:
        print(f"Erro ao cancelar consulta: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def atualizar_paciente(clinica: Clinica):
    """Atualiza dados de um paciente."""
    print("\n=== Atualizar Paciente ===")
    try:
        id_paciente = int(input("ID do paciente a ser atualizado: "))

        # Busca o paciente primeiro para mostrar os dados atuais
        paciente = clinica.repo.buscar_paciente(
            id_paciente
        )
        if not paciente:
            print(f"Paciente ID {id_paciente} não encontrado.")
            return

        print(
            f"Atualizando paciente: {paciente.nome} (Plano atual: {paciente.plano_saude})"
        )
        print("Pressione Enter para manter o valor atual.")

        novo_telefone = input(f"Novo telefone ({paciente.telefone}): ").strip()
        novo_plano = input(f"Novo plano de saúde ({paciente.plano_saude}): ").strip()

        # Usa os dados antigos se o usuário não digitar nada
        if not novo_telefone:
            novo_telefone = paciente.telefone
        if not novo_plano:
            novo_plano = paciente.plano_saude

        paciente_atualizado = clinica.atualizar_dados_paciente(
            id_paciente, novo_telefone, novo_plano
        )

        print(f"Paciente atualizado com sucesso!")
        print(f"  Novo Telefone: {paciente_atualizado.telefone}")
        print(f"  Novo Plano: {paciente_atualizado.plano_saude}")

    except ValueError as e:
        print(f"\n[ERRO] Não foi possível atualizar: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


def main():
    """Função principal que executa o menu do sistema."""
    print("Sistema de Agendamento de Clínica")
    print("=" * 40)

    repo = AgendaRepository(db_path)
    clinica = Clinica(repo)

    while True:
        print("\n" + "=" * 40)
        print("Menu Principal:")
        print("1. Cadastrar médico")
        print("2. Cadastrar paciente")
        print("3. Marcar consulta")
        print("4. Listar consultas de um paciente")
        print("5. Listar pacientes cadastrados")
        print("6. Listar médicos cadastrados")
        print("7. Cancelar consulta")
        print("8. Atualizar dados do paciente")
        print("9. Sair")
        print("=" * 40)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_medico(clinica)
        elif opcao == "2":
            cadastrar_paciente(clinica)
        elif opcao == "3":
            marcar_consulta(clinica)
        elif opcao == "4":
            listar_consultas(clinica)
        elif opcao == "5":
            listar_pacientes(clinica)
        elif opcao == "6":
            listar_medicos(clinica)
        elif opcao == "7":
            cancelar_consulta(clinica)
        elif opcao == "8":
            atualizar_paciente(clinica)
        elif opcao == "9":
            print("Encerrando o sistema...")
            break
        else:
            print("Opção inválida! Tente novamente.")


if __name__ == "__main__":
    main()
