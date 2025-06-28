from flask import Flask, render_template, request, redirect, url_for, session

from azure.storage.blob import BlobServiceClient
from msal import ConfidentialClientApplication

from io import BytesIO
from flask import send_file
import os

app = Flask(__name__)
app.secret_key = 'FlaskAppSecret_2'  # reemplazá por algo más seguro en producción

# 🔐 Configuración de Azure AD
TENANT_ID =  "bff06d89-48f9-41a6-b2e3-8910cfe1f722"
CLIENT_ID = "119bbec8-fcfb-44dd-a211-33ce892cbfe1"
CLIENT_SECRET = "lOT8Q~bYdojiEEEnWgi.F7dysdIzNgGktsKgtcUh"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "http://localhost:5000/getAToken"
SCOPE = ["User.Read"]

# Configuración Azure
AZURE_CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=principlescloudproject;AccountKey=9tzksc8EDnHh3QOQhBNq69Q76NmtEQ1g720VZBj492fvQOoj94gDzjGTXcgW+IoBPU9TlVz1ihSg+AStboHatQ==;EndpointSuffix=core.windows.net'
CONTAINER_NAME = 'uploads'
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)



# 🔐 MSAL client
msal_app = ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    blobs = container_client.list_blobs()
    files = [blob.name for blob in blobs]
    return render_template('home.html', files=files, user=session['user'])
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', user=session['user'])

@app.route('/perfil')
def perfil():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('perfil.html', user=session['user'])

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get("user"):
        return redirect(url_for("login"))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            blob_client = container_client.get_blob_client(file.filename)
            blob_client.upload_blob(file.read(), overwrite=True)
            return redirect(url_for('mydocuments'))
    return render_template('upload.html', user=session["user"]["name"])


@app.route("/login")
def login():
    auth_url = msal_app.get_authorization_request_url(SCOPE, redirect_uri=REDIRECT_URI)
    return redirect(auth_url)

@app.route("/getAToken")
def authorized():
    code = request.args.get('code')
    if not code:
        return "No se recibió el código de autorización.", 400
    result = msal_app.acquire_token_by_authorization_code(code, scopes=SCOPE, redirect_uri=REDIRECT_URI)

    if "id_token_claims" in result:
        session["user"] = {
            "name": result["id_token_claims"]["name"],
            "preferred_username": result["id_token_claims"]["preferred_username"]
        }
        return redirect(url_for("home"))  # 👈 Ahora va a /home
    return f"Login failed: {result.get('error_description')}", 400


@app.route("/logout")
def logout():
    session.clear()
    return redirect("https://login.microsoftonline.com/common/oauth2/v2.0/logout" +
                    "?post_logout_redirect_uri=http://localhost:5000/")



@app.route('/home')
def ahome():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', user=session['user'])

@app.route('/mydocuments')
def mydocuments():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        blobs_list = container_client.list_blobs()
        blobs = [blob.name for blob in blobs_list]
    except Exception as e:
        print(f"Error al obtener blobs: {e}")
        blobs = []

    return render_template('mydocuments.html', user=session['user'], blobs=blobs)


@app.route('/news')
def news():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('news.html', user=session['user'])

@app.route('/about')
def about():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('about.html', user=session['user'])


@app.route('/download/<path:blob_name>')
def download_blob(blob_name):
    if 'user' not in session:
        return redirect(url_for('login'))

    blob_client = container_client.get_blob_client(blob_name)
    stream = blob_client.download_blob()
    file_data = stream.readall()

    return send_file(BytesIO(file_data), 
                     download_name=blob_name.split('/')[-1], 
                     as_attachment=True)



if __name__ == '__main__':
    app.run(debug=True)
