

# Auto Organizador de Arquivos para Vídeos
Organizar e manter organizado arquivos utilizados na criação de vídeos.

Este é um script em Python que organiza automaticamente arquivos de vídeo, áudio e imagens em pastas personalizadas. Ele é útil para editores de vídeo que desejam manter seus arquivos fonte organizados.

## Funcionalidades

- Organiza arquivos por tipo: Imagens, Vídeos e Áudios.
- Cria pastas personalizadas com um nome base fornecido pelo usuário.
- Monitora o diretório em tempo real para organizar novos arquivos automaticamente.

## Como Usar

1. Execute o script.
2. Selecione o diretório que deseja monitorar.
3. Defina um nome base para as pastas.
4. Clique em "Iniciar Monitoramento".

## Requisitos

- Python 3.x
- Bibliotecas: `watchdog`, `pystray`, `Pillow`

## Instalação

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio
pip install -r requirements.txt
