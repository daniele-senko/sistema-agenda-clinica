from persistencia import AgendaRepository
import os

db_file = "test_clinica.db"

def test_agenda_repository():
    if os.path.exists(db_file):
        os.remove(db_file)
        print("Banco de dados de teste removido.")

    repo = AgendaRepository(db_file)

    # Teste: salvar_agendamento
    from models.paciente import Paciente
    from models.medico import Medico
    from models.agendamento import Agendamento
    from datetime import datetime

    paciente0 = Paciente(nome="Paciente Teste", cpf="000.000.000-00", telefone="(00) 00000-0000",
                         plano_saude="Teste Saúde")
    medico0 = Medico(nome="Dr. Teste", cpf="111.111.111-11", telefone="(11) 11111-1111", crm="CRM0000", especialidade="Teste Especialidade", regras_disponibilidade={"dias_semana": [0,1,2,3,4], "hora_inicio": "08:00", "hora_fim": "17:00", "bloqueios": []})
    agendamento = Agendamento(paciente=paciente0, medico=medico0, data_hora_inicio=datetime(2024, 6, 15, 10, 0), duracao_minutos=30)

    repo.salvar_paciente(paciente0)
    repo.salvar_medico(medico0)
    repo.salvar_agendamento(agendamento)

    repo.buscar_todos_medicos()

if __name__ == "__main__":
    test_agenda_repository()