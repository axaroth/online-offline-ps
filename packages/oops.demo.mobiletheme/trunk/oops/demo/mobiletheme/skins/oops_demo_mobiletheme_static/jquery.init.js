$('div.type-Book').live('pageshow',function(event, ui){
  prevPages = ui.prevPage;

  if(prevPages.length == 0){return}

  attr_class = $(this).attr('class');
  var path = getCurrentPath(attr_class);
  
  var links = $(this).find('a');
  $.each(links, function(index, value){
    var href = $(value).attr('href');
    href = href.replace(path,'');
    $(value).attr('href',href)
  })
});





$('div.type-Chapter').live('pageshow',function(event, ui){  
  var links = $(this).find('a');
  $.each(links, function(index, value){
    $(value).attr('rel','external');
  })
  
  prevPages = ui.prevPage;
  if(prevPages.length == 0){return}
  
  attr_class = $(this).attr('class');
  var path = getCurrentPath(attr_class);
  
  var images = $(this).find('img');
  $.each(images, function(index, value){
    var src = $(value).attr('src');
    src = src.replace(path,'');
    $(value).attr('src',src)
  })

});



/**
*
* utility
*
**************/
function getCurrentPath(attributePath){
  classes = attributePath.split(' ');
  var path = '';
  for (i=0;i<classes.length;i++){
    value = classes[i]
    if(value.indexOf('path-')!=-1){
      path = value.replace('path-','');
    }
  }
  return path;
}

