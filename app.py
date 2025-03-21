from flask import Flask, render_template, request, redirect, url_for, session
import random
import plotly.graph_objs as go
import plotly.io as pio
import json
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'helloworld!gaptheminderhackathonyay!!!'

users_db = {}

stock_data = {
    "$PlasticSea": 100,
    "$LiveLaughLand": 50,
    "$ClimateWhat": 75
}

# News prompt data
with open("questions.json", "r", encoding="utf-8") as file:
    questions = json.load(file)


# Routes

@app.route("/")
def index():
    if 'user' in session:
        return redirect(url_for('invest_form'))
    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect(url_for('invest_form'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_db.get(username)
        if user and check_password_hash(user['password'], password):
            session['user'] = username  # Store user info in session
            session['balance'] = user['balance']  # Retrieve balance from the database
            return redirect(url_for('invest_form'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if username in users_db:
            return render_template('signup.html', error="Username already exists.")

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match.")

        hashed_password = generate_password_hash(password)

        users_db[username] = {'password': hashed_password, 'balance': 1000}

        return redirect(url_for('login'))

    return render_template("signup.html")


@app.route('/investment', methods=['GET'])
def invest_form():
    if 'balance' not in session:
        user = users_db.get(session['user'])
        session['balance'] = user['balance'] if user else 1000

    if 'stock_prices' not in session:
        session['stock_prices'] = {stock: [price] for stock, price in stock_data.items()}

    if 'balance_history' not in session:
        session['balance_history'] = [session['balance']]  # Initialize balance history with the starting balance

    return render_template("invest_form.html", stocks=stock_data, balance=session['balance'], questions=questions)


@app.route('/result', methods=['POST'])
def invest():
    if 'user' not in session:
        return redirect(url_for('login'))  # Ensure the user is logged in before proceeding

    stock = request.form['stock']
    user_answer = request.form['answer']
    amount = float(request.form['amount'])
    question_index = int(request.form['question_index'])  # Get the question index from the form

    if amount > session['balance']:
        return redirect(url_for('invest_form'))

    if stock not in questions:
        return redirect(url_for('invest_form'))

    question_data = questions[stock][question_index]
    correct_answer = question_data['answer'][0]  # Get only the first answer
    question_text = question_data['question']  # Get the question text
    answer_percentage = question_data['answer'][1]
    answer_detail = question_data['answer'][2]

    if user_answer == correct_answer:
        price_change = random.uniform(0.05, 0.20)  # 5-20% increase
        result = "correct"
    else:
        price_change = random.uniform(0.25, 0.75)  # 25-75% decrease
        result = "incorrect"
        price_change = -price_change

    old_price = stock_data[stock]
    new_price = old_price * (1 + price_change)

    new_price = max(10, new_price)

    stock_data[stock] = new_price

    if 'stock_prices' not in session:
        session['stock_prices'] = {stock: [old_price] for stock, old_price in stock_data.items()}

    session['stock_prices'][stock].append(new_price)

    investment_return = amount * price_change

    session['balance'] = session['balance'] - amount + (amount + investment_return)

    if 'balance_history' not in session:
        session['balance_history'] = [session['balance']]
    else:
        session['balance_history'].append(session['balance'])

    if session['user'] in users_db:
        users_db[session['user']]['balance'] = session['balance']
    else:
        return "Error: User not found in the database."

    chart_html = generate_chart(session['balance_history'], session['stock_prices'])

    amount_change = investment_return

    return render_template('result.html',
                           stock=stock,
                           result=result,
                           amount=amount,
                           new_balance=session['balance'],
                           price_change=round(price_change * 100, 2),
                           stock_data=stock_data,
                           chart_html=chart_html,
                           correct_answer=correct_answer,
                           question_text=question_text,
                           answer_percentage=answer_percentage,
                           answer_detail=answer_detail,
                           amount_change=amount_change)

def generate_chart(balance_history, stock_prices):
    fig = go.Figure()

    # Add balance history
    fig.add_trace(go.Scatter(
        y=balance_history,
        x=list(range(len(balance_history))),
        mode='lines+markers',
        name="Balance",
        line=dict(color="blue", width=2)
    ))

    # Add each stock's price history
    for stock, prices in stock_prices.items():
        fig.add_trace(go.Scatter(
            y=prices,
            x=list(range(len(prices))),
            mode='lines+markers',
            name=f"{stock} Price",
            line=dict(dash="dash")
        ))

    # Layout settings
    fig.update_layout(
        title="Balance & Stock Price History",
        title_x=0.5,
        xaxis_title="Investment Round",
        yaxis_title="Value",
        hovermode="x",
    )

    chart_html = pio.to_html(fig, full_html=True, include_mathjax="cdn")
    return chart_html


@app.route('/logout')
def logout():
    session.clear()
    return redirect((url_for('login')))


if __name__ == '__main__':
    app.run(debug=True)
