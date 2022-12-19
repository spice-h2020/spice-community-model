from cmspice.apiServer import run

from sys import argv

# Tareas de inicialización
# TODO: Faltarían otras tareas relacionadas con el core del community model
if len(argv) == 2:
    run(port=int(argv[1]))
else:
    run()