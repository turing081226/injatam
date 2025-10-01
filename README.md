# 부여 시장 맞춤 안내

Streamlit 기반 시장 탐색/추천/경로 안내 데모 앱.

## 로컬 실행

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export GEMINI_API_KEY="YOUR_KEY"  # Windows: set GEMINI_API_KEY=...
streamlit run app.py
