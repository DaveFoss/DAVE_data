=========================
Contributing to DAVE_data
=========================

Thank you for considering contributing to DAVE_data! We welcome contributions from everyone.
Every little bit helps, and credit will always be given. By participating in this project,
you agree to abide by our guidelines.

How Can You Contribute?
-----------------------

Bug reports
===========

Before reporting a bug, please ensure that the bug was not already reported by searching on
GitHub under `Issues <https://github.com/DaveFoss/DAVE_data/issues>`_.

If you're unable to find an open issue addressing the problem, open a `new one
<https://github.com/DaveFoss/DAVE_data/issues/new>`_. When reporting a bug please include a
title and clear description with relevant information such as:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Documentation improvements
==========================

DaveFoss could always use more documentation, whether as part of the
official DaveFoss docs, in docstrings, or even on the web in blog posts,
articles, and such. You can send feedback on what's essential and missing;
as well as suggesting a correction or a new one yourself.

Feature requests and feedback
=============================

The best way to send feedback is to file an issue at https://github.com/DaveFoss/DAVE_data/issues.

If you are proposing a feature:

* Explain clearly and in detail how it would work. You are welcome to describe any alternative solutions you have considered.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that code contributions are welcome :)

Development
===========

To set up `DAVE_data` for local development:

1. Fork `DAVE_data <https://github.com/DaveFoss/DAVE_data>`_
   (look for the "Fork" button).
2. Clone your fork locally::

    git clone git@github.com:YOURGITHUBNAME/DAVE_data.git

3. Create a branch for local development::

    git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

4. If you have added code that should be tested, add tests.

5. When you're done making changes run all the checks and docs builder with one command::

    tox

6. Commit your changes and push your branch to GitHub::

    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guideline
-----------------------

If you need some code review or feedback while you're developing the code just make the pull request.

For merging, you should:

1. Include passing tests (run ``tox``).
2. Update documentation when there's new API, functionality etc.
3. Add a note to ``CHANGELOG.rst`` about the changes.

Changelog Guideline
-----------------------

Guiding Principles
==================

* Changelogs are for humans, not machines.
* There should be an entry for every single version.
* The same types of changes should be grouped.
* Add the link to a git commit if there is one.
* The latest version comes first.
* The release date of each version is displayed.

Types of changes
================

* Added for new features.
* Changed for changes in existing functionality.
* Deprecated for soon-to-be removed features.
* Removed for now removed features.
* Fixed for any bug fixes.
* Required for any new requirements
* Event for an achieved Milestone

Guidelines
----------

- Follow the coding style used in the project.
- Write clear and meaningful commit messages.
- Ensure that your changes do not introduce new issues.
- Be respectful and considerate in your interactions with others.

Tips
----

To run a subset of tests::

    tox -e envname -- pytest -k test_myfeature

To run all the test environments in *parallel*::

    tox -p auto
