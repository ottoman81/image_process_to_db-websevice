import sys
import os

# Proje kök dizinini Python path'ine ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
# Projenin ana dizinini sisteme ekle
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

try:
    from Application.CameraOCRApp import CameraOCRApp
    from Utils.TesseractUtils import setup_tesseract, manual_tesseract_setup
except ImportError as e:
    print(f"Import hatası: {e}")
    print("Lütfen tüm dosyaların doğru konumda olduğundan emin olun.")
    sys.exit(1)

def main():
    print("Gelişmiş Kamera OCR ve Sıcaklık Veritabanı Uygulaması")
    print("=" * 50)
    
    # Tesseract kurulumunu kontrol et
    if not setup_tesseract():
        print("\nTesseract otomatik olarak bulunamadı.")
        
        # Manuel yol girmeyi dene
        manual_path = input("Lütfen Tesseract.exe'nin tam yolunu girin (boş bırakırsanız uygulama kapanır): ").strip()
        if manual_path:
            if not manual_tesseract_setup(manual_path):
                print("Tesseract kurulumu başarısız. Uygulama kapanıyor.")
                return 1
        else:
            print("Tesseract bulunamadı. Uygulama kapanıyor.")
            return 1
    
    try:
        app = CameraOCRApp(sys.argv)
        return app.run()
    except Exception as e:
        print(f"Uygulama çalıştırılırken bir hata oluştu: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())