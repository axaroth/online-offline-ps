//TODO refactor printResultRow and  showOfflineSearchResults for online search
//TODO create two functions with gears and witout gear that returns the same
//     data structure
//     without gears: ajax call to external service (search_online) with
//     SearchableText and document_type parameters that returns results in JSON
//     format
//TODO evalute use of jquery templates for dom manipulation (results printing)
//TODO put search related stuff in oops.search.js
var SearchableText;
var DocumentType;
var searchURL = '/search_online'

function offlineSearchResults(){
  console.log("offline");
  databaseServer = google.gears.factory.create('beta.database');
  databaseServer.open('search_db');
  var data = []
  if (SearchableText!=null && SearchableText!='') {
    if (DocumentType != null && DocumentType != 'all'){
        search_query = 'SELECT Url, Title, DocumentType FROM Resources WHERE SearchableText MATCH ? and DocumentType = ?'
        forEachRow(databaseServer, search_query, [SearchableText, DocumentType], function(item,index){
            data[index] = {
                        'Url':item['Url'],
                        'Title':item['Title'],
                        'DocumentType':item['DocumentType']
                        };
        })
    } else {
        search_query = 'SELECT Url, Title, DocumentType FROM Resources WHERE SearchableText MATCH ?'
        forEachRow(databaseServer, search_query, [SearchableText], function(item,index){
            data[index] = {
                        'Url':item['Url'],
                        'Title':item['Title'],
                        'DocumentType':item['DocumentType']
                        };
        })
    }
  }
  return data;
}


function onlineSearchResults(){
    console.log("online");
    $.getJSON(searchURL,
            {'SearchTerm':SearchableText,'document_type':DocumentType},
            function(data){
              $.each(data.results,function(i,item){
                  data_item = {
                      'Url':item.path,
                      'Title':item.title,
                      'DocumentType':item.document_type
                      };
                  printResultRow(i,data_item)
              })
            })
}


function printResultRow(index, map){  
  var searchResults = $('#search-results')
  result_link = $('<a />');
  result_link.attr('href', map['Url']).html(map['Title']);
  doctype = map['DocumentType']
  dt_tag = null;
  if (doctype != null && doctype != 'n/a' && doctype !=''){
    dt_tag = $('<div class="discreet">Document Type: </div>');
    dt_tag.append('<span class="doctype">'+doctype+'</span>');
  }
  searchResults.append($('<li />').html(result_link).append(dt_tag));
}

$(document).ready(function(){
    var results = null;
    SearchableText = $.getURLParam('SearchableText')
    DocumentType = $.getURLParam('document_type')
  
    if (google.gears && google.gears.factory.hasPermission){
      results = offlineSearchResults();
      if (results){
        $.each(results,function(i,item){
            printResultRow(i,item)
        })
      }
    }else{
      onlineSearchResults();
    }
    
});   

