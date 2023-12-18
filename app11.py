from flask import Flask, request, render_template_string
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

@app.route('/', methods=['GET', 'POST'])
def index():
    user_message = ''
    package_install_message = ''
    package_remove_message = ''
    docker_message = ''

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

        elif 'create_docker_container' in request.form:
            # Create Docker container logic
            container_name = request.form['container_name']
            image_name = request.form['docker_image']
            try:
                container = docker_client.containers.run(image_name, name=container_name, detach=True)
                docker_message = f"Container {container_name} created successfully."
            except docker.errors.APIError as e:
                docker_message = f"Docker Error: {str(e)}"

        elif 'pull_docker_image' in request.form:
            # Pull Docker image logic
            image_name = request.form['docker_image']
            try:
                docker_client.images.pull(image_name)
                docker_message = f"Image {image_name} pulled successfully."
            except docker.errors.APIError as e:
                docker_message = f"Docker Error: {str(e)}"

        elif 'delete_docker_container' in request.form:
            # Delete Docker container logic
            container_name = request.form['container_name']
            try:
                container = docker_client.containers.get(container_name)
                container.remove(force=True)
                docker_message = f"Container {container_name} deleted successfully."
            except docker.errors.NotFound:
                docker_message = f"Container {container_name} not found."
            except docker.errors.APIError as e:
                docker_message = f"Docker Error: {str(e)}"

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

                <h2>Pull Docker Image</h2>
                <form method="POST">
                    <label for="docker_image">Docker Image:</label>
                    <input type="text" id="docker_image" name="docker_image">
                    <br>
                    <input type="submit" name="pull_docker_image" value="Pull Docker Image">
                </form>
                <p>{{ docker_message }}</p>

                <h2>Delete Docker Container</h2>
                <form method="POST">
                    <label for="container_name">Container Name:</label>
                    <input type="text" id="container_name" name="container_name">
                    <br>
                    <input type="submit" name="delete_docker_container" value="Delete Docker Container">
                </form>
                <p>{{ docker_message }}</p>
            </div>
        </body>
        </html>
    ''', user_message=user_message, package_install_message=package_install_message, package_remove_message=package_remove_message, docker_message=docker_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
