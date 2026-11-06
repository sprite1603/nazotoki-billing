/**
 * 謎解き予定（Notion）を JSON で返す中継スクリプト（Google Apps Script）
 *
 * 設定:
 *   1. プロジェクトの設定 → スクリプト プロパティ に NOTION_TOKEN を追加
 *   2. デプロイ → 新しいデプロイ → 種類「ウェブアプリ」
 *        次のユーザーとして実行: 自分 / アクセスできるユーザー: 全員
 *   3. 発行された URL（…/exec）を site/config.js の API_URL に設定
 */
const DATABASE_ID = '371b37adbf34809ba194d9dfd55d8f2b';

function doGet() {
  try {
    return json_({ updated: now_(), events: fetchEvents_() });
  } catch (e) {
    return json_({ error: String(e && e.message || e) });
  }
}

function fetchEvents_() {
  const token = PropertiesService.getScriptProperties().getProperty('NOTION_TOKEN');
  if (!token) throw new Error('NOTION_TOKEN が未設定です');

  const events = [];
  let cursor = null;
  do {
    const body = { sorts: [{ property: '日付', direction: 'ascending' }], page_size: 100 };
    if (cursor) body.start_cursor = cursor;
    const res = UrlFetchApp.fetch('https://api.notion.com/v1/databases/' + DATABASE_ID + '/query', {
      method: 'post',
      contentType: 'application/json',
      headers: { Authorization: 'Bearer ' + token, 'Notion-Version': '2022-06-28' },
      payload: JSON.stringify(body),
      muteHttpExceptions: true,
    });
    const data = JSON.parse(res.getContentText());
    if (res.getResponseCode() !== 200) throw new Error('Notion API: ' + (data.message || res.getResponseCode()));

    data.results.forEach(function (page) {
      const p = page.properties;
      const start = p['日付'].date && p['日付'].date.start;
      events.push({
        title: p['公演名'].title.map(function (t) { return t.plain_text; }).join('').trim() || '(無題)',
        date: start ? toJstDate_(start) : null,
        amount: p['金額'].number,
        people: p['人数'].number,
        members: p['メンバー'].multi_select.map(function (m) { return m.name; }),
        received: p['受取チェック'].checkbox,
      });
    });
    cursor = data.has_more ? data.next_cursor : null;
  } while (cursor);
  return events;
}

function toJstDate_(s) {
  if (s.indexOf('T') < 0) return s;
  return Utilities.formatDate(new Date(s), 'Asia/Tokyo', 'yyyy-MM-dd');
}

function now_() {
  return Utilities.formatDate(new Date(), 'Asia/Tokyo', "yyyy-MM-dd'T'HH:mm");
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
