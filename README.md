📄 ExtratorCB - Automação de Comprovantes Bancários

💻 Sobre o Projeto

O ExtratorCB é uma ferramenta desktop desenvolvida para automatizar o processo de auditoria de RH e Tesouraria. Ele processa grandes arquivos PDF contendo múltiplos comprovantes de pagamento bancário, identifica funcionários específicos através de uma lista de dados e recorta individualmente cada comprovante, renomeando-os para o padrão corporativo.

O sistema resolve o problema de ter que tirar "prints" manuais de PDFs bancários que contêm 2 comprovantes por página, economizando horas de trabalho manual.

⚙️ Funcionalidades Técnicas

Extração Inteligente ("Island Strategy"): Utiliza lógica geométrica e detecção de âncoras de texto (Regex) para isolar comprovantes mesmo em layouts irregulares.

Fuzzy Matching: Utiliza a biblioteca thefuzz para encontrar nomes de funcionários mesmo com abreviações ou pequenos erros de digitação.

OCR/Regex Híbrido: Extrai datas e CPFs ignorando formatações (pontos/traços) para garantir assertividade.

Interface Moderna: GUI construída com CustomTkinter (Modo Escuro nativo e responsividade).

Multithreading: Processamento em background para não congelar a interface durante a leitura de PDFs pesados.

🛠 Tecnologias Utilizadas

Linguagem: Python

GUI: CustomTkinter

Manipulação de PDF: pdfplumber & pypdf

Lógica de Texto: Regex & TheFuzz

🚀 Como Executar o Projeto

Pré-requisitos

Certifique-se de ter o Python instalado em sua máquina.

Clone o repositório:

git clone [https://github.com/Robert-Taylor-MF/ExtratorCB.git](https://github.com/Robert-Taylor-MF/ExtratorCB.git)


Instale as dependências:

pip install -r requirements.txt


Execute a interface:

python interface_extrator.py


📦 Como Gerar o Executável (.exe)

Para distribuir para usuários finais sem Python instalado:

pyinstaller --noconsole --onefile --icon=assets/icone.ico --collect-all customtkinter --name "ExtratorCB" interface_extrator.py


📝 Autor

Desenvolvido por Robert Taylor.