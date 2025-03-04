import os
import shutil
import logging
import time
from tkinter import Tk, Label, Button, StringVar, messagebox, Frame, Entry
from tkinter.filedialog import askdirectory
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Definir as extensões para cada tipo de arquivo
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.flv', '.mov', '.avi', '.wmv']
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a']

# Configuração do logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Função para garantir que o nome do arquivo seja único
def make_unique(dest, name):
    filename, extension = os.path.splitext(name)
    counter = 1
    # Se o arquivo já existir, adiciona um número ao final do nome
    while os.path.exists(os.path.join(dest, name)):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1
    return name

# Função para mover arquivos, tratando duplicados e erros de permissão
def move_file(dest, entry, name):
    try:
        if os.path.exists(os.path.join(dest, name)):
            unique_name = make_unique(dest, name)
            logging.info(f"Arquivo duplicado encontrado. Renomeando para: {unique_name}")
        else:
            unique_name = name

        # Tentar mover o arquivo
        shutil.move(entry, os.path.join(dest, unique_name))
        logging.info(f"Movido: {name} -> {os.path.join(dest, unique_name)}")
    except PermissionError:
        logging.warning(f"Arquivo em uso: {name}. Tentando novamente em 5 segundos...")
        time.sleep(5)  # Esperar 5 segundos antes de tentar novamente
        move_file(dest, entry, name)  # Tentar mover novamente
    except Exception as e:
        logging.error(f"Erro ao mover o arquivo {name}: {e}")

# Função para organizar os arquivos
def organize_files(directory, base_folder_name):
    # Criar pastas personalizadas com o nome base
    folders = {
        'Imagens': os.path.join(directory, f"{base_folder_name} Imagens"),
        'Videos': os.path.join(directory, f"{base_folder_name} Videos"),
        'Audios': os.path.join(directory, f"{base_folder_name} Audios")
    }

    # Criar pastas se não existirem
    for folder_type, folder_path in folders.items():
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logging.info(f"Pasta criada: {folder_path}")

    # Iterar sobre os arquivos no diretório
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Ignorar pastas
        if os.path.isdir(file_path):
            continue

        # Verificar a extensão do arquivo e mover para a pasta correspondente
        if any(filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
            move_file(folders['Imagens'], file_path, filename)
        elif any(filename.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
            move_file(folders['Videos'], file_path, filename)
        elif any(filename.lower().endswith(ext) for ext in AUDIO_EXTENSIONS):
            move_file(folders['Audios'], file_path, filename)

    logging.info("Organização concluída!")

# Função para processar arquivos existentes na pasta
def process_existing_files(directory, base_folder_name):
    logging.info("Processando arquivos existentes na pasta...")
    organize_files(directory, base_folder_name)

# Classe para monitorar mudanças no diretório
class OrganizerHandler(FileSystemEventHandler):
    def __init__(self, directory, base_folder_name):
        self.directory = directory
        self.base_folder_name = base_folder_name

    def on_modified(self, event):
        # Organiza os arquivos quando há mudanças no diretório
        organize_files(self.directory, self.base_folder_name)

# Interface gráfica
class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de Arquivos")
        self.observer = None
        self.base_folder_name = StringVar()

        # Componentes da interface
        Label(root, text="Diretório para monitorar:").grid(row=0, column=0, padx=10, pady=10)
        self.directory_entry = Entry(root, width=40, state='readonly')
        self.directory_entry.grid(row=0, column=1, padx=10, pady=10)
        Button(root, text="Selecionar Diretório", command=self.select_directory).grid(row=1, column=0, columnspan=2, pady=5)

        # Campo para o nome base das pastas
        Label(root, text="Nome base para as pastas:").grid(row=2, column=0, padx=10, pady=10)
        Entry(root, textvariable=self.base_folder_name, width=40).grid(row=2, column=1, padx=10, pady=10)

        # Botões de controle
        self.start_button = Button(root, text="Iniciar Monitoramento", command=self.start_monitoring, state='disabled')
        self.start_button.grid(row=3, column=0, columnspan=2, pady=5)
        self.stop_button = Button(root, text="Parar Monitoramento", command=self.stop_monitoring, state='disabled')
        self.stop_button.grid(row=4, column=0, columnspan=2, pady=5)

    # Função para selecionar o diretório
    def select_directory(self):
        directory = askdirectory()
        if directory:
            self.directory_entry.config(state='normal')
            self.directory_entry.delete(0, 'end')
            self.directory_entry.insert(0, directory)
            self.directory_entry.config(state='readonly')
            self.start_button.config(state='normal')
            logging.info(f"Diretório selecionado: {directory}")

    # Função para iniciar o monitoramento
    def start_monitoring(self):
        directory = self.directory_entry.get()
        base_folder_name = self.base_folder_name.get()

        if not os.path.isdir(directory):
            messagebox.showerror("Erro", "Diretório inválido!")
            return

        if not base_folder_name:
            messagebox.showerror("Erro", "Defina um nome base para as pastas!")
            return

        # Processar arquivos existentes na pasta
        process_existing_files(directory, base_folder_name)

        # Configurar o observer do watchdog
        event_handler = OrganizerHandler(directory, base_folder_name)
        self.observer = Observer()
        self.observer.schedule(event_handler, directory, recursive=True)
        self.observer.start()
        logging.info(f"Monitoramento iniciado em: {directory}")

        # Atualizar estado dos botões
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

    # Função para parar o monitoramento
    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logging.info("Monitoramento parado.")
            self.observer = None

        # Atualizar estado dos botões
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

# Ponto de entrada do programa
if __name__ == "__main__":
    root = Tk()
    app = FileOrganizerApp(root)
    root.mainloop()