import os
import shutil
import zipfile
import tarfile
import gzip
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

POLISH_LETTERS = {"ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ż": "z", "ź": "z"}
IMAGE_EXTENSIONS = {"JPG", "JPEG", "PNG", "GIF", "BMP"}
VIDEO_EXTENSIONS = {"MP4", "AVI", "MKV", "MOV", "WMV"}
DOCUMENTS_EXTENSIONS = {"PDF", "DOC", "DOCX", "TXT", "RTF"}
AUDIO_EXTENSIONS = {"MP3", "WAV", "FLAC", "AAC", "OGG"}
APPLICATIONS_EXTENSIONS = {"EXE", "MSI", "DMG", "APP", "DEB"}
ARCHIVES_EXTENSIONS = {"ZIP", "TAR", "GZ"}

class CleanFolder:
    def __init__(self, path):
        self.path = path
        self.all_existing_extentions = set()
        self.unrecognized_extensions = set()

    def normalize(self, some_string):  
        result = ""
        for char in some_string:
            if char.lower() in POLISH_LETTERS:
                result += POLISH_LETTERS[char.lower()]
            elif char.isspace() or char.isalnum():
                result += char
            else:
                result += "_"
        return result 

    def move_and_normalize_files(self, file_path, new_folder_name):
        normalized_name = self.normalize(Path(file_path).stem)
        move_file = os.path.join(os.path.dirname(file_path), new_folder_name)
        move_to = os.path.join(move_file, f"{normalized_name}.{file_path.split('.')[-1]}")

        os.makedirs(move_file, exist_ok= True)
        shutil.move(file_path, move_to)

    def archive_folder_and_move(self, path, arch_name, new_folder_name):
        arch_path = os.path.join(path, arch_name)
        extracted_archive = os.path.join(path, arch_name.split('.')[0])
        move_file = os.path.join(os.path.dirname(arch_path), new_folder_name)
        move_to = os.path.join(move_file, arch_name.split('.')[0])

        if arch_name.split('.')[-1].upper() == 'ZIP':
            with zipfile.ZipFile(arch_path, 'r') as zip:
                zip.extractall(extracted_archive)

        elif arch_name.split('.')[-1].upper() == 'TAR':
            with tarfile.open(arch_path, 'r') as tar:
                tar.extractall(extracted_archive)

        elif arch_name.split('.')[-1].upper() == 'GZ':
            with gzip.open(arch_path, 'rb') as f_in, open(extracted_archive, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.remove(arch_path)
        os.makedirs(move_file, exist_ok = True)
        shutil.move(extracted_archive, move_to)      

    def process_folder(self, root, dirs, files):
        for file in files:
            file_path = os.path.join(root, file)
            extension = file.split('.')[-1].upper()

            if any(folder in root for folder in ["Pictures", "Video", "Documents", "Music", "Applications", "Unrecognized extensions"]):
                continue
            if extension in IMAGE_EXTENSIONS:
                self.all_existing_extentions.add(extension)
                self.move_and_normalize_files(file_path, "Pictures")
            elif extension in VIDEO_EXTENSIONS:
                self.all_existing_extentions.add(extension)
                self.move_and_normalize_files(file_path, "Video")
            elif extension in DOCUMENTS_EXTENSIONS:
                self.all_existing_extentions.add(extension)
                self.move_and_normalize_files(file_path, "Documents")
            elif extension in AUDIO_EXTENSIONS:
                self.all_existing_extentions.add(extension)
                self.move_and_normalize_files(file_path, "Music")
            elif extension in APPLICATIONS_EXTENSIONS:
                self.all_existing_extentions.add(extension)
                self.move_and_normalize_files(file_path, "Applications")
            elif extension in ARCHIVES_EXTENSIONS:
                self.all_existing_extentions.add(extension)
                self.archive_folder_and_move(root, file, "Archive")
            else:
                self.unrecognized_extensions.add(extension)
                continue

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            new_dir_path = os.path.join(root, self.normalize(dir))
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
            else:
                os.rename(dir_path ,new_dir_path)

    def process_folders(self):
        with ThreadPoolExecutor(max_workers=4) as executor:
            for root, dirs, files in os.walk(self.path):
                executor.submit(self.process_folder, root, dirs, files)
        print("Existing extensions:", self.all_existing_extentions)
        print("Unrecognized extensions:", self.unrecognized_extensions)


if __name__ == "__main__":
    folder_cleaner = CleanFolder("D:/Program files/OneDrive/Pulpit/Balagan")
    folder_cleaner.process_folders()
