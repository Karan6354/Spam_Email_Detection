from flask import Flask, render_template, request
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
import string

ps = PorterStemmer()

nltk.download('stopwords')
nltk.download('punkt')

# Initialize the Flask app
app = Flask("app")

# Load the pre-trained SVM model (assumes the model has already been trained and saved)
model_path = 'model/spam_svm_model.pkl'
vectorizer_path = 'model/tfidf_vectorizer.pkl'

# Load the SVM model and the TfidfVectorizer
svm_model = pickle.load(open(model_path, 'rb'))
vectorizer = pickle.load(open(vectorizer_path, 'rb'))

# Preprocess Text
# * Lower case
# * Tokenization
# * Remove special characters
# * Remove stop words and punctuation
def preprocess_text(text):
    # Tokenize the text, convert to lowercase, and remove non-alphanumeric tokens
    tokens = [word for word in word_tokenize(text.lower()) if word.isalnum()]
    
    # Remove stopwords and punctuation
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words and word not in string.punctuation]

    # Apply stemming to each token
    # tokens = [ps.stem(word) for word in tokens]
    
    # Return the processed text as a string
    return " ".join(tokens)

# Define the route for the home page (the form)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the email text from the user input form
        email_text = request.form['email_text']

        processed_email_text = preprocess_text(email_text)
        
        # Vectorize the input text using the saved TfidfVectorizer
        email_vectorized = vectorizer.transform([processed_email_text]).toarray()
        
        # Predict whether the email is spam or not
        prediction = svm_model.predict(email_vectorized)
        
        # Display the result
        if prediction == 1:
            result = "Spam"
        else:
            result = "Not Spam"
        
        return render_template('index.html', result=result, email_text=email_text)

    return render_template('index.html', result=None)

if __name__ == "__main__":
    app.run()