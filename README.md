# Shiva Draft Intelligence

Upload every file in this folder to the root of a GitHub repository.

## Deploy with Streamlit Community Cloud
1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, `shiva_draft_roi.sqlite`, `.gitignore`, and the `.streamlit` folder.
3. In Streamlit Community Cloud, create a new app from the repository.
4. Set the main file path to `app.py`.
5. Deploy.

## Local test
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Add to phone home screen
Open the deployed app in Safari or Chrome and choose **Add to Home Screen**.
