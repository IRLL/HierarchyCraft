with import <nixpkgs> { };

let
  pythonPackages = python3Packages;
in pkgs.mkShell rec {
  name = "localDevPythonEnv";
  venvDir = "./.venv";
  buildInputs = [
    # A Python interpreter including the 'venv' module is required to bootstrap
    # the environment.
    pythonPackages.python

    # This executes some shell code to initialize a venv in $venvDir before
    # dropping into the shell
    pythonPackages.venvShellHook

    # Those are dependencies that we would like to use from nixpkgs, which will
    # add them to PYTHONPATH and thus make them accessible from within the venv.
    pythonPackages.numpy
    pythonPackages.networkx
    pythonPackages.matplotlib
    pythonPackages.seaborn
    pythonPackages.tqdm
    pythonPackages.pygame
  ];

  # Run this command, only after creating the virtual environment
  postVenvCreation = ''
    pip install -e '.[dev,gui,planning,gym]'
  ''; 

  # Now we can execute any commands within the virtual environment.
  # This is optional and can be left out to run pip manually.
  postShellHook = ''
  '';

}
