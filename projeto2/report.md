Project 2 Report
=================

###### Students

- Thales Eduardo Adair Menato - *[@thamenato](https://github.com/thamenato)*
- Thiago Faria Nogueira - *[@ThiagoTioGuedes](https://github.com/ThiagoTioGuedes)*
- Camilo Aparecido Ferri Moreira - *[@debugmaster](https://github.com/debugmaster)*

Atenção: o projeto precisa do Python 2.7.X para funcionar. Não utilizar Python 3.X.

Modo de usar
=================
1 - Abra uma instância de *transmitter.py*.
2 - Insira a porta desejada ( **exemplo:9999** ). Outros parâmetros podem ser inseridos, tais como tamanho inicial da janela, porcentagem de perda de pacotes e porcentagem de pacotes a ser corrompida.
3 - Abra um instância de *receiver.py*.
4 - Insira o host, a porta e o nome do arquivo ( exemplo: **localhost 9999 dc_ufscar.jpg** ).
4.1 - Os arquivos disponíveis são: 
- brandenburg_concerto.mp3 (3.12 MB), 
- complete_works_lovecraft.pdf (7.77 MB), 
- dc_ufscar.jpg (1.41 MB), 
- delete.me ( 35 B)
- voyage.mp4 (13.1 MB).
5 - Repita 4) se deseja fazer o download de outros arquivos.

Detalhes de Implementação
=================

Foi implementado um protocolo ( em nível de aplicação) para envio, sem perdas, de arquivos entre dois hosts. 
Ele contém:
- verificação de dados corrompidos
- reenvio em caso de perda de ACK ou pacote
- janela adaptativa
O protocolo utiliza o Go-Back-N.

O cabeçalho tem as seguintes informações:
TYPE - VALOR 0 (Data) ou 1 (ACK) (1 byte)
FLAG SYN (1 byte) - usada para iniciar um envio
FLAG FIN (1 byte) - usada para terminar um envio
SEQUENCE NUMBER (4 bytes) - id do pacote
CHECKSUM (2 bytes) - usado na verificação de erros

O tempo de espera do transmissor para detectar alguma perda é de 1 segundo.
O tempo de espera do receptor para detectar alguma perda é de 1 segundo.
