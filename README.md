<p align="center">
    <img src="icon_256.png" width="128"/>
</p>

<h1 align="center">QtGuidedUI</h1>

<p align="center">
    <img alt="GitHub top language" src="https://img.shields.io/github/languages/top/hasielhassan/QtGuidedUI" />
    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/hasielhassan/QtGuidedUI" />
    <img alt="License" src="https://img.shields.io/github/license/hasielhassan/QtGuidedUI" />
    <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/hasielhassan/QtGuidedUI" />
    <img alt="GitHub release downloads" src="https://img.shields.io/github/downloads/hasielhassan/QtGuidedUI/total" />
    <img alt="GitHub release downloads" src="https://img.shields.io/badge/Python Versions-3.7 / 3.9 / 3.11-blue" />

</p>

![Demo](/sample/screenrecording.gif)

QtGuidedUI is a lightweight interactive guide system built with [PySide](https://wiki.qt.io/Qt_for_Python), but using [Qt.py](https://github.com/mottosso/Qt.py) for extended Qt bindings support. 

It allows developers to create guided tours of their applications by configuring a series of steps in a JSON file. 

The guide highlights specific UI elements, displays helpful tooltips with images and descriptions, and manages navigation through the guide steps.

## Features

- **Configurable Steps:** Define steps in a JSON configuration file with descriptions, images, and pre-actions.
- **Widget Highlighting:** Visually highlight UI elements to draw user attention.
- **Interactive Dialogs:** Display tooltips and dialogs with navigation controls (Next, Skip).
- **Dynamic Positioning:** Automatically calculate dialog positions relative to highlighted widgets.
- **Pre-Action Support:** Execute pre-defined actions before displaying each step.

## Getting Started

### Prerequisites

- **Python 3.7+**

Install requirements using pip:
- **Qt.py 1.4.1+** 

```bash
pip install -r requirements.txt
```

### Configuration

Create a JSON configuration file for your guide. An example configuration (`guide_config.json`) might look like this:

```json
{
  "intro_message": "Welcome to the interactive guide!",
  "outro_message": "You have completed the guide.",
  "dialog_image_width": 300,
  "steps": [
    {
      "order": 1,
      "object_name": "startButton",
      "description": "Click this button to begin.",
      "image": "start_button.png",
      "pre_action": "prepare_start"
    },
    {
      "order": 2,
      "object_name": "settingsButton",
      "description": "Access settings here.",
      "image": "settings.gif"
    }
  ]
}
```

- **intro_message:** Message displayed at the beginning of the guide.
- **outro_message:** Message displayed after the guide is completed.
- **steps:** An array of guide steps where:
  - `order` defines the sequence.
  - `object_name` is the name of the widget to highlight.
  - `description` is the tooltip text.
  - `image` (optional) is the image (or GIF) to show.
    Path is relative to the `guide_config.json` file.
  - `pre_action` (optional) is the name of a method on the parent widget to call before the step is shown.

## Usage

Integrate the guided UI into your application by instantiating the `GuidedUI` widget and calling `start_guide()`.

Example:

```python
import sys
from Qt.QtWidgets import QApplication
from QtGuidedUI import GuidedUI  # Adjust the import according to your project structure

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Pass the path to your JSON configuration file.
    guide = GuidedUI("path/to/guide_config.json")
    guide.start_guide()
    guide.show()  # Display the main UI if necessary
    sys.exit(app.exec())
```

A complete and more realistic example is available in the sample folder:

[sample/sample.py](sample/sample.py)

## Attributions

- Logo: [Next step icons created by Danteee82 - Flaticon](https://www.flaticon.com/free-icon/ecommerce_8602327)

- Example image [sample.png](sample/images/sample.png):
  - [WebArtDevelopers BIG FANCY 3D ROTATING SVG BUTTON](https://webartdevelopers.com/blog/big-fancy-3d-rotating-svg-button-2/)
- Example gif [sample.gif](sample/images/sample.gif):
  - [WebArtDevelopers UI/UX EXAMPLE: TAB SWITCH ANIMATION](https://webartdevelopers.com/blog/ui-ux-example-tab-switch-animation/)

## License

This project is licensed under the MIT License. 

See the [LICENSE](LICENSE) file for details.

