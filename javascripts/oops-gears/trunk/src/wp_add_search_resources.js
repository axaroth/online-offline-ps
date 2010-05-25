function addSearchResources(contents, store_id){
  //  Remove all resources related to this store  
  databaseServer.execute('DELETE from Resources where StoreId = ?', [store_id]).close();
  
  last_rowid_rs = databaseServer.execute("SELECT max(rowid) from Resources");
  last_rowid = last_rowid_rs.field(0);
  last_rowid_rs.close();
  
  if (last_rowid == null){last_rowid = -1};
  rowid = last_rowid + 1;
  
  for (var i = 0; i < contents.length; i++) {
    path = contents[i]['path']
    title = contents[i]['title']
    text = contents[i]['text']
    document_type = contents[i]['document_type']
    if (document_type == null){document_type = 'n/a';};
    
    databaseServer.execute('INSERT INTO Resources (rowid, StoreId, Url, Title, SearchableText, DocumentType) VALUES ' +
      '(?, ?, ?, ?, ?, ?)',
      [rowid, store_id, path, title, text, document_type]).close();  
    rowid++;
  }  ;
};

var wp = google.gears.workerPool;
wp.onmessage = function(a, b, message){
    data = message.body; // this is a list of json
    databaseServer = google.gears.factory.create('beta.database');
    databaseServer.open('search_db');
    
    // add resources
    databaseServer.execute('BEGIN').close();  
    for (i=0; i<data.length; i++){
        addSearchResources(data[i]['contents'], data[i]['storeid']);
    };
    databaseServer.execute('COMMIT').close();

    wp.sendMessage('All search resources updated', message.sender);
};



