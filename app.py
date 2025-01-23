from flask import Flask, render_template, request, redirect, url_for, flash
import os
import ibm_db
import hashlib
import secrets
from ibm_watsonx_ai import Credentials, APIClient
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ibm import WatsonxEmbeddings
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from langchain_ibm import WatsonxLLM
import jsonify

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# IBM Db2 Connection string
db2_connection_string = "DATABASE=bludb;HOSTNAME=0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31198;PROTOCOL=TCPIP;UID=qsj67798;PWD=LKc0qT2omrUoA6qm;SECURITY=SSL"

# WatsonX credentials
credentials = Credentials(
    url="https://us-south.ml.cloud.ibm.com",
    api_key="wUumZ-raqvUZ-a5J2rOBTlkWFv7YNpnNFJyanU55e0GB",
)
project_id = os.getenv("97ea408b-8fee-4927-86e3-13fdc670ee98","f18352f9-2746-4cc6-b3c8-8025ac2377bb")
api_client = APIClient(credentials=credentials, project_id=project_id)

# Initialize Watsonx embeddings
embeddings = WatsonxEmbeddings(
    model_id="ibm/slate-30m-english-rtrvr",
    url=credentials.url,
    apikey=credentials.api_key,
    project_id=project_id,
)

# Initialize Granite model
parameters = {
    GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.MAX_NEW_TOKENS: 100,
    GenParams.STOP_SEQUENCES: ["<|endoftext|>"]
}
model_id = "ibm/granite-3-8b-instruct"
watsonx_granite = WatsonxLLM(
    model_id=model_id,
    url=credentials.url,
    apikey=credentials.api_key,
    project_id=project_id,
    params=parameters
)
chat_history = []
qa = None
# Route for displaying the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get the user inputs from the signup form
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hash the password
        
        # Create connection to Db2
        conn = ibm_db.connect(db2_connection_string, '', '')
        if conn:
            # Check if the username already exists
            check_sql = f"SELECT * FROM Users WHERE Username = ?"
            stmt = ibm_db.prepare(conn, check_sql)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.execute(stmt)
            result = ibm_db.fetch_assoc(stmt)
            
            if result:
                flash("Username already exists!", "danger")
                return redirect(url_for('signup'))

            # Insert new user into the User table
            insert_sql = f"INSERT INTO Users (username, passw) VALUES (?, ?)"
            stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.bind_param(stmt, 2, hashed_password)
            ibm_db.execute(stmt)

            
            return redirect(url_for('login'))
        else:
            flash("Database connection failed!", "danger")
            return redirect(url_for('signup'))

    return render_template('signup.html')

usname = " "
# Route for displaying the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the user inputs from the login form
        global usname 
        usname = request.form['username']
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hash the password
        
        # Create connection to Db2
        conn = ibm_db.connect(db2_connection_string, '', '')
        if conn:
            # Check if the username and password match
            check_sql = f"SELECT * FROM Users WHERE username = ? AND passw = ?"
            stmt = ibm_db.prepare(conn, check_sql)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.bind_param(stmt, 2, hashed_password)
            ibm_db.execute(stmt)
            result = ibm_db.fetch_assoc(stmt)
            
            if result:
                flash("Login successful!", "success")
                return redirect(url_for('main'))  # Redirect to a dashboard or home page
            else:
                flash("Invalid username or password!", "danger")
                return redirect(url_for('login'))
        else:
            flash("Database connection failed!", "danger")
            return redirect(url_for('login'))
    
    return render_template('login.html')


# Route for the dashboard or home page after login
@app.route('/')
def initial():
    
    return render_template('welcome.html')

@app.route('/main')
def main():
    user_details = {
        "username": usname  # Replace with actual session data
    }
    return render_template('main.html', user=user_details)

@app.route('/dashboard')
def dashboard():
    user_details = {
        "username": usname  # Replace with actual session data
    }
    return render_template('dashboard.html',user=user_details)


@app.route('/report')
def report():
    return render_template('report.html')

@app.route("/chat")
def chat():
    return render_template('chat.html')

@app.route('/process', methods=['POST'])
def process_file():
    """Handle file upload and query."""
    if 'file' not in request.files:
        return render_template('result.html', error="No file part in the request")

    file = request.files['file']

    if not file or file.filename == '':
        return render_template('result.html', error="No file selected")

    if not (file.filename.endswith('.pdf') or file.filename.endswith('.txt')):
        return render_template('result.html', error="Unsupported file type. Please upload a .pdf or .txt file.")

    # Read file content
    text = ""
    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    elif file.filename.endswith('.txt'):
        text = file.read().decode('utf-8')

    # Process text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=0)
    texts = text_splitter.split_text(text)
    documents = [Document(page_content=chunk) for chunk in texts]

    # Create a vector store
    docsearch = Chroma.from_documents(documents, embeddings)

    # Build RetrievalQA
    qa = RetrievalQA.from_chain_type(
        llm=watsonx_granite,
        chain_type="stuff",
        retriever=docsearch.as_retriever()
    )

    # Query from user input
    query = request.form.get('query', "Default query?")
    response = qa.invoke(query)

    # Extract the results field from the response
    if isinstance(response, dict) and 'result' in response:
        answer_text = response['result']
    else:
        answer_text = "No results found or invalid response format."

    # Return the answer text as plain text
    return render_template('result.html', response=answer_text)


if __name__ == '__main__':
    app.run(debug=True)

