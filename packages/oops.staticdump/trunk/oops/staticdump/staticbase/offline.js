SITE_NAME = 'WFP Logistic Operations Guide'
GEARS_MESSAGE = 'Install Gears to enable offline features'
SITE_URL = $('base').attr('href')
RETURN_URL = SITE_URL + 'offline.html'
GEARS_ICON = SITE_URL + '/gears_icon.png'
STORE_NAME = 'wfp_log_offline'

var download_url = 'http://gears.google.com/?action=install&message=' +
GEARS_MESSAGE +'&name=' + SITE_NAME + '&return=' + SITE_URL + '&icon_src='+GEARS_ICON

var localServer;
var databaseServer;
var stores = {};

function debug(val){
    $('<p>x ' + val + ' x</p>').appendTo('#debug');    
}

function showProgress(details){
  $('#progress').append(this.name + " store onprogress " + details.filesComplete + "/" + details.filesTotal)
}

// DB utils
/**
 * For each row in the result set f will be called with the following
 * parameters: row (map where the column names are the key) and rowIndex.
 *
 * @param {Object} db The database object
 * @param {String} sql The SQL statement to execute
 * @param {Array} args query params
 * @param {Function} f Function to call for each row
 */
function forEachRow(db, sql, args, f) {
  var rs = databaseServer.execute(sql, args);
  try {
    var rowIndex = 0;
    var cols = rs.fieldCount();
    var colNames = [];
    for (var i = 0; i < cols; i++) {
      colNames.push(rs.fieldName(i));
    }

    var rowMap;
    while (rs.isValidRow()) {
      rowMap = {};
      for (var i = 0; i < cols; i++) {
        rowMap[colNames[i]] = rs.field(i);
      }
      f.call(null, rowMap, rowIndex);
      rs.next();
      rowIndex++;
    }
  } finally {
    rs.close();
  }
}

function showOfflineSearchResults(){
  var SearchableText = $.getURLParam('SearchableText')
  var searchResults = $('#search-results')
  
  databaseServer = google.gears.factory.create('beta.database');
  databaseServer.open('search_db');

  if (SearchableText!=null) {
    $('#search-term').html(SearchableText)
    forEachRow(databaseServer, 'SELECT Url, Title FROM Resources WHERE SearchableText MATCH ?',
      [SearchableText], function(map, index) {
        result_link = $('<a />');
        result_link.attr('href', map['Url']).html(map['Title']);;
        searchResults.append($('<li />').html(result_link));
      }
    );
  }
}


function addSearchResources(contents, store_id){
  //  Remove all resources related to this store   
  databaseServer.execute('DELETE from Resources where StoreId = ?', 
      [store_id]).close()
  
  for (var i = 0; i < contents.length; i++) {
    databaseServer.execute('BEGIN').close();
    databaseServer.execute('INSERT INTO Resources (rowid, StoreId, Url, Title, SearchableText) VALUES ' +
      '(LAST_INSERT_ROWID(), ?, ?, ?, ?)',
      [store_id, contents[i]['path'], contents[i]['title'], contents[i]['text']]).close();  
    databaseServer.execute('COMMIT').close();
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
  stores[id]['store'].manifestUrl = data['url'];
  stores[id]['version'] = data['version']
  stores[id]['title'] = data['title']
  
  // progress details
  stores[id]['store'].onprogress = function(details){
    $('#' + id + ' .progress').html('progress: ' +details.filesComplete + "/" + details.filesTotal)
  }
  
  // oncomplete update search db
  stores[id]['store'].oncomplete = function(details){
    if (details.newVersion){updateSearchDB(id);}
  }
  
  //lastUpdate
  lastUpdateCheckTime = stores[id]['store'].lastUpdateCheckTime
  if (lastUpdateCheckTime != 0 ){
    now = new Date()
    date = new Date(now.getTime() + (lastUpdateCheckTime/1000))

    $('#' + id + ' .lastUpdate').html('Last update: ' + date.getDate() + '/' +
     date.getMonth() + '/' + date.getFullYear() + ' ' + date.getHours() + ':' +
     date.getMinutes())
  }
  
  // status
  var timerId = window.setInterval(function() {
    status = $('#' + id + ' .actions')
    if (stores[id]['store'].currentVersion) {
      window.clearInterval(timerId);
      status.html('All data available (version: ' +
        stores[id]['store'].currentVersion +')')
    } else if (stores[id]['store'].updateStatus == 3) {
      status.html("Error: " + stores[id]['store'].lastErrorMessage);
    } else if (stores[id]['store'].updateStatus == 1) {
      status.html("Checking updates");
    } else if (stores[id]['store'].updateStatus == 2) {
      status.html("Downloading updates");
    }
  }, 500);
    
  
}

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
        // XXX non so come controllare la sua presenza!
        databaseServer.execute('CREATE VIRTUAL TABLE Resources USING fts2(StoreId, Url, Title, SearchableText)');
      } catch (ex){
      }
      
      // create a store for each manifest
      $.getJSON('manifest-versions.json', function(data){$.each(data, initStore)});    
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
  })
  return false;
}


function setGearsMessages(){
  $('#gears-messages .install').hide();
  $('#gears-messages .enable').hide();
  $('#gears-messages .status').hide();
  
  if (!window.google || !google.gears){
    $('#gears-messages .install a.offlineDownload').attr('href', download_url);
    $('#gears-messages .install').show();
  } else {
  
    $('#gears-messages .enable a.offlineEnable').click(function(){createStore();return false;});
    $('#gears-messages .status a.offlineUpdate').click(function(){checkForUpdate(); return false;});  
    
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

