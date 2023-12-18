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
    package_install_message = ''
    package_remove_message = ''

    if request.method == 'POST':
        if 'username' in request.form:
            # User creation logic
            username = request.form['username']
            password = request.form['password']
            command = f"sudo useradd {username} && echo '{username}:{password}' | sudo chpasswd"
            user_message = run_command(command)

        elif 'package_install' in request.form:
            # Package installation logic
            package = request.form['package_install']
            command = f"sudo yum install -y {package}"
            package_install_message = run_command(command)

        elif 'package_remove' in request.form:
            # Package removal logic
            package = request.form['package_remove']
            command = f"sudo yum remove -y {package}"
            package_remove_message = run_command(command)

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Impressive Web Page</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #fff;
                    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
                    border-radius: 5px;
                }
                h2 {
                    color: #333;
                }
                form {
	                    margin-top: 10px;
                }
                input[type="text"] {
                    width: 100%;
                    padding: 10px;
                    margin-bottom: 10px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
                input[type="submit"] {
                    background-color: #007BFF;
                    color: #fff;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 3px;
                    cursor: pointer;
                }
                p {
                    color: #333;
                }
            </style>
        </head>
        <body>
            <div class="container">
<h1>DevOps Project by Vijay Lathwal</h1>        
        <h2>Create User</h2>
                <form method="POST">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username">
                    <br>
                    <label for="password">Password:</label>
                    <input type="text" id="password" name="password">
                    <br>
                    <input type="submit" value="Create User">
                </form>
                <p>{{ user_message }}</p>

                <h2>Install Package</h2>
                <form method="POST">
                    <label for="package_install">Package Name:</label>
                    <input type="text" id="package_install" name="package_install">
                    <br>
                    <input type="submit" value="Install Package">
                </form>
                <p>{{ package_install_message }}</p>

                <h2>Remove Package</h2>
                <form method="POST">
                    <label for="package_remove">Package Name:</label>
                    <input type="text" id="package_remove" name="package_remove">
                    <br>
                    <input type="submit" value="Remove Package">
                </form>
                <p>{{ package_remove_message }}</p>
            </div>
        </body>
        </html>
    ''', user_message=user_message, package_install_message=package_install_message, package_remove_message=package_remove_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
