from flask import Flask, request, render_template, jsonify
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

# Function to create a Docker container
def create_docker_container(container_name, image_name):
    try:
        container = docker_client.containers.run(image_name, name=container_name, detach=True)
        return f"Container {container_name} created successfully."
    except docker.errors.APIError as e:
        return f"Docker Error: {str(e)}"

# Function to pull a Docker image
def pull_docker_image(image_name):
    try:
        docker_client.images.pull(image_name)
        return f"Image {image_name} pulled successfully."
    except docker.errors.APIError as e:
        return f"Docker Error: {str(e)}"

# Function to delete a Docker container
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

            elif 'create_user_docker_container' in request.form:
                user_container_name = request.form['user_container_name']
                user_docker_image = request.form['user_docker_image']
                docker_message = create_docker_container(user_container_name, user_docker_image)

        elif active_tab == 'packages':
            if 'package_install' in request.form:
                package = request.form['package_install']
                package_install_message = install_package(package)

            elif 'package_remove' in request.form:
                package = request.form['package_remove']
                package_remove_message = remove_package(package)

            elif 'create_package_docker_container' in request.form:
                package_container_name = request.form['package_container_name']
                package_docker_image = request.form['package_docker_image']
                docker_message = create_docker_container(package_container_name, package_docker_image)

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

    return render_template('index.html', user_message=user_message, package_install_message=package_install_message, package_remove_message=package_remove_message, docker_message=docker_message, active_tab=active_tab)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
