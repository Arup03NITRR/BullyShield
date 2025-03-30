from flask import Flask, render_template, request
import numpy as np
import pickle
import smtplib
import ssl
from email.message import EmailMessage
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string

app = Flask(__name__)

# Load models
with open('./saved_models/tfidf.pkl', 'rb') as file:
    tfidf = pickle.load(file)

with open('./saved_models/rf_clf.pkl', 'rb') as file:
    rf_clf = pickle.load(file)

# Email function
def send_email(subject, body):
    email_sender = "bullyshield30@gmail.com"
    email_password = "qejs dljx gnns oosf"
    email_receiver = "arup.paul.sbhs@gmail.com"

    em = EmailMessage()
    em.set_content(body)
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(em)

# Cyberbullying Level Detection
def get_type(data):
    levels = {
        1: "level 1",
        2: "level 2",
        3: "level 3",
        4: "level 4",
        5: "level 5"
    }
    return levels.get(data, "Not bullied")

def encourage(label):
    encouragements = {
        "level 1": "Age is just a number. Celebrate your uniqueness!",
        "level 2": "Express your true identity with confidence.",
        "level 3": "Your beliefs are valuable and deserve respect.",
        "level 4": "Stay strong—this challenge will pass.",
        "level 5": "Your cultural heritage is a source of strength.",
    }
    return encouragements.get(label, "Don't be a bully!")

# Prediction Function
nltk.download('stopwords')
nltk.download('punkt')

def text_preprocessing(text):
    text = text.lower().translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    tokens = word_tokenize(text.strip())  # Tokenization with whitespace cleanup
    stop_words = set(stopwords.words('english'))
    tokens = [x for x in tokens if x not in stop_words]  # Remove stopwords
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(x) for x in tokens]  # Stemming
    return ' '.join(tokens)

def prediction(text):
    text = text_preprocessing(text)
    print(text)
    transformed_text = tfidf.transform([text])
    result = rf_clf.predict(transformed_text)[0]
    return get_type(int(result))  # Ensure it's an integer before using it in the dictionary lookup

# Flask Routes
@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    message = None
    
    if request.method == "POST":
        val = request.form["text"]
        result = prediction(val)
        
        if result in ["level 3", "level 5"]:  # Fix: Direct comparison with string values
            subject = f"Discrimination Alert: {result}"
            message = "Cybercrime Branch has been notified!"
            send_email(subject, "User is facing discrimination.")
    
    return render_template("index.html", result=result, message=message)

if __name__ == '__main__':
    app.run(debug=True)