## Sistema de Agenda de Clínica Médica
*Desenvolvimento de um Sistema Robusto de Gerenciamento de Agendamentos*

### Objetivo
Modelar e implementar um sistema de backend robusto para gerenciar os agendamentos de uma clinica médica. O sistema deve aplicar os quatro pilares da POO para cadastrar entidades, gerenciar horários de trabalho, validar conflitos de agendamento e permitir consultas detalhadas da agenda.

### 3. Contexto
Uma clínica médica precisa de um sistema para gerenciar agendamentos de consultas, verificando disponibilidade de médicos, evitando conflitos de horários e permitindo consultas da agenda por paciente e por médico.

### Requisitos Técnicos

#### Tecnologias e Conceitos
* Utilizar Python, sem qualquer biblioteca de interface gráfica.
* Aplicar explicitamente: Abstração, Herança, Encapsulamento e Polimorfismo.
* Integrar com um banco de dados SQLite, garantindo que a lógica de negócio permaneça separada da lógica de persistência (Separação de Responsabilidades).

---

### Detalhamento das Funcionalidades Exigidas
O sistema deve implementar as seguintes lógicas de negócio:

*1. Verificação de Disponibilidade (Lógica de Horários):*
Ao marcar uma consulta, o sistema deve validar duas camadas de disponibilidade:
* Horário de Trabalho do Médico: Verificar se a data/hora solicitada está dentro do expediente de trabalho padrão do médico (ex: Segunda, das 8h às 12h).
* Conflito de Agendamento: Verificar se a data/hora e duração solicitadas colidem com qualquer outro agendamento já marcado (e não cancelado) para aquele médico.

*2. Consulta de Agenda por Paciente:*
O sistema deve ser capaz de receber a identificação de um paciente e retornar uma lista de todos os seus agendamentos (passados e futuros), ordenados por data.

*3. Consulta de Agenda por Médico:*
O sistema deve ser capaz de receber a identificação de um médico e uma data especifica, e retornar uma lista de todos os seus agendamentos (de todos os status) para aquele dia, ordenados por hora.

---

### Modelo de Classes Essenciais

*1. Abstração e Herança*
* *Pessoa (Classe Abstrata):* Atributos: nome, cpf, telefone. Método Abstrato: identificar().
* *Paciente (Classe Concreta):* Herda de Pessoa. Atributos Adicionais: plano_saude. Implementa identificar().
* *Medico (Classe Concreta):* Herda de Pessoa. Atributos Adicionais: crm, especialidade. Atributo de Lógica (Novo): regras_disponibilidade.
    * Sugestão de implementação: Um dicionário ou objeto que define os horários de trabalho. Ex: {'segunda': [('08:00', '12:00'), ('14:00', '18:00')], 'terca': [...]}.

*2. Encapsulamento e Composição*
* *Agendamento:* Composição: Contém _paciente (objeto Paciente) e _medico (objeto Medico).
* *Atributos (Privados):* _data_hora_inicio (datetime), _duracao_minutos (int) (Ex: 30, 45, 60), status (string: 'Agendado', 'Cancelado', 'Realizado').
* *Propriedades (Getters):* data_hora_fim (propriedade calculada que retorna _data_hora_inicio + duracao).
* *Métodos (Encapsulamento):* cancelar(): Altera _status para 'Cancelado', aplicando regras de negócio se necessário. confirmar_realizacao(): Altera _status para 'Realizado'.

*3. Separação de Responsabilidades (Banco de Dados)*
* *GerenciadorBD (Classe de Repositório):* Responsável por toda a interação SQL com o clinica.db.
* *Tabelas Esperadas:* pacientes, medicos, agendamentos. A tabela medicos deve incluir uma coluna para armazenar as regras_disponibilidade (sugestão: armazenar como um JSON string). A tabela agendamentos deve incluir data_hora_inicio e duracao_minutos.
* *Métodos de Busca:* buscar_paciente(id_paciente): Retorna um objeto Paciente, buscar_medico(id_medico): Retorna um objeto Medico (deve desserializar as regras de disponibilidade), buscar_agendamentos_por_paciente(id_paciente): Retorna uma list[Agendamento].
* buscar_agendamentos_por_medico_e_data(id_medico, data): Retorna uma list[Agendamento] apenas para o dia especificado.

*4. Classe Orquestradora (Lógica de Negócios)*
* *Clinica:* Contém uma instância de GerenciadorBD. Não contém SQL.
* *Método (Lógica Principal):* marcar_consulta(id_paciente, id_medico, data_hora_desejada, duracao_minutos):
    * Busca o objeto medico usando o GerenciadorBD.
    * Chama um método privado: _verificar_disponibilidade(medico, data_hora_desejada, duracao_minutos).
    * Se disponível, busca o paciente, cria o objeto Agendamento e o salva usando o GerenciadorBD.
    * Se indisponível (seja por regra de trabalho ou conflito), retorna uma mensagem de erro.
* *Método Privado (Lógica de Horários):* _verificar_disponibilidade(medico, data_hora, duracao):
    * Verifica Regra de Trabalho: Usa o atributo medico.regras_disponibilidade para checar se a data_hora e a data_hora + duracao estão dentro do expediente daquele dia da semana. Se não, retorna False.
    * Verifica Conflitos: Usa _db.buscar_agendamentos_por_medico_e_data(medico.id, data_hora.date()) para pegar todas as consultas do dia.
    * Itera sobre os agendamentos retornados (que não estejam 'Cancelados'). Para cada agendamento existente, verifica se há sobreposição de horários.
    * Se encontrar sobreposição, retorna False (Conflito).
    * Se passar pelas duas verificações, retorna True.
* *Método (Consulta):* consultar_agenda_paciente(id_paciente): Usa o GerenciadorBD para buscar todos os agendamentos do paciente. Imprime os agendamentos formatados.
* *Método (Consulta):* consultar_agenda_medico(id_medico, data): Usa o GerenciadorBD para buscar todos os agendamentos do médico naquela data. Imprime os agendamentos formatados.
* *Método (Polimorfismo):* listar_membros_clinica(): Busca todos os Pacientes e Medicos, coloca-os numa lista de Pessoas e chama identificar() em cada um.

---

### 7. Critérios de Avaliação
* *Aplicação Correta da POO (40%):*
    * Abstração: Uso correto de Pessoa como classe base abstrata.
    * Encapsulamento: Proteção de atributos e encapsulamento da lógica de BD.
    * Herança: Estrutura clara (Paciente/Medico herdam de Pessoa).
    * Polimorfismo: Método identificar() implementado de formas diferentes.
* *Integração com SQLite (25%):*
    * Modelagem correta do banco com três tabelas.
    * Persistência de objetos (Pacientes, Medicos) e agendamentos.
    * Separação clara entre lógica de negócio e persistência.
* *Lógica de Validação de Disponibilidade (25%):*
    * Implementação correta da verificação de horário de trabalho.
    * Implementação correta da verificação de conflitos de agendamento.
    * Tratamento adequado de exceções e casos especiais.
* *Funcionalidades de Consulta (10%):*
    * Sistema de consulta por paciente funcional.
    * Sistema de consulta por médico e data funcional.
    * Ordenação correta dos resultados.
