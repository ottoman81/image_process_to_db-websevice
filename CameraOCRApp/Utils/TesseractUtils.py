import os
import platform
import subprocess
import sys
import pytesseract
from pathlib import Path

def find_tesseract():
    """
    Sistemde Tesseract'ın kurulu olduğu yeri bulur
    """
    system = platform.system()
    
    # Windows için olası yollar
    if system == "Windows":
        windows_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME')),
        ]
        
        # PATH'tan da kontrol et
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        for path_dir in path_dirs:
            if 'tesseract' in path_dir.lower():
                possible_path = os.path.join(path_dir, 'tesseract.exe')
                if os.path.exists(possible_path):
                    windows_paths.insert(0, possible_path)
        
        for path in windows_paths:
            if os.path.exists(path):
                print(f"Tesseract bulundu: {path}")
                return path
        
        # Son çare: where komutu ile arama
        try:
            result = subprocess.run(['where', 'tesseract'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                path = result.stdout.split('\n')[0].strip()
                if os.path.exists(path):
                    print(f"Tesseract where komutu ile bulundu: {path}")
                    return path
        except:
            pass
            
        return 'tesseract'
    
    # Linux/Mac için
    else:
        # which komutu ile arama
        try:
            result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                path = result.stdout.strip()
                print(f"Tesseract bulundu: {path}")
                return path
        except:
            pass
            
        # Linux için olası yollar
        linux_paths = [
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/opt/homebrew/bin/tesseract',
            '/usr/bin/tesseract-ocr'
        ]
        
        for path in linux_paths:
            if os.path.exists(path):
                print(f"Tesseract bulundu: {path}")
                return path
                
        return 'tesseract'

def setup_tesseract():
    """
    Tesseract'ı yapılandırır ve kurulumu kontrol eder
    """
    tesseract_cmd = find_tesseract()
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    try:
        # Sürüm kontrolü
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract {version} başarıyla bulundu: {tesseract_cmd}")
        return True
        
    except Exception as e:
        print(f"✗ Tesseract bulunamadı veya çalıştırılamadı!")
        print(f"  Hata: {str(e)}")
        print("\nÇözüm yolları:")
        print("1. Tesseract'ı https://github.com/UB-Mannheim/tesseract/wiki adresinden indirin")
        print("2. Kurulum sırasında 'Add to PATH' seçeneğini işaretleyin")
        return False

def manual_tesseract_setup(tesseract_path):
    """
    Manuel olarak Tesseract yolu ayarlama
    """
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print(f"✓ Manuel yol ayarlandı: {tesseract_path}")
        return setup_tesseract()
    else:
        print(f"✗ Belirtilen yol geçerli değil: {tesseract_path}")
        return False

def search_for_tesseract():
    """
    Tesseract'ı daha derinlemesine ara
    """
    print("\nDerinlemesine Tesseract araması:")
    
    # Tüm sürücülerde arama (Windows)
    if platform.system() == "Windows":
        drives = []
        try:
            # Mevcut sürücüleri al
            for drive in range(65, 91):  # A: dan Z: ye
                drive_letter = chr(drive) + ":\\"
                if os.path.exists(drive_letter):
                    drives.append(drive_letter)
        except:
            drives = ["C:\\"]
        
        search_patterns = [
            "**/tesseract.exe",
            "**/Tesseract-OCR/tesseract.exe",
            "**/Tesseract/tesseract.exe"
        ]
        
        found_paths = []
        for drive in drives:
            for pattern in search_patterns:
                try:
                    for path in Path(drive).glob(pattern):
                        if path.is_file() and "tesseract" in path.name.lower():
                            found_paths.append(str(path))
                            print(f"  Bulundu: {path}")
                except:
                    continue
        
        if found_paths:
            print(f"\n✓ Tesseract bulundu! Lütfen bu yolu kopyalayın: {found_paths[0]}")
            return found_paths[0]
    
    print("  Tesseract bulunamadı. Lütfen manuel olarak kurun.")
    return None