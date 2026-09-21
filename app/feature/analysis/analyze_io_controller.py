from app.app_model import AppModel
from app.feature.analysis.analyze_view_io import AnalyzeIOView


class AnalyzeIOController:
    """Keep the IO analysis view synchronized with the filtered recording."""

    def __init__(self, app_model: AppModel, view: AnalyzeIOView):
        """Connect recording updates and display any data already in the model."""
        self.app_model = app_model
        self.view = view
        self.app_model.experiment_data_changed.connect(self.update_ui_from_model)
        self.update_ui_from_model()

    def update_ui_from_model(self) -> None:
        """Refresh the IO plot from the model's filtered data."""
        self.view.set_data(self.app_model.filtered_data_df)
