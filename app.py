from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'postgresql://postgres:password@localhost:5432/tododb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

metrics = PrometheusMetrics(app)
metrics.info("flask_app", "Flask Todo App", version =  "1.0")

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    todos = Todo.query.all()
    return render_template('index.html', todos=todos)

@app.route('/health')
def health():
    try:
        db.session.execute('SELECT 1')
        return {"status" : "ok"}, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status" : "error", "message" : str(e)}, 500

@app.route('/add', methods=['POST'])
def add_todo():
    task = request.form.get('todo')
    if task:
        new_todo = Todo(task=task)
        db.session.add(new_todo)
        db.session.commit()
        logger.info(f"New task added: {task}")
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>', methods=['GET'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
        logger.warning(f"Task deleted: {todo}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
