## DESCRIPTION
`covid_dashboard` is an python application based on a `dash` framework.
It presents a user interface to analyze data gathered from:
[covid19api.com](https://documenter.getpostman.com/view/10808728/SzS8rjbc?version=latest)

Dashboard is available via docker: `amasend/covid_dashboard:1.0`  

## HOW TO RUN INSTRUCTION

You need to install a docker on your system, please refer to `docker` installation process:
 https://docs.docker.com/get-docker/  

After docker installation just run:
`docker run -ti -p 8050:8050/tcp amasend/covid_dashboard:1.0`

