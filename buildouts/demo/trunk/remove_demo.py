# ./bin/instace run remove_demo.py
import transaction

if 'oops-demo' in app.objectIds():
    app.manage_delObjects(['oops-demo',])
    transaction.commit()
    print 'removed'
else:
    print 'not created'
