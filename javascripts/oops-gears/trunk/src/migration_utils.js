function upgradeSearchDBWithoutDocumentTypes(){
    // from unreleased version to 0.1
    // used to migrate old Resource table w/o DocumentType Column

    // has gears enabled?
    if (!window.google || !google.gears){return null};
    if (!google.gears.factory.hasPermission){return null};
    databaseServer = google.gears.factory.create('beta.database');
    databaseServer.open('search_db'); 

    // has old table?
    rs = databaseServer.execute("SELECT sql FROM sqlite_master WHERE tbl_name = 'Resources'");
    if (!rs.isValidRow()){return null};
    var has_documenttype = rs.field(0).indexOf('DocumentType') != -1;
    rs.close();
    if (has_documenttype){return null};
    
    //recreate table
    databaseServer.execute("DROP TABLE Resources");
    databaseServer.execute('CREATE VIRTUAL TABLE Resources USING fts2(StoreId, Url, Title, SearchableText, DocumentType)');
    
    // get all searchabletext json and update resources table    
    var search_data = [];
    $.getJSON('manifest-versions.json', function(data){
        $.each(data, function(store_id, data){
            url = data['url'].replace('manifest.json', 'searchabletext.json');
            $.ajax({url: url, async: false, dataType: 'json', 
                    success:  function(sdata){search_data.push(sdata)}
            });
        });
        workerPool.sendMessage(search_data, addSearchResourcesWorker);
    });
};

