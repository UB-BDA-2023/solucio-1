## Pràctica 5: Bases de dades de series temporals

Benvingut/da a la cinquena pràctica de l'assignatura de Bases de dades. Aquesta pràctica parteix de la plantilla de la pràctica anterior. Com sabeu tenim una API REST que ens permet crear, esborrar, modificar i consultar les dades d'una aplicació de sensors. En aquesta pràctica volem ampliar el cas d'ús de la nostra API per a poder buscar sobre text.

## Com començar?

Per començar, necessitaràs clonar aquest repositori. Pots fer-ho amb el següent comandament:

```bash
git clone url-del-teu-assignment
```

Recorda que fem servir docker-compose per a executar l'entorn de desenvolupament i provar el que anem desenvolupant. Per a arrancar l'entorn de desenvolupament, pots fer servir el següent comandament:

```bash
docker-compose up -d
```

Recorda parar l'entorn de desenvolupament de la setmana passada abans de començar a treballar amb aquesta pràctica.

Si vols parar l'entorn de desenvolupament, pots fer servir el següent comandament:

```bash
docker-compose down
```

Cal que tinguis en compte que si fas servir aquest comandament, no esborraràs tota la informació que tinguis a la base de dades, ja que per defecte down només esborra els conteidors i la xarxa entre ells. Si vols esborrar tota la informació que tinguis a la base de dades, pots fer servir el següent comandament:

```bash
docker-compose down -v
```

**Important**: Quan executem `docker-compose up`, Docker construeix una imatge de Docker amb FastAPI amb una fotografia estàtica del codi que tenim al directori. Això vol dir que si modifiquem el codi, no es veurà reflexat a l'entorn de desenvolupament. Per això, cal que executem docker-compose up cada cop que modifiquem el codi. Si no ho fem, no veurem els canvis que haguem fet.


### Context


Fins ara hem vist com podem guardar de manera més eficient les dades simples amb moltes lectures i escriptures, com podem guardar dades semi-estructurades per a poder guardar sensors de diferents tipus i a poder cercar per a camps de text de la descripció o el nom del sensor.

Hem creat un bon gestor de sensors! Però no és gaire útil per als usuaris... El fet de només guardar la última dada que envia el sensor fa que no es pugui fer cap mena d'anàlisi de les dades. Per exemple, si volem saber l'evolució de les temperatures registrades per un dels sensors, no podem fer-ho.

Així doncs, el que farem en aquesta pràctica és guardar les dades de manera temporalitzada, és a dir, guardar les dades de manera que puguem fer consultes sobre les dades que s'han guardat en un interval de temps determinat.

Farem servir `TimescaleDB`, una base de dades de series temporals que està basada en PostgreSQL. Aquesta base de dades té una gran quantitat de funcionalitats que ens permetran fer consultes molt eficients sobre les dades que guardem.

### Objectius

* Crear una nova instància de `TimescaleDB`.
* Crear una nova instància de [`YoYo`](https://ollycope.com/software/yoyo/latest/) per a poder crear migracions sobre Timescale (mantenint la instancia que genera la taula principal a Potgres).
* Crear una nova migració per a crear una nova taula (`sensor_data`) que guardi les dades de manera temporalitzada. 
* Modificar la funcionalitat de l'endpoint de POST `("/{sensor_id}/data")` per a que guardi les dades passades a la nova taula.
* Modificar l'endpoint de GET `("/{sensor_id}/data")` per a que busqui les dades a la nova taula. Aquest endpoint haurà de treballar amb els següents paràmetres:
  * `from`: La data d'inici de l'interval de temps que volem consultar.
  * `to`: La data de fi de l'interval de temps que volem consultar.
  * `bucket`: La mida de les agregacions de temps a fer (els valors possibles seràn: `hour`, `day`, `week`, `month`, `year`).


## Què hem de fer?

Abans de res, explora el codi que s'ha creat per aquesta pràctica. 

### Punt 1: Mirar i Provar els tests

Tal i com vàrem fer a la setmana passada, hem creat una sèrie de tests per a comprovar que el codi que hem creat funciona correctament. Per a executar els tests, pots fer servir el següent comandament:

```bash
docker exec bdda_api sh -c "pytest"
```

També pots comprovar els tests a l'autograding de github, aquesta setmana la puntuació màxima és de 200 punts i hi ha un total d' `20` tests amb un valor de `10` punts cadascun:

Veuràs que `20` tests fallen. Això és normal, ja que encara no hem implementat el codi que passa els tests.

### Punt 2: Mirar els endpoints al fitxer controller.py:

En aquesta pràctica hem modificat l'api del següent endpoint:
`@router.get("/{sensor_id}/data")`
Ara rebrà com a paràmetres:
  * `from`: La data d'inici de l'interval de temps que volem consultar.
  * `to`: La data de fi de l'interval de temps que volem consultar.
  * `bucket`: La mida de les agregacions de temps a fer (els valors possibles seràn: `hour`, `day`, `week`, `month`, `year`).
  

### Punt 3: Connectar-nos a TimeScale

Per accedir a TimeScale farem servir el client de python psycopg2 per a Postgres ja que Timescale és una extensió d'aquesta base de dades realacional 

En la classe `TimeScale.py` podeu veure les crides als mètodes bàsics per a fer interactuar amb TimeScale:

```python
	import psycopg2
import os
class Timescale:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ.get("TS_HOST"),
            port=os.environ.get("TS_PORT"),
            user=os.environ.get("TS_USER"),
            password=os.environ.get("TS_PASSWORD"),
            database=os.environ.get("TS_DBNAME"))
        self.cursor = self.conn.cursor()
        
    def getCursor(self):
            return self.cursor

    def close(self):
        self.cursor.close()
        self.conn.close()
    
    def ping(self):
        return self.conn.ping()
    
    def execute(self, query):
       return self.cursor.execute(query)
    
    def delete(self, table):
        self.cursor.execute("DELETE FROM " + table)
        self.conn.commit()
```


### Punt 4: Codificar els endpoints de controller.py

* Codifiqueu de nou  els endpoints de `controller.py`de tal forma que utilitzin TimeScale.

A `controller.py` teniu una connexió a TimeScale per fer servir en els dos endpoints necessaris. 
Per a crear la taula `sensor_data` a TimeScale podeu crear una nova carpeta `migrationsTS` i col·locar allà la definició de la taula. Recordeu que a Timescale hem de convertir aquesta taula a *hypertable*. (Reviseu la documentació de [TimescaleDB](https://docs.timescale.com/api/latest/)).

* Per executar la creació d'aquesta nova migració ho podeu fer desde línia de comandes, cridant-ho des del `command` de `docker-compose`, fixeu-vos com ara s'està fent per la base de dades de postgres.
 O alternativament sense tocar el docker-compose es pot fer des de codi python amb la lliberia [`yoyo`](https://ollycope.com/software/yoyo/latest/), i executant-ho des del `main.py` abans de començar l'app.

* Haureu de modificar els mètodes a `repository.py` per tal d'implementar aquests canvis.

Per a fer les agregacions per a diferents unitats de temps, hem de fer servir vistes materialitzades.
Com que volem que siguin en temps real, hem de fer servir les *continuous_aggregates* de TimescaleDB. (Revisar documentació de [TimescaleDB](https://docs.timescale.com/api/latest/)).

 * Com sempre fixeu-vos bé amb els `schemas` que heu de fer servir per a que els `payloads` de l'API de fastAPI funcioni adequadament no podeu canviar aquests schemas. 




### Punt 5: Executar els tests

Ara que ja has implementat les rutes, pots tornar a executar els tests per a veure si has fet bé les coses. Per fer-ho, has de fer servir el següent comandament:

```bash
docker exec bdda_api sh -c "pytest"
```

Si tot ha anat bé, hauries de veure que tots els tests passen.

## Entrega

Durant les pràctiques farem servir GitHub Classroom per gestionar les entregues. Per tal de clonar el repositori ja has hagut d'acceptar l'assignment a GitHub Classroom. Per entregar la pràctica has de pujar els canvis al teu repositori de GitHub Classroom. El repositori conté els tests i s'executa automàticament cada vegada que puges els canvis al teu repositori. Si tots els tests passen, la pràctica està correctament entregada.

Per pujar els canvis al teu repositori, has de fer servir el següent comandament:

```bash
git add .
git commit -m "Missatge de commit"
git push
```

## Puntuació

Aquesta pràctica té una puntuació màxima de 10 punts. La puntuació es repartirà de la següent manera:

- 6 punts: Correcta execució dels tests. Important, per a que la pràctica sigui avaluable heu d'aconseguir que com a mínim `17` dels `20` tests s'executin correctament.
- 2 punts: L'estil del codi i la seva estructura i documentació.
- 2 punts: La correcta implementació de la funcionalitat.

## Qüestionari d'avaluació de cada pràctica

Cada pràctica té un qüestionari d'avaluació. Aquest qüestionari ens permet avaluar el coneixement teòric i de comprensió de la pràctica. És obligatori i forma part de l'avaluació continua de l'assignatura. Per contestar el qüestionari, has d'anar al campus virtual de l'assignatura i anar a la secció de qüestionaris.
 






