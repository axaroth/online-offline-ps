//UNCOMMENT OR DEFINE THE FOLLOWING VARIABLES

//SITE_NAME = 'OOPS'
//GEARS_MESSAGE = 'Install Gears to enable offline features'
//SITE_URL = $('base').attr('href')
//RETURN_URL = SITE_URL + 'offline.html'
//GEARS_ICON = SITE_URL + 'gears_icon.png'
//STORE_NAME = 'oops_offline'

// DO NOT MODIFY FROM HERE

var download_url = 'http://gears.google.com/?action=install&message=' +
GEARS_MESSAGE +'&name=' + SITE_NAME + '&return=' + SITE_URL + '&icon_src='+GEARS_ICON
var localServer;
var databaseServer;
var stores = {};
var workerPool;
var addSearchResourcesWorker;

function showProgress(details){
  $('#progress').append(this.name + " store onprogress " + details.filesComplete + 
  "/" + details.filesTotal)
}


function updateSearchDB(store_id){
  // get json for searchabletext
  searchabletext_url = stores[store_id]['store'].manifestUrl.replace('manifest.json', 
    'searchabletext.json')

  // update resources    
  $.getJSON(searchabletext_url, function(data, status){
    workerPool.sendMessage([data], addSearchResourcesWorker);
  })
}


function initStore(id,data){
  stores[id] = {}
  stores[id]['store'] = localServer.createManagedStore(STORE_NAME+id);
  stores[id]['store'].manifestUrl = SITE_URL + data['url'].substr(1);
  stores[id]['version'] = data['version']
  stores[id]['title'] = data['title']
  
  // progress details
  stores[id]['store'].onprogress = function(details){
    $('#' + id + ' label.progress').show();
    $('#' + id + ' span.progress').html(details.filesComplete + "/" + details.filesTotal);
    perc = (details.filesComplete/details.filesTotal)*100;
    $('#' + id + ' .progressBar span').css('width',perc+'%');
    $('#' + id + ' .progressBar').show();
  }
  
  // oncomplete update search db
  stores[id]['store'].oncomplete = function(details){
    if (details.newVersion){updateSearchDB(id);}
      $(".button").text("updated");
  }

  // status
  var timerId = window.setInterval(function() {
    status = '#' + id + ' .actions';
    if (stores[id]['store'].currentVersion) {
      window.clearInterval(timerId);
      $('.availability').show();
      $(status).html('<label>Current version: </label>'+stores[id]['store'].currentVersion);
    } else if (stores[id]['store'].updateStatus == 3) {
      $(status).html("Error: " + stores[id]['store'].lastErrorMessage);
    } else if (stores[id]['store'].updateStatus == 1) {
      $(status).html("Checking updates");
    } else if (stores[id]['store'].updateStatus == 2) {
     $(status).html("Downloading updates");
    }
  }, 500);
    
  
}

// XXX there is a lot of duplicated code here!
function initStores(){ 
  if (!window.google || !google.gears) {
    return;
  } else {
    if (google.gears.factory.hasPermission){
      // create a localServer
      localServer = google.gears.factory.create("beta.localserver");
      
      // create a database for search
      databaseServer = google.gears.factory.create('beta.database');
      databaseServer.open('search_db');
      try {
        // XXX how to check if the table already exists?
        databaseServer.execute('CREATE VIRTUAL TABLE Resources USING fts2(StoreId, Url, Title, SearchableText, DocumentType)');
      } catch (ex){
      }
      
    // create a store for each manifest
    $.getJSON('manifest-versions.json', function(data){$.each(data, initStore)});
    }
  }
  return;
}


function initStoresByIds(ids){
  if (!window.google || !google.gears) {
    return;
  } else {
    if (google.gears.factory.hasPermission){
      // create a localServer
      localServer = google.gears.factory.create("beta.localserver");
      
      // create a database for search
      databaseServer = google.gears.factory.create('beta.database');
      databaseServer.open('search_db');
      try {
        // XXX how to check if the table already exists?
        databaseServer.execute('CREATE VIRTUAL TABLE Resources USING fts2(StoreId, Url, Title, SearchableText, DocumentType)');
      } catch (ex){
      }

      // create a worker pool for search
      workerPool = google.gears.factory.create('beta.workerpool');
      workerPool.onmessage = function(a, b, message) {
          console.log('Upgrade status: ' + message.body);
      };
      addSearchResourcesWorker = workerPool.createWorkerFromUrl(SITE_URL + 'wp_add_search_resources.js');
      
     $.getJSON('manifest-versions.json', function(data){
        $.each(data,function(i,data){
            if($.inArray(i,ids)>-1){initStore(i,data);};
        });		
     });
    }
  }
  return;
}


function createStore(){

  if (!google.gears.factory.hasPermission){
    google.gears.factory.getPermission(siteName=SITE_NAME, imageUrl=GEARS_ICON, 
                                       extraMessage=GEARS_MESSAGE);
  }
  
  if (google.gears.factory.hasPermission){  
      initStores()
      $('.gears-messages .enable').hide();
      $('.gears-messages .status').show();
  }
  
}


function checkForUpdate(){
  $.each(stores, function(id){
    stores[id]['store'].checkForUpdate();
  });
  return false;
}


function setGearsMessages(){
  $('.gears-messages .install').hide();
  $('.gears-messages .enable').hide();
  $('.gears-messages .status').hide();
   $('label.progress').hide();
   $('.progressBar').hide();
  
  if (!window.google || !google.gears){
    $('.gears-messages .install a.offlineDownload').attr('href', download_url);
    $('.gears-messages .install').show();
  } else {
  
    $('gears-messages .enable a.offlineEnable').click(function(){createStore();return false;});
    $('.gears-messages .status a.offlineUpdate').click(function(){checkForUpdate();$(this).addClass('checked'); return false;});  
    
    if (!google.gears.factory.hasPermission){
      $('.gears-messages .enable').show();
    } else {
      $('.gears-messages .status').show();
    }
    
  }
  
}


$(document).ready(function(){
  setGearsMessages();
});   

