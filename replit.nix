{ pkgs }: {
  deps = [
    pkgs.python311Full
    pkgs.replitPackages.prybar
    pkgs.replitPackages.stderred
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.replitPackages.prybar
      pkgs.replitPackages.stderred
    ];
    PYTHONHOME = "${pkgs.python311Full}";
    PYTHONBIN = "${pkgs.python311Full}/bin/python3.11";
    LANG = "en_US.UTF-8";
    STDERREDBIN = "${pkgs.replitPackages.stderred}/bin/stderred";
    PRYBAR_PYTHON_BIN = "${pkgs.python311Full}/bin/python3.11";
    PRYBAR_SCRIPT_PATH = "$HOME/.config/replit-nix/run";
  };
}

