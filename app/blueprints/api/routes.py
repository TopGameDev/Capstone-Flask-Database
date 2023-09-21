from . import api
from app import db
from app.models import Post, User
from flask import request
from .auth import basic_auth, token_auth



@api.route('/token')
@basic_auth.login_required
def get_token():
    auth_user = basic_auth.current_user()
    token = auth_user.get_token()
    return {
        'token': token,
        'tokenExpiration': auth_user.token_expiration
    }

@api.route('/posts')
def get_posts():
    posts = db.session.execute(db.select(Post)).scalars().all()
    return [post.to_dict() for post in posts]

@api.route('/posts/<post_id>')
def get_post(post_id):
    post = db.session.get(Post, post_id)
    if post:
        return post.to_dict()
    else:
        return {'error': f'Post with an ID of {post_id} does not exist.'}, 404


@api.route('/posts', methods=["POST"])
@token_auth.login_required
def create_post():
    print(request)
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    data = request.json
    print(data, type(data))
    required_fields = ['title', 'body']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400

    title = data.get('title')
    body = data.get('body')
    image_url = data.get('image_url')


    current_user = token_auth.current_user()
    new_post = Post(title=title, body=body, image_url=image_url, user_id=current_user.id)
    db.session.add(new_post)
    db.session.commit()

    return new_post.to_dict(), 201


@api.route('/posts/<post_id>', methods=['PUT'])
@token_auth.login_required
def edit_post(post_id):
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    post = db.session.get(Post, post_id)
    if post is None:
        return {'error': f"Post with an ID of {post_id} not found"}, 404
    current_user = token_auth.current_user()
    if post.author != current_user:
        return {'error': 'You do not have permission to edit this post'}, 403
    data = request.json
    for field in data:
        if field in {'title','body', 'image_url'}:
            setattr(post, field, data[field])
    db.session.commit()
    return post.to_dict()

@api.route('/posts/<post_id>', methods=['DELETE'])
@token_auth.login_required
def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        return {'error': f'Post with an ID of {post_id} does not exist!'}, 404
    current_user = token_auth.current_user()
    if post.author != current_user:
        return {'error': "You do not have permission to delete this post"}, 403
    db.session.delete(post)
    db.session.commit()
    return {'succes': f"'{post.title}' has been deleted!"}


@api.route('/users/me')
@token_auth.login_required
def get_me():
    me = token_auth.current_user()
    return me.to_dict()


@api.route('/users', methods=['POST'])
def create_user():
    print(request)
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    data = request.json
    print(data, type(data))
    required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400

    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    check_user = db.session.execute(db.select(User).where((User.username == username) | (User.email == email))).scalar()
    if check_user:
        return {'error': f"A user with that username and/or email already exists"}, 400

    new_user = User(first_name = first_name, last_name = last_name, username = username, email = email, password = password)
    db.session.add(new_user)
    db.session.commit()

    return new_user.to_dict(), 201

@api.route('/users/<user_id>', methods=['PUT'])
@token_auth.login_required
def edit_user(user_id):
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    user = db.session.get(User, user_id)
    if user is None:
        return {'error': f"User with an ID of {user_id} not found"}, 404
    data = request.json
    for field in data:
        if field in {'firstName', 'lastName', 'email', 'username', 'profile'}:
            setattr(user, field, data[field])
    db.session.commit()
    return user.to_dict()