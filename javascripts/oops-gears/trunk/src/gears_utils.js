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

// Other functions
function  resources_path() {
    // extract the name of the resource directory
    return  $('link').attr('href').split('/')[1] + '/'
}

