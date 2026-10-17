const START_DATE_STRING = '2026-04-20';
const START_DAY_NUMBER = 82;

// ==========================================
// CONFIGURATION
// ==========================================
function getProps() {
    const p = PropertiesService.getScriptProperties();
    return {
        token: String(p.getProperty('BOT_TOKEN') || '').trim(),
        allowedId: String(p.getProperty('ALLOWED_CHAT_ID') || '').trim(),
        folderId: String(p.getProperty('FOLDER_ID') || '').trim(),
        webhookUrl: String(p.getProperty('WEBHOOK_URL') || '').trim()
    };
}

function tgUrl() {
    return 'https://api.telegram.org/bot' + getProps().token;
}

// ==========================================
// WEBHOOK (Nhận lệnh từ Telegram)
// ==========================================
function doPost(e) {
    if (!e || !e.postData) return HtmlService.createHtmlOutput("OK");
    try {
        const data = JSON.parse(e.postData.contents);
        const props = getProps();

        if (data.message && data.message.text) {
            const chatId = String(data.message.chat.id);

            // Chặn người lạ
            if (props.allowedId && chatId !== props.allowedId) return HtmlService.createHtmlOutput("OK");

            const text = data.message.text.trim().toLowerCase();

            if (text.startsWith('/start')) {
                sendMessage_(chatId, '🌅 Daily Story Bot đã sẵn sàng!\nNhập lệnh /sendnow để bot lấy và gửi ảnh của ngày hôm nay ngay lập tức.');
            } else if (text.startsWith('/sendnow')) {
                sendMessage_(chatId, '⏳ Đang vào Drive lấy ảnh, đợi chút nhé...');
                sendDailyStory();
            }
        }
    } catch (err) {
        Logger.log(err);
    }
    return HtmlService.createHtmlOutput("OK");
}

function sendMessage_(chatId, text) {
    UrlFetchApp.fetch(tgUrl() + '/sendMessage', {
        method: 'post',
        contentType: 'application/json',
        payload: JSON.stringify({ chat_id: chatId, text: text }),
                      muteHttpExceptions: true
    });
}

// ==========================================
// MAIN LOGIC (Hàm chính gửi ảnh)
// ==========================================
function sendDailyStory() {
    const props = getProps();
    if (!props.token || !props.allowedId || !props.folderId) {
        Logger.log("LỖI: Chưa cấu hình đủ BOT_TOKEN, ALLOWED_CHAT_ID hoặc FOLDER_ID trong Script Properties.");
        return;
    }

    // Tính toán số ngày
    const startDate = new Date(START_DATE_STRING + 'T00:00:00');
    const today = new Date();
    startDate.setHours(0, 0, 0, 0);
    today.setHours(0, 0, 0, 0);

    const diffTime = today.getTime() - startDate.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const targetDay = START_DAY_NUMBER + diffDays;

    if (targetDay < 1) {
        Logger.log(`Ngày không hợp lệ: ${targetDay}`);
        return;
    }

    // Tìm ảnh trên Google Drive
    const fileName = `Day_${targetDay}.png`;
    const folder = DriveApp.getFolderById(props.folderId);

    const safeFileName = fileName.replace(/"/g, '\\"');
    const files = folder.searchFiles(`title = "${safeFileName}"`);

    if (!files.hasNext()) {
        sendMessage_(props.allowedId, `⚠️ Không tìm thấy ảnh cho hôm nay: <b>${fileName}</b>\nBạn hãy kiểm tra lại trên Google Drive nhé.`);
        return;
    }

    const imageFile = files.next();
    const imageBlob = imageFile.getBlob().setName(fileName);

    // Gửi ảnh qua Telegram
    const res = UrlFetchApp.fetch(tgUrl() + '/sendPhoto', {
        method: 'post',
        payload: {
            chat_id: props.allowedId,
            photo: imageBlob,
            caption: `Day ${targetDay}'s cover`
        },
        muteHttpExceptions: true
    });

    const responseText = res.getContentText();
    Logger.log("Kết quả gửi ảnh: " + responseText);

    let responseData;
    try {
        responseData = JSON.parse(responseText);
    } catch (err) {
        Logger.log('Telegram trả về dữ liệu không hợp lệ.');
        return;
    }

    if (!responseData.ok) {
        sendMessage_(props.allowedId, `❌ Lỗi khi gửi ảnh: ${responseData.description}`);
        return;
    }

    // Dọn dẹp (Xóa ảnh cũ)
    cleanupOldFiles_(folder, targetDay);
}

function cleanupOldFiles_(folder, targetDay) {
    for (let i = 1; i <= 5; i++) {
        const oldDayNumber = targetDay - i;
        if (oldDayNumber < 1) break;

        const oldFileName = `Day_${oldDayNumber}.png`;
        const safeOldFileName = oldFileName.replace(/"/g, '\\"');
        const oldFiles = folder.searchFiles(`title = "${safeOldFileName}"`);

        while (oldFiles.hasNext()) {
            const oldFile = oldFiles.next();
            oldFile.setTrashed(true);
            Logger.log(`Đã chuyển ảnh cũ vào thùng rác: ${oldFileName}`);
        }
    }
}

// ==========================================
// DEBUG & SETUP TOOLS
// ==========================================
function forceSetWebhook() {
    // Web App URL (bắt buộc phải có /exec ở đuôi) lấy từ Script Properties > WEBHOOK_URL
    const props = getProps();
    if (!props.webhookUrl) {
        Logger.log("Chưa có WEBHOOK_URL trong Script Properties");
        return;
    }
    const res = UrlFetchApp.fetch('https://api.telegram.org/bot' + props.token + '/setWebhook?url=' + encodeURIComponent(props.webhookUrl) + '&drop_pending_updates=true', {muteHttpExceptions: true});
    Logger.log("Kết quả set Webhook: " + res.getContentText());
}

function testSendMessage() {
    const props = getProps();
    const res = UrlFetchApp.fetch('https://api.telegram.org/bot' + props.token + '/sendMessage', {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({ chat_id: props.allowedId, text: "✅ Test message từ Bot Daily Story!" }),
                                  muteHttpExceptions: true
});
    Logger.log("Kết quả Test: " + res.getContentText());
    }
