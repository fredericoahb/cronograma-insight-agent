up:
	docker compose up --build

down:
	docker compose down

backend:
	uvicorn backend.app:app --reload --port 8000

frontend:
	streamlit run frontend/app.py --server.port 8501
