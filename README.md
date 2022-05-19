# mini-amazon-skeleton

Skeleton code for the CompSci 316 undergraduate course project.
Created by [Rickard Stureborg](http://www.rickard.stureborg.com) and [Yihao Hu](https://www.linkedin.com/in/yihaoh/).

## Running/Stopping the Website

To run your website, in your VM, go into the repository directory and issue the following commands:

```
source env/bin/activate
flask run
```

The first command will activate a specialized Python environment for running Flask.
While the environment is activated, you should see a `(env)` prefix in the command prompt in your VM shell.
You should only run Flask while inside this environment; otherwise it will produce an error.

If you are running a local Vagrant VM, to view the app in your browser, you simply need to visit [http://localhost:5000/](http://localhost:5000/).
If you are running a Google VM, you will need to point your browser to `http://vm_external_ip_addr:5000/`, where `vm_external_ip_addr` is the external IP address of your Google VM.

To stop your website, simply press <kbd>Ctrl</kbd><kbd>C</kbd> in the VM shell where flask is running.
You can then deactivate the environment using

```
deactiviate
```
