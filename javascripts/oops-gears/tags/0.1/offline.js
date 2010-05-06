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


function showProgress(details){
  $('#progress').append(this.name + " store onprogress " + details.filesComplete + 
  "/" + details.filesTotal)
}

function printResultRow(map, index){
  var searchResults = $('#search-results')
  result_link = $('<a />');
  result_link.attr('href', map['Url']).html(map['Title']);
  doctype = map['DocumentType']
  dt_tag = null;
  if (doctype != null && doctype != 'n/a'){
    dt_tag = $('<div class="discreet">Document Type: </div>');
    dt_tag.append('<span class="doctype">'+doctype+'</span>');
  }
  searchResults.append($('<li />').html(result_link).append(dt_tag));
}


function showOfflineSearchResults(){
  var SearchableText = $.getURLParam('SearchableText')
  var DocumentType = $.getURLParam('document_type')
  var searchResults = $('#search-results')
  
  databaseServer = google.gears.factory.create('beta.database');
  databaseServer.open('search_db');

  if (SearchableText!=null && SearchableText!='') {
    $('#message').hide();
    $('#annexes').show();
    $('#search-term').html('for '+SearchableText);
    if (DocumentType != null && DocumentType != 'all'){
        search_query = 'SELECT Url, Title, DocumentType FROM Resources WHERE SearchableText MATCH ? and DocumentType = ?'
        $('#search-doctype').html(DocumentType)
        forEachRow(databaseServer, search_query, [SearchableText, DocumentType], printResultRow)
    } else {
        search_query = 'SELECT Url, Title, DocumentType FROM Resources WHERE SearchableText MATCH ?'
        forEachRow(databaseServer, search_query, [SearchableText], printResultRow)
    }
  }
}


function addSearchResources(contents, store_id){
  //  Remove all resources related to this store  
  databaseServer.execute('DELETE from Resources where StoreId = ?', 
      [store_id]).close();
  
  last_rowid_rs = databaseServer.execute("SELECT max(rowid) from Resources")
  last_rowid = last_rowid_rs.field(0)
  last_rowid_rs.close()
  
  if (last_rowid == null){
      last_rowid = -1
  }
  rowid = last_rowid + 1;
  
  for (var i = 0; i < contents.length; i++) {
    databaseServer.execute('BEGIN').close();
    path = contents[i]['path']
    title = contents[i]['title']
    text = contents[i]['text']
    document_type = contents[i]['document_type']
    if (document_type == null){
        document_type = 'n/a';
    }
    
    databaseServer.execute('INSERT INTO Resources (rowid, StoreId, Url, Title, SearchableText, DocumentType) VALUES ' +
      '(?, ?, ?, ?, ?, ?)',
      [rowid, store_id, path, title, text, document_type]).close();  
    databaseServer.execute('COMMIT').close();
    rowid++;
  }  

}


function updateSearchDB(store_id){
  // get json for searchabletext
  searchabletext_url = stores[store_id]['store'].manifestUrl.replace('manifest.json', 
    'searchabletext.json')

  // update resources    
  $.getJSON(searchabletext_url, function(data, status){
    addSearchResources(data['contents'], store_id)
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
      $('#gears-messages .enable').hide();
      $('#gears-messages .status').show();
  }
  
}


function checkForUpdate(){
  $.each(stores, function(id){
    stores[id]['store'].checkForUpdate();
  });
  return false;
}


function setGearsMessages(){
  $('#gears-messages .install').hide();
  $('#gears-messages .enable').hide();
  $('#gears-messages .status').hide();
   $('label.progress').hide();
   $('.progressBar').hide();
  
  if (!window.google || !google.gears){
    $('#gears-messages .install a.offlineDownload').attr('href', download_url);
    $('#gears-messages .install').show();
  } else {
  
    $('#gears-messages .enable a.offlineEnable').click(function(){createStore();return false;});
    $('#gears-messages .status a.offlineUpdate').click(function(){checkForUpdate();$(this).addClass('checked'); return false;});  
    
    if (!google.gears.factory.hasPermission){
      $('#gears-messages .enable').show();
    } else {
      $('#gears-messages .status').show();
    }
    
  }
  
}


$(document).ready(function(){
  setGearsMessages();
});   
