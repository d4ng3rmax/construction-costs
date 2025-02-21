from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField,
    SelectField,
    IntegerField,
    FieldList,
    FormField,
    FloatField,
)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from datetime import datetime
import re


class FormLogin(FlaskForm):
    email = StringField(
        "E-mail",
        validators=[
            DataRequired(message="Campo obrigatório"),
            Email(message="O campo deve ser um email válido"),
        ],
    )
    senha = PasswordField(
        "Senha", validators=[DataRequired(message="Campo obrigatório")]
    )
    dados = BooleanField("Lembrar Dados")
    botao = SubmitField("Entrar")


class FormCadastro(FlaskForm):
    email = StringField(
        "E-mail",
        validators=[
            DataRequired(message="Campo obrigatório"),
            Email(message="O campo deve ser um email válido"),
        ],
    )
    senha = PasswordField(
        "Senha", validators=[DataRequired(message="Campo obrigatório")]
    )
    confirmar_senha = PasswordField(
        "Confirmação da Senha",
        validators=[
            DataRequired(message="Campo obrigatório"),
            EqualTo("senha", message="As senhas devem ser iguais"),
        ],
    )
    botao = SubmitField("Cadastrar")


class FormAlterarSenha(FlaskForm):
    senha = PasswordField(
        "Nova Senha", validators=[DataRequired(message="Campo obrigatório")]
    )
    confirmar_senha = PasswordField(
        "Confirmação da Nova Senha",
        validators=[
            DataRequired(message="Campo obrigatório"),
            EqualTo("senha", message="As senhas devem ser iguais"),
        ],
    )
    botao = SubmitField("Alterar Senha")


class FormRecuperarSenha(FlaskForm):
    email = StringField(
        "E-mail",
        validators=[
            DataRequired(message="Campo obrigatório"),
            Email(message="O campo deve ser um email válido"),
        ],
    )
    botao = SubmitField("Recuperar conta")


def validate_numerical_decimal(form, field):
    pattern = r"^\d+([,.]\d+)?$"
    if not re.match(pattern, field.data):
        raise ValidationError("O campo deve ser um número.")

    # Substitua a vírgula por um ponto para converter em float
    field.data = field.data.replace(",", ".")

    # Converta a string para float
    try:
        field.data = float(field.data)
    except ValueError:
        raise ValidationError("O campo deve ser um número.")


def validate_nota_fiscal(form, field):
    pattern = r"^\d+([,.]\d+)?$"
    if not re.match(pattern, field.data):
        raise ValidationError("O campo deve ser um número.")

    # Substitua a vírgula por um ponto para converter em float
    field.data = field.data.replace(",", ".")

    # Converta a string para float
    try:
        field.data = int(field.data)
    except ValueError:
        raise ValidationError("O campo deve ser um número.")


class FormNovaObra(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    endereco = StringField("Endereço", validators=[DataRequired()])
    area = StringField("Área", validators=[DataRequired(), validate_numerical_decimal])
    data_inicio = StringField(
        "Data de Início",
        validators=[DataRequired()],
        default=datetime.now().strftime("%d/%m/%Y"),
    )
    descricao = TextAreaField("Descrição")
    botao_novaobra = SubmitField("Nova Obra")

    def validate_data_inicio(self, field):
        try:
            datetime.strptime(field.data, "%d/%m/%Y")
        except ValueError:
            raise ValidationError("Formato de data inválido. Use DD/MM/YYYY.")


class FormEditarObra(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    endereco = StringField("Endereço", validators=[DataRequired()])
    area = StringField("Área", validators=[DataRequired(), validate_numerical_decimal])
    data_inicio = StringField("Data de Início", validators=[DataRequired()])
    descricao = TextAreaField("Descrição")
    botao_salvarobra = SubmitField("Salvar Obra")

    def validate_data_inicio(self, field):
        try:
            datetime.strptime(field.data, "%d/%m/%Y")
        except ValueError:
            raise ValidationError("Formato de data inválido. Use DD/MM/YYYY.")


class FormEtapas(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    botao = SubmitField("Adicionar Etapa")


class FormEditarEtapas(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    botao = SubmitField("Salvar Etapa")


class FormSubetapas(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    etapa_relacionada = SelectField("Etapa Relacionada", validators=[DataRequired()])
    botao = SubmitField("Adicionar Subetapa")


class FormEditarSubetapas(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    etapa_relacionada = SelectField("Etapa Relacionada", validators=[DataRequired()])
    botao = SubmitField("Salvar Subetapa")


class FormMateriais(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    botao = SubmitField("Adicionar Material")


class FormEditarMateriais(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    botao = SubmitField("Salvar Material")


class FormServicos(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    botao = SubmitField("Adicionar Serviço")


class FormEditarServicos(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    botao = SubmitField("Salvar Serviço")


class FormFornecedores(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    botao = SubmitField("Adicionar Fornecedor")


class FormEditarFornecedores(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    botao = SubmitField("Salvar Fornecedor")


class FormDiversos(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    botao = SubmitField("Adicionar Custo Diversos")


class FormEditarDiversos(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    botao = SubmitField("Salvar Custo Diverso")


def validar_etapa(form, field):
    if field.data == 99999:
        raise ValidationError("Etapa inválida.")


def validar_subetapa(form, field):
    if field.data == 99999:
        raise ValidationError("Subetapa inválida.")


class FormLancamentoCusto(FlaskForm):
    data_lancamento = StringField(
        "Data", validators=[DataRequired()], default=datetime.now().strftime("%d/%m/%Y")
    )
    fornecedor_id = SelectField("Fornecedor", coerce=int, validators=[DataRequired()])
    nota_fiscal = StringField(
        "Nota Fiscal", validators=[DataRequired(), validate_nota_fiscal]
    )
    etapa_id = SelectField(
        "Etapa", coerce=int, validators=[DataRequired(), validar_etapa]
    )
    subetapa_id = SelectField(
        "Subetapa", coerce=int, validators=[DataRequired(), validar_etapa]
    )
    material_id = SelectField("Material", coerce=int, validators=[DataRequired()])
    quantidade = StringField(
        "Quantidade", validators=[DataRequired(), validate_numerical_decimal]
    )
    preco_unitario = StringField(
        "Preço Unitário", validators=[DataRequired(), validate_numerical_decimal]
    )
    adicionar_item = SubmitField("Adicionar Item")

    def validate_data_lancamento(self, field):
        try:
            datetime.strptime(field.data, "%d/%m/%Y")
        except ValueError:
            raise ValidationError("Formato de data inválido. Use DD/MM/YYYY.")


class FormEditarLancamentoCusto(FlaskForm):
    data_lancamento = StringField(
        "Data", validators=[DataRequired()], default=datetime.now().strftime("%d/%m/%Y")
    )
    fornecedor_id = SelectField("Fornecedor", coerce=int, validators=[DataRequired()])
    nota_fiscal = StringField(
        "Nota Fiscal", validators=[DataRequired(), validate_nota_fiscal]
    )
    etapa_id = SelectField(
        "Etapa", coerce=int, validators=[DataRequired(), validar_etapa]
    )
    subetapa_id = SelectField(
        "Subetapa", coerce=int, validators=[DataRequired(), validar_etapa]
    )
    material_id = SelectField("Material", coerce=int, validators=[DataRequired()])
    quantidade = StringField(
        "Quantidade", validators=[DataRequired(), validate_numerical_decimal]
    )
    preco_unitario = StringField(
        "Preço Unitário", validators=[DataRequired(), validate_numerical_decimal]
    )
    adicionar_item = SubmitField("Salvar Item")

    def validate_data_lancamento(self, field):
        try:
            datetime.strptime(field.data, "%d/%m/%Y")
        except ValueError:
            raise ValidationError("Formato de data inválido. Use DD/MM/YYYY.")


class FormLancamentoServico(FlaskForm):
    data_lancamento = StringField(
        "Data", validators=[DataRequired()], default=datetime.now().strftime("%d/%m/%Y")
    )
    fornecedor_id = SelectField("Fornecedor", coerce=int, validators=[DataRequired()])
    nota_fiscal = StringField(
        "Nota Fiscal", validators=[DataRequired(), validate_nota_fiscal]
    )
    etapa_id = SelectField(
        "Etapa", coerce=int, validators=[DataRequired(), validar_etapa]
    )
    subetapa_id = SelectField(
        "Subetapa", coerce=int, validators=[DataRequired(), validar_etapa]
    )
    servico_id = SelectField("Serviço", coerce=int, validators=[DataRequired()])
    quantidade = StringField(
        "Quantidade", validators=[DataRequired(), validate_numerical_decimal]
    )
    preco_unitario = StringField(
        "Preço Unitário", validators=[DataRequired(), validate_numerical_decimal]
    )
    adicionar_item = SubmitField("Adicionar Item")

    def validate_data_lancamento(self, field):
        try:
            datetime.strptime(field.data, "%d/%m/%Y")
        except ValueError:
            raise ValidationError("Formato de data inválido. Use DD/MM/YYYY.")


class FormEditarLancamentoServico(FlaskForm):
    data_lancamento = StringField(
        "Data", validators=[DataRequired()], default=datetime.now().strftime("%d/%m/%Y")
    )
    fornecedor_id = SelectField("Fornecedor", coerce=int, validators=[DataRequired()])
    nota_fiscal = StringField(
        "Nota Fiscal", validators=[DataRequired(), validate_nota_fiscal]
    )
    etapa_id = SelectField(
        "Etapa", coerce=int, validators=[DataRequired(), validar_etapa]
    )
    subetapa_id = SelectField(
        "Subetapa", coerce=int, validators=[DataRequired(), validar_etapa]
    )
    servico_id = SelectField("Serviço", coerce=int, validators=[DataRequired()])
    quantidade = StringField(
        "Quantidade", validators=[DataRequired(), validate_numerical_decimal]
    )
    preco_unitario = StringField(
        "Preço Unitário", validators=[DataRequired(), validate_numerical_decimal]
    )
    adicionar_item = SubmitField("Salvar Item")

    def validate_data_lancamento(self, field):
        try:
            datetime.strptime(field.data, "%d/%m/%Y")
        except ValueError:
            raise ValidationError("Formato de data inválido. Use DD/MM/YYYY.")


class FormLancamentoDiverso(FlaskForm):
    data_lancamento = StringField(
        "Data", validators=[DataRequired()], default=datetime.now().strftime("%d/%m/%Y")
    )
    diverso_id = SelectField("Custo Diversos", coerce=int, validators=[DataRequired()])
    quantidade = StringField(
        "Quantidade", validators=[DataRequired(), validate_numerical_decimal]
    )
    preco_unitario = StringField(
        "Preço Unitário", validators=[DataRequired(), validate_numerical_decimal]
    )
    adicionar_item = SubmitField("Adicionar Item")

    def validate_data_lancamento(self, field):
        try:
            datetime.strptime(field.data, "%d/%m/%Y")
        except ValueError:
            raise ValidationError("Formato de data inválido. Use DD/MM/YYYY.")


class FormEditarLancamentoDiverso(FlaskForm):
    data_lancamento = StringField(
        "Data", validators=[DataRequired()], default=datetime.now().strftime("%d/%m/%Y")
    )
    diverso_id = SelectField("Custo Diversos", coerce=int, validators=[DataRequired()])
    quantidade = StringField(
        "Quantidade", validators=[DataRequired(), validate_numerical_decimal]
    )
    preco_unitario = StringField(
        "Preço Unitário", validators=[DataRequired(), validate_numerical_decimal]
    )
    adicionar_item = SubmitField("Salvar Item")

    def validate_data_lancamento(self, field):
        try:
            datetime.strptime(field.data, "%d/%m/%Y")
        except ValueError:
            raise ValidationError("Formato de data inválido. Use DD/MM/YYYY.")


class MaterialItemForm(FlaskForm):
    etapa_id = SelectField("Etapa", coerce=int, validators=[DataRequired()])
    subetapa_id = SelectField("Subetapa", coerce=int, validators=[DataRequired()])
    material_id = SelectField("Material", coerce=int, validators=[DataRequired()])
    quantidade = FloatField("Quantidade", validators=[DataRequired()])
    preco_unitario = FloatField("Preço Unitário", validators=[DataRequired()])


class FormNotaFiscal(FlaskForm):
    data_lancamento = StringField("Data", validators=[DataRequired()])
    fornecedor_id = SelectField("Fornecedor", coerce=int, validators=[DataRequired()])
    nota_fiscal = StringField("Nota Fiscal", validators=[DataRequired()])
    itens = FieldList(FormField(MaterialItemForm), min_entries=1)
    adicionar_item = SubmitField("Adicionar Material")
    confirmar_nf = SubmitField("Lançar Nota Fiscal")
