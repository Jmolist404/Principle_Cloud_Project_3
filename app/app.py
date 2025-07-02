from flask import Flask, render_template, request, redirect, url_for, session, send_file
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from msal import ConfidentialClientApplication
from datetime import datetime, timedelta
from io import BytesIO
from urllib.parse import quote


import logging

logging.basicConfig(level=logging.DEBUG)

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled Exception: {e}")
    return "Internal Server Error", 500

app = Flask(__name__)
app.secret_key = 'FlaskAppSecret_2'

# Azure AD auth
TENANT_ID = "bff06d89-48f9-41a6-b2e3-8910cfe1f722"
CLIENT_ID = "119bbec8-fcfb-44dd-a211-33ce892cbfe1"
CLIENT_SECRET = "lOT8Q~bYdojiEEEnWgi.F7dysdIzNgGktsKgtcUh"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "https://myappservice1234-jmb.azurewebsites.net/getAToken"
SCOPE = ["User.Read"]

# Key Vault
VAULT_URL = "https://pcloudkeyvaluejm25.vault.azure.net/"
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=VAULT_URL, credential=credential)

# Blob Storage
AZURE_CONNECTION_STRING = secret_client.get_secret("AzureBlobConnectionString").value
CONTAINER_NAME = 'uploads'
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# MSAL
msal_app = ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
)

def get_blob_url_with_sas(blob_name):
    blob_name = blob_name.strip()
    if not blob_name:
        raise ValueError("blob_name vacío después de strip()")

    account_name = blob_service_client.account_name
    account_key = secret_client.get_secret("AzureBlobAccountKey").value


    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=CONTAINER_NAME,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(days=1)
    )

    encoded_blob_name = quote(blob_name, safe='')
    return f"https://{account_name}.blob.core.windows.net/{CONTAINER_NAME}/{encoded_blob_name}?{sas_token}"

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))

    files = []
    blobs_list = container_client.list_blobs()
    for blob in blobs_list:
        blob_name = blob.name.strip()
        if not blob_name:
            continue
        print(f"📄 Procesando: '{blob_name}'")  
        sas_url = get_blob_url_with_sas(blob_name)
        files.append({'name': blob_name, 'url': sas_url})
    return render_template('home.html', user=session['user'], files=files)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for("login"))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            blob_name = file.filename.strip()
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(file.read(), overwrite=True)
            return redirect(url_for('home'))

    return render_template('upload.html', user=session['user'])


@app.route('/download/<path:blob_name>')
def download_blob(blob_name):
    if 'user' not in session:
        return redirect(url_for('login'))

    blob_name = blob_name.strip()
    blob_client = container_client.get_blob_client(blob_name)
    stream = blob_client.download_blob()
    file_data = stream.readall()

    # Detecta tipo por extensión
    extension = blob_name.lower().split('.')[-1]
    image_extensions = ['jpg', 'jpeg', 'png', 'gif']

    if extension in image_extensions:
        # Mostrar en navegador
        mimetype = f"image/{'jpeg' if extension in ['jpg', 'jpeg'] else extension}"
        return send_file(BytesIO(file_data),
                         mimetype=mimetype,
                         download_name=blob_name,
                         as_attachment=False)
    else:
        # Descargar como archivo
        return send_file(BytesIO(file_data),
                         download_name=blob_name,
                         as_attachment=True)

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
        return redirect(url_for("home"))
    return f"Login failed: {result.get('error_description')}", 400

@app.route("/logout")
def logout():
    session.clear()
    return redirect("https://login.microsoftonline.com/common/oauth2/v2.0/logout" +
                "?post_logout_redirect_uri=https://myappservice1234-jmb.azurewebsites.net/")

@app.route('/mydocuments')
def mydocuments():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        blobs_list = container_client.list_blobs()
        blobs = [blob.name.strip() for blob in blobs_list if blob.name.strip()]
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

if __name__ == '__main__':
    app.run(debug=True)
