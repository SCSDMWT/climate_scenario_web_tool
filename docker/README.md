# Running as a Docker Compose project

The web tool can be run as a Docker Compose project defined in
[`docker-compose.yml`](docker/docker-compose.yaml).
Sensitive environment variables should to be kept out of the git repository.
Create a file called `.env` in the same directory as the `docker-compose.yml`,
with the following content:
```bash
POSTGRES_PASSWORD=<postgres_password>
TILE_LAYER_URL="https://api.os.uk/maps/raster/v1/zxy/Outdoor_27700/{z}/{x}/{y}.png?key=<os_api_key>"
```
Replace `<postgres_password>` with a secure password and `<os_api_key>` with 
a [Ordinance Survey API key](https://docs.os.uk/os-apis/core-concepts/getting-started-with-an-api-project).
Note that `{x}`, `{y}` and  `{z}` should not be changed in the value of `TILE_LAYER_URL`.

Start the Docker containers by running:
```bash
 sudo docker compose up
```
The web tool should now be available at [http://localhost](http://localhost).

## Known Issues

### First run

When the Postgres container is ran for the first time, it takes a while to 
import the hazard data. While
data is being imported there will be many lines printed containing `INSTERT`
to the screen or the container's log.
This could result in the Web app's connection
to the database to fail and fall back to calculating hazard data per request
and slow performance.
When this happens, waiting for the data to be imported and restarting
the containers should resolve the problem.

### Remove old containers

Issues could arise when upgrading the containers to later versions.
All stopped Docker containers can be removed with
```bash
sudo docker rm (docker ps -a -q)
```
After this, running `docker compose up` will reinitialise all containers.
