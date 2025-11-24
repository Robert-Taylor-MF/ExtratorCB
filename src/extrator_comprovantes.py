import pdfplumber
from pypdf import PdfReader, PdfWriter
from thefuzz import fuzz
import os
import unicodedata
import re

# --- ATENÇÃO: Este arquivo NÃO deve ter importações de interface (tkinter, ctk) ---
# Ele é puro processamento de dados.

class ExtratorComprovantes:
    def __init__(self, pdf_path, lista_funcionarios, callback_log=None):
        """
        :param pdf_path: Caminho do PDF
        :param lista_funcionarios: Lista de dicts com dados
        :param callback_log: Função para enviar mensagens de volta para a UI (sem importar a UI)
        """
        self.pdf_path = pdf_path
        self.lista_funcionarios = lista_funcionarios
        self.matches = [] 
        # Se não passar callback, usa print (para testes manuais)
        self.log = callback_log if callback_log else print

    def normalizar_texto(self, texto):
        if not texto:
            return ""
        return ''.join(c for c in unicodedata.normalize('NFD', texto)
                  if unicodedata.category(c) != 'Mn').upper()

    def extrair_data_credito(self, texto):
        padrao = r"DATA D[OE] CREDITO[:\s]*(\d{2})/(\d{2})/(\d{4})"
        match = re.search(padrao, texto)
        if match:
            dia, mes, ano = match.groups()
            return ano, mes
        return None, None

    def processar_pdf(self, update_progress=None):
        self.log(f"--- Analisando: {os.path.basename(self.pdf_path)} ---")
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_paginas = len(pdf.pages)
                
                for i, page in enumerate(pdf.pages):
                    if update_progress:
                        percentual = (i / total_paginas) * 100
                        update_progress(percentual)

                    width = page.width
                    height = page.height
                    
                    # 1. Âncoras
                    txt_rodape = "exceto feriados"
                    ocorrencias_rodape = page.search(txt_rodape)
                    ocorrencias_rodape.sort(key=lambda x: x['top']) 
                    
                    txt_cabecalho = "COMPROVANTE"
                    ocorrencias_cabecalho = page.search(txt_cabecalho)
                    ocorrencias_cabecalho.sort(key=lambda x: x['top'])

                    bbox_top = None
                    bbox_bottom = None

                    # --- Lógica Superior ---
                    inicio_y_1 = 0 
                    if len(ocorrencias_cabecalho) >= 1:
                        inicio_y_1 = max(0, ocorrencias_cabecalho[0]['top'] - 70)
                    
                    if len(ocorrencias_rodape) >= 1:
                        limite_inferior_1 = ocorrencias_rodape[0]['bottom'] + 1
                        bbox_top = (0, inicio_y_1, width, limite_inferior_1)
                    else:
                        bbox_top = (0, 0, width, height / 2)

                    # --- Lógica Inferior ---
                    inicio_y_2 = height / 2 
                    fim_y_2 = height
                    
                    if len(ocorrencias_rodape) >= 1:
                        inicio_y_2 = ocorrencias_rodape[0]['bottom'] + 2
                    elif len(ocorrencias_cabecalho) >= 2:
                        inicio_y_2 = ocorrencias_cabecalho[1]['top'] - 70
                    
                    if len(ocorrencias_rodape) >= 2:
                        fim_y_2 = ocorrencias_rodape[1]['bottom'] + 1
                    
                    bbox_bottom = (0, inicio_y_2, width, fim_y_2)

                    if bbox_top: self._analisar_area(page, bbox_top, i)
                    if bbox_bottom: self._analisar_area(page, bbox_bottom, i)
                    
        except Exception as e:
            self.log(f"Erro crítico ao ler PDF: {e}")

    def _analisar_area(self, page, bbox, num_pagina):
        try:
            if bbox[3] <= bbox[1]: return 
            crop = page.crop(bbox)
            texto_original = crop.extract_text() or ""
            texto_norm = self.normalizar_texto(texto_original)
        except ValueError:
            return 

        ano, mes = self.extrair_data_credito(self.normalizar_texto(texto_original))

        for func in self.lista_funcionarios:
            nome_alvo = self.normalizar_texto(func['nome'])
            cpf_alvo = re.sub(r'\D', '', func.get('cpf', ''))
            
            encontrou = False
            texto_apenas_numeros = re.sub(r'\D', '', texto_norm)
            
            if cpf_alvo and len(cpf_alvo) > 5 and cpf_alvo in texto_apenas_numeros:
                encontrou = True
            elif nome_alvo:
                score = fuzz.partial_ratio(nome_alvo, texto_norm)
                if score >= 85:
                    encontrou = True

            if encontrou:
                self.log(f"  > Encontrado: {func['nome']} (Pág {num_pagina + 1})")
                self.matches.append({
                    'pagina': num_pagina,
                    'bbox': bbox,
                    'funcionario_dados': func,
                    'ano': ano,
                    'mes': mes
                })
                break

    def salvar_arquivos_individuais(self, pasta_saida):
        if not self.matches:
            self.log("  ! Nenhum comprovante encontrado neste arquivo.")
            return

        os.makedirs(pasta_saida, exist_ok=True)
        reader = PdfReader(self.pdf_path)
        
        total = len(self.matches)
        salvos = 0

        for match in self.matches:
            writer = PdfWriter()
            page = reader.pages[match['pagina']]
            original_height = float(page.mediabox.height)
            
            plumber_bbox = match['bbox'] 
            new_top = original_height - float(plumber_bbox[1])
            new_bottom = original_height - float(plumber_bbox[3])

            page.mediabox.lower_left = (0, new_bottom)
            page.mediabox.upper_right = (float(page.mediabox.width), new_top)

            writer.add_page(page)

            chapa = match['funcionario_dados'].get('chapa', 'SEM_MATRICULA')
            chapa = re.sub(r'[\\/*?:"<>|]', '', chapa)
            ano = match['ano'] if match['ano'] else "0000"
            mes = match['mes'] if match['mes'] else "00"
            
            nome_arquivo = f"{ano}_{mes}-{chapa}.pdf"
            caminho_completo = os.path.join(pasta_saida, nome_arquivo)

            try:
                with open(caminho_completo, "wb") as f:
                    writer.write(f)
                salvos += 1
            except PermissionError:
                self.log(f"  [ERRO] Arquivo aberto/travado: {nome_arquivo}")
        
        self.log(f"  > {salvos}/{total} extraídos com sucesso.")

def carregar_lista_do_txt(caminho_txt, logger=print):
    lista = []
    if not os.path.exists(caminho_txt):
        logger(f"ERRO: TXT não encontrado: {caminho_txt}")
        return []

    logger(f"Lendo lista: {os.path.basename(caminho_txt)}")
    with open(caminho_txt, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('#'): continue
            partes = linha.split(';')
            
            if len(partes) >= 3:
                lista.append({'nome': partes[0].strip(), 'cpf': partes[1].strip(), 'chapa': partes[2].strip()})
            elif len(partes) == 2:
                lista.append({'nome': partes[0].strip(), 'cpf': partes[1].strip(), 'chapa': 'SEM_MATRICULA'})
            else:
                logger(f"  [AVISO] Linha inválida no TXT: {linha}")
    
    logger(f"Total de funcionários na lista: {len(lista)}")
    return lista