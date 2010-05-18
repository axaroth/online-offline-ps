/**
**  OOPS.STATUS.JS
**  
**  parameters:
**  {
**  'time':30, [seconds between ping]
**  'elementId':'onlineStatus', [dom element id to add message]
**  'onlineMess':'online message', [html is available]
**  'offlineMess':'offline message', [html is available]
**  'onlineClass':'online', [class relative to status]
**  'offlineClass':'offline',
**  }
**
**  sample call:
**  <script dump="true" type="text/javascript">
**    $('#onlineStatus').ready(function(){status({'time':30});});
**  </script>
**/


var elementId = 'onlineStatus';
var TIME_BETWEEN_PINGS = 10*1000;
var PING_TIMEOUT_SECONDS = 1*1000;
var onlineMess = "[Server Accessible]"
var offlineMess = "[Server Inaccessible]"
var onlineClass = "online"
var offlineClass = "offline"
var element = null;
var resource = "http://"+location.host+"/fake.html?q="+ Math.floor(Math.random() * 100000); 

function pingSuccess(){
  try{  
    request=new XMLHttpRequest();
    request.open("GET",resource,false);
    request.send("");
    element.innerHTML = onlineMess;
    element.className = onlineClass; 
  }catch(err){
    element.innerHTML = offlineMess;
    element.className = offlineClass;
  }

}

function status(properties){
    element = document.getElementById(elementId);
    if (element != null){
        if(properties.time){TIME_BETWEEN_PINGS = properties.time * 1000;}
        if(properties.elementId){elementId = properties.elementId;}
        if(properties.onlineMess){onlineMess = properties.onlineMess;}
        if(properties.offlineMess){offlineMess = properties.offlineMess;}
        if(properties.onlineClass){onlineClass = properties.onlineClass;}
        if(properties.offlineClass){offlineClass = properties.offlineClass;}
        isOnline();
    }
}


function isOnline(){
    window.setTimeout("pingSuccess()",PING_TIMEOUT_SECONDS);
    window.setTimeout("isOnline()",TIME_BETWEEN_PINGS);
}

