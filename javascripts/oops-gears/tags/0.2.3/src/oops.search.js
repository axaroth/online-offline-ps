/***
JQUERY PLUGIN oopsSearch

plugin with callback to search oops engine during online and offline mode with Google Gears

This write the result on node selected and with callback is possibile
work on dom created

params are url paramaters to get from request to interrogate oops system
sample:
$('#search-results').oopsSearch({
  searchabletext : 'SearchableText',
  documenttype : 'document_type'
},function(){docTypeValue()});

****/

var SearchableText;
var DocumentType;
var searchURL = '/search_online'
var thisObj;

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


function printResultRow(index, map){
  var searchResults = thisObj
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



(function($){
  
  $.fn.oopsSearch = function(options,callback){
    setting = jQuery.extend({
      searchabletext : 'SearchableText',
      documenttype : 'document_type'
      
    },options);
    var results = null;
    SearchableText = $.getURLParam(setting.searchabletext)
    DocumentType = $.getURLParam(setting.documenttype)
    thisObj = this
  
    //TODO refactor this; oops API?
    var useGears;
    if (!window.google || !google.gears){
      useGears = false;
    } else{
      if (!google.gears.factory.hasPermission){
        useGears = false;
      } else {
        useGears = true;  
      }
    }
    
    if (useGears == true){
      results = offlineSearchResults();
      if (results){
        $.each(results,function(i,item){
            printResultRow(i,item)
        })
        if($.isFunction(callback)){
            callback.call(thisObj)
          }
      }
    }else{
      //online search
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
          
          if($.isFunction(callback)){
            callback.call(thisObj)
          }
    
        })
    }
    
    return this;
  };
  
  
})(jQuery);
