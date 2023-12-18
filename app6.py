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
            </head>
            <body>
                <div class="tab">
                    <button class="tablinks" onclick="openTab(event, 'CreateUser')">Create User</button>
                    <button class="tablinks" onclick="openTab(event, 'InstallPackage')">Install Package</button>
                    <button class="tablinks" onclick="openTab(event, 'RemovePackage')">Remove Package</button>
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
    ''', user_message=user_message, package_install_message=package_install_message, package_remove_message=package_remove_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
