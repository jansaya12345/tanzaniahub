from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from app.models import Job, Property, User
from app.forms import JobForm, PropertyForm, RegisterForm, LoginForm, EditProfileForm


# ----------------- 🟡 HOME ROUTE -----------------
@app.route('/')
def home():
    query = request.args.get('query')
    jobs = Job.query.filter(Job.title.ilike(f"%{query}%")).all() if query else Job.query.all()
    properties = Property.query.filter(Property.title.ilike(f"%{query}%")).all() if query else Property.query.all()
    return render_template('index.html', jobs=jobs, properties=properties)


# ----------------- 🟠 REGISTER ROUTE (FIXED) -----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already in use. Please log in.', 'danger')
            return redirect(url_for('login'))

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# ----------------- 🟠 LOGIN ROUTE (FIXED) -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Welcome back!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)


# ----------------- ✅ LOGOUT ROUTE -----------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


# ----------------- 🟡 POST JOB ROUTE -----------------
@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    form = JobForm()
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            company=form.company.data,
            location=form.location.data,
            description=form.description.data,
            salary=form.salary.data,
            user_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('post_job.html', form=form)


# ----------------- 🟡 POST PROPERTY ROUTE -----------------
@app.route('/post-property', methods=['GET', 'POST'])
@login_required
def post_property():
    form = PropertyForm()
    if form.validate_on_submit():
        property = Property(
            title=form.title.data,
            location=form.location.data,
            price=form.price.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(property)
        db.session.commit()
        flash('Property listed successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('post_property.html', form=form)


# ----------------- 🟠 PROFILE ROUTE (FIXED) -----------------
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))

    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio

    return render_template('profile.html', form=form)


# ----------------- 🟡 DASHBOARD ROUTE -----------------
@app.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    properties = Property.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', jobs=jobs, properties=properties)


# ----------------- 🚫 DELETE JOB ROUTE -----------------
@app.route('/delete-job/<int:job_id>', methods=['GET'])
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.user_id != current_user.id:
        flash("Permission denied!", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(job)
    db.session.commit()
    flash("Job deleted successfully.", "success")
    return redirect(url_for('dashboard'))


# ----------------- 🚫 DELETE PROPERTY ROUTE -----------------
@app.route('/delete-property/<int:property_id>', methods=['GET'])
@login_required
def delete_property(property_id):
    property = Property.query.get_or_404(property_id)
    if property.user_id != current_user.id:
        flash("Permission denied!", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(property)
    db.session.commit()
    flash("Property deleted successfully.", "success")
    return redirect(url_for('dashboard'))
