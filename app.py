from flask import Flask,render_template,request

app = Flask(__name__)
@app.route("/",methods=["GET","POST"]) ##/はトップページ
def index():
    salary = None
    hourly_wage = 1100 ##時給（1100円で固定）

    if request.method == "POST": ##ユーザーがフォームを送信=POSTした時に実行
        try:
            hours = float(request.form["hours"]) ##フォームの入力を取り出す、floatは小数点ありの数字に変換
            salary = int (hours * hourly_wage) ##intは小数点以下切り捨て
        except ValueError:
            salary = "エラー：数値を入力してください"
    return render_template("index.html",salary=salary) ##salaryにsalaryを代入しindex.htmlを返す

if __name__ == "__main__":
    app.run(debug=True)