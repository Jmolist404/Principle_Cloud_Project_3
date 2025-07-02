# Document Portal

**Document Portal** is a secure, cloud-based web application designed to help users organize, access, and manage their personal documents from anywhere. Built with Flask and powered by Microsoft Azure services, this platform ensures that sensitive information is stored safely and is always within reach.

---

## Key Highlights

- **Secure Microsoft Authentication**  
  Users sign in using their Microsoft accounts via MSAL, ensuring identity protection and seamless session management.

- **Cloud Document Storage**  
  Documents are uploaded directly to Azure Blob Storage and can be downloaded anytime with just a click.

- **Organized File Management**  
  A user-friendly interface makes it easy to view, upload, download, and manage files. Uploads support multiple formats and organize files in one place.

- **Mobile-Friendly Design**  
  The portal is fully responsive, working across desktops, tablets, and smartphones.

- **Document Sharing (Planned)**  
  Users will be able to generate secure, time-limited links to share files with institutions or trusted individuals.

- **OCR and Tagging Features (Coming Soon)**  
  Integrated OCR will allow scanning and text recognition to improve document search and metadata extraction.

---

## Project Structure

```
Principle_Cloud_Project_3/
├── App/ 
├─── static/                  # CSS, images, and JS files
├─── templates/               # HTML templates (Jinja2)
│   ├── about.html
│   ├── home.html
│   ├── mydocuments.html
│   └── news.html
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├─── pipelines/
├   ├── azure-pipelines.yml
│   ├── terraform-pipline.yml 
├─── terraform/  
│   ├── app_services.tf
│   ├── provider.tf
│   ├── resource_group.tf
│   └── storage_account.tf     
```

---

## Technologies Used

- **Backend:** Python 3.x, Flask
- **Cloud Services:** Azure Blob Storage, Azure Key Vault, Azure Active Directory (MSAL)
- **Frontend:** HTML5, CSS3, Jinja2 Templates
- **Security:** OAuth2 Authorization, Encrypted Key Vault secrets

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Jmolist404/Principle_Cloud_Project_3.git
cd document-portal
```

### 2. Create a virtual environment (Recomendation)

```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Azure Resources

Before running the app, ensure you have:
- An Azure **Blob Storage** account with a container named `uploads`
- An **Azure Key Vault** with a secret `AzureBlobConnectionString`
- A registered **Azure App (Azure AD)** with:
  - Client ID
  - Tenant ID
  - Client Secret

These values must be updated in `app.py`:
```python
TENANT_ID = "your-tenant-id"
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"
VAULT_URL = "https://your-keyvault-name.vault.azure.net/"
```

### 5. Start the Flask app

```bash
python app.py
```

The app will be available at [http://localhost:5000](http://localhost:5000)

---

## Main Pages

- **Homepage (`/home`)**: Displays a welcome message and a table of available uploaded documents.
- **Upload (`/mydocuments`)**: Simple file upload interface with POST request to `/upload`.
- **Download (`/download/<blob_name>`)**: Downloads the selected file from Azure Blob.
- **About (`/about`)**: Explains key features of the portal.
- **News (`/news`)**: Displays articles and tips related to document security and updates.

---

## Security Notes

- All routes require the user to be logged in via Microsoft (session-based).
- Secrets are retrieved at runtime from Azure Key Vault via `DefaultAzureCredential`.
- Files are stored in Azure Blob with server-side encryption and access controls.

---

## Contact Information

If you have any issues, ideas, or just want to reach out:

- 📧 Email: [support@documentportal.com](mailto:support@documentportal.com)  
- 📞 Phone: +1 (555) 123-4567  
- 🏢 Address: 456 Civic Center Plaza, Suite 200, San Francisco, CA 94102

---

© 2025 Document Portal — Built with care using Flask and Azure.
