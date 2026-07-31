# Astra Study frontend

The Streamlit workspace uses the FastAPI application at `http://127.0.0.1:8000/api/v1` by default.

```powershell
uv run uvicorn app.main:app --reload
uv run python -m streamlit run frontend/app.py
```

Set `ASTRA_API_URL` to use a different API base URL.
