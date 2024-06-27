from flask import Blueprint, render_template, request, jsonify
import requests
frontend_blueprint = Blueprint('frontend', __name__)

def fetch_data():
    builds = requests.get('http://pokebuild-backend:5000/api/builds/').json()
    pokemons = requests.get('http://pokebuild-backend:5000/api/pokemons/').json()
    return builds, pokemons

def get_pokemon_id(build):
    return [
        build.get(f'pokemon_id_{j+1}', -1) if build.get(f'pokemon_id_{j+1}') is not None else -1
        for j in range(6)
    ]

def get_pokedex_id(pokemon_list, pokemons):
    pokedex_id_list = []

    for pokemon_id in pokemon_list:
        if pokemon_id == -1 or pokemon_id - 1 >= len(pokemons):
            pokedex_id_list.append('000')
        else:
            for pokemon in pokemons:
                if pokemon['id'] == pokemon_id:
                    pokedex_id_list.append(str(pokemon['pokedex_id']).zfill(3))
                    break

    return pokedex_id_list

def get_build_dict(builds, pokemons):
    build_dict = {}
    for build in builds:
        result = get_pokedex_id(get_pokemon_id(build), pokemons)
        build_row = {
            'owner_id': build['owner_id'],
            'build_name': build['build_name'],
            'timestamp': build['timestamp']
        }
        for j in range(6):
            build_row[f'pokemon_id_{j+1}'] = result[j]
        build_dict[build['id']] = build_row

    return build_dict

def get_user_builds(user_id):
    user_builds=requests.get(f'http://pokebuild-backend:5000/api/builds_by_user/{user_id}').json()
    builds_dict = []

    if isinstance(user_builds, dict):
        user_builds = [user_builds]

    for build in user_builds:
        build_row = {
            'id': build['id'],
            'build_name': build['build_name'],
            'pokemon_id_1': build['pokemon_id_1'],
            'pokemon_id_2': build['pokemon_id_2'],
            'pokemon_id_3': build['pokemon_id_3'],
            'pokemon_id_4': build['pokemon_id_4'],
            'pokemon_id_5': build['pokemon_id_5'],
            'pokemon_id_6': build['pokemon_id_6'],
            'timestamp': build['timestamp']
        }
        builds_dict.append(build_row)
    return builds_dict

def get_user_name(user_id):
    user_data = requests.get(f'http://pokebuild-backend:5000/api/user_profile/{user_id}/')
    try:
        user_data = user_data.json()
    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Response content: {user_data.content}")
        raise
    return user_data['username']

def get_user_profile_picture(user_id):
    user_data = requests.get(f'http://pokebuild-backend:5000/api/user_profile/{user_id}/')
    try:
        user_data = user_data.json()
    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Response content: {user_data.content}")
        raise
    return user_data['profile_picture']

@frontend_blueprint.route('/')
@frontend_blueprint.route('/home', strict_slashes=False)
def index():
    builds, pokemons = fetch_data()
    build_dict = get_build_dict(builds, pokemons)
    return render_template('home.html', build_dict=build_dict)

@frontend_blueprint.route('/pop-up-test')
def pop_up_test():
    return render_template('pop-up-test.html')

@frontend_blueprint.route('/build_list_container', strict_slashes=False)
def build_list_container():
    return render_template("build_list_container.html")

@frontend_blueprint.route('/login_register', strict_slashes=False)
def login_register():
    return render_template('login_register.html')

def get_pokemon_name_by_id(pokedex_id):
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokedex_id}')
    if response.status_code == 200:
        pokemon_data = response.json()  # Aquí se corrige el uso de json()
        return pokemon_data['name']
    else:
        return None

def get_user_pokemons(user_id):
    user_pokemons=requests.get(f'http://pokebuild-backend:5000/api/pokemons_by_user/{user_id}').json()
    if isinstance(user_pokemons, dict): #Cuando es solo un unico pokemon, en vez de devolverlo como una lista, lo devuelve como un diccionario y ocurre un error con el for.
        user_pokemons = [user_pokemons]
    pokemons_dict = []
    for pokemon in user_pokemons:
        especie_pokemon= get_pokemon_name_by_id(pokemon['pokedex_id'])
        build_row = {
            'name': pokemon['name'],
            'id': pokemon['id'],
            'pokedex_id': pokemon['pokedex_id'],
            'especie': especie_pokemon,
            'level': pokemon['level'],
            'ability_1': pokemon['ability_1'],
            'ability_2': pokemon['ability_2'],
            'ability_3': pokemon['ability_3'],
            'ability_4':pokemon['ability_4']
        }
        pokemons_dict.append(build_row)
    return pokemons_dict

@frontend_blueprint.route('/modify_pokemon_form/<owner_id>', strict_slashes=False)
def formulario_modificar_pokemon(owner_id):
    pokemons = requests.get("http://localhost:5000/api/get_all_pokemons").json()
    user_pokemons = get_user_pokemons(owner_id)
    if request.method == "POST":
        return render_template("home.html")
    return render_template('formulario_modificar_pokemon.html', pokemons=pokemons['pokemons'], owner_id=owner_id, user_pokemons=user_pokemons)


@frontend_blueprint.route('/add_build_form/<owner_id>', methods = ['GET', 'POST'], strict_slashes=False)
def pokemon_container(owner_id): # cambiar user id cuando este el auth
    pokemons_dic = get_user_pokemons(owner_id)
    return render_template('add_build_form.html', pokemons=pokemons_dic, owner_id=owner_id)  

@frontend_blueprint.route('/modify_build_form/<owner_id>', methods = ['GET', 'POST'], strict_slashes=False)
def sasa(owner_id): # cambiar user id cuando este el auth
    pokemons_dic = get_user_pokemons(owner_id)
    builds_dic=get_user_builds(owner_id)
    return render_template('modify_build_form.html', pokemons=pokemons_dic, builds = builds_dic, owner_id=owner_id) 

@frontend_blueprint.route('/delete_pokemon_form/<owner_id>', strict_slashes=False)
def delete_pokemon(owner_id):
    if request.method == 'POST':
        return render_template('home.html') #tiene que ser cambiado a profile
    user_pokemons=requests.get(f'http://pokebuild-backend:5000/api/pokemons_by_user/{owner_id}').json()
    if isinstance(user_pokemons, dict):
        user_pokemons = [user_pokemons]
    pokemons_dict = []
    for pokemon in user_pokemons:
        build_row = {
            'name': pokemon['name'],
            'id': pokemon['id']
        }
        pokemons_dict.append(build_row)
    return render_template('delete_pokemon.html', pokemons=pokemons_dict, owner_id=owner_id)

@frontend_blueprint.route('/add_pokemon_form/<owner_id>', methods=["POST", "GET"], strict_slashes=False) #Hasta que este el POST endpoint de pokemon, tiene esto.
def add_pokemon_form(owner_id):
    pokemons = requests.get("http://localhost:5000/api/get_all_pokemons").json()
    if request.method == "POST":
        return render_template("home.html")
    return render_template('add_pokemon_form.html', pokemons=pokemons['pokemons'], owner_id=owner_id)

@frontend_blueprint.route('/user_profile/<user_id>', strict_slashes=False)
def user_profile(user_id):
    user_builds = requests.get(f'http://pokebuild-backend:5000/api/builds_by_user/{user_id}').json()

    if isinstance(user_builds, dict):
        user_builds = [user_builds]

    pokemons = requests.get('http://pokebuild-backend:5000/api/pokemons/').json()
    user_pokemons = requests.get(f'http://pokebuild-backend:5000/api/pokemons_by_user/{user_id}').json()

    if isinstance(user_pokemons, dict):
        user_pokemons = [user_pokemons]

    pokemons_owned = set()
    build_dict = {}

    for pokemon in user_pokemons:
        pokemons_owned.add(str(pokemon['pokedex_id']).zfill(3))

    for build in user_builds:
        result = get_pokedex_id(get_pokemon_id(build), pokemons)
        build_row = {'owner_id': user_id, 'build_name': build['build_name'],'timestamp': build['timestamp']}
        for j in range(6):
            build_row[f'pokemon_id_{j+1}'] = result[j]
        build_dict[build['id']] = build_row
    
    try:
        username = get_user_name(user_id)
        profile_picture = get_user_profile_picture(user_id)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
    return render_template('user_profile.html', build_dict=build_dict, user_id=user_id, pokemons_owned=pokemons_owned, username=username, profile_picture=profile_picture)

@frontend_blueprint.route('/login', strict_slashes=False)
def login_form():
    return render_template('login_form.html')

@frontend_blueprint.route('/register', strict_slashes=False)
def register_form():
    return render_template('register_form.html')

@frontend_blueprint.route('/trainers', strict_slashes=False)
def trainers_list_container():
    usuarios = requests.get('http://pokebuild-backend:5000/api/users_profiles/').json() #Se puede agregar a fetch_data, pero tengo miedo de cagarla uwu
    dic_nombre_usuario = {}
    for user in usuarios:
        dic_nombre_usuario[user['id']] = user['id']
        dic_nombre_usuario[user['username']] = user['username']
        dic_nombre_usuario[user['build_count']] = user['build_count']
        dic_nombre_usuario[user['pokemon_count']] = user['pokemon_count']
    return render_template('trainers_list_container.html', usuarios=usuarios, dic_nombre_usuario=dic_nombre_usuario)

@frontend_blueprint.route('/modify_user_data/<user_id>', strict_slashes=False)
def modify_user_data(user_id):
    user_data = requests.get(f'http://pokebuild-backend:5000/api/user_profile/{user_id}/').json()
    return render_template('edit_profile.html', user_data=user_data)

@frontend_blueprint.route('/modify_build_form/<owner_id>', strict_slashes=False)
def modify_build_form(owner_id):
    return render_template('modify_build_form.html', build=get_user_builds(owner_id))

@frontend_blueprint.route('/delete_build/<owner_id>', strict_slashes=False)
def delete_build_form(owner_id):
    return render_template('delete_build.html', builds=get_user_builds(owner_id))