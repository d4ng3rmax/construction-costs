from flask import render_template, redirect, flash, url_for, request, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
from base_dir import app, db, bcrypt
from base_dir.forms import *
from base_dir.models import *
from datetime import datetime


@app.route("/")
def home():
    return render_template("home.html")


def extract_numerical_part(item):
    numerical_parts = re.findall(r"\d+\.?\d*", item)
    if numerical_parts:
        return [float(part.replace(",", ".")) for part in numerical_parts]
    return []


@app.route("/acesso", methods=["GET", "POST"])
def acesso():
    form_login = FormLogin()

    if form_login.validate_on_submit():
        email = form_login.email.data
        senha = form_login.senha.data
        dados = form_login.dados.data

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, senha):
            login_user(usuario, remember=dados)
            flash(
                f"Login feito com sucesso! E-mail: {form_login.email.data}",
                "alert-success",
            )
            par_next = request.args.get("next")
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for("dashboard"))
        else:
            flash("Falha no login. Email ou senha incorretos.", "alert-danger")

    return render_template("acesso.html", form_login=form_login)


@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash(f"Logout feito com sucesso!", "alert-success")
    return redirect(url_for("home"))


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    form_cadastro = FormCadastro()

    if form_cadastro.validate_on_submit():
        email = form_cadastro.email.data
        senha = form_cadastro.senha.data
        senha_cript = bcrypt.generate_password_hash(senha)
        nivel = 1
        plano = "Básico"

        # Verificar se o e-mail já está em uso
        try:
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente:
                flash(
                    "Este e-mail já está cadastrado. Escolha outro e-mail.",
                    "alert-danger",
                )
                return redirect(url_for("cadastro"))
        except:
            pass

        # Criar um novo usuário
        novo_usuario = Usuario(email=email, senha=senha_cript, nivel=nivel, plano=plano)
        db.session.add(novo_usuario)
        db.session.commit()

        # Efetuar login automaticamente após o cadastro
        login_user(novo_usuario, remember=True)

        flash(f"Conta criada com sucesso! E-mail: {email}", "alert-success")
        return redirect(url_for("dashboard"))

    return render_template("cadastro.html", form_cadastro=form_cadastro)


@app.route("/recuperar-senha", methods=["GET", "POST"])
def recuperarsenha():
    form_recuperar_senha = FormRecuperarSenha()

    return render_template(
        "recuperarsenha.html", form_recuperar_senha=form_recuperar_senha
    )


@app.route("/meu-perfil", methods=["GET", "POST"])
@login_required
def meuperfil():
    form_alterar_senha = FormAlterarSenha()
    usuario = current_user

    if form_alterar_senha.validate_on_submit():
        senha = form_alterar_senha.senha.data
        senha_cript = bcrypt.generate_password_hash(senha)
        usuario.senha = senha_cript

        db.session.commit()
        flash("Senha alterada com sucesso!", "alert-success")
        return redirect(url_for("meuperfil"))

    return render_template(
        "meuperfil.html", usuario=usuario, form_alterar_senha=form_alterar_senha
    )


@app.route("/alterar-plano", methods=["GET", "POST"])
@login_required
def alterarplano():
    usuario = current_user

    return render_template("alterarplano.html", usuario=usuario)


@app.route("/dashboard")
@login_required
def dashboard():
    usuario = current_user
    n_obras = 0
    area_construida = 0

    for obra in usuario.obras:
        n_obras += 1
        area_construida += obra.area

    # Verificar o limite de lançamentos
    n_mat = 0
    n_ser = 0
    n_div = 0
    for n in usuario.obras:
        for m in n.lancamentos_custo:
            n_mat += 1
        for s in n.lancamentos_servico:
            n_ser += 1
        for d in n.lancamentos_diverso:
            n_div += 1
    n_lanc = n_mat + n_ser + n_div

    return render_template(
        "dashboard.html",
        usuario=usuario,
        n_obras=n_obras,
        area_construida=area_construida,
        n_mat=n_mat,
        n_ser=n_ser,
        n_div=n_div,
        n_lanc=n_lanc,
    )


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.nivel != 2:
            return redirect(url_for("dashboard"))
        return func(*args, **kwargs)

    return decorated_view


@app.route("/dashboard/admin-page/")
@admin_required
@login_required
def admin():
    usuario = current_user
    usuarios = Usuario.query.all()
    obras = Obra.query.all()
    n_usuarios = 0
    n_basico = 0
    n_premium = 0
    n_obras = 0

    for n in usuarios:
        n_usuarios += 1

    for no in obras:
        n_obras += 1

    return render_template(
        "admin.html", usuario=usuario, n_usuarios=n_usuarios, n_obras=n_obras
    )


@app.route("/cadastro/obras", methods=["GET", "POST"])
@login_required
def obras():
    # print("📩 Dados recebidos no POST:", request.form)  # 🔍 Verifica se os dados chegam no servidor
    usuario = current_user
    form_nova_obra = FormNovaObra()
    prev_page = request.args.get("prev_page")

    if form_nova_obra.validate_on_submit():
        obra_nome = form_nova_obra.nome.data
        obra_nome = obra_nome.lower()
        obra_endereco = form_nova_obra.endereco.data
        obra_area = form_nova_obra.area.data
        obra_data_inicio_str = form_nova_obra.data_inicio.data
        obra_data_inicio = datetime.strptime(obra_data_inicio_str, "%d/%m/%Y")
        obra_descricao = form_nova_obra.descricao.data
        obra = Obra(
            nome=obra_nome,
            endereco=obra_endereco,
            data_inicio=obra_data_inicio,
            area=obra_area,
            descricao=obra_descricao,
        )

        # Verificar os limites de usuario
        n_obras = 0
        for n in usuario.obras:
            n_obras += 1

        # if usuario.plano == "Básico" and n_obras >= 1:
        if usuario.plano == "Básico" and n_obras >= 5:
            flash("Limite máximo de obras cadastradas já foi atingido", "alert-danger")
            return redirect(url_for("obras"))

        if usuario.plano == "Avançado" and n_obras >= 3:
            flash("Limite máximo de obras cadastradas já foi atingido", "alert-danger")
            return redirect(url_for("obras"))

        # Validar obra com mesmo nome
        obra_existente = Obra.query.filter_by(nome=obra_nome).first()
        if obra_existente:
            flash("Já existe uma obra com esse nome", "alert-danger")
            return render_template(
                "obras.html", form_nova_obra=form_nova_obra, usuario=usuario
            )

        usuario.obras.append(obra)
        db.session.commit()
        return redirect(url_for("obras"))

    obra_id = request.form.get("obra_id")
    action = request.form.get("action")

    if action == "selecionar":
        obra = Obra.query.get(obra_id)
        usuario.obra_selecionada = obra.id
        db.session.commit()

        if prev_page:
            return redirect(url_for(prev_page))
        else:
            return redirect(url_for("obras"))

    #  if action == "excluir":
    #      obra = Obra.query.get(obra_id)
    #      if obra:
    #          lancamentos = LancamentoCusto.query.filter_by(obra_id=obra.id)
    #          if lancamentos:
    #              for lancamento in lancamentos:
    #                  db.session.delete(lancamento)
    #          db.session.delete(obra)
    #          usuario.obra_selecionada = None
    #          db.session.commit()
    #          return redirect(url_for("obras"))

    if action == "excluir":
        obra = Obra.query.get(obra_id)
        if obra:
            # Deletar os lançamentos da obra antes de excluí-la
            lancamentos = LancamentoCusto.query.filter_by(obra_id=obra.id).all()
            for lancamento in lancamentos:
                db.session.delete(lancamento)

            # Excluir a obra
            db.session.delete(obra)

            # Desmarcar a obra selecionada apenas se for a mesma que está sendo excluída
            if usuario.obra_selecionada == obra.id:
                usuario.obra_selecionada = None

            db.session.commit()
            flash("Obra excluída com sucesso!", "alert-success")
            return redirect(url_for("obras"))

    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()

    return render_template(
        "obras.html",
        form_nova_obra=form_nova_obra,
        usuario=usuario,
        obra_selecionada=obra_selecionada,
        prev_page=prev_page,
    )


@app.route("/cadastro/obras/editar/ID-<int:obra_id>", methods=["GET", "POST"])
@login_required
def obraseditar(obra_id):
    usuario = current_user
    form_editar_obra = FormEditarObra()
    obra = Obra.query.filter_by(id=obra_id).first()
    obra_nome_original = obra.nome

    if form_editar_obra.validate_on_submit():
        obra_nome = form_editar_obra.nome.data.lower()
        obra_endereco = form_editar_obra.endereco.data
        obra_area = form_editar_obra.area.data
        obra_data_inicio_str = form_editar_obra.data_inicio.data
        obra_data_inicio = datetime.strptime(obra_data_inicio_str, "%d/%m/%Y")
        obra_descricao = form_editar_obra.descricao.data

        # Validar obra com mesmo nome
        obra_existente = Obra.query.filter_by(nome=obra_nome).first()
        if obra_nome == obra_nome_original:
            pass
        elif obra_existente:
            flash("Já existe uma obra com esse nome", "alert-danger")
            return render_template(
                "obraseditar.html", form_editar_obra=form_editar_obra, usuario=usuario
            )

        # Atualizar os campos da obra com os dados do formulário
        obra.nome = obra_nome
        obra.endereco = obra_endereco
        obra.area = obra_area
        obra.data_inicio = obra_data_inicio
        obra.descricao = obra_descricao

        db.session.commit()
        flash("Obra editada com sucesso!", "alert-success")
        return redirect(url_for("obras"))

    # Preencher o formulário com os dados existentes da obra
    form_editar_obra.nome.data = obra.nome
    form_editar_obra.endereco.data = obra.endereco
    form_editar_obra.area.data = str(obra.area)
    form_editar_obra.data_inicio.data = obra.data_inicio.strftime("%d/%m/%Y")
    form_editar_obra.descricao.data = obra.descricao

    return render_template(
        "obraseditar.html", form_editar_obra=form_editar_obra, usuario=usuario
    )


@app.route("/cadastro/obras/desselecionar", methods=["POST"])
@login_required
def desselecionar_obra():
    usuario = current_user
    usuario.obra_selecionada = None  # Remove a obra selecionada
    db.session.commit()

    flash("Obra desselecionada com sucesso!", "alert-info")
    return redirect(url_for("obras"))


@app.route("/cadastro/etapas", methods=["GET", "POST"])
@login_required
def etapas():
    usuario = current_user
    form_etapas = FormEtapas()

    if form_etapas.validate_on_submit():
        etapa_nome = form_etapas.nome.data
        etapa_nome = etapa_nome.lower()
        etapa = Etapa(nome=etapa_nome, usuario=usuario)

        # Validar obra com mesmo nome
        etapa_existente = Etapa.query.filter_by(nome=etapa_nome).first()
        if etapa_existente:
            flash("Já existe uma etapa com esse nome", "alert-danger")
            return render_template(
                "etapas.html", form_etapas=form_etapas, usuario=usuario
            )

        usuario.etapas.append(etapa)
        db.session.commit()
        return redirect(url_for("etapas"))

    etapa_id = request.form.get("etapa_id")
    action = request.form.get("action")
    if action == "excluir":
        etapa = Etapa.query.get(etapa_id)
        if etapa:
            subetapas = Subetapa.query.filter_by(etapa_id=etapa_id)
            if subetapas:
                for subetapa in subetapas:
                    db.session.delete(subetapa)
            db.session.delete(etapa)
            db.session.commit()
            return redirect(url_for("etapas"))

    return render_template("etapas.html", form_etapas=form_etapas, usuario=usuario)


@app.route("/cadastro/etapas/editar/ID-<int:etapa_id>", methods=["GET", "POST"])
@login_required
def etapaseditar(etapa_id):
    usuario = current_user
    form_editar_etapas = FormEditarEtapas()
    etapa = Etapa.query.filter_by(id=etapa_id).first()
    etapa_nome_original = etapa.nome

    if form_editar_etapas.validate_on_submit():
        etapa_nome = form_editar_etapas.nome.data.lower()

        # Validar etapa com mesmo nome
        etapa_existente = Etapa.query.filter_by(
            nome=etapa_nome, usuario=usuario
        ).first()
        if etapa_nome == etapa_nome_original:
            pass
        elif etapa_existente:
            flash("Já existe uma etapa com esse nome", "alert-danger")
            return render_template(
                "etapaseditar.html",
                form_editar_etapas=form_editar_etapas,
                usuario=usuario,
            )

        # Atualizar os campos da obra com os dados do formulário
        etapa.nome = etapa_nome

        db.session.commit()
        flash("Etapa editada com sucesso!", "alert-success")
        return redirect(url_for("etapas"))

    # Preencher o formulário com os dados existentes da obra
    form_editar_etapas.nome.data = etapa.nome

    return render_template(
        "etapaseditar.html", form_editar_etapas=form_editar_etapas, usuario=usuario
    )


@app.route("/cadastro/subetapas", methods=["GET", "POST"])
@login_required
def subetapas():
    usuario = current_user
    form_subetapas = FormSubetapas()
    etapas = Etapa.query.all()

    sorted_etapas = sorted(etapas, key=lambda etapa: etapa.nome)
    form_subetapas.etapa_relacionada.choices = [
        (etapa.id, etapa.nome.capitalize()) for etapa in sorted_etapas
    ]

    if form_subetapas.validate_on_submit():
        subetapa_nome = form_subetapas.nome.data
        subetapa_nome = subetapa_nome.lower()
        etapa_id = form_subetapas.etapa_relacionada.data

        # Verificar duplicidade
        subetapa_existente = Subetapa.query.filter_by(nome=subetapa_nome).first()
        if subetapa_existente:
            flash("Já existe uma subetapa com esse nome", "alert-danger")
            return render_template(
                "subetapas.html", form_subetapas=form_subetapas, usuario=usuario
            )

        nova_subetapa = Subetapa(nome=subetapa_nome, usuario=usuario, etapa_id=etapa_id)
        usuario.subetapas.append(nova_subetapa)
        db.session.commit()

        return redirect(url_for("subetapas"))

    subetapa_id = request.form.get("subetapa_id")
    action = request.form.get("action")
    if action == "excluir":
        subetapa = Subetapa.query.get(subetapa_id)
        if subetapa:
            db.session.delete(subetapa)
            db.session.commit()
            return redirect(url_for("subetapas"))

    return render_template(
        "subetapas.html", form_subetapas=form_subetapas, usuario=usuario
    )


@app.route("/cadastro/subetapas/editar/ID-<int:subetapa_id>", methods=["GET", "POST"])
@login_required
def subetapaseditar(subetapa_id):
    usuario = current_user
    form_editar_subetapas = FormEditarSubetapas()
    subetapa = Subetapa.query.filter_by(id=subetapa_id).first()
    subetapa_nome_original = subetapa.nome

    etapas = Etapa.query.all()
    sorted_etapas = sorted(etapas, key=lambda etapa: etapa.nome)
    form_editar_subetapas.etapa_relacionada.choices = [
        (etapa.id, etapa.nome.capitalize()) for etapa in sorted_etapas
    ]

    if form_editar_subetapas.validate_on_submit():
        subetapa_nome = form_editar_subetapas.nome.data.lower()
        etapa_escolhida = form_editar_subetapas.etapa_relacionada.data

        # Validar obra com mesmo nome
        subetapa_existente = Subetapa.query.filter_by(nome=subetapa_nome).first()
        if subetapa_nome == subetapa_nome_original:
            pass
        elif subetapa_existente:
            flash("Já existe uma subetapa com esse nome", "alert-danger")
            return render_template(
                "subetapaseditar.html",
                form_editar_subetapas=form_editar_subetapas,
                usuario=usuario,
            )

        # Atualizar os campos da obra com os dados do formulário
        subetapa.nome = subetapa_nome
        subetapa.etapa_id = etapa_escolhida

        db.session.commit()
        flash("Subetapa editada com sucesso!", "alert-success")
        return redirect(url_for("subetapas"))

    # Preencher o formulário com os dados existentes da obra
    etapas = Etapa.query.all()
    sorted_etapas = sorted(etapas, key=lambda etapa: etapa.nome)
    form_editar_subetapas.etapa_relacionada.choices = [
        (etapa.id, etapa.nome.capitalize()) for etapa in sorted_etapas
    ]
    form_editar_subetapas.etapa_relacionada.default = subetapa.etapa_id
    form_editar_subetapas.process()
    form_editar_subetapas.nome.data = subetapa.nome.capitalize()

    return render_template(
        "subetapaseditar.html",
        form_editar_subetapas=form_editar_subetapas,
        usuario=usuario,
    )


@app.route("/cadastro/materiais", methods=["GET", "POST"])
@login_required
def materiais():
    form_materiais = FormMateriais()
    usuario = current_user

    if form_materiais.validate_on_submit():
        material_nome = form_materiais.nome.data.strip().lower()

        # Verificar duplicidade
        material_existente = Materiais.query.filter_by(nome=material_nome).first()
        if material_existente:
            flash("Já existe um material com esse nome!", "alert-danger")
            return render_template(
                "materiais.html",
                form_materiais=form_materiais,
                usuario=usuario,
                materiais=sorted(usuario.materiais, key=lambda m: m.nome),
            )

        n_materiais = len(usuario.materiais)
        limite_materiais = 10 if usuario.plano == "Básico" else 250

        if n_materiais >= limite_materiais:
            flash(
                "Limite máximo de materiais cadastrados já foi atingido!",
                "alert-danger",
            )
            return render_template(
                "materiais.html",
                form_materiais=form_materiais,
                usuario=usuario,
                materiais=sorted(usuario.materiais, key=lambda m: m.nome),
            )

        novo_material = Materiais(nome=material_nome, usuario=usuario)
        db.session.add(novo_material)
        db.session.commit()
        flash("Material cadastrado com sucesso!", "alert-success")

        return redirect(url_for("materiais"))

    materiais_ordenados = sorted(usuario.materiais, key=lambda item: item.nome.lower())

    material_id = request.form.get("material_id")
    action = request.form.get("action")

    if action == "excluir":
        material = Materiais.query.get(material_id)
        if material:
            db.session.delete(material)
            db.session.commit()
            flash("Material excluído com sucesso!", "alert-success")
            return redirect(url_for("materiais"))  # 🔄 Atualiza a lista após a exclusão

    return render_template(
        "materiais.html",
        form_materiais=form_materiais,
        usuario=usuario,
        materiais=materiais_ordenados,
    )


@app.route("/cadastro/materiais/editar/ID-<int:material_id>", methods=["GET", "POST"])
@login_required
def materiaiseditar(material_id):
    usuario = current_user
    form_editar_materiais = FormEditarMateriais()
    material = Materiais.query.filter_by(id=material_id).first()
    material_nome_original = material.nome

    if form_editar_materiais.validate_on_submit():
        material_nome = form_editar_materiais.nome.data.lower()

        # Validar obra com mesmo nome
        material_existente = Materiais.query.filter_by(nome=material_nome).first()
        if material_nome == material_nome_original:
            pass
        elif material_existente:
            flash("Já existe um material com esse nome", "alert-danger")
            return render_template(
                "materiaiseditar.html",
                form_editar_materiais=form_editar_materiais,
                usuario=usuario,
            )

        # Atualizar os campos da obra com os dados do formulário
        material.nome = material_nome

        db.session.commit()
        flash("Material editado com sucesso!", "alert-success")
        return redirect(url_for("materiais"))

    # Preencher o formulário com os dados existentes da obra
    form_editar_materiais.nome.data = material.nome

    materiais_ordenados = sorted(
        usuario.materiais,
        key=lambda item: (
            re.sub(r"\d+\.?\d*", "", item.nome).strip().lower(),
            extract_numerical_part(item.nome),
        ),
    )

    return render_template(
        "materiaiseditar.html",
        form_editar_materiais=form_editar_materiais,
        usuario=usuario,
        materiais=materiais_ordenados,
    )


@app.route("/cadastro/servicos", methods=["GET", "POST"])
@login_required
def servicos():
    form_servicos = FormServicos()
    usuario = current_user

    if form_servicos.validate_on_submit():
        servico_nome = form_servicos.nome.data
        servico_nome = servico_nome.lower()
        servico = Servicos(nome=servico_nome, usuario=usuario)

        # Verificar limite de serviços
        n_servicos = 0
        for n in usuario.servicos:
            n_servicos += 1

        if usuario.plano == "Básico" and n_servicos >= 10:
            flash("Limite máximo de itens cadastradas já foi atingido", "alert-danger")
            return redirect(url_for("servicos"))

        if usuario.plano == "Avançado" and n_servicos >= 250:
            flash("Limite máximo de itens cadastradas já foi atingido", "alert-danger")
            return redirect(url_for("servicos"))

        # Verificar duplicidade
        servico_existente = Servicos.query.filter_by(nome=servico_nome).first()
        if servico_existente:
            flash("Já existe um servico com esse nome", "alert-danger")
            return render_template(
                "servicos.html", form_servicos=form_servicos, usuario=usuario
            )

        usuario.servicos.append(servico)
        db.session.commit()
        return redirect(url_for("servicos"))

    servico_id = request.form.get("servico_id")
    action = request.form.get("action")
    if action == "excluir":
        servico = Servicos.query.get(servico_id)
        if servico:
            db.session.delete(servico)
            db.session.commit()
            return redirect(url_for("servicos"))

    return render_template(
        "servicos.html", form_servicos=form_servicos, usuario=usuario
    )


@app.route("/cadastro/servicos/editar/ID-<int:servico_id>", methods=["GET", "POST"])
@login_required
def servicoseditar(servico_id):
    usuario = current_user
    form_editar_servicos = FormEditarServicos()
    servico = Servicos.query.filter_by(id=servico_id).first()
    servico_nome_original = servico.nome

    if form_editar_servicos.validate_on_submit():
        servico_nome = form_editar_servicos.nome.data.lower()

        # Validar obra com mesmo nome
        servico_existente = Servicos.query.filter_by(nome=servico_nome).first()
        if servico_nome == servico_nome_original:
            pass
        elif servico_existente:
            flash("Já existe uma servico com esse nome", "alert-danger")
            return render_template(
                "servicoseditar.html",
                form_editar_servicos=form_editar_servicos,
                usuario=usuario,
            )

        # Atualizar os campos da obra com os dados do formulário
        servico.nome = servico_nome

        db.session.commit()
        flash("servico editada com sucesso!", "alert-success")
        return redirect(url_for("servicos"))

    # Preencher o formulário com os dados existentes da obra
    form_editar_servicos.nome.data = servico.nome

    return render_template(
        "servicoseditar.html",
        form_editar_servicos=form_editar_servicos,
        usuario=usuario,
    )


@app.route("/cadastro/fornecedores", methods=["GET", "POST"])
@login_required
def fornecedores():
    form_fornecedores = FormFornecedores()
    usuario = current_user

    if form_fornecedores.validate_on_submit():
        fornecedor_nome = form_fornecedores.nome.data
        fornecedor_nome = fornecedor_nome.lower()
        fornecedor = Fornecedores(nome=fornecedor_nome, usuario=usuario)

        # Verificar duplicidade
        fornecedor_existente = Fornecedores.query.filter_by(
            nome=fornecedor_nome
        ).first()
        if fornecedor_existente:
            flash("Já existe um fornecedor com esse nome", "alert-danger")
            return render_template(
                "fornecedores.html",
                form_fornecedores=form_fornecedores,
                usuario=usuario,
            )

        usuario.fornecedores.append(fornecedor)
        db.session.commit()
        return redirect(url_for("fornecedores"))

    fornecedor_id = request.form.get("fornecedor_id")
    action = request.form.get("action")
    if action == "excluir":
        fornecedor = Fornecedores.query.get(fornecedor_id)
        if fornecedor:
            db.session.delete(fornecedor)
            db.session.commit()
            return redirect(url_for("fornecedores"))

    return render_template(
        "fornecedores.html", form_fornecedores=form_fornecedores, usuario=usuario
    )


@app.route(
    "/cadastro/fornecedores/editar/ID-<int:fornecedor_id>", methods=["GET", "POST"]
)
@login_required
def fornecedoreseditar(fornecedor_id):
    usuario = current_user
    form_editar_fornecedores = FormEditarFornecedores()
    fornecedor = Fornecedores.query.filter_by(id=fornecedor_id).first()
    fornecedor_nome_original = fornecedor.nome

    if form_editar_fornecedores.validate_on_submit():
        fornecedor_nome = form_editar_fornecedores.nome.data.lower()

        # Validar obra com mesmo nome
        fornecedor_existente = Fornecedores.query.filter_by(
            nome=fornecedor_nome
        ).first()
        if fornecedor_nome == fornecedor_nome_original:
            pass
        elif fornecedor_existente:
            flash("Já existe uma fornecedor com esse nome", "alert-danger")
            return render_template(
                "fornecedoreseditar.html",
                form_editar_fornecedores=form_editar_fornecedores,
                usuario=usuario,
            )

        # Atualizar os campos da obra com os dados do formulário
        fornecedor.nome = fornecedor_nome

        db.session.commit()
        flash("fornecedor editada com sucesso!", "alert-success")
        return redirect(url_for("fornecedores"))

    # Preencher o formulário com os dados existentes da obra
    form_editar_fornecedores.nome.data = fornecedor.nome

    return render_template(
        "fornecedoreseditar.html",
        form_editar_fornecedores=form_editar_fornecedores,
        usuario=usuario,
    )


@app.route("/cadastro/diversos", methods=["GET", "POST"])
@login_required
def diversos():
    form_diversos = FormDiversos()
    usuario = current_user

    if form_diversos.validate_on_submit():
        diverso_nome = form_diversos.nome.data
        diverso_nome = diverso_nome.lower()
        diverso = Diversos(nome=diverso_nome, usuario=usuario)

        # Verificar limite de diversos
        n_diversos = 0
        for n in usuario.diversos:
            n_diversos += 1

        if usuario.plano == "Básico" and n_diversos >= 10:
            flash("Limite máximo de itens cadastradas já foi atingido", "alert-danger")
            return redirect(url_for("diversos"))

        if usuario.plano == "Avançado" and n_diversos >= 250:
            flash("Limite máximo de itens cadastradas já foi atingido", "alert-danger")
            return redirect(url_for("diversos"))

        # Verificar duplicidade
        diverso_existente = Diversos.query.filter_by(nome=diverso_nome).first()
        if diverso_existente:
            flash("Já existe um diverso com esse nome", "alert-danger")
            return render_template(
                "diversos.html", form_diversos=form_diversos, usuario=usuario
            )

        usuario.diversos.append(diverso)
        db.session.commit()
        return redirect(url_for("diversos"))

    diverso_id = request.form.get("diverso_id")
    action = request.form.get("action")
    if action == "excluir":
        diverso = Diversos.query.get(diverso_id)
        if diverso:
            db.session.delete(diverso)
            db.session.commit()
            return redirect(url_for("diversos"))

    return render_template(
        "diversos.html", form_diversos=form_diversos, usuario=usuario
    )


@app.route("/cadastro/diversos/editar/ID-<int:diverso_id>", methods=["GET", "POST"])
@login_required
def diversoseditar(diverso_id):
    usuario = current_user
    form_editar_diversos = FormEditarDiversos()
    diverso = Diversos.query.filter_by(id=diverso_id).first()
    diverso_nome_original = diverso.nome

    if form_editar_diversos.validate_on_submit():
        diverso_nome = form_editar_diversos.nome.data.lower()

        # Validar obra com mesmo nome
        diverso_existente = Diversos.query.filter_by(nome=diverso_nome).first()
        if diverso_nome == diverso_nome_original:
            pass
        elif diverso_existente:
            flash("Já existe uma diverso com esse nome", "alert-danger")
            return render_template(
                "diversoseditar.html",
                form_editar_diversos=form_editar_diversos,
                usuario=usuario,
            )

        diverso.nome = diverso_nome

        db.session.commit()
        flash("diverso editada com sucesso!", "alert-success")
        return redirect(url_for("diversos"))

    form_editar_diversos.nome.data = diverso.nome

    return render_template(
        "diversoseditar.html",
        form_editar_diversos=form_editar_diversos,
        usuario=usuario,
    )


@app.route("/obter_subetapas_por_etapa")
def obter_subetapas_por_etapa():
    etapa_id = request.args.get("etapa_id")
    subetapas = Subetapa.query.filter_by(etapa_id=etapa_id).all()
    subetapas_data = [
        {"id": subetapa.id, "nome": subetapa.nome} for subetapa in subetapas
    ]
    return jsonify(subetapas_data)


@app.route("/lancamento/materiais", methods=["GET", "POST"])
@login_required
def lancamentomateriais():
    form_nf = FormNotaFiscal()

    form_nf.fornecedor_id.choices = [(f.id, f.nome) for f in Fornecedores.query.all()]
    form_nf.etapa_id.choices = [(e.id, e.nome) for e in Etapa.query.all()]
    form_nf.subetapa_id.choices = [(s.id, s.nome) for s in Subetapa.query.all()]
    form_nf.material_id.choices = [(m.id, m.nome) for m in Materiais.query.all()]

    usuario = current_user
    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()

    if not obra_selecionada:
        flash(
            "Nenhuma obra foi selecionada. Selecione uma obra para continuar.",
            "alert-warning",
        )
        return redirect(url_for("obras"))

    fornecedores = Fornecedores.query.all()
    form_nf.fornecedor_id.choices = [(f.id, f.nome) for f in fornecedores]

    if "adicionar_item" in request.form:
        if form_nf.validate_on_submit():
            pass
        else:
            flash("Preencha todos os campos obrigatórios corretamente!", "alert-danger")
            return render_template(
                "lancamentocusto.html",
                form_nf=form_nf,
                usuario=usuario,
                obra_selecionada=obra_selecionada,
                errors=form_nf.errors,
            )

    return render_template(
        "lancamentocusto.html",
        form_nf=form_nf,
        usuario=usuario,
        obra_selecionada=obra_selecionada,
    )


@app.route(
    "/cadastro/lancamento-materiais/editar/ID-<int:lancamentomateriais_id>",
    methods=["GET", "POST"],
)
@login_required
def lancamentomateriaiseditar(lancamentomateriais_id):
    form_editar_lancamento_custo = FormEditarLancamentoCusto()
    usuario = current_user
    lancamento = LancamentoCusto.query.filter_by(id=lancamentomateriais_id).first()
    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()

    # Preencher campos choices do formulario
    sorted_fornecedores = sorted(
        usuario.fornecedores, key=lambda fornecedor: fornecedor.nome
    )
    form_editar_lancamento_custo.fornecedor_id.choices = [
        (fornecedor.id, fornecedor.nome.title()) for fornecedor in sorted_fornecedores
    ]

    sorted_etapas = sorted(usuario.etapas, key=lambda etapa: etapa.nome)
    form_editar_lancamento_custo.etapa_id.choices = [
        (etapa.id, etapa.nome.title()) for etapa in sorted_etapas
    ]

    subs = Subetapa.query.filter_by(etapa_id=lancamento.etapa_id)
    sorted_subetapas = sorted(subs, key=lambda subetapa: subetapa.nome)
    form_editar_lancamento_custo.subetapa_id.choices = [
        (subetapa.id, subetapa.nome.title()) for subetapa in sorted_subetapas
    ]

    sorted_materiais = sorted(
        usuario.materiais,
        key=lambda item: (
            re.sub(r"\d+\.?\d*", "", item.nome).strip().lower(),
            extract_numerical_part(item.nome),
        ),
    )
    form_editar_lancamento_custo.material_id.choices = [
        (material.id, material.nome.capitalize()) for material in sorted_materiais
    ]

    if "adicionar_item" in request.form:
        if (
            form_editar_lancamento_custo.validate_on_submit()
            and request.method == "POST"
        ):

            data_lancamento = datetime.strptime(
                form_editar_lancamento_custo.data_lancamento.data, "%d/%m/%Y"
            )
            lancamento.data_lancamento = data_lancamento
            lancamento.fornecedor_id = form_editar_lancamento_custo.fornecedor_id.data
            lancamento.nota_fiscal = form_editar_lancamento_custo.nota_fiscal.data
            lancamento.etapa_id = form_editar_lancamento_custo.etapa_id.data
            lancamento.subetapa_id = form_editar_lancamento_custo.subetapa_id.data
            lancamento.material_id = form_editar_lancamento_custo.material_id.data
            lancamento.quantidade = form_editar_lancamento_custo.quantidade.data
            lancamento.preco_unit = form_editar_lancamento_custo.preco_unitario.data

            db.session.commit()
            flash("Lançamento editado com sucesso!", "alert-success")
            return redirect(url_for("lancamentomateriais"))

    # Preencher o formulário com os dados existentes da obra
    form_editar_lancamento_custo.data_lancamento.data = (
        lancamento.data_lancamento.strftime("%d/%m/%Y")
    )
    form_editar_lancamento_custo.fornecedor_id.data = lancamento.fornecedor_id
    form_editar_lancamento_custo.nota_fiscal.data = lancamento.nota_fiscal
    form_editar_lancamento_custo.etapa_id.data = lancamento.etapa_id
    form_editar_lancamento_custo.subetapa_id.data = lancamento.subetapa_id
    form_editar_lancamento_custo.material_id.data = lancamento.material_id
    form_editar_lancamento_custo.quantidade.data = lancamento.quantidade
    form_editar_lancamento_custo.preco_unitario.data = lancamento.preco_unit

    return render_template(
        "lancamentocustoeditar.html",
        form_editar_lancamento_custo=form_editar_lancamento_custo,
        usuario=usuario,
        obra_selecionada=obra_selecionada,
    )


@app.route("/lancamento/servicos", methods=["GET", "POST"])
@login_required
def lancamentoservicos():
    form_lancamento_servico = FormLancamentoServico()
    usuario = current_user
    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()

    # Preencher campos choices do formulario
    sorted_fornecedores = sorted(
        usuario.fornecedores, key=lambda fornecedor: fornecedor.nome
    )
    form_lancamento_servico.fornecedor_id.choices = [
        (fornecedor.id, fornecedor.nome.title()) for fornecedor in sorted_fornecedores
    ]

    sorted_etapas = sorted(usuario.etapas, key=lambda etapa: etapa.nome)
    form_lancamento_servico.etapa_id.choices = (
        (99999, "Selecione uma etapa..."),
    ) + tuple((etapa.id, etapa.nome.capitalize()) for etapa in sorted_etapas)

    sorted_subetapas = sorted(usuario.subetapas, key=lambda subetapa: subetapa.nome)
    form_lancamento_servico.subetapa_id.choices = (
        (99999, "Selecione uma subetapa..."),
    ) + tuple(
        (subetapa.id, subetapa.nome.capitalize()) for subetapa in sorted_subetapas
    )

    sorted_servicos = sorted(
        usuario.servicos,
        key=lambda item: (
            re.sub(r"\d+\.?\d*", "", item.nome).strip().lower(),
            extract_numerical_part(item.nome),
        ),
    )
    form_lancamento_servico.servico_id.choices = [
        (servico.id, servico.nome.capitalize()) for servico in sorted_servicos
    ]

    if "adicionar_item" in request.form:
        if form_lancamento_servico.validate_on_submit() and request.method == "POST":

            # Verificar o limite de lançamentos
            n_mat = 0
            n_ser = 0
            n_div = 0
            for n in usuario.obras:
                for m in n.lancamentos_custo:
                    n_mat += 1
                for s in n.lancamentos_servico:
                    n_ser += 1
                for d in n.lancamentos_diverso:
                    n_div += 1
            n_lanc = n_mat + n_ser + n_div

            if usuario.plano == "Básico" and n_lanc >= 10:
                flash(
                    "Limite máximo de lançamentos cadastradas já foi atingido",
                    "alert-danger",
                )
                return redirect(url_for("lancamentoservicos"))

            if usuario.plano == "Avançado" and n_lanc >= 2000:
                flash(
                    "Limite máximo de itens lançamentos já foi atingido", "alert-danger"
                )
                return redirect(url_for("lancamentoservicos"))

            data_lancamento_id = form_lancamento_servico.data_lancamento.data
            fornecedor_lancamento_id = form_lancamento_servico.fornecedor_id.data
            nota_fiscal_lancamento = form_lancamento_servico.nota_fiscal.data
            etapa_lancamento_id = form_lancamento_servico.etapa_id.data
            subetapa_lancamento_id = form_lancamento_servico.subetapa_id.data
            servico_lancamento_id = form_lancamento_servico.servico_id.data
            quantidade_lancamento = form_lancamento_servico.quantidade.data
            preco_unitario_lancamento = form_lancamento_servico.preco_unitario.data

            data_lancamento = datetime.strptime(data_lancamento_id, "%d/%m/%Y")

            lancamento = LancamentoServico(
                data_lancamento=data_lancamento,
                nota_fiscal=nota_fiscal_lancamento,
                quantidade=quantidade_lancamento,
                preco_unit=preco_unitario_lancamento,
                servico_id=servico_lancamento_id,
                fornecedor_id=fornecedor_lancamento_id,
                etapa_id=etapa_lancamento_id,
                subetapa_id=subetapa_lancamento_id,
                obra_id=obra_selecionada.id,
            )

            obra_selecionada.lancamentos_servico.append(lancamento)
            db.session.commit()

            # Zerar campos
            form_lancamento_servico.servico_id.data = ""
            form_lancamento_servico.quantidade.data = ""
            form_lancamento_servico.preco_unitario.data = ""

    lancamento_id = request.form.get("lancamento_id")
    action = request.form.get("action")
    if action == "excluir":
        lancamento = LancamentoServico.query.get(lancamento_id)
        if lancamento:
            db.session.delete(lancamento)
            db.session.commit()
            return redirect(url_for("lancamentoservicos"))

    return render_template(
        "lancamentoservico.html",
        form_lancamento_servico=form_lancamento_servico,
        usuario=usuario,
        obra_selecionada=obra_selecionada,
    )


@app.route(
    "/cadastro/lancamento-servicos/editar/ID-<int:lancamentoservicos_id>",
    methods=["GET", "POST"],
)
@login_required
def lancamentoservicoseditar(lancamentoservicos_id):
    form_editar_lancamento_servico = FormEditarLancamentoServico()
    usuario = current_user
    lancamento = LancamentoServico.query.filter_by(id=lancamentoservicos_id).first()
    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()

    # Preencher campos choices do formulario
    sorted_fornecedores = sorted(
        usuario.fornecedores, key=lambda fornecedor: fornecedor.nome
    )
    form_editar_lancamento_servico.fornecedor_id.choices = [
        (fornecedor.id, fornecedor.nome.title()) for fornecedor in sorted_fornecedores
    ]

    sorted_etapas = sorted(usuario.etapas, key=lambda etapa: etapa.nome)
    form_editar_lancamento_servico.etapa_id.choices = [
        (etapa.id, etapa.nome.title()) for etapa in sorted_etapas
    ]

    subs = Subetapa.query.filter_by(etapa_id=lancamento.etapa_id)
    sorted_subetapas = sorted(subs, key=lambda subetapa: subetapa.nome)
    form_editar_lancamento_servico.subetapa_id.choices = [
        (subetapa.id, subetapa.nome.title()) for subetapa in sorted_subetapas
    ]

    sorted_servicos = sorted(
        usuario.servicos,
        key=lambda item: (
            re.sub(r"\d+\.?\d*", "", item.nome).strip().lower(),
            extract_numerical_part(item.nome),
        ),
    )
    form_editar_lancamento_servico.servico_id.choices = [
        (servico.id, servico.nome.capitalize()) for servico in sorted_servicos
    ]

    if "adicionar_item" in request.form:
        if (
            form_editar_lancamento_servico.validate_on_submit()
            and request.method == "POST"
        ):

            data_lancamento = datetime.strptime(
                form_editar_lancamento_servico.data_lancamento.data, "%d/%m/%Y"
            )
            lancamento.data_lancamento = data_lancamento
            lancamento.fornecedor_id = form_editar_lancamento_servico.fornecedor_id.data
            lancamento.nota_fiscal = form_editar_lancamento_servico.nota_fiscal.data
            lancamento.etapa_id = form_editar_lancamento_servico.etapa_id.data
            lancamento.subetapa_id = form_editar_lancamento_servico.subetapa_id.data
            lancamento.servico_id = form_editar_lancamento_servico.servico_id.data
            lancamento.quantidade = form_editar_lancamento_servico.quantidade.data
            lancamento.preco_unit = form_editar_lancamento_servico.preco_unitario.data

            db.session.commit()
            flash("Lançamento editado com sucesso!", "alert-success")
            return redirect(url_for("lancamentoservicos"))

    # Preencher o formulário com os dados existentes da obra
    form_editar_lancamento_servico.data_lancamento.data = (
        lancamento.data_lancamento.strftime("%d/%m/%Y")
    )
    form_editar_lancamento_servico.fornecedor_id.data = lancamento.fornecedor_id
    form_editar_lancamento_servico.nota_fiscal.data = lancamento.nota_fiscal
    form_editar_lancamento_servico.etapa_id.data = lancamento.etapa_id
    form_editar_lancamento_servico.subetapa_id.data = lancamento.subetapa_id
    form_editar_lancamento_servico.servico_id.data = lancamento.servico_id
    form_editar_lancamento_servico.quantidade.data = lancamento.quantidade
    form_editar_lancamento_servico.preco_unitario.data = lancamento.preco_unit

    return render_template(
        "lancamentoservicoeditar.html",
        form_editar_lancamento_servico=form_editar_lancamento_servico,
        usuario=usuario,
        obra_selecionada=obra_selecionada,
    )


@app.route("/lancamento/diversos", methods=["GET", "POST"])
@login_required
def lancamentodiversos():
    form_lancamento_diverso = FormLancamentoDiverso()
    usuario = current_user
    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()

    # Preencher campos choices do formulario
    sorted_diversos = sorted(
        usuario.diversos,
        key=lambda item: (
            re.sub(r"\d+\.?\d*", "", item.nome).strip().lower(),
            extract_numerical_part(item.nome),
        ),
    )
    form_lancamento_diverso.diverso_id.choices = [
        (diverso.id, diverso.nome.capitalize()) for diverso in sorted_diversos
    ]

    if "adicionar_item" in request.form:
        if form_lancamento_diverso.validate_on_submit() and request.method == "POST":

            # Verificar o limite de lançamentos
            n_mat = 0
            n_ser = 0
            n_div = 0
            for n in usuario.obras:
                for m in n.lancamentos_custo:
                    n_mat += 1
                for s in n.lancamentos_servico:
                    n_ser += 1
                for d in n.lancamentos_diverso:
                    n_div += 1
            n_lanc = n_mat + n_ser + n_div

            if usuario.plano == "Básico" and n_lanc >= 10:
                flash(
                    "Limite máximo de lançamentos cadastradas já foi atingido",
                    "alert-danger",
                )
                return redirect(url_for("lancamentodiversos"))

            if usuario.plano == "Avançado" and n_lanc >= 2000:
                flash(
                    "Limite máximo de itens lançamentos já foi atingido", "alert-danger"
                )
                return redirect(url_for("lancamentodiversos"))

            data_lancamento_id = form_lancamento_diverso.data_lancamento.data
            diverso_lancamento_id = form_lancamento_diverso.diverso_id.data
            quantidade_lancamento = form_lancamento_diverso.quantidade.data
            preco_unitario_lancamento = form_lancamento_diverso.preco_unitario.data

            data_lancamento = datetime.strptime(data_lancamento_id, "%d/%m/%Y")

            lancamento = LancamentoDiverso(
                data_lancamento=data_lancamento,
                quantidade=quantidade_lancamento,
                preco_unit=preco_unitario_lancamento,
                diverso_id=diverso_lancamento_id,
                obra_id=obra_selecionada.id,
            )

            obra_selecionada.lancamentos_diverso.append(lancamento)
            db.session.commit()

            # Zerar campos
            form_lancamento_diverso.diverso_id.data = ""
            form_lancamento_diverso.quantidade.data = ""
            form_lancamento_diverso.preco_unitario.data = ""

    lancamento_id = request.form.get("lancamento_id")
    action = request.form.get("action")
    if action == "excluir":
        lancamento = LancamentoDiverso.query.get(lancamento_id)
        if lancamento:
            db.session.delete(lancamento)
            db.session.commit()
            return redirect(url_for("lancamentodiversos"))

    return render_template(
        "lancamentodiverso.html",
        form_lancamento_diverso=form_lancamento_diverso,
        usuario=usuario,
        obra_selecionada=obra_selecionada,
    )


@app.route(
    "/cadastro/lancamento-diversos/editar/ID-<int:lancamentodiversos_id>",
    methods=["GET", "POST"],
)
@login_required
def lancamentodiversoseditar(lancamentodiversos_id):
    form_editar_lancamento_diverso = FormEditarLancamentoDiverso()
    usuario = current_user
    lancamento = LancamentoDiverso.query.filter_by(id=lancamentodiversos_id).first()
    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()

    # Preencher campos choices do formulario
    sorted_diversos = sorted(
        usuario.diversos,
        key=lambda item: (
            re.sub(r"\d+\.?\d*", "", item.nome).strip().lower(),
            extract_numerical_part(item.nome),
        ),
    )
    form_editar_lancamento_diverso.diverso_id.choices = [
        (diverso.id, diverso.nome.capitalize()) for diverso in sorted_diversos
    ]

    if "adicionar_item" in request.form:
        if (
            form_editar_lancamento_diverso.validate_on_submit()
            and request.method == "POST"
        ):

            data_lancamento = datetime.strptime(
                form_editar_lancamento_diverso.data_lancamento.data, "%d/%m/%Y"
            )
            lancamento.data_lancamento = data_lancamento
            lancamento.diverso_id = form_editar_lancamento_diverso.diverso_id.data
            lancamento.quantidade = form_editar_lancamento_diverso.quantidade.data
            lancamento.preco_unit = form_editar_lancamento_diverso.preco_unitario.data

            db.session.commit()
            flash("Lançamento editado com sucesso!", "alert-success")
            return redirect(url_for("lancamentodiversos"))

    # Preencher o formulário com os dados existentes da obra
    form_editar_lancamento_diverso.data_lancamento.data = (
        lancamento.data_lancamento.strftime("%d/%m/%Y")
    )
    form_editar_lancamento_diverso.diverso_id.data = lancamento.diverso_id
    form_editar_lancamento_diverso.quantidade.data = lancamento.quantidade
    form_editar_lancamento_diverso.preco_unitario.data = lancamento.preco_unit

    return render_template(
        "lancamentodiversoeditar.html",
        form_editar_lancamento_diverso=form_editar_lancamento_diverso,
        usuario=usuario,
        obra_selecionada=obra_selecionada,
    )


@app.route("/relatorios/custo-por-etapa", methods=["GET", "POST"])
@login_required
def custoporetapa():
    usuario = current_user
    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()

    if not obra_selecionada:
        flash(
            "Nenhuma obra foi selecionada. Selecione uma obra para visualizar o relatório.",
            "alert-warning",
        )
        return redirect(url_for("obras"))

    etapas = Etapa.query.filter_by(usuario_id=usuario.id).all()
    custo_etapa = {}
    custo_total = 0

    for etapa in etapas:
        custo_etapa[etapa.nome] = 0

        lancamento_materiais = LancamentoCusto.query.filter_by(
            etapa_id=etapa.id, obra_id=obra_selecionada.id
        ).all()
        for lancamento in lancamento_materiais:
            lancamento_custo = lancamento.quantidade * lancamento.preco_unit
            custo_etapa[etapa.nome] += lancamento_custo
            custo_total += lancamento_custo

        lancamento_servicos = LancamentoServico.query.filter_by(
            etapa_id=etapa.id, obra_id=obra_selecionada.id
        ).all()
        for lancamento in lancamento_servicos:
            lancamento_custo = lancamento.quantidade * lancamento.preco_unit
            custo_etapa[etapa.nome] += lancamento_custo
            custo_total += lancamento_custo

    custo_etapa_ordenado = dict(
        sorted(custo_etapa.items(), key=lambda item: item[1], reverse=True)
    )

    return render_template(
        "custoporetapa.html",
        custo_etapa=custo_etapa_ordenado,
        custo_total=custo_total,
    )


@app.route("/relatorios/custo-por-subetapa", methods=["GET", "POST"])
@login_required
def custoporsubetapa():
    usuario = current_user
    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()

    if not obra_selecionada:
        flash(
            "Nenhuma obra foi selecionada. Selecione uma obra para visualizar o relatório.",
            "alert-warning",
        )
        return redirect(url_for("obras"))

    subetapas = Subetapa.query.filter_by(usuario_id=usuario.id).all()
    custo_subetapa = {}
    custo_total = 0

    for subetapa in subetapas:
        custo_subetapa[subetapa.nome] = 0

        lancamento_materiais = LancamentoCusto.query.filter_by(
            subetapa_id=subetapa.id, obra_id=obra_selecionada.id
        ).all()
        for lancamento in lancamento_materiais:
            lancamento_custo = lancamento.quantidade * lancamento.preco_unit
            custo_subetapa[subetapa.nome] += lancamento_custo
            custo_total += lancamento_custo

        lancamento_servicos = LancamentoServico.query.filter_by(
            subetapa_id=subetapa.id, obra_id=obra_selecionada.id
        ).all()
        for lancamento in lancamento_servicos:
            lancamento_custo = lancamento.quantidade * lancamento.preco_unit
            custo_subetapa[subetapa.nome] += lancamento_custo
            custo_total += lancamento_custo

    custo_subetapa_ordenado = dict(
        sorted(custo_subetapa.items(), key=lambda item: item[1], reverse=True)
    )

    return render_template(
        "custoporsubetapa.html",
        custo_subetapa=custo_subetapa_ordenado,
        custo_total=custo_total,
    )


@app.route("/relatorios/quantitativo-de-materiais", methods=["GET", "POST"])
@login_required
def quantitativo():
    usuario = current_user
    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()

    if not obra_selecionada:
        flash(
            "Nenhuma obra foi selecionada. Selecione uma obra para visualizar o relatório.",
            "alert-warning",
        )
        return redirect(url_for("obras"))

    materiais = Materiais.query.filter_by(usuario_id=usuario.id).all()
    servicos = Servicos.query.filter_by(usuario_id=usuario.id).all()
    qtd_material = {}

    for material in materiais:
        qtd_material[material.nome] = 0

        lancamento_materiais = LancamentoCusto.query.filter_by(
            material_id=material.id, obra_id=obra_selecionada.id
        ).all()
        for lancamento in lancamento_materiais:
            qtd_material[material.nome] += lancamento.quantidade

    qtd_material_ordenado = dict(
        sorted(qtd_material.items(), key=lambda item: item[1], reverse=True)
    )

    return render_template(
        "quantitativo.html", qtd_material=qtd_material_ordenado, usuario=usuario
    )


@app.route("/relatorios/fluxo-caixa-mensal", methods=["GET", "POST"])
@login_required
def fluxocaixamensal():
    usuario = current_user
    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()
    custos_ordenados = ()

    if obra_selecionada:
        lancamento_materiais = LancamentoCusto.query.filter_by(
            obra_id=obra_selecionada.id
        ).all()
        lancamento_servicos = LancamentoServico.query.filter_by(
            obra_id=obra_selecionada.id
        ).all()
        lancamento_diversos = LancamentoDiverso.query.filter_by(
            obra_id=obra_selecionada.id
        ).all()

        custos_mensais = {}

        for lancamento in lancamento_materiais:
            data_lancamento = lancamento.data_lancamento
            mes_lancamento = data_lancamento.strftime("%m-%Y")
            custo_total = lancamento.quantidade * lancamento.preco_unit
            custos_mensais.setdefault(mes_lancamento, 0)
            custos_mensais[mes_lancamento] += custo_total

        for lancamento in lancamento_servicos:
            data_lancamento = lancamento.data_lancamento
            mes_lancamento = data_lancamento.strftime("%m-%Y")
            custo_total = lancamento.quantidade * lancamento.preco_unit
            custos_mensais.setdefault(mes_lancamento, 0)
            custos_mensais[mes_lancamento] += custo_total

        for lancamento in lancamento_diversos:
            data_lancamento = lancamento.data_lancamento
            mes_lancamento = data_lancamento.strftime("%m-%Y")
            custo_total = lancamento.quantidade * lancamento.preco_unit
            custos_mensais.setdefault(mes_lancamento, 0)
            custos_mensais[mes_lancamento] += custo_total

        # Ordena as chaves (meses) do dicionário em ordem cronológica crescente
        meses_ordenados = sorted(
            custos_mensais.keys(), key=lambda x: datetime.strptime(x, "%m-%Y")
        )

        # Cria uma lista de tuplas (mês, custo_total) ordenada cronologicamente
        custos_ordenados = [(mes, custos_mensais[mes]) for mes in meses_ordenados]

    return render_template(
        "fluxocaixamensal.html", custos_mensais=custos_ordenados, usuario=usuario
    )


@app.route("/relatorios/resumo-custos", methods=["GET", "POST"])
@login_required
def resumodecustos():
    usuario = current_user
    obra_selecionada = Obra.query.filter_by(id=usuario.obra_selecionada).first()
    custo_materiais = 0
    custo_servicos = 0
    custo_diversos = 0
    custo_total = 0
    custo_metro = 0

    if obra_selecionada:
        lancamento_materiais = LancamentoCusto.query.filter_by(
            obra_id=obra_selecionada.id
        ).all()
        lancamento_servicos = LancamentoServico.query.filter_by(
            obra_id=obra_selecionada.id
        ).all()
        lancamento_diversos = LancamentoDiverso.query.filter_by(
            obra_id=obra_selecionada.id
        ).all()

        for lancamento in lancamento_materiais:
            custo = lancamento.quantidade * lancamento.preco_unit
            custo_materiais += custo

        for lancamento in lancamento_servicos:
            custo = lancamento.quantidade * lancamento.preco_unit
            custo_servicos += custo

        for lancamento in lancamento_diversos:
            custo = lancamento.quantidade * lancamento.preco_unit
            custo_diversos += custo

        custo_total = custo_materiais + custo_servicos + custo_diversos

        custo_metro = custo_total / obra_selecionada.area

    return render_template(
        "resumodecustos.html",
        custo_materiais=custo_materiais,
        custo_servicos=custo_servicos,
        custo_diversos=custo_diversos,
        custo_total=custo_total,
        custo_metro=custo_metro,
    )
