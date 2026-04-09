/**
 * Google Apps Script — Hamad Carousel → Sheets Bridge
 *
 * خطوات النشر:
 * 1. افتح: https://script.google.com
 * 2. مشروع جديد (New Project)
 * 3. الصق هذا الكود كاملاً
 * 4. غيّر SPREADSHEET_ID بمعرف شيتك
 * 5. Deploy > New Deployment > Web App
 *    - Execute as: Me
 *    - Who has access: Anyone
 * 6. انسخ الـ URL وضعه في إعدادات التطبيق
 */

const SPREADSHEET_ID = "13Y2DlQHx77l7BS3ZXErOYI-Hvd50Eza8oj2u3nq2KOA";
const SHEET_NAME     = "Sheet1"; // غيّر لو اسم الصفحة مختلف

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss    = SpreadsheetApp.openById(SPREADSHEET_ID);
    let sheet   = ss.getSheetByName(SHEET_NAME);

    // أضف هيدر تلقائياً لو الشيت فارغ
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        "التاريخ", "الموضوع",
        "سلايد 1 — كفر",
        "سلايد 2",
        "سلايد 3",
        "سلايد 4",
        "سلايد 5",
        "سلايد 6 — CTA",
      ]);
      // تنسيق الهيدر
      const header = sheet.getRange(1, 1, 1, 8);
      header.setBackground("#7c3aed");
      header.setFontColor("#ffffff");
      header.setFontWeight("bold");
      header.setHorizontalAlignment("center");
    }

    // استخرج السلايدات بالترتيب
    const slides = data.slides || [];
    const texts  = [1,2,3,4,5,6].map(n => {
      const s = slides.find(x => x.num === n);
      return s ? s.text : "";
    });

    const date = new Date().toLocaleDateString("ar-KW", {
      year:"numeric", month:"2-digit", day:"2-digit"
    });

    sheet.appendRow([date, data.topic || "", ...texts]);

    // تنسيق الصف الجديد
    const lastRow = sheet.getLastRow();
    const row = sheet.getRange(lastRow, 1, 1, 8);
    row.setWrap(true);
    row.setVerticalAlignment("top");
    sheet.setRowHeight(lastRow, 120);

    return ContentService
      .createTextOutput(JSON.stringify({ status: "ok", row: lastRow }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: "error", message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// للاختبار من المتصفح
function doGet() {
  return ContentService
    .createTextOutput(JSON.stringify({ status: "ok", message: "Carousel Sheet Bridge is running" }))
    .setMimeType(ContentService.MimeType.JSON);
}
