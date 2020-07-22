<h1 align="center">InstaLiveCLI</h1>

<div align="center">
  :snake: :globe_with_meridians: :star2:
</div>
<div align="center">
  <strong>Live Instagram with CLI </strong>
</div>
<div align="center">
InstaLiveCLI is a Python CLI that create and control an Instagram Live and provide you a rtmp server and stream key to streaming using sofwares like OBS-Studio or XSplit Broadcaster.
</div>

<br />

<div align="center">
  <!-- License -->
  <a href="#">
    <img src="https://img.shields.io/github/license/harrypython/itsagramlive"
      alt="License" />
  </a>
  <!-- Version -->
  <a href="#">
    <img src="https://img.shields.io/github/v/tag/RaihanStark/instalivecli?label=Version"
      alt="GitHub tag (latest by date)" />
  </a>
	
<a href='https://instalivecli.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/instalivecli/badge/?version=latest' alt='Documentation Status' />
</a>
</div>

<div align="center">
  <h3>
    <a href="https://github.com/RaihanStark/instaliveweb">
      WEB/GUI Version
    </a>
    <span> | </span>
    <a href="https://pypi.org/project/InstaLiveCLI/">
      PyPI Package
    </a>
	  <span> | </span>
    <a href="https://instalivecli.readthedocs.io/en/latest/">
      Documentation
    </a>
    <span> | </span>
    <a href="https://webchat.freenode.net/?channels=choo">
      Initial Project
    </a>
  </h3>
</div>

<div align="center">
  <sub>The little script that could. Built with ❤︎ by
  <a href="https://github.com/RaihanStark">Raihan Yudo Saputra</a> and make it possible by 
  <a href="https://github.com/harrypython/itsagramlive">
    harrypython
  </a>
</div>

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Commands](#commands)
- [Installation](#installation)
- [Example](#example)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)
- [See Also](#see-also)

## Features

- **stability:** It's very stable script to starting your live :star:
- **easy to use:** using arguments or write it yourself in script :dash:
- **fully featured:** control your broadcast just like in the app :sparkles:
- **cookie persistent:** login once, use it anytime for 90 days :clap:
- **python:** Everyone knows that, It's a python :snake:

## Installation

```bash
pip install InstaLiveCLI
```

## Commands

- **info**
  Show details about the broadcast
- **mute comments**
  Prevent viewers from commenting
- **unmute comments**
  Allow viewers do comments
- **viewers**
  List viewers
- **chat**
  Send a comment
- **comments**
  Get the list of comments
- **wave**
  Wave to a viewer
- **stop**
  Terminate broadcast

## Example

There's two ways how to use and operate it, with Command Line and Script:

#### > Command Line

```python
from InstaLiveCLI import InstaLiveCLI

live = InstaLiveCLI()
live.start()
```

```bash
python3 live_broadcast.py -u yourInstagramUsername -p yourPassword -proxy user:password@ip:port
```

and you're ready to go. :boom:

### > Scripting

It possible to use this package in your projects without needing to configure and code anything, just place it! :two_hearts:

```python
from InstaLiveCLI import InstaLiveCLI

live = InstaLiveCLI(
	username='foo',
	password='bar'
)
"""
And you can access all the function on the class
You can read the documentation!
"""
live.create_broadcast() #for example
print(live.stream_key) # ...
```

```bash
python3 live_broadcast.py
```

Want to see more examples? Check out the documentation. :book:

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Author

- HarryPython - [itsagramlive](https://github.com/harrypython/itsagramlive) ( CLI Version )
- Raihan Yudo Saputra - [instalivecli](https://github.com/RaihanStark/instalivecli)

## License

[ GNU GPLv3 ](https://choosealicense.com/licenses/gpl-3.0/)

## See Also

- [InstaLiveWeb](https://github.com/choojs/bankai) - a web version of it
- [ItsAGramLive](https://github.com/harrypython/itsagramlive) - initial project from Harry Python
