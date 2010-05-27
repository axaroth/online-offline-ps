/**
**  OOPS.STATUS.JS
**  
**  parameters:
**  {
**  'time':30, [seconds between ping]
**  'idOnline':'on', [dom element id to show when online]
**  'idOffline':'off', [dom element id to show when offline]
**  }
**
**  sample call:
 $('#onlineStatus').oopsStatus({
				'time':30,
				'idOnline':'oops_online',
				'idOffline':'oops_offline'});
**/
var TIME_BETWEEN_PINGS = 10*1000;
var PING_TIMEOUT_SECONDS = 1*1000;
var onlineNode;
var offlineNode;
var containerObj;
var resource = "http://"+location.host+"/fake.html?q="+ Math.floor(Math.random() * 100000); 

function setOnline(){
  console.log("online")
  $(offlineNode).removeClass('oops_active').hide();
  $(onlineNode).addClass('oops_active').show();
  containerObj.removeClass('oops_offline');
  containerObj.addClass('oops_online');
}

function setOffline(){
  console.log("offline")
  $(onlineNode).removeClass('oops_active').hide();
  $(offlineNode).addClass('oops_active').show();
  containerObj.removeClass('oops_online');
  containerObj.addClass('oops_offline');
}
function pingSuccess(){
  try{  
    var request = google.gears.factory.create('beta.httprequest');
    request.open('GET', resource);
    //2(sent),3(interactive),4(complete)
    var states = new Array(); 
    request.onreadystatechange = function() {
      try{
        states.push(request.readyState);
        if (request.readyState == 4) {
          if (request.status){setOnline()}
        }
      }catch(err){
        setOffline()
      }
    };
    request.send("")
  }catch(err){
    console.log(err)
    setOffline()
  }
}


function isOnline(){
    window.setTimeout("pingSuccess()",PING_TIMEOUT_SECONDS);
    window.setTimeout("isOnline()",TIME_BETWEEN_PINGS);
}



(function($){
  $.fn.oopsStatus = function(options,callback){
    setting = jQuery.extend({
      time : 10,
      idOnline : 'oops_online',
      idOffline : 'oops_offline'
    },options);
    
    TIME_BETWEEN_PINGS = setting.time * 1000;
    onlineNode = '#' + setting.idOnline
    offlineNode = '#' + setting.idOffline
    containerObj = this
    isOnline()
    
    return this;
  };
})(jQuery);