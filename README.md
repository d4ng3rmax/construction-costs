# 🏗️ Custos de Obra

## 📌 Descrição do Projeto
O **Custos de Obra** é um sistema de gestão de obras desenvolvido em **Flask** e **SQLAlchemy**, permitindo aos usuários cadastrarem obras, gerenciarem etapas, subetapas, fornecedores, materiais e serviços. O objetivo é manter um controle detalhado sobre os custos e processos envolvidos na construção.

## 🚀 Funcionalidades Principais
### ✅ **Gestão de Obras**
- Criar, editar e excluir obras
- Selecionar uma obra ativa para gestão
- Desselecionar uma obra ativa
- Limites de cadastro com base no plano do usuário

### ✅ **Gestão de Etapas e Subetapas**
- Criar, editar e excluir etapas e subetapas
- Relacionamento entre etapas e subetapas

### ✅ **Gestão de Materiais, Serviços e Fornecedores**
- Cadastro de materiais utilizados nas obras
- Cadastro de serviços vinculados a etapas e subetapas
- Registro de fornecedores vinculados aos materiais e serviços

### ✅ **Lançamentos de Custos**
- Adicionar lançamentos de custos de materiais
- Adicionar lançamentos de custos de serviços
- Adicionar lançamentos diversos

### ✅ **Relatórios e Análises**
- Resumo de custos da obra
- Fluxo de caixa mensal
- Quantitativo de materiais utilizados
- Relatório de custos por etapa e subetapa

---

## 🛠️ **Tecnologias Utilizadas**
- **Backend:** Flask + Flask-Login + Flask-WTF + Flask-Bcrypt
- **Banco de Dados:** SQLite + SQLAlchemy
- **Frontend:** HTML + CSS (SCSS) + JavaScript
- **Template Engine:** Jinja2
- **Bibliotecas Extras:** Flatpickr (para seleção de datas)

---

## 🔄 **Atualizações Recentes**
### 📌 **Feb 2025**
- 🔹 **Correção:** Agora, ao excluir uma obra, a obra selecionada só é desmarcada se for a mesma que está sendo excluída.
- 🔹 **Melhoria:** Adicionado um botão de "X" para desselecionar a obra ativa.
- 🔹 **Ajuste de Estilo:** Movido o CSS inline do botão de desselecionar para `./scss/_main.scss`.
- 🔹 **Correção de Identação:** Ajustado o VSCode para formatar o código automaticamente com `black`.

---

## 📥 **Instalação e Configuração**
### 🔧 **1. Clonar o repositório**
```bash
git clone https://github.com/seu-usuario/custos-de-obra.git
cd custos-de-obra
```

### 📦 **2. Criar e ativar um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate
```

### 📌 **3. Instalar dependências**
```bash
pip install -r requirements.txt
```

### 🛠️ **4. Executar a aplicação**
```bash
python main.py
```
Acesse o sistema via: **http://127.0.0.1:5000**

---

## 📜 **Estrutura do Projeto**
```
./base_dir/
│── static/                  # Arquivos CSS, JS e imagens
│── templates/               # Arquivos HTML (Jinja2)
│── instance/                # Configurações do banco SQLite
│── main.py                  # Arquivo principal para rodar a aplicação
│── routes.py                # Define todas as rotas Flask
│── models.py                # Modelos do banco de dados (SQLAlchemy)
│── forms.py                 # Formulários WTForms
│── TESTESDB.py              # Scripts para testes no banco
│── __init__.py              # Inicializa a aplicação Flask
```

---

## 📜 **Licença**
Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---
