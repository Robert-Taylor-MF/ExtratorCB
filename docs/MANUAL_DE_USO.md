📘 Manual de Utilização - ExtratorCB

Bem-vindo ao manual do Extrator de Comprovantes Bancários. Esta ferramenta foi criada para facilitar a separação de comprovantes de pagamento em arquivos PDF.

📋 Pré-requisitos

Para utilizar o sistema, você precisará de:

Lista de Funcionários (.txt): Um arquivo de texto contendo os dados de quem você quer buscar.

Arquivos do Banco (.pdf): Os arquivos baixados do site do banco contendo os comprovantes.

Como montar o arquivo .txt

O arquivo deve seguir estritamente o formato abaixo, separado por ponto e vírgula (;).
Uma linha por funcionário.

Formato:
Nome Completo;CPF;Matricula

Exemplo:

Carlos Drummond; 123.456.789-00; 001520
Clarice Lispector; 11122233344; 001521


Nota: O CPF pode ser colocado com ou sem pontos.

🚀 Passo a Passo

1. Carregar a Base de Dados

Abra o programa ExtratorCB.

No campo "1. Lista de Funcionários", clique no botão "Carregar TXT".

Selecione o arquivo .txt que você preparou.

2. Selecionar os PDFs

No campo "2. Arquivos PDF", clique em "Adicionar PDFs".

Você pode selecionar um ou vários arquivos de uma vez (ex: competência Janeiro, Fevereiro, Março).

Eles aparecerão na lista de "Arquivos na Fila".

3. Escolher onde Salvar

No campo "3. Pasta de Destino", clique em "Selecionar Pasta".

Escolha a pasta onde o robô deve salvar os comprovantes recortados.

Sugestão: Crie uma pasta nova para não misturar arquivos.

4. Executar

Clique no botão verde "INICIAR EXTRAÇÃO".

A barra de progresso mostrará o andamento.

Ao final, uma mensagem de "Sucesso" aparecerá na tela.

❓ Solução de Problemas Comuns

Erro: "Arquivo aberto/travado"

Causa: Você está tentando salvar um comprovante mas o PDF anterior ou o arquivo de destino já está aberto no Adobe Reader/Navegador.

Solução: Feche todos os PDFs abertos e tente novamente.

Erro: Nenhum comprovante encontrado

Causa: O nome no PDF está muito diferente do nome no TXT ou o formato do banco mudou.

Solução: Verifique se o nome no .txt está correto. O sistema usa inteligência para aproximar nomes, mas diferenças muito grandes podem falhar.