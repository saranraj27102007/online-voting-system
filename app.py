from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client
import random

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# ---------------- DATABASE ---------------- #

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15))
    voted = db.Column(db.Boolean, default=False)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    votes = db.Column(db.Integer, default=0)

# ---------- Create Default Candidates ---------- #

with app.app_context():
    db.create_all()

    if Candidate.query.count() == 0:
        db.session.add(Candidate(name="Candidate A"))
        db.session.add(Candidate(name="Candidate B"))
        db.session.commit()

# ---------------- OTP SETUP ---------------- #

TWILIO_SID = "YOUR_SID"
TWILIO_TOKEN = "YOUR_TOKEN"
TWILIO_NUMBER = "YOUR_TWILIO_NUMBER"

client = Client(TWILIO_SID, TWILIO_TOKEN)

def send_otp(phone):
    otp = random.randint(1000,9999)
    session['otp'] = str(otp)

    client.messages.create(
        body=f"Your Voting OTP is {otp}",
        from_=TWILIO_NUMBER,
        to=phone
    )

# ---------------- ROUTES ---------------- #

@app.route("/")
def index():
    return render_template("index.html")

# Register
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        phone = request.form['phone']
        send_otp(phone)
        session['phone'] = phone
        return redirect("/verify")
    return render_template("register.html")

# OTP Verify
@app.route("/verify", methods=["GET","POST"])
def verify():
    if request.method == "POST":
        user_otp = request.form['otp']

        if user_otp == session.get('otp'):
            new_user = User(phone=session['phone'])
            db.session.add(new_user)
            db.session.commit()
            session['user'] = new_user.id
            return redirect("/vote")
    return '''
    <form method="POST">
        Enter OTP: <input name="otp">
        <button>Verify</button>
    </form>
    '''

# Vote Page
@app.route("/vote")
def vote():
    user = User.query.get(session.get('user'))

    if user.voted:
        return "You already voted"

    candidates = Candidate.query.all()
    return render_template("vote.html", candidates=candidates)

# Submit Vote
@app.route("/cast_vote/<int:id>")
def cast_vote(id):
    user = User.query.get(session.get('user'))

    if not user.voted:
        candidate = Candidate.query.get(id)
        candidate.votes += 1
        user.voted = True
        db.session.commit()

    return redirect("/vote")

# Admin Panel
@app.route("/admin")
def admin():
    candidates = Candidate.query.all()
    return render_template("admin.html", candidates=candidates)

# Live Chart Data
@app.route("/results_data")
def results_data():
    candidates = Candidate.query.all()
    return jsonify({
        c.name: c.votes for c in candidates
    })

if __name__ == "__main__":
    app.run(debug=True)
