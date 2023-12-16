#!/bin/bash

now="$(date)"

echo ""
echo $now

# echo "previo a abrir exe"

#	abre exe "PoductosMG"
mono /home/inea/sistemas/inea_produccion/executables/ProductosMG/ProductosMG.exe &
# echo "exe abierto"

#	pausa
sleep 4
# echo "pausa post apertua de exe"

#	ejecuta actualización de precios y lo cierra
xdotool search --name "Productos MG" mousemove --window=%1 100 30 click 1 sleep 5 mousemove --window=%1 350 30 click 1 sleep 0.5 mousemove --window=%1 350 40 click 1 mousemove --window=%1 600 30 click 1 sleep 180 getwindowfocus windowkill

# 	notifica ejecución a Notion
/home/inea/sistemas/inea_produccion/env/bin/python3.11 /home/inea/sistemas/inea_produccion/notificaciones/notificador.py -c "console" "notion" -m "Ejecución de Precios MG>GBP notificada" -o "up" -s "Precios MG en GBP"


echo "script de actualización de precios ejecutado"
echo ---------

