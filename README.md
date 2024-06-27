Result: https://www.google.com/maps/d/u/1/edit?mid=1h18uoyypzX_R0-Bb6yTLPtnoZGMZCzs&usp=sharing

# Run with Docker
## Create a volume
`docker volume create maasser-storage`

## Run
```
docker build -t scrap-kosher-rest .
docker run --mount type=bind,source="$(pwd)"/Storage,target=/app/Storage scrap-kosher-rest
```

# Run without Docker
`python3 app/scrap.py`
`python3 app/scrap_mikvaot.py`
`python3 app/scrap_synagogues.py`
`python3 app/scrap_tzohar.py`