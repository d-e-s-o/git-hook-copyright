copyright
=========


Purpose
-------

**copyright** is a Python module that provides functionality for
automated handling of copyright headers in files. In particular, it
provides the means for "normalizing" the years typically stated in
the copyright header. Normalizing in this sense means creating the
smallest string of years preserving the existing semantics.
As an example, consider a (simplified and non-normalized) header such
as:

 > Copyright (C) 2005,2006,2006-2014 Daniel Mueller (deso@posteo.net)

In this example the year 2006 is included in the span 2006-2014. Hence,
it can be removed without any loss in semantics. Furthermore, since 2005
is the year before 2006, the year span can just start with the year
2005, resulting in the following normalized header without any change in
semantics:

 > Copyright (C) 2005-2014 Daniel Mueller (deso@posteo.net)

Normalization also includes the proper sorting of the years in ascending
order as well as (if desired) merging in the current year.


Support
-------

The module is tested with Python 3. There is no work going on to
ensure compatibility with Python 2.
