"""Güvenli Okul v3.0: rapor, yedek, takvim ve içerik yardımcıları."""
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path

import db


def pdf_proje_raporu(dil: str = "Türkçe") -> bytes:
    """Kişisel veri içermeyen, Unicode fontlu çok sayfalı proje özeti üretir."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                    TableStyle, PageBreak, KeepTogether)

    font_dir = Path(__file__).resolve().parent
    latin_path = font_dir / "DejaVuSans.ttf"
    arabic_path = font_dir / "NotoSansArabic-Regular.ttf"
    arabic_bold_path = font_dir / "NotoSansArabic-Bold.ttf"
    if not latin_path.is_file():
        raise RuntimeError("PDF için gerekli DejaVuSans.ttf bulunamadı. Proje dosyalarını eksiksiz çıkarın.")
    pdfmetrics.registerFont(TTFont("GOSans", str(latin_path)))
    pdfmetrics.registerFont(TTFont("GOSans-Bold", str(latin_path)))
    font = "GOSans"
    bold_font = "GOSans-Bold"
    rtl = dil == "العربية"
    if rtl:
        if not arabic_path.is_file() or not arabic_bold_path.is_file():
            raise RuntimeError("Arapça PDF için NotoSansArabic font dosyaları bulunamadı.")
        pdfmetrics.registerFont(TTFont("GOArabic", str(arabic_path)))
        pdfmetrics.registerFont(TTFont("GOArabic-Bold", str(arabic_bold_path)))
        font, bold_font = "GOArabic", "GOArabic-Bold"
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
        except ImportError as exc:
            raise RuntimeError("Arapça PDF için arabic-reshaper ve python-bidi paketleri kurulmalı.") from exc

    catalog = {
        "Türkçe": {"title":"Güvenli Okul — Proje Raporu","intro":"Bu rapor, uygulamadaki demo kayıtlarından ve toplu istatistiklerden oluşturulmuştur.","purpose":"Projenin amacı","purpose_text":"Akran zorbalığı şüphesine ilişkin bildirimlerin güvenli biçimde iletilmesini, takip edilmesini ve yetkili kişilerce değerlendirilmesini destekleyen bir prototip sunmak.","features":"Temel özellikler","method":"Yöntem ve değerlendirme","limits":"Sınırlılıklar","privacy":"Gizlilik ve veri güvenliği","conclusion":"Sonuç","total":"Toplam bildirim","open":"Açık bildirim","closed":"Sonuçlandırılan bildirim","activities":"Önleyici çalışma","status":"Bildirim durumları","note":"Önemli not","note_text":"Kural tabanlı öncelik sinyalleri karar veya zorbalık kanıtı değildir. Bildirim sayısındaki değişim, zorbalığın gerçek sıklığını veya bir çalışmanın nedensel etkisini kanıtlamaz.","features_text":"Anonim bildirim ve takip kodu; yetkili inceleme alanı; açıklanabilir öncelik sinyalleri; trend ve ortam analizi; önleyici çalışma takvimi; eğitim ve yardım içerikleri; yedekleme ve raporlama.","method_text":"Sistem, kullanıcı tarafından girilen açıklamalarda belirli ifade örüntülerini kural tabanlı olarak tarar. Üretilen sinyaller yalnızca insan incelemesine yardımcı olur.","limits_text":"Bu sürüm bir demo/prototiptir; gerçek okul sistemlerine bağlı değildir. Otomatik analiz kesin sınıflandırma yapmaz ve her durumu yakalayamayabilir.","privacy_text":"Rapor kişisel bildirim açıklamalarını, takip kodlarını veya tekil öğrenci bilgilerini içermez. Yalnızca toplu sayılar kullanılır.","conclusion_text":"Güvenli Okul, güvenli bildirim ve önleyici farkındalık süreçlerini desteklemek amacıyla geliştirilen bir prototiptir. Gerçek kullanım öncesinde kurum onayı, güvenlik incelemesi ve hukuki değerlendirme gerekir.","date":"Rapor tarihi","empty":"Henüz bildirim kaydı bulunmuyor."},
        "English": {"title":"Güvenli Okul — Project Report","intro":"This report is generated from demonstration records and aggregate statistics in the application.","purpose":"Project purpose","purpose_text":"To provide a prototype that supports secure reporting, tracking and authorized human review of suspected peer bullying.","features":"Core features","method":"Method and evaluation","limits":"Limitations","privacy":"Privacy and data protection","conclusion":"Conclusion","total":"Total reports","open":"Open reports","closed":"Resolved reports","activities":"Preventive activities","status":"Report statuses","note":"Important note","note_text":"Rule-based priority signals are not decisions or proof of bullying. Changes in report counts do not establish the true frequency of bullying or a causal effect.","features_text":"Anonymous reporting and tracking codes; protected review area; explainable priority signals; trend and setting analysis; preventive activity calendar; learning and help resources; backup and reporting.","method_text":"The system scans user-submitted descriptions for selected linguistic patterns using rules. Signals support human review only.","limits_text":"This version is a demo/prototype and is not connected to real school systems. Automated analysis is not a definitive classification and may miss cases.","privacy_text":"The report excludes personal report descriptions, tracking codes and individual student information. Aggregate figures only are used.","conclusion_text":"Güvenli Okul is a prototype intended to support safe reporting and preventive awareness. Institutional approval, security review and legal assessment are required before real-world use.","date":"Report date","empty":"No report records are available yet."},
        "Deutsch": {"title":"Güvenli Okul — Projektbericht","intro":"Dieser Bericht basiert auf Demodaten und aggregierten Statistiken der Anwendung.","purpose":"Projektziel","purpose_text":"Ein Prototyp zur sicheren Meldung, Nachverfolgung und menschlichen Prüfung möglicher Fälle von Peer-Mobbing.","features":"Kernfunktionen","method":"Methode und Auswertung","limits":"Einschränkungen","privacy":"Datenschutz","conclusion":"Fazit","total":"Meldungen insgesamt","open":"Offene Meldungen","closed":"Abgeschlossene Meldungen","activities":"Präventionsmaßnahmen","status":"Meldungsstatus","note":"Wichtiger Hinweis","note_text":"Regelbasierte Prioritätssignale sind weder Entscheidungen noch Beweise. Änderungen der Meldezahlen belegen keine tatsächliche Häufigkeit und keine kausale Wirkung.","features_text":"Anonyme Meldung und Tracking-Codes; geschützter Prüfbereich; erklärbare Prioritätssignale; Trendanalysen; Präventionskalender; Lern- und Hilfsangebote; Sicherung und Berichte.","method_text":"Das System prüft eingegebene Beschreibungen regelbasiert auf ausgewählte sprachliche Muster. Signale dienen ausschließlich der menschlichen Prüfung.","limits_text":"Diese Version ist ein Prototyp ohne Verbindung zu realen Schulsystemen. Die automatische Analyse ist keine endgültige Klassifizierung.","privacy_text":"Der Bericht enthält keine persönlichen Meldungstexte, Tracking-Codes oder individuellen Schülerdaten.","conclusion_text":"Güvenli Okul ist ein Prototyp zur Unterstützung sicherer Meldungen und präventiver Aufklärung. Vor einem realen Einsatz sind institutionelle und rechtliche Prüfungen erforderlich.","date":"Berichtsdatum","empty":"Noch keine Meldungen vorhanden."},
        "Français": {"title":"Güvenli Okul — Rapport de projet","intro":"Ce rapport est généré à partir des données de démonstration et de statistiques agrégées.","purpose":"Objectif du projet","purpose_text":"Proposer un prototype facilitant le signalement sécurisé, le suivi et l’examen humain des suspicions de harcèlement entre pairs.","features":"Fonctionnalités principales","method":"Méthode et évaluation","limits":"Limites","privacy":"Confidentialité et protection des données","conclusion":"Conclusion","total":"Signalements au total","open":"Signalements ouverts","closed":"Signalements clôturés","activities":"Actions de prévention","status":"Statut des signalements","note":"Remarque importante","note_text":"Les signaux de priorité fondés sur des règles ne sont ni des décisions ni des preuves. L’évolution des signalements ne démontre ni la fréquence réelle ni un effet causal.","features_text":"Signalement anonyme et code de suivi ; espace d’examen protégé ; signaux explicables ; analyses des tendances ; calendrier préventif ; ressources éducatives ; sauvegarde et rapports.","method_text":"Le système recherche des motifs linguistiques définis dans les descriptions à l’aide de règles. Les signaux servent uniquement à soutenir l’examen humain.","limits_text":"Cette version est un prototype non connecté aux systèmes scolaires réels. L’analyse automatique n’est pas une classification définitive.","privacy_text":"Le rapport exclut les descriptions personnelles, les codes de suivi et les informations individuelles des élèves.","conclusion_text":"Güvenli Okul est un prototype destiné à soutenir les signalements sûrs et la prévention. Une validation institutionnelle, technique et juridique est nécessaire avant tout usage réel.","date":"Date du rapport","empty":"Aucun signalement n’est encore disponible."},
        "Español": {"title":"Güvenli Okul — Informe del proyecto","intro":"Este informe se genera a partir de datos de demostración y estadísticas agregadas.","purpose":"Objetivo del proyecto","purpose_text":"Ofrecer un prototipo que facilite la comunicación segura, el seguimiento y la revisión humana de posibles casos de acoso entre iguales.","features":"Funciones principales","method":"Método y evaluación","limits":"Limitaciones","privacy":"Privacidad y protección de datos","conclusion":"Conclusión","total":"Informes totales","open":"Informes abiertos","closed":"Informes resueltos","activities":"Actividades preventivas","status":"Estado de los informes","note":"Nota importante","note_text":"Las señales de prioridad basadas en reglas no son decisiones ni pruebas. Los cambios en el número de informes no demuestran la frecuencia real ni un efecto causal.","features_text":"Informes anónimos y códigos de seguimiento; área de revisión protegida; señales explicables; análisis de tendencias; calendario preventivo; recursos educativos; copias de seguridad e informes.","method_text":"El sistema busca patrones lingüísticos seleccionados mediante reglas. Las señales solo sirven de apoyo a la revisión humana.","limits_text":"Esta versión es un prototipo y no está conectada a sistemas escolares reales. El análisis automático no constituye una clasificación definitiva.","privacy_text":"El informe no incluye descripciones personales, códigos de seguimiento ni datos individuales del alumnado.","conclusion_text":"Güvenli Okul es un prototipo para apoyar la comunicación segura y la prevención. Antes de un uso real se requieren aprobaciones institucionales y revisiones legales y de seguridad.","date":"Fecha del informe","empty":"Todavía no hay informes."},
        "العربية": {"title":"Güvenli Okul — تقرير المشروع","intro":"أُعد هذا التقرير اعتماداً على بيانات تجريبية وإحصاءات مجمعة من التطبيق.","purpose":"هدف المشروع","purpose_text":"تقديم نموذج أولي يدعم الإبلاغ الآمن والمتابعة والمراجعة البشرية للحالات المشتبه بها من التنمر بين الأقران.","features":"الميزات الأساسية","method":"المنهج والتقييم","limits":"القيود","privacy":"الخصوصية وحماية البيانات","conclusion":"الخلاصة","total":"إجمالي البلاغات","open":"البلاغات المفتوحة","closed":"البلاغات المغلقة","activities":"الأنشطة الوقائية","status":"حالات البلاغات","note":"ملاحظة مهمة","note_text":"إشارات الأولوية القائمة على القواعد ليست قرارات ولا أدلة على التنمر. ولا تثبت تغيرات عدد البلاغات المعدل الحقيقي أو وجود أثر سببي.","features_text":"الإبلاغ المجهول ورموز المتابعة؛ مساحة مراجعة محمية؛ إشارات أولوية قابلة للتفسير؛ تحليل الاتجاهات؛ تقويم الأنشطة الوقائية؛ موارد تعليمية؛ نسخ احتياطي وتقارير.","method_text":"يفحص النظام الأوصاف بحثاً عن أنماط لغوية محددة باستخدام قواعد. وتدعم الإشارات المراجعة البشرية فقط.","limits_text":"هذه النسخة نموذج تجريبي غير متصل بأنظمة المدارس الحقيقية. ولا يمثل التحليل الآلي تصنيفاً نهائياً.","privacy_text":"لا يتضمن التقرير أوصاف البلاغات الشخصية أو رموز المتابعة أو بيانات الطلاب الفردية.","conclusion_text":"Güvenli Okul نموذج أولي لدعم الإبلاغ الآمن والوقاية. ويتطلب الاستخدام الفعلي موافقات مؤسسية ومراجعات أمنية وقانونية.","date":"تاريخ التقرير","empty":"لا توجد بلاغات مسجلة حتى الآن."},
        "Azərbaycan dili": {"title":"Güvenli Okul — Layihə hesabatı","intro":"Bu hesabat tətbiqdəki demo məlumatları və ümumiləşdirilmiş statistika əsasında hazırlanıb.","purpose":"Layihənin məqsədi","purpose_text":"Mümkün həmyaşıd zorakılığı hallarının təhlükəsiz bildirilməsini, izlənməsini və səlahiyyətli şəxslər tərəfindən qiymətləndirilməsini dəstəkləyən prototip təqdim etmək.","features":"Əsas funksiyalar","method":"Metod və qiymətləndirmə","limits":"Məhdudiyyətlər","privacy":"Məxfilik və məlumatların qorunması","conclusion":"Nəticə","total":"Ümumi bildirişlər","open":"Açıq bildirişlər","closed":"Tamamlanmış bildirişlər","activities":"Profilaktik tədbirlər","status":"Bildiriş statusları","note":"Vacib qeyd","note_text":"Qayda əsaslı prioritet siqnalları qərar və ya zorakılıq sübutu deyil. Bildiriş sayındakı dəyişiklik real tezliyi və ya səbəb-nəticə əlaqəsini sübut etmir.","features_text":"Anonim bildiriş və izləmə kodları; qorunan araşdırma sahəsi; izah edilə bilən prioritet siqnalları; trend təhlili; profilaktik tədbirlər təqvimi; təhsil resursları; ehtiyat nüsxə və hesabatlar.","method_text":"Sistem daxil edilən mətnlərdə seçilmiş dil nümunələrini qaydalar əsasında yoxlayır. Siqnallar yalnız insan yoxlamasına kömək edir.","limits_text":"Bu versiya real məktəb sistemlərinə qoşulmayan demo prototipdir. Avtomatik təhlil yekun təsnifat deyil.","privacy_text":"Hesabata şəxsi bildiriş mətnləri, izləmə kodları və ayrı-ayrı şagirdlərin məlumatları daxil edilmir.","conclusion_text":"Güvenli Okul təhlükəsiz bildiriş və profilaktik maarifləndirməni dəstəkləyən prototipdir. Real istifadədən əvvəl institusional, hüquqi və təhlükəsizlik yoxlamaları tələb olunur.","date":"Hesabat tarixi","empty":"Hələ bildiriş qeydi yoxdur."}
    }
    t = catalog.get(dil, catalog["Türkçe"])
    def shape(value: str) -> str:
        if not rtl:
            return value
        return get_display(arabic_reshaper.reshape(value))

    records = db.kayitlari_getir(limit=None)
    total = len(records)
    open_count = sum(1 for r in records if r.get("durum") != "Sonuçlandırıldı")
    closed_count = total - open_count
    activities = int(db.onleyici_ozeti().get("Toplam", 0))
    statuses = {}
    for record in records:
        status = str(record.get("durum") or "—")
        statuses[status] = statuses.get(status, 0) + 1

    out = BytesIO()
    doc = SimpleDocTemplate(out, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=20*mm, bottomMargin=18*mm, title=shape(t["title"]),
                            author="Güvenli Okul")
    styles = getSampleStyleSheet()
    align = TA_RIGHT if rtl else TA_LEFT
    title_style = ParagraphStyle("GOTitle", parent=styles["Title"], fontName=bold_font,
        alignment=TA_CENTER, textColor=colors.HexColor("#17345B"), fontSize=21, leading=29, spaceAfter=8*mm)
    body = ParagraphStyle("GOBody", parent=styles["BodyText"], fontName=font, fontSize=9.2,
        leading=15, alignment=align, textColor=colors.HexColor("#26364A"), spaceAfter=3*mm)
    heading = ParagraphStyle("GOHeading", parent=styles["Heading2"], fontName=bold_font,
        fontSize=13, leading=18, textColor=colors.HexColor("#17345B"), alignment=align,
        spaceBefore=5*mm, spaceAfter=2*mm)
    small = ParagraphStyle("GOSmall", parent=body, fontSize=8, leading=12, textColor=colors.HexColor("#65758A"))
    story = [Spacer(1, 12*mm), Paragraph(shape(t["title"]), title_style),
             Paragraph(shape(t["intro"]), body), Spacer(1, 5*mm)]
    metric_rows = [[shape(t["total"]), str(total)], [shape(t["open"]), str(open_count)],
                   [shape(t["closed"]), str(closed_count)], [shape(t["activities"]), str(activities)]]
    table = Table(metric_rows, colWidths=[112*mm, 30*mm], hAlign="RIGHT" if rtl else "LEFT")
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F1F5FA")),
        ("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#172B4D")),("FONTNAME",(0,0),(-1,-1),font),
        ("FONTSIZE",(0,0),(-1,-1),9), ("GRID",(0,0),(-1,-1),.45,colors.HexColor("#D8E1EC")),
        ("ALIGN",(0,0),(-1,-1),"RIGHT" if rtl else "LEFT"),("PADDING",(0,0),(-1,-1),9)]))
    story += [table, Paragraph(shape(t["purpose"]), heading), Paragraph(shape(t["purpose_text"]), body),
              Paragraph(shape(t["features"]), heading), Paragraph(shape(t["features_text"]), body),
              Paragraph(shape(t["method"]), heading), Paragraph(shape(t["method_text"]), body),
              Paragraph(shape(t["limits"]), heading), Paragraph(shape(t["limits_text"]), body),
              Paragraph(shape(t["privacy"]), heading), Paragraph(shape(t["privacy_text"]), body)]
    if statuses:
        story += [Paragraph(shape(t["status"]), heading)]
        column_labels = {
            "Türkçe": ("Durum", "Sayı"), "English": ("Status", "Count"),
            "Deutsch": ("Status", "Anzahl"), "Français": ("Statut", "Nombre"),
            "Español": ("Estado", "Cantidad"), "العربية": ("الحالة", "العدد"),
            "Azərbaycan dili": ("Status", "Say")}
        status_labels = {
            "Türkçe": {"İnceleme bekliyor":"İnceleme bekliyor","İnceleniyor":"İnceleniyor","Sonuçlandırıldı":"Sonuçlandırıldı"},
            "English": {"İnceleme bekliyor":"Awaiting review","İnceleniyor":"Under review","Sonuçlandırıldı":"Resolved"},
            "Deutsch": {"İnceleme bekliyor":"Wartet auf Prüfung","İnceleniyor":"In Prüfung","Sonuçlandırıldı":"Abgeschlossen"},
            "Français": {"İnceleme bekliyor":"En attente d’examen","İnceleniyor":"En cours d’examen","Sonuçlandırıldı":"Clôturé"},
            "Español": {"İnceleme bekliyor":"Pendiente de revisión","İnceleniyor":"En revisión","Sonuçlandırıldı":"Resuelto"},
            "العربية": {"İnceleme bekliyor":"بانتظار المراجعة","İnceleniyor":"قيد المراجعة","Sonuçlandırıldı":"تم الحل"},
            "Azərbaycan dili": {"İnceleme bekliyor":"Yoxlama gözləyir","İnceleniyor":"Yoxlanılır","Sonuçlandırıldı":"Tamamlandı"}}
        col_a, col_b = column_labels.get(dil, column_labels["Türkçe"])
        status_data = [[shape(col_a), shape(col_b)]]
        labels = status_labels.get(dil, status_labels["Türkçe"])
        status_data += [[shape(labels.get(k, k)), str(v)] for k,v in sorted(statuses.items())]
        st_table = Table(status_data, colWidths=[112*mm,30*mm], repeatRows=1)
        st_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17345B")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,-1),font),
            ("FONTSIZE",(0,0),(-1,-1),8.5),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#D8E1EC")),
            ("PADDING",(0,0),(-1,-1),7)]))
        story.append(st_table)
    else:
        story.append(Paragraph(shape(t["empty"]), body))
    story += [Paragraph(shape(t["note"]), heading), Paragraph(shape(t["note_text"]), body),
              Paragraph(shape(t["conclusion"]), heading), Paragraph(shape(t["conclusion_text"]), body)]
    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D8E1EC"))
        canvas.line(18*mm, 14*mm, A4[0]-18*mm, 14*mm)
        canvas.setFont(font, 7)
        canvas.setFillColor(colors.HexColor("#65758A"))
        canvas.drawString(18*mm, 9*mm, f"Güvenli Okul · Demo / Prototype · {datetime.now(db.TZ):%d.%m.%Y %H:%M}")
        canvas.drawRightString(A4[0]-18*mm, 9*mm, str(document.page))
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()


def takvim_uyarilari() -> list[dict]:
    """Yaklaşan ve gecikmiş önleyici çalışmalar; yalnızca yönetim ekranında gösterilir."""
    today = datetime.now(db.TZ).date()
    alerts = []
    for item in db.onleyici_calismalari_getir():
        if item["durum"] in ("Tamamlandı", "İptal edildi"):
            continue
        try:
            due = datetime.strptime(item["planlanan_tarih"], "%Y-%m-%d").date()
        except (TypeError, ValueError):
            continue
        days = (due - today).days
        if days < 0:
            alerts.append({"type": "overdue", "days": abs(days), "item": item})
        elif days <= 14:
            alerts.append({"type": "upcoming", "days": days, "item": item})
    return sorted(alerts, key=lambda a: (a["type"] != "overdue", a["days"]))


EGITIM_KARTLARI = [
    {"title": "Akran zorbalığını tanımak", "summary": "Tekrarlayan, güç dengesizliği içeren davranışları; tek seferlik anlaşmazlıklardan ayırt etmeye yardımcı bilgiler.", "steps": ["Davranışın tekrar edip etmediğine bakın.", "Taraflar arasındaki güç dengesizliğini değerlendirin.", "Etiket koymadan, somut davranışı ve etkisini anlatın."]},
    {"title": "Dijital güvenlik", "summary": "Çevrim içi ortamda saygı, mahremiyet ve güvenli destek arama yolları.", "steps": ["Kişisel bilgileri ve başkalarının özel içeriklerini paylaşmayın.", "Rahatsız edici iletişime yanıt vermek zorunda değilsiniz.", "Güvendiğiniz bir yetişkinden destek isteyin."]},
    {"title": "Tanık olanlar ne yapabilir?", "summary": "Güvenli ve destekleyici müdahale yolları.", "steps": ["Güvenli değilse doğrudan müdahale etmeyin.", "Dışlamaya katılmayın; destekleyici bir tutum gösterin.", "Durumu güvenilir bir yetişkine bildirin."]},
    {"title": "Destek istemek", "summary": "Yardım istemek güçsüzlük değildir; güvenilir yetişkinler ve okul destek birimleriyle konuşun.", "steps": ["Kendinizi güvende hissettiğiniz yetişkini seçin.", "Ne olduğunu ve nasıl etkilendiğinizi anlatın.", "Acil tehlikede yerel acil yardım hizmetlerine başvurun."]},
]

HELP_STEPS = [
    ("1. Bildirim gönder", "Yeni bildirim sayfasında olay türü, ortam ve zaman bilgilerini seçin. Gerçek ad, telefon veya başka kişisel bilgi yazmayın."),
    ("2. Takip kodunu sakla", "Gönderimden sonra oluşan kodu güvenli bir yerde saklayın. Kod, bildirimin durumunu sorgulamak içindir."),
    ("3. Durumu takip et", "Bildirim sorgula alanında takip kodunu girin. Öğrenci ekranında açıklama ve inceleme notları gösterilmez."),
    ("4. Yetkili incelemesi", "Yetkili personel bildirimi insan değerlendirmesiyle inceler. Otomatik sinyaller tek başına karar vermez."),
]
