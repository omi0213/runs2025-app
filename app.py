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

def フォント登録():
    font_paths = ['/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc']
    for path in font_paths:
        try:
            pdfmetrics.registerFont(TTFont('Japanese', path))
            print(f"✅ フォントOK")
            return True
        except:
            continue
    return False

フォントOK = フォント登録()

HTML = '''
<!DOCTYPE html>
<html><head><title>🏃 RUNS2025</title><meta charset="UTF-8">
<style>
body{background:#f0f0f0;padding:20px;font-family:Arial;}
.container{max-width:500px;margin:auto;background:white;padding:30px;border-radius:10px;}
input,select{padding:10px;width:100%;margin:5px 0;}
button{padding:10px 20px;margin:5px;background:#ff6b6b;color:white;border:none;border-radius:5px;cursor:pointer;}
.preview-container{display:none;background:#f9f9f9;padding:20px;margin:20px 0;border:2px solid #ffd700;}
</style></head>
<body>
<div class="container">
<h1> RUNS2025 記録証</h1>

<input type="text" id="search" placeholder="横山　貴臣" value="横山　貴臣">
<select id="event">
    <option value="1000m">1000m走</option>
    <option value="3000m" selected>3000m走</option>
</select>
<button onclick="previewPDF()">👁️ プレビュー</button>
<button onclick="getPDF()">🎉 ダウンロード</button>

<div id="result"></div>
<div id="preview-container" class="preview-container">
    <h3>プレビュー</h3>
    <div id="preview-html"></div>
    <button onclick="downloadPDF()">✅ ダウンロード</button>
    <button onclick="closePreview()">✕ 戻る</button>
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
            document.getElementById('result').innerHTML = '❌ ' + data.error;
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
    print(f"🔍 CSVチェック: {os.path.exists(記録ファイル)}")
    if os.path.exists(記録ファイル):
        df = pd.read_csv(記録ファイル)
        print(f"🔍 CSVデータ: {len(df)}行")
        print(f"🔍 最初の行: {df.iloc[0].to_dict() if len(df)>0 else 'なし'}")
        df = df.iloc[:, :3]
        df.columns = ['名前', '種目', '記録']
        return df
    return pd.DataFrame(columns=['名前', '種目', '記録'])

@app.route('/')
def ホーム():
    return render_template_string(HTML)

@app.route('/records')
def 全記録():
    df = データ読み込み()
    return df.to_dict('records')

@app.route('/preview/<name>/<event>')
def PDFプレビュー(name, event):
    print(f"🔍 プレビュー検索: {name}, {event}")
    df = データ読み込み()
    該当 = df[(df['名前'] == name) & (df['種目'] == event)]
    print(f"🔍 検索結果: {len(該当)}件")
    if 該当.empty:
        return {'error': f'"{name}" の {event} の記録がありません'}
    
    記録 = 該当.iloc[0]['記録']
    print(f"✅ プレビュー成功: {記録}")
    
    preview_html = f'''
    <div style="padding:30px;border:3px solid gold;background:white;width:300px;margin:auto;">
        <div style="text-align:center;font-size:24px;"> RUNS2025 </div>
        <div style="text-align:center;font-size:20px;margin:20px 0;">種目：{event}</div>
        <div style="text-align:center;font-size:18px;margin:20px 0;">名前：{name}</div>
        <div style="text-align:center;font-size:36px;color:red;">記録：{記録}</div>
        <div style="text-align:center;font-size:20px;margin:20px 0;">NICE RUNS!!</div>
        <div style="text-align:center;font-size:14px;">{datetime.now().strftime('2025年%m月%d日')}</div>
    </div>
    '''
    return {'html': preview_html, 'url': f'/pdf/{name}/{event}'}

@app.route('/pdf/<name>/<event>')
def PDF発行(name, event):
    print(f"📄 PDF作成: {name}, {event}")
    df = データ読み込み()
    該当 = df[(df['名前'] == name) & (df['種目'] == event)]
    if 該当.empty:
        return f'<h1>❌ "{name}" の {event} の記録がありません</h1>'
    
    記録 = 該当.iloc[0]['記録']
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=B5)
    width, height = B5
    c.setFillColorRGB(1,1,1)
    c.rect(0,0,width,height,fill=1)
    c.setFillColorRGB(0,0,0)
    if フォントOK:
        c.setFont("Japanese", 24)
    else:
        c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height-100, "RUNS2025")
    if フォントOK:
        c.setFont("Japanese", 20)
    else:
        c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height-150, f"{event}")
    if フォントOK:
        c.setFont("Japanese", 18)
    else:
        c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height-200, f"名前：{name}")
    if フォントOK:
        c.setFont("Japanese", 36)
    else:
        c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2, height-250, f"記録：{記録}")
    if フォントOK:
        c.setFont("Japanese", 20)
    else:
        c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height-300, "NICE RUNS!!")
    if フォントOK:
        c.setFont("Japanese", 14)
    else:
        c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height-380, f"{datetime.now().strftime('2025年%m月%d日')}")
    if フォントOK:
        c.setFont("Japanese", 14)
    else:
        c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height-410, "SHONAN RUNS")
    c.setStrokeColorRGB(1,0.84,0)
    c.setLineWidth(3)
    c.rect(20,20,width-40,height-40)
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"RUNS2025_{name}_{event}.pdf")

if __name__ == '__main__':
    print("🚀 RUNS2025 デバッグ版起動！")
    app.run(debug=True, host='0.0.0.0', port=5001)