import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import json
import webbrowser
from extrator_comprovantes import ExtratorComprovantes, carregar_lista_do_txt

# Configuração Padrão (será sobrescrita pelo JSON)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "config_extrator.json"
GITHUB_URL = "https://github.com/Robert-Taylor-MF"

class AppExtrator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ExtratorCB - Automação RH")
        self.geometry("800x800")
        self.minsize(600, 600)
        
        # Ícone
        try:
            if os.path.exists("assets/icone.ico"): # Caminho ajustado para estrutura src
                self.iconbitmap("assets/icone.ico")
            elif os.path.exists("icone.ico"):
                self.iconbitmap("icone.ico")
        except Exception:
            pass
        
        # Variáveis
        self.caminho_txt = ctk.StringVar()
        self.caminho_saida = ctk.StringVar()
        self.lista_pdfs = [] # Lista de caminhos completos
        
        # Carregar configurações e Tema
        self.config = self.carregar_config()
        self.aplicar_tema_inicial()
        
        self.criar_widgets()
        
        # Restaurar últimas configurações de caminhos
        if self.config.get("last_txt"):
            self.caminho_txt.set(self.config["last_txt"])
        if self.config.get("last_output"):
            self.caminho_saida.set(self.config["last_output"])

    def aplicar_tema_inicial(self):
        # Define o tema antes de criar os widgets para evitar 'flash' branco
        tema_salvo = self.config.get("theme", "System")
        ctk.set_appearance_mode(tema_salvo)
        # Variável para controlar o switch visualmente
        self.switch_var = ctk.StringVar(value=tema_salvo)

    def criar_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # Log area expande

        # --- TOPO: Título e Switch de Tema ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        # Switch de Tema (NOVIDADE QUE ESTAVA FALTANDO)
        self.switch_theme = ctk.CTkSwitch(
            self.frame_top, 
            text="Modo Escuro / Claro", 
            command=self.alternar_tema,
            variable=self.switch_var,
            onvalue="Dark",
            offvalue="Light"
        )
        self.switch_theme.pack(side="right")

        # --- Bloco 1: Lista de Funcionários ---
        self.frame_txt = ctk.CTkFrame(self)
        self.frame_txt.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="ew")
        
        lbl_txt = ctk.CTkLabel(self.frame_txt, text="1. Lista de Funcionários (.txt)", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_txt.pack(padx=15, pady=(5, 0), anchor="w")
        
        frame_txt_inner = ctk.CTkFrame(self.frame_txt, fg_color="transparent")
        frame_txt_inner.pack(fill="x", padx=10, pady=(5, 10))
        
        self.entry_txt = ctk.CTkEntry(frame_txt_inner, textvariable=self.caminho_txt, placeholder_text="Selecione o arquivo...", height=35)
        self.entry_txt.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_txt = ctk.CTkButton(frame_txt_inner, text="Carregar TXT", command=self.selecionar_txt, width=140, height=35)
        btn_txt.pack(side="right")

        # --- Bloco 2: Lista de PDFs ---
        self.frame_pdf = ctk.CTkFrame(self)
        self.frame_pdf.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")
        
        lbl_pdf = ctk.CTkLabel(self.frame_pdf, text="2. Arquivos PDF (Competências)", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_pdf.pack(padx=15, pady=(5, 0), anchor="w")

        self.scroll_pdfs = ctk.CTkScrollableFrame(self.frame_pdf, height=140, label_text="Arquivos na Fila")
        self.scroll_pdfs.pack(fill="both", expand=True, padx=15, pady=5)
        
        frame_pdf_btns = ctk.CTkFrame(self.frame_pdf, fg_color="transparent")
        frame_pdf_btns.pack(fill="x", padx=15, pady=(5, 10))
        
        btn_add_pdf = ctk.CTkButton(frame_pdf_btns, text="Adicionar PDFs", command=self.adicionar_pdfs, width=150, height=35)
        btn_add_pdf.pack(side="left") 
        
        btn_clear_pdf = ctk.CTkButton(frame_pdf_btns, text="Limpar Tudo", command=self.limpar_pdfs, 
                                      fg_color="#D32F2F", hover_color="#B71C1C", width=150, height=35)
        btn_clear_pdf.pack(side="right")

        # --- Bloco 3: Pasta de Saída ---
        self.frame_out = ctk.CTkFrame(self)
        self.frame_out.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        lbl_out = ctk.CTkLabel(self.frame_out, text="3. Pasta de Destino", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_out.pack(padx=15, pady=(5, 0), anchor="w")
        
        frame_out_inner = ctk.CTkFrame(self.frame_out, fg_color="transparent")
        frame_out_inner.pack(fill="x", padx=10, pady=(5, 10))
        
        self.entry_out = ctk.CTkEntry(frame_out_inner, textvariable=self.caminho_saida, placeholder_text="Onde salvar os arquivos?", height=35)
        self.entry_out.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_out = ctk.CTkButton(frame_out_inner, text="Selecionar Pasta", command=self.selecionar_saida, width=140, height=35)
        btn_out.pack(side="right")

        # --- Bloco 4: Execução e Log ---
        self.frame_run = ctk.CTkFrame(self)
        self.frame_run.grid(row=4, column=0, padx=20, pady=(10, 5), sticky="nsew")
        
        self.btn_executar = ctk.CTkButton(self.frame_run, text="INICIAR EXTRAÇÃO", command=self.iniciar_thread, 
                                          width=300, height=45,
                                          font=ctk.CTkFont(size=16, weight="bold"),
                                          fg_color="#2E7D32", hover_color="#1B5E20")
        self.btn_executar.pack(pady=(15, 10), anchor="center")
        
        self.progress_bar = ctk.CTkProgressBar(self.frame_run, width=400)
        self.progress_bar.pack(pady=(0, 10), anchor="center")
        self.progress_bar.set(0)
        
        self.log_area = ctk.CTkTextbox(self.frame_run, font=("Consolas", 12))
        self.log_area.pack(fill="both", expand=True, padx=15, pady=(0, 5))
        self.log_area.configure(state="disabled")

        # --- Rodapé ---
        self.frame_footer = ctk.CTkFrame(self, fg_color="transparent", height=30)
        self.frame_footer.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        
        self.lbl_creditos = ctk.CTkLabel(self.frame_footer, 
                                         text="Desenvolvido por Robert Taylor 🚀", 
                                         font=ctk.CTkFont(size=11),
                                         text_color="gray60",
                                         cursor="hand2")
        self.lbl_creditos.pack(anchor="center")
        
        self.lbl_creditos.bind("<Button-1>", lambda e: self.abrir_github())
        self.lbl_creditos.bind("<Enter>", lambda e: self.lbl_creditos.configure(text_color="#3B8ED0"))
        self.lbl_creditos.bind("<Leave>", lambda e: self.lbl_creditos.configure(text_color="gray60"))

    # --- Lógica da UI ---

    def alternar_tema(self):
        novo_tema = self.switch_var.get()
        ctk.set_appearance_mode(novo_tema)
        self.salvar_config("theme", novo_tema)

    def atualizar_lista_visual_pdfs(self):
        # Limpa visualmente
        for widget in self.scroll_pdfs.winfo_children():
            widget.destroy()
            
        for i, pdf in enumerate(self.lista_pdfs):
            nome = os.path.basename(pdf)
            
            # Container do Item (Zebrado)
            cor_bg = ("gray85", "gray25") if i % 2 == 0 else ("gray90", "gray20")
            
            item_frame = ctk.CTkFrame(self.scroll_pdfs, fg_color=cor_bg) 
            item_frame.pack(fill="x", padx=5, pady=2)
            
            # Ícone e Nome
            lbl = ctk.CTkLabel(item_frame, text=f"📄 {nome}", anchor="w", padx=10)
            lbl.pack(side="left", pady=5, fill="x", expand=True)
            
            # Botão Remover Individual (X) (NOVIDADE QUE FALTAVA)
            # Usamos lambda p=pdf: ... para capturar o valor atual de 'pdf' no loop
            btn_remove = ctk.CTkButton(
                item_frame, 
                text="✕", 
                width=30, 
                height=25,
                fg_color="transparent", 
                text_color=("red", "#ff5555"),
                hover_color=("gray75", "gray30"),
                command=lambda p=pdf: self.remover_um_pdf(p)
            )
            btn_remove.pack(side="right", padx=10)

    def remover_um_pdf(self, pdf_path):
        if pdf_path in self.lista_pdfs:
            self.lista_pdfs.remove(pdf_path)
            self.atualizar_lista_visual_pdfs()

    def adicionar_pdfs(self):
        filenames = filedialog.askopenfilenames(title="Selecione os PDFs", filetypes=[("PDF", "*.pdf")])
        if filenames:
            for f in filenames:
                if f not in self.lista_pdfs:
                    self.lista_pdfs.append(f)
            self.atualizar_lista_visual_pdfs()

    def limpar_pdfs(self):
        self.lista_pdfs = []
        self.atualizar_lista_visual_pdfs()

    # --- Métodos Auxiliares ---

    def abrir_github(self):
        webbrowser.open(GITHUB_URL)

    def log(self, mensagem):
        self.log_area.configure(state="normal")
        self.log_area.insert("end", mensagem + "\n")
        self.log_area.see("end")
        self.log_area.configure(state="disabled")

    def selecionar_txt(self):
        filename = filedialog.askopenfilename(title="Selecione a Lista TXT", filetypes=[("Texto", "*.txt")])
        if filename:
            self.caminho_txt.set(filename)
            self.salvar_config("last_txt", filename)

    def selecionar_saida(self):
        folder = filedialog.askdirectory(title="Pasta de Saída")
        if folder:
            self.caminho_saida.set(folder)
            self.salvar_config("last_output", folder)

    def iniciar_thread(self):
        if not self.caminho_txt.get():
            messagebox.showwarning("Atenção", "Selecione o arquivo TXT.")
            return
        if not self.lista_pdfs:
            messagebox.showwarning("Atenção", "Adicione pelo menos um PDF.")
            return
        if not self.caminho_saida.get():
            messagebox.showwarning("Atenção", "Selecione a pasta de destino.")
            return

        self.btn_executar.configure(state="disabled")
        self.progress_bar.set(0)
        
        self.log_area.configure(state="normal")
        self.log_area.delete("1.0", "end")
        self.log_area.configure(state="disabled")

        t = threading.Thread(target=self.worker_processamento)
        t.start()

    def worker_processamento(self):
        txt_path = self.caminho_txt.get()
        output_folder = self.caminho_saida.get()
        total_arquivos = len(self.lista_pdfs)

        def logger_wrapper(msg):
            self.after(0, lambda: self.log(msg))

        logger_wrapper(">>> Carregando base de dados...")
        lista_funcionarios = carregar_lista_do_txt(txt_path, logger=logger_wrapper)

        if not lista_funcionarios:
            self.after(0, lambda: messagebox.showerror("Erro", "Lista vazia ou inválida."))
            self.after(0, lambda: self.btn_executar.configure(state="normal"))
            return

        for idx, pdf_path in enumerate(self.lista_pdfs):
            pdf_nome = os.path.basename(pdf_path)
            logger_wrapper(f"\n>>> Processando ({idx+1}/{total_arquivos}): {pdf_nome}")
            
            extrator = ExtratorComprovantes(pdf_path, lista_funcionarios, callback_log=logger_wrapper)
            
            def progress_callback(percent):
                progresso_geral = ((idx * 100) + percent) / (total_arquivos * 100)
                self.after(0, lambda: self.progress_bar.set(progresso_geral))

            extrator.processar_pdf(update_progress=progress_callback)
            extrator.salvar_arquivos_individuais(output_folder)

        self.after(0, lambda: self.progress_bar.set(1.0))
        logger_wrapper("\n>>> CONCLUÍDO! Todos arquivos foram gerados. <<<")
        self.after(0, lambda: messagebox.showinfo("Sucesso", "Processo finalizado com sucesso!"))
        self.after(0, lambda: self.btn_executar.configure(state="normal"))

    def carregar_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except: pass
        return {}

    def salvar_config(self, key, value):
        self.config[key] = value
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)

if __name__ == "__main__":
    app = AppExtrator()
    app.mainloop()