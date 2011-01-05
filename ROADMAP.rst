Multilang URLs Roadmap
======================

Future
------

* Sticky language selection

  * When a user requests a lang-prefixed page, the middleware sets their
    language cookie so that they'll be sent back to that same language if
    they arrive back at the language-agnostic root URL

* Refactor MultilangRegexURLResolver so that it properly handles app_name
  and name_space

* Build separate gettext wrapper for translatable URLs

  * Remove requirement that translatable URL patterns be wrapped in gettext
    blocks

  * Remove requirement that translatable URLs be wrapped in explicit "url"
    function