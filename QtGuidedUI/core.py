import os
import json
import logging
from Qt.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QToolTip,
)
from Qt.QtCore import Qt, QPoint, QSize
from Qt.QtGui import QPixmap, QMovie

logger = logging.getLogger("QtGuidedUI")


class GuidedUI(QWidget):
    """A widget that initializes and starts an interactive guide based on a JSON configuration.

    Attributes:
        guide_data (dict): The JSON configuration loaded from file.
        guide (InteractiveGuide): The interactive guide instance.
    """

    def __init__(self, guide_json_path: str, parent: QWidget = None) -> None:
        """Initialize the GuidedUI widget.

        Args:
            guide_json_path (str): The path to the JSON configuration file for the guide.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.guide_data = self.load_guide_config(guide_json_path)
        images_dir = os.path.dirname(guide_json_path)
        self.guide = InteractiveGuide(self, self.guide_data, images_dir)

    def load_guide_config(self, path: str) -> dict:
        """Load the guide configuration from a JSON file.

        Args:
            path (str): The path to the JSON configuration file.

        Returns:
            dict: The loaded configuration dictionary.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error("Failed to load guide config: %s", e)
            raise

    def start_guide(self) -> None:
        """Start the interactive guide."""
        self.guide.start()


class InteractiveGuide:
    """Manages an interactive guide through UI components based on configuration steps.

    Attributes:
        parent_widget (QWidget): The parent widget containing UI elements.
        steps (list): List of guide steps sorted by order.
        intro_message (str): Introduction message to display at the start of the guide.
        outro_message (str): Conclusion message to display when the guide completes.
        dialog_image_width (int): Width of the dialog window image.
        images_dir (str): Directory containing images for the guide.
        current_step_index (int): Index of the current guide step.
        current_widget (QWidget): The currently highlighted widget.
        current_widget_original_style (str | None): Original style sheet of the highlighted widget.
    """

    def __init__(self, parent_widget: QWidget, guide_data: dict, images_dir: str) -> None:
        """Initialize the interactive guide.

        Args:
            parent_widget (QWidget): The parent widget containing UI elements.
            guide_data (dict): The guide configuration data.
            images_dir (str): Directory where guide images are stored.
        """
        self.parent_widget = parent_widget
        # Sort steps by the "order" key; default order is 0 if not provided.
        self.steps = sorted(guide_data.get("steps", []), key=lambda x: x.get("order", 0))
        self.intro_message = guide_data.get("intro_message", "Welcome to the guide!")
        self.outro_message = guide_data.get("outro_message", "Guide completed!")
        self.dialog_image_width = guide_data.get("dialog_image_width", 500)
        self.images_dir = images_dir
        self.current_step_index = -1
        self.current_widget = None
        self.current_widget_original_style = None

    def start(self) -> None:
        """Start the interactive guide by showing the introduction message."""
        self.show_message_dialog(
            title="Interactive Guide",
            message=self.intro_message,
            button_text="Start",
            callback=self.next_step,
        )

    def next_step(self) -> None:
        """Proceed to the next step in the guide, executing any pre-actions and highlighting widgets."""
        self.current_step_index += 1

        if self.current_step_index >= len(self.steps):
            # All steps are completed; show completion dialog.
            self.show_message_dialog(
                title="Guide Completed",
                message=self.outro_message,
                button_text="Close",
            )
            return

        step = self.steps[self.current_step_index]

        # Execute pre-action if defined.
        pre_action = step.get("pre_action")
        if pre_action:
            logger.info("Executing pre-action: %s", pre_action)
            action_callable = getattr(self.parent_widget, pre_action, None)
            if callable(action_callable):
                try:
                    action_callable()
                except Exception as e:
                    logger.warning("Pre-action '%s' failed: %s", pre_action, e)
            else:
                logger.warning("Pre-action '%s' is not callable.", pre_action)

        # Attempt to find the widget by its object name.
        widget = self.parent_widget.findChild(QWidget, step.get("object_name"))
        if widget is None:
            logger.warning(
                "Widget '%s' not found. Skipping this step.", step.get("object_name")
            )
            self.next_step()
            return

        self.highlight_widget(widget)
        self.show_step_tooltip(widget=widget, step=step)

    def show_message_dialog(
        self, title: str, message: str, button_text: str = "OK", callback=None
    ) -> None:
        """Display a modal message dialog with a callback on button press.

        Args:
            title (str): The title of the dialog.
            message (str): The message to display.
            button_text (str, optional): Text for the dialog button. Defaults to "OK".
            callback (callable, optional): Function to call after dialog acceptance. Defaults to None.
        """
        dialog = QDialog(self.parent_widget)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(message))

        def on_button_clicked() -> None:
            dialog.accept()
            if callback:
                callback()

        btn = QPushButton(button_text)
        btn.clicked.connect(on_button_clicked)
        layout.addWidget(btn)

        dialog.setLayout(layout)
        dialog.exec()

    def next_step_action(self, dialog: QDialog) -> None:
        """Handle action to proceed to the next step after closing a dialog.

        Args:
            dialog (QDialog): The dialog to close.
        """
        dialog.accept()
        self.restore_widget_style()
        self.next_step()

    def skip_guide_action(self, dialog: QDialog) -> None:
        """Handle action to skip the guide, closing the dialog and restoring widget style.

        Args:
            dialog (QDialog): The dialog to close.
        """
        dialog.close()
        self.restore_widget_style()
        QToolTip.showText(
            self.parent_widget.mapToGlobal(QPoint(100, 100)),
            "Guide skipped.",
            self.parent_widget,
        )

    def highlight_widget(self, widget: QWidget) -> None:
        """Highlight a widget by changing its style to draw user attention.

        Args:
            widget (QWidget): The widget to highlight.
        """
        logger.info("Highlighting widget: %s", widget.objectName())
        self.current_widget = widget
        self.current_widget_original_style = widget.styleSheet()
        widget.setStyleSheet("border: 3px solid green;")

    def restore_widget_style(self) -> None:
        """Restore the original style of the currently highlighted widget."""
        if self.current_widget and self.current_widget_original_style is not None:
            logger.info("Restoring widget style for: %s", self.current_widget.objectName())
            self.current_widget.setStyleSheet(self.current_widget_original_style)
            self.current_widget = None
            self.current_widget_original_style = None
        else:
            logger.warning("No widget style to restore.")

    def _calculate_tooltip_position(self, widget: QWidget, dialog: QDialog) -> QPoint:
        """Calculate a dynamic position for the tooltip dialog relative to the widget.

        Args:
            widget (QWidget): The widget to anchor the tooltip.
            dialog (QDialog): The tooltip dialog.

        Returns:
            QPoint: The calculated global position for the dialog.
        """
        widget_rect = widget.rect()
        widget_center = widget.mapToGlobal(widget_rect.center())
        parent_rect = self.parent_widget.rect()
        parent_global_pos = self.parent_widget.mapToGlobal(parent_rect.topLeft())
        parent_center = parent_global_pos + QPoint(
            parent_rect.width() // 2, parent_rect.height() // 2
        )
        dialog_size = dialog.size()

        # Default horizontal centering relative to widget.
        x = widget_center.x() - dialog_size.width() // 2

        # Vertical positioning: below widget if above parent's center, else above widget.
        if widget_center.y() < parent_center.y():
            y = widget.mapToGlobal(widget_rect.bottomLeft()).y() + 10
        else:
            y = widget.mapToGlobal(widget_rect.topLeft()).y() - dialog_size.height() - 10

        # Adjust horizontal position if dialog is out of parent's bounds.
        if x < parent_global_pos.x():
            x = parent_global_pos.x() + 10
        elif x + dialog_size.width() > parent_global_pos.x() + parent_rect.width():
            x = parent_global_pos.x() + parent_rect.width() - dialog_size.width() - 10

        return QPoint(x, y)

    def show_step_tooltip(self, widget: QWidget, step: dict) -> None:
        """Show a tooltip dialog for the current step, including description, image, and navigation buttons.

        Args:
            widget (QWidget): The widget to highlight and anchor the tooltip.
            step (dict): The step configuration containing description, image, and other properties.
        """
        tooltip_dialog = QDialog(self.parent_widget)
        tooltip_dialog.setWindowFlags(Qt.ToolTip)
        layout = QVBoxLayout()

        # Add the step description.
        layout.addWidget(QLabel(step.get("description", "")))

        # Process and add image if available.
        image_filename = step.get("image")
        if image_filename:
            image_path = os.path.join(self.images_dir, image_filename)
            logger.info("Using image path: %s", image_path)
            image_label = QLabel()
            if image_path.lower().endswith(".gif"):
                movie = QMovie(image_path)

                def resize_movie_frame() -> None:
                    pixmap = movie.currentPixmap()
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaledToWidth(
                            self.dialog_image_width, Qt.SmoothTransformation
                        )
                        image_label.setPixmap(scaled_pixmap)

                movie.frameChanged.connect(resize_movie_frame)
                movie.start()
            else:
                pixmap = QPixmap(image_path)
                image_label.setPixmap(pixmap.scaledToWidth(
                    self.dialog_image_width, Qt.SmoothTransformation)
                )
            layout.addWidget(image_label)

        # Create navigation buttons.
        btn_next = QPushButton("Next")
        btn_skip = QPushButton("Skip Guide")
        btn_next.clicked.connect(lambda: self.next_step_action(tooltip_dialog))
        btn_skip.clicked.connect(lambda: self.skip_guide_action(tooltip_dialog))

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_next)
        btn_layout.addWidget(btn_skip)
        layout.addLayout(btn_layout)

        tooltip_dialog.setLayout(layout)
        tooltip_dialog.adjustSize()  # Ensure size is calculated before positioning.

        # Calculate and set dynamic position for the dialog.
        pos = self._calculate_tooltip_position(widget, tooltip_dialog)
        tooltip_dialog.move(pos)
        tooltip_dialog.show()
