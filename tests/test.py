import os
import sys
import subprocess
import unittest
from pathlib import Path

def run_tests():
    """Testleri çalıştıran fonksiyon"""
    try:
        # test klasörünü bul
        test_dir = Path("test")
        if not test_dir.exists():
            print("Hata: 'test' klasörü bulunamadı!")
            return False
        
        # test dosyalarını bul
        test_files = list(test_dir.glob("test_*.py"))
        
        if not test_files:
            print("Uyarı: test klasöründe test dosyası bulunamadı!")
            return False
            
        print(f"Toplam {len(test_files)} adet test dosyası bulundu:")
        for file in test_files:
            print(f"  - {file.name}")
        
        # testleri çalıştır
        print("\nTestler çalıştırılıyor...")
        result = subprocess.run([
            sys.executable, "-m", "unittest", 
            f"{test_dir}/test_*.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tüm testler başarıyla çalıştı!")
            return True
        else:
            print("❌ Testler başarısız oldu:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return False

if __name__ == "__main__":
    print("Python modül testi başlatılıyor...")
    success = run_tests()
    if not success:
        sys.exit(1)