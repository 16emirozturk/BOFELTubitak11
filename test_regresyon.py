import os
import tempfile
import unittest
from pathlib import Path

import db


class GuvenliOkulRegresyonTestleri(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.eski_yol = db.DB_YOLU
        db.DB_YOLU = Path(self.tmp.name) / "test.db"
        db.hazirla()
        db.anonim_hazirla()

    def tearDown(self):
        db.DB_YOLU = self.eski_yol
        self.tmp.cleanup()

    def _bildirim(self, aciklama):
        return db.bildirim_ekle(olay_turu="Diğer", ortam="Sınıfta", zaman_bilgisi="Bugün",
            tekrar_durumu="Bir kez", aciklama=aciklama, anonim=True, demo=True)

    def test_sayfalama_ve_toplam_sayisi(self):
        for i in range(7):
            self._bildirim(f"Test açıklaması {i}")
        self.assertEqual(db.kayit_sayisi(), 7)
        self.assertEqual(len(db.kayitlari_getir(limit=3, offset=0)), 3)
        self.assertEqual(len(db.kayitlari_getir(limit=3, offset=3)), 3)
        self.assertEqual(len(db.kayitlari_getir(limit=3, offset=6)), 1)
        self.assertEqual(len(db.kayitlari_getir(limit=None)), 7)

    def test_veri_silme_yordamı_kapalı(self):
        self._bildirim("Kalıcı test kaydı")
        with self.assertRaises(RuntimeError):
            db.sonuclanmis_kayitlari_sil(360, "test")
        self.assertEqual(db.kayit_sayisi(), 1)

    def test_yedek_ve_geri_yukleme(self):
        self._bildirim("Yedek testi")
        yedek = db.veritabani_yedegi_uret()
        self.assertTrue(yedek.startswith(b"SQLite format 3"))
        db.veritabani_yedegini_yukle(yedek)
        self.assertEqual(db.kayit_sayisi(), 1)
        self.assertEqual(db.veritabani_durumunu_kontrol_et()["durum"], "ok")

    def test_gecersiz_yedek_reddedilir(self):
        with self.assertRaises(Exception):
            db.veritabani_yedegini_yukle(b"not-a-database")

    def test_yedi_dilde_yeni_yonetim_alani_cevirileri(self):
        from i18n import translate
        expected = {
            "Türkçe": "Akıllı Yönetim Çalışma Alanı",
            "English": "Smart Administration Workspace",
            "Deutsch": "Arbeitsbereich für die Verwaltung",
            "Français": "Espace de travail de gestion",
            "Español": "Espacio de trabajo de administración",
            "العربية": "مساحة عمل الإدارة الذكية",
            "Azərbaycan dili": "Ağıllı idarəetmə iş sahəsi",
        }
        for language, result in expected.items():
            with self.subTest(language=language):
                self.assertEqual(translate("Akıllı Yönetim Çalışma Alanı", language), result)

    def test_pdf_unicode_diller(self):
        import gelistirmeler
        for language in ("Türkçe", "English", "Deutsch", "Français", "Español", "Azərbaycan dili"):
            with self.subTest(language=language):
                pdf = gelistirmeler.pdf_proje_raporu(language)
                self.assertTrue(pdf.startswith(b"%PDF-"))
                self.assertGreater(len(pdf), 5000)

    def test_arapca_pdf_bagimliliklari(self):
        try:
            import arabic_reshaper  # noqa: F401
            import bidi.algorithm  # noqa: F401
        except ImportError:
            self.skipTest("Arapça PDF için requirements.txt içindeki RTL paketleri bu ortamda kurulu değil.")
        import gelistirmeler
        pdf = gelistirmeler.pdf_proje_raporu("العربية")
        self.assertTrue(pdf.startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
