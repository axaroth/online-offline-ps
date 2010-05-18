var elementId = 'serverStatus';
var TIME_BETWEEN_PINGS = 10*1000;
var PING_TIMEOUT_SECONDS = 1*1000;
var mess_online = "[Server Accessible]"
var mess_offline = "[Server Inaccessible]"
var element = null;
var resource = "http://"+location.host+"/fake.html?q="+ Math.floor(Math.random() * 100000); 

function pingSuccess(){
  try{  
    request=new XMLHttpRequest();
    request.open("GET",resource,false);
    request.send("");
    element.innerHTML = mess_online;
  }catch(err){
    element.innerHTML = mess_offline;
  }

}

function status(properties){
    element = document.getElementById(elementId);
    if (element != null){
        if(properties.time){TIME_BETWEEN_PINGS = properties.time * 1000;}
        if(properties.elementId){elementId = properties.elementId;}
        if(properties.online){mess_online = properties.online;}
        if(properties.offline){mess_offline = properties.offline;}
        isOnline();
    }
}


function isOnline(){
    window.setTimeout("pingSuccess()",PING_TIMEOUT_SECONDS);
    window.setTimeout("isOnline()",TIME_BETWEEN_PINGS);
}

