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
# 修正1: フォントファイル名を汎用的なものに変更
# このファイル（ipaexg.ttf）をプログラムと同じディレクトリに置いてください
FONT_NAME = 'JapaneseFont'
FONT_FILE = 'ipaexg.ttf' 

def フォント登録():
    # 修正2: 汎用フォントファイルのチェックと登録
    if not os.path.exists(FONT_FILE):
        print(f"❌ フォントファイルが見つかりません: {FONT_FILE}。IPAフォントなどをダウンロードしてこのファイル名で保存してください。")
        return False

    try:
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))
        print(f"✅ フォントOK: {FONT_FILE} を {FONT_NAME} として登録しました。")
        return True
    except Exception as e:
        print(f"❌ フォント登録エラー: {e}")
        return False

# グローバル変数へのフォント登録結果の保存はそのまま
フォントOK = フォント登録()

# ... (HTML変数、データ読み込み関数、ルート関数は省略) ...
# HTML変数、データ読み込み関数、ホーム、全記録、PDFプレビューは元のコードのまま使用してください。

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

    # 修正3: フォントOKの場合、登録した汎用フォント名を使用
    base_font = FONT_NAME if フォントOK else "Helvetica-Bold"
    
    # RUNS2025
    c.setFont(base_font, 24)
    c.drawCentredString(width/2, height-100, "RUNS2025")
    
    # 種目
    c.setFont(base_font, 20)
    c.drawCentredString(width/2, height-150, f"種目：{event}") # '種目：' に漢字が含まれる場合はフォントが必須
    
    # 名前
    c.setFont(base_font, 18)
    c.drawCentredString(width/2, height-200, f"名前：{name}") # '名前：' と {name} に漢字が含まれる場合はフォントが必須
    
    # 記録
    c.setFont(base_font, 36)
    c.drawCentredString(width/2, height-250, f"記録：{記録}") # '記録：' に漢字が含まれる場合はフォントが必須
    
    # NICE RUNS!!
    c.setFont(base_font, 20)
    c.drawCentredString(width/2, height-300, "NICE RUNS!!")

    # 日付
    c.setFont(base_font, 14)
    c.drawCentredString(width/2, height-380, f"{datetime.now().strftime('2025年%m月%d日')}") # 年月日 に漢字が含まれる場合はフォントが必須

    # SHONAN RUNS
    c.drawCentredString(width/2, height-410, "SHONAN RUNS")

    # 枠線
    c.setStrokeColorRGB(1,0.84,0)
    c.setLineWidth(3)
    c.rect(20,20,width-40,height-40)
    
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"RUNS2025_{name}_{event}.pdf")

if __name__ == '__main__':
    print("🚀 RUNS2025 デバッグ版起動！")
    # '記録ファイル'が存在しない場合は作成を試みる
    if not os.path.exists(記録ファイル):
        print(f"⚠️ {記録ファイル} が見つかりません。テストデータを作成します。")
        test_data = pd.DataFrame([
            ['横山　貴臣', '3000m', '9:15.34'],
            ['山田　太郎', '1000m', '2:50.00'],
        ], columns=['名前', '種目', '記録'])
        test_data.to_csv(記録ファイル, index=False)
        print("✅ テストデータ作成完了。")
    app.run(debug=True, host='0.0.0.0', port=5001)
