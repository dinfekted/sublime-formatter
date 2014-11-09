# Sublime Formatter plugin

Attempt to make language independent (for languages with c-like syntax) source
code formatting with regexps and a bit of python code. This is really glorious
plugin that works (for pity) not as stable as it should be.


### Demo

![Demo](https://github.com/shagabutdinov/sublime-enhanced-demos/raw/master/formatter.gif "Demo")


### WARNING

This plugin is in beta.

This plugin theoretically can corrupt source code and get it to unrunnable
state. I didn't experienced that but it still can happen. Please use it with
care.

This plugin still requires features to be added. See issues list to find out
what will be added later.

This plugin can be slow on large files (especially css as it hits too much
regexps). Any advises on optimization are highly appreciated.

This plugin format source code according to my personal taste. If you would like
to have another formatting model you can contribute and add settings to
different cases of formatting.


### Installation

This plugin is part of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
plugin set. You can install sublime-enhanced and this plugin will be installed
automatically.

If you would like to install this package separately check "Installing packages
separately" section of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
package.


### Usage

Hit keyboard shortcut and see what happened. If you unlucky formatting of file
will be corrupted and you will need to hit "undo" and do formatting manually.


### Commands

| Description                  | Keyboard shortcut | Command palette   |
|------------------------------|-------------------|-------------------|
| Format source code           | ctrl+shift+a      | Formatter: format |


### Dependencies

* [Semicolon](https://github.com/shagabutdinov/sublime-semicolon)
* [WrapStatement](https://github.com/shagabutdinov/sublime-wrap-statement)