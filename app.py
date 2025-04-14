from flask import Flask, render_template, request, redirect, url_for, flash

@app.route('/dashboard/cloud-accounts')
def cloud_accounts():
    # You can add logic here to fetch existing cloud accounts from your database
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