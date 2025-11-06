from flask import Flask, request, send_file, render_template_string
import pandas as pd
import io
from reportlab.lib.pagesizes import B5
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

app = Flask(__name__)
記録ファイル = "runs2025.csv"

# フォント設定
def フォント登録():
    # Mac標準フォント
    font_paths = ['/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc']
    for path in font_paths:
        try:
            pdfmetrics.registerFont(TTFont('Japanese', path))
            print(f"フォントOK: {path}")
            return True
        except Exception as e:
            print(f"フォントエラー: {e}")
            continue
    print("フォント登録失敗: 標準フォントなし")
    return False

フォントOK = フォント登録()

HTML = '''
<!DOCTYPE html>
<html><head><title>RUNS2025</title><meta charset="UTF-8">
<style>
body{background:#f0f0f0;padding:20px;font-family:Arial;}
.container{max-width:500px;margin:auto;background:white;padding:30px;border-radius:10px;}
input,select{padding:10px;width:100%;margin:5px 0;}
button{padding:10px 20px;margin:5px;background:#ff6b6b;color:white;border:none;border-radius:5px;cursor:pointer;}
.preview-container{display:none;background:#f9f9f9;padding:20px;margin:20px 0;border:2px solid #ffd700;}
</style></head>
<body>
<div class="container">
<h1>RUNS2025 記録証</h1>
<input type="text" id="search" placeholder="横山　貴臣" value="横山　貴臣">
<select id="event">
    <option value="1000m">1000m走</option>
    <option value="3000m" selected>3000m走</option>
</select>
<button onclick="previewPDF()">プレビュー</button>
<button onclick="getPDF()">ダウンロード</button>
<div id="result"></div>
<div id="preview-container" class="preview-container">
    <h3>プレビュー</h3>
    <div id="preview-html"></div>
    <button onclick="downloadPDF()">ダウンロード</button>
    <button onclick="closePreview()">戻る</button>
</div>
<h3>全記録</h3>
<div id="records"></div>
</div>
<script>
let previewData = null;
function previewPDF() {
    const name = document.getElementById('search').value;
    const event = document.getElementById('event').value;
    document.getElementById('result').innerHTML = 'チェック中...';
    fetch(`/preview/${encodeURIComponent(name)}/${encodeURIComponent(event)}`)
    .then(r=>r.json())
    .then(data=>{
        document.getElementById('result').innerHTML = '';
        if(data.error) {
            document.getElementById('result').innerHTML = ' ' + data.error;
            return;
        }
        previewData = data;
        document.getElementById('preview-html').innerHTML = data.html;
        document.getElementById('preview-container').style.display = 'block';
    }).catch(e=>document.getElementById('result').innerHTML = 'エラー: ' + e);
}
function downloadPDF() { window.open(previewData.url, '_blank'); }
function closePreview() { document.getElementById('preview-container').style.display = 'none'; }
function getPDF() { previewPDF(); }
function loadRecords() {
    fetch('/records').then(r=>r.json()).then(data=>{
        document.getElementById('records').innerHTML = data.map(r=>`<div>${r['名前']}: ${r['種目']} ${r['記録']}</div>`).join('') || 'データなし';
    });
}
loadRecords();
</script>
</body></html>
'''

def データ読み込み():
    print(f"CSVチェック: {os.path.exists(記録ファイル)}")
    if os.path.exists(記録ファイル):
        df = pd.read_csv(記録ファイル, encoding='utf-8')
        print(f"CSVデータ: {len(df)}行")
        df = df.iloc[:, :3]
        df.columns = ['名前', '種目', '記録']
        return df
    else:
       
