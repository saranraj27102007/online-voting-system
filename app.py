from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "adminsecret"

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ======================
# Database Models
# ======================

class Voter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.String(50), unique=True)
    voted = db.Column(db.Boolean, default=False)


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    votes = db.Column(db.Integer, default=0)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))


# ======================
# Create Database
# ======================

with app.app_context():
    db.create_all()

    # Default Candidates
    if Candidate.query.count() == 0:
        db.session.add(Candidate(name="Candidate A"))
        db.session.add(Candidate(name="Candidate B"))
        db.session.add(Candidate(name="Candidate C"))
        db.session.commit()

    # Default Admin
    if Admin.query.count() == 0:
        db.session.add(Admin(username="admin", password="admin123"))
        db.session.commit()

    # Default Voters
    if Voter.query.count() == 0:
        voters = ["V001", "V002", "V003", "V004"]
        for v in voters:
            db.session.add(Voter(voter_id=v))
        db.session.commit()


# ======================
# Home Page
# ======================

@app.route("/")
def home():
    return render_template("index.html")


# ======================
# Voter Page
# ======================

@app.route("/vote", methods=["GET", "POST"])
def vote():

    if request.method == "POST":

        voter_id = request.form["voter_id"]
        candidate_id = request.form["candidate"]

        voter = Voter.query.filter_by(voter_id=voter_id).first()

        if not voter:
            return "Invalid Voter ID"

        if voter.voted:
            return "You already voted!"

        candidate = Candidate.query.get(candidate_id)
        candidate.votes += 1
        voter.voted = True

        db.session.commit()

        return redirect("/success")

    candidates = Candidate.query.all()
    return render_template("vote.html", candidates=candidates)


# ======================
# Success Page
# ======================

@app.route("/success")
def success():
    return render_template("success.html")


# ======================
# Admin Login
# ======================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username, password=password).first()

        if admin:
            session["admin"] = username
            return redirect("/dashboard")

        return "Invalid Admin Login"

    return render_template("admin_login.html")


# ======================
# Admin Dashboard
# ======================

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/admin")

    candidates = Candidate.query.all()
    return render_template("dashboard.html", candidates=candidates)


# ======================
# Admin Logout
# ======================

@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin")


# ======================
# Run App
# ======================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)



