## DESCRIPTION
`covid_dashboard` is a python application based on a `dash` framework.
It presents a user interface to analyze data gathered from:
[covid19api.com](https://documenter.getpostman.com/view/10808728/SzS8rjbc?version=latest)

Dashboard is available via docker: `amasend/covid_dashboard:1.3`  

## HOW TO RUN

You need to install a docker on your system, please refer to `docker` installation process:
 https://docs.docker.com/get-docker/  

After docker installation just run:
`docker run -ti -p 8050:8050/tcp amasend/covid_dashboard:1.3`
and go to `127.0.0.1:8050` in your browser.


## POLAND vs GREECE v1.3
![image](https://raw.githubusercontent.com/amasend/covid_dashboard/master/screens/poland_greece_1.3.png)

## POLAND vs UKRAINE v1.2
![image](https://raw.githubusercontent.com/amasend/covid_dashboard/master/screens/poland_ukraine_1.2.png)


## CHINA DAILY % CHANGE 1.1
![image](https://raw.githubusercontent.com/amasend/covid_dashboard/master/screens/china_pct_daily_change.png)

## Main Screen 1.0
![image](https://raw.githubusercontent.com/amasend/covid_dashboard/master/screens/main.png)

## POLAND vs CHINA 1.0
![image](https://raw.githubusercontent.com/amasend/covid_dashboard/master/screens/poland_china.png)

## POLAND vs CHINA logarithmic 1.0
![image](https://raw.githubusercontent.com/amasend/covid_dashboard/master/screens/poland_china_log.png)

## POLAND vs CHINA logarithmic started from ~ 100 confirmed cases 1.0
![image](https://raw.githubusercontent.com/amasend/covid_dashboard/master/screens/poland_china_log_100.png)

## Docker container release history:
`1.4` - added UI revision to be persisted, corrected some locations on map, change in log scale and yaxis info, updated hover info for heat-map  
`1.3` - added heat-map with world data  
`1.2` - changed main screen with descriptions, added option to select bar graph type (normal diff or with %)  
`1.1` - added support for bar plots (only main selected country), 
bar plots show a daily % change for each category of data  
`1.0` - initial base container