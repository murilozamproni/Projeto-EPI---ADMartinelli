import flet as ft
import sqlite3
from datetime import datetime
import smtplib
from email.message import EmailMessage

PRIMARY_COLOR = "#0A3B7C"
SECONDARY_COLOR = "#1D5BB6"
BG_COLOR = "#EAECEE"
TEXT_COLOR = "#333333"
SIDEBAR_BG = "#343A40"
CARD_BG = "#F8F9FA"
INPUT_BG = "#D1D5DB"

EMAIL_ENDERECO = 'SEU EMAIL'
EMAIL_SENHA = 'SENHA'

def criar_banco():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(epis)")
    colunas_epis = [col[1] for col in cursor.fetchall()]
    if colunas_epis and 'validade' not in colunas_epis:
        cursor.execute("DROP TABLE IF EXISTS epis")
        cursor.execute("DROP TABLE IF EXISTS entregas")
        
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, login TEXT UNIQUE, senha TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS epis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, validade TEXT, tipo TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entregas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario TEXT, epi TEXT, data TEXT, status TEXT
        )
    """)
    try:
        cursor.execute("INSERT INTO usuarios (nome, login, senha) VALUES (?, ?, ?)", ("Administrador", "admin", "admin"))
        conn.commit()
    except:
        pass
    conn.close()

def main(page: ft.Page):
    criar_banco()
    page.title = "SEGURA EPI - Equipamentos de Proteção Individual"
    page.window_width = 1920
    page.window_height = 1080
    page.window_maximized = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#9BA4B5"

    def get_funcionarios():
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nome, login FROM usuarios")
        dados = cursor.fetchall()
        conn.close()
        return dados

    def get_epis():
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nome, validade, tipo FROM epis")
        dados = cursor.fetchall()
        conn.close()
        return dados

    def get_entregas():
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("SELECT funcionario, epi, data, status FROM entregas")
        dados = cursor.fetchall()
        conn.close()
        return dados

    msg_erro_login = ft.Text("Erro: E-mail ou Senha incorretos!", color=ft.Colors.RED_700, size=14, weight="bold", visible=False)

    def validar_login(e):
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE login = ? AND senha = ?", (user_input.value, pass_input.value))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            msg_erro_login.visible = False
            exibir_dashboard(usuario[1])
        else:
            msg_erro_login.visible = True
            page.update()

    def realizar_logout(e):
        user_input.value = ""
        pass_input.value = ""
        msg_erro_login.visible = False
        page.clean()
        page.bgcolor = "#9BA4B5"
        page.add(tela_login)
        page.update()

    user_input = ft.TextField(
        hint_text="seu.email@empresa.com", 
        width=350, 
        height=45,
        prefix_icon=ft.Icons.EMAIL_OUTLINED, 
        border_radius=5, 
        bgcolor=INPUT_BG,
        border=ft.InputBorder.NONE,
        color=ft.Colors.BLACK87,
        hint_style=ft.TextStyle(color=ft.Colors.BLACK54)
    )
    
    pass_input = ft.TextField(
        hint_text="••••••••", 
        width=350, 
        height=45,
        password=True, 
        can_reveal_password=True, 
        prefix_icon=ft.Icons.LOCK_OUTLINE, 
        border_radius=5, 
        bgcolor=INPUT_BG,
        border=ft.InputBorder.NONE,
        color=ft.Colors.BLACK87,
        hint_style=ft.TextStyle(color=ft.Colors.BLACK54),
        on_submit=validar_login
    )

    botao_login = ft.Container(
        content=ft.ElevatedButton(
            "Confirmar Acesso",
            on_click=validar_login,
            bgcolor=SECONDARY_COLOR,
            color=ft.Colors.WHITE,
            width=350,
            height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))
        ),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=SECONDARY_COLOR),
        border_radius=6
    )

    tela_login = ft.Stack(
        expand=True,
        controls=[
            ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=430,
                                padding=40,
                                border_radius=15,
                                border=ft.border.all(3, ft.Colors.WHITE),
                                bgcolor=ft.Colors.WHITE,
                                shadow=ft.BoxShadow(spread_radius=2, blur_radius=25, color=ft.Colors.BLACK38),
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=15,
                                    controls=[
                                        ft.Image(src="logo_principal.jpeg", width=110, height=110, fit="contain"),
                                        ft.Text("SEGURA EPI", size=24, weight="bold", color=PRIMARY_COLOR),
                                        ft.Text("EQUIPAMENTOS DE PROTEÇÃO INDIVIDUAL", size=9, weight="bold", color=ft.Colors.GREY_500),
                                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                                        ft.Column(
                                            spacing=5,
                                            controls=[
                                                ft.Text("E-mail", size=14, color=ft.Colors.BLACK87),
                                                user_input
                                            ]
                                        ),
                                        ft.Column(
                                            spacing=5,
                                            controls=[
                                                ft.Text("Senha", size=14, color=ft.Colors.BLACK87),
                                                pass_input
                                            ]
                                        ),
                                        msg_erro_login,
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            width=350,
                                            controls=[
                                                ft.Checkbox(label="Lembrar de mim", label_style=ft.TextStyle(color=ft.Colors.BLACK87, size=13)),
                                                ft.TextButton("Esqueci minha senha?", style=ft.ButtonStyle(color=SECONDARY_COLOR, padding=0))
                                            ]
                                        ),
                                        botao_login
                                    ]
                                )
                            )
                        ]
                    )
                ]
            )
        ]
    )

    def exibir_dashboard(nome_usuario):
        page.clean()
        page.bgcolor = BG_COLOR

        tabela_entregas = ft.DataTable(columns=[ft.DataColumn(ft.Text("Funcionário")), ft.DataColumn(ft.Text("EPI Recebido")), ft.DataColumn(ft.Text("Data")), ft.DataColumn(ft.Text("Status"))])
        tabela_epis = ft.DataTable(columns=[ft.DataColumn(ft.Text("Nome do EPI")), ft.DataColumn(ft.Text("Validade")), ft.DataColumn(ft.Text("Tipo"))])
        tabela_funcionarios = ft.DataTable(columns=[ft.DataColumn(ft.Text("Nome Completo")), ft.DataColumn(ft.Text("Login"))])

        drop_funcionario = ft.Dropdown(label="Selecione o Funcionário", width=400, border_radius=8, bgcolor=CARD_BG)
        drop_epi = ft.Dropdown(label="Selecione o Equipamento", width=400, border_radius=8, bgcolor=CARD_BG)

        novo_epi_nome = ft.TextField(label="Nome do Equipamento:", hint_text="Ex: Capacete, Luva de Raspa...", width=400, border_radius=8, bgcolor=CARD_BG)
        novo_epi_validade = ft.TextField(label="Prazo de Validade (em dias):", hint_text="Insira o número de dias", width=400, border_radius=8, bgcolor=CARD_BG, prefix_icon=ft.Icons.CALENDAR_TODAY)
        novo_epi_tipo = ft.Dropdown(label="Tipo de EPI:", hint_text="Selecione o Tipo", width=400, border_radius=8, bgcolor=CARD_BG)
        novo_epi_tipo.options = [ft.dropdown.Option("Proteção da Cabeça"), ft.dropdown.Option("Proteção Auditiva"), ft.dropdown.Option("Proteção das Mãos"), ft.dropdown.Option("Proteção Respiratória")]

        novo_nome = ft.TextField(label="Nome Completo", width=400, border_radius=8, bgcolor=CARD_BG)
        novo_login = ft.TextField(label="E-mail Corporativo / Login", width=400, border_radius=8, bgcolor=CARD_BG)
        nova_senha = ft.TextField(label="Senha de Acesso", width=400, password=True, border_radius=8, bgcolor=CARD_BG)

        def atualizar_dados():
            tabela_funcionarios.rows.clear()
            for f in get_funcionarios():
                tabela_funcionarios.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(f[0])), ft.DataCell(ft.Text(f[1]))]))
            
            tabela_epis.rows.clear()
            drop_epi.options.clear()
            for e in get_epis():
                tabela_epis.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(e[0])), ft.DataCell(ft.Text(e[1])), ft.DataCell(ft.Text(e[2]))]))
                drop_epi.options.append(ft.dropdown.Option(e[0]))

            drop_funcionario.options.clear()
            for f in get_funcionarios():
                drop_funcionario.options.append(ft.dropdown.Option(f[0]))

            tabela_entregas.rows.clear()
            for ent in get_entregas():
                cor_status = ft.Colors.GREEN if ent[3] == "Assinado" else ft.Colors.ORANGE
                tabela_entregas.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(ent[0])), ft.DataCell(ft.Text(ent[1])), ft.DataCell(ft.Text(ent[2])), ft.DataCell(ft.Text(ent[3], color=cor_status, weight="bold"))]))
            page.update()

        def enviar_link_facial(e):
            if drop_funcionario.value and drop_epi.value:
                conn = sqlite3.connect("usuarios.db")
                cursor = conn.cursor()
                cursor.execute("SELECT login FROM usuarios WHERE nome = ?", (drop_funcionario.value,))
                resultado = cursor.fetchone()
                
                email_destino = resultado[0] if resultado else 'email_destino'

                try:
                    msg = EmailMessage()
                    msg['Subject'] = 'SEGURA EPI - Assinatura Digital Necessária'
                    msg['From'] = EMAIL_ENDERECO
                    msg['To'] = email_destino

                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                        <body style="font-family: Arial, sans-serif; color: #333;">
                            <h2 style="color: #0A3B7C;">SEGURA EPI - Confirmação de Recebimento</h2>
                            <p>Olá, {drop_funcionario.value},</p>
                            <p>Um novo Equipamento de Proteção Individual (<strong>{drop_epi.value}</strong>) foi registrado para você.</p>
                            <p>Para confirmar o recebimento e assinar eletronicamente, por favor, realize o reconhecimento facial clicando no botão abaixo através do seu smartphone:</p>
                            <hr>
                            <a href="https://seusite.com/reconhecimento" style="background-color: #1D5BB6; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; margin-top: 10px;">Iniciar Reconhecimento Facial</a>
                            <br><br>
                            <p>Atenciosamente,<br>Segurança do Trabalho</p>
                        </body>
                    </html>
                    """

                    msg.set_content('Acesse o link para realizar o reconhecimento facial: https://seusite.com/reconhecimento')
                    msg.add_alternative(html_content, subtype='html')

                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(EMAIL_ENDERECO, EMAIL_SENHA)
                        smtp.send_message(msg)

                    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
                    cursor.execute("INSERT INTO entregas (funcionario, epi, data, status) VALUES (?, ?, ?, ?)", (drop_funcionario.value, drop_epi.value, data_atual, "Pendente (E-mail Enviado)"))
                    conn.commit()
                    
                    page.snack_bar = ft.SnackBar(ft.Text(f"E-mail enviado para {email_destino} com sucesso!"), bgcolor=ft.Colors.GREEN_700)

                except Exception as ex:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao enviar e-mail: {str(ex)}"), bgcolor=ft.Colors.RED_700)
                
                finally:
                    conn.close()
                    page.snack_bar.open = True
                    atualizar_dados()

        def salvar_epi(e):
            if novo_epi_nome.value and novo_epi_validade.value and novo_epi_tipo.value:
                conn = sqlite3.connect("usuarios.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO epis (nome, validade, tipo) VALUES (?, ?, ?)", (novo_epi_nome.value, novo_epi_validade.value, novo_epi_tipo.value))
                conn.commit()
                conn.close()
                novo_epi_nome.value = novo_epi_validade.value = novo_epi_tipo.value = ""
                page.snack_bar = ft.SnackBar(ft.Text("Equipamento cadastrado com sucesso!"), bgcolor=ft.Colors.GREEN_700)
                page.snack_bar.open = True
                atualizar_dados()

        def salvar_funcionario(e):
            if novo_nome.value and novo_login.value and nova_senha.value:
                conn = sqlite3.connect("usuarios.db")
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO usuarios (nome, login, senha) VALUES (?, ?, ?)", (novo_nome.value, novo_login.value, nova_senha.value))
                    conn.commit()
                    novo_nome.value = novo_login.value = nova_senha.value = ""
                    page.snack_bar = ft.SnackBar(ft.Text("Perfil corporativo criado!"), bgcolor=ft.Colors.GREEN_700)
                except:
                    page.snack_bar = ft.SnackBar(ft.Text("Erro: E-mail/Login já cadastrado!"), bgcolor=ft.Colors.RED_700)
                conn.close()
                page.snack_bar.open = True
                atualizar_dados()

        tela_resumo = ft.Column([
            ft.Text("Painel de Gerenciamento - SEGURA EPI", size=24, weight="bold", color=SIDEBAR_BG),
            ft.Row([
                ft.Container(content=ft.Column([ft.Text("Total de EPIs Ativos", color=ft.Colors.GREY_700, weight="bold"), ft.Row([ft.Text("345", size=35, weight="bold", color=SIDEBAR_BG), ft.Icon(ft.Icons.SHIELD, color=PRIMARY_COLOR)])]), bgcolor=ft.Colors.WHITE, padding=20, border_radius=10, width=250, shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12)),
                ft.Container(content=ft.Column([ft.Text("Funcionários Cadastrados", color=ft.Colors.GREY_700, weight="bold"), ft.Row([ft.Text("187", size=35, weight="bold", color=SIDEBAR_BG), ft.Icon(ft.Icons.PERSON, color=PRIMARY_COLOR)])]), bgcolor=ft.Colors.WHITE, padding=20, border_radius=10, width=250, shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12)),
                ft.Container(content=ft.Column([ft.Text("Entregas do Mês", color=ft.Colors.GREY_700, weight="bold"), ft.Row([ft.Text("112", size=35, weight="bold", color=SIDEBAR_BG), ft.Icon(ft.Icons.ASSIGNMENT_TURNED_IN, color=PRIMARY_COLOR)])]), bgcolor=ft.Colors.WHITE, padding=20, border_radius=10, width=250, shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12)),
                ft.Container(content=ft.Column([ft.Text("Vencimentos Próximos", color=ft.Colors.BROWN_700, weight="bold"), ft.Row([ft.Text("15", size=35, weight="bold", color=ft.Colors.RED_700), ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.RED_700)])]), bgcolor="#FDECEC", padding=20, border_radius=10, width=250, shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12)),
            ], spacing=20),
            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
            ft.Row([
                ft.Container(content=ft.Row([ft.Icon(ft.Icons.ADD_MODERATOR, size=40, color=SECONDARY_COLOR), ft.Column([ft.Text("Adicionar Equipamento", weight="bold", size=16), ft.Text("Entrada de novo EPI", color=ft.Colors.GREY)])]), on_click=lambda e: mudar_conteudo("Inventário de EPIs"), bgcolor=ft.Colors.WHITE, padding=20, border_radius=10, width=380, shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12)),
                ft.Container(content=ft.Row([ft.Icon(ft.Icons.PERSON_ADD, size=40, color=SECONDARY_COLOR), ft.Column([ft.Text("Criar Perfil de Funcionário", weight="bold", size=16), ft.Text("Adicionar novo colaborador", color=ft.Colors.GREY)])]), on_click=lambda e: mudar_conteudo("Equipe e Usuários"), bgcolor=ft.Colors.WHITE, padding=20, border_radius=10, width=380, shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12)),
            ], spacing=20),
            ft.Row([
                ft.Container(content=ft.Row([ft.Icon(ft.Icons.ASSIGNMENT_RETURN, size=40, color=SECONDARY_COLOR), ft.Column([ft.Text("Registrar Nova Entrega", weight="bold", size=16), ft.Text("Atribuir EPI a funcionário", color=ft.Colors.GREY)])]), on_click=lambda e: mudar_conteudo("Registro de Entregas"), bgcolor=ft.Colors.WHITE, padding=20, border_radius=10, width=380, shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12)),
                ft.Container(content=ft.Row([ft.Icon(ft.Icons.BAR_CHART, size=40, color=SECONDARY_COLOR), ft.Column([ft.Text("Gerar Relatórios", weight="bold", size=16), ft.Text("Consumo e Custos", color=ft.Colors.GREY)])]), bgcolor=ft.Colors.WHITE, padding=20, border_radius=10, width=380, shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12)),
            ], spacing=20)
        ], visible=True)

        tela_entregas = ft.Column([
            ft.Container(
                width=600,
                padding=40,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(2, ft.Colors.WHITE),
                border_radius=15,
                shadow=ft.BoxShadow(spread_radius=2, blur_radius=20, color=ft.Colors.BLACK12),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.Image(src="logo_principal.jpeg", width=80, height=80, fit="contain"),
                        ft.Text("SEGURA EPI", size=20, weight="bold", color=SIDEBAR_BG),
                        ft.Text("Registrar Entrega de EPI", size=18, weight="bold", color=TEXT_COLOR),
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                        drop_funcionario,
                        drop_epi,
                        ft.Container(
                            content=ft.ElevatedButton(
                                "Enviar Link de Reconhecimento Facial", 
                                icon=ft.Icons.PHONE_ANDROID,
                                on_click=enviar_link_facial, 
                                bgcolor=SECONDARY_COLOR, 
                                color=ft.Colors.WHITE, 
                                width=400, 
                                height=50,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                            ),
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=SECONDARY_COLOR)
                        ),
                        ft.Row([ft.TextButton("Visualizar Entregas", on_click=lambda e: None), ft.TextButton("Voltar ao Dashboard", on_click=lambda e: mudar_conteudo("Dashboard"))], alignment=ft.MainAxisAlignment.CENTER)
                    ]
                )
            ),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Text("Status de Assinaturas Eletrônicas", size=20, weight="bold", color=SIDEBAR_BG),
            ft.Container(content=tabela_entregas, bgcolor=ft.Colors.WHITE, border_radius=10, padding=10, expand=True)
        ], visible=False, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

        tela_epis = ft.Column([
            ft.Container(
                width=600,
                padding=40,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(2, ft.Colors.WHITE),
                border_radius=15,
                shadow=ft.BoxShadow(spread_radius=2, blur_radius=20, color=ft.Colors.BLACK12),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.Image(src="logo_principal.jpeg", width=80, height=80, fit="contain"),
                        ft.Text("SEGURA EPI", size=20, weight="bold", color=SIDEBAR_BG),
                        ft.Text("Cadastrar Novo Equipamento de EPI", size=18, weight="bold", color=TEXT_COLOR),
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                        novo_epi_nome,
                        novo_epi_validade,
                        novo_epi_tipo,
                        ft.Container(
                            content=ft.ElevatedButton(
                                "Cadastrar Equipamento", 
                                on_click=salvar_epi, 
                                bgcolor=SECONDARY_COLOR, 
                                color=ft.Colors.WHITE, 
                                width=400, 
                                height=50,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                            ),
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=SECONDARY_COLOR)
                        ),
                        ft.Row([ft.TextButton("Visualizar Lista de EPIs", on_click=lambda e: None), ft.TextButton("Voltar ao Dashboard", on_click=lambda e: mudar_conteudo("Dashboard"))], alignment=ft.MainAxisAlignment.CENTER)
                    ]
                )
            ),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Text("Inventário Atual", size=20, weight="bold", color=SIDEBAR_BG),
            ft.Container(content=tabela_epis, bgcolor=ft.Colors.WHITE, border_radius=10, padding=10, expand=True)
        ], visible=False, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

        tela_funcionarios = ft.Column([
            ft.Container(
                width=600,
                padding=40,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(2, ft.Colors.WHITE),
                border_radius=15,
                shadow=ft.BoxShadow(spread_radius=2, blur_radius=20, color=ft.Colors.BLACK12),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.Image(src="logo_principal.jpeg", width=80, height=80, fit="contain"),
                        ft.Text("SEGURA EPI", size=20, weight="bold", color=SIDEBAR_BG),
                        ft.Text("Cadastrar Acesso RH / Funcionário", size=18, weight="bold", color=TEXT_COLOR),
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                        novo_nome,
                        novo_login,
                        nova_senha,
                        ft.Container(
                            content=ft.ElevatedButton(
                                "Registrar Acesso", 
                                on_click=salvar_funcionario, 
                                bgcolor=SECONDARY_COLOR, 
                                color=ft.Colors.WHITE, 
                                width=400, 
                                height=50,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                            ),
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=SECONDARY_COLOR)
                        ),
                        ft.TextButton("Voltar ao Dashboard", on_click=lambda e: mudar_conteudo("Dashboard"))
                    ]
                )
            ),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Text("Equipe Autorizada", size=20, weight="bold", color=SIDEBAR_BG),
            ft.Container(content=tabela_funcionarios, bgcolor=ft.Colors.WHITE, border_radius=10, padding=10, expand=True)
        ], visible=False, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

        container_principal = ft.Container(
            content=ft.Column([tela_resumo, tela_entregas, tela_epis, tela_funcionarios], expand=True, scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=40
        )

        def mudar_conteudo(tela_nome):
            tela_resumo.visible = False
            tela_entregas.visible = False
            tela_epis.visible = False
            tela_funcionarios.visible = False

            if tela_nome == "Dashboard": tela_resumo.visible = True
            elif tela_nome == "Registro de Entregas": tela_entregas.visible = True
            elif tela_nome == "Inventário de EPIs": tela_epis.visible = True
            elif tela_nome == "Equipe e Usuários": tela_funcionarios.visible = True
            page.update()

        def criar_botao_menu(texto, icone):
            return ft.TextButton(
                content=ft.Row([ft.Icon(icone, color=ft.Colors.WHITE70), ft.Text(texto, color=ft.Colors.WHITE, size=15)]),
                on_click=lambda _: mudar_conteudo(texto if texto in ["Dashboard", "Inventário de EPIs", "Registro de Entregas", "Equipe e Usuários"] else "Dashboard"),
                style=ft.ButtonStyle(padding=20, shape=ft.RoundedRectangleBorder(radius=0)),
                width=280
            )

        sidebar = ft.Container(
            width=280,
            bgcolor=SIDEBAR_BG,
            content=ft.Column([
                ft.Container(
                    content=ft.Row([ft.Image(src="logo_principal.jpeg", width=40, height=40, fit="contain"), ft.Text("SEGURA EPI", color=ft.Colors.WHITE, size=18, weight="bold")]),
                    padding=20,
                    bgcolor=ft.Colors.BLACK12
                ),
                criar_botao_menu("Dashboard", ft.Icons.HOME),
                criar_botao_menu("Inventário de EPIs", ft.Icons.CHECK_BOX_OUTLINE_BLANK),
                criar_botao_menu("Equipe e Usuários", ft.Icons.PEOPLE_OUTLINE),
                criar_botao_menu("Registro de Entregas", ft.Icons.LOCAL_SHIPPING_OUTLINED),
                criar_botao_menu("Relatórios Gerenciais", ft.Icons.INSERT_CHART_OUTLINED),
                criar_botao_menu("Centro de Alertas", ft.Icons.NOTIFICATIONS_NONE),
                criar_botao_menu("Configurações", ft.Icons.SETTINGS_OUTLINED),
                ft.Container(expand=True),
                ft.TextButton(
                    content=ft.Row([ft.Icon(ft.Icons.EXIT_TO_APP, color=ft.Colors.WHITE70), ft.Text("Sair", color=ft.Colors.WHITE, size=15)]),
                    on_click=realizar_logout,
                    style=ft.ButtonStyle(padding=20, shape=ft.RoundedRectangleBorder(radius=0)),
                    width=280
                )
            ], spacing=0)
        )

        top_bar = ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=ft.padding.symmetric(horizontal=40, vertical=15),
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
            content=ft.Row([
                ft.Text(f"Bem-vindo ao SeguraEPI, {nome_usuario}.", size=20, weight="bold", color=SIDEBAR_BG),
                ft.Row([ft.Text(f"Olá, {nome_usuario}", weight="bold"), ft.CircleAvatar(content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE), bgcolor=PRIMARY_COLOR)])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        layout = ft.Row([
            sidebar,
            ft.Column([top_bar, container_principal], expand=True, spacing=0)
        ], expand=True, spacing=0)

        page.add(layout)
        atualizar_dados()

    page.add(tela_login)

ft.app(target=main)


