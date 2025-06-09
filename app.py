from flask import Flask,render_template,request,redirect
import sqlite3
from datetime import datetime


app = Flask(__name__)
HOURLY_WAGE = 1100 ##時給（1100円で固定）
FARE = 200 ##交通費（とりあえず固定）

def init_db():
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

    if request.method == 'POST': ##ユーザーがフォームを送信=POSTした時に実行
        action = request.form.get('action') ##valueの値を取得
        if action == 'add':
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

    #合計給与を計算
    total_breaktime = sum(row[3] for row in data) ##合計休憩時間を計算
    total_hours = sum(row[2] for row in data) ##1行ごとに2つめの値を足す
    total_hours = total_hours - total_breaktime ##合計勤務時間から合計休憩時間を引く
    total_days = sum(1 for row in data)
    total_salary = (total_hours * HOURLY_WAGE)+(total_days * FARE)

    conn.close()        
    return render_template('index.html',data=data,total=total_salary,HOURLY_WAGE=HOURLY_WAGE,FARE=FARE) ##salaryにsalaryを代入しindex.htmlを返す

if __name__ == '__main__': ##このファイルを直接実行したときだけFlaskを起動
    init_db()
    app.run(debug=True)