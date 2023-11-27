## inea_produccion/bash_scripts

En este directorio se alojan los scripts de bash que corren cada script de producción mediante cron en el servidor de producción.

Se usan scripts de bash para poder correr cada script python dentro de su entorno virtual. Se activa el entorno y luego se corre el script python dentro de ese entorno.
 
Por cada bash_script hay una versión "desarrollo" que se arma con paths locales para testeo en desarrollo, y una versión "producción" con los paths del servidor de producción.

