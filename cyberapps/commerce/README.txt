====================
eCommerce with loops
====================

Note: This package depends on loops.

Let's do some basic set up

  >>> from zope.app.testing.setup import placefulSetUp, placefulTearDown
  >>> site = placefulSetUp(True)

  >>> from zope import component, interface

and setup a simple loops site with a concept manager and some concepts
(with all the type machinery, what in real life is done via standard
ZCML setup):

  >>> from cyberapps.commerce.tests import TestSite
  >>> t = TestSite(site)
  >>> concepts, resources, views = t.setup()

We also collect here some basic imports we'll need later.

  >>> from loops.concept import Concept
  >>> from loops.common import adapted
  >>> from loops.setup import addAndConfigureObject

We also use an adapter to the concept manager for accessing the commerce
objects.

  >>> from cyberapps.commerce.manager import Manager
  >>> manager = Manager(concepts)


Shops and Products
==================

Let's start with two shops:

  >>> shop1 = manager.shops.create('shop1', title='PC up Ltd')
  >>> shop2 = manager.shops.create('shop2', title='Video up Ltd')

  >>> len(list(manager.shops))
  2

  >>> shop1.title
  'PC up Ltd'

Now we create a few products ...

  >>> p001 = manager.products.create('001', title='Silent Case')
  >>> p002 = manager.products.create('002', title='Portable Projector')
  >>> p003 = manager.products.create('003', title='HD Flatscreen Monitor')
  >>> p004 = manager.products.create('004', title='Giga Mainboard')

  >>> p001.title
  'Silent Case'
  >>> p001.fullDescription

... and add them to the shops.

  >>> shop1.products.add(p001)
  >>> shop1.products.add(p003)
  >>> shop1.products.add(p004)
  >>> shop2.products.add(p002)
  >>> shop2.products.add(p003)

We can now list the products in a shop.

  >>> sorted((p.productId, p.title) for p in shop1.products)
  [('001', 'Silent Case'), ('003', 'HD Flatscreen Monitor'),
   ('004', 'Giga Mainboard')]

  >>> sorted((s.name, s.title) for s in p003.shops)
  [('shop1', 'PC up Ltd'), ('shop2', 'Video up Ltd')]

Categories
----------

  >>> cat001 = manager.categories.create('001', title='Cases')
  >>> p001.categories.add(cat001)


Customers
=========

Now let's add a few customers.

  >>> c001 = manager.customers.create('001', title='Your Local Computer Store')
  >>> c002 = manager.customers.create('002', title='Speedy Gonzales')
  >>> c003 = manager.customers.create('003', title='TeeVee')
  >>> c004 = manager.customers.create('004', title='MacVideo')

These are stored in a separate ConceptManager object.

  >>> customers = concepts.getLoopsRoot()['customers']
  >>> len(customers)
  4

In the testing scenario we have to index all the customer objects.

  >>> from zope.app.catalog.interfaces import ICatalog
  >>> catalog = component.getUtility(ICatalog)
  >>> from loops import util
  >>> for r in customers.values():
  ...     catalog.index_doc(int(util.getUidForObject(r)), r)

Now the customers can be accessed via the standard concept manager adapter.

  >>> manager.customers.get('004')
  <cyberapps.commerce.customer.Customer object ...>

  >>> shop1.customers.add(c001)
  >>> shop1.customers.add(c002)
  >>> shop1.customers.add(c004)
  >>> shop2.customers.add(c002)
  >>> shop2.customers.add(c003)
  >>> shop2.customers.add(c004)

  >>> sorted((c.customerId, c.title) for c in shop1.customers)
  [('001', 'Your Local Computer Store'), ('002', 'Speedy Gonzales'),
   ('004', 'MacVideo')]

  >>> sorted((s.name, s.title) for s in c002.shops)
  [('shop1', 'PC up Ltd'), ('shop2', 'Video up Ltd')]


Carts and Orders
================

A cart is just a collection of order items belonging to a certain customer
(or some other kind of party).

  >>> orderItems = manager.orderItems

  >>> orderItems.add(p001, c001, shop=shop1, quantity=3)
  <OrderItem ['44', 1, '60', '... ...', '???']: {'quantity': 3, 'shop': '40'}>

  >>> orderItems.getCart(c001)
  [<OrderItem ['44', 1, '60', '... ...', '???']: {'quantity': 3, 'shop': '40'}>]

Orders
------

The items in a shopping cart may be included in an order.

  >>> ord001 = manager.orders.create('001', shop=shop1, customer=c001)

  >>> for item in orderItems.getCart(c001):
  ...     item.setOrder(ord001)

Now the default cart is empty; we have to supply the order for
retrieving the order items. But now we can omit the customer from the query.

  >>> orderItems.getCart(c001)
  []
  >>> orderItems.getCart(c001, ord001)
  [<OrderItem ['44', 1, '60', '... ...', '74']: {'quantity': 3, 'shop': '40'}>]
  >>> orderItems.getCart(order=ord001)
  [<OrderItem ['44', 1, '60', '... ...', '74']: {'quantity': 3, 'shop': '40'}>]


Administrative Views and Forms
==============================

  >>> from zope.publisher.browser import TestRequest

Listings
--------

  >>> from cyberapps.commerce.browser.base import SimpleListing

Forms
-----

  >>> from loops.view import Node
  >>> from cyberapps.commerce.browser.product import CreateProductPage

  >>> home = addAndConfigureObject(views, Node, 'home', target=cat001.context)

  >>> form = CreateProductPage(home, TestRequest())


Fin de partie
=============

  >>> placefulTearDown()
