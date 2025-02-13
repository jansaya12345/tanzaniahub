from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db  # Ensure app is imported first
from app.models import Job, Property, User
from app.forms import JobForm, PropertyForm, RegisterForm, LoginForm


# Home Route
from flask import request


from flask import render_template, request
from app import app, db
from app.models import Job, Property

@app.route('/')
def home():
    query = request.args.get('query')
    filter_type = request.args.get('filter_type')

    jobs = Job.query.filter(Job.title.contains(query) if query else True).all()
    properties = Property.query.filter(Property.title.contains(query) if query else True).all()

    return render_template('index.html', jobs=jobs, properties=properties)


    jobs = jobs_query.all()

    # Filter Properties based on search inputs
    properties_query = Property.query
    if search_query:
        properties_query = properties_query.filter(Property.title.ilike(f"%{search_query}%"))
    if filter_location:
        properties_query = properties_query.filter(Property.location.ilike(f"%{filter_location}%"))

    properties = properties_query.all()

    return render_template('index.html', jobs=jobs, properties=properties, search_query=search_query)


@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    form = JobForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to post a job.", "danger")
            return redirect(url_for("login"))

        new_job = Job(
            title=form.title.data,
            company=form.company.data,
            location=form.location.data,
            description=form.description.data,
            salary=form.salary.data,
            user_id=current_user.id  # 🔹 Assign logged-in user ID
        )
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('post_job.html', form=form)


# Route for posting a property (only for logged-in users)
from flask_login import current_user


@app.route('/post-property', methods=['GET', 'POST'])
@login_required
def post_property():
    form = PropertyForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to post a property.", "danger")
            return redirect(url_for("login"))

        new_property = Property(
            title=form.title.data,
            location=form.location.data,
            price=form.price.data,
            description=form.description.data,
            user_id=current_user.id  # 🔹 Assign logged-in user ID
        )
        db.session.add(new_property)
        db.session.commit()
        flash('Property posted successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('post_property.html', form=form)


# User Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('login'))

        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# User Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check email and password.', 'danger')

    return render_template('login.html', form=form)


# User Logout Route
from flask import redirect, url_for, flash
from flask_login import logout_user

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))  # 🔹 Ensure it redirects to home

@app.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    properties = Property.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', jobs=jobs, properties=properties)


@app.route('/delete-job/<int:job_id>', methods=['GET'])
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.user_id != current_user.id:
        flash("You don't have permission to delete this job!", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(job)
    db.session.commit()
    flash("Job deleted successfully!", "success")
    return redirect(url_for('dashboard'))


@app.route('/delete-property/<int:property_id>', methods=['GET'])
@login_required
def delete_property(property_id):
    property = Property.query.get_or_404(property_id)
    if property.user_id != current_user.id:
        flash("You don't have permission to delete this property!", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(property)
    db.session.commit()
    flash("Property deleted successfully!", "success")
    return redirect(url_for('dashboard'))
