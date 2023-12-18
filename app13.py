from flask import Flask, request, render_template_string, jsonify
import subprocess
import docker

app = Flask(__name__)

# Create a Docker client
docker_client = docker.from_env()

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout or "Success"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def create_user(username, password):
    command = f"sudo useradd {username} && echo '{username}:{password}' | sudo chpasswd"
    return run_command(command)

def install_package(package):
    command = f"sudo yum install -y {package}"
    return run_command(command)

def remove_package(package):
    command = f"sudo yum remove -y {package}"
    return run_command(command)

def create_docker_container(container_name, image_name):
    try:
        container = docker_client.containers.run(image_name, name=container_name, detach=True)
        return f"Container {container_name} created successfully."
    except docker.errors.APIError as e:
        return f"Docker Error: {str(e)}"

def pull_docker_image(image_name):
    try:
        docker_client.images.pull(image_name)
        return f"Image {image_name} pulled successfully."
    except docker.errors.APIError as e:
        return f"Docker Error: {str(e)}"

def delete_docker_container(container_name):
    try:
        container = docker_client.containers.get(container_name)
        container.remove(force=True)
        return f"Container {container_name} deleted successfully."
    except docker.errors.NotFound:
        return f"Container {container_name} not found."
    except docker.errors.APIError as e:
        return f"Docker Error: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    user_message = ''
    package_install_message = ''
    package_remove_message = ''
    docker_message = ''
    active_tab = request.form.get('active_tab', 'users')

    if request.method == 'POST':
        if active_tab == 'users':
            if 'username' in request.form:
                username = request.form['username']
                password = request.form['password']
                user_message = create_user(username, password)

        elif active_tab == 'packages':
            if 'package_install' in request.form:
                package = request.form['package_install']
                package_install_message = install_package(package)

            elif 'package_remove' in request.form:
                package = request.form['package_remove']
                package_remove_message = remove_package(package)

        elif active_tab == 'docker':
            if 'create_docker_container' in request.form:
                container_name = request.form['container_name']
                image_name = request.form['docker_image']
                docker_message = create_docker_container(container_name, image_name)

            elif 'pull_docker_image' in request.form:
                image_name = request.form['docker_image']
                docker_message = pull_docker_image(image_name)

            elif 'delete_docker_container' in request.form:
                container_name = request.form['container_name']
                docker_message = delete_docker_container(container_name)

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>DevOps Dashboard</title>
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
                .tabs {
                    display: flex;
                }
                .tab {
                    flex: 1;
                    text-align: center;
                    padding: 10px;
                    background-color: #007BFF;
                    color: #fff;
                    cursor: pointer;
                }
                .tab-content {
                    display: none;
                }
                .tab-content.active {
                    display: block;
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
            <script>
                function switchTab(tabName) {
                    document.getElementById('active_tab').value = tabName;
                    var tabContents = document.getElementsByClassName('tab-content');
                    for (var i = 0; i < tabContents.length; i++) {
                        tabContents[i].style.display = 'none';
                    }
                    document.getElementById(tabName).style.display = 'block';
                }
            </script>
        </head>
        <body>
            <div class="container">
                <h1>DevOps Dashboard by Vijay Lathwal</h1>

                <div class="tabs">
                    <div class="tab" onclick="switchTab('users')">Users</div>
                    <div class="tab" onclick="switchTab('packages')">Packages</div>
                    <div class="tab" onclick="switchTab('docker')">Docker</div>
                </div>

                <div class="tab-content" id="users">
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
                </div>

                <div class="tab-content" id="packages">
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

                <div class="tab-content" id="docker">
                    <h2>Create Docker Container</h2>
                    <form method="POST">
                        <label for="container_name">Container Name:</label>
                        <input type="text" id="container_name" name="container_name">
                        <br>
                        <label for="docker_image">Docker Image:</label>
                        <input type="text" id="docker_image" name="docker_image">
                        <br>
                        <input type="submit" name="create_docker_container" value="Create Docker Container">
                    </form>
                    <p>{{ docker_message }}</p>
                </div>
                <input type="hidden" id="active_tab" name="active_tab" value="{{ active_tab }}">
            </div>
        </body>
        </html>
    ''', user_message=user_message, package_install_message=package_install_message, package_remove_message=package_remove_message, docker_message=docker_message, active_tab=active_tab)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
