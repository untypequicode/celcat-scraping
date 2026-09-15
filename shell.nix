{
  pkgs ? import <nixpkgs> { },
}:
pkgs.mkShell {
  nativeBuildInputs = with pkgs.buildPackages; [
    python314
    pnpm

    cargo
    rustc
    rustfmt
    clippy
    rust-analyzer
  ];
}
