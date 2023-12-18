from flask import Flask, request, render_template_string, jsonify
import subprocess
import threading

app = Flask(__name__)

# Function to run a command and capture its output
def run_command(command, progress_callback):
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        for line in process.stdout:
            progress_callback(line.strip())

        process.wait()
        return process.returncode == 0

    except Exception as e:
        return str(e)

# Function to update progress using Flask's jsonify
def update_progress(progress_message):
    progress_data = {'progress_message': progress_message}
    return jsonify(progress_data)

# Main route to render the HTML page and handle form submissions
@app.route('/', methods=['GET', 'POST'])
def index():
    user_message = ''
    package_install_message = ''
    package_remove_message = ''

    docker_pull_message = ''
    docker_delete_container_message = ''
    docker_delete_image_message = ''
    docker_list_images_message = ''
    docker_list_containers_message = ''

    ansible_playbook_message = ''
    system_service_start_message = ''
    system_service_stop_message = ''
    system_service_status_message = ''

    # Function to update progress during command execution
    def progress_callback(message):
        nonlocal user_message, package_install_message, package_remove_message, \
            docker_pull_message, docker_delete_container_message, docker_delete_image_message, \
            docker_list_images_message, docker_list_containers_message, \
            ansible_playbook_message, system_service_start_message, \
            system_service_stop_message, system_service_status_message

        # Handle progress updates based on the message content
        if message.startswith("Progress: "):
            progress_message = message.split("Progress: ")[1]

            # Update the appropriate message variable based on the context
            if message.startswith("Progress: CreateUser"):
                user_message = progress_message
            elif message.startswith("Progress: InstallPackage"):
                package_install_message = progress_message
            elif message.startswith("Progress: RemovePackage"):
                package_remove_message = progress_message
            elif message.startswith("Progress: DockerPull"):
                docker_pull_message = progress_message
            elif message.startswith("Progress: DockerDeleteContainer"):
                docker_delete_container_message = progress_message
            elif message.startswith("Progress: DockerDeleteImage"):
                docker_delete_image_message = progress_message
            elif message.startswith("Progress: DockerListImages"):
                docker_list_images_message = progress_message
            elif message.startswith("Progress: DockerListContainers"):
                docker_list_containers_message = progress_message
            elif message.startswith("Progress: AnsiblePlaybook"):
                ansible_playbook_message = progress_message
            elif message.startswith("Progress: SystemServiceStart"):
                system_service_start_message = progress_message
            elif message.startswith("Progress: SystemServiceStop"):
                system_service_stop_message = progress_message
            elif message.startswith("Progress: SystemServiceStatus"):
                system_service_status_message = progress_message

    if request.method == 'POST':
        if 'username' in request.form:
            # User creation logic
            username = request.form['username']
            password = request.form['password']
            command = f"sudo useradd {username} && echo '{username}:{password}' | sudo chpasswd"
            success = run_command(command, progress_callback)
            if success:
                user_message = f"User '{username}' successfully created."
            else:
                user_message = f"Failed to create user '{username}'."

        elif 'package_install' in request.form:
            # Package installation logic
            package = request.form['package_install']
            command = f"sudo yum install -y {package}"
            success = run_command(command, progress_callback)
            if success:
                package_install_message = f"Package '{package}' successfully installed."
            else:
                package_install_message = f"Failed to install package '{package}'."

        elif 'package_remove' in request.form:
            # Package removal logic
            package = request.form['package_remove']
            command = f"sudo yum remove -y {package}"
            success = run_command(command, progress_callback)
            if success:
                package_remove_message = f"Package '{package}' successfully removed."
            else:
                package_remove_message = f"Failed to remove package '{package}'."

        # Add Docker handling logic
        elif 'docker_pull' in request.form:
            docker_image_name = request.form['docker_pull']
            docker_pull_command = f"docker pull {docker_image_name}"
            success = run_command(docker_pull_command, progress_callback)
            if success:
                docker_pull_message = f"Successfully pulled Docker image '{docker_image_name}'."
            else:
                docker_pull_message = f"Failed to pull Docker image '{docker_image_name}'."

        elif 'docker_delete_container' in request.form:
            container_name = request.form['docker_delete_container']
            docker_delete_container_command = f"docker rm {container_name}"
            success = run_command(docker_delete_container_command, progress_callback)
            if success:
                docker_delete_container_message = f"Deleted Docker container '{container_name}'."
            else:
                docker_delete_container_message = f"Failed to delete Docker container '{container_name}'."

        elif 'docker_delete_image' in request.form:
            image_name = request.form['docker_delete_image']
            docker_delete_image_command = f"docker rmi {image_name}"
            success = run_command(docker_delete_image_command, progress_callback)
            if success:
                docker_delete_image_message = f"Deleted Docker image '{image_name}'."
            else:
                docker_delete_image_message = f"Failed to delete Docker image '{image_name}'."

        elif 'docker_list_images' in request.form:
            docker_list_images_command = "docker images"
            success = run_command(docker_list_images_command, progress_callback)
            if success:
                pass  # The output will be captured in the progress_callback
            else:
                docker_list_images_message = "Failed to list Docker images."

        elif 'docker_list_containers' in request.form:
            docker_list_containers_command = "docker ps -a"
            success = run_command(docker_list_containers_command, progress_callback)
            if success:
                pass  # The output will be captured in the progress_callback
            else:
                docker_list_containers_message = "Failed to list Docker containers."

        # Add Ansible playbook handling logic
        elif 'ansible_playbook' in request.form:
            ansible_playbook_content = request.form['ansible_playbook']
            # Save the playbook content to a file and run it using Ansible
            with open('/tmp/ansible_playbook.yml', 'w') as playbook_file:
                playbook_file.write(ansible_playbook_content)
            ansible_command = f"ansible-playbook /tmp/ansible_playbook.yml"
            success = run_command(ansible_command, progress_callback)
            if success:
                ansible_playbook_message = "Ansible playbook executed successfully."
            else:
                ansible_playbook_message = "Failed to execute Ansible playbook."

        # Add System Service operations handling logic
        elif 'system_service_start' in request.form:
            service_name = request.form['system_service_start']
            service_start_command = f"sudo systemctl start {service_name}"
            success = run_command(service_start_command, progress_callback)
            if success:
                system_service_start_message = f"Started system service '{service_name}'."
            else:
                system_service_start_message = f"Failed to start system service '{service_name}'."

        elif 'system_service_stop' in request.form:
            service_name = request.form['system_service_stop']
            service_stop_command = f"sudo systemctl stop {service_name}"
            success = run_command(service_stop_command, progress_callback)
            if success:
                system_service_stop_message = f"Stopped system service '{service_name}'."
            else:
                system_service_stop_message = f"Failed to stop system service '{service_name}'."

        elif 'system_service_status' in request.form:
            service_name = request.form['system_service_status']
            service_status_command = f"sudo systemctl status {service_name}"
            success = run_command(service_status_command, progress_callback)
            if success:
                pass  # The output will be captured in the progress_callback
            else:
                system_service_status_message = f"Failed to retrieve status of system service '{service_name}'."

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
                </style>
                <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
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

                    <!-- Add Docker delete container, delete image, list images, and list containers forms and output display here -->
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

                    // Function to update progress using jQuery
                    function updateProgress(message) {
                        $("#progress_messages").append("<p>" + message + "</p>");
                    }

                    // Function to submit forms and display progress
                    $("form").submit(function (event) {
                        event.preventDefault();  // Prevent the form from submitting normally
                        var form = $(this);  // The form being submitted
                        var url = form.attr("action");  // The form's action URL

                        // Send an AJAX POST request
                        $.ajax({
                            type: "POST",
                            url: url,
                            data: form.serialize(),  // Serialize the form data
                            success: function (data) {
                                // Handle success (data is the response from the server)
                                if (data.progress_message) {
                                    updateProgress(data.progress_message);
                                }
                                // You can also update the result messages here if needed
                                // Example: $("#result_message").html(data.result_message);
                            },
                            dataType: "json"  // Expect JSON response from the server
                        });
                    });
                </script>
                <div id="progress_messages"></div>  <!-- Progress messages will be displayed here -->
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

