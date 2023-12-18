from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout or "Success"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

@app.route('/', methods=['GET', 'POST'])
def index():
    user_message = ''
    package_message = ''

    if request.method == 'POST':
        if 'username' in request.form:
            # User creation logic
            username = request.form['username']
            password = request.form['password']
            command = f"sudo useradd {username} && echo '{username}:{password}' | sudo chpasswd"
            user_message = run_command(command)

        elif 'package' in request.form:
            # Package installation logic
            package = request.form['package']
            command = f"sudo yum install -y {package}"
            package_message = run_command(command)

    return render_template_string('''
        <h2>Create User</h2>
        <form method="POST">
            Username: <input type="text" name="username"><br>
            Password: <input type="text" name="password"><br>
            <input type="submit" value="Create User">
        </form>
        <p>{{ user_message }}</p>

        <h2>Install Package</h2>
        <form method="POST">
            Package Name: <input type="text" name="package"><br>
            <input type="submit" value="Install Package">
        </form>
        <p>{{ package_message }}</p>
    ''', user_message=user_message, package_message=package_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
