# Deployment Guide: Pool Finder AI

Follow these steps to deploy your application to GitHub and Streamlit Cloud.

## 1. Push Code to GitHub

1.  **Initialize Git** (if not already done):
    ```bash
    git init
    ```
2.  **Add all files**:
    ```bash
    git add .
    ```
3.  **Create initial commit**:
    ```bash
    git commit -m "Initialize project and prepare for deployment"
    ```
4.  **Create a new repository** on GitHub (e.g., `gpool`).
5.  **Add the remote and push**:
    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/gpool.git
    git branch -M main
    git push -u origin main
    ```

## 2. Deploy to Streamlit Cloud

1.  Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2.  Click **"New app"**.
3.  Select your repository (`gpool`), the branch (`main`), and the main file (`app.py`).
4.  Before clicking "Deploy", click on **"Advanced settings..."**.

## 3. Configure Secrets

In the **Secrets** section of the advanced settings, paste your API keys from your `.env` file in the following format:

```toml
GOOGLE_MAPS_API_KEY = "your_google_maps_key_here"
GEMINI_API_KEY = "your_gemini_key_here"
```

5.  Click **"Save"** and then **"Deploy"**.

Your app should now be live!
