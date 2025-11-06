from persistencia import AgendaRepository

def test_agenda_repository():
    repo = AgendaRepository("test_clinica.db")

    # Teste: salvar_agendamento
    from models.paciente import Paciente
    from models.medico import Medico
    from models.agendamento import Agendamento
    from datetime import datetime

    paciente = Paciente(nome="Teste Paciente", data_nascimento="1990-01-01", telefone="123456789")
    medico = Medico(nome="Teste Médico", especialidade="Cardiologia", telefone="987654321")
    novo_agendamento = Agendamento(paciente=paciente, medico=medico, data_hora_inicio=datetime(2024, 6, 15, 10, 0), duracao_minutos=30)

    agendamento_id = repo.salvar_agendamento(novo_agendamento)
    assert isinstance(agendamento_id, int)

    # Verificar se o agendamento foi salvo corretamente
    agendamentos_apos_salvar = repo.buscar_agendamentos_por_medico_e_data(1, "2024-06-15")
    assert any(ag.id == agendamento_id for ag in agendamentos_apos_salvar)

    # Teste: buscar_agendamentos_por_medico_e_data
    agendamentos = repo.buscar_agendamentos_por_medico_e_data(1, "2024-06-15")
    assert isinstance(agendamentos, list)
    for ag in agendamentos:
        assert ag.medico.id == 1
        assert ag.data_hora_inicio.date().isoformat() == "2024-06-15"

    print("Todos os testes do AgendaRepository passaram.")

if __name__ == "__main__":
    test_agenda_repository()