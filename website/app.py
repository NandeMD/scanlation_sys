from website import create_app
from config import get_api_ip

if __name__ == "__main__":
    print(f"API IP set to: {get_api_ip()}")

    app = create_app()
    app.run(debug=True)
