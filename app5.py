from flask import Flask, request, render_template_string
import subprocess
import docker

app = Flask(__name__)
client = docker.from_env()

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
    container_message = ''

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

        elif 'container_action' in request.form:
            # Docker container logic
            action = request.form['container_action']
            container_name = request.form['container_name']
            image_name = request.form['image_name']

            if action == 'create':
                # Create a Docker container
                client.containers.create(image_name, name=container_name, detach=True)
                container_message = f"Container {container_name} created from image {image_name}"

            elif action == 'pull':
                # Pull a Docker image
                client.images.pull(image_name)
                container_message = f"Image {image_name} pulled"

            elif action == 'run':
                # Run a Docker container
                container = client.containers.get(container_name)
                container.start()
                container_message = f"Container {container_name} started"

            elif action == 'remove':
                # Remove a Docker container
                container = client.containers.get(container_name)
                container.stop()
                container.remove()
                container_message = f"Container {container_name} removed"

    return render_template_string('''
        <html>
            <!-- ... (previous HTML code) ... -->

            <h2>Docker Actions</h2>
            <form method="POST">
                Action:
                <select name="container_action">
                    <option value="create">Create Container</option>
                    <option value="pull">Pull Image</option>
                    <option value="run">Run Container</option>
                    <option value="remove">Remove Container</option>
                </select><br>
                Image Name: <input type="text" name="image_name"><br>
                Container Name: <input type="text" name="container_name"><br>
                <input type="submit" value="Execute">
            </form>
            <p>{{ container_message }}</p>
        </html>
    ''', user_message=user_message, package_install_message=package_install_message, package_remove_message=package_remove_message, container_message=container_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
