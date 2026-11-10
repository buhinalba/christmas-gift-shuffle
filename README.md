# Christmas Gift Schuffle

Generic gift-exchange assignment application.

## Current implementation

- Generic assignment engine: N participants and exactly N-1 themes.
- Immutable domain entities and aggregate-wide validation.
- Repository interface independent of the database vendor.
- SQLite persistence with transactional writes and assignment uniqueness constraints.
- Application services for exchange creation and assignment generation.
- Streamlit organiser and participant-preview screens.

## Run locally

Python 3.11+:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pytest
streamlit run app.py
```

SQLite defaults to `data/christmas_gift_schuffle.db`. Override with `SQLITE_DATABASE_PATH`.

## Security warning

The current UI is a development preview only. The participant email selector is not authentication, and organiser access is not protected. Do not deploy publicly until Google OAuth, admin allowlisting and server-side authorisation are implemented.

## Architecture

- `domain`: entities, business rules and assignment strategies.
- `application`: use cases and repository interfaces.
- `infrastructure`: SQLite adapter and dependency wiring.
- `presentation/streamlit`: organiser and participant UI.

A Snowflake adapter can be added by implementing `GiftExchangeRepository`; domain and application layers should remain unchanged.
