# AI Fake News Detector - Backend

This Flask backend provides endpoints for text fake news detection using a Hugging Face model.

Quick start

1. Create a virtual environment and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure `.env` with your `MONGO_URI` and `JWT_SECRET`.

4. Run the app:

```bash
python app.py
```

The server listens on port 5000 by default and allows CORS from http://localhost:5173.
