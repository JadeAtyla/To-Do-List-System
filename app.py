from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Ensure instance folder exists for the database
os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'instance', 'todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "deleted": self.deleted,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

@app.route('/')
def index():
    # Get first page of active tasks for initial render
    active_tasks = Todo.query.filter_by(completed=False, deleted=False).order_by(Todo.created_at.desc()).limit(5).all()
    return render_template('index.html', initial_tasks=[t.to_dict() for t in active_tasks])

@app.route('/api/todos/', methods=['GET', 'POST'])
def todos():
    if request.method == 'POST':
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        if not title:
            return jsonify({"error": "Title is required"}), 400
        todo = Todo(
            title=title,
            description=description
        )
        db.session.add(todo)
        db.session.commit()
        return jsonify(todo.to_dict()), 201

    # GET with pagination and state filter
    state = request.args.get('state')
    page = int(request.args.get('page', 1))
    per_page = 5

    query = Todo.query
    if state == 'active':
        query = query.filter_by(completed=False, deleted=False)
    elif state == 'completed':
        query = query.filter_by(completed=True, deleted=False)
    elif state == 'deleted':
        query = query.filter_by(deleted=True)

    pagination = query.order_by(Todo.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    todos = [todo.to_dict() for todo in pagination.items]
    return jsonify({
        "count": pagination.total,
        "results": todos
    })

@app.route('/api/todos/<int:todo_id>/', methods=['PATCH'])
def update_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    data = request.get_json()
    updated = False

    if 'title' in data:
        todo.title = data['title']
        updated = True
    if 'description' in data:
        todo.description = data['description']
        updated = True
    if 'completed' in data:
        # Accept both boolean and string "true"/"false"
        val = data['completed']
        if isinstance(val, str):
            val = val.lower() == 'true'
        todo.completed = bool(val)
        updated = True
    if 'deleted' in data:
        val = data['deleted']
        if isinstance(val, str):
            val = val.lower() == 'true'
        todo.deleted = bool(val)
        updated = True

    if updated:
        todo.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(todo.to_dict()), 200
    else:
        return jsonify({"error": "No valid fields to update"}), 400

# Optional: DELETE endpoint for hard delete (not used by frontend)
@app.route('/api/todos/<int:todo_id>/', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Todo deleted"}), 204

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
