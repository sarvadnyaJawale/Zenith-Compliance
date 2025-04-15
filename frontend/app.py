@app.route('/dashboard/run-scan')
@login_required
def run_scan():
    return render_template('Dashboard/run-scan.html')