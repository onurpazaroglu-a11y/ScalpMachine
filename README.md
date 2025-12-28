ScalpMachine

Human-in-the-loop, AI destekli çoklu interval teknik analiz sistemi

Genel Bakış

ScalpMachine; kullanıcı tarafından tanımlanan teknik indikatörler, çoklu zaman dilimi (interval) analizleri ve kullanıcı geri bildirimleriyle zaman içinde gelişen bir karar destek platformudur.

Program ilk kurulduğunda hazır bir AI modeli içermez.
AI, programın içinde yer alır ancak kullanıcı kullandıkça öğrenir.

Bu yaklaşım ile:

kontrol kullanıcıda kalır

otomatik bot davranışı oluşmaz

sistem kişiselleşir

Temel Özellikler

GUI tabanlı indikatör seçimi

Çoklu interval analiz desteği

CALL / PUT / WAIT sinyal üretimi

Interval bazlı analiz sonuçları

Kullanıcı onaylı işlem akışı

Performans bazlı Risk Governor

Arka arkaya kayıplarda otomatik blok

Kullanıcı geri bildirimiyle gelişen AI

Modüler indikatör ve AI yapısı

AI Yaklaşımı

ScalpMachine’daki AI:

piyasayı tahmin etmez

analiz üretmez

işlem açmaz

AI’nın görevi:

hangi sinyallerin kullanıcı için işe yaradığını öğrenmek

confidence ve risk ayarlamaları yapmak

WAIT kararlarını optimize etmek

AI:

programın içindedir

ilk gün boştur

zamanla gelişir

silinebilir ve yeniden eğitilebilir

Risk Governor (Davranışsal Stop-Loss)

Program fiyat bazlı değil, performans bazlı koruma uygular.

Örnek:

Arka arkaya 5 yanlış işlem

Program 15 dakika işlem üretimini bloke eder

Bu sürede:

analiz devam eder

AI veri toplamayı sürdürür

kullanıcı korunur

Modüler Mimari
İndikatörler

Her indikatör bağımsız bir modüldür ve sonradan eklenebilir.

AI Modülleri

Her AI:

belirli indikatörlere

belirli interval kullanımına

kendi veritabanına

bağlı olarak çalışır.

Dosya Yapısı (Özet)

core/ → analiz ve sinyal motoru

gui/ → kullanıcı arayüzü

indicators/ → indikatör modülleri

ai/ → öğrenme ve karar ayarlayıcı

db/ → SQLite veritabanları

data/ → ekran görüntüleri

Uyarı

Bu yazılım bir karar destek sistemidir.
Üretilen sinyaller yatırım tavsiyesi değildir.
Tüm işlemlerin sorumluluğu kullanıcıya aittir.

Lisans

Bu proje geliştirici tarafından belirlenen lisans koşullarına tabidir.

Kapanış Yorumu (Önemli)

Bu yapı:

kısa vadeli bir “bot”

hazır bir sinyal yazılımı

değil;

kullanıcıyla birlikte olgunlaşan kişisel bir karar altyapısıdır.