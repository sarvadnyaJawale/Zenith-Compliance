from flask import Flask, render_template

app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend/templates")

@app.route("/")
def home():
    return render_template("home.html")  # Change this to your main HTML file

if __name__ == "__main__":
    app.run(debug=True)