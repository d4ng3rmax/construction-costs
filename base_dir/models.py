from base_dir import db, login_manager
from flask_login import UserMixin
from sqlalchemy import DateTime
from datetime import datetime


@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(id_usuario)


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(60), nullable=False)
    nivel = db.Column(db.Integer, nullable=False)
    plano = db.Column(db.String(60), nullable=False)

    obra_selecionada = db.Column(db.Integer)

    obras = db.relationship("Obra", backref="usuario", lazy=True)
    etapas = db.relationship("Etapa", backref="usuario", lazy=True)
    subetapas = db.relationship("Subetapa", backref="usuario", lazy=True)
    materiais = db.relationship("Materiais", backref="usuario", lazy=True)
    servicos = db.relationship("Servicos", backref="usuario", lazy=True)
    fornecedores = db.relationship("Fornecedores", backref="usuario", lazy=True)
    diversos = db.relationship("Diversos", backref="usuario", lazy=True)


class Obra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(90), nullable=False)
    endereco = db.Column(db.String(90), nullable=False)
    data_inicio = db.Column(DateTime, nullable=False)
    area = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    lancamentos_custo = db.relationship(
        "LancamentoCusto", back_populates="obra", lazy=True
    )
    lancamentos_servico = db.relationship(
        "LancamentoServico", back_populates="obra", lazy=True
    )
    lancamentos_diverso = db.relationship(
        "LancamentoDiverso", back_populates="obra", lazy=True
    )


class Etapa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    subetapas = db.relationship("Subetapa", backref="etapa", lazy=True)


class Subetapa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    etapa_id = db.Column(db.Integer, db.ForeignKey("etapa.id"), nullable=False)


class Materiais(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)


class Servicos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)


class Fornecedores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)


class Diversos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)


class LancamentoCusto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_lancamento = db.Column(DateTime, nullable=False)
    nota_fiscal = db.Column(db.String(15), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    preco_unit = db.Column(db.Float, nullable=False)

    # Chaves estrangeiras
    obra_id = db.Column(db.Integer, db.ForeignKey("obra.id"), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey("materiais.id"), nullable=False)
    fornecedor_id = db.Column(
        db.Integer, db.ForeignKey("fornecedores.id"), nullable=False
    )
    etapa_id = db.Column(db.Integer, db.ForeignKey("etapa.id"), nullable=False)
    subetapa_id = db.Column(db.Integer, db.ForeignKey("subetapa.id"), nullable=False)

    # Relacionamentos
    obra = db.relationship("Obra", back_populates="lancamentos_custo", lazy=True)
    etapa = db.relationship("Etapa", backref="lancamentos_custo", lazy=True)
    subetapa = db.relationship("Subetapa", backref="lancamentos_custo", lazy=True)
    material = db.relationship("Materiais", backref="lancamentos_custo", lazy=True)
    fornecedor = db.relationship("Fornecedores", backref="lancamentos_custo", lazy=True)


class LancamentoServico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_lancamento = db.Column(DateTime, nullable=False)
    nota_fiscal = db.Column(db.String(15), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    preco_unit = db.Column(db.Float, nullable=False)

    # Chaves estrangeiras
    obra_id = db.Column(db.Integer, db.ForeignKey("obra.id"), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey("servicos.id"), nullable=False)
    fornecedor_id = db.Column(
        db.Integer, db.ForeignKey("fornecedores.id"), nullable=False
    )
    etapa_id = db.Column(db.Integer, db.ForeignKey("etapa.id"), nullable=False)
    subetapa_id = db.Column(db.Integer, db.ForeignKey("subetapa.id"), nullable=False)

    # Relacionamentos
    obra = db.relationship("Obra", back_populates="lancamentos_servico", lazy=True)
    etapa = db.relationship("Etapa", backref="lancamentos_servico", lazy=True)
    subetapa = db.relationship("Subetapa", backref="lancamentos_servico", lazy=True)
    servico = db.relationship("Servicos", backref="lancamentos_servico", lazy=True)
    fornecedor = db.relationship(
        "Fornecedores", backref="lancamentos_servico", lazy=True
    )


class LancamentoDiverso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_lancamento = db.Column(DateTime, nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    preco_unit = db.Column(db.Float, nullable=False)

    # Chaves estrangeiras
    obra_id = db.Column(db.Integer, db.ForeignKey("obra.id"), nullable=False)
    diverso_id = db.Column(db.Integer, db.ForeignKey("diversos.id"), nullable=False)

    # Relacionamentos
    obra = db.relationship("Obra", back_populates="lancamentos_diverso", lazy=True)
    diverso = db.relationship("Diversos", backref="lancamentos_diverso", lazy=True)


class ContasPagar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_vencimento = db.Column(DateTime, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Pendente")  # Pendente, Pago, Cancelado
    nota_fiscal = db.Column(db.String(15), nullable=False)
