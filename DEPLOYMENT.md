# Deployment Guide: Pool Finder AI

Follow these steps to deploy your application to GitHub and Streamlit Cloud.

## 1. Code is on GitHub

The code has already been pushed to your public repository:
[https://github.com/benjpy/152_gpool](https://github.com/benjpy/152_gpool)

You can skip any local Git setup for now unless you want to make further changes.

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
