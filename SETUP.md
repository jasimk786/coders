# AI Fake News Detector - Setup Guide

## Project Structure
- `backend/` - Flask API server
- `frontend/` - React web application

## Large Files Not Included
Due to GitHub file size limits, the following are excluded:
- `fine_tuned_bert/` - Pre-trained BERT model (download separately)
- `Fake.csv` and `Real.csv` - Training datasets (download separately)

## Setup Instructions

### Backend Setup
1. Navigate to backend folder: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with your configuration
4. Download the BERT model and place in `fine_tuned_bert/` folder
5. Run: `python app.py`

### Frontend Setup
1. Navigate to frontend folder: `cd frontend`
2. Install dependencies: `npm install`
3. Create `.env` file with API endpoint
4. Run: `npm run dev`

## Model and Data
- Download the fine-tuned BERT model from [your model source]
- Download datasets from [your data source]
- Place them in the appropriate folders as shown in the project structure