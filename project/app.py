from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

# ---------------- DATABASE CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="_@Anushree09",
    database="narrateit"
)
cursor = db.cursor()

# ---------------- GLOBAL USER ----------------
current_user_id = None

# ---------------- VADER SENTIMENT ANALYZER ----------------
analyzer = SentimentIntensityAnalyzer()

# ---------------- LOGIN PAGE ----------------
@app.route('/')
def login_page():
    return render_template("login.html")

# ---------------- REGISTER PAGE ----------------
@app.route('/register')
def register_page():
    return render_template("register.html")

# ---------------- SIGNUP ----------------
@app.route('/register_user', methods=['POST'])
def register_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        return "Passwords do not match"

    sql = "INSERT INTO signup (name,email,password) VALUES (%s,%s,%s)"
    cursor.execute(sql, (name,email,password))
    db.commit()

    return "Signup Successful. <a href='/'>Login Here</a>"

# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():
    global current_user_id
    email = request.form.get('email')
    password = request.form.get('password')

    sql = "SELECT * FROM signup WHERE email=%s AND password=%s"
    cursor.execute(sql, (email,password))
    user = cursor.fetchone()

    if user:
        current_user_id = user[0]
        return redirect(url_for('images'))  # go to image gallery
    else:
        return "Invalid Email or Password"

# ---------------- IMAGE GALLERY PAGE ----------------
@app.route('/images')
def images():
    # List of images in your 'static' folder
    image_list = ['img1.jpg', 'img2.jpg', 'img3.jpg', 'img4.jpg']
    return render_template("image.html", images=image_list)

# ---------------- TEXTBOX PAGE ----------------
@app.route('/textbox')
def textbox():
    # Get selected image from query parameters
    image_filename = request.args.get('image_filename')
    return render_template("textbox.html", image_filename=image_filename)

# ---------------- SUBMIT STORY ----------------
@app.route('/submit_story', methods=['POST'])
def submit_story():
    story = request.form['story_text']
    image_filename = request.form['image_filename']

    # Analyze sentiment using VADER
    score = analyzer.polarity_scores(story)
    compound = score['compound']

    if compound > 0:
        sentiment = "Positive"
    elif compound < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    # Store story + sentiment + image in database
    sql = "INSERT INTO story (user_id, story_text, sentiment, image_filename) VALUES (%s,%s,%s,%s)"
    cursor.execute(sql, (current_user_id, story, sentiment, image_filename))
    db.commit()

    # Show result page
    return render_template("result.html",
                           story=story,
                           sentiment=sentiment,
                           positive=score['pos'],
                           negative=score['neg'],
                           neutral=score['neu'],
                           image_filename=image_filename)

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)