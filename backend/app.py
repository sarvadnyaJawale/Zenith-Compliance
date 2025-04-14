from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend/templates")
app.secret_key = 'your_secret_key_here'  # Add this line after creating the Flask app

@app.route('/')
def landing():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/profile')
def profile():
    return render_template('Dashboard/profile.html')

@app.route("/")
def index():
    return render_template("Dashboard/index.html")

@app.route("/404")
def error_404():
    return render_template("Dashboard/404.html")

@app.route("/alerts")
def alerts():
    return render_template("Dashboard/alerts.html")

@app.route("/avatars")
def avatars():
    return render_template("Dashboard/avatars.html")

@app.route("/badge")
def badge():
    return render_template("Dashboard/badge.html")

@app.route("/bar-chart")
def bar_chart():
    return render_template("Dashboard/bar-chart.html")

@app.route("/basic-tables")
def basic_tables():
    return render_template("Dashboard/basic-tables.html")

@app.route("/blank")
def blank():
    return render_template("Dashboard/blank.html")

@app.route("/buttons")
def buttons():
    return render_template("Dashboard/buttons.html")

@app.route("/calendar")
def calendar():
    return render_template("Dashboard/calendar.html")

@app.route("/form-elements")
def form_elements():
    return render_template("Dashboard/form-elements.html")

@app.route("/images")
def images():
    return render_template("Dashboard/images.html")

@app.route("/line-chart")
def line_chart():
    return render_template("Dashboard/line-chart.html")

@app.route("/sidebar")
def sidebar():
    return render_template("Dashboard/sidebar.html")

@app.route("/signin")
def signin():
    return render_template("Dashboard/signin.html")

@app.route("/signup")
def signup():
    return render_template("Dashboard/signup.html")

@app.route("/videos")
def videos():
    return render_template("Dashboard/videos.html")

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

@app.route('/cloud_accounts')
def cloud_accounts():
    return render_template('Dashboard/cloud-accounts.html')

@app.route('/dashboard/add-cloud-account')
def add_cloud_account():
    return render_template('Dashboard/add-cloud-account.html')

@app.route('/dashboard/add-cloud-account', methods=['POST'])
def add_cloud_account_submit():
    # Get form data
    access_key = request.form.get('access_key')
    secret_key = request.form.get('secret_key')
    region = request.form.get('region')
    alias = request.form.get('alias')
    
    # Here you would add code to save this information to your database
    # For example with SQLAlchemy:
    # new_account = CloudAccount(access_key=access_key, secret_key=secret_key, region=region, alias=alias)
    # db.session.add(new_account)
    # db.session.commit()
    
    # Redirect back to the cloud accounts page with a success message
    flash('Cloud account added successfully!', 'success')
    return redirect(url_for('cloud_accounts'))

@app.route('/pricing')
def pricing():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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
