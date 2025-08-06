# Buid an Item Catalog Application

## Project Overview

> This project describe that, how to develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## How to Run? :traffic_light:

### Pre Requirements

* [Git 2.50.1](https://git-scm.com/) Version Control System
* [Python 3.10.12](https://www.python.org/downloads/windows/) High-Level Programming Language
* [Vagrant 2.4.7](https://www.vagrantup.com/) Build and Maintain Virtual Machine
* [VirtualBox 7.1.4](https://www.virtualbox.org/wiki/Download_Old_Builds) Execute the Virtual Machine
* Flask Framework (Pre-installed in Virtual Machine)
* Bootstrap 4.1.3 (Required Proper Inrernet Connection)

### Setup the Project

1. Install Git.
2. Install Vagrant and VirtualBox.
3. Python and PostgreSQL are already pre-installed in VM.
4. If you're using Python 3 specifically (and pip3 is available), use:

    ```text
    pip3 install -r requirements.txt
    ```

5. Download or Clone [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository.
6. Download or Clone [Buid an Item Catalog Application](https://github.com/FixEight/udacity-buid-an-item-catalog-application.git) repository.
7. You will need to unzip repository after downloading it or open it after cloning. Move all the content of the cloning/downloaded folder in (New Folder) whose name is **catalog** and move this **catalog** folder inside **vagrant** sub-directory in the downloaded **fullstack-nanodegree-vm**.

### Start the Virtual Machine

The VM is a Linux server system that runs on top of your own computer. You can share files easily between your compute. Launch the VM inside **vagrant** sub-directory in the downloaded **fullstack-nanodegree-vm** repository using command in terminal/Git Bash:

```bash
#!/bin/bash
$ vagrant up
```

log in VM using command in terminal/Git Bash:

```bash
#!/bin/bash
$ vagrant ssh
```

After log in VM, change directory `cd` to /vagrant and look around with `ls`. Then you will get Shell Prompt look like this:

```text
vagrant@vagrant:/vagrant$
```

After in vagrant directory, change directory `cd` to /catalog and look around with `ls`. Then you will get Shell Prompt look like this:

```text
vagrant@vagrant:/vagrant/catalog$
```

### Setup the Database

After in catalog directory in VM. Create database using the command:

```bash
#!/bin/bash
$ python3 database_setup.py
```

After creating database populate it with dummy data by using this command:

```bash
#!/bin/bash
$ python3 lotsofitems.py
```

## Run the Project: :rocket:

Inside **vagrant/catalog** sub-directory run the `project.py` file using the command:

```bash
#!/bin/bash
$ python3 project.py
```

After this open your favourite **Browser** and then type this address in address bar:

```text
http://localhost:8000/catalog/
```

## For JSON Endpoints

Try these links to access public JSON Endpoints.

**Return the JSON objects of all categories and items:**

```text
http://localhost:8000/catalog/JSON
```

**Return the JSON objects of items of specific category:**

```text
http://localhost:8000/catalog/<int:categories_id>/JSON
```

**Return the JSON objects of specific item:**

```text
http://localhost:8000/catalog/<int:categories_id>/<int:itemID>/JSON
```

## Expected Output in Browser: :camel:

![Buid an Item Catalog Application](images/catalog.png)

## License

Buid an Item Catalog Application is Copyright :copyright: 2018 Kashif Iqbal. It is free, and may be redistributed under the terms specified in the [LICENSE](https://choosealicense.com/licenses/mit/#) file.
