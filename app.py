from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os



app = Flask(__name__)


#Configuration de la base de données
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_wiew = 'login' # Page de redirection au cas où l'utilisateur n'est pas connécté


#Modèle pour les ustilisateurs
class User(db.Model) :
	id  = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100), nullable = False)
	age = db.Column(db.Integer, nullable = False)
	password = db.Column(db.String(50), nullable = False)


# Chargement de l'utilisateur
@login_manager.user_loader
def user_loader(user_id) :
	return User.query.get(int (user_id))

# Ici commence les routes

#Route d'accueil
@app.route('/')
def home():
	return render_template('index.html')
	
@app.route('/about')
def about():
	return "Bienvenu sur la page about !!"
	
@app.route('/contact')
def contact():
	return "Bienvenu sur la page contact !!"

@app.route('/user/<name>')
def user(name):
	return f" Bonjour ! Bienvenu à toi {name} !!"

@app.route('/profile/<name>/<int:age>')
def profile(name, age):
	return render_template('profile.html', name=name, age=age)


#Route pour le formulaire création d'utilisateur
@app.route('/form', methods=['GET', 'POST'])
def form():
	if request.method == 'POST' :
		name = request.form.get('name')
		age = request.form.get('age')
		# password = request.form.get('password')

		password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

		#Créer un nouvel utilisateur et l'ajouter à la base de données
		new_user = User(name=name, age=age, password=password)

		try :
			db.session.add(new_user)
			db.session.commit()

		
			#return f"Hey ! {name}, c'est un super age {age} ans."

			return redirect('/users') #redirection vers la liste de utilisateurs
		except :
			return f"Une erreur s'est produit lors de la création de l'utilisateur nom : { name } age : {age} mot de passe : { password }."

	return render_template('form.html')

# Route pour afficher les utilisateurs enregistrés
@app.route('/users')
def users():
	all_users = User.query.all() # Récupère tous les utilisateurs de la base
	return render_template('users.html', users=all_users)

# Route pour la supperssion de l'un des utilisateurs enregistrés
@app.route('/delete/<int:id>', methods = ['POST'])
def delete_user(id):
	user_to_delete = User.query.get_or_404(id) # Récupère l'utilisateur ou renvoie une erreur 404

	try :
		db.session.delete(user_to_delete)
		db.session.commit()
		return redirect('/users') # Redirection vers la liste des utilisateurs
	except:
		return f"Une erreur s'est produit lors de la suppression de l'utilisateurs portant l'id {id}"

# Route pour la modification d'un utilisateur
@app.route('/edit/<int:id>', methods = ['GET', 'POST'])
def edit_user(id):
	user = User.query.get_or_404(id) # Récupère l'utilisateur ou renvoie une erreur 404

	if request.method == 'POST' :
		user.name = request.form.get('name')
		user.age = request.form.get('age')
		
		#password = request.form.get('password')

		password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

		try :
			db.session.commit()
			return redirect('/users') # Redirection vers la liste des utilisateurs
		except:
			return "Une erreur s'est produit lors de la modification de l'utilisateur."

	return render_template('edit.html', user = user)


# Route pour la création des utilisateurs avec leur mot de passe crypté
@app.route('/register', methods = ['GET', 'POST'])
def register():

	# if request.method == 'POST' :
	# 	name = request.form.get('username')
	# 	age = request.form.get('age')
	# 	password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
		
	# 	new_user = User(name = username, age = age, password = password)
	# 	try :
	# 		db.session.add(new_user)
	# 		db.session.commit()
	# 		flash('Votre compte a été créé ! Vous pouvez maintenant vous connecter.', 'success')
	# 		return redirect(url_for('login'))
	# 	except : 
	# 		return f"Une erreur s'est produit lors de la création de votre compte {name} avec le mot de passe {password}."


	if request.method == 'POST' :
		name = request.form.get('name')
		age = request.form.get('age')
		
	# 	# password = request.form.get('password')

		password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')

	# 	Créer un nouvel utilisateur et l'ajouter à la base de données
		new_user = User(name=name, age=age, password=password)

		try :
	  	 	db.session.add(new_user)
	  	 	db.session.commit()
	  	 	# flash('Votre compte a été créé ! Vous pouvez maintenant vous connecter.', 'success')
	  	 	# return render_template('login.html')
	  	 	# return redirect('/login')
	  	 	return "Holla !!, register fait."
		except : 
			return f" C'est registre. Une erreur s'est produit lors de la création de votre compte {name} avec le mot de passe {password}."

	return render_template('register.html')


# Route pour la connexion des utilisateurs
@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST' :
		name = request.form.get('name')
		password = request.form.get('password')


		user = User.query.filter_by(name = name).first()

		if user and bcrypt.check_password_hash(user.password, password) :
			login_user(user)
			flash('Connexion réussie !', 'success')
			return redirect(url_for('dashboard'))
		else :
			return 'Echec de la connexion. Veuillez revérifier votre identifiant ou mot de passe.'
	return render_template('login.html')

# Route pour la déconnexion
@app.route('/logout')
@login_required
def logout() :
	logout_user()
	flash('Déconnexion réussie.', 'info')
	return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html', name=current_user.username)




if __name__ == '__main__' :

	# Crée la base de données si elle n'existe pas encore
	with app.app_context():
		db.create_all()
	
	#print("Démarrage du serveur Flask ... ")
	
	app.run(debug=True)