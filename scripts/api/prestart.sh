#!/bin/bash

# Let the DB start
python -m src.scripts.wait-for-db

# Run the migrations
alembic upgrade head
