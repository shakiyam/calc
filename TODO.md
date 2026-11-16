# TODO

- TODO#1 Stop `check_for_image_updates` at the first `readonly UV_IMAGE=` match in `tools/uv.sh` by adding `; exit` to the awk program in `Makefile`, like the other image lookups in the same target; verify with `make check_for_image_updates`
- TODO#2 Add the missing trailing newline to `.markdownlint.json` as `.editorconfig` requires; verify with `make markdownlint`
- TODO#3 Remove the redundant `RUN mkdir -p /opt/calc` from `Dockerfile` and `dev.Dockerfile`, since `WORKDIR` creates the directory; verify with `make all`

Next ID: TODO#4
