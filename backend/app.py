from flask import Flask, render_template, url_for

app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend/templates")

@app.route('/')
def landing():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/sign-in')
def sign_in():
    return render_template('sign-in.html')

@app.route('/sign-up')
def sign_up():
    return render_template('sign-up.html')

@app.route('/features')
def features():
    return render_template('features.html')

# New pages (placeholder: home.html until real templates are built)
@app.route('/about')
def about():
    return render_template('about-us.html')

@app.route('/pricing')
def pricing():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact-us.html')

@app.route('/blog')
def blog():
    return render_template('home.html')

@app.route('/integrations')
def integrations():
    return render_template('home.html')

@app.route('/careers')
def careers():
    return render_template('home.html')

@app.route('/team')
def team():
    return render_template('home.html')

# Utility pages
@app.route('/reset-password')
def reset_password():
    return render_template('home.html')

@app.route('/custom-404')
def custom_404():
    return render_template('home.html')

@app.route('/terms-of-use')
def terms_of_use():
    return render_template('home.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('home.html')

@app.route('/style-guide')
def style_guide():
    return render_template('home.html')

@app.route('/licenses')
def licenses():
    return render_template('home.html')

@app.route('/change_log')
def change_log():
    return render_template('home.html')

@app.route('/utility-pages/sign-in')
def utility_sign_in():
    return render_template('sign-in.html')


if __name__ == "__main__":
    app.run(debug=True)
