from flask import Flask

app = Flask(__name__)

# Default route to /
@app.route("/")
def home():
	print("Server received request for Home page")
	return "Welcome to Home Page"

# Route to static page
@app.route("/about")
def about():
	print("Server received request for About page")
	return "About me..."

if __name__ == "__main__":
	app.run(debug=True)