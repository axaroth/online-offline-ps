Introduction
============

  To use ISearchDataDumper dumpers you must add these calls in your 'dump' method
  of the base dumper of the content:

    - self.base_search_data
        Create the dictionary with the text. In some case this method must be
        overwritten to much the need of the content, for example in case it is
        a container.

    - self.save_search_data
        save the searchabletext.json file woth data generate from base_search_data

  Below the code get from collective.book for Chapter:

    # Chapter
    class ChapterDumper(BaseDumper):
        implements(IDumper)

        def dump(self):
            """ """
            self.index_html()

            # add annexes and pictures pages
            self.add_page_html(self.context, dump_name = 'pictures.html',
                               view='pictures')
            self.add_page_html(self.context, dump_name = 'annexes.html',
                               view='annexes')


            self.base_search_data()
            self.custom_dumps()
            self.update_manifest_with_files()
            self.save_search_data()
            self.manifest()
