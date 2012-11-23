Introduction
============

This is a full-blown functional test. The emphasis here is on testing what
the user may input and see, and the system is largely tested as a black box.
We use PloneTestCase to set up this test as well, so we have a full Plone site
to play with. We *can* inspect the state of the portal, e.g. using 
self.portal and self.folder, but it is often frowned upon since you are not
treating the system as a black box. Also, if you, for example, log in or set
roles using calls like self.setRoles(), these are not reflected in the test
browser, which runs as a separate session.

Being a doctest, we can tell a story here.

First, we must perform some setup. We use the testbrowser that is shipped
with Five, as this provides proper Zope 2 integration. Most of the 
documentation, though, is in the underlying zope.testbrower package.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()

The following is useful when writing and debugging testbrowser tests. It lets
us see all error messages in the error_log.

    >>> self.portal.error_log._ignored_exceptions = ()

With that in place, we can go to the portal front page and log in. We will
do this using the default user from PloneTestCase:

    >>> from Products.PloneTestCase.setup import portal_owner, default_password

    >>> browser.open(portal_url)

We have the login portlet, so let's use that.

    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

Here, we set the value of the fields on the login form and then simulate a
submit click.

We then test that we are still on the portal front page:

    >>> browser.url == portal_url
    True

And we ensure that we get the friendly logged-in message:

    >>> "You are now logged in" in browser.contents
    True


-*- extra stuff goes here -*-
The Voice content type
===============================

In this section we are tesing the Voice content type by performing
basic operations like adding, updadating and deleting Voice content
items.

Adding a new Voice content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Voice' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Voice').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Voice' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Voice Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Voice' content item to the portal.

Updating an existing Voice content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Voice Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Voice Sample' in browser.contents
    True

Removing a/an Voice content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Voice
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Voice Sample' in browser.contents
    True

Now we are going to delete the 'New Voice Sample' object. First we
go to the contents tab and select the 'New Voice Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Voice Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Voice
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Voice Sample' in browser.contents
    False

Adding a new Voice content item as contributor
------------------------------------------------

Not only site managers are allowed to add Voice content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Voice' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Voice').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Voice' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Voice Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Voice content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Glossary content type
===============================

In this section we are tesing the Glossary content type by performing
basic operations like adding, updadating and deleting Glossary content
items.

Adding a new Glossary content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Glossary' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Glossary').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Glossary' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Glossary Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Glossary' content item to the portal.

Updating an existing Glossary content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Glossary Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Glossary Sample' in browser.contents
    True

Removing a/an Glossary content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Glossary
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Glossary Sample' in browser.contents
    True

Now we are going to delete the 'New Glossary Sample' object. First we
go to the contents tab and select the 'New Glossary Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Glossary Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Glossary
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Glossary Sample' in browser.contents
    False

Adding a new Glossary content item as contributor
------------------------------------------------

Not only site managers are allowed to add Glossary content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Glossary' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Glossary').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Glossary' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Glossary Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Glossary content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Chapter content type
===============================

In this section we are tesing the Chapter content type by performing
basic operations like adding, updadating and deleting Chapter content
items.

Adding a new Chapter content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Chapter' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Chapter').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Chapter' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Chapter Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Chapter' content item to the portal.

Updating an existing Chapter content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Chapter Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Chapter Sample' in browser.contents
    True

Removing a/an Chapter content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Chapter
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Chapter Sample' in browser.contents
    True

Now we are going to delete the 'New Chapter Sample' object. First we
go to the contents tab and select the 'New Chapter Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Chapter Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Chapter
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Chapter Sample' in browser.contents
    False

Adding a new Chapter content item as contributor
------------------------------------------------

Not only site managers are allowed to add Chapter content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Chapter' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Chapter').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Chapter' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Chapter Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Chapter content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Book content type
===============================

In this section we are tesing the Book content type by performing
basic operations like adding, updadating and deleting Book content
items.

Adding a new Book content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Book' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Book').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Book' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Book Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Book' content item to the portal.

Updating an existing Book content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Book Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Book Sample' in browser.contents
    True

Removing a/an Book content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Book
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Book Sample' in browser.contents
    True

Now we are going to delete the 'New Book Sample' object. First we
go to the contents tab and select the 'New Book Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Book Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Book
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Book Sample' in browser.contents
    False

Adding a new Book content item as contributor
------------------------------------------------

Not only site managers are allowed to add Book content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Book' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Book').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Book' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Book Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Book content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)



