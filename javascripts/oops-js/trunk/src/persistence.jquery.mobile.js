/**
 * Copyright (c) 2010 Roberto Saccon <rsaccon@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following
 * conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 */

if (!window.persistence.jquery) {
  throw new Error("persistence.jquery.js should be loaded before persistence.jquery.mobile.js");
}

persistence.jquery.mobile = {};

(function($){
    var $pjqm = persistence.jquery.mobile;

    if (window.openDatabase) {
        $pjqm.pageEntityName = "Page";
        $pjqm.imageEntityName = "Image";
        $pjqm.pathField = "path";
        $pjqm.dataField = "data";

        var originalAjaxMethod = $.ajax;

        function expand(docPath, srcPath) {
            // take care of the base tag
            console.log('expand srcPath: '+srcPath);
            ex = location.pathname+srcPath.substring(2)
            console.log('expand: '+ex);
            return ex

        }

        function base64Image(img, type) {
            var canvas = document.createElement("canvas");
            canvas.width = img.width;
            canvas.height = img.height;

            // Copy the image contents to the canvas
            var ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0);

            return canvas.toDataURL("image/" + type);
        }

        // parseUri 1.2.2
        // (c) Steven Levithan <stevenlevithan.com>
        // MIT License

        var parseUriOptions = {
            strictMode: false,
            key: ["source","protocol","authority","userInfo","user","password","host","port","relative","path","directory","file","query","anchor"],
            q:   {
                name:   "queryKey",
                parser: /(?:^|&)([^&=]*)=?([^&]*)/g
            },
            parser: {
                strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
                loose:  /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
            }
        };

        function parseUri (str) {
            var o   = parseUriOptions,
                m   = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
                uri = {},
                i   = 14;

            while (i--) uri[o.key[i]] = m[i] || "";

            uri[o.q.name] = {};
            uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
                if ($1) uri[o.q.name][$1] = $2;
            });

            return uri;
        }

        function getImageType(parsedUri) {
            if (parsedUri.queryKey.type) {
                return parsedUri.queryKey.type;
            }  else {
                return (/\.png$/i.test(parsedUri.path)) ? "png" : "jpeg";
            }
        }

        $.ajax = function(settings) {
            console.log('persistence.jquery.mobile rewritten ajax');
            var parsedUrl = parseUri(settings.url);
            var entities = {}, urlPathSegments = parsedUrl.path.split("/");
            if ((settings.type == "post") && (urlPathSegments.length > 1)) {
                var entityName = (urlPathSegments[1].charAt(0).toUpperCase() + urlPathSegments[1].substring(1));
                if (persistence.isDefined(entityName)) {
                    var Form = persistence.define(entityName);

                    var persistFormData = function() {
                        var obj = {};
                        settings.data.replace(/(?:^|&)([^&=]*)=?([^&]*)/g, function ( $0, $1, $2 ) {
                            if ($1) {
                                obj[$1] = $2;
                            }
                        });

                        var entity = new Form(obj);
                        persistence.add(entity);
                        persistence.flush();
                    };

                    if (!navigator.hasOwnProperty("onLine") || navigator.onLine) {
                        originalAjaxMethod({
                            url: settings.url,
                            success: function(data) {
                                settings.success(data);
                                persistFormData();
                            },
                            error: settings.error
                        });
                    } else {
                        persistFormData();
                    }
                } else {
                    originalAjaxMethod(settings);
                }
            } else if (persistence.urlExcludeRx && persistence.urlExcludeRx.test(parsedUrl.path)) {
                originalAjaxMethod(settings);
            } else {
                if (persistence.isDefined($pjqm.pageEntityName)) {
                    console.log('Page and images management');
                    var Page = persistence.define($pjqm.pageEntityName);
                    Page.findBy($pjqm.pathField, settings.url, function(page) {
                        if (page) {
                            //
                            // load page and images from persistencejs
                            //
                            console.log('load page and images from DB');
                            if (settings.success) {
                                p = document.createElement('html');
                                p.innerHTML = page[$pjqm.dataField]();
                                n_imgs = $(p).find('img').length;
                                $(p).find('img').each(function (index, element) {
                                    if (persistence.isDefined($pjqm.imageEntityName)) {
                                        var Img = persistence.define($pjqm.imageEntityName);
                                        Img.findBy(
                                            $pjqm.pathField,
                                            expand(settings.url, $(element).attr('src')),
                                            function(image){
                                                console.log('add image as data:', $(element).attr('src'));
                                                $(element).attr('src', image[$pjqm.dataField]());
                                                if (n_imgs == (index+1)) {
                                                    settings.success(p.innerHTML);
                                                }
                                            }
                                        );
                                    } else {
                                        n_imgs = 0;
                                    }
                                });
                                if (n_imgs == 0) {
                                   settings.success(p.innerHTML);
                                }
                            }
                        } else {
                            //
                            // ajax-load page and persist page and images
                            //
                            console.log('ajax-load page and persist page and images');
                            originalAjaxMethod({
                                url: settings.url,
                                success: function(data) {
                                    settings.success(data);
                                    if (persistence.isDefined($pjqm.pageEntityName)) {
                                        var entities = [], crawlImages = false;
                                        var Page = persistence.define($pjqm.pageEntityName);
                                        if (persistence.isDefined($pjqm.imageEntityName)) {
                                            var Img = persistence.define($pjqm.imageEntityName), count = 0;
                                            $("[data-url=\""+settings.url.replace(/\//g,"\\/").replace(/\./g,"\\.")+"\"] img").each(function(i, img){
                                                //
                                                console.log('original img src:',img.src);

                                                page = $("[data-url=\""+settings.url.replace(/\//g,"\\/").replace(/\./g,"\\.")+"\"]")
                                                attr_class = page.attr('class');
                                                var path = getCurrentPath(attr_class);

                                                var src = $(img).attr('src');
                                                src = src.replace(path,'');
                                                $(img).attr('src',src)

                                                console.log('rewritten img src:', img.src);
                                                //
                                                crawlImages = true;
                                                count++;
                                                $(img).load(function()  {
                                                  var obj = {}, parsedImgSrc = parseUri(img.src);
                                                  obj[$pjqm.pathField] = parsedImgSrc.path;
                                                  obj[$pjqm.dataField] = base64Image(img, getImageType(parsedImgSrc));
                                                  entities.push(new Img(obj));

                                                  if (crawlImages && (--count == 0)) {
                                                      for (var j=0; j<entities.length; j++) {
                                                          persistence.add(entities[j]);
                                                      }
                                                      persistence.flush();
                                                  }
                                                });
                                                $(img).error(function() {
                                                    crawlImages = false;
                                                });
                                            });
                                        }

                                        var obj = {};
                                        obj[$pjqm.pathField] = settings.url;
                                        obj[$pjqm.dataField] = data;

                                        entities.push(new Page(obj));

                                        if (!crawlImages) {
                                            persistence.add(entities[0]);
                                            persistence.flush();
                                        }
                                    }
                                },
                                error: settings.error
                            });
                        }
                    });
                } else {
                    originalAjaxMethod(settings);
                }
            }
        };
    }
})(jQuery);