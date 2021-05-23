# Implementación de Chord en python 3

## Generalidades

El programa consta de dos módulos esenciales, las clases server y chordNode que se encuentran en los scripts del mismo nombre.

***

## La clase Server

La clase server es la encargada de coordinar el trabajo con los nodos del modelo chord, es decir, esta clase es la que debe contactar cada nodo al comenzar su ejecución para obtener información sobre la distribución del grafo, así como su propio id. Esta clase al instanciarse prepara el socket por el cual establecerá las conexiones, y espera por mensajes entrantes que serán atendidos usando el patrón dispatcher-worker. Estos mensajes pueden ser de distintos tipos:

* **JOIN:** Los mensajes tipo JOIN se usan para indicar que existe un nuevo proceso intentando unirse al modelo, el server lo añadirá al grupo en cuestión y le devolverá un id que no esté siendo usado por ningún otro nodo de ese grupo.

* **LEAVE:** Los mensajes tipo LEAVE se usan para indicar que un nodo está a punto de dejar el grupo.

* **EXISTS:** Los mensajes tipo EXISTS se usan para preguntar si existe algún nodo que posea una dirección IP dada.

* **SUBGROUP:** Los mensajes tipo SUBGROUP se usan para obtener los ids de todos los nodos pertenecientes a un subgrupo dado. Esto es útil para construir las Finger Tables de los distintos nodos.

* **NBITS:** Los mensajes tipo NBITS se usan para preguntar al servidor la cantidad de bits que están siendo usados en el modelo actual para identificar los nodos y por tanto, la cantidad de nodos máxima que permite el modelo.

* **ADDRESS:** Los mensajes tipo ADDRESS se usan para preguntar al servidor sobre la dirección IP del nodo al que pertenece un id en particular.

* **BIND:** Los mensajes tipo BIND se usan para indicar al servidor cual será la dirección IP por la cual estará escuchando comunicaciones un nodo en particular.

* **DISCONNECT:** Los mensajes tipo DISCONNECT se usan para cerrar la conexión actual con el servidor.

Cada mensaje que llegue al servidor debe estar formado por una tupla la cual en su primera posición debe tener el tipo del mensaje correspondiente y en la segunda el texto del mensaje en caso necesario.

***

## La clase chordNode

La clase chordNode abrirá al iniciarse dos sockets, uno tipo TCP para la comunicación con el servidor y otro tipo zmq.REP para atender los pedidos entrantes al nodo. La clase abrirá además un hilo extra que actualizará constantemente, preguntándole al server, los nodos conectados al modelo y la Finger Table del nodo. Los tipos de mensajes que atiende el nodo son:

* **STOP:** Se utiliza para detener el proceso que corre el nodo.

* **LOOKUP_REQ:** Se utiliza para indicarle al nodo que busque en su Finger Table cual es el nodo que responde a un hash dado, se responderá con un mensaje tipo LOOKUP_REP.

* **CONNECT:** Se utiliza para indicarle al nodo que otro nodo se ha conectado a la red y está pidiendo por su reconocimiento.

***

## La clase chordClient

Se implementó ademas la clase chordClient como un ejemplo del uso de los nodos en la red, esta se comunica con el servidor para obtener su id personal y para obtener el id de los nodos del modelo, y luego preguntará a un nodo random por algún hash random y creará un log de los resultados obtenidos durante el proceso que se imprimirá en la salida estándar.

***

Las implementaciones de los métodos finger, recomputeFingerTable y localSuccNode pertenecientes a la clase chordNode son similares a las proporcionadas anteriormente en el ejemplo de chord dado en conferencia.

***
## Dependencias

Para correr los scripts solo es necesario tener python 3 y zmq.

***

Para correr una instancia de la clase server es necesario correr el script correspondiente pasándole opcionalmente el puerto por el que escuchará conexiones y la cantidad de bits utilizados para identificar la red.

```bash
$ python3 server.py --port 8080 --bits 5
```

Para correr una instancia de la clase chordNode es necesario correr el script correspondiente pasándole la dirección del server y opcionalmente los puertos a los cuales se relacionarán los sockets que se usaran para las comunicaciones. 

```bash
$ python3 chordNode.py --server localhost:8080 --inPort 5000 --outPort 5001
```

Para correr una instancia de la clase chordClient es necesario correr el script correspondiente pasándole la dirección del server y opcionalmente los puertos a los cuales se relacionarán los sockets que se usarán para las comunicaciones.

```bash
$ python3 chordClient.py --server localhost:8080 --port1 5002 --port2 5003
```

***
## Script doit.py
Se proporcionó además un script para observar el comportamiento de los nodos pero dentro de una misma máquina, este script abre varios hilos desde los cuales correrá distintas instancias de nodos chord y mostrará los resultados a la salida estándar.

Para correr el script es necesario pasarle la cantidad de bits del modelo y la cantidad de nodos que se desea que corran simultáneamente.

```bash
$ python3 doit.py 5 10
```

***
## Dockerfile

Se anexó un dockerfile que se encarga de crear una imagen con zmq y el código del programa dentro. Esto es útil para probar el correcto funcionamiento del programa creando un contenedor para el servidor y otros varios para los nodos, corriendo en ellos el script correspondiente, sin tener que especificar los puertos para las clases chordNode y chordClient, solo la dirección que posee el contenedor del servidor. Para la correcta comunicación se necesita exponer los puertos 8080 y 8081 de cada contenedor a puertos dentro de la máquina host evitando colisiones. 


