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

    # Define additional variables for Docker, Ansible, and System Service operations
    docker_pull_message = ''
    docker_delete_container_message = ''
    docker_delete_image_message = ''
    docker_list_images_message = ''
    docker_list_containers_message = ''

    ansible_playbook_message = ''
    system_service_start_message = ''
    system_service_stop_message = ''
    system_service_status_message = ''

    if request.method == 'POST':
        if 'username' in request.form:
            # User creation logic
            username = request.form['username']
            password = request.form['password']
            command = f"sudo useradd {username} && echo '{username}:{password}' | sudo chpasswd"
            user_message = run_command(command)

            # Check if the user was successfully created and update the message
            if user_message == "Success":
                user_message = f"User '{username}' successfully created."
            else:
                user_message = f"Failed to create user '{username}': {user_message}"

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

        # Add Docker handling logic
        elif 'docker_pull' in request.form:
            docker_image_name = request.form['docker_pull']
            docker_pull_command = f"docker pull {docker_image_name}"
            docker_pull_message = run_command(docker_pull_command)

        elif 'docker_delete_container' in request.form:
            container_name = request.form['docker_delete_container']
            docker_delete_container_command = f"docker rm {container_name}"
            docker_delete_container_message = run_command(docker_delete_container_command)

        elif 'docker_delete_image' in request.form:
            image_name = request.form['docker_delete_image']
            docker_delete_image_command = f"docker rmi {image_name}"
            docker_delete_image_message = run_command(docker_delete_image_command)

        elif 'docker_list_images' in request.form:
            docker_list_images_command = "docker images"
            docker_list_images_message = run_command(docker_list_images_command)

        elif 'docker_list_containers' in request.form:
            docker_list_containers_command = "docker ps -a"
            docker_list_containers_message = run_command(docker_list_containers_command)

        # Add Ansible playbook handling logic
        elif 'ansible_playbook' in request.form:
            ansible_playbook_content = request.form['ansible_playbook']
            # Save the playbook content to a file and run it using Ansible
            with open('/tmp/ansible_playbook.yml', 'w') as playbook_file:
                playbook_file.write(ansible_playbook_content)
            ansible_command = f"ansible-playbook /tmp/ansible_playbook.yml"
            ansible_playbook_message = run_command(ansible_command)

        # Add System Service operations handling logic
        elif 'system_service_start' in request.form:
            service_name = request.form['system_service_start']
            service_start_command = f"sudo systemctl start {service_name}"
            system_service_start_message = run_command(service_start_command)

        elif 'system_service_stop' in request.form:
            service_name = request.form['system_service_stop']
            service_stop_command = f"sudo systemctl stop {service_name}"
            system_service_stop_message = run_command(service_stop_command)

        elif 'system_service_status' in request.form:
            service_name = request.form['system_service_status']
            service_status_command = f"sudo systemctl status {service_name}"
            system_service_status_message = run_command(service_status_command)

    return render_template_string('''
        <html>
            <head>
                <style>
                    body { background-color: #f0f0f0; }
                    .tab { overflow: hidden; border: 1px solid #ccc; background-color: #f9f9f9; }
                    .tab button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; }
                    .tab button:hover { background-color: #ddd; }
                    .tab button.active { background-color: #ccc; }
                    .tabcontent { display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { text-align: left; padding: 8px; }
                    tr:nth-child(even) { background-color: #f2f2f2; }
                    th { background-color: #4CAF50; color: white; }
                </style>
            </head>
            <body>
                <div class="tab">
                    <button class="tablinks" onclick="openTab(event, 'CreateUser')">Create User</button>
                    <button class="tablinks" onclick="openTab(event, 'InstallPackage')">Install Package</button>
                    <button class="tablinks" onclick="openTab(event, 'RemovePackage')">Remove Package</button>
                    <button class="tablinks" onclick="openTab(event, 'Docker')">Docker</button>
                    <button class="tablinks" onclick="openTab(event, 'Ansible')">Ansible</button>
                    <button class="tablinks" onclick="openTab(event, 'SystemService')">System Service</button>
                </div>

                <div id="CreateUser" class="tabcontent">
                    <h2>Create User</h2>
                    <form method="POST">
                        Username: <input type="text" name="username"><br>
                        Password: <input type="text" name="password"><br>
                        <input type="submit" value="Create User">
                    </form>
                    <p>{{ user_message }}</p>
                </div>

                <div id="InstallPackage" class="tabcontent">
                    <h2>Install Package</h2>
                    <form method="POST">
                        Package Name: <input type="text" name="package_install"><br>
                        <input type="submit" value="Install Package">
                    </form>
                    <p>{{ package_install_message }}</p>
                </div>

                <div id="RemovePackage" class="tabcontent">
                    <h2>Remove Package</h2>
                    <form method="POST">
                        Package Name: <input type="text" name="package_remove"><br>
                        <input type="submit" value="Remove Package">
                    </form>
                    <p>{{ package_remove_message }}</p>
                </div>

                <!-- Docker Tab -->
                <div id="Docker" class="tabcontent">
                    <h2>Docker</h2>
                    <form method="POST">
                        Pull Docker Image: <input type="text" name="docker_pull"><br>
                        <input type="submit" value="Pull Image">
                    </form>
                    <p>{{ docker_pull_message }}</p>

                    <form method="POST">
                        Delete Docker Container: <input type="text" name="docker_delete_container"><br>
                        <input type="submit" value="Delete Container">
                    </form>
                    <p>{{ docker_delete_container_message }}</p>

                    <form method="POST">
                        Delete Docker Image: <input type="text" name="docker_delete_image"><br>
                        <input type="submit" value="Delete Image">
                    </form>
                    <p>{{ docker_delete_image_message }}</p>

                    <form method="POST">
                        List Docker Images:<br>
                        <input type="submit" name="docker_list_images" value="List Images">
                    </form>
                    <p>{{ docker_list_images_message }}</p>

                    <!-- Display Docker Images in a Table -->
                    <h3>Docker Images</h3>
                    <table>
                        <tr>
                            <th>Repository</th>
                            <th>Tag</th>
                            <th>Image ID</th>
                            <th>Created</th>
                        </tr>
                        {% for image in docker_list_images_message.splitlines() %}
                            {% if not loop.first %}
                                {% set image_info = image.split() %}
                                <tr>
                                    <td>{{ image_info[0] }}</td>
                                    <td>{{ image_info[1] }}</td>
                                    <td>{{ image_info[2] }}</td>
                                    <td>{{ image_info[3] }}</td>
                                </tr>
                            {% endif %}
                        {% endfor %}
                    </table>

                    <form method="POST">
                        List Docker Containers:<br>
                        <input type="submit" name="docker_list_containers" value="List Containers">
                    </form>
                    <p>{{ docker_list_containers_message }}</p>

                    <!-- Display Docker Containers in a Table -->
                    <h3>Docker Containers</h3>
                    <table>
                        <tr>
                            <th>Container ID</th>
                            <th>Image</th>
                            <th>Command</th>
                            <th>Created</th>
                            <th>Status</th>
                            <th>Ports</th>
                        </tr>
                        {% for container in docker_list_containers_message.splitlines() %}
                            {% if not loop.first %}
                                {% set container_info = container.split() %}
                                <tr>
                                    <td>{{ container_info[0] }}</td>
                                    <td>{{ container_info[1] }}</td>
                                    <td>{{ container_info[2] }}</td>
                                    <td>{{ container_info[4] }}</td>
                                    <td>{{ container_info[5] }}</td>
                                    <td>{{ container_info[6] }}</td>
                                </tr>
                            {% endif %}
                        {% endfor %}
                    </table>
                </div>

                <!-- Ansible Tab -->
                <div id="Ansible" class="tabcontent">
                    <h2>Ansible</h2>
                    <form method="POST">
                        Ansible Playbook Content:<br>
                        <textarea name="ansible_playbook" rows="4" cols="50"></textarea><br>
                        <input type="submit" value="Run Ansible Playbook">
                    </form>
                    <p>{{ ansible_playbook_message }}</p>
                </div>

                <!-- System Service Tab -->
                <div id="SystemService" class="tabcontent">
                    <h2>System Service Operations</h2>
                    <form method="POST">
                        Start Service: <input type="text" name="system_service_start"><br>
                        <input type="submit" value="Start Service">
                    </form>
                    <p>{{ system_service_start_message }}</p>

                    <form method="POST">
                        Stop Service: <input type="text" name="system_service_stop"><br>
                        <input type="submit" value="Stop Service">
                    </form>
                    <p>{{ system_service_stop_message }}</p>

                    <form method="POST">
                        Check Service Status: <input type="text" name="system_service_status"><br>
                        <input type="submit" value="Check Status">
                    </form>
                    <p>{{ system_service_status_message }}</p>
                </div>

                <script>
                    function openTab(evt, tabName) {
                        var i, tabcontent, tablinks;
                        tabcontent = document.getElementsByClassName("tabcontent");
                        for (i = 0; i < tabcontent.length; i++) {
                            tabcontent[i].style.display = "none";
                        }
                        tablinks = document.getElementsByClassName("tablinks");
                        for (i = 0; i < tablinks.length; i++) {
                            tablinks[i].className = tablinks[i].className.replace(" active", "");
                        }
                        document.getElementById(tabName).style.display = "block";
                        evt.currentTarget.className += " active";
                    }
                </script>
            </body>
        </html>
    ''', user_message=user_message, package_install_message=package_install_message,
       package_remove_message=package_remove_message, docker_pull_message=docker_pull_message,
       docker_delete_container_message=docker_delete_container_message, docker_delete_image_message=docker_delete_image_message,
       docker_list_images_message=docker_list_images_message, docker_list_containers_message=docker_list_containers_message,
       ansible_playbook_message=ansible_playbook_message, system_service_start_message=system_service_start_message,
       system_service_stop_message=system_service_stop_message, system_service_status_message=system_service_status_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)   
