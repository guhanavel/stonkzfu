from stonk import init_app
from redis import Redis

app = init_app()
redis = Redis(host='redis', port=6379)

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
