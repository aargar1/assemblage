# Assemblage

Assemblage is a web-based platform that gives users (intended mostly for educational users) access to real, fully configured Linux programming environments directly in their browser. Each user is provisioned a secure personal shell account where they can practice command-line skills, write scripts, and develop software in languages such as Python, C, C++, Java, and JavaScript. 

The system combines a Flask-powered interface and a Visual Studio Code deployment running on JupyterHub, all deployed behind Nginx for performance and security. Assemblage intends to provide a consistent, low-friction learning environment ideal for classrooms, remote instruction, workshops, and self-study.

## Installation
Assemblage's own install script assumes a Debian(-derivative) Linux configuration with `systemctl` installed. However, manual installation itself should be generally straightforward assuming that the system has (working) installations of Python3, `build-essentials` (or equivalent, ie. `cc`, `make`, etc.) and Node.js. The `install.sh` script provides great guidance regardless.

On a Debian(-derivative) system, one may automate the installation with the packaged `install.sh` script by cloning this repository and executing the script, which will insert Assemblage into the `/srv` directory. 

> If Nginx is already running on the system, or there is another webserver currently using ports 8080, 8000, 80, 500, etc., you might want to manually configure the Nginx sites in `src/nginx`; the script is written with fresh systems in mind.

Once a manual installation has been performed or the script has been run, one will want to automatically enter the fields in `/srv/asm/config.py`; the `SMTP_*` fields are self-expanatory; the `DOMAIN` field allows you to restrict usage of Assemblage to users with a certain email domain (ie. `university.edu`). `DOMAIN` can be left blank if the service is intended for members of the general public or if it is hosted on an intranet.
## Usage & Management

Assemblage is designed to be as intuitive as possible to use. End users should set up their account by using the `create` command at your Assemblage installation's homepage, and can log in via SSH, or via the online Visual Studio Code IDE (`yourinstallation.tld/jupyter`). Instructions for using Visual Studio Code can be found [here](https://code.visualstudio.com/).

Assemblage doesn't contain its own interface to manage users; instead, all Assemblage users are also Unix users in `/etc/passwd` and can be managed accordingly. By default, Assemblage provides users with home folders in `/home/edu`; the size of these can be configured by setting project or user quotas.

Assemblage does, in order to prevent misuse, gather a record of all new user's names and email addresses at `/srv/asm`, however it is reccomended to only allow users with institutional email addresses. A server management console like [Cockpit](https://cockpit-project.org/) might be useful depending on your own usecase.

## Ackowlegements
Thanks to the various repositories, examples, and open source projects that were used in the process of building Assemblage. Namely,
* Flask, Gunicorn, and Nginx, for powering the interface
* Jupyter, for managing spawns of the online IDE
* code-server and VS Code, for powering the online IDE

Where possible, license reproductions have been included for most, if not all, projects utilized in Assemblage.

## License
Assemblage is licensed under the [Server Side Public License](https://www.mongodb.com/legal/licensing/server-side-public-license). 

Assemblage is fundamentally a server-side educational platform: its primary value is not a reusable library, but a carefully integrated system. In practice, this kind of software is most often deployed as a hosted service rather than redistributed as standalone binaries.

The SSPL is intended to address a specific problem in this space: it prevents third parties from taking the software, offering it as a closed, hosted service, and contributing nothing back to the community. Under SSPL, anyone is free to use, study, modify, and self-host Assemblage, including in classrooms, universities, workshops, and personal labs. However, if someone offers Assemblage as a publicly accessible service, they are required to make the full source code of that service available under the same license.

It’s worth noting that SSPL is not OSI-approved, and some distributions and organizations avoid it for that reason. If your use case requires an OSI-approved license, Assemblage may not be a suitable dependency. That said, for its intended role—as a deployable, educational server platform—the SSPL provides protections that permissive licenses do not.

> If your _educational institution_ would like to use Assemblage for _patently non-commercial applications_, but cannot do so under the SSPL, please contact me via an issue; I would be happy to work something out.