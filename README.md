# mega-download

**mega-download** is a simple mega.nz shared folders and files downloader

### Requirements
- **Python 3.10 or greater**
- See `requirements.txt` for additional dependencies. Install with:
  - `python -m pip install -r requirements.txt`
### Usage
##### Install as a module
- `cd mega-download`
- `python -m pip install .`
- `python -m mega_download [options...] URL [URL...]`
  - where `URL` is a full links to the mega.nz folder or file (folder file links are suppported, too)
##### Without installing
- `cd mega-download`
- Run either:
  - `python mega_download/__main__.py [options...] URL [URL...]` OR
  - `mega-download.cmd [options...] URL [URL...]` (Windows)
  - `mega-download.sh [options...] URL [URL...]` (Linux)


- Invoke `python ... --help` to list options

For bug reports, questions and feature requests use our [issue tracker](https://github.com/trickerer01/mega-download/issues)
