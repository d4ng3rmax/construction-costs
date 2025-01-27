from base_dir import app, db
from base_dir.models import *
from datetime import datetime

with app.app_context():
    db.drop_all()
    db.create_all()

with app.app_context():
    usuario = Usuario.query.filter_by(email="teste2@gmail.com").first()
    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()

    data_lancamento_id = "15/07/2024"
    data_lancamento = datetime.strptime(data_lancamento_id, '%d/%m/%Y')
    nota_fiscal_lancamento = 1
    quantidade_lancamento = 1
    preco_unitario_lancamento = 1
    material_lancamento_id = 5
    fornecedor_lancamento_id = 1
    etapa_lancamento_id = 1
    subetapa_lancamento_id = 1

    for i in range(1, 20001):
        lancamento = LancamentoCusto(data_lancamento=data_lancamento, nota_fiscal=nota_fiscal_lancamento,
                                     quantidade=quantidade_lancamento, preco_unit=preco_unitario_lancamento,
                                     material_id=material_lancamento_id, fornecedor_id=fornecedor_lancamento_id,
                                     etapa_id=etapa_lancamento_id, subetapa_id=subetapa_lancamento_id,
                                     obra_id=obra_selecionada.id)

        obra_selecionada.lancamentos_custo.append(lancamento)
    db.session.commit()
