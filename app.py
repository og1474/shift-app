from flask import Flask,render_template,request,redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_setting_db():
    conn_setting = sqlite3.connect('setting.db')
    c_setting = conn_setting.cursor() ##すでにある場合は上書きしない
    ##基本情報用テーブル
    c_setting.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            wage REAL,
            fare REAL  
        )
    ''')
    ##データが存在しない時だけ初期値を入れる
    c_setting.execute('SELECT COUNT(*) FROM settings')
    if c_setting.fetchone()[0] == 0:
        c_setting.execute('INSERT INTO settings (id,wage,fare) VALUES (1,?,?)',(1000,0))
    conn_setting.commit()
    conn_setting.close()

#"シフト用テーブル"
def init_shift_db():
    conn = sqlite3.connect('shift.db')
    c = conn.cursor() ##すでにある場合は上書きしない
    c.execute('''
        CREATE TABLE IF NOT EXISTS shifts ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            hours REAL NOT NULL,
            breaktime REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/",methods=['GET','POST']) ##/はトップページ
def index():
    conn = sqlite3.connect('shift.db')
    c = conn.cursor()
    conn_setting = sqlite3.connect('setting.db')
    c_setting = conn_setting.cursor()

    if request.method == 'POST': ##ユーザーがフォームを送信=POSTした時に実行
        action = request.form.get('action') ##valueの値を取得
        if action == 'setting-add':
            wage = float(request.form['wage'])
            fare = float(request.form['fare'])
            c_setting.execute('UPDATE settings SET wage = ?, fare = ? WHERE id = 1', (wage, fare))
            conn_setting.commit() ##ここは忘れない
        elif action == 'add':
            date = request.form['date'] ##dateで入力された日付を取得
            hours = float(request.form['hours']) ##hoursで入植された数字を取得して小数に変換
            if hours >= 8.0:
                breaktime = 1.5
            elif hours >= 6.0:
                breaktime = 1.0
            else:
                breaktime = 0
            c.execute('INSERT INTO shifts (date,hours,breaktime) VALUES(?,?,?)',(date,hours,breaktime)) ##テーブルに保存
            conn.commit()
        elif action == 'delete':
            delete_id = request.form['id'] ##削除するidを取得
            c.execute('DELETE FROM shifts WHERE id = ?',(delete_id,)) ##指定されたidのデータを削除
            conn.commit()
    
    c.execute('SELECT id,date,hours,breaktime FROM shifts') ##データベースから記録を取得
    data = c.fetchall()
    c_setting.execute('SELECT wage,fare FROM settings')
    info = c_setting.fetchone()

    #合計給与を計算
    total_breaktime = sum(row[3] for row in data) ##合計休憩時間を計算
    total_hours = sum(row[2] for row in data) ##1行ごとに2つめの値を足す
    total_days = sum(1 for row in data)
    wage = info[0]
    fare = info[1]
    total_salary = (total_hours - total_breaktime) * wage + total_days * fare

    conn.close() 
    conn_setting.close()       
    return render_template('index.html',
                           data=data,
                           total=total_salary,
                           wage=wage,
                           fare=fare) ##index.htmlを返す

if __name__ == '__main__': ##このファイルを直接実行したときだけFlaskを起動
    init_setting_db()
    init_shift_db()
    app.run(debug=True)