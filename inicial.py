import flet as ft
import sqlite3
from datetime import datetime

def criar_banco():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, login TEXT UNIQUE, senha TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS epis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, ca TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entregas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario TEXT, epi TEXT, data TEXT
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
    page.title = "SISTEMA DE SEGURANÇA DO TRABALHO - CONTROLE DE EPI"
    page.window_width = 1920
    page.window_height = 1080
    page.window_maximized = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    
    PRIMARY_COLOR = ft.Colors.BLUE_900
    ACCENT_COLOR = ft.Colors.AMBER_600

    def validar_login(e):
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE login = ? AND senha = ?", (user_input.value, pass_input.value))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            exibir_dashboard()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Erro: Login ou Senha incorretos!"), bgcolor=ft.Colors.RED_700)
            page.snack_bar.open = True
            page.update()

    def exibir_dashboard():
        page.clean()
        
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SHIELD, color=ft.Colors.WHITE, size=40),
                ft.Text("PAINEL DE CONTROLE DE EPI", color=ft.Colors.WHITE, size=30, weight="bold"),
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=PRIMARY_COLOR,
            padding=20,
            border_radius=10
        )

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
            cursor.execute("SELECT nome, ca FROM epis")
            dados = cursor.fetchall()
            conn.close()
            return dados

        def get_entregas():
            conn = sqlite3.connect("usuarios.db")
            cursor = conn.cursor()
            cursor.execute("SELECT funcionario, epi, data FROM entregas")
            dados = cursor.fetchall()
            conn.close()
            return dados

        tabela_entregas = ft.DataTable(columns=[ft.DataColumn(ft.Text("Funcionário")), ft.DataColumn(ft.Text("EPI Recebido")), ft.DataColumn(ft.Text("Data"))])
        tabela_epis = ft.DataTable(columns=[ft.DataColumn(ft.Text("Nome do EPI")), ft.DataColumn(ft.Text("C.A."))])
        tabela_funcionarios = ft.DataTable(columns=[ft.DataColumn(ft.Text("Nome Completo")), ft.DataColumn(ft.Text("Login"))])

        drop_funcionario = ft.Dropdown(label="Funcionário", width=400)
        drop_epi = ft.Dropdown(label="EPI", width=400)

        novo_epi = ft.TextField(label="Nome do Equipamento", width=400)
        novo_ca = ft.TextField(label="Número do C.A.", width=200)

        novo_nome = ft.TextField(label="Nome Completo", width=300)
        novo_login = ft.TextField(label="Login", width=200)
        nova_senha = ft.TextField(label="Senha", width=200, password=True)

        def atualizar_interface():
            tabela_funcionarios.rows.clear()
            for f in get_funcionarios():
                tabela_funcionarios.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(f[0])), ft.DataCell(ft.Text(f[1]))]))
            
            tabela_epis.rows.clear()
            drop_epi.options.clear()
            for e in get_epis():
                tabela_epis.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(e[0])), ft.DataCell(ft.Text(e[1]))]))
                drop_epi.options.append(ft.dropdown.Option(e[0]))

            drop_funcionario.options.clear()
            for f in get_funcionarios():
                drop_funcionario.options.append(ft.dropdown.Option(f[0]))

            tabela_entregas.rows.clear()
            for ent in get_entregas():
                tabela_entregas.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(ent[0])), ft.DataCell(ft.Text(ent[1])), ft.DataCell(ft.Text(ent[2]))]))
            
            page.update()

        def salvar_funcionario(e):
            if novo_nome.value and novo_login.value and nova_senha.value:
                conn = sqlite3.connect("usuarios.db")
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO usuarios (nome, login, senha) VALUES (?, ?, ?)", (novo_nome.value, novo_login.value, nova_senha.value))
                    conn.commit()
                    novo_nome.value = novo_login.value = nova_senha.value = ""
                    page.snack_bar = ft.SnackBar(ft.Text("Funcionário salvo!"), bgcolor=ft.Colors.GREEN_700)
                except:
                    page.snack_bar = ft.SnackBar(ft.Text("Erro: Login já existe!"), bgcolor=ft.Colors.RED_700)
                conn.close()
                page.snack_bar.open = True
                atualizar_interface()

        def salvar_epi(e):
            if novo_epi.value and novo_ca.value:
                conn = sqlite3.connect("usuarios.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO epis (nome, ca) VALUES (?, ?)", (novo_epi.value, novo_ca.value))
                conn.commit()
                conn.close()
                novo_epi.value = novo_ca.value = ""
                page.snack_bar = ft.SnackBar(ft.Text("EPI cadastrado!"), bgcolor=ft.Colors.GREEN_700)
                page.snack_bar.open = True
                atualizar_interface()

        def registrar_entrega(e):
            if drop_funcionario.value and drop_epi.value:
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
                conn = sqlite3.connect("usuarios.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO entregas (funcionario, epi, data) VALUES (?, ?, ?)", (drop_funcionario.value, drop_epi.value, data_atual))
                conn.commit()
                conn.close()
                page.snack_bar = ft.SnackBar(ft.Text("Entrega registrada com sucesso!"), bgcolor=ft.Colors.GREEN_700)
                page.snack_bar.open = True
                atualizar_interface()

        # --- SEÇÕES (Invisíveis por padrão, exceto Entregas) ---
        aba_entregas = ft.Column([
            ft.Text("Registrar Nova Entrega", size=20, weight="bold"),
            ft.Row([drop_funcionario, drop_epi, ft.ElevatedButton("Registrar", on_click=registrar_entrega, bgcolor=PRIMARY_COLOR, color=ft.Colors.WHITE, height=50)]),
            ft.Divider(),
            ft.Text("Histórico de Entregas", size=20, weight="bold"),
            ft.ListView([tabela_entregas], expand=True)
        ], expand=True, visible=True)

        aba_epis = ft.Column([
            ft.Text("Cadastrar Novo EPI", size=20, weight="bold"),
            ft.Row([novo_epi, novo_ca, ft.ElevatedButton("Salvar EPI", on_click=salvar_epi, bgcolor=PRIMARY_COLOR, color=ft.Colors.WHITE, height=50)]),
            ft.Divider(),
            ft.Text("EPIs Cadastrados", size=20, weight="bold"),
            ft.ListView([tabela_epis], expand=True)
        ], expand=True, visible=False)

        aba_funcionarios = ft.Column([
            ft.Text("Cadastrar Novo Funcionário", size=20, weight="bold"),
            ft.Row([novo_nome, novo_login, nova_senha, ft.ElevatedButton("Salvar", on_click=salvar_funcionario, bgcolor=PRIMARY_COLOR, color=ft.Colors.WHITE, height=50)]),
            ft.Divider(),
            ft.Text("Funcionários Cadastrados", size=20, weight="bold"),
            ft.ListView([tabela_funcionarios], expand=True)
        ], expand=True, visible=False)

        # --- CONTROLE DE TROCA DE TELA ---
        def mudar_aba(e):
            aba_entregas.visible = False
            aba_epis.visible = False
            aba_funcionarios.visible = False
            
            if e.control.text == "Entregas":
                aba_entregas.visible = True
            elif e.control.text == "EPIs":
                aba_epis.visible = True
            elif e.control.text == "Funcionários":
                aba_funcionarios.visible = True
            
            page.update()

        menu_botoes = ft.Row([
            ft.ElevatedButton("Entregas", icon=ft.Icons.ASSIGNMENT, on_click=mudar_aba, height=40),
            ft.ElevatedButton("EPIs", icon=ft.Icons.CONSTRUCTION, on_click=mudar_aba, height=40),
            ft.ElevatedButton("Funcionários", icon=ft.Icons.PEOPLE, on_click=mudar_aba, height=40),
        ], alignment=ft.MainAxisAlignment.CENTER)

        conteudo = ft.Container(
            content=ft.Column([aba_entregas, aba_epis, aba_funcionarios], expand=True),
            expand=True,
            padding=20
        )

        page.add(header, menu_botoes, ft.Divider(), conteudo)
        atualizar_interface()

    user_input = ft.TextField(label="Usuário", width=400, prefix_icon=ft.Icons.PERSON, border_color=PRIMARY_COLOR)
    pass_input = ft.TextField(label="Senha", width=400, password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK, border_color=PRIMARY_COLOR, on_submit=validar_login)

    card_login = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.SECURITY, size=80, color=ACCENT_COLOR),
                ft.Text("Acesso Restrito", size=25, weight="bold"),
                user_input,
                pass_input,
                ft.ElevatedButton("ENTRAR", on_click=validar_login, bgcolor=PRIMARY_COLOR, color=ft.Colors.WHITE, width=400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
            padding=50,
        ),
        elevation=10
    )

    page.add(ft.Row([card_login], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True))

ft.app(target=main)